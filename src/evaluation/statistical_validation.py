"""Statistical validation for Research Task F.1.

Compares the baseline and SMOTE-balanced Random Forest models using
statistical tests applied to **existing outputs only**. No model
retraining, no SHAP regeneration, and no LIME regeneration occur in
this module.

Statistical tests applied
~~~~~~~~~~~~~~~~~~~~~~~~~
1. **McNemar's test** — paired binary outcomes (82,332 test samples).
2. **Bootstrap confidence intervals** — non-parametric CIs for
   accuracy, macro F1, and weighted F1 for both models.
3. **Wilcoxon signed-rank test (SHAP)** — paired feature importances
   (baseline vs SMOTE) for all 42 SHAP features.
4. **Wilcoxon signed-rank test (LIME)** — paired feature importances
   (baseline vs SMOTE) for all LIME-covered features.
5. **Wilcoxon signed-rank test (confidence)** — per-sample prediction
   confidence for all 82,332 paired test observations.

Multiple comparisons are corrected via Holm–Bonferroni across the
four hypothesis tests (McNemar + three Wilcoxon).

Public API
~~~~~~~~~~
- :func:`run_statistical_validation` — orchestrates all analyses and
  writes outputs to ``outputs/statistics/``, ``outputs/reports/``,
  ``outputs/tables/``, and ``outputs/figures/``.
"""

from __future__ import annotations

import hashlib
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import chi2, norm, wilcoxon
from sklearn.metrics import accuracy_score, f1_score

from src.config import get_config, get_path_manager
from src.core.logging_config import get_logger
from src.core.reproducibility import set_global_seed
from src.utils.file_utils import ensure_dir, write_json, write_text

logger = get_logger(__name__)

# ── Upstream artefacts verified by SHA-256 ───────────────────────────────────

_UPSTREAM_ARTEFACTS: dict[str, str] = {
    "predictions/baseline": "outputs/predictions/baseline_predictions.parquet",
    "predictions/smote": "outputs/predictions/smote_predictions.parquet",
    "predictions/registry": "outputs/predictions/sample_registry.parquet",
    "shap/baseline": "outputs/shap/shap_values_baseline.parquet",
    "shap/smote": "outputs/shap/shap_values_smote.parquet",
    "lime/baseline": "outputs/lime/lime_explanations_baseline.parquet",
    "lime/smote": "outputs/lime/lime_explanations_smote.parquet",
    "comparison/similarity": "outputs/comparison/explanation_similarity.csv",
    "comparison/ranking": "outputs/comparison/explanation_comparison.parquet",
}


# ── SHA-256 helpers ───────────────────────────────────────────────────────────

def _compute_sha256(path: Path) -> str:
    """Return the hex-encoded SHA-256 digest of *path*.

    Args:
        path: File to hash.

    Returns:
        Lowercase hex SHA-256 string.

    Raises:
        FileNotFoundError: If *path* does not exist.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Upstream artefact missing: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot_hashes(root: Path) -> dict[str, str]:
    """Compute SHA-256 for every upstream artefact.

    Args:
        root: Project root directory.

    Returns:
        Mapping of logical key → SHA-256 hex string.
    """
    hashes: dict[str, str] = {}
    for key, rel in _UPSTREAM_ARTEFACTS.items():
        path = root / rel
        hashes[key] = _compute_sha256(path)
        logger.debug("SHA-256 [%s]: %s…", key, hashes[key][:12])
    return hashes


def _verify_upstream_unchanged(initial: dict[str, str], root: Path) -> bool:
    """Assert no upstream artefact was modified during the analysis.

    Args:
        initial: Hashes computed before the analysis began.
        root: Project root directory.

    Returns:
        ``True`` if all hashes match; ``False`` (with error logs) otherwise.
    """
    ok = True
    for key, original_hash in initial.items():
        current = _compute_sha256(root / _UPSTREAM_ARTEFACTS[key])
        if current != original_hash:
            logger.error(
                "INTEGRITY VIOLATION: %s was modified (was %s…, now %s…)",
                key, original_hash[:12], current[:12],
            )
            ok = False
    if ok:
        logger.info("SHA-256 self-test PASSED — all %d upstream artefacts unchanged", len(initial))
    return ok


# ── Data loading ──────────────────────────────────────────────────────────────

def load_prediction_data(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the prediction repository artefacts (read-only).

    Args:
        root: Project root directory.

    Returns:
        Tuple of (sample_registry, baseline_predictions, smote_predictions).
    """
    registry = pd.read_parquet(root / "outputs/predictions/sample_registry.parquet")
    baseline = pd.read_parquet(root / "outputs/predictions/baseline_predictions.parquet")
    smote = pd.read_parquet(root / "outputs/predictions/smote_predictions.parquet")
    logger.info(
        "Inputs loaded — registry: %d rows, baseline: %d rows, smote: %d rows",
        len(registry), len(baseline), len(smote),
    )
    return registry, baseline, smote


def load_evaluation_metrics(root: Path) -> dict[str, Any]:
    """Load the Random Forest evaluation report (read-only).

    Args:
        root: Project root directory.

    Returns:
        Parsed report dict from ``outputs/reports/random_forest_report.json``.
    """
    import json
    path = root / "outputs/reports/random_forest_report.json"
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    logger.info(
        "Evaluation metrics loaded — baseline accuracy=%.4f, smote accuracy=%.4f",
        data["baseline"]["accuracy"], data["smote"]["accuracy"],
    )
    return data


