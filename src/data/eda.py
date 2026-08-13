"""Exploratory Data Analysis for the UNSW-NB15 training and testing sets.

Strictly read-only and descriptive: loads each CSV exactly as
distributed and computes statistical summaries, correlations, and
visualisations. Never cleans, encodes, scales, balances, merges, or
removes anything from either dataset — those decisions belong to the
preprocessing stage (Phase C), not here.

Training and testing statistics are always computed independently.
Where the dataset's class count is small enough to stay readable
(class distribution, percentage, imbalance ratio), figures show both
splits side by side in one image — never by combining the underlying
rows, only by placing two independently-computed panels together.
For denser analyses (correlation, full-feature distributions,
categorical frequencies, outliers) the headline figure focuses on the
training set, consistent with the project's established convention
(Milestone A and Task B.2 also centre the training split); the
testing split's statistics are still computed independently and saved
as CSV tables.

Usage::

    from src.data.eda import run_eda

    result = run_eda()

Design decisions
~~~~~~~~~~~~~~~~
* ``id`` is excluded from correlation, distribution, and outlier
  analysis — it is a row identifier, not a network-flow feature, and
  including it would produce a meaningless high-variance/high-IR
  artefact (same reasoning applied when regenerating Milestone A's
  figures).
* Skewness/kurtosis thresholds and the IQR multiplier for outlier
  detection use well-established statistical conventions (Bulmer's
  skewness classification; Tukey's 1.5x/3x IQR fences) rather than
  project-specific hyperparameters, so they are documented constants
  rather than YAML config values.
* Matplotlib only, no seaborn, per this task's explicit instruction
  to avoid unnecessary dependencies (seaborn remains available in
  requirements.txt for future stages).
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.data.dataset_acquisition import verify_dataset_ready
from src.data.dataset_profile import categorize_features, load_dataset
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_FIGURE_DPI = 300

# Bulmer's skewness classification thresholds.
_SKEW_HIGH_THRESHOLD = 1.0
_SKEW_MODERATE_THRESHOLD = 0.5

# Excess kurtosis threshold for "heavy-tailed" (normal distribution = 0).
_KURTOSIS_HEAVY_TAIL_THRESHOLD = 3.0

# Tukey's fences for outlier detection.
_IQR_OUTLIER_MULTIPLIER = 1.5
_IQR_EXTREME_OUTLIER_MULTIPLIER = 3.0

# Pearson |r| threshold above which a feature pair is "highly correlated".
_HIGH_CORRELATION_THRESHOLD = 0.8

_ID_COLUMN = "id"


def _set_publication_style() -> None:
    """Apply consistent, publication-quality matplotlib defaults."""
    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.labelweight": "bold",
        "figure.titlesize": 14,
        "figure.titleweight": "bold",
        "savefig.dpi": _FIGURE_DPI,
        "savefig.bbox": "tight",
    })


# ── configuration & loading ─────────────────────────────────

def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml``.

    Returns:
        Parsed dataset configuration dictionary.
    """
    config_path = get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME
    return read_yaml(config_path)


def load_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the training and testing splits independently.

    Returns:
        Tuple of ``(train_df, test_df)``.

    Raises:
        RuntimeError: If the dataset is not verified ready (see
            :func:`src.data.dataset_acquisition.verify_dataset_ready`).
    """
    if not verify_dataset_ready():
        raise RuntimeError(
            "Dataset not ready — run scripts/01_dataset_acquisition.py first"
        )

    dataset_cfg = _load_dataset_config()
    raw_dir = get_path_manager().raw_data_dir
    files_by_split = {
        entry["split"]: entry["filename"] for entry in dataset_cfg.get("expected_files", [])
    }

    train_df = load_dataset(raw_dir / files_by_split["training"])
    test_df = load_dataset(raw_dir / files_by_split["testing"])
    return train_df, test_df


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return numerical feature columns, excluding the row identifier.

    Args:
        df: Loaded dataset.

    Returns:
        Column names categorised as numerical, minus ``id``.
    """
    cats = categorize_features(df)
    return [c for c in cats["numerical"] if c != _ID_COLUMN]


# ══════════════════════════════════════════════════════════════
# 1. Class distribution analysis
# ══════════════════════════════════════════════════════════════

