"""Tests for regulatory framework definitions."""

import json

import pytest

from transparency_engine.config import ReportingPeriod
from transparency_engine.frameworks import REGISTRY, get_framework
from transparency_engine.frameworks.appi import APPIFramework
from transparency_engine.frameworks.custom import CustomFramework
from transparency_engine.frameworks.dsa import DSAFramework
from transparency_engine.frameworks.lgpd import LGPDFramework
from transparency_engine.frameworks.osa import OSAFramework


class TestAPPIFramework:
    def test_basic_properties(self, appi_framework):
        assert appi_framework.name == "Japan Act on the Protection of Personal Information"
        assert appi_framework.short_code == "appi"
        assert appi_framework.reporting_cadence == ReportingPeriod.ANNUAL

    def test_has_individual_rights_metrics(self, appi_framework):
        ids = {m.metric_id for m in appi_framework.metric_requirements()}
        assert "disclosure_requests_received" in ids
        assert "disclosure_requests_fulfilled" in ids
        assert "disclosure_requests_denied" in ids
        assert "rights_requests_median_response_days" in ids

    def test_has_incident_metrics(self, appi_framework):
        ids = {m.metric_id for m in appi_framework.metric_requirements()}
        assert "incidents_reported_to_ppc" in ids
        assert "incidents_affecting_principals" in ids
        assert "incident_median_detection_to_notification_days" in ids

    def test_has_transfer_metrics(self, appi_framework):
        ids = {m.metric_id for m in appi_framework.metric_requirements()}
        assert "cross_border_transfers_count" in ids
        assert "third_party_disclosures_domestic" in ids

    def test_has_governance_metrics(self, appi_framework):
        ids = {m.metric_id for m in appi_framework.metric_requirements()}
        assert "privacy_manager_appointed" in ids

    def test_report_sections_ordered(self, appi_framework):
        sections = appi_framework.report_sections()
        orders = [s.order for s in sections]
        assert orders == sorted(orders)

    def test_section_metrics_reference_valid_ids(self, appi_framework):
        valid_ids = {m.metric_id for m in appi_framework.metric_requirements()}
        for section in appi_framework.report_sections():
            for mid in section.metrics:
                assert mid in valid_ids, (
                    f"Section '{section.section_id}' references unknown metric '{mid}'"
                )

    def test_validate_completeness_required_only(self, appi_framework):
        required_ids = appi_framework.required_metric_ids()
        assert appi_framework.validate_completeness(required_ids) == []

    def test_validate_completeness_missing(self, appi_framework):
        missing = appi_framework.validate_completeness(set())
        assert "disclosure_requests_received" in missing
        assert "incidents_reported_to_ppc" in missing

    def test_template_name(self, appi_framework):
        assert appi_framework.get_template_name() == "appi_report.html"


class TestDSAFramework:
    def test_basic_properties(self, dsa_framework):
        assert dsa_framework.name == "EU Digital Services Act"
        assert dsa_framework.short_code == "dsa"
        assert dsa_framework.reporting_cadence == ReportingPeriod.SEMI_ANNUAL

    def test_has_required_metrics(self, dsa_framework):
        metrics = dsa_framework.metric_requirements()
        assert len(metrics) > 10
        ids = {m.metric_id for m in metrics}
        assert "notices_received" in ids
        assert "content_moderation_orders_received" in ids
        assert "automated_detection_items" in ids

    def test_report_sections_ordered(self, dsa_framework):
        sections = dsa_framework.report_sections()
        orders = [s.order for s in sections]
        assert orders == sorted(orders)

    def test_section_metrics_reference_valid_ids(self, dsa_framework):
        valid_ids = {m.metric_id for m in dsa_framework.metric_requirements()}
        for section in dsa_framework.report_sections():
            for mid in section.metrics:
                assert mid in valid_ids, (
                    f"Section '{section.section_id}' references unknown metric '{mid}'"
                )

    def test_validate_completeness_all_present(self, dsa_framework):
        all_ids = {m.metric_id for m in dsa_framework.metric_requirements()}
        assert dsa_framework.validate_completeness(all_ids) == []

    def test_validate_completeness_missing(self, dsa_framework):
        missing = dsa_framework.validate_completeness(set())
        assert len(missing) > 0
        assert "notices_received" in missing

    def test_template_name(self, dsa_framework):
        assert dsa_framework.get_template_name() == "dsa_report.html"


