"""Pipeline entry point: statistical validation & significance analysis (F.1).

Run independently::

    python scripts/14_statistical_validation.py

Loads existing outputs only — prediction repository, evaluation metrics,
SHAP comparison, and LIME comparison. Applies McNemar's test, bootstrap
confidence intervals, Wilcoxon signed-rank tests, effect size measures,
and Holm–Bonferroni multiple comparison correction.

No model is retrained, no SHAP value is recomputed, and no LIME
explanation is regenerated. All upstream artefacts are verified by
SHA-256 before and after the analysis.

Outputs written
~~~~~~~~~~~~~~~
outputs/statistics/
    statistical_results.parquet
    statistical_summary.csv

outputs/reports/
    statistical_validation_report.md
    statistical_validation_report.json

outputs/tables/
    hypothesis_tests.csv
    confidence_intervals.csv
    effect_sizes.csv

outputs/figures/
    bootstrap_distributions.png
    confidence_interval_comparison.png
    effect_sizes.png
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.evaluation.statistical_validation import run_statistical_validation  # noqa: E402

logger = get_logger(__name__)


def main() -> int:
    """Run the statistical validation pipeline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if the dataset is not ready, a required
        upstream artefact is missing, or the SHA-256 self-test fails.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_statistical_validation()
    except FileNotFoundError as exc:
        logger.exception("Required upstream artefact missing: %s", exc)
        return 1
    except RuntimeError as exc:
        logger.exception("Statistical validation failed: %s", exc)
        return 1

    n_tests = len(report.get("hypothesis_tests", []))
    n_rejected = sum(
        1 for t in report.get("hypothesis_tests", [])
        if t.get("reject_h0_holm")
    )
    n_cis = len(report.get("bootstrap_cis", []))
    n_effects = len(report.get("effect_sizes", []))

    logger.info(
        "Statistical validation complete — "
        "%d hypothesis tests (%d rejected at Holm-corrected α=0.05), "
        "%d bootstrap CIs, %d effect sizes",
        n_tests, n_rejected, n_cis, n_effects,
    )
    logger.info(
        "Outputs written to outputs/statistics/, outputs/reports/, "
        "outputs/tables/, outputs/figures/"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
