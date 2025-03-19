"""Metric versioning and backwards compatibility.

Regulatory definitions evolve between reporting periods. This module tracks
which version of a metric definition was in effect for a given period, and
handles backwards-compatible transformations when metric definitions change.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class MetricVersion(BaseModel):
    """A specific version of a metric definition."""

    metric_id: str
    version: str
    effective_from: date
    effective_until: date | None = None
    changes: str = ""
    backwards_compatible: bool = True
    renamed_from: str | None = None


class MetricVersionRegistry:
    """Tracks metric versions across reporting periods."""

    def __init__(self) -> None:
        self._versions: dict[str, list[MetricVersion]] = {}

    def register(self, version: MetricVersion) -> None:
        self._versions.setdefault(version.metric_id, []).append(version)
        self._versions[version.metric_id].sort(key=lambda v: v.effective_from)

    def get_version(self, metric_id: str, as_of: date) -> MetricVersion | None:
        versions = self._versions.get(metric_id, [])
        active = None
        for v in versions:
            if v.effective_from <= as_of:
                if v.effective_until is None or as_of <= v.effective_until:
                    active = v
        return active

    def is_compatible(self, metric_id: str, period_start: date, period_end: date) -> bool:
        """Check if the metric definition is stable across the full period."""
        versions = self._versions.get(metric_id, [])
        relevant = [
            v
            for v in versions
            if v.effective_from <= period_end
            and (v.effective_until is None or v.effective_until >= period_start)
        ]
        if len(relevant) <= 1:
            return True
        return all(v.backwards_compatible for v in relevant)

    def list_metrics(self) -> list[str]:
        return sorted(self._versions.keys())

    def history(self, metric_id: str) -> list[MetricVersion]:
        return list(self._versions.get(metric_id, []))


# Default registry with known version milestones
_DEFAULT_REGISTRY = MetricVersionRegistry()

_DEFAULT_VERSIONS = [
    MetricVersion(
        metric_id="cm_items_reported",
        version="1.0",
        effective_from=date(2024, 1, 1),
        changes="Initial definition aligned with DSA Transparency Database schema.",
    ),
    MetricVersion(
        metric_id="cm_items_actioned",
        version="1.0",
        effective_from=date(2024, 1, 1),
        changes="Initial definition.",
    ),
    MetricVersion(
        metric_id="cm_items_actioned",
        version="1.1",
        effective_from=date(2024, 7, 1),
        changes=(
            "Added 'labelling' as a valid action_type following DSA delegated regulation update."
        ),
        backwards_compatible=True,
    ),
    MetricVersion(
        metric_id="gov_orders_received",
        version="1.0",
        effective_from=date(2024, 1, 1),
        changes="Initial definition.",
    ),
    MetricVersion(
        metric_id="auto_items_flagged",
        version="1.0",
        effective_from=date(2024, 1, 1),
        changes="Initial definition.",
    ),
    MetricVersion(
        metric_id="auto_false_positive_rate",
        version="1.0",
        effective_from=date(2024, 1, 1),
        changes="Initial definition. Denominator = total automated actions.",
    ),
]

for _v in _DEFAULT_VERSIONS:
    _DEFAULT_REGISTRY.register(_v)


def get_default_registry() -> MetricVersionRegistry:
    return _DEFAULT_REGISTRY
