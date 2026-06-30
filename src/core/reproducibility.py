"""Reproducibility utilities for deterministic experiment execution.

Provides four public functions:

* :func:`set_global_seed` — seed all RNGs in a single call.
* :func:`get_current_seed` — retrieve the active seed value.
* :func:`seed_context` — context manager that temporarily sets a
  seed and restores the previous RNG state on exit.
* :func:`get_reproducibility_report` — structured environment
  snapshot for experiment artefacts.

Usage in every pipeline script::

    from src.core.reproducibility import set_global_seed
    set_global_seed(42)

Design decisions
~~~~~~~~~~~~~~~~
* NumPy and PyTorch are optional: the module never crashes if they
  are absent — it simply skips those RNGs and logs a warning.
* ``PYTHONHASHSEED`` is set via ``os.environ`` so that hash-based
  operations (set iteration, dict ordering in older Pythons) are
  deterministic.  Note: this only takes full effect when set
  *before* the interpreter starts; setting it at runtime is
  best-effort and logged accordingly.
* ``seed_context`` captures and restores full RNG state objects,
  not just the seed integer, so downstream code cannot observe
  side effects from the temporary seed.
"""

from __future__ import annotations

import contextlib
import os
import platform
import random
import sys
from contextlib import contextmanager
from typing import Any, Generator

from src.core.logging_config import get_logger

logger = get_logger(__name__)

# ── private state ───────────────────────────────────────────
_current_seed: int | None = None


# ── optional dependency probes ──────────────────────────────

def _has_numpy() -> bool:
    """Return *True* if NumPy is importable."""
    try:
        import numpy  # noqa: F401
        return True
    except ImportError:
        return False


def _has_torch() -> bool:
    """Return *True* if PyTorch is importable."""
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


# ── public API ──────────────────────────────────────────────

def set_global_seed(seed: int) -> None:
    """Seed every available RNG for reproducible execution.

    Seeds the following in order:

    1. ``PYTHONHASHSEED`` environment variable.
    2. Python ``random`` module.
    3. NumPy ``numpy.random`` (if installed).
    4. PyTorch ``torch.manual_seed`` and CUDA seeds (if installed).
    5. PyTorch deterministic mode (if installed).

    This function is safe to call multiple times; each call resets
    all RNGs to the new seed.

    Args:
        seed: Non-negative integer seed value.

    Raises:
        TypeError: If *seed* is not an integer.
        ValueError: If *seed* is negative.
    """
    global _current_seed  # noqa: PLW0603

    if not isinstance(seed, int):
        raise TypeError(
            f"Seed must be an integer, got {type(seed).__name__}"
        )
    if seed < 0:
        raise ValueError(f"Seed must be non-negative, got {seed}")

    # 1. Python hash seed (best-effort at runtime)
    os.environ["PYTHONHASHSEED"] = str(seed)

    # 2. Python stdlib random
    random.seed(seed)

    # 3. NumPy
    if _has_numpy():
        import numpy as np
        np.random.seed(seed)
        logger.debug("NumPy RNG seeded with %d", seed)
    else:
        logger.warning("NumPy not installed — skipping numpy.random.seed()")

    # 4–5. PyTorch
    if _has_torch():
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        with contextlib.suppress(AttributeError):
            torch.use_deterministic_algorithms(True)
        logger.debug("PyTorch RNG seeded with %d (deterministic mode on)", seed)
    else:
        logger.debug("PyTorch not installed — skipping torch seeds")

    _current_seed = seed
    logger.info("Global seed set to %d", seed)


def get_current_seed() -> int | None:
    """Return the seed most recently passed to :func:`set_global_seed`.

    Returns:
        The active seed, or *None* if :func:`set_global_seed` has
        not been called yet in this process.
    """
    return _current_seed


@contextmanager
def seed_context(seed: int) -> Generator[None, None, None]:
    """Temporarily set a global seed, restoring prior state on exit.

    Captures the full RNG state of Python ``random`` (and NumPy if
    available) before applying the temporary seed.  On exit — whether
    normal or via exception — the saved state is restored so the
    caller's RNG sequence is unaffected.

    Args:
        seed: Temporary seed to apply inside the context.

    Yields:
        Nothing.  Use as a context manager::

            with seed_context(99):
                value = random.random()  # deterministic
            # RNG state restored here
    """
    global _current_seed  # noqa: PLW0603
    previous_seed = _current_seed

    # Save Python random state
    py_state = random.getstate()

    # Save NumPy state if available
    np_state: Any = None
    if _has_numpy():
        import numpy as np
        np_state = np.random.get_state()

    logger.debug("seed_context: entering with seed=%d (previous=%s)", seed, previous_seed)

    try:
        set_global_seed(seed)
        yield
    finally:
        # Restore Python random state
        random.setstate(py_state)

        # Restore NumPy state
        if np_state is not None and _has_numpy():
            import numpy as np
            np.random.set_state(np_state)

        # Restore the tracked seed value
        _current_seed = previous_seed

        logger.debug("seed_context: restored previous seed=%s", previous_seed)


def get_reproducibility_report() -> dict[str, Any]:
    """Build a structured snapshot of the reproducibility environment.

    The returned dictionary is intended to be serialised alongside
    experiment outputs so that any result can be traced back to its
    exact execution context.

    Returns:
        Dictionary with keys:

        - ``python_version``
        - ``platform``
        - ``current_seed``
        - ``pythonhashseed``
        - ``numpy_version`` (or ``"not installed"``)
        - ``torch_version`` (or ``"not installed"``)
        - ``torch_cuda_available``
        - ``torch_deterministic``
    """
    report: dict[str, Any] = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "current_seed": _current_seed,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "not set"),
    }

    # NumPy
    if _has_numpy():
        import numpy as np
        report["numpy_version"] = np.__version__
    else:
        report["numpy_version"] = "not installed"

    # PyTorch
    if _has_torch():
        import torch
        report["torch_version"] = torch.__version__
        report["torch_cuda_available"] = torch.cuda.is_available()
        try:
            report["torch_deterministic"] = torch.are_deterministic_algorithms_enabled()
        except AttributeError:
            report["torch_deterministic"] = "unknown"
    else:
        report["torch_version"] = "not installed"
        report["torch_cuda_available"] = False
        report["torch_deterministic"] = "n/a"

    return report
