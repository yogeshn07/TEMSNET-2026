"""Pipeline entry point: descriptive profiling of UNSW-NB15 splits.

Run independently::

    python scripts/02_dataset_profile.py

Gates on dataset integrity (Task B.1) before profiling. Profiles the
training and testing splits independently — purely descriptive, no
cleaning, encoding, scaling, or merging. Writes JSON/Markdown reports
and CSV tables to ``outputs/reports/`` and ``outputs/tables/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.data.dataset_profile import run_dataset_profiling  # noqa: E402

logger = get_logger(__name__)


def main() -> int:
    """Run dataset profiling and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or
        profiling fails.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    result = run_dataset_profiling()
    summary = result["summary"]

    logger.info(
        "Profile summary — train: %d rows, test: %d rows, %d attack classes",
        summary["total_training_samples"],
        summary["total_testing_samples"],
        summary["num_attack_classes"],
    )
    logger.info("Reports saved to outputs/reports/ and outputs/tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
