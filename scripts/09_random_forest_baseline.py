"""Pipeline entry point: dual Random Forest baseline (D.1).

Run independently::

    python scripts/09_random_forest_baseline.py

Trains Model A on training_baseline.parquet and Model B on
training_balanced_smote.parquet, both with identical hyperparameters,
and evaluates both on the same untouched testing_baseline.parquet.
Saves models, metrics tables, confusion matrix figures, and reports.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.models.random_forest import run_random_forest_baseline  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run the dual Random Forest baseline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or the
        required upstream artefacts (Task C.5's processed datasets)
        are missing.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_random_forest_baseline()
    except FileNotFoundError:
        logger.exception("Required upstream artefact missing")
        return 1

    logger.info(
        "Baseline accuracy=%.4f (macro F1=%.4f) | SMOTE accuracy=%.4f (macro F1=%.4f)",
        report["baseline"]["accuracy"], report["baseline"]["macro_f1"],
        report["smote"]["accuracy"], report["smote"]["macro_f1"],
    )
    logger.info("Models saved to outputs/models/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
