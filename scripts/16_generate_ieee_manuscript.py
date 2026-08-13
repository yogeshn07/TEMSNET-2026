"""Pipeline entry point: IEEE conference manuscript generation (F.3).

Run independently::

    python scripts/16_generate_ieee_manuscript.py

Loads all existing outputs from F.1 (statistical validation) and F.2
(results interpretation) and assembles a complete IEEE conference paper.

No model is retrained. No preprocessing is rerun. No explanations are
regenerated. All numerical values are sourced from existing pipeline outputs.

Research Questions Addressed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All four research questions (RQ1–RQ4) as answered in F.2 are written into
the manuscript with exact numerical values from pipeline outputs.

Outputs written
~~~~~~~~~~~~~~~
docs/paper/
    manuscript.md           — full IEEE conference paper in Markdown
    manuscript.docx         — Word document (if python-docx is installed)
    manuscript_outline.md   — section structure with word-count targets
    figure_table_map.csv    — mapping of all 30 existing figures to sections
    publication_checklist.md — IEEE pre-submission checklist
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import verify_dataset_ready  # noqa: E402
from src.reporting.ieee_manuscript_generator import run_ieee_manuscript_generator  # noqa: E402

logger = get_logger(__name__)


def main() -> int:
    """Run the IEEE manuscript generation pipeline and return a process exit code.

    Returns:
        ``0`` on success, ``1`` if a required upstream artefact is missing
        or any output cannot be written.
    """
    setup_logging()

    if not verify_dataset_ready():
        logger.error("Dataset not ready — run scripts/01_dataset_acquisition.py first")
        return 1

    try:
        report = run_ieee_manuscript_generator()
    except FileNotFoundError as exc:
        logger.exception(
            "Required upstream artefact missing: %s — "
            "run scripts/14_statistical_validation.py and "
            "scripts/15_results_interpretation.py first",
            exc,
        )
        return 1
    except Exception:
        logger.exception("Manuscript generation failed unexpectedly")
        return 1

    logger.info(
        "F.3 complete — %d sections, ~%d words, %d figures catalogued, %d tables catalogued",
        len(report.get("sections", [])),
        report.get("approximate_word_count", 0),
        report.get("n_figures_catalogued", 0),
        report.get("n_tables_catalogued", 0),
    )
    logger.info("manuscript.md:           %s", report["manuscript_md"])
    if report.get("manuscript_docx"):
        logger.info("manuscript.docx:         %s", report["manuscript_docx"])
    else:
        logger.warning(
            "manuscript.docx not generated — install python-docx: pip install python-docx"
        )
    logger.info("manuscript_outline.md:   %s", report["manuscript_outline"])
    logger.info("figure_table_map.csv:    %s", report["figure_table_map"])
    logger.info("publication_checklist.md:%s", report["publication_checklist"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
