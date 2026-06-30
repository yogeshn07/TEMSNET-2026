"""Reusable filesystem utilities.

Pure functions for reading, writing, copying, moving, and validating
files.  Every function uses :mod:`pathlib`, logs its operations via
the project logging framework, and raises clear exceptions on failure.

No domain logic lives here — only generic filesystem plumbing that
any module in the project can import.

Usage::

    from src.utils.file_utils import write_text, read_yaml, ensure_dir

Design decisions
~~~~~~~~~~~~~~~~
* All path parameters accept ``str | Path`` and are resolved
  internally so callers never need to worry about types.
* Atomic writes use a temporary file + rename to avoid leaving
  half-written output on crash.  On Windows, ``os.replace`` is used
  for the rename step because ``Path.rename`` can fail if the target
  already exists.
* YAML and JSON helpers are thin wrappers that standardise encoding,
  error handling, and logging — they do not duplicate the config
  loader's logic because the config loader validates *project config*
  while these helpers handle *arbitrary* files.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.core.logging_config import get_logger

logger = get_logger(__name__)


# ── path helpers ────────────────────────────────────────────

def _to_path(p: str | Path) -> Path:
    """Coerce *p* to an absolute ``Path``.

    Args:
        p: String or Path to resolve.

    Returns:
        Resolved absolute ``Path``.
    """
    return Path(p).resolve()


# ── directory operations ────────────────────────────────────

def ensure_dir(path: str | Path) -> Path:
    """Create *path* and any missing parents.

    Args:
        path: Directory to create.

    Returns:
        The resolved ``Path``, guaranteed to exist.
    """
    resolved = _to_path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    logger.debug("Directory ensured: %s", resolved)
    return resolved


# ── validation ──────────────────────────────────────────────

def file_exists(path: str | Path) -> bool:
    """Return *True* if *path* is an existing regular file.

    Args:
        path: File path to check.

    Returns:
        ``True`` when the path exists and is a file.
    """
    return _to_path(path).is_file()


def validate_file_exists(path: str | Path, label: str = "File") -> Path:
    """Assert that *path* exists and is a file.

    Args:
        path: File path to validate.
        label: Human-readable name used in the error message.

    Returns:
        Resolved ``Path``.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    resolved = _to_path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} not found: {resolved}")
    return resolved


# ── atomic write helper ─────────────────────────────────────

def _atomic_write_bytes(target: Path, data: bytes) -> None:
    """Write *data* atomically by writing to a temp file then renaming.

    Args:
        target: Final destination path.
        data: Raw bytes to write.
    """
    fd, tmp_path = tempfile.mkstemp(
        dir=str(target.parent), suffix=".tmp"
    )
    try:
        os.write(fd, data)
        os.close(fd)
        fd = -1
        os.replace(tmp_path, str(target))
    except BaseException:
        if fd >= 0:
            with contextlib.suppress(OSError):
                os.close(fd)
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise


# ── text I/O ────────────────────────────────────────────────

def read_text(path: str | Path, encoding: str = "utf-8") -> str:
    """Read a text file and return its contents.

    Args:
        path: File to read.
        encoding: Character encoding.

    Returns:
        File contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        UnicodeDecodeError: If the file cannot be decoded.
    """
    resolved = validate_file_exists(path)
    content = resolved.read_text(encoding=encoding)
    logger.debug("Read text file: %s (%d chars)", resolved, len(content))
    return content


def write_text(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
    atomic: bool = True,
) -> Path:
    """Write *content* to a text file.

    Args:
        path: Destination file path.
        content: String to write.
        encoding: Character encoding.
        atomic: When *True*, write to a temp file first then rename.

    Returns:
        Resolved ``Path`` of the written file.
    """
    resolved = _to_path(path)
    ensure_dir(resolved.parent)

    if atomic:
        _atomic_write_bytes(resolved, content.encode(encoding))
    else:
        resolved.write_text(content, encoding=encoding)

    logger.debug("Wrote text file: %s (%d chars)", resolved, len(content))
    return resolved


# ── YAML I/O ────────────────────────────────────────────────

def read_yaml(path: str | Path) -> dict[str, Any]:
    """Read a YAML file and return its contents as a dict.

    Args:
        path: YAML file to read.

    Returns:
        Parsed YAML content.  Returns an empty dict for empty files.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the YAML is malformed.
        ValueError: If the root element is not a mapping.
    """
    resolved = validate_file_exists(path, label="YAML file")
    raw = resolved.read_text(encoding="utf-8")

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        logger.error("Malformed YAML in %s: %s", resolved.name, exc)
        raise

    if data is None:
        logger.debug("Read YAML file (empty): %s", resolved)
        return {}
    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a YAML mapping in {resolved.name}, "
            f"got {type(data).__name__}"
        )

    logger.debug("Read YAML file: %s (%d keys)", resolved, len(data))
    return data


