"""Brazil Lei Geral de Proteção de Dados (LGPD) framework.

Implements transparency reporting obligations under Brazil's LGPD
(Law No. 13,709/2018), as enforced by the ANPD (Autoridade Nacional de
Proteção de Dados). Covers data subject rights, incident notification,
international transfers, and governance disclosures.
"""

from __future__ import annotations

from transparency_engine.config import ReportingPeriod
from transparency_engine.frameworks.base import BaseFramework, MetricRequirement, ReportSection


class LGPDFramework(BaseFramework):
    @property
    def name(self) -> str:
        return "Brazil Lei Geral de Proteção de Dados"

    @property
    def short_code(self) -> str:
        return "lgpd"

    @property
    def reporting_cadence(self) -> ReportingPeriod:
        return ReportingPeriod.ANNUAL

    def metric_requirements(self) -> list[MetricRequirement]:
        return [
            # --- Data subject rights (Art. 17-22) ---
            MetricRequirement(
                metric_id="dsr_requests_received",
                name="Data subject requests received",
                description=(
                    "Total requests from data subjects exercising rights under Art. 17-22, "
                    "including access, correction, deletion, portability, and objection"
                ),
                breakdown_by=["request_type"],
            ),
            MetricRequirement(
                metric_id="dsr_requests_fulfilled",
                name="Data subject requests fulfilled",
                description="Requests completed within the 15-day deadline set by Art. 19",
                breakdown_by=["request_type"],
            ),
            MetricRequirement(
                metric_id="dsr_requests_denied",
                name="Data subject requests denied",
                description="Requests denied and the grounds for denial (Art. 19, §3)",
                breakdown_by=["denial_reason"],
            ),
            MetricRequirement(
                metric_id="dsr_median_response_days",
                name="Median DSR response time (days)",
                description="Median calendar days from request receipt to final response",
                data_type="float",
                aggregation="mean",
            ),
            # --- Incident notification (Art. 48-49) ---
            MetricRequirement(
                metric_id="incidents_reported_to_anpd",
                name="Incidents reported to ANPD",
                description=(
                    "Security incidents involving personal data reported to the ANPD "
                    "within the required timeframe (Art. 48)"
                ),
            ),
            MetricRequirement(
                metric_id="incidents_affecting_data_subjects",
                name="Data subjects affected by incidents",
                description=(
                    "Number of data subjects whose personal data was compromised "
                    "across all reported incidents"
                ),
            ),
            MetricRequirement(
                metric_id="incident_median_detection_to_notification_days",
                name="Median detection-to-notification time (days)",
                description=(
                    "Median calendar days between incident detection and ANPD notification"
                ),
                data_type="float",
                aggregation="mean",
            ),
            # --- International transfers (Art. 33-36) ---
            MetricRequirement(
                metric_id="international_transfers_count",
                name="International data transfers conducted",
                description=(
                    "Number of data transfer arrangements with recipients outside Brazil, "
                    "per permitted mechanisms in Art. 33"
                ),
                breakdown_by=["transfer_mechanism", "destination_country"],
            ),
            MetricRequirement(
                metric_id="international_transfers_standard_clauses",
                name="Transfers covered by standard contractual clauses",
                description=(
                    "Transfers relying on ANPD-approved standard contractual clauses "
                    "as the transfer mechanism"
                ),
                required=False,
            ),
            # --- Processing activities register (Art. 37) ---
            MetricRequirement(
                metric_id="processing_activities_registered",
                name="Processing activities in the register",
                description=(
                    "Number of distinct processing activities recorded in the data "
                    "processing register maintained under Art. 37"
                ),
                aggregation="latest",
            ),
            MetricRequirement(
                metric_id="processing_activities_by_legal_basis",
                name="Processing activities by legal basis",
                description=(
                    "Breakdown of processing activities by the legal basis applied "
                    "(consent, legitimate interest, contractual necessity, legal obligation, etc.)"
                ),
                breakdown_by=["legal_basis"],
            ),
            # --- Governance (Art. 41, 50) ---
            MetricRequirement(
                metric_id="dpo_appointed",
                name="Data Protection Officer appointed",
                description=(
                    "Whether a DPO (Encarregado) has been designated and publicly "
                    "disclosed under Art. 41"
                ),
                data_type="integer",  # 1 = yes, 0 = no
                aggregation="latest",
            ),
            MetricRequirement(
                metric_id="privacy_impact_assessments_conducted",
                name="Privacy impact assessments conducted",
                description=(
                    "Number of Data Protection Impact Assessments (DPIAs) "
                    "completed during the reporting period (Art. 38)"
                ),
                required=False,
            ),
            MetricRequirement(
                metric_id="staff_privacy_training_completions",
                name="Staff privacy training completions",
                description=(
                    "Number of staff who completed data protection training as part of "
                    "the organisation's privacy governance programme"
                ),
                required=False,
            ),
        ]

    def report_sections(self) -> list[ReportSection]:
        return [
            ReportSection(
                section_id="data_subject_rights",
                title="Data Subject Rights (Art. 17-22)",
                description=(
                    "Exercise of individual rights including access, correction, "
                    "deletion, portability, and objection."
                ),
                metrics=[
                    "dsr_requests_received",
                    "dsr_requests_fulfilled",
                    "dsr_requests_denied",
                    "dsr_median_response_days",
                ],
                order=1,
            ),
            ReportSection(
                section_id="incident_management",
                title="Security Incident Notification (Art. 48-49)",
                description=(
                    "Incidents involving personal data reported to the ANPD "
                    "and affected data subjects."
                ),
                metrics=[
                    "incidents_reported_to_anpd",
                    "incidents_affecting_data_subjects",
                    "incident_median_detection_to_notification_days",
                ],
                order=2,
            ),
            ReportSection(
                section_id="international_transfers",
                title="International Data Transfers (Art. 33-36)",
                description="Transfers of personal data to recipients outside Brazil.",
                metrics=[
                    "international_transfers_count",
                    "international_transfers_standard_clauses",
                ],
                order=3,
            ),
            ReportSection(
                section_id="processing_register",
                title="Processing Activities Register (Art. 37)",
                description=(
                    "Overview of personal data processing activities and the legal "
                    "bases on which they rely."
                ),
                metrics=[
                    "processing_activities_registered",
                    "processing_activities_by_legal_basis",
                ],
                order=4,
            ),
            ReportSection(
                section_id="governance",
                title="Governance and Accountability (Art. 41, 50)",
                description=(
                    "Organisational measures, DPO designation, and privacy impact assessments."
                ),
                metrics=[
                    "dpo_appointed",
                    "privacy_impact_assessments_conducted",
                    "staff_privacy_training_completions",
                ],
                order=5,
            ),
        ]
