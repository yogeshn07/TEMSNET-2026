"""YAML configuration loader with validation.

Provides a single entry-point — :func:`load_config` — that reads a
YAML file, validates required keys, and returns a plain dictionary.
A module-level singleton :func:`get_config` caches the merged
experiment configuration so it is loaded only once per process.

Design decisions
~~~~~~~~~~~~~~~~
* Returns ``dict`` rather than a custom dataclass so that downstream
  modules are free to destructure only the keys they need without
  coupling to a central schema that would change with every milestone.
* Validation is opt-in: callers pass *required_keys* when they need
  guarantees, but exploratory scripts can load raw YAML without
  constraints.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.config.constants import (
    CONFIG_DIR_NAME,
    EXPERIMENT_CONFIG,
    LOGGING_CONFIG,
    PATHS_CONFIG,
)
from src.config.paths import PathManager, _find_project_root


# ── private state ───────────────────────────────────────────
_config_cache: dict[str, Any] | None = None


# ── public API ──────────────────────────────────────────────

def load_yaml(filepath: Path) -> dict[str, Any]:
    """Read a single YAML file and return its contents as a dict.

    Args:
        filepath: Absolute or relative path to a ``.yaml`` file.

    Returns:
        Parsed YAML content.

    Raises:
        FileNotFoundError: If *filepath* does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
        ValueError: If the file is empty or does not contain a mapping.
    """
    filepath = Path(filepath).resolve()
    if not filepath.exists():
        raise FileNotFoundError(f"Configuration file not found: {filepath}")

    with open(filepath, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a YAML mapping in {filepath.name}, "
            f"got {type(data).__name__}"
        )
    return data


def validate_keys(
    config: dict[str, Any],
    required_keys: list[str],
    source: str = "config",
) -> None:
    """Verify that *config* contains every key in *required_keys*.

    Args:
        config: Configuration dictionary to check.
        required_keys: Keys that must be present.
        source: Human-readable label for error messages.

    Raises:
        KeyError: If any required key is missing, listing all
            missing keys in a single message.
    """
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise KeyError(
            f"Missing required key(s) in {source}: {missing}"
        )


def load_config(
    filepath: Path,
    required_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Load and optionally validate a YAML configuration file.

    Args:
        filepath: Path to the YAML file.
        required_keys: If provided, :func:`validate_keys` is called
            against the loaded dict before returning.

    Returns:
        Configuration dictionary.

    Raises:
        FileNotFoundError: File does not exist.
        yaml.YAMLError: Invalid YAML syntax.
        ValueError: File is empty or not a mapping.
        KeyError: A required key is absent.
    """
    config = load_yaml(filepath)
    if required_keys:
        validate_keys(config, required_keys, source=str(filepath.name))
    return config


def get_config(reload: bool = False) -> dict[str, Any]:
    """Return the merged project configuration (cached singleton).

    Loads and merges all three standard config files on first call:

    * ``configs/experiment.yaml``
    * ``configs/paths.yaml``
    * ``configs/logging.yaml``

    Subsequent calls return the cached result unless *reload* is
    ``True``.

    Args:
        reload: Force re-reading from disk when *True*.

    Returns:
        Merged configuration dictionary with top-level keys
        ``"experiment"``, ``"paths"``, and ``"logging"``.
    """
    global _config_cache  # noqa: PLW0603

    if _config_cache is not None and not reload:
        return _config_cache

    root = _find_project_root()
    config_dir = root / CONFIG_DIR_NAME

    merged: dict[str, Any] = {
        "experiment": load_yaml(config_dir / EXPERIMENT_CONFIG),
        "paths": load_yaml(config_dir / PATHS_CONFIG),
        "logging": load_yaml(config_dir / LOGGING_CONFIG),
    }

    _config_cache = merged
    return merged


def get_path_manager(config: dict[str, Any] | None = None) -> PathManager:
    """Build a :class:`PathManager` from the loaded path configuration.

    Args:
        config: Full merged config dict (as returned by
            :func:`get_config`).  Loaded automatically when *None*.

    Returns:
        A configured :class:`PathManager` instance.
    """
    if config is None:
        config = get_config()
    return PathManager(path_overrides=config.get("paths", {}))
