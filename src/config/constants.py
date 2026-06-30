"""Project-wide constants.

Only true invariants belong here — values that never change across
experiments, configurations, or runs.  Dataset-specific metadata
(feature names, class mappings) belongs in YAML configuration or
dedicated metadata modules, not here.
"""

from typing import Final

# ── Project identity ────────────────────────────────────────
PROJECT_NAME: Final[str] = "TEMSNET-2026"
PROJECT_TITLE: Final[str] = (
    "Impact of Class Imbalance on XAI Explanation Quality "
    "in ML-Based Network Intrusion Detection Systems"
)
VERSION: Final[str] = "0.1.0"
VENUE: Final[str] = "IEEE TEMSMET 2026"

# ── Supported datasets ─────────────────────────────────────
SUPPORTED_DATASETS: Final[tuple[str, ...]] = ("unsw_nb15",)

# ── File encoding ───────────────────────────────────────────
DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_CSV_SEPARATOR: Final[str] = ","

# ── Reproducibility defaults ───────────────────────────────
DEFAULT_RANDOM_SEED: Final[int] = 42

# ── Configuration file names ───────────────────────────────
CONFIG_DIR_NAME: Final[str] = "configs"
EXPERIMENT_CONFIG: Final[str] = "experiment.yaml"
PATHS_CONFIG: Final[str] = "paths.yaml"
LOGGING_CONFIG: Final[str] = "logging.yaml"
