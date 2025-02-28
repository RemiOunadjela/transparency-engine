"""Pre-publication validation rules.

Runs a battery of consistency and completeness checks on metric data
before it is used to generate a report. Designed to catch the kinds
of errors that typically surface during regulator review.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from transparency_engine.frameworks.base import BaseFramework


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationResult(BaseModel):
    check_name: str
    passed: bool
    severity: Severity = Severity.ERROR
    message: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


def check_required_metrics(df: pd.DataFrame, framework: BaseFramework) -> ValidationResult:
    """Verify all required metrics are present in the dataset."""
    present = set(df["metric_id"].unique())
    missing = framework.validate_completeness(present)
    if missing:
        return ValidationResult(
            check_name="required_metrics",
            passed=False,
            message=f"Missing {len(missing)} required metric(s): {', '.join(missing)}",
            details={"missing": missing},
        )
    return ValidationResult(
        check_name="required_metrics",
        passed=True,
        message="All required metrics present.",
    )


def check_negative_values(df: pd.DataFrame) -> ValidationResult:
    """Flag any negative values, which are almost always data errors in count metrics."""
    negatives = df[df["value"] < 0]
    if not negatives.empty:
        bad_metrics = negatives["metric_id"].unique().tolist()
        return ValidationResult(
            check_name="negative_values",
            passed=False,
            severity=Severity.ERROR,
            message=f"Found {len(negatives)} rows with negative values.",
            details={"affected_metrics": bad_metrics},
        )
    return ValidationResult(
        check_name="negative_values",
        passed=True,
        message="No negative values found.",
    )


def check_appeal_consistency(df: pd.DataFrame) -> ValidationResult:
    """Appeals upheld should not exceed total appeals received."""
    checks = [
        ("appeals_received", "appeals_upheld"),
        ("complaints_received", "complaints_reversed"),
        ("notices_received", "notices_actioned"),
    ]
    issues = []
    for total_id, subset_id in checks:
        total_rows = df[df["metric_id"] == total_id]
        subset_rows = df[df["metric_id"] == subset_id]
        if total_rows.empty or subset_rows.empty:
            continue
        total_val = total_rows["value"].sum()
        subset_val = subset_rows["value"].sum()
        if subset_val > total_val:
            issues.append(f"{subset_id} ({subset_val:,.0f}) exceeds {total_id} ({total_val:,.0f})")

    if issues:
        return ValidationResult(
            check_name="appeal_consistency",
            passed=False,
            severity=Severity.ERROR,
            message="Subset metrics exceed their parent totals.",
            details={"issues": issues},
        )
    return ValidationResult(
        check_name="appeal_consistency",
        passed=True,
        message="Subset/total relationships are consistent.",
    )


def check_percentage_bounds(df: pd.DataFrame) -> ValidationResult:
    """Percentage metrics should be between 0 and 100."""
    pct_keywords = ["rate", "percentage", "accuracy"]
    pct_metrics = df[df["metric_id"].str.contains("|".join(pct_keywords), case=False, na=False)]
    out_of_range = pct_metrics[(pct_metrics["value"] < 0) | (pct_metrics["value"] > 100)]
    if not out_of_range.empty:
        bad = out_of_range["metric_id"].unique().tolist()
        return ValidationResult(
            check_name="percentage_bounds",
            passed=False,
            severity=Severity.WARNING,
            message=f"Percentage metrics outside 0-100 range: {', '.join(bad)}",
            details={"affected_metrics": bad},
        )
    return ValidationResult(
        check_name="percentage_bounds",
        passed=True,
        message="Percentage metrics within valid range.",
    )


def check_period_consistency(df: pd.DataFrame) -> ValidationResult:
    """All rows should have the same period value when validating a single-period dataset."""
    periods = df["period"].unique()
    if len(periods) > 1:
        return ValidationResult(
            check_name="period_consistency",
            passed=False,
            severity=Severity.WARNING,
            message=f"Multiple periods found in dataset: {', '.join(str(p) for p in periods)}",
            details={"periods": list(periods)},
        )
    return ValidationResult(
        check_name="period_consistency",
        passed=True,
        message="Single period detected.",
    )


def check_historical_restatement(
    current_df: pd.DataFrame, previous_df: pd.DataFrame, threshold: float = 0.50
) -> ValidationResult:
    """Detect suspiciously large period-over-period swings that may indicate restatement.

    A metric changing by more than ``threshold`` (default 50%) between consecutive
    periods warrants a restatement note in the report.
    """
    flagged = []

    cur_agg = current_df.groupby("metric_id")["value"].sum()
    prev_agg = previous_df.groupby("metric_id")["value"].sum()

    common = set(cur_agg.index) & set(prev_agg.index)
    for mid in common:
        cur_val = cur_agg[mid]
        prev_val = prev_agg[mid]
        if prev_val == 0:
            continue
        pct_change = abs(cur_val - prev_val) / prev_val
        if pct_change > threshold:
            flagged.append(
                {
                    "metric_id": mid,
                    "current": cur_val,
                    "previous": prev_val,
                    "change_pct": round(pct_change * 100, 1),
                }
            )

    if flagged:
        return ValidationResult(
            check_name="historical_restatement",
            passed=False,
            severity=Severity.WARNING,
            message=(
                f"{len(flagged)} metric(s) changed by more than "
                f"{threshold * 100:.0f}% -- consider adding restatement notes."
            ),
            details={"flagged_metrics": flagged},
        )
    return ValidationResult(
        check_name="historical_restatement",
        passed=True,
        message="No large period-over-period swings detected.",
    )


def run_validation(
    df: pd.DataFrame,
    framework: BaseFramework,
    previous_df: pd.DataFrame | None = None,
) -> list[ValidationResult]:
    """Run the full validation suite and return all results."""
    results = [
        check_required_metrics(df, framework),
        check_negative_values(df),
        check_appeal_consistency(df),
        check_percentage_bounds(df),
        check_period_consistency(df),
    ]

    if previous_df is not None and not previous_df.empty:
        results.append(check_historical_restatement(df, previous_df))

    return results
