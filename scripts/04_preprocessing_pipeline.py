"""Pipeline entry point: preprocessing pipeline design & safe stages.

Run independently::

    python scripts/04_preprocessing_pipeline.py

Runs stages 1-3 (dataset validation, loading, schema verification)
and separates features from the target (X/y) for both splits
independently. Stages 4-10 are architecturally defined but not yet
implemented (see Research Tasks C.2 onward). No feature value is
modified. Writes the pipeline design report to ``outputs/reports/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.data.preprocessing_pipeline import run_preprocessing_pipeline  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run the preprocessing pipeline's safe stages and return an exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or schema
        validation fails.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        result = run_preprocessing_pipeline()
    except Exception:
        logger.exception("Preprocessing pipeline failed")
        return 1

    logger.info(
        "Pipeline complete — training X=%s, testing X=%s",
        result.train.X.shape, result.test.X.shape,
    )
    logger.info("Design report saved to outputs/reports/preprocessing_pipeline_design.{json,md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
