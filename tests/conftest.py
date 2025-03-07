"""Shared fixtures for the test suite."""

import pandas as pd
import pytest

from transparency_engine.config import PeriodSpec
from transparency_engine.frameworks.dsa import DSAFramework
from transparency_engine.frameworks.osa import OSAFramework


@pytest.fixture
def dsa_framework():
    return DSAFramework()


@pytest.fixture
def osa_framework():
    return OSAFramework()


@pytest.fixture
def sample_dsa_data():
    """Minimal valid dataset covering required DSA metrics."""
    fw = DSAFramework()
    rows = []
    for req in fw.metric_requirements():
        rows.append({"metric_id": req.metric_id, "period": "2024-H1", "value": 100})
    return pd.DataFrame(rows)


@pytest.fixture
def sample_period():
    return PeriodSpec.parse("2024-H1")


@pytest.fixture
def sample_multi_period_data():
    """Dataset with two periods for comparison tests."""
    metrics = [
        "notices_received",
        "notices_actioned",
        "complaints_received",
        "complaints_reversed",
    ]
    rows = []
    for mid in metrics:
        rows.append({"metric_id": mid, "period": "2024-H1", "value": 200})
        rows.append({"metric_id": mid, "period": "2023-H2", "value": 150})
    return pd.DataFrame(rows)
