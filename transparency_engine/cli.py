"""Command-line interface for transparency-engine.

Provides the full workflow from project scaffolding to report generation:

    transparency-engine init --framework dsa
    transparency-engine ingest --data metrics.csv --period 2024-H1
    transparency-engine validate --framework dsa --period 2024-H1
    transparency-engine generate --framework dsa --period 2024-H1 --format html
    transparency-engine compare --periods 2024-H1,2023-H2 --metrics all
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from transparency_engine import __version__
from transparency_engine.config import OutputFormat, PeriodSpec, ProjectConfig


@click.group()
@click.version_option(version=__version__, prog_name="transparency-engine")
def cli() -> None:
    """Open-source transparency reporting for digital platforms."""


@cli.command()
@click.option(
    "--framework",
    type=click.Choice(["dsa", "osa"], case_sensitive=False),
    default="dsa",
    help="Regulatory framework to scaffold.",
)
@click.option("--platform-name", default="My Platform", help="Name of the platform.")
@click.option("--output-dir", default=".", help="Directory to create the project in.")
def init(framework: str, platform_name: str, output_dir: str) -> None:
    """Scaffold a new transparency reporting project."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "data").mkdir(exist_ok=True)
    (out / "reports").mkdir(exist_ok=True)

    config = ProjectConfig(
        framework=framework,
        platform_name=platform_name,
        data_dir="data",
        output_dir="reports",
    )
    config.save(out / "transparency-engine.json")

    click.echo(f"Initialized {framework.upper()} project for '{platform_name}' in {out.resolve()}")
    click.echo("  Created: data/")
    click.echo("  Created: reports/")
    click.echo("  Created: transparency-engine.json")
    click.echo("")
    click.echo("Next steps:")
    click.echo("  1. Place your metrics data in data/")
    click.echo("  2. Run: transparency-engine ingest --data data/metrics.csv --period 2024-H1")


@cli.command()
@click.option(
    "--data",
    "data_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to metrics data file.",
)
@click.option("--period", required=True, help="Reporting period (e.g. 2024-H1).")
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(),
    help="Path to project config.",
)
def ingest(data_path: str, period: str, config_path: str | None) -> None:
    """Load and validate metrics data."""
    from transparency_engine.frameworks import get_framework
    from transparency_engine.ingestion import load_data, validate_schema

    period_spec = PeriodSpec.parse(period)
    config = ProjectConfig.load(Path(config_path) if config_path else None)
    framework = get_framework(config.framework)

    click.echo(f"Loading data from {data_path}...")
    df = load_data(data_path)
    click.echo(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

    errors = validate_schema(df, framework)
    error_count = sum(1 for e in errors if e.severity == "error")
    warn_count = sum(1 for e in errors if e.severity == "warning")

    for err in errors:
        icon = "ERROR" if err.severity == "error" else "WARN"
        click.echo(f"  [{icon}] {err.column}: {err.error}")

    if error_count > 0:
        click.echo(f"\nIngestion failed: {error_count} error(s), {warn_count} warning(s)")
        sys.exit(1)
    else:
        click.echo(f"\nIngestion complete: {len(df)} rows for period {period_spec}")
        if warn_count:
            click.echo(f"  ({warn_count} warning(s) -- review before publishing)")


@cli.command()
@click.option("--framework", default=None, help="Framework (overrides config).")
@click.option("--period", required=True, help="Reporting period to validate.")
@click.option(
    "--data",
    "data_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to metrics data.",
)
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(),
    help="Path to project config.",
)
def validate(framework: str | None, period: str, data_path: str, config_path: str | None) -> None:
    """Run pre-publication validation checks."""
    from transparency_engine.frameworks import get_framework
    from transparency_engine.ingestion import load_data
    from transparency_engine.validation import run_validation

    config = ProjectConfig.load(Path(config_path) if config_path else None)
    fw_name = framework or config.framework
    fw = get_framework(fw_name)

    df = load_data(data_path)
    results = run_validation(df, fw)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    click.echo(f"Validation results for {fw.name} -- period {period}:")
    click.echo(f"  {passed} passed, {failed} failed\n")

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        click.echo(f"  [{status}] {r.check_name}: {r.message}")

    if failed > 0:
        sys.exit(1)


