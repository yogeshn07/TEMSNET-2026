"""Preprocessing pipeline framework for UNSW-NB15 — architecture only.

This module defines the **fixed execution order** for every
preprocessing stage and implements only the value-preserving
operations that are safe before any modelling decision has been
made: schema verification, column-order verification, dtype
verification, target-column verification, and feature/target (X/y)
separation. No feature value is read, imputed, encoded, scaled, or
removed by this module.

Stages 4-9 (missing value handling, duplicate handling, encoding,
scaling, feature selection, class balancing) are declared in
:data:`PIPELINE_STAGES` with ``status=PLANNED`` and are implemented in
later Research Tasks (C.2 onward). The registry exists so every
future stage has a fixed, reviewable position in the sequence before
a single line of its implementation is written.

Usage::

    from src.data.preprocessing_pipeline import run_preprocessing_pipeline

    result = run_preprocessing_pipeline()

Data leakage protection
~~~~~~~~~~~~~~~~~~~~~~~~
1. Training and testing CSVs are loaded as two separate ``DataFrame``
   objects (via :func:`src.data.eda.load_datasets`) and are never
   concatenated, joined, or otherwise combined anywhere in this
   module.
2. Each split is validated and split into X/y independently, using
   the same frozen schema reference (``configs/preprocessing.yaml``)
   but never each other's data — no statistic computed on one split
   can leak into the other because no such statistic is computed
   here at all.
3. Stage order is enforced by :data:`PIPELINE_STAGES`, an immutable
   ordered tuple. A future stage cannot silently run earlier or later
   than declared without an explicit, reviewable edit to that tuple.
4. **Contract for future stages (C.2+):** any transformer that learns
   parameters from data (imputer, encoder, scaler, feature selector)
   MUST be fitted on ``X_train`` only, then applied via
   ``.transform()`` to both ``X_train`` and ``X_test``. Class
   balancing (e.g. SMOTE, undersampling) MUST be applied to the
   training split only — the test split must always reflect the
   real-world class distribution. This module does not implement
   those stages, but documents the rule they must follow.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.data.eda import load_datasets
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_PREPROCESSING_CONFIG_FILENAME = "preprocessing.yaml"
_DATASET_CONFIG_FILENAME = "dataset.yaml"


class SchemaValidationError(Exception):
    """Raised when a dataset split fails schema, order, dtype, or target validation."""


# ══════════════════════════════════════════════════════════════
# Stage registry — the fixed execution order
# ══════════════════════════════════════════════════════════════

class StageStatus(str, Enum):
    """Implementation status of a pipeline stage."""

    IMPLEMENTED = "implemented"
    PLANNED = "planned"


@dataclass(frozen=True)
class PipelineStageSpec:
    """Metadata describing one stage in the fixed preprocessing sequence.

    Attributes:
        order: Position in the execution sequence (1-indexed).
        name: Short stage identifier.
        status: Whether this stage is implemented now or planned for
            a later Research Task.
        description: One-line description of what the stage does.
        leakage_note: Leakage-prevention rule that applies to this
            stage, if any.
        research_task: The Research Task expected to implement this
            stage (for planned stages).
    """

    order: int
    name: str
    status: StageStatus
    description: str
    leakage_note: str = ""
    research_task: str = ""


PIPELINE_STAGES: tuple[PipelineStageSpec, ...] = (
    PipelineStageSpec(
        order=1, name="Dataset Validation", status=StageStatus.IMPLEMENTED,
        description="Verify raw dataset files exist and pass integrity checks before loading.",
        leakage_note="Runs independently for train and test file paths.",
        research_task="C.1 (this task, reuses B.1)",
    ),
    PipelineStageSpec(
        order=2, name="Data Loading", status=StageStatus.IMPLEMENTED,
        description="Load training and testing CSVs as two independent DataFrames.",
        leakage_note="Train and test are never concatenated at load time.",
        research_task="C.1 (this task, reuses B.2/B.3 loader)",
    ),
    PipelineStageSpec(
        order=3, name="Schema Verification", status=StageStatus.IMPLEMENTED,
        description="Verify column presence, column order, dtypes, and target column against a frozen schema contract.",
        leakage_note="Each split validated against the same static reference schema, never against the other split.",
        research_task="C.1 (this task)",
    ),
    PipelineStageSpec(
        order=4, name="Missing Value Handling", status=StageStatus.PLANNED,
        description="Impute or flag missing values (UNSW-NB15 currently has none; safeguard for future data).",
        leakage_note="Any imputer must be fit on X_train only and applied to X_test via transform().",
        research_task="C.2",
    ),
    PipelineStageSpec(
        order=5, name="Duplicate Handling", status=StageStatus.PLANNED,
        description="Detect and decide how to handle duplicate rows within each split.",
        leakage_note="Deduplication is evaluated independently per split; rows are never compared across splits.",
        research_task="C.2",
    ),
    PipelineStageSpec(
        order=6, name="Feature Encoding", status=StageStatus.PLANNED,
        description="Encode categorical features (proto, service, state) into numeric representations.",
        leakage_note="Encoder (e.g. OneHotEncoder, OrdinalEncoder) fit on X_train categories only; test set categories not seen during fit are handled explicitly, never used to refit.",
        research_task="C.3",
    ),
    PipelineStageSpec(
        order=7, name="Feature Scaling", status=StageStatus.PLANNED,
        description="Scale/normalise numerical features.",
        leakage_note="Scaler statistics (mean, std, min, max) computed on X_train only, applied to X_test via transform().",
        research_task="C.3",
    ),
    PipelineStageSpec(
        order=8, name="Feature Selection", status=StageStatus.PLANNED,
        description="Select a feature subset based on training-set statistics (e.g. variance, correlation, importance).",
        leakage_note="Selection criteria computed on X_train/y_train only; the same selected columns are then applied to X_test.",
        research_task="C.4",
    ),
    PipelineStageSpec(
        order=9, name="Class Balancing", status=StageStatus.PLANNED,
        description="Address class imbalance (e.g. oversampling, undersampling, class weighting) for model training.",
        leakage_note="Applied to the training split only; the test split must retain the real-world class distribution for valid evaluation.",
        research_task="C.5",
    ),
    PipelineStageSpec(
        order=10, name="Export Processed Dataset", status=StageStatus.PLANNED,
        description="Persist the fully processed train/test feature and target arrays to data/processed/.",
        leakage_note="Train and test exported as separate files; no merged artefact is ever produced.",
        research_task="C.6",
    ),
)


def verify_stage_registry_integrity() -> bool:
    """Verify :data:`PIPELINE_STAGES` is contiguous, ordered, and unique.

    Returns:
        ``True`` if stage orders are exactly ``1..len(PIPELINE_STAGES)``
        with no gaps or duplicates.
    """
    orders = [s.order for s in PIPELINE_STAGES]
    expected = list(range(1, len(PIPELINE_STAGES) + 1))
    valid = orders == expected
    if not valid:
        logger.error("Pipeline stage registry is not contiguous/ordered: %s", orders)
    return valid


# ══════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════

def _load_preprocessing_config() -> dict[str, Any]:
    """Load ``configs/preprocessing.yaml``.

    Returns:
        Parsed preprocessing configuration (expected schema contract).
    """
    config_path = get_path_manager().configs_dir / _PREPROCESSING_CONFIG_FILENAME
    return read_yaml(config_path)


def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml`` (for ``target_column``).

    Returns:
        Parsed dataset configuration dictionary.
    """
    config_path = get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME
    return read_yaml(config_path)


