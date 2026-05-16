"""
Production settings for Render / Gunicorn.

Use: DJANGO_SETTINGS_MODULE=config.settings.production
Env file: .env.production (or Render dashboard env vars)
"""

from .base import *  # noqa: F403

# Step 3: DEBUG=False, SECURE_*, WhiteNoise, DATABASE_URL, logging