def load_explanation_data(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the explanation comparison artefacts (read-only).

    Args:
        root: Project root directory.

    Returns:
        Tuple of (explanation_similarity_df, explanation_comparison_df).
    """
    similarity = pd.read_csv(root / "outputs/comparison/explanation_similarity.csv")
    comparison = pd.read_parquet(root / "outputs/comparison/explanation_comparison.parquet")
    logger.info(
        "Explanation data loaded — similarity: %d rows, comparison: %d rows",
        len(similarity), len(comparison),
    )
    return similarity, comparison


# ── Assumption verification ───────────────────────────────────────────────────

def verify_paired_structure(
    registry: pd.DataFrame,
    baseline: pd.DataFrame,
    smote: pd.DataFrame,
) -> dict[str, Any]:
    """Verify that the paired test structure is intact.

    Assumptions checked:
    - All three files cover the same 82,332 rows in the same order.
    - The sample IDs are consistent across files.
    - Both predicted-class columns are present in the registry.

    Args:
        registry: Sample registry from the prediction repository.
        baseline: Baseline model predictions.
        smote: SMOTE model predictions.

    Returns:
        Dict with ``n_samples``, ``ids_consistent``, ``zero_diff_rate``
        (fraction of samples where confidence is identical between models),
        and ``model_agreement_rate``.
    """
    n = len(registry)
    ids_consistent = (
        (registry["sample_id"] == baseline["sample_id"]).all()
        and (registry["sample_id"] == smote["sample_id"]).all()
    )
    agree = (
        registry["predicted_class_baseline"] == registry["predicted_class_smote"]
    ).sum()
    conf_diff = (baseline["confidence"] - smote["confidence"]).abs()
    zero_diff_rate = (conf_diff == 0.0).mean()

    logger.info("Assumption check — n=%d, IDs consistent=%s", n, ids_consistent)
    logger.info(
        "Assumption check — model agreement rate=%.4f, zero confidence-diff rate=%.4f",
        agree / n, zero_diff_rate,
    )
    return {
        "n_samples": n,
        "ids_consistent": bool(ids_consistent),
        "model_agreement_rate": agree / n,
        "zero_confidence_diff_rate": zero_diff_rate,
    }


# ── McNemar's test ────────────────────────────────────────────────────────────

def _build_mcnemar_table(registry: pd.DataFrame) -> tuple[int, int, int, int]:
    """Build the 2×2 McNemar contingency table.

    Assumption: both classifiers are evaluated on the **same** test set.
    The table counts:
    - a: both correct
    - b: baseline wrong, SMOTE correct (SMOTE gains)
    - c: baseline correct, SMOTE wrong (SMOTE loses)
    - d: both wrong

    Args:
        registry: Sample registry with true and predicted classes.

    Returns:
        Tuple (a, b, c, d) of cell counts.
    """
    base_ok = registry["predicted_class_baseline"] == registry["true_class"]
    smote_ok = registry["predicted_class_smote"] == registry["true_class"]
    a = (base_ok & smote_ok).sum()
    b = (~base_ok & smote_ok).sum()
    c = (base_ok & ~smote_ok).sum()
    d = (~base_ok & ~smote_ok).sum()
    logger.info(
        "McNemar contingency — a(both correct)=%d, b(base wrong/smote right)=%d, "
        "c(base right/smote wrong)=%d, d(both wrong)=%d",
        a, b, c, d,
    )
    return a, b, c, d


def run_mcnemar_test(
    registry: pd.DataFrame,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Apply McNemar's test to compare baseline vs SMOTE predictions.

    Statistical assumptions:
    - Binary outcomes (correct/incorrect per sample) are paired — the
      same 82,332 test instances are evaluated by both classifiers.
    - Samples are independent of each other (distinct network flows).
    - McNemar's test is valid for comparing two classifiers on the same
      test set regardless of the class distribution.

    Limitations:
    - Tests whether the two models' *error patterns* are symmetric;
      does not directly test which model has higher accuracy.
    - Does not account for class imbalance.

    Args:
        registry: Sample registry with paired predictions.
        cfg: Configuration dict from ``statistical_validation.yaml``.

    Returns:
        Dict with test name, statistic, p-value, b, c, interpretation,
        and assumption documentation.
    """
    mcnemar_cfg = cfg.get("mcnemar", {})
    yates = mcnemar_cfg.get("continuity_correction", True)
    exact_threshold = mcnemar_cfg.get("exact_threshold", 25)

    a, b, c, d = _build_mcnemar_table(registry)
    n_discordant = b + c

    if n_discordant < exact_threshold:
        from scipy.stats import binom
        k = min(b, c)
        p_value = float(2 * binom.cdf(k, n_discordant, 0.5))
        method_used = "exact_binomial"
        stat = float(k)
    else:
        correction = 1.0 if yates else 0.0
        stat = (abs(b - c) - correction) ** 2 / n_discordant
        p_value = float(chi2.sf(stat, df=1))
        method_used = "chi2_yates" if yates else "chi2"

    logger.info(
        "McNemar's test (%s) — stat=%.4f, p=%.6g, n_discordant=%d",
        method_used, stat, p_value, n_discordant,
    )
    return {
        "test": "McNemar",
        "method": method_used,
        "statistic": stat,
        "p_value": p_value,
        "n_discordant": n_discordant,
        "b_smote_gains": b,
        "c_smote_loses": c,
        "assumptions": (
            "Paired binary outcomes on the same 82,332 test instances. "
            "Samples assumed independent. Yates continuity correction applied."
        ),
        "limitations": (
            "Tests symmetry of errors, not which model is more accurate. "
            "Does not capture per-class behaviour."
        ),
    }


# ── Bootstrap confidence intervals ────────────────────────────────────────────

def _bootstrap_iter_fast(
    y_true_int: np.ndarray,
    y_pred_int: np.ndarray,
    n_classes: int,
    rng: np.random.Generator,
) -> tuple[float, float, float]:
    """Draw one bootstrap resample and return accuracy + F1 scores.

    Uses ``np.bincount`` to build the confusion matrix without any
    Python-level sklearn call inside the loop, making it ~50× faster
    than the equivalent ``f1_score`` approach.

    Args:
        y_true_int: Integer-encoded true labels (pre-computed once).
        y_pred_int: Integer-encoded predicted labels (pre-computed once).
        n_classes: Number of distinct classes.
        rng: Seeded random number generator.

    Returns:
        Tuple of (accuracy, macro_f1, weighted_f1).
    """
    n = len(y_true_int)
    idx = rng.integers(0, n, size=n)
    yt, yp = y_true_int[idx], y_pred_int[idx]

    # Build confusion matrix via bincount — O(n) single C call
    cm = np.bincount(n_classes * yt + yp, minlength=n_classes * n_classes)
    cm = cm.reshape(n_classes, n_classes).astype(np.float64)

    diag = np.diagonal(cm)
    col_sum = cm.sum(axis=0)
    row_sum = cm.sum(axis=1)

    acc = diag.sum() / n
    with np.errstate(divide="ignore", invalid="ignore"):
        prec = np.where(col_sum > 0, diag / col_sum, 0.0)
        rec = np.where(row_sum > 0, diag / row_sum, 0.0)
        denom = prec + rec
        f1 = np.where(denom > 0, 2.0 * prec * rec / denom, 0.0)

    macro = f1.mean()
    support = row_sum / row_sum.sum() if row_sum.sum() > 0 else np.ones(n_classes) / n_classes
    weighted = float(np.dot(f1, support))
    return float(acc), float(macro), weighted


def bootstrap_model_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    label: str,
    cfg: dict[str, Any],
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    """Bootstrap confidence intervals for one model's predictions.

    Estimation method: percentile bootstrap. Labels are integer-encoded
    once before the loop; each iteration uses ``np.bincount`` for the
    confusion matrix, avoiding per-iteration sklearn overhead.

    Args:
        y_true: True class labels (n=82,332).
        y_pred: Predicted class labels.
        label: Model identifier (``"baseline"`` or ``"smote"``).
        cfg: Configuration dict.
        seed: Random seed for resampling.

    Returns:
        Tuple of (list of CI dicts, dict of raw bootstrap arrays).
    """
    boot_cfg = cfg.get("bootstrap", {})
    n_iter = int(boot_cfg.get("n_iterations", 2000))
    conf = float(boot_cfg.get("confidence_level", 0.95))
    alpha = 1.0 - conf

    # Encode labels to integers once — avoids repeated string comparison
    labels_sorted = sorted(np.unique(y_true).tolist())
    n_classes = len(labels_sorted)
    enc = {c: i for i, c in enumerate(labels_sorted)}
    y_true_int = np.array([enc[c] for c in y_true], dtype=np.int32)
    y_pred_int = np.array([enc.get(c, 0) for c in y_pred], dtype=np.int32)

    rng = np.random.default_rng(seed)
    acc_arr = np.empty(n_iter)
    macro_arr = np.empty(n_iter)
    weighted_arr = np.empty(n_iter)

    logger.info("Bootstrap CI — model=%s, n_iter=%d (fast bincount mode) …", label, n_iter)
    for i in range(n_iter):
        acc_arr[i], macro_arr[i], weighted_arr[i] = _bootstrap_iter_fast(
            y_true_int, y_pred_int, n_classes, rng
        )

    ci_rows: list[dict[str, Any]] = []
    for name, arr, obs in [
        ("accuracy", acc_arr, float(accuracy_score(y_true, y_pred))),
        ("macro_f1", macro_arr, float(f1_score(y_true, y_pred, average="macro", zero_division=0))),
        ("weighted_f1", weighted_arr, float(f1_score(y_true, y_pred, average="weighted", zero_division=0))),
    ]:
        lo = float(np.percentile(arr, 100 * alpha / 2))
        hi = float(np.percentile(arr, 100 * (1 - alpha / 2)))
        ci_rows.append({
            "model": label, "metric": name, "observed": obs,
            "ci_lower": lo, "ci_upper": hi,
            "ci_width": hi - lo, "confidence_level": conf, "n_bootstrap": n_iter,
            "method": "percentile_bootstrap",
        })
        logger.info("  %s/%s: %.4f [%.4f, %.4f]", label, name, obs, lo, hi)

    samples = {
        f"{label}_accuracy": acc_arr,
        f"{label}_macro_f1": macro_arr,
        f"{label}_weighted_f1": weighted_arr,
    }
    return ci_rows, samples


def run_bootstrap_cis(
    registry: pd.DataFrame,
    baseline: pd.DataFrame,
    smote: pd.DataFrame,
    cfg: dict[str, Any],
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    """Bootstrap CIs for both models.

    Args:
        registry: Sample registry (provides true labels).
        baseline: Baseline predictions.
        smote: SMOTE predictions.
        cfg: Configuration dict.
        seed: Base random seed.

    Returns:
        Tuple of (all CI rows, dict of all bootstrap sample arrays).
    """
    y_true = registry["true_class"].to_numpy()
    y_base = baseline["predicted_class"].to_numpy()
    y_smote = smote["predicted_class"].to_numpy()

    rows_b, samples_b = bootstrap_model_ci(y_true, y_base, "baseline", cfg, seed)
    rows_s, samples_s = bootstrap_model_ci(y_true, y_smote, "smote", cfg, seed + 1)

    all_rows = rows_b + rows_s
    all_samples = {**samples_b, **samples_s}
    logger.info("Bootstrap CIs computed — %d CI rows total", len(all_rows))
    return all_rows, all_samples


# ── Wilcoxon signed-rank tests ────────────────────────────────────────────────

def run_wilcoxon_confidence(
    baseline: pd.DataFrame,
    smote: pd.DataFrame,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Wilcoxon signed-rank test on paired per-sample confidence scores.

    Statistical assumptions:
    - Confidence differences are independently drawn.
    - The distribution of differences is symmetric about its median
      (not necessarily normal).
    - n=82,332 pairs → normal approximation (``method='approx'``) is
      appropriate.

    Limitations:
    - Many zero differences (same predicted class, same score) are
      dropped (zero_method='wilcox'); this is documented below.
    - Confidence is a Random Forest vote proportion — discrete, not
      truly continuous.
    - A statistically significant shift may reflect class difficulty
      changes, not necessarily model improvement.

    Args:
        baseline: Baseline predictions (``confidence`` column).
        smote: SMOTE predictions (``confidence`` column).
        cfg: Configuration dict.

    Returns:
        Dict with test name, statistic, p-value, n_pairs, n_nonzero,
        and documentation.
    """
    wilcox_cfg = cfg.get("wilcoxon", {})
    alt = wilcox_cfg.get("alternative", "two-sided")

    base_conf = baseline["confidence"].to_numpy()
    smote_conf = smote["confidence"].to_numpy()
    diff = base_conf - smote_conf
    n_zero = int((diff == 0).sum())
    n_nonzero = len(diff) - n_zero

    logger.info(
        "Wilcoxon (confidence) — n_pairs=%d, n_zero_diff=%d (%.1f%%)",
        len(diff), n_zero, 100 * n_zero / len(diff),
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        stat, p_value = wilcoxon(base_conf, smote_conf, alternative=alt, method="approx")
        for w in caught:
            logger.warning("Wilcoxon (confidence) scipy warning: %s", str(w.message))

    logger.info("Wilcoxon (confidence) — W=%.4f, p=%.6g", stat, p_value)
    return {
        "test": "Wilcoxon_confidence",
        "statistic": float(stat),
        "p_value": float(p_value),
        "n_pairs": len(diff),
        "n_zero_differences": n_zero,
        "n_nonzero_pairs": n_nonzero,
        "alternative": alt,
        "method": "approx (normal approximation)",
        "assumptions": (
            "Paired confidence scores for the same 82,332 test instances. "
            "Normal approximation used (n >> 50). Zero differences removed "
            "(zero_method='wilcox'). Differences assumed symmetric."
        ),
        "limitations": (
            f"{n_zero} zero differences ({100*n_zero/len(diff):.1f}%) removed. "
            "Discrete vote proportions are not truly continuous. "
            "Significant p-value does not imply the shift is diagnostically meaningful."
        ),
    }


def run_wilcoxon_explanations(
    explanation_comp: pd.DataFrame,
    cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    """Wilcoxon signed-rank tests on paired feature importance values.

    Tests whether SHAP / LIME feature importance magnitudes are
    significantly different between the baseline and SMOTE models.

    Statistical assumptions:
    - Feature importance pairs are the same features across both models.
    - Differences between paired values are symmetric about the median.
    - ``method='auto'`` — scipy selects exact for n≤50 (SHAP~42,
      LIME~36), which is appropriate given the small sample sizes.

    Limitations:
    - Feature importances are not independent (correlated features).
    - Small n reduces statistical power; non-significant result does
      not imply equal importance distributions.

    Args:
        explanation_comp: Comparison DataFrame with ``method``,
            ``baseline_value``, ``smote_value`` columns.
        cfg: Configuration dict.

    Returns:
        List of result dicts, one per XAI method.
    """
    wilcox_cfg = cfg.get("wilcoxon", {})
    alt = wilcox_cfg.get("alternative", "two-sided")
    min_pairs = int(wilcox_cfg.get("min_pairs", 6))
    results: list[dict[str, Any]] = []

    for method in ["SHAP", "LIME"]:
        subset = explanation_comp[explanation_comp["method"] == method].copy()
        n = len(subset)
        if n < min_pairs:
            logger.warning("Wilcoxon (%s) skipped — n=%d < min_pairs=%d", method, n, min_pairs)
            continue

        x = subset["baseline_value"].to_numpy()
        y = subset["smote_value"].to_numpy()
        diff = x - y
        n_zero = int((diff == 0).sum())

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            stat, p_value = wilcoxon(x, y, alternative=alt, method="auto")
            for w in caught:
                logger.warning("Wilcoxon (%s) scipy warning: %s", method, str(w.message))

        logger.info(
            "Wilcoxon (%s importances) — n=%d, W=%.4f, p=%.6g", method, n, stat, p_value
        )
        results.append({
            "test": f"Wilcoxon_{method}_importance",
            "statistic": float(stat),
            "p_value": float(p_value),
            "n_pairs": n,
            "n_zero_differences": n_zero,
            "alternative": alt,
            "method": "auto (exact for n≤50)",
            "assumptions": (
                f"Paired {method} feature importances for {n} features present in both models. "
                "Differences assumed symmetric. Feature importances may be correlated."
            ),
            "limitations": (
                f"n={n} pairs limits statistical power. "
                "Feature importances are not independent observations. "
                "Absolute importance magnitudes differ between methods."
            ),
        })

    return results


# ── Effect sizes ──────────────────────────────────────────────────────────────

def _cohens_h(p1: float, p2: float) -> float:
    """Compute Cohen's h for two proportions.

    Cohen's h = 2·arcsin(√p2) − 2·arcsin(√p1).
    Sign: positive means p2 > p1.

    Args:
        p1: First proportion (baseline).
        p2: Second proportion (SMOTE).

    Returns:
        Cohen's h (signed).
    """
    return float(2 * np.arcsin(np.sqrt(p2)) - 2 * np.arcsin(np.sqrt(p1)))


def _interpret_cohens_h(h: float, cfg: dict[str, Any]) -> str:
    """Return a verbal magnitude label for Cohen's h.

    Args:
        h: Absolute Cohen's h value.
        cfg: Configuration dict containing ``effect_size.cohens_h`` thresholds.

    Returns:
        One of ``"negligible"``, ``"small"``, ``"medium"``, ``"large"``.
    """
    abs_h = abs(h)
    thresholds = cfg.get("effect_size", {}).get("cohens_h", {})
    large = float(thresholds.get("large", 0.8))
    medium = float(thresholds.get("medium", 0.5))
    small = float(thresholds.get("small", 0.2))
    if abs_h >= large:
        return "large"
    if abs_h >= medium:
        return "medium"
    if abs_h >= small:
        return "small"
    return "negligible"


def _rank_biserial_r(p_value: float, n_pairs: int) -> float:
    """Estimate rank-biserial r from a Wilcoxon p-value.

    Uses r = |Z| / √n where Z is derived from the two-tailed p-value.
    Capped at [0, 1].

    Args:
        p_value: Two-tailed p-value from Wilcoxon test.
        n_pairs: Number of non-zero difference pairs used.

    Returns:
        Rank-biserial correlation coefficient in [0, 1].
    """
    p_clamped = max(p_value, 1e-300)
    z = abs(norm.ppf(p_clamped / 2))
    r = z / np.sqrt(n_pairs)
    return min(float(r), 1.0)


def _interpret_rank_biserial(r: float, cfg: dict[str, Any]) -> str:
    """Return a verbal magnitude label for rank-biserial r.

    Args:
        r: Absolute rank-biserial r.
        cfg: Configuration dict containing thresholds.

    Returns:
        One of ``"negligible"``, ``"small"``, ``"medium"``, ``"large"``.
    """
    thresholds = cfg.get("effect_size", {}).get("rank_biserial", {})
    large = float(thresholds.get("large", 0.5))
    medium = float(thresholds.get("medium", 0.3))
    small = float(thresholds.get("small", 0.1))
    if r >= large:
        return "large"
    if r >= medium:
        return "medium"
    if r >= small:
        return "small"
    return "negligible"


def compute_effect_sizes(
    boot_cis: list[dict[str, Any]],
    wilcoxon_results: list[dict[str, Any]],
    cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compute all effect sizes for the study.

    Effect sizes reported:
    - Cohen's h for accuracy (proportion) difference.
    - Cohen's h for macro F1 difference.
    - Rank-biserial r for each Wilcoxon test.

    Args:
        boot_cis: Output of :func:`run_bootstrap_cis`.
        wilcoxon_results: Combined Wilcoxon results list.
        cfg: Configuration dict.

    Returns:
        List of effect-size dicts, one per comparison.
    """
    ci_lookup: dict[tuple[str, str], float] = {
        (row["model"], row["metric"]): row["observed"]
        for row in boot_cis
    }

    effects: list[dict[str, Any]] = []

    for metric in ("accuracy", "macro_f1", "weighted_f1"):
        p_base = ci_lookup.get(("baseline", metric), float("nan"))
        p_smote = ci_lookup.get(("smote", metric), float("nan"))
        h = _cohens_h(p_base, p_smote)
        effects.append({
            "comparison": f"baseline_vs_smote_{metric}",
            "effect_metric": "cohens_h",
            "value": h,
            "magnitude": _interpret_cohens_h(h, cfg),
            "direction": "smote_higher" if h > 0 else "baseline_higher",
            "interpretation": (
                f"Cohen's h={h:.4f} quantifies the practical difference in {metric} "
                f"between the two training distributions. |h|<0.2 is considered negligible."
            ),
        })
        logger.info("Effect size — %s: Cohen's h=%.4f (%s)", metric, h, effects[-1]["magnitude"])

    for wres in wilcoxon_results:
        n_nonzero = wres.get("n_pairs", 0) - wres.get("n_zero_differences", 0)
        if n_nonzero < 1:
            continue
        r = _rank_biserial_r(wres["p_value"], n_nonzero)
        effects.append({
            "comparison": wres["test"],
            "effect_metric": "rank_biserial_r",
            "value": r,
            "magnitude": _interpret_rank_biserial(r, cfg),
            "direction": "N/A (unsigned)",
            "interpretation": (
                f"Rank-biserial r={r:.4f} derived from Wilcoxon Z/√n. "
                f"Ranges [0,1]; 0.1/0.3/0.5 = small/medium/large."
            ),
        })
        logger.info("Effect size — %s: r=%.4f (%s)", wres["test"], r, effects[-1]["magnitude"])

    return effects


# ── Multiple comparison correction ────────────────────────────────────────────

def apply_holm_bonferroni(
    tests: list[dict[str, Any]],
    alpha: float,
) -> list[dict[str, Any]]:
    """Apply Holm–Bonferroni correction across all hypothesis tests.

    Tests are sorted by ascending p-value; the adjusted threshold for
    the k-th test (1-indexed) is α/(m − k + 1) where m is the total
    number of tests.

    Args:
        tests: List of test result dicts, each with a ``"p_value"`` key.
        alpha: Family-wise significance level (e.g., 0.05).

    Returns:
        Augmented list with ``"p_adjusted"`` and ``"reject_h0"`` keys.
    """
    m = len(tests)
    indexed = sorted(enumerate(tests), key=lambda x: x[1]["p_value"])
    rejected_so_far = True
    for rank, (orig_idx, test) in enumerate(indexed, start=1):
        threshold = alpha / (m - rank + 1)
        p = test["p_value"]
        reject = bool(p <= threshold) and rejected_so_far
        if not reject:
            rejected_so_far = False
        tests[orig_idx]["p_adjusted_threshold"] = threshold
        tests[orig_idx]["reject_h0_holm"] = reject
        tests[orig_idx]["holm_rank"] = rank

    n_rejected = sum(1 for t in tests if t.get("reject_h0_holm"))
    logger.info(
        "Holm–Bonferroni — m=%d tests, α=%.2f, %d rejected", m, alpha, n_rejected
    )
    return tests


# ── Figure generation ─────────────────────────────────────────────────────────

def _get_style(cfg: dict[str, Any]) -> str:
    """Return a valid matplotlib style name.

    Args:
        cfg: Configuration dict.

    Returns:
        A matplotlib style name that is installed.
    """
    requested = cfg.get("figures", {}).get("style", "seaborn-v0_8-paper")
    available = plt.style.available
    if requested in available:
        return requested
    for fallback in ("seaborn-paper", "seaborn-v0_8-paper", "ggplot", "default"):
        if fallback in available:
            return fallback
    return "default"


def plot_bootstrap_distributions(
    boot_cis: list[dict[str, Any]],
    boot_samples: dict[str, np.ndarray],
    out_dir: Path,
    cfg: dict[str, Any],
) -> Path:
    """Plot bootstrap sampling distributions for accuracy and F1 (Figure 1).

    Six-panel figure (2 rows × 3 cols): baseline / SMOTE, for each of
    accuracy, macro F1, weighted F1. Each panel shows the bootstrap
    histogram, 95% CI shaded, and the observed value marked.

    Args:
        boot_cis: CI rows from :func:`run_bootstrap_cis`.
        boot_samples: Raw bootstrap arrays keyed by ``"model_metric"``.
        out_dir: Output directory for the figure.
        cfg: Configuration dict.

    Returns:
        Path to the saved figure.
    """
    fig_cfg = cfg.get("figures", {})
    dpi = int(fig_cfg.get("dpi", 300))
    figsize = tuple(fig_cfg.get("figsize_bootstrap", [14, 10]))
    style = _get_style(cfg)

    metrics = ["accuracy", "macro_f1", "weighted_f1"]
    models = ["baseline", "smote"]
    ci_lookup = {(r["model"], r["metric"]): r for r in boot_cis}
    colours = {"baseline": "#2196F3", "smote": "#FF5722"}

    with plt.style.context(style):
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle(
            "Bootstrap Sampling Distributions (n=2 000 resamples, 95% CI)",
            fontsize=13, fontweight="bold", y=1.01,
        )
        for row, model in enumerate(models):
            for col, metric in enumerate(metrics):
                ax = axes[row][col]
                key = f"{model}_{metric}"
                samples = boot_samples[key]
                ci = ci_lookup[(model, metric)]
                lo, hi, obs = ci["ci_lower"], ci["ci_upper"], ci["observed"]
                colour = colours[model]

                ax.hist(samples, bins=40, color=colour, alpha=0.7, edgecolor="white", linewidth=0.4)
                ax.axvspan(lo, hi, alpha=0.25, color=colour, label=f"95% CI [{lo:.4f}, {hi:.4f}]")
                ax.axvline(obs, color="black", linewidth=1.4, linestyle="--", label=f"Observed {obs:.4f}")
                ax.axvline(lo, color=colour, linewidth=0.8, linestyle=":")
                ax.axvline(hi, color=colour, linewidth=0.8, linestyle=":")

                display_metric = metric.replace("_", " ").title()
                ax.set_title(f"{model.upper()} — {display_metric}", fontsize=10)
                ax.set_xlabel(display_metric, fontsize=9)
                ax.set_ylabel("Frequency" if col == 0 else "", fontsize=9)
                ax.legend(fontsize=7, loc="upper left")
                ax.tick_params(labelsize=8)

        fig.tight_layout()
        path = out_dir / "bootstrap_distributions.png"
        fig.savefig(str(path), dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    logger.info("Figure saved: %s", path)
    return path


def plot_ci_comparison(
    boot_cis: list[dict[str, Any]],
    out_dir: Path,
    cfg: dict[str, Any],
) -> Path:
    """Forest plot comparing 95% CIs for baseline vs SMOTE (Figure 2).

    Args:
        boot_cis: CI rows from :func:`run_bootstrap_cis`.
        out_dir: Output directory.
        cfg: Configuration dict.

    Returns:
        Path to the saved figure.
    """
    fig_cfg = cfg.get("figures", {})
    dpi = int(fig_cfg.get("dpi", 300))
    figsize = tuple(fig_cfg.get("figsize_ci", [10, 6]))
    style = _get_style(cfg)

    metrics = ["accuracy", "macro_f1", "weighted_f1"]
    labels = ["Accuracy", "Macro F1", "Weighted F1"]
    colours = {"baseline": "#2196F3", "smote": "#FF5722"}
    offsets = {"baseline": -0.15, "smote": 0.15}
    markers = {"baseline": "o", "smote": "s"}

    ci_lookup = {(r["model"], r["metric"]): r for r in boot_cis}

    with plt.style.context(style):
        fig, ax = plt.subplots(figsize=figsize)
        for i, (metric, label) in enumerate(zip(metrics, labels)):
            for model in ["baseline", "smote"]:
                ci = ci_lookup[(model, metric)]
                y = i + offsets[model]
                ax.plot(ci["observed"], y, markers[model], color=colours[model], markersize=7, zorder=3)
                ax.hlines(y, ci["ci_lower"], ci["ci_upper"], colors=colours[model], linewidth=2.5)
                ax.vlines([ci["ci_lower"], ci["ci_upper"]], y - 0.05, y + 0.05,
                          colors=colours[model], linewidth=1.5)

        ax.set_yticks(range(len(metrics)))
        ax.set_yticklabels(labels, fontsize=11)
        ax.set_xlabel("Metric Value", fontsize=11)
        ax.set_title("95% Bootstrap CI Comparison: Baseline vs SMOTE", fontsize=12, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

        patches = [
            mpatches.Patch(color=colours["baseline"], label="Baseline"),
            mpatches.Patch(color=colours["smote"], label="SMOTE"),
        ]
        ax.legend(handles=patches, loc="lower right", fontsize=10)
        ax.set_xlim(
            min(r["ci_lower"] for r in boot_cis) - 0.02,
            max(r["ci_upper"] for r in boot_cis) + 0.02,
        )
        fig.tight_layout()
        path = out_dir / "confidence_interval_comparison.png"
        fig.savefig(str(path), dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    logger.info("Figure saved: %s", path)
    return path


def plot_effect_sizes(
    effect_sizes: list[dict[str, Any]],
    out_dir: Path,
    cfg: dict[str, Any],
) -> Path:
    """Bar chart of effect sizes with interpretation bands (Figure 3).

    Args:
        effect_sizes: Output of :func:`compute_effect_sizes`.
        out_dir: Output directory.
        cfg: Configuration dict.

    Returns:
        Path to the saved figure.
    """
    fig_cfg = cfg.get("figures", {})
    dpi = int(fig_cfg.get("dpi", 300))
    figsize = tuple(fig_cfg.get("figsize_effect", [10, 6]))
    style = _get_style(cfg)

    magnitude_colours = {
        "negligible": "#9E9E9E",
        "small": "#4CAF50",
        "medium": "#FF9800",
        "large": "#F44336",
    }

    comparisons = [e["comparison"] for e in effect_sizes]
    values = [abs(e["value"]) for e in effect_sizes]
    magnitudes = [e["magnitude"] for e in effect_sizes]
    bar_colours = [magnitude_colours.get(m, "#9E9E9E") for m in magnitudes]

    short_labels = [
        c.replace("baseline_vs_smote_", "").replace("_", " ").title()
        .replace("Wilcoxon ", "Wilcoxon\n") for c in comparisons
    ]

    with plt.style.context(style):
        fig, ax = plt.subplots(figsize=figsize)
        bars = ax.barh(range(len(comparisons)), values, color=bar_colours, edgecolor="white",
                       height=0.6)

        for band_val, band_label, colour in [
            (0.2, "Small", "#4CAF50"), (0.5, "Medium", "#FF9800"), (0.8, "Large", "#F44336"),
        ]:
            ax.axvline(band_val, color=colour, linewidth=1.2, linestyle="--", alpha=0.7)
            ax.text(band_val + 0.005, len(comparisons) - 0.5, band_label,
                    color=colour, fontsize=8, va="top")

        for bar, val, mag in zip(bars, values, magnitudes):
            ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                    f"{val:.3f} ({mag})", va="center", ha="left", fontsize=8)

        ax.set_yticks(range(len(comparisons)))
        ax.set_yticklabels(short_labels, fontsize=9)
        ax.set_xlabel("Effect Size (absolute value)", fontsize=11)
        ax.set_title("Effect Size Summary: Baseline vs SMOTE", fontsize=12, fontweight="bold")
        ax.set_xlim(0, max(values) + 0.15)
        ax.grid(axis="x", alpha=0.3)

        legend_patches = [
            mpatches.Patch(color=c, label=f"{k.title()} effect")
            for k, c in magnitude_colours.items()
        ]
        ax.legend(handles=legend_patches, loc="lower right", fontsize=9)
        fig.tight_layout()
        path = out_dir / "effect_sizes.png"
        fig.savefig(str(path), dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    logger.info("Figure saved: %s", path)
    return path


# ── Table persistence ─────────────────────────────────────────────────────────

def save_tables(
    hypothesis_tests: list[dict[str, Any]],
    boot_cis: list[dict[str, Any]],
    effect_sizes: list[dict[str, Any]],
    tables_dir: Path,
) -> None:
    """Write the three CSV tables required by Task F.1.

    Args:
        hypothesis_tests: All hypothesis tests after Holm correction.
        boot_cis: Bootstrap CI rows.
        effect_sizes: Effect size rows.
        tables_dir: Destination directory (``outputs/tables/``).
    """
    ensure_dir(tables_dir)
    ht_cols = ["test", "statistic", "p_value", "p_adjusted_threshold",
               "reject_h0_holm", "holm_rank", "assumptions", "limitations"]
    pd.DataFrame(hypothesis_tests)[
        [c for c in ht_cols if c in pd.DataFrame(hypothesis_tests).columns]
    ].to_csv(tables_dir / "hypothesis_tests.csv", index=False)
    logger.info("Table saved: hypothesis_tests.csv")

    ci_cols = ["model", "metric", "observed", "ci_lower", "ci_upper",
               "ci_width", "confidence_level", "n_bootstrap", "method"]
    pd.DataFrame(boot_cis)[ci_cols].to_csv(
        tables_dir / "confidence_intervals.csv", index=False
    )
    logger.info("Table saved: confidence_intervals.csv")

    eff_cols = ["comparison", "effect_metric", "value", "magnitude", "direction", "interpretation"]
    pd.DataFrame(effect_sizes)[eff_cols].to_csv(
        tables_dir / "effect_sizes.csv", index=False
    )
    logger.info("Table saved: effect_sizes.csv")


# ── Statistics output (parquet + summary CSV) ─────────────────────────────────

def save_statistics_outputs(
    hypothesis_tests: list[dict[str, Any]],
    boot_cis: list[dict[str, Any]],
    effect_sizes: list[dict[str, Any]],
    stats_dir: Path,
) -> None:
    """Save ``statistical_results.parquet`` and ``statistical_summary.csv``.

    Args:
        hypothesis_tests: Hypothesis test results (after correction).
        boot_cis: Bootstrap CI rows.
        effect_sizes: Effect size rows.
        stats_dir: ``outputs/statistics/`` directory.
    """
    ensure_dir(stats_dir)

    rows: list[dict[str, Any]] = []
    for t in hypothesis_tests:
        rows.append({"section": "hypothesis_test", **t})
    for ci in boot_cis:
        rows.append({"section": "bootstrap_ci", **ci})
    for ef in effect_sizes:
        rows.append({"section": "effect_size", **ef})

    df_full = pd.DataFrame(rows)
    df_full.to_parquet(stats_dir / "statistical_results.parquet", index=False)
    logger.info("Saved: statistical_results.parquet (%d rows)", len(df_full))

    summary_rows: list[dict[str, Any]] = []
    for t in hypothesis_tests:
        summary_rows.append({
            "section": "hypothesis_test",
            "name": t["test"],
            "stat": t["statistic"],
            "p_value": t["p_value"],
            "reject_h0": t.get("reject_h0_holm"),
        })
    for ci in boot_cis:
        summary_rows.append({
            "section": "bootstrap_ci",
            "name": f"{ci['model']}_{ci['metric']}",
            "stat": ci["observed"],
            "p_value": None,
            "reject_h0": None,
        })
    pd.DataFrame(summary_rows).to_csv(stats_dir / "statistical_summary.csv", index=False)
    logger.info("Saved: statistical_summary.csv")


# ── JSON serialisation helper ─────────────────────────────────────────────────

def _to_json_safe(obj: Any) -> Any:
    """Recursively convert numpy / pandas scalars to native Python types.

    ``json.dumps`` rejects ``numpy.int64``, ``numpy.float64``, and
    ``numpy.bool_``.  This helper does a depth-first walk and replaces
    them with ``int``, ``float``, and ``bool`` respectively.

    Args:
        obj: Arbitrary Python object to sanitise.

    Returns:
        A JSON-serialisable copy of *obj*.
    """
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_safe(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


# ── Report generation ─────────────────────────────────────────────────────────

def _fmt_pval(p: float) -> str:
    """Format a p-value for the report.

    Args:
        p: p-value.

    Returns:
        Formatted string.
    """
    if p < 1e-300:
        return "< 1e-300 (machine epsilon)"
    if p < 0.001:
        return f"{p:.2e}"
    return f"{p:.6f}"


def _build_md_report(  # noqa: PLR0912
    results: dict[str, Any],
    generated_at: str,
) -> str:
    """Render the full statistical validation report in Markdown.

    Args:
        results: Assembled results dict from :func:`run_statistical_validation`.
        generated_at: ISO-8601 timestamp string.

    Returns:
        Markdown text of the full report.
    """
    r = results
    alpha = r["config"]["significance_level"]
    lines: list[str] = [
        "# Statistical Validation Report",
        "",
        f"**Generated:** {generated_at}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        "**Task:** F.1 — Statistical Validation & Significance Analysis  ",
        "",
        "---",
        "",
        "## Methodology",
        "",
        "This report validates previously generated experimental results using statistical tests "
        "applied to **existing outputs only**. No model was retrained, no SHAP values were "
        "recomputed, and no LIME explanations were regenerated. All input artefacts are "
        "verified by SHA-256 before and after the analysis.",
        "",
        "Statistical significance threshold: α = {:.2f}.  ".format(alpha),
        "Multiple comparison correction: **Holm–Bonferroni** across all hypothesis tests.  ",
        "Effect sizes: **Cohen's h** (proportions) and **rank-biserial r** (Wilcoxon tests).  ",
        "Confidence intervals: **95% percentile bootstrap** (n={} resamples).".format(
            r["config"]["bootstrap"]["n_iterations"]
        ),
        "",
        "---",
        "",
        "## Structural Assumptions",
        "",
        f"- **n_samples:** {r['structure']['n_samples']:,}",
        f"- **Sample IDs consistent across files:** {r['structure']['ids_consistent']}",
        f"- **Model agreement rate:** {r['structure']['model_agreement_rate']:.4f}",
        f"- **Zero confidence-difference rate:** {r['structure']['zero_confidence_diff_rate']:.4f}",
        "",
        "---",
        "",
        "## Hypothesis Tests",
        "",
        "### 1. McNemar's Test (Paired Classification Outcomes)",
        "",
        "**Assumption:** Both models evaluated on the same 82,332 test instances.  ",
        "**Null hypothesis (H₀):** The two classifiers make symmetric errors (b = c).  ",
    ]

    mc = r["mcnemar"]
    lines += [
        f"**Method:** {mc['method']}  ",
        f"**Statistic:** {mc['statistic']:.4f}  ",
        f"**p-value:** {_fmt_pval(mc['p_value'])}  ",
        f"**n_discordant (b+c):** {mc['n_discordant']:,} "
        f"(b={mc['b_smote_gains']:,}, c={mc['c_smote_loses']:,})  ",
        f"**Reject H₀ (Holm-corrected):** {mc.get('reject_h0_holm')}  ",
        "",
        f"*Limitations: {mc['limitations']}*",
        "",
    ]

    lines += [
        "### 2–4. Wilcoxon Signed-Rank Tests",
        "",
    ]
    for wres in r["wilcoxon"]:
        lines += [
            f"#### {wres['test'].replace('_', ' ')}",
            f"**n pairs:** {wres['n_pairs']} (zero differences removed: {wres['n_zero_differences']})  ",
            f"**Statistic (W):** {wres['statistic']:.4f}  ",
            f"**p-value:** {_fmt_pval(wres['p_value'])}  ",
            f"**Reject H₀ (Holm-corrected):** {wres.get('reject_h0_holm')}  ",
            f"*Assumptions: {wres['assumptions']}*  ",
            f"*Limitations: {wres['limitations']}*",
            "",
        ]

    lines += [
        "---",
        "",
        "## Bootstrap Confidence Intervals (95%)",
        "",
        "| Model | Metric | Observed | CI Lower | CI Upper | Width |",
        "|---|---|---|---|---|---|",
    ]
    for ci in r["bootstrap_cis"]:
        lines.append(
            f"| {ci['model']} | {ci['metric']} | {ci['observed']:.4f} | "
            f"{ci['ci_lower']:.4f} | {ci['ci_upper']:.4f} | {ci['ci_width']:.4f} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Effect Sizes",
        "",
        "| Comparison | Metric | Value | Magnitude | Direction |",
        "|---|---|---|---|---|",
    ]
    for ef in r["effect_sizes"]:
        lines.append(
            f"| {ef['comparison']} | {ef['effect_metric']} | "
            f"{ef['value']:.4f} | {ef['magnitude']} | {ef['direction']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Threats to Validity",
        "",
        "- **Test-set representativeness.** The 82,332-row UNSW-NB15 test split follows the "
        "dataset's predefined partition; findings are specific to this split.",
        "- **Class imbalance in McNemar's test.** McNemar's test does not weight classes; "
        "dominant classes (Normal, Generic) drive the discordant counts.",
        "- **Feature dependence in Wilcoxon (explanations).** SHAP / LIME feature importances "
        "are correlated; the Wilcoxon test assumes independent observations.",
        "- **Small n for explanation Wilcoxon.** n=42 (SHAP) and n≤40 (LIME) limit statistical "
        "power; a non-significant result does not imply equal distributions.",
        "- **Bootstrap independence.** Bootstrap resamples each row independently; "
        "any within-sample temporal structure in network flows is not preserved.",
        "- **No causal claims.** All findings are associative; the observed differences "
        "describe what changed in model behaviour, not why.",
        "",
        "---",
        "",
        "## Limitations",
        "",
        "- Confidence scores are discrete vote proportions (not continuous); the Wilcoxon "
        "approximation is less accurate in the presence of many ties.",
        "- Statistical significance (low p-value) does not equal practical importance. "
        "Effect sizes and CI widths should be consulted jointly.",
        "- Holm–Bonferroni controls the family-wise error rate at α=0.05; "
        "it is conservative when tests are positively correlated.",
        "",
        "---",
        "",
        "## Statistical Validation Summary",
        "*(Suitable for inclusion in the IEEE paper Results section)*",
        "",
    ]

    mc_reject = mc.get("reject_h0_holm")
    conf_wres = next((w for w in r["wilcoxon"] if "confidence" in w["test"]), None)
    shap_wres = next((w for w in r["wilcoxon"] if "SHAP" in w["test"]), None)
    lime_wres = next((w for w in r["wilcoxon"] if "LIME" in w["test"]), None)

    acc_base = next((c for c in r["bootstrap_cis"] if c["model"] == "baseline" and c["metric"] == "accuracy"), None)
    acc_smote = next((c for c in r["bootstrap_cis"] if c["model"] == "smote" and c["metric"] == "accuracy"), None)
    h_acc = next((e for e in r["effect_sizes"] if "accuracy" in e["comparison"] and e["effect_metric"] == "cohens_h"), None)

    lines += [
        "Statistical validation applied McNemar's test, three Wilcoxon signed-rank tests, "
        "95% percentile bootstrap confidence intervals, and Cohen's h / rank-biserial effect sizes, "
        f"with Holm–Bonferroni correction across {len(r['hypothesis_tests'])} hypothesis tests "
        f"(α = {alpha}).",
        "",
    ]
    if acc_base and acc_smote:
        lines.append(
            f"Baseline accuracy was {acc_base['observed']:.4f} (95% CI "
            f"[{acc_base['ci_lower']:.4f}, {acc_base['ci_upper']:.4f}]); "
            f"SMOTE accuracy was {acc_smote['observed']:.4f} (95% CI "
            f"[{acc_smote['ci_lower']:.4f}, {acc_smote['ci_upper']:.4f}]). "
        )
    if h_acc:
        lines[-1] += (
            f"The Cohen's h effect size for accuracy was {h_acc['value']:.4f} ({h_acc['magnitude']}). "
        )
    if mc_reject is not None:
        lines.append(
            "McNemar's test {}rejected H₀ (p={}, Holm-corrected), indicating the "
            "two classifiers' error patterns are {}symmetric.".format(
                "" if mc_reject else "did not ",
                _fmt_pval(mc["p_value"]),
                "a" if mc_reject else "",
            )
        )
    if conf_wres:
        lines.append(
            "The Wilcoxon test on per-sample confidence scores {}rejected H₀ (p={}), "
            "suggesting the prediction confidence distribution {}shifted significantly.".format(
                "" if conf_wres.get("reject_h0_holm") else "did not ",
                _fmt_pval(conf_wres["p_value"]),
                "" if conf_wres.get("reject_h0_holm") else "did not ",
            )
        )
    if shap_wres:
        lines.append(
            "SHAP feature importance magnitudes {}differed significantly between models "
            "(Wilcoxon, p={}).".format(
                "" if shap_wres.get("reject_h0_holm") else "did not ",
                _fmt_pval(shap_wres["p_value"]),
            )
        )
    if lime_wres:
        lines.append(
            "LIME feature importance magnitudes {}differed significantly between models "
            "(Wilcoxon, p={}).".format(
                "" if lime_wres.get("reject_h0_holm") else "did not ",
                _fmt_pval(lime_wres["p_value"]),
            )
        )
    lines += [
        "All findings are observational; no causal claim is made. "
        "Reproducibility is guaranteed by configuration-seeded bootstrap resampling "
        "and SHA-256 verification of all upstream artefacts.",
        "",
        "---",
        "*End of Statistical Validation Report*",
    ]
    return "\n".join(lines)


# ── Main entry point ──────────────────────────────────────────────────────────

def _load_stat_config(root: Path) -> dict[str, Any]:
    """Load ``configs/statistical_validation.yaml`` directly.

    Args:
        root: Project root directory.

    Returns:
        Statistical validation configuration dict.
    """
    stat_path = root / "configs" / "statistical_validation.yaml"
    if not stat_path.is_file():
        logger.warning("configs/statistical_validation.yaml not found — using defaults")
        return {}
    import yaml
    with open(stat_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    logger.info("Loaded configs/statistical_validation.yaml")
    return data


def run_statistical_validation() -> dict[str, Any]:
    """Run the full statistical validation pipeline (Task F.1).

    Loads existing artefacts only. Applies McNemar's test, bootstrap
    confidence intervals, Wilcoxon signed-rank tests, effect size
    measures, and Holm–Bonferroni correction.

    Returns:
        Comprehensive results dict suitable for JSON serialisation.

    Raises:
        FileNotFoundError: If any required upstream artefact is missing.
        RuntimeError: If SHA-256 self-test detects artefact modification.
    """
    cfg = get_config()
    paths = get_path_manager()
    root = paths.project_root

    stat_cfg = _load_stat_config(root)
    alpha = float(stat_cfg.get("significance_level", 0.05))
    seed = int(cfg.get("experiment", {}).get("random_seed", 42))

    set_global_seed(seed)
    logger.info("=== Task F.1 Statistical Validation ===")
    logger.info("Project root: %s", root)

    # SHA-256 snapshot (before)
    initial_hashes = _snapshot_hashes(root)
    logger.info("Inputs loaded — SHA-256 snapshot of %d upstream artefacts taken", len(initial_hashes))

    # Load data
    registry, baseline, smote = load_prediction_data(root)
    load_evaluation_metrics(root)
    _, explanation_comp = load_explanation_data(root)

    # Structural assumption check
    structure = verify_paired_structure(registry, baseline, smote)
    logger.info("Assumptions checked — structure verified")

    # McNemar's test
    logger.info("Statistical tests executing — McNemar's test …")
    mcnemar = run_mcnemar_test(registry, stat_cfg)

    # Bootstrap CIs
    logger.info("Confidence intervals computing — bootstrap (n=%d) …",
                stat_cfg.get("bootstrap", {}).get("n_iterations", 2000))
    boot_cis, boot_samples = run_bootstrap_cis(registry, baseline, smote, stat_cfg, seed)

    # Wilcoxon tests
    logger.info("Statistical tests executing — Wilcoxon (confidence scores) …")
    wilcox_conf = run_wilcoxon_confidence(baseline, smote, stat_cfg)
    logger.info("Statistical tests executing — Wilcoxon (explanation importances) …")
    wilcox_expl = run_wilcoxon_explanations(explanation_comp, stat_cfg)

    all_wilcoxon = [wilcox_conf] + wilcox_expl
    hypothesis_tests = [mcnemar] + all_wilcoxon

    # Holm–Bonferroni correction
    hypothesis_tests = apply_holm_bonferroni(hypothesis_tests, alpha)

    # Effect sizes
    logger.info("Effect sizes computing …")
    effect_sizes = compute_effect_sizes(boot_cis, all_wilcoxon, stat_cfg)

    # Output directories
    stats_dir = ensure_dir(root / "outputs/statistics")
    figures_dir = paths.figures_dir
    tables_dir = paths.tables_dir
    reports_dir = paths.reports_dir

    # Figures
    logger.info("Reports generating — figures …")
    fig1 = plot_bootstrap_distributions(boot_cis, boot_samples, figures_dir, stat_cfg)
    fig2 = plot_ci_comparison(boot_cis, figures_dir, stat_cfg)
    fig3 = plot_effect_sizes(effect_sizes, figures_dir, stat_cfg)

    # Tables
    logger.info("Reports generating — tables …")
    save_tables(hypothesis_tests, boot_cis, effect_sizes, tables_dir)

    # Statistics outputs
    save_statistics_outputs(hypothesis_tests, boot_cis, effect_sizes, stats_dir)

    # Assemble full results
    generated_at = datetime.now(tz=timezone.utc).isoformat()
    results: dict[str, Any] = {
        "generated_at": generated_at,
        "config": {
            "significance_level": alpha,
            "multiple_comparison_correction": stat_cfg.get("multiple_comparison_correction", "holm_bonferroni"),
            "bootstrap": stat_cfg.get("bootstrap", {}),
        },
        "structure": structure,
        "mcnemar": mcnemar,
        "bootstrap_cis": boot_cis,
        "wilcoxon": all_wilcoxon,
        "hypothesis_tests": hypothesis_tests,
        "effect_sizes": effect_sizes,
        "figures": [str(fig1), str(fig2), str(fig3)],
        "upstream_sha256": initial_hashes,
    }

    # Reports
    md_text = _build_md_report(results, generated_at)
    write_text(reports_dir / "statistical_validation_report.md", md_text)
    logger.info("Reports generated — statistical_validation_report.md")

    json_report = _to_json_safe({k: v for k, v in results.items() if k != "upstream_sha256"})
    write_json(reports_dir / "statistical_validation_report.json", json_report)
    logger.info("Reports generated — statistical_validation_report.json")

    # SHA-256 self-test (after)
    ok = _verify_upstream_unchanged(initial_hashes, root)
    if not ok:
        raise RuntimeError("SHA-256 self-test FAILED — upstream artefacts were modified")

    logger.info("Validation completed — Task F.1 finished successfully")
    return results
