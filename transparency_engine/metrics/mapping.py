"""Cross-framework metric mapping.

Different regulators ask for the same underlying data under different names.
This module provides a canonical mapping layer so that a single data pipeline
can feed multiple framework reports.
"""

from __future__ import annotations

from pydantic import BaseModel


class MetricMapping(BaseModel):
    """Maps a framework-specific metric ID to a canonical taxonomy metric."""

    framework_metric_id: str
    canonical_metric_id: str
    transform: str | None = None  # optional transformation note


# Pre-built mappings. In production you would load these from a config file,
# but for the core library it's cleaner to keep them in code.

DSA_MAPPING: list[MetricMapping] = [
    MetricMapping(
        framework_metric_id="notices_received",
        canonical_metric_id="cm_items_reported",
    ),
    MetricMapping(
        framework_metric_id="notices_actioned",
        canonical_metric_id="cm_items_actioned",
    ),
    MetricMapping(
        framework_metric_id="notices_median_response_time",
        canonical_metric_id="cm_median_action_time",
    ),
    MetricMapping(
        framework_metric_id="content_moderation_orders_received",
        canonical_metric_id="gov_orders_received",
    ),
    MetricMapping(
        framework_metric_id="content_moderation_orders_median_response_time",
        canonical_metric_id="gov_median_response_time",
    ),
    MetricMapping(
        framework_metric_id="complaints_received",
        canonical_metric_id="ac_complaints_received",
    ),
    MetricMapping(
        framework_metric_id="automated_detection_items",
        canonical_metric_id="auto_items_flagged",
    ),
    MetricMapping(
        framework_metric_id="account_suspensions_tos",
        canonical_metric_id="ai_accounts_suspended",
    ),
    MetricMapping(
        framework_metric_id="content_moderation_staff_fte",
        canonical_metric_id="staff_moderation_fte",
    ),
    MetricMapping(
        framework_metric_id="active_recipients_eu",
        canonical_metric_id="reach_mau",
        transform="Filter to EU member states only",
    ),
]

OSA_MAPPING: list[MetricMapping] = [
    MetricMapping(
        framework_metric_id="illegal_content_reports_received",
        canonical_metric_id="cm_items_reported",
        transform="Filter to priority illegal content categories",
    ),
    MetricMapping(
        framework_metric_id="illegal_content_actioned",
        canonical_metric_id="cm_items_actioned",
    ),
    MetricMapping(
        framework_metric_id="illegal_content_proactive_detection",
        canonical_metric_id="auto_items_flagged",
        transform="Filter to illegal content only",
    ),
    MetricMapping(
        framework_metric_id="user_complaints_received",
        canonical_metric_id="ac_complaints_received",
    ),
    MetricMapping(
        framework_metric_id="appeals_received",
        canonical_metric_id="ac_appeals_received",
    ),
    MetricMapping(
        framework_metric_id="automated_moderation_actions",
        canonical_metric_id="auto_items_actioned",
    ),
    MetricMapping(
        framework_metric_id="trust_safety_headcount",
        canonical_metric_id="staff_moderation_fte",
    ),
]

_FRAMEWORK_MAPPINGS: dict[str, list[MetricMapping]] = {
    "dsa": DSA_MAPPING,
    "osa": OSA_MAPPING,
}


class FrameworkMetricMapper:
    """Translates between framework-specific and canonical metric identifiers."""

    def __init__(self, framework: str) -> None:
        self.framework = framework.lower()
        mappings = _FRAMEWORK_MAPPINGS.get(self.framework, [])
        self._to_canonical = {m.framework_metric_id: m for m in mappings}
        self._from_canonical = {m.canonical_metric_id: m for m in mappings}

    def to_canonical(self, framework_metric_id: str) -> str | None:
        mapping = self._to_canonical.get(framework_metric_id)
        return mapping.canonical_metric_id if mapping else None

    def from_canonical(self, canonical_metric_id: str) -> str | None:
        mapping = self._from_canonical.get(canonical_metric_id)
        return mapping.framework_metric_id if mapping else None

    def all_mappings(self) -> list[MetricMapping]:
        return list(self._to_canonical.values())
