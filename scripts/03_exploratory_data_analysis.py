"""Pipeline entry point: exploratory data analysis of UNSW-NB15 splits.

Run independently::

    python scripts/03_exploratory_data_analysis.py

Gates on dataset integrity (Task B.1) before running. Purely
descriptive and read-only — no cleaning, encoding, scaling,
balancing, or merging. Writes figures to ``outputs/figures/``, CSV
tables to ``outputs/tables/``, and JSON/Markdown reports to
``outputs/reports/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.data.eda import run_eda  # noqa: E402

logger = get_logger(__name__)


def main() -> int:
    """Run the EDA pipeline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    report = run_eda()
    summary = report["summary"]

    logger.info(
        "EDA summary — max IR: %.1fx (%s), %d highly skewed features, %d highly correlated pairs",
        summary["max_imbalance_ratio"],
        summary["max_imbalance_class"],
        summary["num_highly_skewed_features"],
        summary["num_highly_correlated_pairs"],
    )
    logger.info("Reports saved to outputs/reports/, outputs/figures/, outputs/tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
