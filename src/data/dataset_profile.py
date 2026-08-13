"""Descriptive profiling for the UNSW-NB15 training and testing datasets.

This module is read-only and purely descriptive: it loads each CSV
exactly as distributed, computes structural and statistical summaries,
and writes reports. It never cleans, encodes, scales, balances, or
merges the data — those belong to the preprocessing stage.

Training and testing sets are always profiled independently; their
class distributions, schemas, and quality metrics are never combined,
since combining them would hide differences (e.g. minority classes
that are rarer in the test split) that matter for the research design.

Usage::

    from src.data.dataset_profile import run_dataset_profiling

    result = run_dataset_profiling()

Design decisions
~~~~~~~~~~~~~~~~
* The target column (``attack_cat``), and the near-constant detection
  threshold live in ``configs/dataset.yaml`` — never hardcoded —
  consistent with the project's configuration-driven design rule.
* All pandas/NumPy scalar types are converted to native Python types
  before being placed in report dicts, because ``numpy.int64`` /
  ``numpy.float64`` are not JSON-serialisable by the stdlib ``json``
  module.
* Functions accept a loaded ``DataFrame`` rather than a filepath
  wherever possible, so each profiling step is independently testable
  without re-reading the CSV from disk.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import get_path_manager
from src.config.constants import DEFAULT_ENCODING, VERSION
from src.core.logging_config import get_logger
from src.utils.file_utils import validate_file_exists, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"


# ── configuration ───────────────────────────────────────────

def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml``.

    Returns:
        Parsed dataset configuration dictionary.
    """
    from src.utils.file_utils import read_yaml

    config_path = get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME
    return read_yaml(config_path)


# ── loading ─────────────────────────────────────────────────

def load_dataset(filepath: Path, encoding: str = DEFAULT_ENCODING) -> pd.DataFrame:
    """Load a UNSW-NB15 CSV exactly as distributed, with no transforms.

    Args:
        filepath: Path to the CSV file.
        encoding: Character encoding to use.

    Returns:
        Loaded ``DataFrame``.

    Raises:
        FileNotFoundError: If *filepath* does not exist.
    """
    validate_file_exists(filepath, label="Dataset file")
    logger.info("Loading dataset: %s", filepath.name)
    df = pd.read_csv(filepath, encoding=encoding)
    logger.info("Loaded %s: %d rows x %d columns", filepath.name, len(df), len(df.columns))
    return df


# ── 1. basic info ───────────────────────────────────────────

def profile_basic_info(
    df: pd.DataFrame,
    dataset_name: str,
    filepath: Path,
    encoding: str = DEFAULT_ENCODING,
) -> dict[str, Any]:
    """Summarise basic dataset metadata.

    Args:
        df: Loaded dataset.
        dataset_name: Human-readable label (e.g. ``"training"``).
        filepath: Source CSV path.
        encoding: Encoding used to load the file.

    Returns:
        Dict with name, path, size, shape, memory usage, encoding.
    """
    return {
        "dataset_name": dataset_name,
        "file_path": str(filepath),
        "file_size_bytes": filepath.stat().st_size,
        "num_rows": int(len(df)),
        "num_columns": int(len(df.columns)),
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        "encoding": encoding,
    }


# ── 2. schema analysis ──────────────────────────────────────

