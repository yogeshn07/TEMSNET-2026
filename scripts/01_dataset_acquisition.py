"""Pipeline entry point: dataset acquisition and integrity verification.

Run independently::

    python scripts/01_dataset_acquisition.py

Locates the UNSW-NB15 raw files described in ``configs/dataset.yaml``
inside ``data/raw/``, computes a cryptographic hash for each, and
writes ``outputs/reports/dataset_inventory.json`` and ``.md``.

Exits with a non-zero status if any expected file is missing, so
downstream pipeline stages do not run against an unverified dataset.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.logging_config import get_logger, setup_logging  # noqa: E402
from src.data.dataset_acquisition import run_dataset_acquisition  # noqa: E402

logger = get_logger(__name__)


def main() -> int:
    """Run dataset acquisition and return a process exit code.

    Returns:
        ``0`` if verification passed, ``1`` otherwise.
    """
    setup_logging()
    inventory = run_dataset_acquisition()

    if inventory["verification_status"] != "PASS":
        logger.error(
            "Dataset acquisition FAILED — missing file(s): %s",
            ", ".join(inventory["missing_files"]),
        )
        logger.error("Obtain UNSW-NB15 manually from: %s", inventory["source"])
        logger.error("Place the missing file(s) into: %s", inventory["raw_data_dir"])
        return 1

    logger.info("Dataset acquisition complete — reports saved to outputs/reports/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