# ══════════════════════════════════════════════════════════════
# Schema verification (safe, value-preserving)
# ══════════════════════════════════════════════════════════════

def verify_schema_columns(df: pd.DataFrame, expected_columns: list[str]) -> dict[str, Any]:
    """Verify the dataset contains exactly the expected columns (any order).

    Args:
        df: Loaded dataset split.
        expected_columns: Frozen schema column list.

    Returns:
        Dict with ``status``, ``missing_columns``, ``extra_columns``.
    """
    actual = set(df.columns)
    expected = set(expected_columns)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    return {
        "status": "PASS" if not missing and not extra else "FAIL",
        "missing_columns": missing,
        "extra_columns": extra,
    }


def verify_column_order(df: pd.DataFrame, expected_columns: list[str]) -> dict[str, Any]:
    """Verify columns appear in the exact expected order.

    Args:
        df: Loaded dataset split.
        expected_columns: Frozen schema column list, in order.

    Returns:
        Dict with ``status`` and the index of the first mismatch
        (``None`` if order matches or column sets differ).
    """
    actual_columns = list(df.columns)
    if actual_columns == expected_columns:
        return {"status": "PASS", "first_mismatch_index": None}

    first_mismatch = next(
        (i for i, (a, e) in enumerate(zip(actual_columns, expected_columns)) if a != e),
        min(len(actual_columns), len(expected_columns)),
    )
    return {"status": "FAIL", "first_mismatch_index": first_mismatch}


