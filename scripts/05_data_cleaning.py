"""Pipeline entry point: evidence-based data quality validation & cleaning.

Run independently::

    python scripts/05_data_cleaning.py

Re-verifies missing values, duplicates, schema consistency, and
target integrity for both splits independently, then applies only
cleaning operations justified by live evidence (expected: none,
consistent with B.1-B.3 findings). Writes reports to
``outputs/reports/`` and tables to ``outputs/tables/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.data_cleaning import run_data_cleaning  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run data quality validation/cleaning and return an exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    report = run_data_cleaning()
    summary = report["summary"]

    logger.info(
        "Cleaning summary — actions performed: %s | actions not performed: %s",
        summary["actions_performed"] or "none",
        summary["actions_not_performed"],
    )
    logger.info("Reports saved to outputs/reports/, tables saved to outputs/tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
