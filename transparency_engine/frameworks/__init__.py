"""Regulatory framework definitions."""

from transparency_engine.frameworks.base import BaseFramework
from transparency_engine.frameworks.custom import CustomFramework
from transparency_engine.frameworks.dsa import DSAFramework
from transparency_engine.frameworks.lgpd import LGPDFramework
from transparency_engine.frameworks.osa import OSAFramework

REGISTRY: dict[str, type[BaseFramework]] = {
    "dsa": DSAFramework,
    "lgpd": LGPDFramework,
    "osa": OSAFramework,
}


def get_framework(name: str) -> BaseFramework:
    """Instantiate a framework by its registry key."""
    cls = REGISTRY.get(name.lower())
    if cls is None:
        raise ValueError(f"Unknown framework '{name}'. Available: {', '.join(sorted(REGISTRY))}")
    return cls()


__all__ = [
    "BaseFramework",
    "DSAFramework",
    "LGPDFramework",
    "OSAFramework",
    "CustomFramework",
    "get_framework",
    "REGISTRY",
]
