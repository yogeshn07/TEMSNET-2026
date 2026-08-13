"""Pipeline entry point: prediction repository (E.1).

Run independently::

    python scripts/10_prediction_repository.py

Loads both trained Random Forest models (no retraining) and the
shared testing set, generates and archives predictions for both, and
builds the sample registry that SHAP (E.2) and LIME (E.3) will reuse.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.models.prediction_repository import run_prediction_repository  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run the prediction repository pipeline and return an exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or the
        required upstream artefacts (Task D.1's trained models) are
        missing.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_prediction_repository()
    except FileNotFoundError:
        logger.exception("Required upstream artefact missing")
        return 1

    logger.info(
        "Repository complete — %d predictions archived per model, agreement=%.4f",
        report["baseline_count"], report["agreement"]["overall_agreement_rate"],
    )
    logger.info("Predictions saved to outputs/predictions/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
