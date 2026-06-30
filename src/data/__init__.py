"""Data loading and preprocessing.

Public API
~~~~~~~~~~
- :func:`run_dataset_acquisition` — locate, hash, and report on the
  raw UNSW-NB15 dataset files.
- :func:`verify_dataset_ready` — cheap existence-only gate-check for
  downstream pipeline stages.
"""

from src.data.dataset_acquisition import run_dataset_acquisition, verify_dataset_ready

__all__ = [
    "run_dataset_acquisition",
    "verify_dataset_ready",
]
