"""Data transformation and period alignment.

Handles aggregation across breakdown dimensions and alignment of raw
event-level data into reporting periods (quarterly, semi-annual, annual).
"""

from __future__ import annotations

import pandas as pd

from transparency_engine.config import PeriodSpec


def _parse_date_column(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    """Ensure a date column is parsed as datetime."""
    if col in df.columns:
        df = df.copy()
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def align_period(df: pd.DataFrame, period: PeriodSpec, date_col: str = "date") -> pd.DataFrame:
    """Filter a DataFrame to rows falling within the given reporting period.

    Expects a date/datetime column. For datasets already labelled with a
    ``period`` column matching the PeriodSpec string, returns rows that match.
    """
    period_str = str(period)

    # If data already has a 'period' column, filter directly
    if "period" in df.columns:
        return df[df["period"] == period_str].copy()

    # Otherwise, filter by date range
    if date_col not in df.columns:
        raise ValueError(f"Cannot align period: DataFrame has no '{date_col}' or 'period' column.")

    df = _parse_date_column(df, date_col)
    start, end = _period_date_range(period)
    mask = (df[date_col] >= start) & (df[date_col] <= end)
    result = df.loc[mask].copy()
    result["period"] = period_str
    return result


def _period_date_range(period: PeriodSpec) -> tuple[str, str]:
    """Return (start_date, end_date) strings for a PeriodSpec."""
    y = period.year
    ranges = {
        "H1": (f"{y}-01-01", f"{y}-06-30"),
        "H2": (f"{y}-07-01", f"{y}-12-31"),
        "Q1": (f"{y}-01-01", f"{y}-03-31"),
        "Q2": (f"{y}-04-01", f"{y}-06-30"),
        "Q3": (f"{y}-07-01", f"{y}-09-30"),
        "Q4": (f"{y}-10-01", f"{y}-12-31"),
        "FY": (f"{y}-01-01", f"{y}-12-31"),
    }
    return ranges[period.label]


def aggregate_metrics(
    df: pd.DataFrame,
    group_by: list[str] | None = None,
    agg_column: str = "value",
    agg_func: str = "sum",
) -> pd.DataFrame:
    """Aggregate metric values, optionally grouping by breakdown dimensions.

    Parameters
    ----------
    df : DataFrame with at least ``metric_id``, ``period``, and ``value`` columns.
    group_by : Additional columns to group by (e.g., ["content_type", "country"]).
    agg_column : Column to aggregate.
    agg_func : Aggregation function -- "sum", "mean", "count", "max", "min", "latest".
    """
    base_groups = ["metric_id", "period"]
    if group_by:
        base_groups = base_groups + [c for c in group_by if c in df.columns]

    if agg_func == "latest":
        # Take the last value per group (assumes chronological order)
        return df.groupby(base_groups, as_index=False).last()

    valid_funcs = {"sum", "mean", "count", "max", "min"}
    if agg_func not in valid_funcs:
        raise ValueError(f"Unsupported aggregation '{agg_func}'. Choose from {valid_funcs}")

    return df.groupby(base_groups, as_index=False).agg({agg_column: agg_func})


def compute_period_comparison(
    df: pd.DataFrame,
    current_period: str,
    previous_period: str,
    value_col: str = "value",
) -> pd.DataFrame:
    """Compute period-over-period change for each metric.

    Returns a DataFrame with columns: metric_id, current_value,
    previous_value, absolute_change, percent_change.
    """
    current = df[df["period"] == current_period].set_index("metric_id")[value_col]
    previous = df[df["period"] == previous_period].set_index("metric_id")[value_col]

    combined = pd.DataFrame(
        {
            "current_value": current,
            "previous_value": previous,
        }
    ).fillna(0)

    combined["absolute_change"] = combined["current_value"] - combined["previous_value"]
    combined["percent_change"] = combined.apply(
        lambda row: (
            (row["absolute_change"] / row["previous_value"] * 100)
            if row["previous_value"] != 0
            else None
        ),
        axis=1,
    )
    return combined.reset_index()
