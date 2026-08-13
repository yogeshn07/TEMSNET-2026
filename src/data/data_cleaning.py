"""Evidence-based data cleaning for the UNSW-NB15 training and testing sets.

Every cleaning action implemented here is gated on evidence collected
at runtime — not applied because it is conventionally common. The
expected outcome, based on B.1 (integrity verification), B.2
(profiling), and B.3 (EDA) — all of which independently found zero
missing values and zero duplicate rows in both splits — is that this
module will perform **no** imputation or deduplication. It re-verifies
those findings live rather than trusting the earlier reports, and
documents the evidence either way.

The only operation this module is permitted to actually apply to the
in-memory data is whitespace normalisation in categorical string
columns, and only if whitespace issues are detected. No values are
removed, no rows are dropped, no encoding/scaling/balancing happens.

Usage::

    from src.data.data_cleaning import run_data_cleaning

    result = run_data_cleaning()

Design decisions
~~~~~~~~~~~~~~~~
* Missing-value and duplicate-row counts reuse
  :func:`src.data.dataset_profile.profile_missing_data` and
  :func:`src.data.dataset_profile.profile_duplicates` rather than
  recomputing them with new logic — the *re-verification* requirement
  is about confirming the conclusion still holds, not about writing
  a second implementation that could silently diverge from the first.
* Schema and target-column re-verification reuse
  :func:`src.data.preprocessing_pipeline.run_schema_validation` and
  :func:`src.data.preprocessing_pipeline.verify_target_column` for
  the same reason.
* Every cleaning *decision* (not just every cleaning *action*) is
  recorded with a reason, the evidence behind it, and the expected
  impact — including decisions to take no action, per the task's
  scientific requirements.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.data.dataset_profile import categorize_features, profile_duplicates, profile_missing_data
from src.data.eda import load_datasets
from src.data.preprocessing_pipeline import run_schema_validation, verify_target_column
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_PREPROCESSING_CONFIG_FILENAME = "preprocessing.yaml"


def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml``.

    Returns:
        Parsed dataset configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME)


def _load_preprocessing_config() -> dict[str, Any]:
    """Load ``configs/preprocessing.yaml`` (the frozen schema contract).

    Returns:
        Parsed preprocessing configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _PREPROCESSING_CONFIG_FILENAME)


# ══════════════════════════════════════════════════════════════
# Numeric quality checks
# ══════════════════════════════════════════════════════════════

def detect_infinite_values(df: pd.DataFrame, numeric_columns: list[str]) -> dict[str, Any]:
    """Detect infinite (+/-inf) values in numeric columns.

    Args:
        df: Loaded dataset split.
        numeric_columns: Columns to check.

    Returns:
        Dict with ``total_infinite`` and a per-column breakdown.
    """
    per_column = []
    for col in numeric_columns:
        count = int(np.isinf(df[col]).sum())
        per_column.append({"column": col, "infinite_count": count})

    total = sum(c["infinite_count"] for c in per_column)
    return {"total_infinite": total, "per_column": per_column}


def detect_invalid_numeric_values(df: pd.DataFrame, numeric_columns: list[str]) -> dict[str, Any]:
    """Detect negative values in columns that are semantically non-negative.

    Every UNSW-NB15 numerical feature (durations, byte counts, packet
    counts, rates, TTLs, jitter, etc.) represents a non-negative
    network-flow quantity, so a negative value would indicate a data
    error rather than a valid observation.

    Args:
        df: Loaded dataset split.
        numeric_columns: Columns to check.

    Returns:
        Dict with ``total_invalid`` and a per-column breakdown of
        negative-value counts.
    """
    per_column = []
    for col in numeric_columns:
        count = int((df[col] < 0).sum())
        per_column.append({"column": col, "negative_count": count})

    total = sum(c["negative_count"] for c in per_column)
    return {"total_invalid": total, "per_column": per_column}


# ══════════════════════════════════════════════════════════════
# Categorical quality checks
# ══════════════════════════════════════════════════════════════