def compute_class_distribution(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
    """Compute class counts, percentages, and imbalance ratio.

    Args:
        df: Loaded dataset (single split).
        target_column: Name of the target column.

    Returns:
        ``DataFrame`` with columns ``class_name``, ``count``, ``pct``,
        ``imbalance_ratio``, sorted by descending count.
    """
    counts = df[target_column].value_counts().sort_values(ascending=False)
    count_values = counts.to_numpy(dtype=np.int64)
    total = len(df)
    majority = int(count_values[0])

    return pd.DataFrame({
        "class_name": counts.index.tolist(),
        "count": count_values,
        "pct": np.round(100 * count_values / total, 4),
        "imbalance_ratio": np.round(majority / count_values, 4),
    })


def plot_class_distribution(
    train_dist: pd.DataFrame, test_dist: pd.DataFrame, save_path: Path
) -> Path:
    """Plot per-class instance counts for both splits, log scale.

    Args:
        train_dist: Output of :func:`compute_class_distribution` (train).
        test_dist: Output of :func:`compute_class_distribution` (test).
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, dist, title in ((axes[0], train_dist, "Training Set"), (axes[1], test_dist, "Testing Set")):
        colors = plt.get_cmap("tab10")(np.linspace(0, 1, len(dist)))
        bars = ax.bar(dist["class_name"], dist["count"], color=colors)
        ax.set_yscale("log")
        ax.set_ylabel("Instance Count (log scale)")
        ax.set_xlabel("Attack Category")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=30)
        for bar, val in zip(bars, dist["count"]):
            ax.text(bar.get_x() + bar.get_width() / 2, val * 1.05, f"{val:,}", ha="center", va="bottom", fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("UNSW-NB15 — Per-Class Instance Distribution")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_class_percentage(
    train_dist: pd.DataFrame, test_dist: pd.DataFrame, save_path: Path
) -> Path:
    """Plot per-class percentage share for both splits.

    Args:
        train_dist: Output of :func:`compute_class_distribution` (train).
        test_dist: Output of :func:`compute_class_distribution` (test).
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, dist, title in ((axes[0], train_dist, "Training Set"), (axes[1], test_dist, "Testing Set")):
        colors = plt.get_cmap("tab10")(np.linspace(0, 1, len(dist)))
        bars = ax.bar(dist["class_name"], dist["pct"], color=colors)
        ax.set_ylabel("Percentage of Total (%)")
        ax.set_xlabel("Attack Category")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=30)
        for bar, val in zip(bars, dist["pct"]):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.3, f"{val:.2f}%", ha="center", va="bottom", fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("UNSW-NB15 — Per-Class Percentage Share")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_imbalance_ratio(
    train_dist: pd.DataFrame, test_dist: pd.DataFrame, save_path: Path
) -> Path:
    """Plot per-class imbalance ratio for both splits, horizontal bars.

    Args:
        train_dist: Output of :func:`compute_class_distribution` (train).
        test_dist: Output of :func:`compute_class_distribution` (test).
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for ax, dist, title in ((axes[0], train_dist, "Training Set"), (axes[1], test_dist, "Testing Set")):
        sorted_dist = dist.sort_values("imbalance_ratio")
        colors = ["#d62728" if ir > 10 else "#1f77b4" for ir in sorted_dist["imbalance_ratio"]]
        bars = ax.barh(sorted_dist["class_name"], sorted_dist["imbalance_ratio"], color=colors)
        ax.set_xlabel("Imbalance Ratio (majority / class count)")
        ax.set_title(title)
        max_ir = sorted_dist["imbalance_ratio"].max()
        for bar, val in zip(bars, sorted_dist["imbalance_ratio"]):
            ax.text(bar.get_width() + max_ir * 0.01, bar.get_y() + bar.get_height() / 2, f"{val:.1f}", va="center", fontsize=8)
        ax.grid(axis="x", alpha=0.3)

    from matplotlib.patches import Patch
    fig.legend(
        handles=[Patch(color="#d62728", label="Severe (IR > 10)"), Patch(color="#1f77b4", label="Moderate (IR <= 10)")],
        loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.02),
    )
    fig.suptitle("UNSW-NB15 — Per-Class Imbalance Ratio")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# 2 & 6. Numerical feature exploration / distribution characteristics
# ══════════════════════════════════════════════════════════════

def compute_distribution_characteristics(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """Compute skewness and kurtosis for every numerical column.

    Classifies each feature using Bulmer's skewness convention
    (|skew| < 0.5 approximately symmetric, 0.5-1.0 moderately skewed,
    > 1.0 highly skewed) and flags heavy-tailed features where excess
    kurtosis exceeds :data:`_KURTOSIS_HEAVY_TAIL_THRESHOLD`.

    Args:
        df: Loaded dataset.
        numeric_columns: Columns to analyse.

    Returns:
        ``DataFrame`` with ``column``, ``skewness``, ``kurtosis``,
        ``skew_category``, ``heavy_tailed`` columns.
    """
    rows = []
    for col in numeric_columns:
        skew = float(df[col].skew())
        kurt = float(df[col].kurt())

        if abs(skew) > _SKEW_HIGH_THRESHOLD:
            skew_category = "highly_skewed"
        elif abs(skew) > _SKEW_MODERATE_THRESHOLD:
            skew_category = "moderately_skewed"
        else:
            skew_category = "approximately_symmetric"

        rows.append({
            "column": col,
            "skewness": round(skew, 4),
            "kurtosis": round(kurt, 4),
            "skew_category": skew_category,
            "heavy_tailed": kurt > _KURTOSIS_HEAVY_TAIL_THRESHOLD,
        })

    return pd.DataFrame(rows)


def detect_outliers_iqr(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """Detect outliers using Tukey's IQR fences (robust to non-normality).

    A value is a mild outlier beyond ``Q1 - 1.5*IQR`` / ``Q3 + 1.5*IQR``
    and an extreme outlier beyond ``Q1 - 3*IQR`` / ``Q3 + 3*IQR``.
    Also reports the coefficient of variation (std / mean) as a
    dispersion indicator.

    Args:
        df: Loaded dataset.
        numeric_columns: Columns to analyse.

    Returns:
        ``DataFrame`` with per-column outlier counts/percentages and
        coefficient of variation.
    """
    n_rows = len(df)
    rows = []
    for col in numeric_columns:
        series = df[col]
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1

        mild_lo, mild_hi = q1 - _IQR_OUTLIER_MULTIPLIER * iqr, q3 + _IQR_OUTLIER_MULTIPLIER * iqr
        ext_lo, ext_hi = q1 - _IQR_EXTREME_OUTLIER_MULTIPLIER * iqr, q3 + _IQR_EXTREME_OUTLIER_MULTIPLIER * iqr

        mild_count = int(((series < mild_lo) | (series > mild_hi)).sum())
        extreme_count = int(((series < ext_lo) | (series > ext_hi)).sum())

        mean = series.mean()
        cv = float(series.std() / mean) if mean != 0 else float("nan")

        rows.append({
            "column": col,
            "outlier_count": mild_count,
            "outlier_pct": round(100 * mild_count / n_rows, 4) if n_rows else 0.0,
            "extreme_outlier_count": extreme_count,
            "extreme_outlier_pct": round(100 * extreme_count / n_rows, 4) if n_rows else 0.0,
            "coefficient_of_variation": round(cv, 4) if not np.isnan(cv) else None,
        })

    return pd.DataFrame(rows)


def plot_numerical_distributions(
    df: pd.DataFrame, skew_df: pd.DataFrame, save_path: Path, top_n: int = 12
) -> Path:
    """Plot histograms for the most skewed numerical features.

    Args:
        df: Loaded dataset (training set, by convention).
        skew_df: Output of :func:`compute_distribution_characteristics`.
        save_path: PNG destination.
        top_n: Number of features to display, ranked by |skewness|.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    top_cols = skew_df.reindex(skew_df["skewness"].abs().sort_values(ascending=False).index).head(top_n)["column"].tolist()

    n_cols = 4
    n_rows = -(-len(top_cols) // n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3.5 * n_rows))
    axes_flat = axes.flat if hasattr(axes, "flat") else [axes]

    for ax, col in zip(axes_flat, top_cols):
        series = df[col]
        lo, hi = series.quantile(0.01), series.quantile(0.99)
        clipped = series.clip(lo, hi)
        ax.hist(clipped, bins=30, color="seagreen", edgecolor="white", linewidth=0.3)
        ax.set_title(col, fontsize=10)
        ax.set_ylabel("Count")
        ax.tick_params(labelsize=7)

    for ax in list(axes_flat)[len(top_cols):]:
        ax.axis("off")

    fig.suptitle(f"UNSW-NB15 (Training Set) — Top {top_n} Most Skewed Numerical Features\n(1st–99th percentile clipped)")
    plt.tight_layout(rect=(0, 0, 1, 0.95))
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_outlier_summary(
    df: pd.DataFrame, outlier_df: pd.DataFrame, save_path: Path, top_n: int = 10
) -> Path:
    """Plot boxplots for the features with the highest outlier percentage.

    Args:
        df: Loaded dataset (training set, by convention).
        outlier_df: Output of :func:`detect_outliers_iqr`.
        save_path: PNG destination.
        top_n: Number of features to display, ranked by outlier %.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    top_cols = outlier_df.sort_values("outlier_pct", ascending=False).head(top_n)["column"].tolist()
    pct_by_col = outlier_df.set_index("column")["outlier_pct"]

    n_cols = 5
    n_rows = -(-len(top_cols) // n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3.2 * n_cols, 4 * n_rows))
    axes_flat = axes.flat if hasattr(axes, "flat") else [axes]

    for ax, col in zip(axes_flat, top_cols):
        series = df[col].clip(df[col].quantile(0.01), df[col].quantile(0.99))
        box = ax.boxplot([series], patch_artist=True, flierprops={"markersize": 3, "alpha": 0.5})
        for patch in box["boxes"]:
            patch.set_facecolor("#ff7f0e")
            patch.set_alpha(0.6)
        ax.set_title(f"{col}\n({pct_by_col[col]:.1f}% outliers)", fontsize=9)
        ax.set_xticks([])
        ax.tick_params(labelsize=7)
        ax.grid(axis="y", alpha=0.3)

    for ax in list(axes_flat)[len(top_cols):]:
        ax.axis("off")

    fig.suptitle(
        f"UNSW-NB15 (Training Set) — Top {top_n} Features by Outlier Percentage (Tukey's IQR Method)\n"
        "(1st–99th percentile clipped; each panel has an independent y-axis scale)"
    )
    plt.tight_layout(rect=(0, 0, 1, 0.93))
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# 3. Categorical feature exploration
# ══════════════════════════════════════════════════════════════

_CATEGORICAL_COLUMNS = ("proto", "service", "state")


def compute_categorical_frequency(df: pd.DataFrame, categorical_columns: tuple[str, ...]) -> dict[str, pd.DataFrame]:
    """Build a frequency table for each categorical column.

    Args:
        df: Loaded dataset.
        categorical_columns: Columns to analyse (``proto``, ``service``, ``state``).

    Returns:
        Mapping of column name to a ``DataFrame`` with ``category``,
        ``count``, ``pct``, sorted by descending count.
    """
    total = len(df)
    tables: dict[str, pd.DataFrame] = {}

    for col in categorical_columns:
        counts = df[col].value_counts().sort_values(ascending=False)
        tables[col] = pd.DataFrame({
            "category": counts.index.tolist(),
            "count": counts.to_numpy(dtype=np.int64),
            "pct": np.round(100 * counts.to_numpy(dtype=np.int64) / total, 4),
        })

    return tables


def plot_categorical_distributions(
    freq_tables: dict[str, pd.DataFrame], save_path: Path, top_n: int = 10
) -> Path:
    """Plot top-N category bar charts for each categorical feature.

    Categories beyond *top_n* are aggregated into an ``"other"`` bar so
    high-cardinality features (e.g. ``proto`` has 130+ values) remain
    readable.

    Args:
        freq_tables: Output of :func:`compute_categorical_frequency`.
        save_path: PNG destination.
        top_n: Number of individual categories to show per feature.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    fig, axes = plt.subplots(1, len(freq_tables), figsize=(6 * len(freq_tables), 6))
    if len(freq_tables) == 1:
        axes = [axes]

    for ax, (col, table) in zip(axes, freq_tables.items()):
        top = table.head(top_n)
        if len(table) > top_n:
            other_count = table["count"].iloc[top_n:].sum()
            other_pct = table["pct"].iloc[top_n:].sum()
            top = pd.concat([top, pd.DataFrame([{"category": "other", "count": other_count, "pct": other_pct}])])

        colors = plt.get_cmap("tab20")(np.linspace(0, 1, len(top)))
        bars = ax.bar(top["category"].astype(str), top["count"], color=colors)
        ax.set_title(f"`{col}`")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        for bar, val in zip(bars, top["count"]):
            ax.text(bar.get_x() + bar.get_width() / 2, val, f"{val:,}", ha="center", va="bottom", fontsize=7, rotation=90)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("UNSW-NB15 (Training Set) — Categorical Feature Distributions")
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def identify_dominant_categories(freq_tables: dict[str, pd.DataFrame], dominance_threshold: float = 50.0) -> dict[str, str]:
    """Identify the single dominant category per feature, if any.

    Args:
        freq_tables: Output of :func:`compute_categorical_frequency`.
        dominance_threshold: Minimum percentage share for a category
            to be considered dominant.

    Returns:
        Mapping of column name to its dominant category name, or
        ``"none"`` if no single category exceeds the threshold.
    """
    dominant: dict[str, str] = {}
    for col, table in freq_tables.items():
        top_pct = table["pct"].iloc[0]
        dominant[col] = table["category"].iloc[0] if top_pct >= dominance_threshold else "none"
    return dominant


# ══════════════════════════════════════════════════════════════
# 4. Correlation analysis
# ══════════════════════════════════════════════════════════════

def compute_correlation_matrix(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """Compute the Pearson correlation matrix for numerical features.

    Args:
        df: Loaded dataset.
        numeric_columns: Columns to correlate.

    Returns:
        Square ``DataFrame`` of pairwise Pearson correlation coefficients.
    """
    return df[numeric_columns].corr(method="pearson")


def find_highly_correlated_pairs(
    corr_matrix: pd.DataFrame, threshold: float = _HIGH_CORRELATION_THRESHOLD
) -> pd.DataFrame:
    """Identify feature pairs with |Pearson r| above *threshold*.

    Args:
        corr_matrix: Output of :func:`compute_correlation_matrix`.
        threshold: Absolute correlation threshold.

    Returns:
        ``DataFrame`` with ``feature_1``, ``feature_2``, ``correlation``,
        one row per pair (no duplicate or self pairs), sorted by
        descending absolute correlation.
    """
    cols = corr_matrix.columns.tolist()
    pairs = []
    for i, col_a in enumerate(cols):
        for col_b in cols[i + 1:]:
            r = float(corr_matrix.loc[col_a, col_b])
            if abs(r) >= threshold:
                pairs.append({"feature_1": col_a, "feature_2": col_b, "correlation": round(r, 4)})

    result = pd.DataFrame(pairs)
    if not result.empty:
        result = result.reindex(result["correlation"].abs().sort_values(ascending=False).index).reset_index(drop=True)
    return result


def plot_correlation_heatmap(corr_matrix: pd.DataFrame, save_path: Path) -> Path:
    """Plot a Pearson correlation heatmap for the training set's numerical features.

    Args:
        corr_matrix: Output of :func:`compute_correlation_matrix`.
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    n = len(corr_matrix)
    fig, ax = plt.subplots(figsize=(max(10, n * 0.35), max(9, n * 0.35)))

    im = ax.imshow(corr_matrix.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(corr_matrix.columns, rotation=90, fontsize=7)
    ax.set_yticklabels(corr_matrix.columns, fontsize=7)
    ax.set_title("UNSW-NB15 (Training Set) — Pearson Correlation Heatmap (Numerical Features)")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson Correlation Coefficient")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# 7. Feature relationship exploration
# ══════════════════════════════════════════════════════════════

def select_relationship_pairs(corr_pairs: pd.DataFrame, max_pairs: int = 4) -> list[tuple[str, str]]:
    """Select the most informative feature pairs for scatter plots.

    Args:
        corr_pairs: Output of :func:`find_highly_correlated_pairs`,
            already sorted by descending absolute correlation.
        max_pairs: Maximum number of pairs to select.

    Returns:
        List of ``(feature_1, feature_2)`` tuples.
    """
    if corr_pairs.empty:
        return []
    top = corr_pairs.head(max_pairs)
    return list(zip(top["feature_1"], top["feature_2"]))


def plot_feature_relationships(
    df: pd.DataFrame, pairs: list[tuple[str, str]], target_column: str, save_path: Path
) -> Path:
    """Plot scatter plots for the most informative correlated feature pairs.

    Points are coloured by binary label (Normal vs. Attack) so the
    relationship's relevance to the classification task is visible
    without performing any classification here.

    Args:
        df: Loaded dataset (training set, by convention).
        pairs: Output of :func:`select_relationship_pairs`.
        target_column: Target column used to derive binary colouring.
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    if not pairs:
        pairs = [(df.columns[0], df.columns[1])]

    n = len(pairs)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5.5))
    if n == 1:
        axes = [axes]

    is_normal = df[target_column] == "Normal"
    sample = df.sample(n=min(5000, len(df)), random_state=42)
    sample_is_normal = is_normal.loc[sample.index]

    for ax, (col_a, col_b) in zip(axes, pairs):
        x_lo, x_hi = sample[col_a].quantile(0.01), sample[col_a].quantile(0.99)
        y_lo, y_hi = sample[col_b].quantile(0.01), sample[col_b].quantile(0.99)
        ax.scatter(
            sample.loc[sample_is_normal, col_a].clip(x_lo, x_hi),
            sample.loc[sample_is_normal, col_b].clip(y_lo, y_hi),
            s=6, alpha=0.4, color="#1f77b4", label="Normal",
        )
        ax.scatter(
            sample.loc[~sample_is_normal, col_a].clip(x_lo, x_hi),
            sample.loc[~sample_is_normal, col_b].clip(y_lo, y_hi),
            s=6, alpha=0.4, color="#d62728", label="Attack",
        )
        ax.set_xlabel(col_a)
        ax.set_ylabel(col_b)
        ax.set_title(f"{col_a} vs {col_b}")
        ax.legend(fontsize=8, markerscale=2)
        ax.grid(alpha=0.3)

    fig.suptitle("UNSW-NB15 (Training Set, 5,000-row sample) — Most Correlated Feature Pairs")
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# 8. Research observations
# ══════════════════════════════════════════════════════════════

