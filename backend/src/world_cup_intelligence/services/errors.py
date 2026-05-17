from __future__ import annotations


class ModelArtifactUnavailableError(RuntimeError):
    def __init__(self, model_slug: str) -> None:
        super().__init__(
            f"The {model_slug} model artifact is unavailable. Retrain the model or restore the backend artifacts before serving this workflow."
        )
        self.model_slug = model_slug
