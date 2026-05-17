from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from world_cup_intelligence.config import docs_path, metadata_path


@dataclass
class ProjectMemory:
    project_goals: list[str]
    architecture_decisions: list[str]
    feature_engineering_logic: list[str]
    evaluation_methodology: list[str]
    deployment_requirements: list[str]
    football_analytics_assumptions: list[str]
    updated_at: str


class ProjectMemoryStore:
    def __init__(self) -> None:
        self.memory_file = metadata_path("project_memory.json")
        self.markdown_file = docs_path("project_memory.md")

    def ensure_defaults(self) -> ProjectMemory:
        if self.memory_file.exists():
            memory = self.load()
            self.save(memory)
            return memory

        memory = ProjectMemory(
            project_goals=[
                "Ship a production-quality World Cup analytics platform, not a notebook prototype.",
                "Keep match prediction, xG analysis, penalty prediction, and tournament simulation in one API-first product.",
                "Support yearly tournament refreshes through config-driven pipelines and reproducible runs.",
            ],
            architecture_decisions=[
                "Use a modular monorepo with explicit separation across ingestion, training, evaluation, API serving, and frontend visualization.",
                "Keep the backend API stable even when the frontend runs in demo mode.",
                "Adopt stateful workflow orchestration and durable project memory for long-running data and modeling tasks.",
            ],
            feature_engineering_logic=[
                "Match prediction uses national-team Elo delta, recent form, goal trend, rest-days delta, confederation strength gap, and host flag.",
                "xG modeling uses shot geometry and contextual event features that can later be normalized through socceraction-style action representations.",
                "Penalty modeling separates target-zone tendency from conversion probability to support both scouting and shootout simulation.",
            ],
            evaluation_methodology=[
                "Every training pipeline must emit versioned artifacts plus tracked metrics for reproducibility.",
                "Classification models should log accuracy, macro F1, and log loss at minimum, with ROC-AUC for binary tasks where possible.",
                "Tournament logic changes require deterministic tests around qualification and bracket generation.",
            ],
            deployment_requirements=[
                "Frontend demo must be publicly deployable as a static site.",
                "Backend must remain independently deployable as a web API with health checks and environment-based config.",
                "Experiments, artifacts, and workflow state must be inspectable after runs.",
            ],
            football_analytics_assumptions=[
                "soccerdata-style caching and source-specific adapters are the default pattern for scraping or ingesting football datasets.",
                "socceraction SPADL or Atomic-SPADL is the target normalization direction for future event-level processing.",
                "Open datasets can power the public demo, but production refreshes must remain source-aware and reproducible.",
            ],
            updated_at=datetime.now(UTC).isoformat(),
        )
        self.save(memory)
        return memory

    def load(self) -> ProjectMemory:
        payload = json.loads(self.memory_file.read_text(encoding="utf-8"))
        return ProjectMemory(**payload)

    def save(self, memory: ProjectMemory) -> None:
        self.memory_file.write_text(json.dumps(asdict(memory), indent=2), encoding="utf-8")
        self.markdown_file.write_text(self._to_markdown(memory), encoding="utf-8")

    def _to_markdown(self, memory: ProjectMemory) -> str:
        sections = [
            ("Project Goals", memory.project_goals),
            ("Architecture Decisions", memory.architecture_decisions),
            ("Feature Engineering Logic", memory.feature_engineering_logic),
            ("Evaluation Methodology", memory.evaluation_methodology),
            ("Deployment Requirements", memory.deployment_requirements),
            ("Football Analytics Assumptions", memory.football_analytics_assumptions),
        ]
        lines = ["# Project Memory", "", f"Updated: `{memory.updated_at}`", ""]
        for title, items in sections:
            lines.append(f"## {title}")
            lines.append("")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
        return "\n".join(lines)
