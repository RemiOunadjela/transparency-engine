"""EU Digital Services Act (DSA) framework.

Implements transparency reporting obligations under Articles 15, 24, and 42
of Regulation (EU) 2022/2065. Metric definitions follow the DSA Transparency
Database schema and VLOP-specific disclosure requirements.
"""

from __future__ import annotations

from transparency_engine.config import ReportingPeriod
from transparency_engine.frameworks.base import BaseFramework, MetricRequirement, ReportSection


class DSAFramework(BaseFramework):
    @property
    def name(self) -> str:
        return "EU Digital Services Act"

    @property
    def short_code(self) -> str:
        return "dsa"

    @property
    def reporting_cadence(self) -> ReportingPeriod:
        return ReportingPeriod.SEMI_ANNUAL

    def metric_requirements(self) -> list[MetricRequirement]:
        return [
            # --- Article 15: Content moderation ---
            MetricRequirement(
                metric_id="content_moderation_orders_received",
                name="Orders received from Member State authorities",
                description=(
                    "Orders received from Member State judicial "
                    "or administrative authorities, per Art. 9"
                ),
                breakdown_by=["member_state", "order_type"],
            ),
            MetricRequirement(
                metric_id="content_moderation_orders_median_response_time",
                name="Median response time to orders",
                description="Median time to inform the issuing authority of the action taken",
                data_type="duration_hours",
                aggregation="mean",
            ),
            MetricRequirement(
                metric_id="notices_received",
                name="Notices submitted via notice-and-action mechanisms",
                description=(
                    "Notices submitted under Art. 16, broken down "
                    "by category of alleged illegal content"
                ),
                breakdown_by=["content_type", "submission_channel"],
            ),
            MetricRequirement(
                metric_id="notices_actioned",
                name="Notices acted upon",
                description=("Notices resulting in content removal, disabling, or demotion"),
                breakdown_by=["content_type", "action_type"],
            ),
            MetricRequirement(
                metric_id="notices_median_response_time",
                name="Median response time to notices",
                description="Median time between receipt of notice and action taken",
                data_type="duration_hours",
                aggregation="mean",
            ),
            MetricRequirement(
                metric_id="complaints_received",
                name="Complaints received via internal complaint-handling",
                description="Complaints lodged under Article 20, broken down by outcome",
                breakdown_by=["complaint_basis", "outcome"],
            ),
            MetricRequirement(
                metric_id="complaints_reversed",
                name="Decisions reversed after complaint",
                description="Number of moderation decisions reversed following internal complaint",
            ),
            MetricRequirement(
                metric_id="complaints_median_resolution_time",
                name="Median complaint resolution time",
                description="Median number of days from complaint to resolution",
                data_type="duration_hours",
                aggregation="mean",
            ),
            MetricRequirement(
                metric_id="out_of_court_disputes",
                name="Disputes submitted to out-of-court settlement bodies",
                description="Number of disputes referred under Article 21",
            ),
            MetricRequirement(
                metric_id="out_of_court_outcomes_upheld",
                name="Out-of-court outcomes in favour of platform",
                description=(
                    "Out-of-court settlement outcomes that upheld the platform's original decision"
                ),
            ),
            MetricRequirement(
                metric_id="account_suspensions_tos",
                name="Account suspensions for ToS violations",
                description="Accounts suspended for violations of terms of service",
                breakdown_by=["violation_category"],
            ),
            MetricRequirement(
                metric_id="account_suspensions_manifestly_illegal",
                name="Account suspensions for manifestly illegal content",
                description="Accounts suspended for provision of manifestly illegal content",
            ),
            MetricRequirement(
                metric_id="content_moderation_staff_fte",
                name="Content moderation FTE",
                description=(
                    "FTE staff dedicated to content moderation, including language capabilities"
                ),
                data_type="float",
                aggregation="latest",
                breakdown_by=["language"],
            ),
            # --- Article 24: Automated means ---
            MetricRequirement(
                metric_id="automated_detection_items",
                name="Items identified by automated means",
                description=("Content items flagged or actioned by automated detection systems"),
                breakdown_by=["content_type", "detection_method"],
            ),
            MetricRequirement(
                metric_id="automated_detection_accuracy",
                name="Automated detection accuracy indicators",
                description=(
                    "Error rates and accuracy indicators for automated content moderation tools"
                ),
                data_type="percentage",
                aggregation="mean",
                required=False,
            ),
            # --- Article 42: VLOP/VLOSE additional ---
            MetricRequirement(
                metric_id="active_recipients_eu",
                name="Average monthly active recipients in the EU",
                description=(
                    "Average monthly active recipients of the service in the EU, per Art. 24(2)"
                ),
                data_type="integer",
                aggregation="mean",
                breakdown_by=["member_state"],
                required=False,
            ),
            MetricRequirement(
                metric_id="content_removals_own_initiative",
                name="Content removed on provider's own initiative",
                description="Items removed proactively without external notice or order",
                breakdown_by=["content_type", "policy_ground"],
            ),
        ]

    def report_sections(self) -> list[ReportSection]:
        return [
            ReportSection(
                section_id="orders",
                title="Orders from Member State Authorities (Art. 9, 15(1)(a))",
                description="Statistics on orders received from national authorities.",
                metrics=[
                    "content_moderation_orders_received",
                    "content_moderation_orders_median_response_time",
                ],
                order=1,
            ),
            ReportSection(
                section_id="notices",
                title="Notice-and-Action (Art. 16, 15(1)(b))",
                description="Notices received and outcomes under Article 16.",
                metrics=[
                    "notices_received",
                    "notices_actioned",
                    "notices_median_response_time",
                ],
                order=2,
            ),
            ReportSection(
                section_id="complaints",
                title="Internal Complaint-Handling (Art. 20, 15(1)(c))",
                description="Complaints processed through the internal system.",
                metrics=[
                    "complaints_received",
                    "complaints_reversed",
                    "complaints_median_resolution_time",
                ],
                order=3,
            ),
            ReportSection(
                section_id="out_of_court",
                title="Out-of-Court Dispute Settlement (Art. 21, 15(1)(d))",
                description="Disputes referred to certified out-of-court bodies.",
                metrics=[
                    "out_of_court_disputes",
                    "out_of_court_outcomes_upheld",
                ],
                order=4,
            ),
            ReportSection(
                section_id="suspensions",
                title="Account Suspensions (Art. 23, 15(1)(e))",
                description="Accounts restricted or suspended during the reporting period.",
                metrics=[
                    "account_suspensions_tos",
                    "account_suspensions_manifestly_illegal",
                ],
                order=5,
            ),
            ReportSection(
                section_id="automated",
                title="Use of Automated Means (Art. 15(1)(e), Art. 24)",
                description="Deployment and performance of automated content moderation tools.",
                metrics=[
                    "automated_detection_items",
                    "automated_detection_accuracy",
                    "content_removals_own_initiative",
                ],
                order=6,
            ),
            ReportSection(
                section_id="resources",
                title="Content Moderation Resources (Art. 15(1)(f))",
                description="Human resources allocated to content moderation.",
                metrics=["content_moderation_staff_fte"],
                order=7,
            ),
            ReportSection(
                section_id="reach",
                title="Active Recipients (Art. 24(2), Art. 42)",
                description="Average monthly active recipients in the EU -- VLOP/VLOSE only.",
                metrics=["active_recipients_eu"],
                order=8,
            ),
        ]
