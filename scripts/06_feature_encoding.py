"""Pipeline entry point: leakage-safe categorical feature encoding.

Run independently::

    python scripts/06_feature_encoding.py

Fits an ordinal encoder on the training split only, applies it to the
testing split via ``.transform()``, handles unseen testing-only
categories deterministically, and writes the encoded datasets to
``data/interim/``. Raw dataset files are never modified.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.data.feature_encoding import run_feature_encoding  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run feature encoding and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    report = run_feature_encoding()

    logger.info(
        "Encoding complete — %d categorical columns, format=%s, train=%d rows, test=%d rows",
        len(report["categorical_columns"]),
        report["output_format"],
        report["training"]["row_count"],
        report["testing"]["row_count"],
    )
    logger.info("Encoded datasets saved to data/interim/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
