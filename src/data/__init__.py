"""Data loading and preprocessing.

Public API
~~~~~~~~~~
- :func:`run_dataset_acquisition` — locate, hash, and report on the
  raw UNSW-NB15 dataset files.
- :func:`verify_dataset_ready` — cheap existence-only gate-check for
  downstream pipeline stages.
- :func:`run_dataset_profiling` — descriptive profiling of the
  training and testing splits (schema, target, missing data, etc.).
- :func:`run_eda` — exploratory data analysis (class distribution,
  correlations, outliers, distribution characteristics).
- :func:`run_preprocessing_pipeline` — preprocessing pipeline
  architecture: schema validation and X/y separation (safe stages
  only; transformations are implemented in later Research Tasks).
- :func:`run_data_cleaning` — evidence-based data quality validation
  and (gated) cleaning for both splits.
- :func:`run_feature_encoding` — leakage-safe categorical feature
  encoding (fit on training only, applied to testing via transform).
- :func:`run_feature_selection` — target-leakage elimination and
  final baseline feature set construction.
- :func:`run_class_rebalancing` — SMOTE class balancing applied to
  the training split only; testing split is never balanced.
"""

from src.data.class_rebalancing import run_class_rebalancing
from src.data.data_cleaning import run_data_cleaning
from src.data.dataset_acquisition import run_dataset_acquisition, verify_dataset_ready
from src.data.dataset_profile import run_dataset_profiling
from src.data.eda import run_eda
from src.data.feature_encoding import run_feature_encoding
from src.data.feature_selection import run_feature_selection
from src.data.preprocessing_pipeline import run_preprocessing_pipeline

__all__ = [
    "run_class_rebalancing",
    "run_data_cleaning",
    "run_dataset_acquisition",
    "run_dataset_profiling",
    "run_eda",
    "run_feature_encoding",
    "run_feature_selection",
    "run_preprocessing_pipeline",
    "verify_dataset_ready",
]
