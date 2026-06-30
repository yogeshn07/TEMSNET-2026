"""Central logging framework for the project.

Provides two public functions:

* :func:`setup_logging` — initialise handlers once per process.
* :func:`get_logger` — return a named logger (calls ``setup_logging``
  automatically on first use).

Every other module in the project should do::

    from src.core.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("message")

Design decisions
~~~~~~~~~~~~~~~~
* Built entirely on the standard-library ``logging`` module so it is
  thread-safe, zero-dependency, and familiar.
* ``setup_logging`` is idempotent — calling it more than once never
  duplicates handlers.
* ``RotatingFileHandler`` keeps disk usage bounded without manual
  intervention.
* All tunables come from ``configs/logging.yaml`` via the config
  loader from Task 2.1; nothing is hardcoded.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# ── private state ───────────────────────────────────────────
_logging_initialised: bool = False

# ── defaults (used when YAML keys are absent) ───────────────
_DEFAULTS: dict[str, Any] = {
    "log_level": "INFO",
    "console_logging": True,
    "file_logging": True,
    "log_dir": "outputs/logs",
    "log_file_name": "temsnet.log",
    "max_bytes": 10_485_760,
    "backup_count": 5,
    "log_format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
}


# ── internal helpers ────────────────────────────────────────

def _load_logging_config() -> dict[str, Any]:
    """Load the ``logging`` section from the merged project config.

    Returns:
        Logging configuration dictionary with defaults applied for
        any missing keys.
    """
    try:
        from src.config.loader import get_config
        full_cfg = get_config()
        yaml_cfg: dict[str, Any] = full_cfg.get("logging", {})
    except Exception:
        yaml_cfg = {}

    merged = {**_DEFAULTS, **yaml_cfg}
    return merged


def _resolve_log_dir(raw_path: str) -> Path:
    """Resolve *raw_path* relative to the project root.

    Args:
        raw_path: Directory path (absolute or project-relative).

    Returns:
        Absolute ``Path`` to the log directory, created if missing.
    """
    path = Path(raw_path)
    if not path.is_absolute():
        try:
            from src.config.paths import _find_project_root
            path = _find_project_root() / path
        except FileNotFoundError:
            path = Path.cwd() / path
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _make_formatter(cfg: dict[str, Any]) -> logging.Formatter:
    """Build a :class:`logging.Formatter` from config values.

    Args:
        cfg: Logging configuration dictionary.

    Returns:
        Configured ``Formatter`` instance.
    """
    return logging.Formatter(
        fmt=cfg["log_format"],
        datefmt=cfg["date_format"],
    )


# ── public API ──────────────────────────────────────────────

def setup_logging(config_override: dict[str, Any] | None = None) -> None:
    """Initialise the project-wide logging configuration.

    Configures the root logger with a console handler and/or a
    rotating file handler based on ``configs/logging.yaml``.

    This function is **idempotent**: repeated calls are no-ops
    unless the root logger currently has no handlers (e.g. after
    a test harness reset).

    Args:
        config_override: Optional dict that takes precedence over
            YAML values.  Useful for tests or one-off scripts that
            need non-standard settings.
    """
    global _logging_initialised  # noqa: PLW0603

    root = logging.getLogger()

    if _logging_initialised and root.handlers:
        return

    cfg = _load_logging_config()
    if config_override:
        cfg.update(config_override)

    level = getattr(logging, cfg["log_level"].upper(), logging.INFO)
    root.setLevel(level)

    formatter = _make_formatter(cfg)

    # ── console handler ──────────────────────────────────────
    if cfg["console_logging"]:
        console = logging.StreamHandler(sys.stderr)
        console.setLevel(level)
        console.setFormatter(formatter)
        root.addHandler(console)

    # ── file handler ─────────────────────────────────────────
    if cfg["file_logging"]:
        log_dir = _resolve_log_dir(cfg["log_dir"])
        log_path = log_dir / cfg["log_file_name"]

        file_handler = RotatingFileHandler(
            filename=str(log_path),
            maxBytes=int(cfg["max_bytes"]),
            backupCount=int(cfg["backup_count"]),
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    _logging_initialised = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, initialising logging on first call.

    This is the **only function** downstream modules need::

        from src.core.logging_config import get_logger

        logger = get_logger(__name__)

    Args:
        name: Logger name — conventionally ``__name__``.

    Returns:
        A :class:`logging.Logger` bound to *name*.
    """
    if not _logging_initialised:
        setup_logging()
    return logging.getLogger(name)
