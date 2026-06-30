"""Pre-flight environment validation.

Detects common setup problems before any experiment runs and returns
a structured, JSON-serialisable report.  Every check is independent:
one failure does not prevent others from running.

Usage::

    from src.core.env_validation import validate_environment

    report = validate_environment()
    if report["overall_status"] != "PASS":
        print("Fix issues before running experiments")

Design decisions
~~~~~~~~~~~~~~~~
* Each ``check_*`` function returns a small dict with a ``status``
  key (``"PASS"`` or ``"FAIL"``) plus detail fields.  This keeps
  individual checks composable and testable in isolation.
* ``validate_environment`` aggregates all checks into a single report
  and sets ``overall_status`` to ``"FAIL"`` if *any* check failed.
* Disk-space reporting uses :func:`shutil.disk_usage` which works on
  Windows, Linux, and macOS without external dependencies.
"""

from __future__ import annotations

import importlib
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from src.config.constants import (
    CONFIG_DIR_NAME,
    EXPERIMENT_CONFIG,
    LOGGING_CONFIG,
    PATHS_CONFIG,
)
from src.config.paths import _find_project_root
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# ── constants ───────────────────────────────────────────────

_MIN_PYTHON: tuple[int, int] = (3, 10)

_REQUIRED_PACKAGES: tuple[str, ...] = (
    "numpy",
    "pandas",
    "sklearn",
    "yaml",
    "matplotlib",
)

_PACKAGE_IMPORT_TO_NAME: dict[str, str] = {
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
}

_REQUIRED_DIRS: tuple[str, ...] = (
    "configs",
    "data",
    "outputs",
    "src",
    "tests",
    "scripts",
    "notebooks",
    "docs",
)

_REQUIRED_CONFIGS: tuple[str, ...] = (
    EXPERIMENT_CONFIG,
    PATHS_CONFIG,
    LOGGING_CONFIG,
)


# ── individual checks ──────────────────────────────────────

def check_python_version() -> dict[str, Any]:
    """Verify the Python interpreter meets the minimum version.

    Returns:
        Dict with ``status``, ``version``, ``executable``, and
        ``meets_minimum`` fields.
    """
    current = sys.version_info[:2]
    meets = current >= _MIN_PYTHON
    result = {
        "status": "PASS" if meets else "FAIL",
        "version": f"{current[0]}.{current[1]}",
        "version_full": sys.version,
        "executable": sys.executable,
        "minimum_required": f"{_MIN_PYTHON[0]}.{_MIN_PYTHON[1]}",
        "meets_minimum": meets,
    }
    if meets:
        logger.info("Python version: %s (OK)", result["version"])
    else:
        logger.error(
            "Python %s found — minimum %s required",
            result["version"],
            result["minimum_required"],
        )
    return result


def check_required_packages() -> dict[str, Any]:
    """Check that all required packages are importable.

    Returns:
        Dict with ``status``, per-package ``installed`` flag, and
        ``version`` where available.
    """
    packages: dict[str, dict[str, Any]] = {}
    all_ok = True

    for import_name in _REQUIRED_PACKAGES:
        display_name = _PACKAGE_IMPORT_TO_NAME.get(import_name, import_name)
        try:
            mod = importlib.import_module(import_name)
            version = getattr(mod, "__version__", "unknown")
            packages[display_name] = {
                "installed": True,
                "version": version,
            }
            logger.debug("Package %s: %s", display_name, version)
        except ImportError:
            packages[display_name] = {
                "installed": False,
                "version": None,
            }
            logger.error("Package %s: NOT INSTALLED", display_name)
            all_ok = False

    return {
        "status": "PASS" if all_ok else "FAIL",
        "packages": packages,
    }


def check_directory_structure() -> dict[str, Any]:
    """Verify that all required project directories exist.

    Returns:
        Dict with ``status`` and per-directory existence flags.
    """
    try:
        root = _find_project_root()
    except FileNotFoundError:
        logger.error("Cannot locate project root")
        return {
            "status": "FAIL",
            "project_root": None,
            "directories": {},
        }

    directories: dict[str, bool] = {}
    all_ok = True

    for dir_name in _REQUIRED_DIRS:
        exists = (root / dir_name).is_dir()
        directories[dir_name] = exists
        if not exists:
            logger.warning("Missing directory: %s", dir_name)
            all_ok = False

    return {
        "status": "PASS" if all_ok else "FAIL",
        "project_root": str(root),
        "directories": directories,
    }


