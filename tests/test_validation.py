"""Tests for validation checks and audit trail."""

import json

import pandas as pd

from transparency_engine.validation.audit import AuditTrail
from transparency_engine.validation.checks import (
    Severity,
    check_appeal_consistency,
    check_historical_restatement,
    check_negative_values,
    check_percentage_bounds,
    check_period_consistency,
    check_required_metrics,
    run_validation,
)


class TestValidationChecks:
    def test_required_metrics_pass(self, sample_dsa_data, dsa_framework):
        result = check_required_metrics(sample_dsa_data, dsa_framework)
        assert result.passed

    def test_required_metrics_fail(self, dsa_framework):
        df = pd.DataFrame(
            {"metric_id": ["notices_received"], "period": ["2024-H1"], "value": [100]}
        )
        result = check_required_metrics(df, dsa_framework)
        assert not result.passed
        assert len(result.details["missing"]) > 0

    def test_negative_values_pass(self):
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [100]})
        result = check_negative_values(df)
        assert result.passed

    def test_negative_values_fail(self):
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [-5]})
        result = check_negative_values(df)
        assert not result.passed

    def test_appeal_consistency_pass(self):
        df = pd.DataFrame(
            {
                "metric_id": ["notices_received", "notices_actioned"],
                "period": ["2024-H1", "2024-H1"],
                "value": [1000, 800],
            }
        )
        result = check_appeal_consistency(df)
        assert result.passed

    def test_appeal_consistency_fail(self):
        df = pd.DataFrame(
            {
                "metric_id": ["notices_received", "notices_actioned"],
                "period": ["2024-H1", "2024-H1"],
                "value": [100, 200],  # actioned > received
            }
        )
        result = check_appeal_consistency(df)
        assert not result.passed

    def test_percentage_bounds_pass(self):
        df = pd.DataFrame({"metric_id": ["detection_rate"], "period": ["2024-H1"], "value": [85.0]})
        result = check_percentage_bounds(df)
        assert result.passed

    def test_percentage_bounds_fail(self):
        df = pd.DataFrame(
            {"metric_id": ["detection_rate"], "period": ["2024-H1"], "value": [150.0]}
        )
        result = check_percentage_bounds(df)
        assert not result.passed

    def test_period_consistency_single(self):
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [100]})
        result = check_period_consistency(df)
        assert result.passed

    def test_period_consistency_multiple(self):
        df = pd.DataFrame(
            {
                "metric_id": ["m1", "m1"],
                "period": ["2024-H1", "2024-H2"],
                "value": [100, 200],
            }
        )
        result = check_period_consistency(df)
        assert not result.passed

    def test_historical_restatement_stable(self):
        current = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [110]})
        previous = pd.DataFrame({"metric_id": ["m1"], "period": ["2023-H2"], "value": [100]})
        result = check_historical_restatement(current, previous)
        assert result.passed

    def test_historical_restatement_flagged(self):
        current = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [300]})
        previous = pd.DataFrame({"metric_id": ["m1"], "period": ["2023-H2"], "value": [100]})
        result = check_historical_restatement(current, previous)
        assert not result.passed
        assert result.severity == Severity.WARNING

    def test_run_validation_suite(self, sample_dsa_data, dsa_framework):
        results = run_validation(sample_dsa_data, dsa_framework)
        assert len(results) >= 4
        assert all(hasattr(r, "passed") for r in results)


class TestAuditTrail:
    def test_log_and_retrieve(self):
        trail = AuditTrail()
        trail.log(
            "load",
            "Loaded CSV file",
            input_shape=(0, 0),
            output_shape=(100, 5),
            source="metrics.csv",
        )
        assert len(trail.entries) == 1
        assert trail.entries[0].operation == "load"

    def test_summary_output(self):
        trail = AuditTrail()
        trail.log("load", "Loaded data", input_shape=(0, 0), output_shape=(50, 3))
        trail.log("filter", "Filtered to period", input_shape=(50, 3), output_shape=(25, 3))
        summary = trail.summary()
        assert "2 operations" in summary
        assert "load" in summary
        assert "filter" in summary

    def test_save_and_load(self, tmp_path):
        trail = AuditTrail()
        trail.log("test_op", "Test operation")
        path = tmp_path / "audit.json"
        trail.save(path)
        assert path.exists()

        loaded = AuditTrail.load(path)
        assert len(loaded.entries) == 1
        assert loaded.entries[0].operation == "test_op"

    def test_to_json(self):
        trail = AuditTrail()
        trail.log("op1", "First operation")
        raw = json.loads(trail.to_json())
        assert len(raw) == 1
        assert raw[0]["operation"] == "op1"
