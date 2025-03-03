"""Audit trail for data transformations.

Every transformation applied to the data -- filtering, aggregation,
period alignment -- is logged here for regulatory traceability. In
practice, auditors ask "how did you arrive at this number?" and the
audit trail answers that question.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    """A single logged transformation step."""

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    operation: str
    description: str
    input_shape: tuple[int, int] | None = None  # (rows, cols) before
    output_shape: tuple[int, int] | None = None  # (rows, cols) after
    parameters: dict[str, Any] = Field(default_factory=dict)


class AuditTrail:
    """Append-only audit log for a reporting pipeline run."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def log(
        self,
        operation: str,
        description: str,
        input_shape: tuple[int, int] | None = None,
        output_shape: tuple[int, int] | None = None,
        **params: Any,
    ) -> None:
        entry = AuditEntry(
            operation=operation,
            description=description,
            input_shape=input_shape,
            output_shape=output_shape,
            parameters=params,
        )
        self._entries.append(entry)

    @property
    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def summary(self) -> str:
        lines = [f"Audit trail: {len(self._entries)} operations"]
        for i, entry in enumerate(self._entries, 1):
            shape_info = ""
            if entry.input_shape and entry.output_shape:
                shape_info = f" [{entry.input_shape[0]} rows -> {entry.output_shape[0]} rows]"
            lines.append(
                f"  {i}. [{entry.timestamp}] {entry.operation}: {entry.description}{shape_info}"
            )
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            [e.model_dump() for e in self._entries],
            indent=2,
            default=str,
        )

    def save(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str) -> AuditTrail:
        trail = cls()
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        for entry_data in raw:
            trail._entries.append(AuditEntry(**entry_data))
        return trail
