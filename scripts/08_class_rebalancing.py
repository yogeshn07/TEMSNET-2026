"""Pipeline entry point: class rebalancing (SMOTE) for the training set.

Run independently::

    python scripts/08_class_rebalancing.py

Balances Task C.4's training_selected.parquet using SMOTE, producing
a parallel SMOTE-balanced training set alongside an untouched baseline
copy. The testing dataset is copied verbatim and never balanced,
fitted on, or transformed.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.class_rebalancing import run_class_rebalancing  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run class rebalancing and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or the
        required upstream artefact (Task C.4's selected datasets) is
        missing.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_class_rebalancing()
    except FileNotFoundError:
        logger.exception("Required upstream artefact missing")
        return 1

    logger.info(
        "Rebalancing complete — training: %d -> %d rows (%d synthetic), testing unchanged at %d rows",
        report["training_baseline"]["row_count"],
        report["training_balanced"]["row_count"],
        report["post_balancing"]["total_synthetic_samples"],
        report["testing_baseline"]["row_count"],
    )
    logger.info("Datasets saved to data/processed/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
