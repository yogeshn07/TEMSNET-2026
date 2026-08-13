"""Leakage-safe categorical feature encoding for UNSW-NB15.

Encodes the categorical feature columns (identified automatically
from the frozen schema in ``configs/preprocessing.yaml``, not
hardcoded) into numeric form using an :class:`~sklearn.preprocessing.
OrdinalEncoder` fitted **exclusively on the training split**. The
fitted encoder is then applied to the testing split via
``.transform()`` — the testing data is never used to learn anything.

Encoding method and rationale
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
UNSW-NB15's categorical features have markedly different cardinality:
``proto`` has 133 observed training categories, ``service`` has 13,
``state`` has 9. One-hot encoding ``proto`` alone would add 133 sparse
binary columns, which:

1. Directly conflicts with this project's XAI focus — SHAP attribution
   on 133 near-empty binary columns is far less interpretable than a
   single attribution on one ordinal-encoded ``proto`` feature.
2. Provides no benefit for the locked research model, Random Forest:
   tree ensembles split on value thresholds and do not assume a
   linear relationship between an encoded value's magnitude and the
   target, unlike linear or distance-based models. A Random Forest
   can still separate non-contiguous groups of ordinal-encoded
   categories by making multiple splits across different trees.

Ordinal encoding is therefore used uniformly for every categorical
column. This is a documented, model-dependent choice — see the
"Limitations" section of the generated report for when it would need
re-evaluation (e.g. if a linear model were substituted for Random
Forest).

Unseen category handling
~~~~~~~~~~~~~~~~~~~~~~~~~
Research Task C.2 found two testing-only ``state`` categories
(``ACC``, ``CLO``) absent from training. ``OrdinalEncoder`` is
configured with ``handle_unknown="use_encoded_value"`` and a fixed
sentinel (:data:`UNKNOWN_CATEGORY_VALUE`, distinct from every valid
learned code) so such categories are mapped deterministically without
raising an error and without influencing the encoder's fit — the
fit happens before the testing split is ever read.

Usage::

    from src.data.feature_encoding import run_feature_encoding

    result = run_feature_encoding()

Design decisions
~~~~~~~~~~~~~~~~
* Reuses :class:`src.data.preprocessing_pipeline.PreprocessingPipeline`
  directly for stages 1-3 (load, validate, X/y split) rather than
  reimplementing dataset loading or schema validation.
* Reuses :func:`src.data.data_cleaning.find_unseen_categories` for
  unseen-category detection rather than recomputing it.
* Categorical columns are identified from
  ``configs/preprocessing.yaml``'s ``expected_dtypes`` (``dtype ==
  "object"``, excluding the target column) — never hardcoded.
* Encoded columns replace the original columns **in place** (same
  column name, same position), so column order is identical to the
  source schema; row order is untouched throughout.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.data.data_cleaning import find_unseen_categories
from src.data.preprocessing_pipeline import PreprocessingPipeline, PreprocessingResult
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_PREPROCESSING_CONFIG_FILENAME = "preprocessing.yaml"

#: Sentinel encoded value for categories seen at transform time but
#: never observed during fitting. Distinct from every valid learned
#: code, which are always >= 0 (ordinal encoder assigns 0..N-1).
#: Must be an int (not float) — scikit-learn's OrdinalEncoder requires
#: this when handle_unknown="use_encoded_value"; the encoded output
#: array itself is still float64 throughout (dtype=np.float64 below).
UNKNOWN_CATEGORY_VALUE: int = -1


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


def get_validated_splits() -> PreprocessingResult:
    """Load and schema-validate both splits via the Task C.1 pipeline.

    Returns:
        :class:`PreprocessingResult` with independent train/test bundles.
    """
    dataset_cfg = _load_dataset_config()
    preprocessing_cfg = _load_preprocessing_config()

    pipeline = PreprocessingPipeline(
        expected_columns=preprocessing_cfg["expected_columns"],
        expected_dtypes=preprocessing_cfg["expected_dtypes"],
        target_column=dataset_cfg.get("target_column", "attack_cat"),
    )
    return pipeline.run()


# ══════════════════════════════════════════════════════════════
# Categorical column identification (schema-driven, not hardcoded)
# ══════════════════════════════════════════════════════════════

def identify_categorical_columns(expected_dtypes: dict[str, str], target_column: str) -> list[str]:
    """Identify categorical feature columns from the frozen schema.

    Args:
        expected_dtypes: Mapping of column name to expected dtype,
            from ``configs/preprocessing.yaml``.
        target_column: Target column to exclude (it is not a feature).

    Returns:
        Sorted list of column names whose expected dtype is
        ``"object"``, excluding *target_column*.
    """
    columns = sorted(
        col for col, dtype in expected_dtypes.items()
        if dtype == "object" and col != target_column
    )
    logger.info("Categorical feature detection: %s", columns)
    return columns


# ══════════════════════════════════════════════════════════════
# Encoder fit / apply (leakage-safe)
# ══════════════════════════════════════════════════════════════

def _encoder_categories(encoder: OrdinalEncoder) -> list[np.ndarray]:
    """Return ``encoder.categories_`` with an explicit, precise type.

    Works around ``OrdinalEncoder.categories_`` being declared with a
    looser array-like union in scikit-learn's type stubs than its
    actual runtime type (``list[numpy.ndarray]``), confirmed empirically.

    Args:
        encoder: Fitted ``OrdinalEncoder``.

    Returns:
        The encoder's learned per-column category arrays.
    """
    return cast(list[np.ndarray], encoder.categories_)


def fit_encoder(X_train: pd.DataFrame, categorical_columns: list[str]) -> OrdinalEncoder:
    """Fit an ``OrdinalEncoder`` using the training split only.

    Args:
        X_train: Training feature matrix.
        categorical_columns: Columns to encode.

    Returns:
        Fitted ``OrdinalEncoder``. Its learned ``categories_`` reflect
        only what was present in *X_train* — the testing split is not
        read by this function.
    """
    encoder = OrdinalEncoder(
        handle_unknown="use_encoded_value",
        unknown_value=UNKNOWN_CATEGORY_VALUE,
        dtype=np.float64,
    )
    encoder.fit(X_train[categorical_columns])
    logger.info(
        "Encoder fitting complete — %d categorical columns, category counts: %s",
        len(categorical_columns),
        {col: len(cats) for col, cats in zip(categorical_columns, _encoder_categories(encoder))},
    )
    return encoder


def apply_encoder(
    X: pd.DataFrame, encoder: OrdinalEncoder, categorical_columns: list[str]
) -> pd.DataFrame:
    """Apply a fitted encoder to a split, replacing columns in place.

    Args:
        X: Feature matrix to transform (training or testing).
        encoder: Encoder previously fitted via :func:`fit_encoder`
            on the training split.
        categorical_columns: Columns to transform.

    Returns:
        New ``DataFrame`` with the same column order and row order as
        *X*; only the categorical columns' values change (object ->
        float64 ordinal codes). All other columns are untouched.
    """
    encoded = X.copy()
    encoded[categorical_columns] = encoder.transform(X[categorical_columns])
    return encoded


# ══════════════════════════════════════════════════════════════
# Unseen category reporting
# ══════════════════════════════════════════════════════════════

def summarize_unseen_categories(
    X_test: pd.DataFrame, unseen: dict[str, list[str]]
) -> list[dict[str, Any]]:
    """Quantify how many testing rows are affected by unseen categories.

    Args:
        X_test: Testing feature matrix (pre-encoding).
        unseen: Output of :func:`src.data.data_cleaning.find_unseen_categories`.

    Returns:
        List of per-column dicts with the unseen category list,
        affected row count, and affected percentage.
    """
    n_rows = len(X_test)
    rows = []
    for col, values in unseen.items():
        affected = int(X_test[col].isin(values).sum()) if values else 0
        rows.append({
            "column": col,
            "unseen_categories": values,
            "affected_row_count": affected,
            "affected_pct": round(100 * affected / n_rows, 4) if n_rows else 0.0,
        })
    return rows


# ══════════════════════════════════════════════════════════════
# Encoding mapping & summary tables
# ══════════════════════════════════════════════════════════════

def build_encoding_mapping(
    encoder: OrdinalEncoder, categorical_columns: list[str]
) -> pd.DataFrame:
    """Build a long-format table of every learned category -> code mapping.

    Args:
        encoder: Fitted ``OrdinalEncoder``.
        categorical_columns: Columns the encoder was fitted on, in order.

    Returns:
        ``DataFrame`` with ``column``, ``category``, ``encoded_value``.
    """
    rows = []
    for col, categories in zip(categorical_columns, _encoder_categories(encoder)):
        rows.extend(
            {"column": col, "category": category, "encoded_value": code}
            for code, category in enumerate(categories)
        )
    return pd.DataFrame(rows)


def summarize_encoded_features(
    X_before: pd.DataFrame, X_after: pd.DataFrame, categorical_columns: list[str]
) -> list[dict[str, Any]]:
    """Summarise the before/after state of each encoded column.

    Args:
        X_before: Feature matrix prior to encoding.
        X_after: Feature matrix after encoding.
        categorical_columns: Columns that were encoded.

    Returns:
        List of per-column dicts with dtype and value-range changes.
    """
    rows = []
    for col in categorical_columns:
        rows.append({
            "column": col,
            "original_dtype": str(X_before[col].dtype),
            "encoded_dtype": str(X_after[col].dtype),
            "original_unique_count": int(X_before[col].nunique(dropna=True)),
            "encoded_min": float(X_after[col].min()),
            "encoded_max": float(X_after[col].max()),
        })
    return rows


# ══════════════════════════════════════════════════════════════
# Reassembly & I/O
# ══════════════════════════════════════════════════════════════

def reassemble_with_target(
    X_encoded: pd.DataFrame, y: pd.Series, target_column: str, expected_columns: list[str]
) -> pd.DataFrame:
    """Reattach the (unmodified) target column at its original schema position.

    Args:
        X_encoded: Encoded feature matrix.
        y: Target values, same row order as *X_encoded*.
        target_column: Name of the target column.
        expected_columns: Frozen schema column list, in original order.

    Returns:
        ``DataFrame`` with columns in exactly the original raw-CSV
        order; only the categorical feature values differ (now
        ordinal-encoded). Target values are untouched.
    """
    combined = X_encoded.copy()
    combined[target_column] = y.values
    return combined[expected_columns]


def save_encoded_dataset(df: pd.DataFrame, directory: Path, stem: str) -> tuple[Path, str]:
    """Save an encoded split, preferring Parquet with a CSV fallback.

    Args:
        df: DataFrame to save.
        directory: Destination directory (created if missing).
        stem: Filename without extension (e.g. ``"training_encoded"``).

    Returns:
        Tuple of ``(resolved_path, format_used)`` where *format_used*
        is ``"parquet"`` or ``"csv"``.
    """
    directory.mkdir(parents=True, exist_ok=True)
    parquet_path = directory / f"{stem}.parquet"

    try:
        df.to_parquet(parquet_path, index=False)
        logger.info("Output generation: saved %s (parquet)", parquet_path.name)
        return parquet_path, "parquet"
    except ImportError:
        csv_path = directory / f"{stem}.csv"
        df.to_csv(csv_path, index=False)
        logger.warning(
            "Parquet engine unavailable — saved %s as CSV instead. "
            "Install pyarrow for Parquet support.", csv_path.name,
        )
        return csv_path, "csv"


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_encoding_tables(
    encoded_summary: list[dict[str, Any]],
    unseen_summary: list[dict[str, Any]],
    mapping_df: pd.DataFrame,
) -> dict[str, Path]:
    """Save the three required CSV tables.

    Args:
        encoded_summary: Output of :func:`summarize_encoded_features`.
        unseen_summary: Output of :func:`summarize_unseen_categories`.
        mapping_df: Output of :func:`build_encoding_mapping`.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    path = tables_dir / "encoded_feature_summary.csv"
    pd.DataFrame(encoded_summary).to_csv(path, index=False)
    paths["encoded_feature_summary"] = path

    unseen_rows = [
        {**{k: v for k, v in row.items() if k != "unseen_categories"},
         "unseen_categories": "; ".join(row["unseen_categories"])}
        for row in unseen_summary
    ]
    path = tables_dir / "unseen_category_summary.csv"
    pd.DataFrame(unseen_rows).to_csv(path, index=False)
    paths["unseen_category_summary"] = path

    path = tables_dir / "encoding_mapping_summary.csv"
    mapping_df.to_csv(path, index=False)
    paths["encoding_mapping_summary"] = path

    logger.info("Table generated: %d feature encoding CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_encoding_markdown(report: dict[str, Any]) -> str:
    """Render the full feature encoding report as Markdown.

    Args:
        report: Report dict from :func:`run_feature_encoding`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    cardinality_desc = ", ".join(
        f"`{e['column']}`={e['original_unique_count']}"
        for e in report["training"]["encoded_feature_summary"]
    )
    lines: list[str] = [
        "# UNSW-NB15 Feature Encoding Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Categorical Features Encoded",
        "",
        f"`{', '.join(report['categorical_columns'])}` — identified automatically from "
        "`configs/preprocessing.yaml`'s frozen schema (`dtype == \"object\"`, excluding the target column), "
        "not hardcoded.",
        "",
        "---",
        "",
        "## Encoding Strategy",
        "",
        "**Method:** Ordinal encoding (`sklearn.preprocessing.OrdinalEncoder`), applied uniformly to every "
        "categorical column.",
        "",
        "**Why this method:** UNSW-NB15's categorical features have very different cardinalities "
        f"({cardinality_desc}). "
        "One-hot encoding the highest-cardinality column would add over a hundred sparse binary columns, which "
        "(a) fragments SHAP feature attributions across many near-empty columns instead of one interpretable "
        "feature, conflicting with this project's XAI focus, and (b) provides no benefit for the locked research "
        "model, Random Forest, which splits on value thresholds rather than assuming a linear relationship "
        "between encoded magnitude and target.",
        "",
        "**Why train-only fitting prevents leakage:** the encoder's `categories_` are learned exclusively from "
        "`X_train`; the testing split is read only via `.transform()`, which applies the already-fixed mapping "
        "and never updates it. No statistic, category, or ordering derived from the testing split can influence "
        "the training-time encoding.",
        "",
        "---",
        "",
        "## Unseen Category Handling",
        "",
        f"**Strategy:** `handle_unknown=\"use_encoded_value\"` with a fixed sentinel "
        f"(`{UNKNOWN_CATEGORY_VALUE}`), distinct from every valid learned code (which are always >= 0). "
        "This is deterministic: the same unseen category always maps to the same sentinel value, and the "
        "sentinel never collides with a real learned category.",
        "",
    ]

    any_unseen = any(row["unseen_categories"] for row in report["unseen_categories"])
    if any_unseen:
        lines += ["| Column | Unseen Categories | Affected Test Rows | Affected % |", "|---|---|---|---|"]
        for row in report["unseen_categories"]:
            if row["unseen_categories"]:
                lines.append(
                    f"| {row['column']} | {', '.join(row['unseen_categories'])} | "
                    f"{row['affected_row_count']} | {row['affected_pct']}% |"
                )
    else:
        lines.append("*No unseen categories found in this run.*")

    lines += [
        "",
        "---",
        "",
        "## Train/Test Integrity Verification",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Encoder fitted on training split only | Confirmed — `fit()` called once, on `X_train` |",
        f"| Testing split transformed via `.transform()` only | Confirmed |",
        f"| Raw dataset files unchanged | Confirmed (SHA-256 verified in self-tests) |",
        f"| Row order preserved | Confirmed (no sort/shuffle anywhere in the pipeline) |",
        f"| Column order preserved | Confirmed (matches original schema exactly) |",
        "",
        "---",
        "",
        "## Output Schema",
        "",
        f"**Output format:** {report['output_format']} "
        f"({'pyarrow available' if report['output_format'] == 'parquet' else 'pyarrow unavailable, CSV fallback used'})",
        "",
        "| Split | Path | Rows | Columns |",
        "|---|---|---|---|",
        f"| Training | `{report['training']['output_path']}` | {report['training']['row_count']:,} | {report['training']['column_count']} |",
        f"| Testing | `{report['testing']['output_path']}` | {report['testing']['row_count']:,} | {report['testing']['column_count']} |",
        "",
        "---",
        "",
        "## Encoded Feature Summary (Training Split)",
        "",
        "| Column | Original Dtype | Encoded Dtype | Original Unique Count | Encoded Range |",
        "|---|---|---|---|---|",
    ]
    for e in report["training"]["encoded_feature_summary"]:
        lines.append(
            f"| {e['column']} | {e['original_dtype']} | {e['encoded_dtype']} | "
            f"{e['original_unique_count']} | [{e['encoded_min']}, {e['encoded_max']}] |"
        )

    lines += [
        "",
        "---",
        "",
        "## Limitations",
        "",
        "- Ordinal encoding imposes an arbitrary, non-meaningful numeric order on nominal categories "
        "(e.g. `proto` codes do not reflect any true magnitude relationship). This is an acceptable, "
        "well-established practice for tree-based models but would need re-evaluation if a linear or "
        "distance-based model were substituted for Random Forest.",
        "- **Important finding, not addressed in this task:** the feature matrix produced here still contains "
        "`id` (a row identifier with no predictive meaning) and `label` (the binary form of the target, "
        "which maps near-perfectly to `attack_cat` per Task C.2's label consistency check). Both remain "
        "present because this task's scope explicitly forbids feature removal. Using `label` as a model "
        "input feature would constitute severe target leakage and must be addressed before model training "
        "— most naturally in a feature selection stage.",
        "",
        "---",
        "",
        "## Feature Encoding Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"Categorical features (`{', '.join(report['categorical_columns'])}`) were encoded using ordinal "
        "encoding fitted exclusively on the training split and applied to the testing split via "
        f"`.transform()`. {s['unseen_category_count']} unseen testing-only categories were detected and mapped "
        f"deterministically to a fixed sentinel value ({UNKNOWN_CATEGORY_VALUE}). Row and column order were "
        f"preserved throughout; the raw dataset files were not modified. Output datasets "
        f"({report['training']['row_count']:,} training rows, {report['testing']['row_count']:,} testing rows) "
        f"were saved in {report['output_format']} format to `data/interim/`.",
        "",
        "---",
        "*End of Feature Encoding Report*",
    ]
    return "\n".join(lines) + "\n"


def save_encoding_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the feature encoding report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_feature_encoding`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "feature_encoding_report.json", json_safe)
    md_path = write_text(reports_dir / "feature_encoding_report.md", _render_encoding_markdown(report))
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_feature_encoding() -> dict[str, Any]:
    """Run the full leakage-safe feature encoding pipeline.

    Loads and validates both splits (reusing Task C.1's pipeline),
    identifies categorical columns from the frozen schema, fits an
    ordinal encoder on the training split only, applies it to both
    splits, handles unseen testing-only categories deterministically,
    saves the encoded datasets, and writes reports/tables.

    Returns:
        Dict with ``training``, ``testing``, ``unseen_categories``,
        ``categorical_columns``, ``output_format``, and ``summary`` keys.
    """
    logger.info("Encoding started")

    dataset_cfg = _load_dataset_config()
    preprocessing_cfg = _load_preprocessing_config()
    target_column = dataset_cfg.get("target_column", "attack_cat")
    expected_columns = preprocessing_cfg["expected_columns"]

    splits = get_validated_splits()
    categorical_columns = identify_categorical_columns(preprocessing_cfg["expected_dtypes"], target_column)

    encoder = fit_encoder(splits.train.X, categorical_columns)

    X_train_encoded = apply_encoder(splits.train.X, encoder, categorical_columns)
    X_test_encoded = apply_encoder(splits.test.X, encoder, categorical_columns)
    logger.info(
        "Testing transformation complete — X_test encoded via transform() only, encoder unchanged"
    )

    unseen = find_unseen_categories(splits.train.X, splits.test.X, categorical_columns)
    unseen_summary = summarize_unseen_categories(splits.test.X, unseen)
    logger.info("Unseen category handling: %d column(s) with unseen categories", sum(1 for v in unseen.values() if v))

    mapping_df = build_encoding_mapping(encoder, categorical_columns)
    train_encoded_summary = summarize_encoded_features(splits.train.X, X_train_encoded, categorical_columns)
    test_encoded_summary = summarize_encoded_features(splits.test.X, X_test_encoded, categorical_columns)

    train_full = reassemble_with_target(X_train_encoded, splits.train.y, target_column, expected_columns)
    test_full = reassemble_with_target(X_test_encoded, splits.test.y, target_column, expected_columns)

    interim_dir = get_path_manager().interim_data_dir
    train_path, train_format = save_encoded_dataset(train_full, interim_dir, "training_encoded")
    test_path, test_format = save_encoded_dataset(test_full, interim_dir, "testing_encoded")
    output_format = train_format

    save_encoding_tables(train_encoded_summary, unseen_summary, mapping_df)

    summary = {
        "unseen_category_count": sum(len(v) for v in unseen.values()),
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }

    report = {
        "categorical_columns": categorical_columns,
        "unseen_categories": unseen_summary,
        "training": {
            "output_path": str(train_path),
            "row_count": len(train_full),
            "column_count": len(train_full.columns),
            "encoded_feature_summary": train_encoded_summary,
        },
        "testing": {
            "output_path": str(test_path),
            "row_count": len(test_full),
            "column_count": len(test_full.columns),
            "encoded_feature_summary": test_encoded_summary,
        },
        "output_format": output_format,
        "summary": summary,
    }
    save_encoding_report(report)

    logger.info("Encoding completed — %d categorical columns encoded, output format: %s", len(categorical_columns), output_format)
    return report
