"""Model training and inference.

Public API
~~~~~~~~~~
- :func:`run_random_forest_baseline` — train and evaluate the dual
  Random Forest baseline (original vs. SMOTE-balanced training data),
  both scored on the same untouched testing set.
- :func:`run_prediction_repository` — archive predictions from both
  trained models against the shared testing set, without retraining;
  the single source of truth for SHAP and LIME (Phase E).
"""

from src.models.prediction_repository import run_prediction_repository
from src.models.random_forest import run_random_forest_baseline

__all__ = [
    "run_prediction_repository",
    "run_random_forest_baseline",
]
