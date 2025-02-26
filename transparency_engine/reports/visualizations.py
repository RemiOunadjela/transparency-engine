"""Chart and graph generation for transparency reports.

Uses matplotlib with a clean, publication-ready style. All functions
return the figure path or a base64-encoded image string for embedding.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

STYLE_DEFAULTS = {
    "figure.figsize": (10, 5),
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
}

PALETTE = ["#1a73e8", "#ea4335", "#34a853", "#fbbc05", "#5f6368", "#9334e6"]


def _apply_style() -> None:
    for key, val in STYLE_DEFAULTS.items():
        plt.rcParams[key] = val


def _figure_to_base64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def render_trend_chart(
    df: pd.DataFrame,
    metric_id: str,
    title: str | None = None,
    output_path: Path | str | None = None,
) -> str:
    """Line chart showing a metric's value over reporting periods.

    Returns base64-encoded PNG or writes to ``output_path``.
    """
    _apply_style()
    metric_data = df[df["metric_id"] == metric_id].copy()
    if metric_data.empty:
        raise ValueError(f"No data found for metric '{metric_id}'")

    metric_data = metric_data.sort_values("period")

    fig, ax = plt.subplots()
    ax.plot(
        metric_data["period"],
        metric_data["value"],
        marker="o",
        linewidth=2,
        color=PALETTE[0],
    )
    ax.set_title(title or metric_id.replace("_", " ").title())
    ax.set_xlabel("Period")
    ax.set_ylabel("Value")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    fig.autofmt_xdate(rotation=30)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(output_path)

    return _figure_to_base64(fig)


def render_comparison_chart(
    df: pd.DataFrame,
    metric_ids: list[str],
    current_period: str,
    previous_period: str,
    title: str = "Period Comparison",
    output_path: Path | str | None = None,
) -> str:
    """Grouped bar chart comparing two periods across metrics.

    Returns base64-encoded PNG or writes to ``output_path``.
    """
    _apply_style()

    current_vals = []
    previous_vals = []
    labels = []

    for mid in metric_ids:
        cur = df[(df["metric_id"] == mid) & (df["period"] == current_period)]["value"].sum()
        prev = df[(df["metric_id"] == mid) & (df["period"] == previous_period)]["value"].sum()
        current_vals.append(cur)
        previous_vals.append(prev)
        labels.append(mid.replace("_", " ").title())

    import numpy as np

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 2), 5))
    ax.bar(x - width / 2, previous_vals, width, label=previous_period, color=PALETTE[4])
    ax.bar(x + width / 2, current_vals, width, label=current_period, color=PALETTE[0])

    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(output_path)

    return _figure_to_base64(fig)