def check_configuration_files() -> dict[str, Any]:
    """Verify config files exist and contain valid YAML.

    Returns:
        Dict with ``status`` and per-file readability/validity flags.
    """
    try:
        root = _find_project_root()
    except FileNotFoundError:
        return {
            "status": "FAIL",
            "configs": {},
        }

    import yaml

    config_dir = root / CONFIG_DIR_NAME
    configs: dict[str, dict[str, Any]] = {}
    all_ok = True

    for filename in _REQUIRED_CONFIGS:
        filepath = config_dir / filename
        entry: dict[str, Any] = {"exists": False, "valid_yaml": False}

        if not filepath.is_file():
            logger.warning("Missing config: %s", filename)
            all_ok = False
            configs[filename] = entry
            continue

        entry["exists"] = True

        try:
            with open(filepath, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            entry["valid_yaml"] = True
            entry["keys"] = list(data.keys()) if isinstance(data, dict) else []
            logger.debug("Config %s: valid (%d keys)", filename, len(entry["keys"]))
        except yaml.YAMLError as exc:
            logger.error("Invalid YAML in %s: %s", filename, exc)
            entry["error"] = str(exc)
            all_ok = False

        configs[filename] = entry

    return {
        "status": "PASS" if all_ok else "FAIL",
        "configs": configs,
    }


def check_disk_space() -> dict[str, Any]:
    """Report available disk space for the project directory.

    Returns:
        Dict with ``status``, ``total_gb``, ``free_gb``, and
        ``used_percent``.
    """
    try:
        root = _find_project_root()
    except FileNotFoundError:
        root = Path.cwd()

    try:
        usage = shutil.disk_usage(str(root))
        total_gb = round(usage.total / (1024 ** 3), 2)
        free_gb = round(usage.free / (1024 ** 3), 2)
        used_pct = round((usage.used / usage.total) * 100, 1)

        result = {
            "status": "PASS",
            "total_gb": total_gb,
            "free_gb": free_gb,
            "used_percent": used_pct,
            "path": str(root),
        }
        logger.info("Disk space: %.1f GB free / %.1f GB total", free_gb, total_gb)
        return result

    except OSError as exc:
        logger.warning("Could not determine disk space: %s", exc)
        return {
            "status": "FAIL",
            "error": str(exc),
        }


# ── aggregated report ──────────────────────────────────────

def generate_environment_report() -> dict[str, Any]:
    """Build a flat environment-info section for the report.

    Returns:
        Dict with platform, Python, and working-directory details.
    """
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "working_directory": str(Path.cwd()),
    }


def validate_environment() -> dict[str, Any]:
    """Run all pre-flight checks and return a structured report.

    The report is a JSON-serialisable dictionary with sections for
    each check, plus an ``overall_status`` that is ``"PASS"`` only
    when every individual check passes.

    Returns:
        Full validation report dictionary.
    """
    logger.info("Starting environment validation")

    python = check_python_version()
    packages = check_required_packages()
    directories = check_directory_structure()
    configs = check_configuration_files()
    disk = check_disk_space()
    env_info = generate_environment_report()

    checks = {
        "python": python,
        "packages": packages,
        "directories": directories,
        "configuration": configs,
        "disk": disk,
    }

    failures = [name for name, result in checks.items() if result["status"] != "PASS"]

    report: dict[str, Any] = {
        "environment": env_info,
        **checks,
        "overall_status": "PASS" if not failures else "FAIL",
        "failed_checks": failures,
    }

    if failures:
        logger.warning(
            "Environment validation FAILED — %d check(s): %s",
            len(failures),
            ", ".join(failures),
        )
    else:
        logger.info("Environment validation PASSED — all checks OK")

    return report
