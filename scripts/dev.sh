#!/usr/bin/env sh
# Local dev helper (Git Bash / WSL)
set -e
cd "$(dirname "$0")/.."
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py runserver "$@"