def generate_research_observations(
    train_dist: pd.DataFrame,
    skew_df: pd.DataFrame,
    outlier_df: pd.DataFrame,
    corr_pairs: pd.DataFrame,
    dominant_categories: dict[str, str],
) -> list[str]:
    """Generate objective, evidence-based observations from the EDA results.

    Reports facts only — no preprocessing or modelling recommendations.

    Args:
        train_dist: Training set class distribution.
        skew_df: Training set distribution characteristics.
        outlier_df: Training set outlier summary.
        corr_pairs: Training set highly correlated feature pairs.
        dominant_categories: Output of :func:`identify_dominant_categories`.

    Returns:
        List of observation strings.
    """
    observations: list[str] = []

    most_imbalanced = train_dist.sort_values("imbalance_ratio", ascending=False).iloc[0]
    n_severe = int((train_dist["imbalance_ratio"] > 10).sum())
    observations.append(
        f"Severe class imbalance is confirmed in the training set: imbalance ratios range from 1.0 (Normal) "
        f"to {most_imbalanced['imbalance_ratio']:.1f}x ({most_imbalanced['class_name']}), with {n_severe} of 10 "
        "classes exceeding an imbalance ratio of 10."
    )

    n_highly_skewed = int((skew_df["skew_category"] == "highly_skewed").sum())
    most_skewed = skew_df.reindex(skew_df["skewness"].abs().sort_values(ascending=False).index).iloc[0]
    observations.append(
        f"{n_highly_skewed} of {len(skew_df)} numerical features are highly skewed (|skewness| > 1.0); "
        f"the most skewed feature is `{most_skewed['column']}` (skewness = {most_skewed['skewness']:.2f})."
    )

    n_heavy_tailed = int(skew_df["heavy_tailed"].sum())
    observations.append(
        f"{n_heavy_tailed} of {len(skew_df)} numerical features are heavy-tailed (excess kurtosis > "
        f"{_KURTOSIS_HEAVY_TAIL_THRESHOLD:.0f}), indicating traffic-volume features contain extreme values "
        "far more frequently than a normal distribution would predict."
    )

    for col, dominant in dominant_categories.items():
        if dominant != "none":
            observations.append(f"The `{col}` feature is dominated by a single category: `{dominant}`.")

    if not corr_pairs.empty:
        top_pair = corr_pairs.iloc[0]
        observations.append(
            f"{len(corr_pairs)} numerical feature pairs exceed |Pearson r| = {_HIGH_CORRELATION_THRESHOLD}, "
            f"indicating redundant traffic statistics; the strongest pair is `{top_pair['feature_1']}` and "
            f"`{top_pair['feature_2']}` (r = {top_pair['correlation']:.2f})."
        )
    else:
        observations.append(
            f"No numerical feature pairs exceed |Pearson r| = {_HIGH_CORRELATION_THRESHOLD}."
        )

    top_outlier = outlier_df.sort_values("outlier_pct", ascending=False).iloc[0]
    observations.append(
        f"The feature with the highest outlier rate (Tukey's 1.5x IQR method) is `{top_outlier['column']}` "
        f"at {top_outlier['outlier_pct']:.2f}% of rows flagged as outliers."
    )

    return observations