def verify_dtypes(df: pd.DataFrame, expected_dtypes: dict[str, str]) -> dict[str, Any]:
    """Verify each column's dtype matches the frozen schema contract.

    Args:
        df: Loaded dataset split.
        expected_dtypes: Mapping of column name to expected dtype string.

    Returns:
        Dict with ``status`` and a list of ``mismatches`` (column,
        expected, actual) for columns present in both *df* and
        *expected_dtypes*.
    """
    mismatches = []
    for col, expected_dtype in expected_dtypes.items():
        if col not in df.columns:
            continue
        actual_dtype = str(df[col].dtype)
        if actual_dtype != expected_dtype:
            mismatches.append({"column": col, "expected": expected_dtype, "actual": actual_dtype})

    return {"status": "PASS" if not mismatches else "FAIL", "mismatches": mismatches}


def verify_target_column(df: pd.DataFrame, target_column: str) -> dict[str, Any]:
    """Verify the target column is present, non-null, and has multiple classes.

    Args:
        df: Loaded dataset split.
        target_column: Expected target column name.

    Returns:
        Dict with ``status``, ``present``, ``null_count``, ``num_classes``.
    """
    if target_column not in df.columns:
        return {"status": "FAIL", "present": False, "null_count": None, "num_classes": None}

    null_count = int(df[target_column].isna().sum())
    num_classes = int(df[target_column].nunique(dropna=True))
    status = "PASS" if null_count == 0 and num_classes > 1 else "FAIL"

    return {"status": status, "present": True, "null_count": null_count, "num_classes": num_classes}


def run_schema_validation(
    df: pd.DataFrame,
    expected_columns: list[str],
    expected_dtypes: dict[str, str],
    target_column: str,
) -> dict[str, Any]:
    """Run every schema check and aggregate into one validation result.

    Args:
        df: Loaded dataset split.
        expected_columns: Frozen schema column list, in order.
        expected_dtypes: Mapping of column name to expected dtype.
        target_column: Expected target column name.

    Returns:
        Aggregated dict with ``overall_status`` plus each individual
        check's result.
    """
    checks = {
        "columns": verify_schema_columns(df, expected_columns),
        "column_order": verify_column_order(df, expected_columns),
        "dtypes": verify_dtypes(df, expected_dtypes),
        "target_column": verify_target_column(df, target_column),
    }
    overall = "PASS" if all(c["status"] == "PASS" for c in checks.values()) else "FAIL"
    return {"overall_status": overall, **checks}


# ══════════════════════════════════════════════════════════════
# Feature / target separation (safe, value-preserving)
# ══════════════════════════════════════════════════════════════

