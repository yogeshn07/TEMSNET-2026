"""Dataset acquisition and integrity verification for UNSW-NB15.

This module never downloads data automatically. UNSW-NB15 is
distributed through UNSW's official research data portal, which
requires manual navigation and offers no stable direct-download URL
suitable for scripted fetching. Automatically pulling from unofficial
mirrors would compromise dataset provenance for an IEEE submission.

Instead, this module verifies that files placed manually into
``data/raw/`` match the expected UNSW-NB15 filenames, then records
size, modification time, and a cryptographic hash for each — so every
future experiment can be traced back to a known-good dataset state.

Usage::

    from src.data.dataset_acquisition import run_dataset_acquisition

    inventory = run_dataset_acquisition()
    if inventory["verification_status"] != "PASS":
        ...  # handle missing files

Design decisions
~~~~~~~~~~~~~~~~
* Expected filenames and the official source URL live in
  ``configs/dataset.yaml`` — never hardcoded in Python — so a dataset
  version change requires no code edit.
* :func:`verify_dataset_ready` performs existence checks only (no
  hashing) so downstream pipeline stages can cheaply gate execution
  without re-hashing large CSV files on every run.
* Hashing reads files in fixed-size chunks to avoid loading large CSVs
  fully into memory.
"""

from __future__ import annotations

import hashlib
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_HASH_CHUNK_SIZE = 65536


# ── configuration ───────────────────────────────────────────

def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml``.

    Returns:
        Parsed dataset configuration dictionary.

    Raises:
        FileNotFoundError: If ``configs/dataset.yaml`` is missing.
    """
    config_path = get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME
    return read_yaml(config_path)


# ── hashing ─────────────────────────────────────────────────

def compute_file_hash(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute a hex digest of *filepath* using chunked reads.

    Args:
        filepath: File to hash.
        algorithm: Name passed to :func:`hashlib.new`.

    Returns:
        Hex digest string.

    Raises:
        FileNotFoundError: If *filepath* does not exist.
        ValueError: If *algorithm* is unsupported.
    """
    if not filepath.is_file():
        raise FileNotFoundError(f"Cannot hash missing file: {filepath}")

    try:
        hasher = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}") from exc

    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(_HASH_CHUNK_SIZE), b""):
            hasher.update(chunk)

    digest = hasher.hexdigest()
    logger.debug("Computed %s hash for %s: %s...", algorithm, filepath.name, digest[:12])
    return digest


# ── location and validation ─────────────────────────────────

def locate_dataset(
    raw_dir: Path,
    expected_files: list[dict[str, str]],
) -> dict[str, Path | None]:
    """Search *raw_dir* for each expected UNSW-NB15 file.

    Args:
        raw_dir: Directory expected to contain the raw dataset.
        expected_files: List of ``{"filename": ..., "description": ...}``.

    Returns:
        Mapping of filename to its resolved ``Path``, or *None* if
        the file is missing.
    """
    located: dict[str, Path | None] = {}
    for entry in expected_files:
        filename = entry["filename"]
        candidate = raw_dir / filename
        if candidate.is_file():
            located[filename] = candidate
            logger.info("Located dataset file: %s", filename)
        else:
            located[filename] = None
            logger.warning("Missing dataset file: %s (expected in %s)", filename, raw_dir)
    return located


def validate_dataset_files(
    raw_dir: Path,
    expected_files: list[dict[str, str]],
) -> dict[str, Any]:
    """Validate that every expected dataset file exists.

    Args:
        raw_dir: Directory expected to contain the raw dataset.
        expected_files: List of expected file descriptors.

    Returns:
        Dict with ``located`` (filename -> Path|None), ``missing``
        (list of filenames), and ``all_present`` (bool).
    """
    located = locate_dataset(raw_dir, expected_files)
    missing = [name for name, path in located.items() if path is None]
    return {
        "located": located,
        "missing": missing,
        "all_present": not missing,
    }


def verify_dataset_ready() -> bool:
    """Cheap existence-only gate-check for downstream pipeline stages.

    Performs no hashing — intended to be called at the start of later
    scripts (preprocessing, training) to confirm the dataset is
    present before proceeding.

    Returns:
        *True* if every expected file exists in ``data/raw/``.
    """
    dataset_cfg = _load_dataset_config()
    raw_dir = get_path_manager().raw_data_dir
    result = validate_dataset_files(raw_dir, dataset_cfg.get("expected_files", []))

    if not result["all_present"]:
        logger.error("Dataset not ready — missing files: %s", ", ".join(result["missing"]))
    return result["all_present"]


# ── inventory ───────────────────────────────────────────────

def build_file_record(filepath: Path, algorithm: str = "sha256") -> dict[str, Any]:
    """Build an integrity record for a single dataset file.

    Args:
        filepath: File to record.
        algorithm: Hash algorithm to use.

    Returns:
        Dict with ``filename``, ``size_bytes``, ``modified_utc``,
        ``hash_algorithm``, and ``hash``.
    """
    stat = filepath.stat()
    modified_utc = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    return {
        "filename": filepath.name,
        "size_bytes": stat.st_size,
        "modified_utc": modified_utc,
        "hash_algorithm": algorithm,
        "hash": compute_file_hash(filepath, algorithm),
    }


