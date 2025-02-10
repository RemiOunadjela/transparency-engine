"""Custom framework loader.

Allows users to define their own regulatory framework via a YAML or JSON
configuration file. Useful for internal reporting standards, Canadian
Bill C-63 compliance, or platform-specific transparency commitments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from transparency_engine.config import ReportingPeriod
from transparency_engine.frameworks.base import BaseFramework, MetricRequirement, ReportSection


class CustomFramework(BaseFramework):
    """A framework loaded from a JSON definition file.

    Expected schema::

        {
            "name": "Internal Transparency Standard",
            "short_code": "its",
            "reporting_cadence": "quarterly",
            "metrics": [ ... ],
            "sections": [ ... ]
        }
    """

    def __init__(self, definition: dict[str, Any] | None = None) -> None:
        self._definition = definition or {}

    @classmethod
    def from_file(cls, path: Path | str) -> CustomFramework:
        path = Path(path)
        with open(path) as f:
            data = json.load(f)
        return cls(definition=data)

    @property
    def name(self) -> str:
        return self._definition.get("name", "Custom Framework")

    @property
    def short_code(self) -> str:
        return self._definition.get("short_code", "custom")

    @property
    def reporting_cadence(self) -> ReportingPeriod:
        raw = self._definition.get("reporting_cadence", "semi-annual")
        return ReportingPeriod(raw)

    def metric_requirements(self) -> list[MetricRequirement]:
        raw_metrics = self._definition.get("metrics", [])
        return [MetricRequirement(**m) for m in raw_metrics]

    def report_sections(self) -> list[ReportSection]:
        raw_sections = self._definition.get("sections", [])
        return [ReportSection(**s) for s in raw_sections]
