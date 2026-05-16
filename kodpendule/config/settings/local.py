"""
Local development settings.

Use: DJANGO_SETTINGS_MODULE=config.settings.local
Env file: .env.local (see .env.local.example)
"""

from .base import *  # noqa: F403

# Step 3: DEBUG=True, DATABASE_URL, django-debug-toolbar, internal IPs
