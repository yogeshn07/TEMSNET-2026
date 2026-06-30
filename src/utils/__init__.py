"""General-purpose utilities.

Public API
~~~~~~~~~~
- :func:`ensure_dir` — create directory with parents.
- :func:`file_exists` — check if a file exists.
- :func:`validate_file_exists` — assert file exists or raise.
- :func:`read_text` / :func:`write_text` — text file I/O.
- :func:`read_yaml` / :func:`write_yaml` — YAML file I/O.
- :func:`read_json` / :func:`write_json` — JSON file I/O.
- :func:`copy_file` / :func:`move_file` — safe file operations.
- :func:`timestamp_str` / :func:`timestamped_path` — filename timestamps.
"""

from src.utils.file_utils import (
    copy_file,
    ensure_dir,
    file_exists,
    move_file,
    read_json,
    read_text,
    read_yaml,
    timestamp_str,
    timestamped_path,
    validate_file_exists,
    write_json,
    write_text,
    write_yaml,
)

__all__ = [
    "copy_file",
    "ensure_dir",
    "file_exists",
    "move_file",
    "read_json",
    "read_text",
    "read_yaml",
    "timestamp_str",
    "timestamped_path",
    "validate_file_exists",
    "write_json",
    "write_text",
    "write_yaml",
]
