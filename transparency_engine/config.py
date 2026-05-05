"""Global configuration and shared constants."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ReportingPeriod(str, Enum):
    """Standard reporting cadences used across regulatory frameworks."""

    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi-annual"
    ANNUAL = "annual"
    CUSTOM = "custom"


class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


class PeriodSpec(BaseModel):
    """A specific reporting period such as 2024-H1 or 2024-Q3."""

    year: int
    label: str  # e.g. "H1", "H2", "Q1", "Q2", "Q3", "Q4", "FY"

    @classmethod
    def parse(cls, raw: str) -> PeriodSpec:
        """Parse a period string like '2024-H1' or '2024-Q3'."""
        parts = raw.strip().split("-", 1)
        if len(parts) != 2:
            raise ValueError(
                f"Period must be in the form YYYY-XX (e.g. 2024-H1, 2024-Q3): got '{raw}'"
            )
        year_str, label = parts
        try:
            year = int(year_str)
        except ValueError:
            raise ValueError(f"Invalid year in period '{raw}'") from None
        valid_labels = {"H1", "H2", "Q1", "Q2", "Q3", "Q4", "FY"}
        if label.upper() not in valid_labels:
            raise ValueError(f"Invalid period label '{label}'. Expected one of {valid_labels}")
        return cls(year=year, label=label.upper())

    def __str__(self) -> str:
        return f"{self.year}-{self.label}"

    def yoy_period(self) -> PeriodSpec:
        """Return the same label period from the prior year (year-over-year baseline)."""
        return PeriodSpec(year=self.year - 1, label=self.label)


class ProjectConfig(BaseModel):
    """Project-level configuration stored in transparency-engine.json."""

    framework: str = "dsa"
    platform_name: str = "My Platform"
    data_dir: str = "data"
    output_dir: str = "reports"
    default_format: OutputFormat = OutputFormat.HTML
    periods: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None = None) -> ProjectConfig:
        config_path = path or Path("transparency-engine.json")
        if config_path.exists():
            with open(config_path) as f:
                return cls.model_validate(json.load(f))
        return cls()

    def save(self, path: Path | None = None) -> None:
        config_path = path or Path("transparency-engine.json")
        with open(config_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)
