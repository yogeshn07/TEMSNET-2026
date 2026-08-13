"""Explainability methods: SHAP, LIME, and their comparison.

Public API
~~~~~~~~~~
- :func:`run_shap_analysis` — SHAP TreeExplainer analysis for both
  Random Forest models against one fixed, deterministic sample subset.
- :func:`run_lime_analysis` — LIME local explanations for both models
  against the exact same subset Task E.2 already selected.
- :func:`run_explanation_comparison` — explanation reliability and
  SHAP-LIME comparative analysis across both models (no retraining,
  no explanation regeneration — compares Task E.2/E.3 outputs only).
"""

from src.explainability.explanation_comparison import run_explanation_comparison
from src.explainability.lime_analysis import run_lime_analysis
from src.explainability.shap_analysis import run_shap_analysis

__all__ = [
    "run_explanation_comparison",
    "run_lime_analysis",
    "run_shap_analysis",
]
