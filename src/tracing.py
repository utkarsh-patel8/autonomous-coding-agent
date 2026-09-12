import json
import uuid

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

DEFAULT_RUNS_DIR = PROJECT_ROOT / "runs"


class RunTracer:
    def __init__(
        self,
        task: str,
        max_output_chars: int = 6000,
    ):
        self.task = task

        self.max_output_chars = (
            max_output_chars
        )

        self.run_id = (
            uuid.uuid4().hex[:12]
        )

        self.started_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        self._start_time = perf_counter()

        self.events: list[dict] = []

    def _elapsed(self) -> float:
        return round(
            perf_counter() - self._start_time,
            4,
        )

    def preview(
        self,
        value,
    ):
        """
        Keep trace files manageable.

        Large file contents and command output are truncated.
        """

        if value is None:
            return None

        if isinstance(value, str):

            if (
                len(value)
                <= self.max_output_chars
            ):
                return value

            return (
                value[:self.max_output_chars]
                + "\n\n"
                + (
                    "[TRACE OUTPUT TRUNCATED - "
                    f"original length: {len(value)} chars]"
                )
            )

        if isinstance(value, dict):
            return {
                str(key): self.preview(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self.preview(item)
                for item in value
            ]

        return value

    def log(
        self,
        event_type: str,
        step: int | None = None,
        **data,
    ):
        event = {
            "event": event_type,
            "elapsed_seconds": self._elapsed(),
        }

        if step is not None:
            event["step"] = step

        for key, value in data.items():
            event[key] = self.preview(value)

        self.events.append(event)

    def save(
        self,
        metrics: dict,
        runs_dir: Path | None = None,
    ) -> str:

        if runs_dir is None:
            runs_dir = DEFAULT_RUNS_DIR

        runs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S")

        filename = (
            f"run_{timestamp}_{self.run_id}.json"
        )

        path = runs_dir / filename

        payload = {
            "run_id": self.run_id,
            "task": self.task,
            "started_at": self.started_at,
            "metrics": metrics,
            "events": self.events,
        }

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        try:
            return str(
                path.relative_to(PROJECT_ROOT)
            )

        except ValueError:
            return str(path)