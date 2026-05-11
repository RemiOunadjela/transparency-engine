"""Main report generator.

Orchestrates the full pipeline from validated data to rendered output,
coordinating templates, visualisations, and format-specific rendering.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

import transparency_engine as _te
from transparency_engine.config import OutputFormat, PeriodSpec
from transparency_engine.frameworks.base import BaseFramework
from transparency_engine.ingestion.transforms import compute_period_comparison

TEMPLATE_DIR = Path(__file__).parent / "templates"


class ReportGenerator:
    """Generates transparency reports for a given framework and period."""

    def __init__(
        self,
        framework: BaseFramework,
        period: PeriodSpec,
        data: pd.DataFrame,
        platform_name: str = "Platform",
        previous_period_data: pd.DataFrame | None = None,
    ) -> None:
        self.framework = framework
        self.period = period
        self.data = data
        self.platform_name = platform_name
        self.previous_data = previous_period_data
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(["html"]),
        )

    def _build_context(self) -> dict[str, Any]:
        """Build the template context from the data."""
        sections = []
        for section in sorted(self.framework.report_sections(), key=lambda s: s.order):
            section_data = self.data[self.data["metric_id"].isin(section.metrics)]
            metrics_summary = []
            for mid in section.metrics:
                metric_rows = section_data[section_data["metric_id"] == mid]
                if metric_rows.empty:
                    continue
                total = metric_rows["value"].sum()
                metrics_summary.append(
                    {
                        "metric_id": mid,
                        "name": mid.replace("_", " ").title(),
                        "value": total,
                        "formatted_value": self._format_value(total),
                        "rows": metric_rows.to_dict("records"),
                    }
                )
            sections.append(
                {
                    "section_id": section.section_id,
                    "title": section.title,
                    "description": section.description,
                    "metrics": metrics_summary,
                }
            )

        context: dict[str, Any] = {
            "framework_name": self.framework.name,
            "framework_code": self.framework.short_code,
            "platform_name": self.platform_name,
            "period": str(self.period),
            "sections": sections,
            "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M UTC"),
            "engine_version": _te.__version__,
        }

        if self.previous_data is not None:
            comparison = self._build_comparison()
            context["comparison"] = comparison

        return context

    def _build_comparison(self) -> list[dict[str, Any]] | None:
        if self.previous_data is None:
            return None
        all_data = pd.concat([self.data, self.previous_data], ignore_index=True)
        current_str = str(self.period)
        prev_periods = self.previous_data["period"].unique()
        if len(prev_periods) == 0:
            return None
        prev_str = prev_periods[0]
        comparison_df = compute_period_comparison(all_data, current_str, prev_str)
        return comparison_df.to_dict("records")

    @staticmethod
    def _format_value(value: float) -> str:
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        elif value == int(value):
            return f"{int(value):,}"
        else:
            return f"{value:.2f}"

    def generate(self, output_format: OutputFormat, output_path: Path | str | None = None) -> str:
        """Render the report and return the content as a string.

        If ``output_path`` is given, also write the result to disk.
        """
        context = self._build_context()

        if output_format == OutputFormat.JSON:
            content = json.dumps(context, indent=2, default=str)
        elif output_format == OutputFormat.MARKDOWN:
            content = self._render_markdown(context)
        elif output_format == OutputFormat.CSV:
            content = self._render_csv(context)
        elif output_format in (OutputFormat.HTML, OutputFormat.PDF):
            content = self._render_html(context)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        if output_format == OutputFormat.PDF:
            if output_path is None:
                raise ValueError("output_path is required for PDF output.")
            self._write_pdf(content, Path(output_path))
            return f"PDF written to {output_path}"

        if output_path is not None:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(content, encoding="utf-8")

        return content

    def _render_csv(self, context: dict[str, Any]) -> str:
        """Render report metrics as a flat CSV.

        Writes a metrics table (one row per metric) followed by a comparison table
        when period-comparison data is present. Both tables share the file so a
        single export is useful for BI tools and spreadsheets alike.
        """
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")

        # Metrics table
        writer.writerow(["table", "period", "section", "metric_id", "metric_name", "value", "formatted_value"])
        period = context["period"]
        for section in context["sections"]:
            for metric in section["metrics"]:
                writer.writerow(
                    [
                        "metrics",
                        period,
                        section["title"],
                        metric["metric_id"],
                        metric["name"],
                        metric["value"],
                        metric["formatted_value"],
                    ]
                )

        # Comparison table (appended when --yoy or --compare-period was used)
        if context.get("comparison"):
            writer.writerow([])
            writer.writerow(["table", "metric_id", "current_value", "previous_value", "absolute_change", "percent_change"])
            for row in context["comparison"]:
                pct = row.get("percent_change")
                writer.writerow(
                    [
                        "comparison",
                        row["metric_id"],
                        row["current_value"],
                        row["previous_value"],
                        row["absolute_change"],
                        f"{pct:.2f}" if pct is not None else "",
                    ]
                )

        return buf.getvalue()

    def _render_html(self, context: dict[str, Any]) -> str:
        template_name = self.framework.get_template_name()
        try:
            template = self._env.get_template(template_name)
        except Exception:
            template = self._env.get_template("dsa_report.html")
        return template.render(**context)

    def _render_markdown(self, context: dict[str, Any]) -> str:
        lines = [
            f"# {context['framework_name']} Transparency Report",
            f"**Platform:** {context['platform_name']}",
            f"**Period:** {context['period']}",
            f"**Generated:** {context['generated_at']}",
            "",
            "---",
            "",
        ]
        for section in context["sections"]:
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(section["description"])
            lines.append("")
            if section["metrics"]:
                lines.append("| Metric | Value |")
                lines.append("|--------|------:|")
                for m in section["metrics"]:
                    lines.append(f"| {m['name']} | {m['formatted_value']} |")
                lines.append("")

        if context.get("comparison"):
            lines.append("## Period Comparison")
            lines.append("")
            lines.append("| Metric | Current | Previous | Change | % Change |")
            lines.append("|--------|--------:|---------:|-------:|---------:|")
            for c in context["comparison"]:
                pct_val = c.get("percent_change")
                pct = f"{pct_val:.1f}%" if pct_val is not None else "N/A"
                lines.append(
                    f"| {c['metric_id']} | {c['current_value']:,.0f} | "
                    f"{c['previous_value']:,.0f} | {c['absolute_change']:,.0f} | {pct} |"
                )
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(
            f"*Generated by transparency-engine v{context['engine_version']} "
            f"on {context['generated_at']}*"
        )

        return "\n".join(lines)

    def _write_pdf(self, html_content: str, path: Path) -> None:
        try:
            from weasyprint import HTML
        except ImportError:
            raise ImportError(
                "WeasyPrint is required for PDF generation. "
                "Install with: pip install transparency-engine[pdf]"
            ) from None

        path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html_content).write_pdf(str(path))