# ══════════════════════════════════════════════════════════════
# Orchestration: per-split analysis bundle
# ══════════════════════════════════════════════════════════════

def _analyse_split(df: pd.DataFrame, target_column: str) -> dict[str, Any]:
    """Run every independent (non-figure) analysis for a single split.

    Args:
        df: Loaded dataset for one split.
        target_column: Target column name.

    Returns:
        Dict bundling class distribution, distribution characteristics,
        outliers, categorical frequency, and correlation results.
    """
    numeric_cols = _numeric_columns(df)

    class_dist = compute_class_distribution(df, target_column)
    skew_df = compute_distribution_characteristics(df, numeric_cols)
    outlier_df = detect_outliers_iqr(df, numeric_cols)
    cat_freq = compute_categorical_frequency(df, _CATEGORICAL_COLUMNS)
    corr_matrix = compute_correlation_matrix(df, numeric_cols)
    corr_pairs = find_highly_correlated_pairs(corr_matrix)

    return {
        "class_distribution": class_dist,
        "distribution_characteristics": skew_df,
        "outliers": outlier_df,
        "categorical_frequency": cat_freq,
        "correlation_matrix": corr_matrix,
        "correlation_pairs": corr_pairs,
        "numeric_columns": numeric_cols,
    }


def save_eda_tables(train_bundle: dict[str, Any], test_bundle: dict[str, Any]) -> dict[str, Path]:
    """Save every EDA CSV table, with a ``split`` column distinguishing
    independently-computed training/testing rows.

    Args:
        train_bundle: Output of :func:`_analyse_split` for training.
        test_bundle: Output of :func:`_analyse_split` for testing.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    def _tag(df: pd.DataFrame, split: str) -> pd.DataFrame:
        out = df.copy()
        out.insert(0, "split", split)
        return out

    combined_dist = pd.concat([
        _tag(train_bundle["class_distribution"], "training"),
        _tag(test_bundle["class_distribution"], "testing"),
    ], ignore_index=True)
    path = tables_dir / "eda_class_distribution.csv"
    combined_dist.to_csv(path, index=False)
    paths["class_distribution"] = path

    combined_skew = pd.concat([
        _tag(train_bundle["distribution_characteristics"], "training"),
        _tag(test_bundle["distribution_characteristics"], "testing"),
    ], ignore_index=True)
    path = tables_dir / "eda_distribution_characteristics.csv"
    combined_skew.to_csv(path, index=False)
    paths["distribution_characteristics"] = path

    combined_outliers = pd.concat([
        _tag(train_bundle["outliers"], "training"),
        _tag(test_bundle["outliers"], "testing"),
    ], ignore_index=True)
    path = tables_dir / "eda_outlier_summary.csv"
    combined_outliers.to_csv(path, index=False)
    paths["outlier_summary"] = path

    cat_rows = []
    for split, bundle in (("training", train_bundle), ("testing", test_bundle)):
        for feature, table in bundle["categorical_frequency"].items():
            tagged = table.copy()
            tagged.insert(0, "feature", feature)
            tagged.insert(0, "split", split)
            cat_rows.append(tagged)
    path = tables_dir / "eda_categorical_frequency.csv"
    pd.concat(cat_rows, ignore_index=True).to_csv(path, index=False)
    paths["categorical_frequency"] = path

    combined_pairs = pd.concat([
        _tag(train_bundle["correlation_pairs"], "training") if not train_bundle["correlation_pairs"].empty
        else pd.DataFrame(columns=["split", "feature_1", "feature_2", "correlation"]),
        _tag(test_bundle["correlation_pairs"], "testing") if not test_bundle["correlation_pairs"].empty
        else pd.DataFrame(columns=["split", "feature_1", "feature_2", "correlation"]),
    ], ignore_index=True)
    path = tables_dir / "eda_correlation_pairs.csv"
    combined_pairs.to_csv(path, index=False)
    paths["correlation_pairs"] = path

    path = tables_dir / "eda_correlation_matrix_training.csv"
    train_bundle["correlation_matrix"].to_csv(path)
    paths["correlation_matrix_training"] = path

    path = tables_dir / "eda_correlation_matrix_testing.csv"
    test_bundle["correlation_matrix"].to_csv(path)
    paths["correlation_matrix_testing"] = path

    logger.info("Table generated: %d EDA CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering & summary
# ══════════════════════════════════════════════════════════════

def generate_eda_summary(
    train_bundle: dict[str, Any],
    test_bundle: dict[str, Any],
    observations: list[str],
    dominant_categories: dict[str, str],
) -> dict[str, Any]:
    """Build a concise EDA summary suitable for the paper's text.

    Args:
        train_bundle: Output of :func:`_analyse_split` for training.
        test_bundle: Output of :func:`_analyse_split` for testing.
        observations: Output of :func:`generate_research_observations`.
        dominant_categories: Output of :func:`identify_dominant_categories`.

    Returns:
        Flat summary dict covering imbalance, protocols, distribution
        characteristics, correlation, and outliers.
    """
    train_dist = train_bundle["class_distribution"]
    skew_df = train_bundle["distribution_characteristics"]
    corr_pairs = train_bundle["correlation_pairs"]
    outlier_df = train_bundle["outliers"]

    most_imbalanced = train_dist.sort_values("imbalance_ratio", ascending=False).iloc[0]
    most_skewed = skew_df.reindex(skew_df["skewness"].abs().sort_values(ascending=False).index).iloc[0]
    top_outlier = outlier_df.sort_values("outlier_pct", ascending=False).iloc[0]
    strongest_pair = corr_pairs.iloc[0].to_dict() if not corr_pairs.empty else None

    return {
        "max_imbalance_ratio": float(most_imbalanced["imbalance_ratio"]),
        "max_imbalance_class": str(most_imbalanced["class_name"]),
        "classes_with_severe_imbalance": int((train_dist["imbalance_ratio"] > 10).sum()),
        "dominant_protocols": {k: v for k, v in dominant_categories.items() if v != "none"},
        "num_highly_skewed_features": int((skew_df["skew_category"] == "highly_skewed").sum()),
        "most_skewed_feature": str(most_skewed["column"]),
        "most_skewed_value": float(most_skewed["skewness"]),
        "num_heavy_tailed_features": int(skew_df["heavy_tailed"].sum()),
        "num_highly_correlated_pairs": int(len(corr_pairs)),
        "strongest_correlation_pair": strongest_pair,
        "highest_outlier_feature": str(top_outlier["column"]),
        "highest_outlier_pct": float(top_outlier["outlier_pct"]),
        "observations": observations,
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }


def _render_eda_markdown(report: dict[str, Any]) -> str:
    """Render the full EDA report as Markdown.

    Args:
        report: Report dict from :func:`run_eda`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    lines: list[str] = [
        "# UNSW-NB15 Exploratory Data Analysis Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## 1. Class Distribution Analysis",
        "",
        "See `class_distribution.png`, `class_percentage.png`, `imbalance_ratio.png` "
        "and `outputs/tables/eda_class_distribution.csv`.",
        "",
        f"- Maximum imbalance ratio: **{s['max_imbalance_ratio']}x** (`{s['max_imbalance_class']}`)",
        f"- Classes with severe imbalance (IR > 10): **{s['classes_with_severe_imbalance']}**",
        "",
        "---",
        "",
        "## 2 & 6. Numerical Feature Exploration & Distribution Characteristics",
        "",
        "See `numerical_distributions.png` and `outputs/tables/eda_distribution_characteristics.csv`.",
        "",
        f"- Highly skewed features (|skewness| > 1.0): **{s['num_highly_skewed_features']}**",
        f"- Most skewed feature: `{s['most_skewed_feature']}` (skewness = {s['most_skewed_value']:.2f})",
        f"- Heavy-tailed features (excess kurtosis > {_KURTOSIS_HEAVY_TAIL_THRESHOLD:.0f}): "
        f"**{s['num_heavy_tailed_features']}**",
        "",
        "---",
        "",
        "## 3. Categorical Feature Exploration",
        "",
        "See `categorical_distributions.png` and `outputs/tables/eda_categorical_frequency.csv`.",
        "",
    ]
    if s["dominant_protocols"]:
        for col, val in s["dominant_protocols"].items():
            lines.append(f"- Dominant category for `{col}`: `{val}`")
    else:
        lines.append("- No feature has a single dominant category exceeding 50%.")

    lines += [
        "",
        "---",
        "",
        "## 4. Correlation Analysis",
        "",
        "See `correlation_heatmap.png` and `outputs/tables/eda_correlation_pairs.csv`.",
        "",
        f"- Highly correlated pairs (|r| > {_HIGH_CORRELATION_THRESHOLD}): **{s['num_highly_correlated_pairs']}**",
    ]
    if s["strongest_correlation_pair"]:
        p = s["strongest_correlation_pair"]
        lines.append(f"- Strongest pair: `{p['feature_1']}` & `{p['feature_2']}` (r = {p['correlation']})")

    lines += [
        "",
        "---",
        "",
        "## 5. Outlier Analysis",
        "",
        "See `outlier_summary.png` and `outputs/tables/eda_outlier_summary.csv` (Tukey's IQR method).",
        "",
        f"- Highest outlier rate: `{s['highest_outlier_feature']}` ({s['highest_outlier_pct']:.2f}% of rows)",
        "",
        "---",
        "",
        "## 7. Feature Relationship Exploration",
        "",
        "See `feature_relationships.png` — scatter plots of the most highly correlated feature pairs, "
        "coloured by binary label (Normal vs. Attack), training set 5,000-row sample.",
        "",
        "---",
        "",
        "## 8. Research Observations",
        "",
    ]
    lines.extend(f"{i}. {obs}" for i, obs in enumerate(s["observations"], start=1))

    lines += [
        "",
        "---",
        "",
        "## EDA Summary (Methodology Section)",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Maximum Imbalance Ratio | {s['max_imbalance_ratio']}x (`{s['max_imbalance_class']}`) |",
        f"| Classes with Severe Imbalance | {s['classes_with_severe_imbalance']} |",
        f"| Highly Skewed Features | {s['num_highly_skewed_features']} |",
        f"| Heavy-Tailed Features | {s['num_heavy_tailed_features']} |",
        f"| Highly Correlated Pairs | {s['num_highly_correlated_pairs']} |",
        f"| Feature with Highest Outlier Rate | `{s['highest_outlier_feature']}` ({s['highest_outlier_pct']:.2f}%) |",
        "",
        "---",
        "*End of Exploratory Data Analysis Report*",
    ]
    return "\n".join(lines) + "\n"


