"""
Environment variable loading.

Priority: os.environ (e.g. Render dashboard) overrides values from the env file.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from decouple import AutoConfig, Config, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@lru_cache(maxsize=4)
def get_config(env_file: str | None = None) -> Config:
    """
    Load settings from BASE_DIR/<env_file> when the file exists.

    When missing, fall back to AutoConfig (`.env` in project root + os.environ).
    """
    filename = env_file or os.environ.get("ENV_FILE", "")
    if filename:
        path = BASE_DIR / filename
        if path.is_file():
            return Config(RepositoryEnv(path))

    default_env = BASE_DIR / ".env"
    if default_env.is_file():
        return Config(RepositoryEnv(default_env))

    return AutoConfig(search_path=BASE_DIR)