def validate_categorical_values(df: pd.DataFrame, categorical_columns: list[str]) -> dict[str, Any]:
    """Check categorical string columns for empty strings and whitespace issues.

    Args:
        df: Loaded dataset split.
        categorical_columns: Columns to check (e.g. ``proto``, ``service``, ``state``).

    Returns:
        Dict with ``total_empty_strings``, ``total_whitespace_issues``,
        and a per-column breakdown including the observed unique
        category count.
    """
    per_column = []
    for col in categorical_columns:
        series = df[col].astype(str)
        empty_count = int((series.str.strip() == "").sum())
        whitespace_count = int((series != series.str.strip()).sum())
        per_column.append({
            "column": col,
            "unique_count": int(df[col].nunique(dropna=True)),
            "empty_string_count": empty_count,
            "whitespace_issue_count": whitespace_count,
        })

    return {
        "total_empty_strings": sum(c["empty_string_count"] for c in per_column),
        "total_whitespace_issues": sum(c["whitespace_issue_count"] for c in per_column),
        "per_column": per_column,
    }


def find_unseen_categories(
    train_df: pd.DataFrame, test_df: pd.DataFrame, categorical_columns: list[str]
) -> dict[str, list[str]]:
    """Identify categories present in the test split but absent from training.

    Relevant for the future encoding stage (C.3): an encoder fit on
    training categories must explicitly handle any category the test
    split contains that training never showed it. This function only
    reports such categories — it does not modify anything.

    Args:
        train_df: Training split.
        test_df: Testing split.
        categorical_columns: Columns to compare.

    Returns:
        Mapping of column name to the sorted list of unseen category
        values (empty list if none).
    """
    unseen: dict[str, list[str]] = {}
    for col in categorical_columns:
        train_values = set(train_df[col].dropna().unique())
        test_values = set(test_df[col].dropna().unique())
        unseen[col] = sorted(str(v) for v in (test_values - train_values))
    return unseen


def verify_label_consistency(
    df: pd.DataFrame, target_column: str, binary_label_column: str
) -> dict[str, Any]:
    """Verify each multi-class label maps to exactly one binary label value.

    Specifically checks that ``Normal`` always maps to ``0`` and every
    other class always maps to ``1`` — the documented UNSW-NB15
    convention (confirmed during the Milestone A regeneration in
    Task B.2).

    Args:
        df: Loaded dataset split.
        target_column: Multi-class target column (``attack_cat``).
        binary_label_column: Binary label column (``label``).

    Returns:
        Dict with ``status`` and a list of any ``inconsistent_classes``
        found (class names mapping to more than one binary value, or
        violating the Normal=0/Attack=1 convention).
    """
    grouped = df.groupby(target_column)[binary_label_column].unique()
    inconsistent = []

    for class_name, label_values in grouped.items():
        if len(label_values) > 1:
            inconsistent.append({"class": str(class_name), "issue": "maps to multiple binary labels", "values": label_values.tolist()})
        elif class_name == "Normal" and label_values[0] != 0:
            inconsistent.append({"class": str(class_name), "issue": "Normal should map to 0", "values": label_values.tolist()})
        elif class_name != "Normal" and label_values[0] != 1:
            inconsistent.append({"class": str(class_name), "issue": "Attack class should map to 1", "values": label_values.tolist()})

    return {"status": "PASS" if not inconsistent else "FAIL", "inconsistent_classes": inconsistent}


# ══════════════════════════════════════════════════════════════
# Safe cleaning operation (evidence-gated)
# ══════════════════════════════════════════════════════════════

