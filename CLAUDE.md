# CLAUDE.md — TEMSNET-2026 Engineering Conventions

## Project

IEEE TEMSMET 2026 paper: "Impact of Class Imbalance on XAI Explanation Quality in ML-Based NIDS"

Dataset: UNSW-NB15. Model: Random Forest. XAI: SHAP (primary), LIME (secondary).

## Architecture Rules

- All configuration comes from `configs/*.yaml`. Never hardcode paths, seeds, hyperparameters, or thresholds.
- Every module under `src/` is a Python package with `__init__.py`.
- Pipeline entry points live in `scripts/` and are numbered (01_, 02_, ...).
- Generated artifacts go to `outputs/` subdirectories, never to the project root.
- Raw data stays in `data/raw/` and is never modified in place.

## Coding Standards

- Python 3.10+. Type hints on all function signatures.
- Google-style docstrings on all public functions.
- Maximum ~40-50 lines per function unless unavoidable.
- No `print()` statements. Use `logging` module exclusively.
- PEP 8 compliance enforced by ruff.
- Line length: 100 characters.

## Reproducibility

- Global random seed set via configuration, applied to `random`, `numpy`, and `sklearn`.
- Every script must call the seed utility before any stochastic operation.
- Train/test split uses the original UNSW-NB15 split (no re-splitting).

## Testing

- Tests in `tests/` using pytest.
- Test files named `test_<module>.py`.
- Run with: `pytest`

## What NOT to Do

- Do not add ML logic to `src/config/` or `src/core/` — those are infrastructure only.
- Do not create new top-level directories without documented justification.
- Do not store large files (data, models) in git — they are gitignored.
- Do not modify the research hypothesis, contribution, or methodology.
- Do not introduce algorithms beyond what the research blueprint specifies.
