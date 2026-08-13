"""Pipeline entry point: explanation reliability & comparative analysis (E.4).

Run independently::

    python scripts/13_explanation_comparison.py

Compares Task E.2's SHAP outputs and Task E.3's LIME outputs across
the baseline and SMOTE-balanced Random Forest models. No retraining,
no explanation regeneration — this script only loads and compares
already-saved outputs.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.explainability.explanation_comparison import run_explanation_comparison  # noqa: E402


logger = get_logger(__name__)


def main() -> int:
    """Run the explanation comparison pipeline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready or the
        required upstream artefacts (Task E.2's SHAP outputs, Task
        E.3's LIME outputs) are missing.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_explanation_comparison()
    except FileNotFoundError:
        logger.exception("Required upstream artefact missing")
        return 1

    logger.info(
        "Comparison complete — %d samples, %d agreement pairs analysed",
        report["subset_size"], len(report["agreement_results"]),
    )
    logger.info("Comparison outputs saved to outputs/comparison/, reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
