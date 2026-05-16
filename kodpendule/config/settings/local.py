"""
Local development settings.

Use: DJANGO_SETTINGS_MODULE=config.settings.local
Env file: .env.local (see .env.local.example)
"""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
SECRET_KEY = "dev-only-insecure-key"
