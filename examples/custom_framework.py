"""Define and use a custom regulatory framework.

Shows how to create a framework definition from scratch,
for instance to comply with internal reporting standards
or emerging regulations like Canada's Bill C-63.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd

from transparency_engine.config import OutputFormat, PeriodSpec
from transparency_engine.frameworks.custom import CustomFramework
from transparency_engine.reports import ReportGenerator

CUSTOM_DEFINITION = {
    "name": "Internal Trust & Safety Quarterly Review",
    "short_code": "internal",
    "reporting_cadence": "quarterly",
    "metrics": [
        {
            "metric_id": "user_reports_total",
            "name": "Total user reports",
            "description": "All reports submitted via in-app flows.",
            "required": True,
        },
        {
            "metric_id": "automated_actions",
            "name": "Automated enforcement actions",
            "description": "Content actions taken without human review.",
            "required": True,
        },
        {
            "metric_id": "appeal_rate",
            "name": "Appeal rate",
            "description": "Percentage of enforcement actions that were appealed.",
            "required": True,
            "data_type": "percentage",
        },
        {
            "metric_id": "false_positive_rate",
            "name": "False positive rate (estimated)",
            "description": "Estimated share of automated actions that were incorrect.",
            "required": False,
            "data_type": "percentage",
        },
    ],
    "sections": [
        {
            "section_id": "overview",
            "title": "Enforcement Overview",
            "description": "High-level enforcement activity for the quarter.",
            "metrics": ["user_reports_total", "automated_actions"],
            "order": 1,
        },
        {
            "section_id": "quality",
            "title": "Enforcement Quality",
            "description": "Accuracy and appeal metrics.",
            "metrics": ["appeal_rate", "false_positive_rate"],
            "order": 2,
        },
    ],
}


def main() -> None:
    # Write the framework definition to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(CUSTOM_DEFINITION, f)
        def_path = f.name

    framework = CustomFramework.from_file(def_path)
    print(f"Loaded custom framework: {framework.name}")
    print(f"  Metrics: {len(framework.metric_requirements())}")
    print(f"  Sections: {len(framework.report_sections())}")

    # Build sample data
    data = pd.DataFrame(
        [
            {"metric_id": "user_reports_total", "period": "2024-Q3", "value": 42500},
            {"metric_id": "automated_actions", "period": "2024-Q3", "value": 187300},
            {"metric_id": "appeal_rate", "period": "2024-Q3", "value": 3.2},
            {"metric_id": "false_positive_rate", "period": "2024-Q3", "value": 1.8},
        ]
    )

    period = PeriodSpec.parse("2024-Q3")
    generator = ReportGenerator(
        framework=framework,
        period=period,
        data=data,
        platform_name="Internal Review",
    )

    report_md = generator.generate(OutputFormat.MARKDOWN)
    print("\n" + report_md)


if __name__ == "__main__":
    main()
