"""Pipeline entry point: integrated results interpretation (F.2).

Run independently::

    python scripts/15_results_interpretation.py

Loads all existing outputs — prediction repository, evaluation metrics,
SHAP / LIME comparison outputs, statistical validation results — and
synthesises them into a scientifically rigorous interpretation.

No model is retrained. No preprocessing is rerun. No explanations are
regenerated. All artefacts are read-only.

Research Questions Addressed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- RQ1: How did SMOTE influence predictive performance?
- RQ2: How did SMOTE influence model explainability?
- RQ3: What relationship exists between predictive performance and explainability?
- RQ4: Does the evidence support the research hypothesis?

Outputs written
~~~~~~~~~~~~~~~
outputs/reports/
    integrated_results_report.md
    integrated_results_report.json

outputs/tables/
    key_findings_summary.csv
    research_question_summary.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.evaluation.results_interpreter import run_results_interpretation  # noqa: E402

logger = get_logger(__name__)


def main() -> int:
    """Run the results interpretation pipeline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if a required upstream artefact is
        missing or any output cannot be written.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_results_interpretation()
    except FileNotFoundError as exc:
        logger.exception("Required upstream artefact missing: %s", exc)
        return 1
    except Exception:
        logger.exception("Results interpretation failed unexpectedly")
        return 1

    rqs = report.get("research_questions", {})
    logger.info(
        "Results interpretation complete — %d research questions answered: %s",
        len(rqs),
        ", ".join(
            f"{v['rq']}={v['verdict']}"
            for v in rqs.values()
        ),
    )
    logger.info(
        "Outputs written to outputs/reports/ and outputs/tables/"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
