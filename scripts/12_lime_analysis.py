"""Pipeline entry point: LIME explainability analysis (E.3).

Run independently::

    python scripts/12_lime_analysis.py

Computes LIME explanations for both Random Forest models against the
exact same fixed sample subset Task E.2 already selected — read
directly from Task E.2's saved artifacts, never recomputed. No
retraining, no SHAP-LIME comparison (that is Task E.4's scope).
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.explainability.lime_analysis import run_lime_analysis  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run the LIME analysis pipeline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or the
        required upstream artefacts (Task D.1's models, Task E.2's
        SHAP analysis outputs) are missing.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_lime_analysis()
    except FileNotFoundError:
        logger.exception("Required upstream artefact missing")
        return 1

    logger.info(
        "LIME analysis complete — %d samples explained, top baseline feature: %s",
        report["subset_size"], report["baseline_importance"][0]["feature"],
    )
    logger.info("LIME explanations saved to outputs/lime/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
