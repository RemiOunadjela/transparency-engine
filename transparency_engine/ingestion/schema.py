"""Schema validation for ingested data.

Ensures that raw data conforms to the expected column structure before
it enters the reporting pipeline. Catches mismatches early so they
don't surface as cryptic errors in report generation.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, Field

from transparency_engine.frameworks.base import BaseFramework


class ColumnSpec(BaseModel):
    name: str
    dtype: str = "any"  # any, integer, float, string, datetime
    required: bool = True


class SchemaDefinition(BaseModel):
    columns: list[ColumnSpec] = Field(default_factory=list)


# The minimal columns every metrics dataset must include.
REQUIRED_COLUMNS = [
    ColumnSpec(name="metric_id", dtype="string", required=True),
    ColumnSpec(name="period", dtype="string", required=True),
    ColumnSpec(name="value", dtype="float", required=True),
]


class ValidationError(BaseModel):
    column: str
    error: str
    severity: str = "error"  # error | warning


class SchemaValidator:
    """Validates a DataFrame against expected schema."""

    def __init__(self, framework: BaseFramework | None = None) -> None:
        self.framework = framework

    def validate(self, df: pd.DataFrame) -> list[ValidationError]:
        errors: list[ValidationError] = []

        # Check required columns
        for col_spec in REQUIRED_COLUMNS:
            if col_spec.name not in df.columns:
                errors.append(
                    ValidationError(
                        column=col_spec.name,
                        error=f"Required column '{col_spec.name}' is missing.",
                    )
                )

        if errors:
            return errors  # Can't validate further without required columns

        # Check for null values in required columns
        for col_spec in REQUIRED_COLUMNS:
            null_count = df[col_spec.name].isna().sum()
            if null_count > 0:
                errors.append(
                    ValidationError(
                        column=col_spec.name,
                        error=f"Column '{col_spec.name}' contains {null_count} null values.",
                    )
                )

        # Type checks
        if "value" in df.columns:
            non_numeric = pd.to_numeric(df["value"], errors="coerce").isna() & df["value"].notna()
            if non_numeric.any():
                count = non_numeric.sum()
                errors.append(
                    ValidationError(
                        column="value",
                        error=f"{count} rows have non-numeric 'value' entries.",
                    )
                )

        # Framework-specific: check that expected metric_ids are present
        if self.framework is not None:
            present_ids = set(df["metric_id"].unique())
            missing = self.framework.validate_completeness(present_ids)
            for mid in missing:
                errors.append(
                    ValidationError(
                        column="metric_id",
                        error=f"Required metric '{mid}' not found in data.",
                        severity="warning",
                    )
                )

        return errors


def validate_schema(
    df: pd.DataFrame, framework: BaseFramework | None = None
) -> list[ValidationError]:
    """Convenience function for one-shot validation."""
    return SchemaValidator(framework).validate(df)
