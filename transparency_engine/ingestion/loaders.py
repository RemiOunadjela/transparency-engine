"""Data source loaders.

Supports CSV, JSON, Parquet, and SQL sources. All loaders return a
pandas DataFrame with a standardised column schema.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class DataLoader:
    """Unified data loader with format auto-detection."""

    SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet", ".pq"}

    def __init__(self, path: str | Path, **kwargs: Any) -> None:
        self.path = Path(path)
        self.kwargs = kwargs

    def load(self) -> pd.DataFrame:
        suffix = self.path.suffix.lower()
        if suffix == ".csv":
            return self._load_csv()
        elif suffix in (".json", ".jsonl"):
            return self._load_json()
        elif suffix in (".parquet", ".pq"):
            return self._load_parquet()
        else:
            raise ValueError(
                f"Unsupported file format '{suffix}'. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

    def _load_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.path, **self.kwargs)

    def _load_json(self) -> pd.DataFrame:
        lines = self.path.suffix.lower() == ".jsonl"
        return pd.read_json(self.path, lines=lines, **self.kwargs)

    def _load_parquet(self) -> pd.DataFrame:
        return pd.read_parquet(self.path, **self.kwargs)


def load_data(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    """Convenience function wrapping DataLoader."""
    return DataLoader(path, **kwargs).load()


def load_from_sql(query: str, connection_string: str) -> pd.DataFrame:
    """Load data via SQLAlchemy connection.

    Requires the ``sql`` extra: ``pip install transparency-engine[sql]``
    """
    try:
        from sqlalchemy import create_engine
    except ImportError:
        raise ImportError(
            "SQLAlchemy is required for SQL loading. "
            "Install with: pip install transparency-engine[sql]"
        ) from None

    engine = create_engine(connection_string)
    return pd.read_sql(query, engine)
