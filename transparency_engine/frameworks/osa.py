"""UK Online Safety Act (OSA) framework.

Implements transparency reporting requirements as outlined in the
Online Safety Act 2023 and OFCOM's draft Transparency Reporting
guidance (published March 2024). Covers user-to-user services
and search services.
"""

from __future__ import annotations

from transparency_engine.config import ReportingPeriod
from transparency_engine.frameworks.base import BaseFramework, MetricRequirement, ReportSection


class OSAFramework(BaseFramework):
    @property
    def name(self) -> str:
        return "UK Online Safety Act"

    @property
    def short_code(self) -> str:
        return "osa"

    @property
    def reporting_cadence(self) -> ReportingPeriod:
        return ReportingPeriod.ANNUAL

    def metric_requirements(self) -> list[MetricRequirement]:
        return [
            # --- Illegal content duties ---
            MetricRequirement(
                metric_id="illegal_content_reports_received",
                name="Reports of illegal content received",
                description="Total user reports relating to priority illegal content categories",
                breakdown_by=["content_category", "reporting_channel"],
            ),
            MetricRequirement(
                metric_id="illegal_content_actioned",
                name="Illegal content items actioned",
                description="Number of items removed or restricted following assessment as illegal",
                breakdown_by=["content_category", "action_type"],
            ),
            MetricRequirement(
                metric_id="illegal_content_proactive_detection",
                name="Proactively detected illegal content",
                description="Items identified through proactive technology before user report",
                breakdown_by=["content_category", "detection_method"],
            ),
            MetricRequirement(
                metric_id="csam_reports_ncmec",
                name="CSAM reports submitted to NCMEC/NCA",
                description=("CSAM reports submitted to the National Crime Agency or NCMEC"),
            ),
            MetricRequirement(
                metric_id="terrorism_content_removals",
                name="Terrorism content removed",
                description="Items of terrorism content removed under the terrorism duty",
                breakdown_by=["referral_source"],
            ),
            # --- Children's safety duties ---
            MetricRequirement(
                metric_id="age_assurance_measures",
                name="Age assurance measures deployed",
                description=("Effectiveness metrics for age verification or estimation measures"),
                data_type="integer",
                aggregation="latest",
            ),
            MetricRequirement(
                metric_id="children_content_actions",
                name="Content actions for children's safety",
                description=("Content moderation actions taken under children's safety duties"),
                breakdown_by=["content_category", "action_type"],
            ),
            # --- User empowerment and complaints ---
            MetricRequirement(
                metric_id="user_complaints_received",
                name="User complaints received",
                description="Total complaints submitted through the platform's complaints process",
                breakdown_by=["complaint_type"],
            ),
            MetricRequirement(
                metric_id="user_complaints_resolved",
                name="User complaints resolved",
                description="Complaints resolved within the reporting period",
                breakdown_by=["outcome"],
            ),
            MetricRequirement(
                metric_id="user_complaints_median_resolution_days",
                name="Median complaint resolution time (days)",
                description="Median calendar days from complaint submission to final resolution",
                data_type="float",
                aggregation="mean",
            ),
            MetricRequirement(
                metric_id="appeals_received",
                name="Appeals of moderation decisions",
                description="Number of appeals submitted against content moderation decisions",
            ),
            MetricRequirement(
                metric_id="appeals_upheld",
                name="Appeals upheld (decision reversed)",
                description="Appeals where the original moderation decision was reversed",
            ),
            # --- Automated systems ---
            MetricRequirement(
                metric_id="automated_moderation_actions",
                name="Content actions taken by automated systems",
                description=(
                    "Moderation actions initiated by automated "
                    "systems (hash-matching, classifiers, etc.)"
                ),
                breakdown_by=["system_type", "content_category"],
            ),
            MetricRequirement(
                metric_id="automated_moderation_overturned",
                name="Automated decisions overturned on review",
                description="Automated moderation actions reversed after human review or appeal",
            ),
            MetricRequirement(
                metric_id="human_review_queue_volume",
                name="Items sent to human review",
                description="Total items escalated from automated systems to human moderators",
            ),
            # --- Staffing and governance ---
            MetricRequirement(
                metric_id="trust_safety_headcount",
                name="Trust & Safety headcount",
                description="Number of staff (FTE) dedicated to trust and safety functions",
                data_type="float",
                aggregation="latest",
            ),
            MetricRequirement(
                metric_id="moderator_wellbeing_measures",
                name="Moderator wellbeing measures in place",
                description="Count of active wellbeing support measures for content moderators",
                data_type="integer",
                aggregation="latest",
                required=False,
            ),
        ]

    def report_sections(self) -> list[ReportSection]:
        return [
            ReportSection(
                section_id="illegal_content",
                title="Illegal Content Duties",
                description="Actions taken to identify and remove priority illegal content.",
                metrics=[
                    "illegal_content_reports_received",
                    "illegal_content_actioned",
                    "illegal_content_proactive_detection",
                    "csam_reports_ncmec",
                    "terrorism_content_removals",
                ],
                order=1,
            ),
            ReportSection(
                section_id="children_safety",
                title="Children's Safety Duties",
                description="Measures to protect children using the service.",
                metrics=[
                    "age_assurance_measures",
                    "children_content_actions",
                ],
                order=2,
            ),
            ReportSection(
                section_id="complaints_and_appeals",
                title="Complaints and Appeals",
                description="User complaints handling and appeal outcomes.",
                metrics=[
                    "user_complaints_received",
                    "user_complaints_resolved",
                    "user_complaints_median_resolution_days",
                    "appeals_received",
                    "appeals_upheld",
                ],
                order=3,
            ),
            ReportSection(
                section_id="automated_systems",
                title="Use of Automated Systems",
                description="Deployment and oversight of automated content moderation.",
                metrics=[
                    "automated_moderation_actions",
                    "automated_moderation_overturned",
                    "human_review_queue_volume",
                ],
                order=4,
            ),
            ReportSection(
                section_id="resources_governance",
                title="Staffing and Governance",
                description="Resources dedicated to trust and safety.",
                metrics=[
                    "trust_safety_headcount",
                    "moderator_wellbeing_measures",
                ],
                order=5,
            ),
        ]