def generate_dataset_inventory() -> dict[str, Any]:
    """Build the full dataset inventory report.

    Locates expected UNSW-NB15 files, computes integrity records for
    every file present, and reports overall verification status.

    Returns:
        Structured, JSON-serialisable inventory dictionary.
    """
    logger.info("Starting dataset acquisition and integrity verification")

    dataset_cfg = _load_dataset_config()
    raw_dir = get_path_manager().raw_data_dir
    algorithm = dataset_cfg.get("hash_algorithm", "sha256")
    expected_files = dataset_cfg.get("expected_files", [])

    validation = validate_dataset_files(raw_dir, expected_files)
    file_records = [
        build_file_record(path, algorithm)
        for path in validation["located"].values()
        if path is not None
    ]

    status = "PASS" if validation["all_present"] else "FAIL"

    inventory: dict[str, Any] = {
        "dataset_name": dataset_cfg.get("dataset_name", "unknown"),
        "dataset_version": dataset_cfg.get("dataset_version", "unknown"),
        "source": dataset_cfg.get("source", "unknown"),
        "source_type": dataset_cfg.get("source_type", "unknown"),
        "raw_data_dir": str(raw_dir),
        "hash_algorithm": algorithm,
        "expected_file_count": len(expected_files),
        "found_file_count": len(file_records),
        "missing_files": validation["missing"],
        "files": file_records,
        "verification_status": status,
        "verification_date_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
        "platform": platform.platform(),
    }

    if status == "PASS":
        logger.info("Dataset verification PASSED — %d file(s) verified", len(file_records))
    else:
        logger.error(
            "Dataset verification FAILED — missing: %s",
            ", ".join(validation["missing"]),
        )

    return inventory


# ── report rendering ────────────────────────────────────────

def _render_inventory_markdown(inventory: dict[str, Any]) -> str:
    """Render the inventory dict as a Markdown report.

    Args:
        inventory: Inventory dictionary from
            :func:`generate_dataset_inventory`.

    Returns:
        Markdown document as a string.
    """
    lines: list[str] = [
        f"# {inventory['dataset_name']} Dataset Inventory Report",
        "",
        f"**Generated:** {inventory['verification_date_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {inventory['project_version']}",
        "",
        "---",
        "",
        "## 1. Dataset Summary",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Dataset Name | {inventory['dataset_name']} |",
        f"| Source | {inventory['source']} |",
        f"| Source Type | {inventory['source_type']} |",
        f"| Version | {inventory['dataset_version']} |",
        f"| Raw Data Directory | {inventory['raw_data_dir']} |",
        f"| Expected Files | {inventory['expected_file_count']} |",
        f"| Found Files | {inventory['found_file_count']} |",
        f"| Hash Algorithm | {inventory['hash_algorithm']} |",
        f"| Verification Status | {inventory['verification_status']} |",
        "",
        "---",
        "",
        "## 2. File Inventory",
        "",
    ]

    if inventory["files"]:
        lines += [
            "| Filename | Size (bytes) | Modified (UTC) | Hash |",
            "|---|---|---|---|",
        ]
        for record in inventory["files"]:
            lines.append(
                f"| {record['filename']} | {record['size_bytes']:,} | "
                f"{record['modified_utc']} | `{record['hash']}` |"
            )
    else:
        lines.append("*No files found in raw data directory.*")

    lines += ["", "---", "", "## 3. Missing Files", ""]

    if inventory["missing_files"]:
        lines.extend(f"- {name}" for name in inventory["missing_files"])
    else:
        lines.append("*None — all expected files present.*")

    lines += [
        "",
        "---",
        "",
        "## 4. Verification",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Status | {inventory['verification_status']} |",
        f"| Verified On | {inventory['verification_date_utc']} |",
        f"| Platform | {inventory['platform']} |",
        "",
        "---",
        "*End of Dataset Inventory Report*",
    ]

    return "\n".join(lines) + "\n"


def save_inventory_json(inventory: dict[str, Any]) -> Path:
    """Save the inventory dict to ``outputs/reports/dataset_inventory.json``.

    Args:
        inventory: Inventory dictionary to serialise.

    Returns:
        Resolved path of the written JSON file.
    """
    target = get_path_manager().reports_dir / "dataset_inventory.json"
    return write_json(target, inventory)


def save_inventory_markdown(inventory: dict[str, Any]) -> Path:
    """Save the inventory dict to ``outputs/reports/dataset_inventory.md``.

    Args:
        inventory: Inventory dictionary to render and save.

    Returns:
        Resolved path of the written Markdown file.
    """
    target = get_path_manager().reports_dir / "dataset_inventory.md"
    content = _render_inventory_markdown(inventory)
    return write_text(target, content)


# ── orchestration ───────────────────────────────────────────

def run_dataset_acquisition() -> dict[str, Any]:
    """Run the full acquisition pipeline: locate, hash, save reports.

    Returns:
        The generated inventory dictionary.
    """
    inventory = generate_dataset_inventory()
    save_inventory_json(inventory)
    save_inventory_markdown(inventory)
    logger.info("Dataset inventory reports saved to outputs/reports/")
    return inventory
