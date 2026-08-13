"""Pipeline entry point: feature selection and target-leakage elimination.

Run independently::

    python scripts/07_feature_selection.py

Audits every feature produced by Task C.3's encoding stage, removes
features with confirmed target leakage (``id``, ``label``), reviews
Task B.3's correlation findings without removing correlated features,
and exports the final baseline datasets to ``data/processed/``. Raw
and interim datasets are never modified.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.data.feature_selection import run_feature_selection  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run feature selection and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or the
        required upstream artefacts (encoded interim data, B.3
        correlation findings) are missing.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_feature_selection()
    except FileNotFoundError:
        logger.exception("Required upstream artefact missing")
        return 1

    s = report["summary"]
    logger.info(
        "Feature selection complete — %d removed (%s), %d retained, output=%s",
        s["removed_count"], s["removed_columns"], s["retained_count"], report["output_format"],
    )
    logger.info("Selected datasets saved to data/processed/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