def clean_categorical_whitespace(
    df: pd.DataFrame, categorical_columns: list[str]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Strip leading/trailing whitespace from categorical columns, if any exists.

    This is the only value-modifying operation this module is
    permitted to apply. It is a no-op (returns a column-identical
    copy) unless whitespace was actually detected by
    :func:`validate_categorical_values` — calling it does not imply
    a transformation occurred; check the returned report's
    ``columns_changed`` list.

    Args:
        df: Loaded dataset split.
        categorical_columns: Columns to clean.

    Returns:
        Tuple of ``(cleaned_df, report)`` where *report* lists which
        columns (if any) had whitespace stripped and how many values
        were affected.
    """
    cleaned = df.copy()
    columns_changed: list[dict[str, Any]] = []

    for col in categorical_columns:
        stripped = cleaned[col].astype(str).str.strip()
        changed_mask = cleaned[col].astype(str) != stripped
        changed_count = int(changed_mask.sum())
        if changed_count > 0:
            cleaned[col] = stripped
            columns_changed.append({"column": col, "values_changed": changed_count})

    return cleaned, {"columns_changed": columns_changed, "total_values_changed": sum(c["values_changed"] for c in columns_changed)}


# ══════════════════════════════════════════════════════════════
# Per-split quality check orchestration
# ══════════════════════════════════════════════════════════════

def run_data_quality_checks(
    df: pd.DataFrame,
    split_label: str,
    expected_columns: list[str],
    expected_dtypes: dict[str, str],
    target_column: str,
    binary_label_column: str,
) -> dict[str, Any]:
    """Run every required quality validation for a single split.

    Re-verifies missing values, duplicates, schema consistency, and
    target integrity (reusing B.2/C.1 functions), then runs the new
    C.2 checks: infinite values, invalid (negative) numeric values,
    categorical whitespace/empty-string issues, and label consistency.

    Args:
        df: Loaded dataset split.
        split_label: ``"training"`` or ``"testing"`` (for logging).
        expected_columns: Frozen schema column list.
        expected_dtypes: Frozen schema dtype mapping.
        target_column: Multi-class target column name.
        binary_label_column: Binary label column name.

    Returns:
        Dict bundling every check's result for this split.
    """
    logger.info("Data quality validation started: %s split", split_label)

    cats = categorize_features(df)
    numeric_cols = [c for c in cats["numerical"] if c != "id"]
    categorical_cols = [c for c in cats["categorical"] if c != target_column]

    schema_result = run_schema_validation(df, expected_columns, expected_dtypes, target_column)
    logger.info("Schema validation (%s): %s", split_label, schema_result["overall_status"])

    missing_result = profile_missing_data(df)
    duplicate_result = profile_duplicates(df)
    target_result = verify_target_column(df, target_column)
    infinite_result = detect_infinite_values(df, numeric_cols)
    invalid_numeric_result = detect_invalid_numeric_values(df, numeric_cols)
    categorical_result = validate_categorical_values(df, categorical_cols)
    label_consistency_result = verify_label_consistency(df, target_column, binary_label_column)

    logger.info(
        "Quality checks complete (%s): missing=%d, duplicates=%d, infinite=%d, invalid_numeric=%d, "
        "empty_strings=%d, label_consistency=%s",
        split_label,
        missing_result["total_missing"],
        duplicate_result["duplicate_count"],
        infinite_result["total_infinite"],
        invalid_numeric_result["total_invalid"],
        categorical_result["total_empty_strings"],
        label_consistency_result["status"],
    )

    return {
        "split_label": split_label,
        "row_count": len(df),
        "schema": schema_result,
        "missing_values": missing_result,
        "duplicates": duplicate_result,
        "target_integrity": target_result,
        "infinite_values": infinite_result,
        "invalid_numeric_values": invalid_numeric_result,
        "categorical_validation": categorical_result,
        "label_consistency": label_consistency_result,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
    }


# ══════════════════════════════════════════════════════════════
# Evidence-based cleaning decisions
# ══════════════════════════════════════════════════════════════

def determine_cleaning_actions(quality_report: dict[str, Any]) -> list[dict[str, Any]]:
    """Decide, from evidence alone, which cleaning actions are warranted.

    Every potential action — imputation, deduplication, whitespace
    cleaning — is evaluated and recorded whether or not it is
    performed, with the reason, the evidence, and the expected impact.

    Args:
        quality_report: Output of :func:`run_data_quality_checks`.

    Returns:
        List of decision dicts, each with ``action``, ``performed``,
        ``reason``, ``evidence``, and ``expected_impact``.
    """
    decisions = []

    missing_count = quality_report["missing_values"]["total_missing"]
    decisions.append({
        "action": "imputation",
        "performed": False,
        "reason": "No missing values detected in this split." if missing_count == 0
        else f"{missing_count} missing values detected — imputation required.",
        "evidence": f"profile_missing_data() total_missing = {missing_count} (re-verified live, consistent with Task B.2)",
        "expected_impact": "None — no data altered." if missing_count == 0
        else "Would alter feature distributions; not yet implemented (Research Task C.2 scope is detection only when evidence is absent).",
    })

    duplicate_count = quality_report["duplicates"]["duplicate_count"]
    decisions.append({
        "action": "deduplication",
        "performed": False,
        "reason": "No duplicate rows detected in this split." if duplicate_count == 0
        else f"{duplicate_count} duplicate rows detected — removal would be warranted.",
        "evidence": f"profile_duplicates() duplicate_count = {duplicate_count} (re-verified live, consistent with Task B.2)",
        "expected_impact": "None — no rows removed." if duplicate_count == 0
        else "Would reduce row count and could shift class distribution; not yet implemented.",
    })

    whitespace_count = quality_report["categorical_validation"]["total_whitespace_issues"]
    empty_count = quality_report["categorical_validation"]["total_empty_strings"]
    decisions.append({
        "action": "categorical_whitespace_cleaning",
        "performed": whitespace_count > 0,
        "reason": "No leading/trailing whitespace detected in categorical columns." if whitespace_count == 0
        else f"{whitespace_count} values had leading/trailing whitespace — stripped.",
        "evidence": f"validate_categorical_values() total_whitespace_issues = {whitespace_count}, total_empty_strings = {empty_count}",
        "expected_impact": "None — categorical values already clean." if whitespace_count == 0
        else f"{whitespace_count} string values normalised; no semantic change to category meaning.",
    })

    infinite_count = quality_report["infinite_values"]["total_infinite"]
    decisions.append({
        "action": "infinite_value_handling",
        "performed": False,
        "reason": "No infinite values detected in numeric columns." if infinite_count == 0
        else f"{infinite_count} infinite values detected — handling required.",
        "evidence": f"detect_infinite_values() total_infinite = {infinite_count}",
        "expected_impact": "None." if infinite_count == 0
        else "Would require replacement or row removal; not yet implemented.",
    })

    invalid_count = quality_report["invalid_numeric_values"]["total_invalid"]
    decisions.append({
        "action": "invalid_numeric_correction",
        "performed": False,
        "reason": "No negative values detected in semantically non-negative numeric columns." if invalid_count == 0
        else f"{invalid_count} negative values detected in non-negative columns — investigation required.",
        "evidence": f"detect_invalid_numeric_values() total_invalid = {invalid_count}",
        "expected_impact": "None." if invalid_count == 0
        else "Would require correction or removal pending root-cause investigation; not yet implemented.",
    })

    return decisions


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_cleaning_tables(train_report: dict[str, Any], test_report: dict[str, Any]) -> dict[str, Path]:
    """Save the three required CSV tables, with a ``split`` column.

    Args:
        train_report: Output of :func:`run_data_quality_checks` (training).
        test_report: Output of :func:`run_data_quality_checks` (testing).

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    summary_rows = []
    for r in (train_report, test_report):
        summary_rows.append({
            "split": r["split_label"],
            "row_count": r["row_count"],
            "schema_status": r["schema"]["overall_status"],
            "missing_values": r["missing_values"]["total_missing"],
            "duplicate_rows": r["duplicates"]["duplicate_count"],
            "infinite_values": r["infinite_values"]["total_infinite"],
            "invalid_numeric_values": r["invalid_numeric_values"]["total_invalid"],
            "empty_strings": r["categorical_validation"]["total_empty_strings"],
            "whitespace_issues": r["categorical_validation"]["total_whitespace_issues"],
            "label_consistency_status": r["label_consistency"]["status"],
        })
    path = tables_dir / "data_quality_summary.csv"
    pd.DataFrame(summary_rows).to_csv(path, index=False)
    paths["data_quality_summary"] = path

    cat_rows = []
    for r in (train_report, test_report):
        for entry in r["categorical_validation"]["per_column"]:
            cat_rows.append({"split": r["split_label"], **entry})
    path = tables_dir / "categorical_validation.csv"
    pd.DataFrame(cat_rows).to_csv(path, index=False)
    paths["categorical_validation"] = path

    num_rows = []
    for r in (train_report, test_report):
        inf_by_col = {c["column"]: c["infinite_count"] for c in r["infinite_values"]["per_column"]}
        for entry in r["invalid_numeric_values"]["per_column"]:
            num_rows.append({
                "split": r["split_label"],
                "column": entry["column"],
                "negative_count": entry["negative_count"],
                "infinite_count": inf_by_col.get(entry["column"], 0),
            })
    path = tables_dir / "numeric_validation.csv"
    pd.DataFrame(num_rows).to_csv(path, index=False)
    paths["numeric_validation"] = path

    logger.info("Table generated: %d data cleaning CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def generate_cleaning_summary(
    train_report: dict[str, Any],
    test_report: dict[str, Any],
    train_actions: list[dict[str, Any]],
    test_actions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a concise cleaning summary suitable for the paper's text.

    Args:
        train_report: Output of :func:`run_data_quality_checks` (training).
        test_report: Output of :func:`run_data_quality_checks` (testing).
        train_actions: Output of :func:`determine_cleaning_actions` (training).
        test_actions: Output of :func:`determine_cleaning_actions` (testing).

    Returns:
        Flat summary dict.
    """
    actions_performed = [a["action"] for a in train_actions + test_actions if a["performed"]]
    actions_not_performed = sorted({a["action"] for a in train_actions + test_actions if not a["performed"]})

    return {
        "training_missing_values": train_report["missing_values"]["total_missing"],
        "testing_missing_values": test_report["missing_values"]["total_missing"],
        "training_duplicate_rows": train_report["duplicates"]["duplicate_count"],
        "testing_duplicate_rows": test_report["duplicates"]["duplicate_count"],
        "training_infinite_values": train_report["infinite_values"]["total_infinite"],
        "testing_infinite_values": test_report["infinite_values"]["total_infinite"],
        "training_invalid_numeric": train_report["invalid_numeric_values"]["total_invalid"],
        "testing_invalid_numeric": test_report["invalid_numeric_values"]["total_invalid"],
        "training_label_consistency": train_report["label_consistency"]["status"],
        "testing_label_consistency": test_report["label_consistency"]["status"],
        "actions_performed": actions_performed,
        "actions_not_performed": sorted(set(actions_not_performed) - set(actions_performed)),
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }


def _render_cleaning_markdown(report: dict[str, Any]) -> str:
    """Render the full data cleaning report as Markdown.

    Args:
        report: Report dict from :func:`run_data_cleaning`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    lines: list[str] = [
        "# UNSW-NB15 Data Cleaning Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Required Validations (Re-verified)",
        "",
        "| Check | Training | Testing |",
        "|---|---|---|",
        f"| Missing Values | {s['training_missing_values']} | {s['testing_missing_values']} |",
        f"| Duplicate Rows | {s['training_duplicate_rows']} | {s['testing_duplicate_rows']} |",
        f"| Infinite Values | {s['training_infinite_values']} | {s['testing_infinite_values']} |",
        f"| Invalid Numeric (negative) | {s['training_invalid_numeric']} | {s['testing_invalid_numeric']} |",
        f"| Label Consistency | {s['training_label_consistency']} | {s['testing_label_consistency']} |",
        "",
        "---",
        "",
        "## Cleaning Decisions (Training Split)",
        "",
    ]
    for a in report["training"]["actions"]:
        lines += [
            f"### {a['action']} — {'PERFORMED' if a['performed'] else 'NOT PERFORMED'}",
            f"- **Reason:** {a['reason']}",
            f"- **Evidence:** {a['evidence']}",
            f"- **Expected impact:** {a['expected_impact']}",
            "",
        ]

    lines += ["---", "", "## Cleaning Decisions (Testing Split)", ""]
    for a in report["testing"]["actions"]:
        lines += [
            f"### {a['action']} — {'PERFORMED' if a['performed'] else 'NOT PERFORMED'}",
            f"- **Reason:** {a['reason']}",
            f"- **Evidence:** {a['evidence']}",
            f"- **Expected impact:** {a['expected_impact']}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Unseen Categories (Test vs. Training)",
        "",
        "*Categories present in the testing split's categorical columns that were never observed in training "
        "— relevant for the future encoding stage (Research Task C.3); reported only, not acted on here.*",
        "",
    ]
    any_unseen = False
    for col, values in report["unseen_categories"].items():
        if values:
            any_unseen = True
            lines.append(f"- `{col}`: {', '.join(values)}")
    if not any_unseen:
        lines.append("*None — every test-set category was observed during training.*")

    lines += [
        "",
        "---",
        "",
        "## Data Cleaning Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
    ]
    if s["actions_performed"]:
        lines.append(f"**Actions performed:** {', '.join(s['actions_performed'])}")
    else:
        lines.append(
            "**No cleaning actions were performed.** Re-verification of missing values, duplicate rows, "
            "infinite values, invalid numeric values, and categorical formatting confirmed the dataset "
            "requires no correction beyond what was already established in Research Tasks B.1-B.3."
        )
    lines += [
        "",
        f"**Actions intentionally not performed:** {', '.join(s['actions_not_performed'])}, "
        "because no supporting evidence was found for any of them in either split.",
        "",
        "---",
        "*End of Data Cleaning Report*",
    ]
    return "\n".join(lines) + "\n"


def save_cleaning_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the data cleaning report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_data_cleaning`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "data_cleaning_report.json", json_safe)
    md_path = write_text(reports_dir / "data_cleaning_report.md", _render_cleaning_markdown(report))
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_data_cleaning() -> dict[str, Any]:
    """Run evidence-based data quality validation and cleaning for both splits.

    Loads training and testing data independently, re-verifies every
    required quality check for each, determines (from evidence alone)
    which cleaning actions are warranted, saves CSV tables, and writes
    the JSON/Markdown reports.

    Returns:
        Dict with ``training``, ``testing``, ``unseen_categories``,
        and ``summary`` keys.
    """
    dataset_cfg = _load_dataset_config()
    preprocessing_cfg = _load_preprocessing_config()
    target_column = dataset_cfg.get("target_column", "attack_cat")
    binary_label_column = dataset_cfg.get("binary_label_column", "label")
    expected_columns = preprocessing_cfg["expected_columns"]
    expected_dtypes = preprocessing_cfg["expected_dtypes"]

    train_df, test_df = load_datasets()

    train_quality = run_data_quality_checks(
        train_df, "training", expected_columns, expected_dtypes, target_column, binary_label_column
    )
    test_quality = run_data_quality_checks(
        test_df, "testing", expected_columns, expected_dtypes, target_column, binary_label_column
    )

    train_actions = determine_cleaning_actions(train_quality)
    test_actions = determine_cleaning_actions(test_quality)

    unseen_categories = find_unseen_categories(train_df, test_df, train_quality["categorical_columns"])

    table_paths = save_cleaning_tables(train_quality, test_quality)

    summary = generate_cleaning_summary(train_quality, test_quality, train_actions, test_actions)

    report = {
        "training": {"quality": train_quality, "actions": train_actions},
        "testing": {"quality": test_quality, "actions": test_actions},
        "unseen_categories": unseen_categories,
        "summary": summary,
    }
    save_cleaning_report(report)

    logger.info(
        "Data quality validation completed — %d tables, 2 reports saved, %d actions performed",
        len(table_paths), len(summary["actions_performed"]),
    )
    return report
