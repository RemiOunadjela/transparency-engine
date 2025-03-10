"""Tests for data ingestion, schema validation, and transforms."""

import pandas as pd
import pytest

from transparency_engine.config import PeriodSpec
from transparency_engine.ingestion.loaders import load_data
from transparency_engine.ingestion.schema import validate_schema
from transparency_engine.ingestion.transforms import (
    aggregate_metrics,
    align_period,
    compute_period_comparison,
)


class TestDataLoader:
    def test_load_csv(self, tmp_path):
        csv_path = tmp_path / "test.csv"
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [100]})
        df.to_csv(csv_path, index=False)

        loaded = load_data(csv_path)
        assert len(loaded) == 1
        assert loaded.iloc[0]["metric_id"] == "m1"

    def test_load_json(self, tmp_path):
        json_path = tmp_path / "test.json"
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [42]})
        df.to_json(json_path, orient="records")

        loaded = load_data(json_path)
        assert len(loaded) == 1

    def test_load_parquet(self, tmp_path):
        pq_path = tmp_path / "test.parquet"
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [99]})
        df.to_parquet(pq_path, index=False)

        loaded = load_data(pq_path)
        assert len(loaded) == 1
        assert loaded.iloc[0]["value"] == 99

    def test_unsupported_format(self, tmp_path):
        bad_path = tmp_path / "test.xlsx"
        bad_path.touch()
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_data(bad_path)


class TestSchemaValidation:
    def test_valid_data_passes(self, sample_dsa_data, dsa_framework):
        errors = validate_schema(sample_dsa_data, dsa_framework)
        error_level = [e for e in errors if e.severity == "error"]
        assert len(error_level) == 0

    def test_missing_column(self, dsa_framework):
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"]})
        errors = validate_schema(df, dsa_framework)
        assert any(e.column == "value" for e in errors)

    def test_null_values_flagged(self, dsa_framework):
        df = pd.DataFrame(
            {"metric_id": ["m1", None], "period": ["2024-H1", "2024-H1"], "value": [100, 200]}
        )
        errors = validate_schema(df, dsa_framework)
        assert any("null" in e.error for e in errors)

    def test_missing_required_metrics_warned(self, dsa_framework):
        df = pd.DataFrame(
            {"metric_id": ["notices_received"], "period": ["2024-H1"], "value": [100]}
        )
        errors = validate_schema(df, dsa_framework)
        warnings = [e for e in errors if e.severity == "warning"]
        assert len(warnings) > 0


class TestTransforms:
    def test_aggregate_sum(self):
        df = pd.DataFrame(
            {
                "metric_id": ["m1", "m1", "m2"],
                "period": ["2024-H1", "2024-H1", "2024-H1"],
                "value": [10, 20, 50],
            }
        )
        result = aggregate_metrics(df)
        m1_val = result[result["metric_id"] == "m1"]["value"].iloc[0]
        assert m1_val == 30

    def test_aggregate_mean(self):
        df = pd.DataFrame(
            {
                "metric_id": ["m1", "m1"],
                "period": ["2024-H1", "2024-H1"],
                "value": [10, 30],
            }
        )
        result = aggregate_metrics(df, agg_func="mean")
        assert result.iloc[0]["value"] == 20.0

    def test_aggregate_with_groupby(self):
        df = pd.DataFrame(
            {
                "metric_id": ["m1", "m1", "m1"],
                "period": ["2024-H1", "2024-H1", "2024-H1"],
                "value": [10, 20, 30],
                "country": ["DE", "DE", "FR"],
            }
        )
        result = aggregate_metrics(df, group_by=["country"])
        assert len(result) == 2

    def test_align_period_by_column(self):
        df = pd.DataFrame(
            {
                "metric_id": ["m1", "m1"],
                "period": ["2024-H1", "2024-H2"],
                "value": [100, 200],
            }
        )
        period = PeriodSpec.parse("2024-H1")
        result = align_period(df, period)
        assert len(result) == 1
        assert result.iloc[0]["value"] == 100

    def test_period_comparison(self, sample_multi_period_data):
        result = compute_period_comparison(sample_multi_period_data, "2024-H1", "2023-H2")
        assert "absolute_change" in result.columns
        assert "percent_change" in result.columns
        assert len(result) == 4
        # All values went from 150 to 200
        for _, row in result.iterrows():
            assert row["absolute_change"] == 50
            assert abs(row["percent_change"] - 33.3) < 0.1

    def test_invalid_agg_func(self):
        df = pd.DataFrame({"metric_id": ["m1"], "period": ["2024-H1"], "value": [10]})
        with pytest.raises(ValueError, match="Unsupported aggregation"):
            aggregate_metrics(df, agg_func="median")
