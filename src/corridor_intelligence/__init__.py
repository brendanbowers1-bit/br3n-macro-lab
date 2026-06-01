"""USD/MXN corridor intelligence — validated data, transparent risk score, briefs."""

from .brief import generate_corridor_brief
from .dataset import load_us_mx_remittances
from .risk_score import compute_corridor_risk_score
from .validate import validate_us_mx_dataset

__all__ = [
    "load_us_mx_remittances",
    "validate_us_mx_dataset",
    "compute_corridor_risk_score",
    "generate_corridor_brief",
]