def write_yaml(
    path: str | Path,
    data: dict[str, Any],
    atomic: bool = True,
) -> Path:
    """Serialise *data* to a YAML file.

    Args:
        path: Destination file path.
        data: Dictionary to serialise.
        atomic: When *True*, write via temp file + rename.

    Returns:
        Resolved ``Path`` of the written file.
    """
    resolved = _to_path(path)
    ensure_dir(resolved.parent)

    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False,
    )

    if atomic:
        _atomic_write_bytes(resolved, content.encode("utf-8"))
    else:
        resolved.write_text(content, encoding="utf-8")

    logger.debug("Wrote YAML file: %s (%d keys)", resolved, len(data))
    return resolved


# ── JSON I/O ────────────────────────────────────────────────

def read_json(path: str | Path) -> Any:
    """Read a JSON file and return its contents.

    Args:
        path: JSON file to read.

    Returns:
        Parsed JSON (typically a dict or list).

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the JSON is malformed.
    """
    resolved = validate_file_exists(path, label="JSON file")
    raw = resolved.read_text(encoding="utf-8")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Malformed JSON in %s: %s", resolved.name, exc)
        raise

    logger.debug("Read JSON file: %s", resolved)
    return data


def write_json(
    path: str | Path,
    data: Any,
    indent: int = 2,
    atomic: bool = True,
) -> Path:
    """Serialise *data* to a JSON file.

    Args:
        path: Destination file path.
        data: Object to serialise (must be JSON-serialisable).
        indent: Indentation level for pretty-printing.
        atomic: When *True*, write via temp file + rename.

    Returns:
        Resolved ``Path`` of the written file.
    """
    resolved = _to_path(path)
    ensure_dir(resolved.parent)

    content = json.dumps(data, indent=indent, ensure_ascii=False)

    if atomic:
        _atomic_write_bytes(resolved, content.encode("utf-8"))
    else:
        resolved.write_text(content, encoding="utf-8")

    logger.debug("Wrote JSON file: %s", resolved)
    return resolved


# ── file operations ─────────────────────────────────────────

def copy_file(src: str | Path, dst: str | Path) -> Path:
    """Copy a file from *src* to *dst*.

    Creates the destination directory if it does not exist.
    Preserves file metadata (timestamps, permissions).

    Args:
        src: Source file path.
        dst: Destination file path.

    Returns:
        Resolved ``Path`` of the copied file.

    Raises:
        FileNotFoundError: If *src* does not exist.
    """
    src_resolved = validate_file_exists(src, label="Source file")
    dst_resolved = _to_path(dst)
    ensure_dir(dst_resolved.parent)

    shutil.copy2(str(src_resolved), str(dst_resolved))
    logger.info("Copied: %s -> %s", src_resolved, dst_resolved)
    return dst_resolved


def move_file(src: str | Path, dst: str | Path) -> Path:
    """Move a file from *src* to *dst*.

    Creates the destination directory if it does not exist.

    Args:
        src: Source file path.
        dst: Destination file path.

    Returns:
        Resolved ``Path`` of the moved file.

    Raises:
        FileNotFoundError: If *src* does not exist.
    """
    src_resolved = validate_file_exists(src, label="Source file")
    dst_resolved = _to_path(dst)
    ensure_dir(dst_resolved.parent)

    shutil.move(str(src_resolved), str(dst_resolved))
    logger.info("Moved: %s -> %s", src_resolved, dst_resolved)
    return dst_resolved


# ── timestamps ──────────────────────────────────────────────

def timestamp_str(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """Return the current UTC time as a formatted string.

    Useful for generating unique, sortable filenames.

    Args:
        fmt: ``strftime`` format string.

    Returns:
        Formatted timestamp string.
    """
    return datetime.now(tz=timezone.utc).strftime(fmt)


def timestamped_path(
    directory: str | Path,
    prefix: str,
    suffix: str = ".log",
    fmt: str = "%Y%m%d_%H%M%S",
) -> Path:
    """Build a file path with an embedded UTC timestamp.

    Example::

        timestamped_path("outputs/logs", "experiment", ".log")
        # -> outputs/logs/experiment_20260629_120000.log

    Args:
        directory: Parent directory.
        prefix: Filename prefix.
        suffix: File extension (including the dot).
        fmt: ``strftime`` format for the timestamp portion.

    Returns:
        Resolved ``Path`` (directory is created if missing).
    """
    dir_resolved = ensure_dir(directory)
    name = f"{prefix}_{timestamp_str(fmt)}{suffix}"
    return dir_resolved / name
