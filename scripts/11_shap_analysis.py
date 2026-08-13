"""Pipeline entry point: SHAP explainability analysis (E.2).

Run independently::

    python scripts/11_shap_analysis.py

Computes SHAP TreeExplainer values for both Random Forest models
against one fixed, deterministic sample subset derived from the
Task E.1 prediction repository. No retraining, no LIME.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.explainability.shap_analysis import run_shap_analysis  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run the SHAP analysis pipeline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or the
        required upstream artefacts (Task D.1's models, Task E.1's
        prediction repository) are missing.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_shap_analysis()
    except FileNotFoundError:
        logger.exception("Required upstream artefact missing")
        return 1

    logger.info(
        "SHAP analysis complete — %d samples explained, top baseline feature: %s",
        report["subset_size"], report["baseline_importance"][0]["feature"],
    )
    logger.info("SHAP values saved to outputs/shap/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