def split_features_target(df: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, pd.Series]:
    """Separate features (X) from the target (y) without altering any value.

    Args:
        df: Validated dataset split.
        target_column: Column to extract as the target.

    Returns:
        Tuple of ``(X, y)`` — ``X`` is *df* minus the target column,
        ``y`` is the target column as a ``Series``. No values are
        modified, imputed, encoded, or scaled.
    """
    X = df.drop(columns=[target_column])
    y = df[target_column].copy()
    return X, y


# ══════════════════════════════════════════════════════════════
# Split bundle & pipeline orchestration
# ══════════════════════════════════════════════════════════════

@dataclass
class SplitBundle:
    """Validated, X/y-separated result for a single dataset split.

    Attributes:
        split_label: ``"training"`` or ``"testing"``.
        X: Feature matrix (target column removed, values unmodified).
        y: Target vector.
        validation: Output of :func:`run_schema_validation`.
        row_count: Number of rows in the split.
    """

    split_label: str
    X: pd.DataFrame
    y: pd.Series
    validation: dict[str, Any]
    row_count: int


@dataclass
class PreprocessingResult:
    """Result of running the preprocessing pipeline's safe stages.

    Attributes:
        train: :class:`SplitBundle` for the training split.
        test: :class:`SplitBundle` for the testing split.
        target_column: Target column name used for X/y separation.
        generated_utc: ISO-8601 UTC timestamp of the run.
    """

    train: SplitBundle
    test: SplitBundle
    target_column: str
    generated_utc: str


class PreprocessingPipeline:
    """Orchestrates the safe, value-preserving preprocessing stages.

    Loads training and testing data independently, validates each
    against the frozen schema contract, and separates features from
    the target — all without merging the two splits or modifying any
    feature value. See the module docstring for the full data leakage
    protection strategy.

    Args:
        expected_columns: Frozen schema column list, in order.
        expected_dtypes: Mapping of column name to expected dtype.
        target_column: Name of the target column.
    """

    def __init__(
        self,
        expected_columns: list[str],
        expected_dtypes: dict[str, str],
        target_column: str,
    ) -> None:
        self.expected_columns = expected_columns
        self.expected_dtypes = expected_dtypes
        self.target_column = target_column

    def validate_and_split(self, df: pd.DataFrame, split_label: str) -> SplitBundle:
        """Validate one split's schema, then separate X/y.

        Args:
            df: Loaded dataset split.
            split_label: ``"training"`` or ``"testing"`` (for logging).

        Returns:
            :class:`SplitBundle` for this split.

        Raises:
            SchemaValidationError: If any schema check fails.
        """
        validation = run_schema_validation(
            df, self.expected_columns, self.expected_dtypes, self.target_column
        )
        if validation["overall_status"] != "PASS":
            raise SchemaValidationError(
                f"Schema validation failed for {split_label} split: {validation}"
            )
        logger.info("Schema verification PASSED: %s split", split_label)

        X, y = split_features_target(df, self.target_column)
        logger.info(
            "Feature/target separated: %s split — X=%s, y=%d rows", split_label, X.shape, len(y)
        )

        return SplitBundle(split_label=split_label, X=X, y=y, validation=validation, row_count=len(df))

    def run(self) -> PreprocessingResult:
        """Run stages 1-3 (validation, loading, schema check) plus X/y split.

        Returns:
            :class:`PreprocessingResult` with independent train/test bundles.
        """
        logger.info("Preprocessing pipeline started — stages 1-3 (safe operations only)")

        train_df, test_df = load_datasets()
        logger.info("Stage 1-2 complete: dataset validated and loaded (train=%d, test=%d)", len(train_df), len(test_df))

        train_bundle = self.validate_and_split(train_df, "training")
        test_bundle = self.validate_and_split(test_df, "testing")
        logger.info("Stage 3 complete: schema verified and X/y separated for both splits")

        return PreprocessingResult(
            train=train_bundle,
            test=test_bundle,
            target_column=self.target_column,
            generated_utc=datetime.now(tz=timezone.utc).isoformat(),
        )


