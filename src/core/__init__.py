"""Core infrastructure: logging, reproducibility, exceptions, validation.

Public API
~~~~~~~~~~
- :func:`get_logger` — obtain a named logger (auto-initialises).
- :func:`setup_logging` — explicit logging initialisation.
- :func:`set_global_seed` — seed all RNGs for reproducibility.
- :func:`get_current_seed` — retrieve the active seed.
- :func:`seed_context` — temporary seed with state restoration.
- :func:`get_reproducibility_report` — environment snapshot dict.
- :func:`validate_environment` — pre-flight environment check.
- :func:`generate_environment_report` — platform/Python info dict.
"""

from src.core.logging_config import get_logger, setup_logging
from src.core.reproducibility import (
    get_current_seed,
    get_reproducibility_report,
    seed_context,
    set_global_seed,
)
from src.core.env_validation import (
    generate_environment_report,
    validate_environment,
)

__all__ = [
    "generate_environment_report",
    "get_current_seed",
    "get_logger",
    "get_reproducibility_report",
    "seed_context",
    "set_global_seed",
    "setup_logging",
    "validate_environment",
]
