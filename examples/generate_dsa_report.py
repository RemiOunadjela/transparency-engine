"""Generate a DSA transparency report from sample data.

Usage:
    python examples/generate_dsa_report.py
"""

from pathlib import Path

from transparency_engine.config import OutputFormat, PeriodSpec
from transparency_engine.frameworks import get_framework
from transparency_engine.ingestion import load_data
from transparency_engine.reports import ReportGenerator
from transparency_engine.validation import run_validation

DATA_PATH = Path(__file__).parent / "sample_data" / "sample_metrics.csv"
OUTPUT_DIR = Path(__file__).parent / "output"


def main() -> None:
    framework = get_framework("dsa")
    period = PeriodSpec.parse("2024-H1")
    prev_period = PeriodSpec.parse("2023-H2")

    df = load_data(DATA_PATH)
    print(f"Loaded {len(df)} rows from {DATA_PATH.name}")

    current_data = df[df["period"] == str(period)]
    previous_data = df[df["period"] == str(prev_period)]

    # Validate
    results = run_validation(current_data, framework, previous_df=previous_data)
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.check_name}: {r.message}")

    # Generate HTML report
    generator = ReportGenerator(
        framework=framework,
        period=period,
        data=current_data,
        platform_name="Acme Social",
        previous_period_data=previous_data,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    html_path = OUTPUT_DIR / "dsa_report_2024_h1.html"
    generator.generate(OutputFormat.HTML, output_path=html_path)
    print(f"\nHTML report: {html_path}")

    md_path = OUTPUT_DIR / "dsa_report_2024_h1.md"
    generator.generate(OutputFormat.MARKDOWN, output_path=md_path)
    print(f"Markdown report: {md_path}")


if __name__ == "__main__":
    main()
