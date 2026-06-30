"""Central path management for the project.

Resolves all directory paths relative to the project root using
``pathlib``.  Never hardcodes OS-specific separators or absolute
paths.  Paths can be overridden via ``configs/paths.yaml``; when no
override is provided, sensible defaults relative to the project root
are used.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _find_project_root(marker: str = "pyproject.toml") -> Path:
    """Walk up from this file's location to find the project root.

    Args:
        marker: Filename whose presence signals the project root.

    Returns:
        Absolute path to the project root directory.

    Raises:
        FileNotFoundError: If no ancestor directory contains *marker*.
    """
    current = Path(__file__).resolve().parent
    for parent in (current, *current.parents):
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(
        f"Cannot locate project root: no '{marker}' found in any "
        f"ancestor of {Path(__file__).resolve()}"
    )


class PathManager:
    """Centralised resolver for every directory the project uses.

    All paths are derived from the project root.  Values from
    ``configs/paths.yaml`` override the defaults when supplied.

    Args:
        path_overrides: Optional mapping from ``configs/paths.yaml``.
            Keys that match a known directory name replace the default.
        project_root: Explicit root path.  Auto-detected when *None*.
    """

    def __init__(
        self,
        path_overrides: dict[str, Any] | None = None,
        project_root: Path | None = None,
    ) -> None:
        self._root: Path = (
            project_root.resolve() if project_root else _find_project_root()
        )
        self._overrides: dict[str, Any] = path_overrides or {}

    # ── helpers ──────────────────────────────────────────────

    def _resolve(self, key: str, default_relative: str) -> Path:
        """Return an overridden path or the default under project root.

        Args:
            key: Lookup key in the overrides dict.
            default_relative: Default path relative to the project root.

        Returns:
            Resolved absolute ``Path``.
        """
        raw = self._overrides.get(key, default_relative)
        path = Path(raw)
        if not path.is_absolute():
            path = self._root / path
        return path.resolve()

    # ── root ─────────────────────────────────────────────────

    @property
    def project_root(self) -> Path:
        """Absolute path to the project root directory."""
        return self._root

    # ── configuration ────────────────────────────────────────

    @property
    def configs_dir(self) -> Path:
        """Directory containing YAML configuration files."""
        return self._resolve("configs_dir", "configs")

    # ── data directories ─────────────────────────────────────

    @property
    def raw_data_dir(self) -> Path:
        """Original, untouched dataset files."""
        return self._resolve("raw_data_dir", "data/raw")

    @property
    def interim_data_dir(self) -> Path:
        """Intermediate processed data (e.g. encoded, not yet scaled)."""
        return self._resolve("interim_data_dir", "data/interim")

    @property
    def processed_data_dir(self) -> Path:
        """Final processed data ready for model consumption."""
        return self._resolve("processed_data_dir", "data/processed")

    @property
    def external_data_dir(self) -> Path:
        """External reference data and lookup tables."""
        return self._resolve("external_data_dir", "data/external")

    # ── output directories ───────────────────────────────────

    @property
    def reports_dir(self) -> Path:
        """Generated Markdown/HTML reports."""
        return self._resolve("reports_dir", "outputs/reports")

    @property
    def figures_dir(self) -> Path:
        """Generated publication figures."""
        return self._resolve("figures_dir", "outputs/figures")

    @property
    def tables_dir(self) -> Path:
        """Generated CSV result tables."""
        return self._resolve("tables_dir", "outputs/tables")

    @property
    def models_dir(self) -> Path:
        """Trained model artefacts."""
        return self._resolve("models_dir", "outputs/models")

    @property
    def logs_dir(self) -> Path:
        """Experiment log files."""
        return self._resolve("logs_dir", "outputs/logs")

    @property
    def checkpoints_dir(self) -> Path:
        """Training checkpoints."""
        return self._resolve("checkpoints_dir", "outputs/checkpoints")

    # ── source & scripts ─────────────────────────────────────

    @property
    def src_dir(self) -> Path:
        """Source code root."""
        return self._resolve("src_dir", "src")

    @property
    def scripts_dir(self) -> Path:
        """Pipeline entry-point scripts."""
        return self._resolve("scripts_dir", "scripts")

    @property
    def tests_dir(self) -> Path:
        """Test suite directory."""
        return self._resolve("tests_dir", "tests")

    # ── utilities ────────────────────────────────────────────

    def ensure_dir(self, path: Path) -> Path:
        """Create *path* (and parents) if it does not exist.

        Args:
            path: Directory path to create.

        Returns:
            The same *path*, guaranteed to exist.
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_output_dirs(self) -> None:
        """Create all output directories if they do not already exist."""
        for prop_name in (
            "reports_dir",
            "figures_dir",
            "tables_dir",
            "models_dir",
            "logs_dir",
            "checkpoints_dir",
        ):
            self.ensure_dir(getattr(self, prop_name))

    def __repr__(self) -> str:
        return f"PathManager(root={self._root})"
