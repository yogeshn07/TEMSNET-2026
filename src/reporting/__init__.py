"""Reporting package: IEEE manuscript generation and publication artifacts.

Public API
~~~~~~~~~~
- :func:`run_ieee_manuscript_generator` — Task F.3: assemble a complete
  IEEE conference-style manuscript from existing experimental outputs.
  No model is retrained. No explanations are regenerated. All numerical
  values are sourced from outputs produced by earlier pipeline stages.
"""

from src.reporting.ieee_manuscript_generator import run_ieee_manuscript_generator

__all__ = ["run_ieee_manuscript_generator"]
