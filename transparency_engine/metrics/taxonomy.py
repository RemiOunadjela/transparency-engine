"""Standard Trust & Safety metric taxonomy.

Provides a canonical set of metric definitions that can be mapped to
any regulatory framework. Built from practical experience delivering
DSA, OSA, and voluntary transparency reports.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class MetricCategory(str, Enum):
    CONTENT_MODERATION = "content_moderation"
    GOVERNMENT_REQUESTS = "government_requests"
    AUTOMATED_ENFORCEMENT = "automated_enforcement"
    USER_REPORTING = "user_reporting"
    APPEALS_AND_COMPLAINTS = "appeals_and_complaints"
    ACCOUNT_INTEGRITY = "account_integrity"
    STAFFING = "staffing"
    REACH = "reach"


class MetricDefinition(BaseModel):
    """Canonical metric definition in the transparency-engine taxonomy."""

    metric_id: str
    name: str
    category: MetricCategory
    description: str
    data_type: str = "integer"
    unit: str = "count"
    aggregation: str = "sum"
    breakdown_dimensions: list[str] = Field(default_factory=list)
    version: str = "1.0"

    def supports_breakdown(self, dimension: str) -> bool:
        return dimension in self.breakdown_dimensions


# Canonical taxonomy -- the source of truth that framework-specific metric IDs map onto.
METRIC_TAXONOMY: dict[str, MetricDefinition] = {}

_RAW_DEFINITIONS: list[dict] = [
    # --- Content moderation ---
    {
        "metric_id": "cm_items_reported",
        "name": "Content items reported by users",
        "category": MetricCategory.CONTENT_MODERATION,
        "description": (
            "Total number of individual content items reported through user-facing reporting flows."
        ),
        "breakdown_dimensions": ["content_type", "reporting_channel", "country"],
    },
    {
        "metric_id": "cm_items_actioned",
        "name": "Content items actioned",
        "category": MetricCategory.CONTENT_MODERATION,
        "description": (
            "Content items where an enforcement action was taken "
            "(removal, restriction, demotion, labelling)."
        ),
        "breakdown_dimensions": ["content_type", "action_type", "policy_area"],
    },
    {
        "metric_id": "cm_removal_rate",
        "name": "Content removal rate",
        "category": MetricCategory.CONTENT_MODERATION,
        "description": "Proportion of reported content items that were removed.",
        "data_type": "percentage",
        "unit": "percent",
        "aggregation": "mean",
    },
    {
        "metric_id": "cm_median_action_time",
        "name": "Median time to action (hours)",
        "category": MetricCategory.CONTENT_MODERATION,
        "description": "Median elapsed hours from content report to enforcement action.",
        "data_type": "float",
        "unit": "hours",
        "aggregation": "mean",
    },
    {
        "metric_id": "cm_proactive_detection_rate",
        "name": "Proactive detection rate",
        "category": MetricCategory.CONTENT_MODERATION,
        "description": "Share of actioned content identified proactively (before user report).",
        "data_type": "percentage",
        "unit": "percent",
        "aggregation": "mean",
    },
    # --- Government requests ---
    {
        "metric_id": "gov_orders_received",
        "name": "Government orders received",
        "category": MetricCategory.GOVERNMENT_REQUESTS,
        "description": "Legal orders received from government or judicial authorities.",
        "breakdown_dimensions": ["country", "order_type"],
    },
    {
        "metric_id": "gov_compliance_rate",
        "name": "Government order compliance rate",
        "category": MetricCategory.GOVERNMENT_REQUESTS,
        "description": "Percentage of government orders complied with (full or partial).",
        "data_type": "percentage",
        "unit": "percent",
        "aggregation": "mean",
        "breakdown_dimensions": ["country"],
    },
    {
        "metric_id": "gov_median_response_time",
        "name": "Median response time to government orders",
        "category": MetricCategory.GOVERNMENT_REQUESTS,
        "description": "Median hours from receipt of order to platform response.",
        "data_type": "float",
        "unit": "hours",
        "aggregation": "mean",
    },
    # --- Automated enforcement ---
    {
        "metric_id": "auto_items_flagged",
        "name": "Items flagged by automated systems",
        "category": MetricCategory.AUTOMATED_ENFORCEMENT,
        "description": (
            "Content items flagged by hash-matching, classifiers, or other automated tools."
        ),
        "breakdown_dimensions": ["content_type", "system_type"],
    },
    {
        "metric_id": "auto_items_actioned",
        "name": "Items actioned by automated systems",
        "category": MetricCategory.AUTOMATED_ENFORCEMENT,
        "description": (
            "Content items where an automated system took enforcement action without human review."
        ),
        "breakdown_dimensions": ["content_type", "action_type"],
    },
    {
        "metric_id": "auto_false_positive_rate",
        "name": "Automated false positive rate",
        "category": MetricCategory.AUTOMATED_ENFORCEMENT,
        "description": "Estimated rate of incorrect automated enforcement actions.",
        "data_type": "percentage",
        "unit": "percent",
        "aggregation": "mean",
    },
    {
        "metric_id": "auto_overturn_rate",
        "name": "Automated action overturn rate",
        "category": MetricCategory.AUTOMATED_ENFORCEMENT,
        "description": "Percentage of automated actions reversed on human review or appeal.",
        "data_type": "percentage",
        "unit": "percent",
        "aggregation": "mean",
    },
    # --- User reporting ---
    {
        "metric_id": "ur_report_volume",
        "name": "User report volume",
        "category": MetricCategory.USER_REPORTING,
        "description": "Total reports submitted by users across all channels.",
        "breakdown_dimensions": ["reporting_channel", "content_type"],
    },
    {
        "metric_id": "ur_median_resolution_time",
        "name": "Median report resolution time",
        "category": MetricCategory.USER_REPORTING,
        "description": "Median hours from user report submission to resolution.",
        "data_type": "float",
        "unit": "hours",
        "aggregation": "mean",
    },
    # --- Appeals and complaints ---
    {
        "metric_id": "ac_appeals_received",
        "name": "Appeals received",
        "category": MetricCategory.APPEALS_AND_COMPLAINTS,
        "description": "Total appeals of content moderation decisions.",
    },
    {
        "metric_id": "ac_appeal_overturn_rate",
        "name": "Appeal overturn rate",
        "category": MetricCategory.APPEALS_AND_COMPLAINTS,
        "description": "Percentage of appeals where the original decision was reversed.",
        "data_type": "percentage",
        "unit": "percent",
        "aggregation": "mean",
    },
    {
        "metric_id": "ac_complaints_received",
        "name": "Complaints received",
        "category": MetricCategory.APPEALS_AND_COMPLAINTS,
        "description": "Complaints lodged through internal complaint-handling systems.",
        "breakdown_dimensions": ["complaint_type", "outcome"],
    },
    # --- Account integrity ---
    {
        "metric_id": "ai_accounts_suspended",
        "name": "Accounts suspended",
        "category": MetricCategory.ACCOUNT_INTEGRITY,
        "description": "Accounts suspended for policy violations.",
        "breakdown_dimensions": ["violation_category"],
    },
    {
        "metric_id": "ai_accounts_reinstated",
        "name": "Accounts reinstated",
        "category": MetricCategory.ACCOUNT_INTEGRITY,
        "description": "Previously suspended accounts reinstated after review or appeal.",
    },
    # --- Staffing ---
    {
        "metric_id": "staff_moderation_fte",
        "name": "Content moderation FTE",
        "category": MetricCategory.STAFFING,
        "description": "Full-time-equivalent headcount for content moderation.",
        "data_type": "float",
        "unit": "fte",
        "aggregation": "latest",
        "breakdown_dimensions": ["language", "region"],
    },
    # --- Reach ---
    {
        "metric_id": "reach_mau",
        "name": "Monthly active users",
        "category": MetricCategory.REACH,
        "description": "Average monthly active users/recipients during the period.",
        "aggregation": "mean",
        "breakdown_dimensions": ["country", "region"],
    },
]


def _build_taxonomy() -> None:
    for entry in _RAW_DEFINITIONS:
        defn = MetricDefinition(**entry)
        METRIC_TAXONOMY[defn.metric_id] = defn


_build_taxonomy()