@cli.command()
@click.option("--framework", default=None, help="Framework (overrides config).")
@click.option("--period", required=True, help="Reporting period.")
@click.option(
    "--data",
    "data_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to metrics data.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "html", "pdf", "json", "csv"], case_sensitive=False),
    default="html",
    help="Output format.",
)
@click.option("--output", "output_path", default=None, help="Output file path.")
@click.option("--platform-name", default=None, help="Report header name.")
@click.option(
    "--compare-period",
    default=None,
    help="Period to compare against (e.g. 2023-H1). Adds a comparison table to the report.",
)
@click.option(
    "--yoy",
    is_flag=True,
    default=False,
    help="Include year-over-year comparison using the same label from the prior year.",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress informational output. Warnings are still printed.",
)
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(),
    help="Path to project config.",
)
def generate(
    framework: str | None,
    period: str,
    data_path: str,
    output_format: str,
    output_path: str | None,
    platform_name: str | None,
    compare_period: str | None,
    yoy: bool,
    quiet: bool,
    config_path: str | None,
) -> None:
    """Generate a transparency report.

    Use --yoy to automatically include a year-over-year comparison (same label,
    prior year). Use --compare-period to specify an explicit baseline period.
    """
    from transparency_engine.frameworks import get_framework
    from transparency_engine.ingestion import load_data
    from transparency_engine.reports import ReportGenerator

    config = ProjectConfig.load(Path(config_path) if config_path else None)
    fw = get_framework(framework or config.framework)
    period_spec = PeriodSpec.parse(period)
    fmt = OutputFormat(output_format.lower())

    if yoy and compare_period:
        click.echo("Error: --yoy and --compare-period are mutually exclusive.")
        sys.exit(1)

    df = load_data(data_path)
    pname = platform_name or config.platform_name

    # Resolve the comparison period
    prev_period_spec: PeriodSpec | None = None
    if yoy:
        prev_period_spec = period_spec.yoy_period()
        if not quiet:
            click.echo(f"Year-over-year comparison: {period_spec} vs {prev_period_spec}")
    elif compare_period:
        prev_period_spec = PeriodSpec.parse(compare_period)
        if not quiet:
            click.echo(f"Period comparison: {period_spec} vs {prev_period_spec}")

    # Filter current and previous period data separately so the report
    # sections only aggregate the requested period's rows.
    if "period" in df.columns:
        current_df = df[df["period"] == str(period_spec)].copy()
    else:
        current_df = df

    prev_df = None
    if prev_period_spec is not None:
        if "period" in df.columns:
            prev_df = df[df["period"] == str(prev_period_spec)].copy()
            if prev_df.empty:
                click.echo(
                    f"Warning: no data found for comparison period {prev_period_spec}. "
                    "Comparison table will be omitted."
                )
                prev_df = None
        else:
            click.echo(
                "Warning: data has no 'period' column; cannot filter comparison period. "
                "Comparison table will be omitted."
            )

    if output_path is None:
        ext = {"markdown": "md", "html": "html", "pdf": "pdf", "json": "json", "csv": "csv"}[
            fmt.value
        ]
        output_path = f"reports/{fw.short_code}_report_{period_spec}.{ext}"

    generator = ReportGenerator(
        framework=fw,
        period=period_spec,
        data=current_df,
        platform_name=pname,
        previous_period_data=prev_df,
    )

    if not quiet:
        click.echo(f"Generating {fmt.value.upper()} report for {fw.name} -- {period_spec}...")
    result = generator.generate(fmt, output_path=output_path)

    if fmt == OutputFormat.PDF:
        click.echo(result)
    elif not quiet:
        click.echo(f"Report written to {output_path}")


@cli.command()
@click.option(
    "--periods",
    required=True,
    help="Comma-separated periods to compare (e.g. 2024-H1,2023-H2).",
)
@click.option(
    "--data",
    "data_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to metrics data.",
)
@click.option("--metrics", default="all", help="Comma-separated metric IDs, or 'all'.")
@click.option("--output", "output_path", default=None, help="Output file path.")
def compare(periods: str, data_path: str, metrics: str, output_path: str | None) -> None:
    """Compare metrics across reporting periods."""
    from transparency_engine.ingestion import load_data
    from transparency_engine.ingestion.transforms import compute_period_comparison

    period_list = [p.strip() for p in periods.split(",")]
    if len(period_list) != 2:
        click.echo("Exactly two periods required (e.g. --periods 2024-H1,2023-H2)")
        sys.exit(1)

    df = load_data(data_path)

    if metrics != "all":
        metric_ids = [m.strip() for m in metrics.split(",")]
        df = df[df["metric_id"].isin(metric_ids)]

    comparison = compute_period_comparison(df, period_list[0], period_list[1])

    click.echo(f"\nComparison: {period_list[0]} vs {period_list[1]}")
    click.echo("-" * 80)
    click.echo(f"{'Metric':<40} {'Current':>10} {'Previous':>10} {'Change':>10} {'%':>8}")
    click.echo("-" * 80)

    for _, row in comparison.iterrows():
        pct = f"{row['percent_change']:.1f}%" if row["percent_change"] is not None else "N/A"
        click.echo(
            f"{row['metric_id']:<40} "
            f"{row['current_value']:>10,.0f} "
            f"{row['previous_value']:>10,.0f} "
            f"{row['absolute_change']:>+10,.0f} "
            f"{pct:>8}"
        )

    if output_path:
        comparison.to_csv(output_path, index=False)
        click.echo(f"\nComparison data saved to {output_path}")


if __name__ == "__main__":
    cli()
