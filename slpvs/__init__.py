"""SLPVS: Smart License Plate-Based Verification System (simulation package)."""
from .config import SimConfig
from .generator import generate
from .metrics import evaluate

__all__ = ["SimConfig", "generate", "evaluate"]
__version__ = "1.1.0"
