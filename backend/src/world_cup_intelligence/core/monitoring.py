from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock


@dataclass
class EndpointMetrics:
    count: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0


class RequestMonitor:
    def __init__(self) -> None:
        self.started_at = datetime.now(UTC)
        self.total_requests = 0
        self.error_requests = 0
        self._paths: dict[str, EndpointMetrics] = defaultdict(EndpointMetrics)
        self._lock = Lock()

    def record(self, path: str, status_code: int, duration_ms: float) -> None:
        with self._lock:
            self.total_requests += 1
            bucket = self._paths[path]
            bucket.count += 1
            bucket.total_duration_ms += duration_ms
            if status_code >= 400:
                self.error_requests += 1
                bucket.error_count += 1

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            top_paths = sorted(
                self._paths.items(),
                key=lambda item: item[1].count,
                reverse=True,
            )[:5]
            return {
                "total_requests": self.total_requests,
                "error_requests": self.error_requests,
                "uptime_seconds": round((datetime.now(UTC) - self.started_at).total_seconds(), 3),
                "top_paths": [
                    {
                        "path": path,
                        "count": metrics.count,
                        "error_count": metrics.error_count,
                        "avg_duration_ms": round(metrics.total_duration_ms / metrics.count, 3) if metrics.count else 0.0,
                    }
                    for path, metrics in top_paths
                ],
            }


request_monitor = RequestMonitor()
