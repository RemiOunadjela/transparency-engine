"""Tests for report generation."""

import pandas as pd
import pytest

from transparency_engine.config import OutputFormat, PeriodSpec
from transparency_engine.reports.generator import ReportGenerator


@pytest.fixture
def report_data():
    return pd.DataFrame(
        [
            {"metric_id": "notices_received", "period": "2024-H1", "value": 284750},
            {"metric_id": "notices_actioned", "period": "2024-H1", "value": 213562},
            {"metric_id": "notices_median_response_time", "period": "2024-H1", "value": 4.2},
            {"metric_id": "complaints_received", "period": "2024-H1", "value": 47830},
            {"metric_id": "complaints_reversed", "period": "2024-H1", "value": 6214},
            {"metric_id": "content_moderation_orders_received", "period": "2024-H1", "value": 342},
        ]
    )


@pytest.fixture
def generator(dsa_framework, report_data):
    period = PeriodSpec.parse("2024-H1")
    return ReportGenerator(
        framework=dsa_framework,
        period=period,
        data=report_data,
        platform_name="TestPlatform",
    )


class TestReportGenerator:
    def test_generate_html(self, generator, tmp_path):
        path = tmp_path / "report.html"
        content = generator.generate(OutputFormat.HTML, output_path=path)
        assert "<html" in content
        assert "TestPlatform" in content
        assert "2024-H1" in content
        assert path.exists()

    def test_generate_markdown(self, generator):
        content = generator.generate(OutputFormat.MARKDOWN)
        assert "# EU Digital Services Act Transparency Report" in content
        assert "TestPlatform" in content
        assert "284.8K" in content or "284,750" in content

    def test_generate_json(self, generator):
        import json

        content = generator.generate(OutputFormat.JSON)
        data = json.loads(content)
        assert data["framework_name"] == "EU Digital Services Act"
        assert data["platform_name"] == "TestPlatform"
        assert len(data["sections"]) > 0

    def test_generate_with_comparison(self, dsa_framework, report_data):
        prev_data = pd.DataFrame(
            [
                {"metric_id": "notices_received", "period": "2023-H2", "value": 251400},
                {"metric_id": "notices_actioned", "period": "2023-H2", "value": 188550},
            ]
        )
        period = PeriodSpec.parse("2024-H1")
        gen = ReportGenerator(
            framework=dsa_framework,
            period=period,
            data=report_data,
            platform_name="TestPlatform",
            previous_period_data=prev_data,
        )
        content = gen.generate(OutputFormat.MARKDOWN)
        assert "Period Comparison" in content

    def test_format_value_large(self, generator):
        assert ReportGenerator._format_value(1_500_000) == "1.5M"
        assert ReportGenerator._format_value(42_000) == "42.0K"
        assert ReportGenerator._format_value(500) == "500"
        assert ReportGenerator._format_value(3.14) == "3.14"

    def test_output_to_file(self, generator, tmp_path):
        path = tmp_path / "subdir" / "report.md"
        generator.generate(OutputFormat.MARKDOWN, output_path=path)
        assert path.exists()
        content = path.read_text()
        assert "TestPlatform" in content

    def test_pdf_requires_output_path(self, generator):
        with pytest.raises(ValueError, match="output_path is required"):
            generator.generate(OutputFormat.PDF)