# ══════════════════════════════════════════════════════════════
# Design report (architecture documentation)
# ══════════════════════════════════════════════════════════════

def _stage_to_dict(stage: PipelineStageSpec) -> dict[str, Any]:
    """Convert a :class:`PipelineStageSpec` to a JSON-safe dict.

    Args:
        stage: Stage specification.

    Returns:
        Dict representation with the status enum converted to a string.
    """
    return {
        "order": stage.order,
        "name": stage.name,
        "status": stage.status.value,
        "description": stage.description,
        "leakage_note": stage.leakage_note,
        "research_task": stage.research_task,
    }


_PIPELINE_DIAGRAM = """
+-----------------------------------------------------------------+
|              UNSW-NB15 Preprocessing Pipeline (C.1)             |
+-----------------------------------------------------------------+
|   [TRAINING SET]                          [TESTING SET]         |
|        |                                       |                |
|        v                                       v                |
|   1. Dataset Validation  ----------------  1. Dataset Validation|
|        |                                       |                |
|        v                                       v                |
|   2. Data Loading        ----------------  2. Data Loading      |
|        |                                       |                |
|        v                                       v                |
|   3. Schema Verification ----------------  3. Schema Verification|
|        |                                       |                |
|        v                                       v                |
|   X_train, y_train                        X_test, y_test        |
|        |                                       |                |
|        v                                       v                |
|   4. Missing Value Handling          [PLANNED — C.2]            |
|   5. Duplicate Handling              [PLANNED — C.2]            |
|   6. Feature Encoding   (fit TRAIN only, transform both) [C.3]  |
|   7. Feature Scaling    (fit TRAIN only, transform both) [C.3]  |
|   8. Feature Selection  (fit TRAIN only, transform both) [C.4]  |
|   9. Class Balancing    (TRAIN only, TEST untouched)     [C.5]  |
|        |                                       |                |
|        v                                       v                |
|  10. Export Processed Dataset  ----------  10. Export Processed |
|      data/processed/train.*                data/processed/test.*|
+-----------------------------------------------------------------+
  NOTE: Training and testing data are never merged at any stage.
  NOTE: Any "fit" operation (stages 6-9) learns parameters from
        the TRAINING split only and is applied to TEST via
        transform() — never re-fit on test data.
""".strip("\n")


def generate_pipeline_design_report(result: PreprocessingResult) -> dict[str, Any]:
    """Build the full pipeline design report.

    Args:
        result: Output of :meth:`PreprocessingPipeline.run`.

    Returns:
        JSON-serialisable dict covering the stage registry, leakage
        safeguards, data flow diagram, and current validation results.
    """
    return {
        "pipeline_diagram": _PIPELINE_DIAGRAM,
        "stages": [_stage_to_dict(s) for s in PIPELINE_STAGES],
        "stage_registry_integrity": verify_stage_registry_integrity(),
        "leakage_safeguards": [
            "Training and testing CSVs are loaded as two independent DataFrames and never concatenated.",
            "Each split is validated against the same static schema contract, never against the other split's data.",
            "X/y separation removes the target column only; no feature value is read, imputed, encoded, or scaled.",
            "Stage order is fixed by an immutable registry (PIPELINE_STAGES), making out-of-order execution a visible code change.",
            "Future fit-based stages (6-9) must fit on X_train only and transform both splits; class balancing (9) applies to training only.",
        ],
        "target_column": result.target_column,
        "training": {
            "row_count": result.train.row_count,
            "feature_count": result.train.X.shape[1],
            "validation": result.train.validation,
        },
        "testing": {
            "row_count": result.test.row_count,
            "feature_count": result.test.X.shape[1],
            "validation": result.test.validation,
        },
        "generated_utc": result.generated_utc,
        "project_version": VERSION,
        "platform": platform.platform(),
    }