class TestLGPDFramework:
    def test_basic_properties(self, lgpd_framework):
        assert lgpd_framework.name == "Brazil Lei Geral de Proteção de Dados"
        assert lgpd_framework.short_code == "lgpd"
        assert lgpd_framework.reporting_cadence == ReportingPeriod.ANNUAL

    def test_has_dsr_metrics(self, lgpd_framework):
        ids = {m.metric_id for m in lgpd_framework.metric_requirements()}
        assert "dsr_requests_received" in ids
        assert "dsr_requests_fulfilled" in ids
        assert "dsr_requests_denied" in ids
        assert "dsr_median_response_days" in ids

    def test_has_incident_metrics(self, lgpd_framework):
        ids = {m.metric_id for m in lgpd_framework.metric_requirements()}
        assert "incidents_reported_to_anpd" in ids
        assert "incidents_affecting_data_subjects" in ids
        assert "incident_median_detection_to_notification_days" in ids

    def test_has_governance_metrics(self, lgpd_framework):
        ids = {m.metric_id for m in lgpd_framework.metric_requirements()}
        assert "dpo_appointed" in ids
        assert "processing_activities_registered" in ids
        assert "international_transfers_count" in ids

    def test_report_sections_ordered(self, lgpd_framework):
        sections = lgpd_framework.report_sections()
        orders = [s.order for s in sections]
        assert orders == sorted(orders)

    def test_section_metrics_reference_valid_ids(self, lgpd_framework):
        valid_ids = {m.metric_id for m in lgpd_framework.metric_requirements()}
        for section in lgpd_framework.report_sections():
            for mid in section.metrics:
                assert mid in valid_ids, (
                    f"Section '{section.section_id}' references unknown metric '{mid}'"
                )

    def test_validate_completeness_required_only(self, lgpd_framework):
        required_ids = lgpd_framework.required_metric_ids()
        assert lgpd_framework.validate_completeness(required_ids) == []

    def test_validate_completeness_missing(self, lgpd_framework):
        missing = lgpd_framework.validate_completeness(set())
        assert "dsr_requests_received" in missing
        assert "incidents_reported_to_anpd" in missing

    def test_template_name(self, lgpd_framework):
        assert lgpd_framework.get_template_name() == "lgpd_report.html"


class TestOSAFramework:
    def test_basic_properties(self, osa_framework):
        assert osa_framework.name == "UK Online Safety Act"
        assert osa_framework.short_code == "osa"
        assert osa_framework.reporting_cadence == ReportingPeriod.ANNUAL

    def test_has_children_safety_metrics(self, osa_framework):
        ids = {m.metric_id for m in osa_framework.metric_requirements()}
        assert "age_assurance_measures" in ids
        assert "children_content_actions" in ids
        assert "csam_reports_ncmec" in ids

    def test_section_metrics_valid(self, osa_framework):
        valid_ids = {m.metric_id for m in osa_framework.metric_requirements()}
        for section in osa_framework.report_sections():
            for mid in section.metrics:
                assert mid in valid_ids


class TestCustomFramework:
    def test_from_file(self, tmp_path):
        definition = {
            "name": "Test Framework",
            "short_code": "test",
            "reporting_cadence": "quarterly",
            "metrics": [
                {
                    "metric_id": "test_metric",
                    "name": "Test Metric",
                    "description": "A test metric.",
                }
            ],
            "sections": [
                {
                    "section_id": "s1",
                    "title": "Section 1",
                    "description": "Test section.",
                    "metrics": ["test_metric"],
                }
            ],
        }
        path = tmp_path / "framework.json"
        path.write_text(json.dumps(definition))

        fw = CustomFramework.from_file(path)
        assert fw.name == "Test Framework"
        assert fw.short_code == "test"
        assert fw.reporting_cadence == ReportingPeriod.QUARTERLY
        assert len(fw.metric_requirements()) == 1
        assert len(fw.report_sections()) == 1

    def test_empty_definition(self):
        fw = CustomFramework()
        assert fw.name == "Custom Framework"
        assert fw.metric_requirements() == []


class TestRegistry:
    def test_get_framework_appi(self):
        fw = get_framework("appi")
        assert isinstance(fw, APPIFramework)

    def test_get_framework_dsa(self):
        fw = get_framework("dsa")
        assert isinstance(fw, DSAFramework)

    def test_get_framework_osa(self):
        fw = get_framework("osa")
        assert isinstance(fw, OSAFramework)

    def test_get_framework_lgpd(self):
        fw = get_framework("lgpd")
        assert isinstance(fw, LGPDFramework)

    def test_get_framework_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown framework"):
            get_framework("nonexistent")

    def test_registry_keys(self):
        assert "appi" in REGISTRY
        assert "dsa" in REGISTRY
        assert "lgpd" in REGISTRY
        assert "osa" in REGISTRY