def profile_schema(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Build a per-column schema table.

    Args:
        df: Loaded dataset.

    Returns:
        List of dicts with column name, dtype, missing count/pct,
        and unique value count.
    """
    n_rows = len(df)
    schema: list[dict[str, Any]] = []

    for col in df.columns:
        missing = int(df[col].isna().sum())
        schema.append({
            "column": col,
            "dtype": str(df[col].dtype),
            "missing_count": missing,
            "missing_pct": round(100 * missing / n_rows, 4) if n_rows else 0.0,
            "unique_count": int(df[col].nunique(dropna=True)),
        })

    return schema


# ── 3. target variable analysis ─────────────────────────────

def profile_target_variable(df: pd.DataFrame, target_column: str) -> dict[str, Any]:
    """Profile the class distribution of the target column.

    Args:
        df: Loaded dataset.
        target_column: Name of the target column (e.g. ``"attack_cat"``).

    Returns:
        Dict with target column name, class count, and a per-class
        distribution table sorted by descending count.

    Raises:
        KeyError: If *target_column* is not present in *df*.
    """
    if target_column not in df.columns:
        raise KeyError(f"Target column '{target_column}' not found in dataset")

    counts = df[target_column].value_counts(dropna=False).sort_values(ascending=False)
    total = len(df)

    distribution = [
        {
            "class_name": str(class_name),
            "count": int(count),
            "pct": round(100 * count / total, 4) if total else 0.0,
        }
        for class_name, count in counts.items()
    ]

    return {
        "target_column": target_column,
        "num_classes": int(len(counts)),
        "class_names": [d["class_name"] for d in distribution],
        "distribution": distribution,
    }


# ── 4. feature categorization ───────────────────────────────

def categorize_features(df: pd.DataFrame) -> dict[str, list[str]]:
    """Categorise every column by data type.

    Binary integer columns (values subset of ``{0, 1}``) are
    classified as boolean rather than integer, since UNSW-NB15 encodes
    flags (e.g. ``is_ftp_login``) as 0/1 integers rather than a native
    boolean dtype.

    Args:
        df: Loaded dataset.

    Returns:
        Dict with keys ``numerical``, ``integer``, ``floating_point``,
        ``categorical``, ``boolean`` — each a list of column names.
    """
    numerical: list[str] = []
    integer: list[str] = []
    floating_point: list[str] = []
    categorical: list[str] = []
    boolean: list[str] = []

    for col in df.columns:
        dtype = df[col].dtype

        if pd.api.types.is_bool_dtype(dtype):
            boolean.append(col)
        elif pd.api.types.is_integer_dtype(dtype):
            unique_vals = set(df[col].dropna().unique().tolist())
            if unique_vals.issubset({0, 1}):
                boolean.append(col)
            else:
                integer.append(col)
                numerical.append(col)
        elif pd.api.types.is_float_dtype(dtype):
            floating_point.append(col)
            numerical.append(col)
        else:
            categorical.append(col)

    return {
        "numerical": numerical,
        "integer": integer,
        "floating_point": floating_point,
        "categorical": categorical,
        "boolean": boolean,
    }


# ── 5. missing data analysis ────────────────────────────────

def profile_missing_data(df: pd.DataFrame) -> dict[str, Any]:
    """Summarise missing values across the dataset.

    Args:
        df: Loaded dataset.

    Returns:
        Dict with total missing count and a per-column breakdown.
    """
    n_rows = len(df)
    per_column = [
        {
            "column": col,
            "missing_count": int(df[col].isna().sum()),
            "missing_pct": round(100 * df[col].isna().sum() / n_rows, 4) if n_rows else 0.0,
        }
        for col in df.columns
    ]
    total_missing = sum(c["missing_count"] for c in per_column)

    return {
        "total_missing": int(total_missing),
        "per_column": per_column,
    }


# ── 6. duplicate analysis ───────────────────────────────────

def profile_duplicates(df: pd.DataFrame) -> dict[str, Any]:
    """Count fully duplicated rows.

    Args:
        df: Loaded dataset.

    Returns:
        Dict with duplicate row count and percentage of total rows.
    """
    n_rows = len(df)
    duplicate_count = int(df.duplicated(keep="first").sum())
    return {
        "total_rows": int(n_rows),
        "duplicate_count": duplicate_count,
        "duplicate_pct": round(100 * duplicate_count / n_rows, 4) if n_rows else 0.0,
    }


# ── 7. constant & near-constant features ────────────────────

def detect_constant_features(
    df: pd.DataFrame,
    near_constant_threshold: float = 0.99,
) -> dict[str, Any]:
    """Detect constant and near-constant columns.

    A column is *constant* if it has exactly one unique value. A
    column is *near-constant* if its single most frequent value
    accounts for at least *near_constant_threshold* of all rows
    (and it is not already constant).

    Args:
        df: Loaded dataset.
        near_constant_threshold: Fraction (0-1) above which a
            dominant value flags a column as near-constant.

    Returns:
        Dict with ``constant_columns`` and ``near_constant_columns``,
        each a list of ``{"column": ..., "dominant_value": ...,
        "dominant_pct": ...}`` dicts.
    """
    n_rows = len(df)
    constant: list[dict[str, Any]] = []
    near_constant: list[dict[str, Any]] = []

    for col in df.columns:
        value_counts = df[col].value_counts(dropna=False)
        if value_counts.empty:
            continue

        dominant_value = value_counts.index[0]
        dominant_pct = value_counts.iloc[0] / n_rows if n_rows else 0.0

        entry = {
            "column": col,
            "dominant_value": str(dominant_value),
            "dominant_pct": round(100 * dominant_pct, 4),
        }

        if df[col].nunique(dropna=False) == 1:
            constant.append(entry)
        elif dominant_pct >= near_constant_threshold:
            near_constant.append(entry)

    return {
        "constant_columns": constant,
        "near_constant_columns": near_constant,
    }


# ── 8. basic numeric summary ────────────────────────────────

def profile_numeric_summary(df: pd.DataFrame, numeric_columns: list[str]) -> list[dict[str, Any]]:
    """Compute descriptive statistics for numeric columns.

    Args:
        df: Loaded dataset.
        numeric_columns: Columns to summarise (typically the union of
            integer and floating-point columns from
            :func:`categorize_features`).

    Returns:
        List of dicts with mean, median, std, min, max, and quartiles
        per column.
    """
    summary: list[dict[str, Any]] = []
    for col in numeric_columns:
        series = df[col]
        summary.append({
            "column": col,
            "mean": round(float(series.mean()), 6),
            "median": round(float(series.median()), 6),
            "std": round(float(series.std()), 6),
            "min": round(float(series.min()), 6),
            "q25": round(float(series.quantile(0.25)), 6),
            "q50": round(float(series.quantile(0.50)), 6),
            "q75": round(float(series.quantile(0.75)), 6),
            "max": round(float(series.max()), 6),
        })
    return summary


# ── single-dataset orchestration ────────────────────────────

def generate_dataset_profile(
    filepath: Path,
    dataset_label: str,
    target_column: str,
    near_constant_threshold: float = 0.99,
) -> dict[str, Any]:
    """Run the full descriptive profile for one dataset file.

    Args:
        filepath: Path to the CSV file.
        dataset_label: Human-readable label (``"training"`` or
            ``"testing"``).
        target_column: Name of the target column.
        near_constant_threshold: Threshold for near-constant detection.

    Returns:
        Nested dict containing every profiling section.
    """
    logger.info("Profiling started: %s dataset", dataset_label)

    df = load_dataset(filepath)
    feature_categories = categorize_features(df)
    numeric_columns = feature_categories["numerical"]

    profile: dict[str, Any] = {
        "basic_info": profile_basic_info(df, dataset_label, filepath),
        "schema": profile_schema(df),
        "target_variable": profile_target_variable(df, target_column),
        "feature_categories": feature_categories,
        "missing_data": profile_missing_data(df),
        "duplicates": profile_duplicates(df),
        "constant_features": detect_constant_features(df, near_constant_threshold),
        "numeric_summary": profile_numeric_summary(df, numeric_columns),
        "profiled_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
        "platform": platform.platform(),
    }

    logger.info("Profiling completed: %s dataset", dataset_label)
    return profile


# ── report rendering ────────────────────────────────────────

def _render_profile_markdown(profile: dict[str, Any]) -> str:
    """Render a single dataset profile as a Markdown report.

    Args:
        profile: Profile dict from :func:`generate_dataset_profile`.

    Returns:
        Markdown document as a string.
    """
    info = profile["basic_info"]
    target = profile["target_variable"]
    cats = profile["feature_categories"]
    missing = profile["missing_data"]
    dupes = profile["duplicates"]
    constants = profile["constant_features"]

    lines: list[str] = [
        f"# UNSW-NB15 {info['dataset_name'].title()} Dataset Profile",
        "",
        f"**Generated:** {profile['profiled_at_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {profile['project_version']}",
        "",
        "---",
        "",
        "## 1. Basic Dataset Information",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Dataset Name | {info['dataset_name']} |",
        f"| File Path | {info['file_path']} |",
        f"| File Size (bytes) | {info['file_size_bytes']:,} |",
        f"| Rows | {info['num_rows']:,} |",
        f"| Columns | {info['num_columns']} |",
        f"| Memory Usage (bytes) | {info['memory_usage_bytes']:,} |",
        f"| Encoding | {info['encoding']} |",
        "",
        "---",
        "",
        "## 2. Schema Analysis",
        "",
        "| Column | Dtype | Missing | Missing % | Unique |",
        "|---|---|---|---|---|",
    ]
    for col in profile["schema"]:
        lines.append(
            f"| {col['column']} | {col['dtype']} | {col['missing_count']} | "
            f"{col['missing_pct']}% | {col['unique_count']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 3. Target Variable Analysis",
        "",
        f"**Target column:** `{target['target_column']}`  ",
        f"**Number of classes:** {target['num_classes']}",
        "",
        "| Class | Count | % of Total |",
        "|---|---|---|",
    ]
    for row in target["distribution"]:
        lines.append(f"| {row['class_name']} | {row['count']:,} | {row['pct']}% |")

    lines += [
        "",
        "---",
        "",
        "## 4. Feature Categorization",
        "",
        "| Category | Count | Columns |",
        "|---|---|---|",
        f"| Numerical | {len(cats['numerical'])} | {', '.join(cats['numerical']) or '—'} |",
        f"| Integer | {len(cats['integer'])} | {', '.join(cats['integer']) or '—'} |",
        f"| Floating-point | {len(cats['floating_point'])} | {', '.join(cats['floating_point']) or '—'} |",
        f"| Categorical | {len(cats['categorical'])} | {', '.join(cats['categorical']) or '—'} |",
        f"| Boolean | {len(cats['boolean'])} | {', '.join(cats['boolean']) or '—'} |",
        "",
        "---",
        "",
        "## 5. Missing Data Analysis",
        "",
        f"**Total missing values:** {missing['total_missing']:,}",
        "",
    ]

    cols_with_missing = [c for c in missing["per_column"] if c["missing_count"] > 0]
    if cols_with_missing:
        lines += ["| Column | Missing Count | Missing % |", "|---|---|---|"]
        for c in cols_with_missing:
            lines.append(f"| {c['column']} | {c['missing_count']} | {c['missing_pct']}% |")
    else:
        lines.append("*No missing values detected in any column.*")

    lines += [
        "",
        "---",
        "",
        "## 6. Duplicate Analysis",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Total Rows | {dupes['total_rows']:,} |",
        f"| Duplicate Rows | {dupes['duplicate_count']:,} |",
        f"| Duplicate % | {dupes['duplicate_pct']}% |",
        "",
        "---",
        "",
        "## 7. Constant & Near-Constant Features",
        "",
        "### Constant Columns",
        "",
    ]

    if constants["constant_columns"]:
        lines += ["| Column | Value | % |", "|---|---|---|"]
        for c in constants["constant_columns"]:
            lines.append(f"| {c['column']} | {c['dominant_value']} | {c['dominant_pct']}% |")
    else:
        lines.append("*None detected.*")

    lines += ["", "### Near-Constant Columns", ""]
    if constants["near_constant_columns"]:
        lines += ["| Column | Dominant Value | % |", "|---|---|---|"]
        for c in constants["near_constant_columns"]:
            lines.append(f"| {c['column']} | {c['dominant_value']} | {c['dominant_pct']}% |")
    else:
        lines.append("*None detected.*")

    lines += [
        "",
        "---",
        "",
        "## 8. Basic Numeric Summary",
        "",
        "| Column | Mean | Median | Std | Min | Q25 | Q50 | Q75 | Max |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for n in profile["numeric_summary"]:
        lines.append(
            f"| {n['column']} | {n['mean']} | {n['median']} | {n['std']} | "
            f"{n['min']} | {n['q25']} | {n['q50']} | {n['q75']} | {n['max']} |"
        )

    lines += ["", "---", "*End of Dataset Profile Report*"]
    return "\n".join(lines) + "\n"


def save_profile_json(profile: dict[str, Any], dataset_label: str) -> Path:
    """Save a profile dict as JSON.

    Args:
        profile: Profile dict from :func:`generate_dataset_profile`.
        dataset_label: ``"training"`` or ``"testing"``.

    Returns:
        Resolved path of the written JSON file.
    """
    target = get_path_manager().reports_dir / f"{dataset_label}_dataset_profile.json"
    return write_json(target, profile)


def save_profile_markdown(profile: dict[str, Any], dataset_label: str) -> Path:
    """Save a profile dict as a Markdown report.

    Args:
        profile: Profile dict from :func:`generate_dataset_profile`.
        dataset_label: ``"training"`` or ``"testing"``.

    Returns:
        Resolved path of the written Markdown file.
    """
    target = get_path_manager().reports_dir / f"{dataset_label}_dataset_profile.md"
    return write_text(target, _render_profile_markdown(profile))


def save_profile_tables(profile: dict[str, Any], dataset_label: str) -> dict[str, Path]:
    """Save CSV tables for schema, class distribution, feature
    summary, missing values, and duplicate summary.

    Args:
        profile: Profile dict from :func:`generate_dataset_profile`.
        dataset_label: ``"training"`` or ``"testing"``.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    schema_df = pd.DataFrame(profile["schema"])
    path = tables_dir / f"{dataset_label}_schema.csv"
    schema_df.to_csv(path, index=False)
    paths["schema"] = path

    class_dist_df = pd.DataFrame(profile["target_variable"]["distribution"])
    path = tables_dir / f"{dataset_label}_class_distribution.csv"
    class_dist_df.to_csv(path, index=False)
    paths["class_distribution"] = path

    cats = profile["feature_categories"]
    feature_rows = [
        {"column": col, "category": category}
        for category, cols in cats.items()
        for col in cols
    ]
    feature_df = pd.DataFrame(feature_rows)
    path = tables_dir / f"{dataset_label}_feature_summary.csv"
    feature_df.to_csv(path, index=False)
    paths["feature_summary"] = path

    missing_df = pd.DataFrame(profile["missing_data"]["per_column"])
    path = tables_dir / f"{dataset_label}_missing_values.csv"
    missing_df.to_csv(path, index=False)
    paths["missing_values"] = path

    dupes = profile["duplicates"]
    dupe_df = pd.DataFrame([
        {"metric": "total_rows", "value": dupes["total_rows"]},
        {"metric": "duplicate_count", "value": dupes["duplicate_count"]},
        {"metric": "duplicate_pct", "value": dupes["duplicate_pct"]},
    ])
    path = tables_dir / f"{dataset_label}_duplicate_summary.csv"
    dupe_df.to_csv(path, index=False)
    paths["duplicate_summary"] = path

    logger.info("Saved %d CSV tables for %s dataset", len(paths), dataset_label)
    return paths


# ── final methodology-ready summary ─────────────────────────

def generate_profile_summary(
    train_profile: dict[str, Any],
    test_profile: dict[str, Any],
) -> dict[str, Any]:
    """Build a concise cross-dataset summary for the paper's Methodology section.

    Args:
        train_profile: Profile dict for the training dataset.
        test_profile: Profile dict for the testing dataset.

    Returns:
        Flat summary dict with total samples, features, target info,
        and missing/duplicate counts for both splits.
    """
    return {
        "total_training_samples": train_profile["basic_info"]["num_rows"],
        "total_testing_samples": test_profile["basic_info"]["num_rows"],
        "total_features": train_profile["basic_info"]["num_columns"],
        "target_variable": train_profile["target_variable"]["target_column"],
        "num_attack_classes": train_profile["target_variable"]["num_classes"],
        "attack_class_names": train_profile["target_variable"]["class_names"],
        "training_missing_values": train_profile["missing_data"]["total_missing"],
        "testing_missing_values": test_profile["missing_data"]["total_missing"],
        "training_duplicate_rows": train_profile["duplicates"]["duplicate_count"],
        "testing_duplicate_rows": test_profile["duplicates"]["duplicate_count"],
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }


def _render_summary_markdown(summary: dict[str, Any]) -> str:
    """Render the cross-dataset summary as Markdown.

    Args:
        summary: Summary dict from :func:`generate_profile_summary`.

    Returns:
        Markdown document as a string.
    """
    lines = [
        "# Dataset Profile Summary",
        "",
        "*Suitable for inclusion in the Methodology section.*",
        "",
        f"**Generated:** {summary['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {summary['project_version']}",
        "",
        "---",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Total Training Samples | {summary['total_training_samples']:,} |",
        f"| Total Testing Samples | {summary['total_testing_samples']:,} |",
        f"| Total Features | {summary['total_features']} |",
        f"| Target Variable | `{summary['target_variable']}` |",
        f"| Number of Attack Classes | {summary['num_attack_classes']} |",
        f"| Attack Class Names | {', '.join(summary['attack_class_names'])} |",
        f"| Training Missing Values | {summary['training_missing_values']:,} |",
        f"| Testing Missing Values | {summary['testing_missing_values']:,} |",
        f"| Training Duplicate Rows | {summary['training_duplicate_rows']:,} |",
        f"| Testing Duplicate Rows | {summary['testing_duplicate_rows']:,} |",
        "",
        "---",
        "*End of Dataset Profile Summary*",
    ]
    return "\n".join(lines) + "\n"


def save_profile_summary(summary: dict[str, Any]) -> tuple[Path, Path]:
    """Save the cross-dataset summary as JSON and Markdown.

    Args:
        summary: Summary dict from :func:`generate_profile_summary`.

    Returns:
        Tuple of (json_path, markdown_path).
    """
    reports_dir = get_path_manager().reports_dir
    json_path = write_json(reports_dir / "dataset_profile_summary.json", summary)
    md_path = write_text(reports_dir / "dataset_profile_summary.md", _render_summary_markdown(summary))
    return json_path, md_path


# ── multi-dataset orchestration ─────────────────────────────

def run_dataset_profiling() -> dict[str, Any]:
    """Profile both the training and testing UNSW-NB15 splits.

    Loads expected filenames and profiling settings from
    ``configs/dataset.yaml``, profiles each split independently,
    saves JSON/Markdown reports and CSV tables for each, and writes
    a concise cross-dataset summary.

    Returns:
        Dict with ``training``, ``testing``, and ``summary`` keys.
    """
    dataset_cfg = _load_dataset_config()
    raw_dir = get_path_manager().raw_data_dir
    target_column = dataset_cfg.get("target_column", "attack_cat")
    threshold = dataset_cfg.get("near_constant_threshold", 0.99)

    files_by_split = {
        entry["split"]: entry["filename"]
        for entry in dataset_cfg.get("expected_files", [])
    }

    profiles: dict[str, dict[str, Any]] = {}
    for split_label in ("training", "testing"):
        filepath = raw_dir / files_by_split[split_label]
        profile = generate_dataset_profile(filepath, split_label, target_column, threshold)
        save_profile_json(profile, split_label)
        save_profile_markdown(profile, split_label)
        save_profile_tables(profile, split_label)
        profiles[split_label] = profile

    summary = generate_profile_summary(profiles["training"], profiles["testing"])
    save_profile_summary(summary)

    logger.info(
        "Dataset profiling complete — %d training / %d testing samples, %d classes",
        summary["total_training_samples"],
        summary["total_testing_samples"],
        summary["num_attack_classes"],
    )

    return {
        "training": profiles["training"],
        "testing": profiles["testing"],
        "summary": summary,
    }
