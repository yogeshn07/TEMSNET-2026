"""Evaluation, statistical validation, and results interpretation.

Public API
~~~~~~~~~~
- :func:`run_statistical_validation` — Task F.1: statistical validation
  of existing experimental results using McNemar's test, bootstrap CIs,
  Wilcoxon signed-rank tests, and effect size measures. Loads existing
  outputs only — no model retraining, no SHAP/LIME regeneration.
- :func:`run_results_interpretation` — Task F.2: integrated scientific
  synthesis answering all four research questions from existing outputs.
  No new experiments are executed.
"""

from src.evaluation.results_interpreter import run_results_interpretation
from src.evaluation.statistical_validation import run_statistical_validation

__all__ = [
    "run_results_interpretation",
    "run_statistical_validation",
]