def save_eda_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the EDA report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_eda`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir

    json_safe = {
        "summary": report["summary"],
        "training": {
            "class_distribution": report["training"]["class_distribution"].to_dict(orient="records"),
            "distribution_characteristics": report["training"]["distribution_characteristics"].to_dict(orient="records"),
            "outliers": report["training"]["outliers"].to_dict(orient="records"),
            "correlation_pairs": report["training"]["correlation_pairs"].to_dict(orient="records"),
        },
        "testing": {
            "class_distribution": report["testing"]["class_distribution"].to_dict(orient="records"),
            "distribution_characteristics": report["testing"]["distribution_characteristics"].to_dict(orient="records"),
            "outliers": report["testing"]["outliers"].to_dict(orient="records"),
            "correlation_pairs": report["testing"]["correlation_pairs"].to_dict(orient="records"),
        },
        "platform": platform.platform(),
    }

    json_path = write_json(reports_dir / "exploratory_data_analysis.json", json_safe)
    md_path = write_text(reports_dir / "exploratory_data_analysis.md", _render_eda_markdown(report))
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_eda() -> dict[str, Any]:
    """Run the complete exploratory data analysis pipeline.

    Loads training and testing sets independently, computes every
    required analysis for both splits, generates all figures (with
    dense visualisations centred on the training set, per this
    module's documented convention), saves CSV tables, and writes the
    JSON/Markdown reports.

    Returns:
        Dict with ``training``, ``testing``, and ``summary`` keys.
    """
    logger.info("EDA started")
    dataset_cfg = _load_dataset_config()
    target_column = dataset_cfg.get("target_column", "attack_cat")

    train_df, test_df = load_datasets()
    logger.info("Dataset loaded: training=%d rows, testing=%d rows", len(train_df), len(test_df))

    train_bundle = _analyse_split(train_df, target_column)
    test_bundle = _analyse_split(test_df, target_column)
    logger.info("Analysis completed: training and testing splits")

    dominant_categories = identify_dominant_categories(train_bundle["categorical_frequency"])
    observations = generate_research_observations(
        train_bundle["class_distribution"],
        train_bundle["distribution_characteristics"],
        train_bundle["outliers"],
        train_bundle["correlation_pairs"],
        dominant_categories,
    )

    figures_dir = get_path_manager().figures_dir
    plot_class_distribution(train_bundle["class_distribution"], test_bundle["class_distribution"], figures_dir / "class_distribution.png")
    plot_class_percentage(train_bundle["class_distribution"], test_bundle["class_distribution"], figures_dir / "class_percentage.png")
    plot_imbalance_ratio(train_bundle["class_distribution"], test_bundle["class_distribution"], figures_dir / "imbalance_ratio.png")
    plot_numerical_distributions(train_df, train_bundle["distribution_characteristics"], figures_dir / "numerical_distributions.png")
    plot_outlier_summary(train_df, train_bundle["outliers"], figures_dir / "outlier_summary.png")
    plot_categorical_distributions(train_bundle["categorical_frequency"], figures_dir / "categorical_distributions.png")
    plot_correlation_heatmap(train_bundle["correlation_matrix"], figures_dir / "correlation_heatmap.png")

    relationship_pairs = select_relationship_pairs(train_bundle["correlation_pairs"])
    plot_feature_relationships(train_df, relationship_pairs, target_column, figures_dir / "feature_relationships.png")

    table_paths = save_eda_tables(train_bundle, test_bundle)

    summary = generate_eda_summary(train_bundle, test_bundle, observations, dominant_categories)

    report = {"training": train_bundle, "testing": test_bundle, "summary": summary}
    save_eda_report(report)

    logger.info("EDA finished — %d figures, %d tables, 2 reports saved", 8, len(table_paths))
    return report
