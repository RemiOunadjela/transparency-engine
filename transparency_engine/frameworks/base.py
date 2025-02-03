"""Base framework defining the interface every regulatory framework must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from transparency_engine.config import ReportingPeriod


class MetricRequirement(BaseModel):
    """Describes a single metric that a framework mandates."""

    metric_id: str
    name: str
    description: str
    required: bool = True
    data_type: str = "integer"  # integer, float, percentage, duration_hours
    aggregation: str = "sum"  # sum, mean, latest, count
    breakdown_by: list[str] = Field(default_factory=list)  # e.g. ["country", "content_type"]


class ReportSection(BaseModel):
    """A section within a regulatory report."""

    section_id: str
    title: str
    description: str
    metrics: list[str]  # metric IDs required in this section
    order: int = 0


class BaseFramework(ABC):
    """Abstract base for regulatory transparency frameworks.

    Subclasses define the exact metrics, report sections, and validation
    rules mandated by a specific regulation (DSA, OSA, etc.).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable framework name."""

    @property
    @abstractmethod
    def short_code(self) -> str:
        """Short identifier used in filenames and CLI flags."""

    @property
    @abstractmethod
    def reporting_cadence(self) -> ReportingPeriod:
        """Default reporting cadence for this framework."""

    @abstractmethod
    def metric_requirements(self) -> list[MetricRequirement]:
        """All metrics required by this framework."""

    @abstractmethod
    def report_sections(self) -> list[ReportSection]:
        """Ordered list of report sections."""

    def required_metric_ids(self) -> set[str]:
        return {m.metric_id for m in self.metric_requirements() if m.required}

    def optional_metric_ids(self) -> set[str]:
        return {m.metric_id for m in self.metric_requirements() if not m.required}

    def validate_completeness(self, provided_metrics: set[str]) -> list[str]:
        """Return a list of missing required metric IDs."""
        return sorted(self.required_metric_ids() - provided_metrics)

    def get_template_name(self) -> str:
        return f"{self.short_code}_report.html"
