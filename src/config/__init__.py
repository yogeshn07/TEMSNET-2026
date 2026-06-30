"""Configuration loading and path management.

Public API
~~~~~~~~~~
- :func:`get_config` — cached merged configuration singleton.
- :func:`get_path_manager` — build a :class:`PathManager` from config.
- :func:`load_config` — load and validate a single YAML file.
- :class:`PathManager` — centralised directory resolver.
"""

from src.config.loader import get_config, get_path_manager, load_config
from src.config.paths import PathManager

__all__ = [
    "PathManager",
    "get_config",
    "get_path_manager",
    "load_config",
]