def _render_design_markdown(report: dict[str, Any]) -> str:
    """Render the pipeline design report as Markdown.

    Args:
        report: Output of :func:`generate_pipeline_design_report`.

    Returns:
        Markdown document as a string.
    """
    lines: list[str] = [
        "# UNSW-NB15 Preprocessing Pipeline — Design Report",
        "",
        f"**Generated:** {report['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {report['project_version']}",
        "",
        "---",
        "",
        "## Pipeline Diagram",
        "",
        "```",
        report["pipeline_diagram"],
        "```",
        "",
        "---",
        "",
        "## Execution Sequence",
        "",
        "| Order | Stage | Status | Research Task | Description |",
        "|---|---|---|---|---|",
    ]
    for s in report["stages"]:
        lines.append(
            f"| {s['order']} | {s['name']} | {s['status']} | {s['research_task']} | {s['description']} |"
        )

    lines += [
        "",
        f"**Stage registry integrity check:** "
        f"{'PASS' if report['stage_registry_integrity'] else 'FAIL'}",
        "",
        "---",
        "",
        "## Data Leakage Prevention Strategy",
        "",
    ]
    lines.extend(f"- {s}" for s in report["leakage_safeguards"])

    lines += [
        "",
        "---",
        "",
        "## Responsibilities of Each Future Stage",
        "",
    ]
    for s in report["stages"]:
        if s["status"] == "planned":
            lines.append(f"**{s['order']}. {s['name']}** ({s['research_task']})  ")
            lines.append(f"{s['description']}  ")
            lines.append(f"*Leakage rule:* {s['leakage_note']}")
            lines.append("")

    lines += [
        "---",
        "",
        "## Current Validation Results (Stages 1-3)",
        "",
        f"**Target column:** `{report['target_column']}`",
        "",
        "| Split | Rows | Features (X) | Schema Status |",
        "|---|---|---|---|",
        f"| Training | {report['training']['row_count']:,} | {report['training']['feature_count']} | "
        f"{report['training']['validation']['overall_status']} |",
        f"| Testing | {report['testing']['row_count']:,} | {report['testing']['feature_count']} | "
        f"{report['testing']['validation']['overall_status']} |",
        "",
        "---",
        "",
        "## Preprocessing Pipeline Design Summary",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        "The preprocessing pipeline follows a fixed 10-stage sequence applied independently to the "
        "training and testing splits of UNSW-NB15. Stages 1-3 (dataset validation, loading, and schema "
        "verification) are implemented and confirmed passing for both splits. Stages 4-9 (missing value "
        "handling, duplicate handling, feature encoding, feature scaling, feature selection, and class "
        "balancing) are architecturally reserved but not yet implemented, ensuring no transformation "
        "decision is made before the exploratory analysis (B.3) is fully incorporated into the design. "
        "Data leakage is prevented structurally: the two splits are never merged, and every future "
        "parameter-learning stage is contractually required to fit on the training split only.",
        "",
        "---",
        "*End of Preprocessing Pipeline Design Report*",
    ]
    return "\n".join(lines) + "\n"


def save_pipeline_design_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the design report as JSON and Markdown.

    Args:
        report: Output of :func:`generate_pipeline_design_report`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_path = write_json(reports_dir / "preprocessing_pipeline_design.json", report)
    md_path = write_text(reports_dir / "preprocessing_pipeline_design.md", _render_design_markdown(report))
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_preprocessing_pipeline() -> PreprocessingResult:
    """Run the safe preprocessing stages and save the design report.

    Returns:
        :class:`PreprocessingResult` with independent train/test bundles.
    """
    preprocessing_cfg = _load_preprocessing_config()
    dataset_cfg = _load_dataset_config()

    pipeline = PreprocessingPipeline(
        expected_columns=preprocessing_cfg["expected_columns"],
        expected_dtypes=preprocessing_cfg["expected_dtypes"],
        target_column=dataset_cfg.get("target_column", "attack_cat"),
    )

    result = pipeline.run()
    report = generate_pipeline_design_report(result)
    save_pipeline_design_report(report)

    logger.info("Preprocessing pipeline design report saved to outputs/reports/")
    return result
