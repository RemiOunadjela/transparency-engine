"""Japan Act on the Protection of Personal Information (APPI) framework.

Implements transparency reporting obligations under Japan's APPI
(Act No. 57 of 2003, substantially revised April 2022), as enforced by
the Personal Information Protection Commission (PPC). Covers individual
rights, incident notification, cross-border transfers, and governance
disclosures.
"""

from __future__ import annotations

from transparency_engine.config import ReportingPeriod
from transparency_engine.frameworks.base import BaseFramework, MetricRequirement, ReportSection


class APPIFramework(BaseFramework):
    @property
    def name(self) -> str:
        return "Japan Act on the Protection of Personal Information"

    @property
    def short_code(self) -> str:
        return "appi"

    @property
    def reporting_cadence(self) -> ReportingPeriod:
        return ReportingPeriod.ANNUAL

    def metric_requirements(self) -> list[MetricRequirement]:
        return [
            # --- Individual rights requests (Art. 32-39) ---
            MetricRequirement(
                metric_id="disclosure_requests_received",
                name="Disclosure requests received",
                description=(
                    "Total requests from principals (data subjects) to disclose retained "
                    "personal information under Art. 33"
                ),
                breakdown_by=["request_type"],
            ),
            MetricRequirement(
                metric_id="disclosure_requests_fulfilled",
                name="Disclosure requests fulfilled",
                description=(
                    "Requests fulfilled within the two-week statutory deadline set by Art. 38"
                ),
                breakdown_by=["request_type"],
            ),
            MetricRequirement(
                metric_id="disclosure_requests_denied",
                name="Disclosure requests denied",
                description=("Requests denied and the permissible grounds cited under Art. 33, §2"),
                breakdown_by=["denial_reason"],
            ),
            MetricRequirement(
                metric_id="correction_cessation_requests_received",
                name="Correction and use-cessation requests received",
                description=(
                    "Requests for correction, addition, deletion (Art. 34) or cessation "
                    "of use and erasure (Art. 35) of personal information"
                ),
                breakdown_by=["request_type"],
            ),
            MetricRequirement(
                metric_id="rights_requests_median_response_days",
                name="Median rights-request response time (days)",
                description=(
                    "Median calendar days from request receipt to final response across "
                    "all individual-rights request types"
                ),
                data_type="float",
                aggregation="mean",
            ),
            # --- Security incident notification (Art. 26) ---
            MetricRequirement(
                metric_id="incidents_reported_to_ppc",
                name="Incidents reported to the PPC",
                description=(
                    "Security incidents involving personal information reported to the Personal "
                    "Information Protection Commission within the required 30-day period (Art. 26)"
                ),
            ),
            MetricRequirement(
                metric_id="incidents_affecting_principals",
                name="Data subjects affected by incidents",
                description=(
                    "Number of principals whose personal information was compromised "
                    "across all notifiable incidents"
                ),
            ),
            MetricRequirement(
                metric_id="incident_median_detection_to_notification_days",
                name="Median detection-to-notification time (days)",
                description=(
                    "Median calendar days between incident detection and PPC notification"
                ),
                data_type="float",
                aggregation="mean",
            ),
            # --- Third-party provision and cross-border transfers (Art. 24, 27-28) ---
            MetricRequirement(
                metric_id="third_party_disclosures_domestic",
                name="Domestic third-party disclosures",
                description=(
                    "Number of disclosures of personal information to domestic third parties "
                    "under Art. 27, including opt-out arrangements where applicable"
                ),
                breakdown_by=["legal_basis"],
            ),
            MetricRequirement(
                metric_id="cross_border_transfers_count",
                name="Cross-border data transfers conducted",
                description=(
                    "Number of transfers of personal information to foreign recipients "
                    "under the permitted mechanisms in Art. 28"
                ),
                breakdown_by=["transfer_mechanism", "destination_country"],
            ),
            MetricRequirement(
                metric_id="cross_border_transfers_with_consent",
                name="Cross-border transfers based on principal consent",
                description=(
                    "Transfers relying on explicit principal consent as the transfer "
                    "mechanism under Art. 28, §1"
                ),
                required=False,
            ),
            # --- Security management (Art. 23-25) ---
            MetricRequirement(
                metric_id="security_controls_reviewed",
                name="Security control reviews conducted",
                description=(
                    "Number of formal reviews of technical and organisational security "
                    "measures required under Art. 23"
                ),
                required=False,
            ),
            MetricRequirement(
                metric_id="processor_supervision_audits",
                name="Personal information processor supervision audits",
                description=(
                    "Audits of subcontractors and processors conducted to verify adequate "
                    "supervision under Art. 25"
                ),
                required=False,
            ),
            # --- Governance ---
            MetricRequirement(
                metric_id="privacy_manager_appointed",
                name="Personal information protection manager appointed",
                description=(
                    "Whether a dedicated personal information protection manager or "
                    "equivalent role has been designated"
                ),
                data_type="integer",  # 1 = yes, 0 = no
                aggregation="latest",
            ),
            MetricRequirement(
                metric_id="staff_privacy_training_completions",
                name="Staff privacy training completions",
                description=(
                    "Number of staff who completed personal information handling training "
                    "during the reporting period"
                ),
                required=False,
            ),
            MetricRequirement(
                metric_id="anonymously_processed_datasets_created",
                name="Anonymously processed information datasets created",
                description=(
                    "Datasets created by anonymising personal information and published "
                    "under Art. 43-46 during the reporting period"
                ),
                required=False,
            ),
        ]

    def report_sections(self) -> list[ReportSection]:
        return [
            ReportSection(
                section_id="individual_rights",
                title="Individual Rights (Art. 32-39)",
                description=(
                    "Exercise of principals' rights to disclosure, correction, deletion, "
                    "cessation of use, and third-party provision cessation."
                ),
                metrics=[
                    "disclosure_requests_received",
                    "disclosure_requests_fulfilled",
                    "disclosure_requests_denied",
                    "correction_cessation_requests_received",
                    "rights_requests_median_response_days",
                ],
                order=1,
            ),
            ReportSection(
                section_id="incident_notification",
                title="Security Incident Notification (Art. 26)",
                description=(
                    "Notifiable incidents involving personal information reported to the "
                    "PPC and affected principals."
                ),
                metrics=[
                    "incidents_reported_to_ppc",
                    "incidents_affecting_principals",
                    "incident_median_detection_to_notification_days",
                ],
                order=2,
            ),
            ReportSection(
                section_id="third_party_and_cross_border",
                title="Third-Party Provision and Cross-border Transfers (Art. 24, 27-28)",
                description=(
                    "Disclosures to domestic third parties and transfers to foreign "
                    "recipients, including the mechanisms used."
                ),
                metrics=[
                    "third_party_disclosures_domestic",
                    "cross_border_transfers_count",
                    "cross_border_transfers_with_consent",
                ],
                order=3,
            ),
            ReportSection(
                section_id="security_management",
                title="Security Management (Art. 23-25)",
                description=(
                    "Organisational and technical measures in place to prevent unauthorised "
                    "disclosure, loss, or damage of personal information."
                ),
                metrics=[
                    "security_controls_reviewed",
                    "processor_supervision_audits",
                ],
                order=4,
            ),
            ReportSection(
                section_id="governance",
                title="Governance and Accountability",
                description=(
                    "Organisational accountability measures including designated roles, "
                    "staff training, and anonymisation activities."
                ),
                metrics=[
                    "privacy_manager_appointed",
                    "staff_privacy_training_completions",
                    "anonymously_processed_datasets_created",
                ],
                order=5,
            ),
        ]
