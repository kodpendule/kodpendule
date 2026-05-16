"""
Reference scaffold for each app package (not imported at runtime).

Per app:
  apps.py          — AppConfig
  models.py        — Step 2
  admin.py         — Step 2
  views.py         — Steps 4–7
  urls.py          — Steps 4–7
  forms.py         — Steps 4–7
  serializers.py   — DRF where useful
  services/        — write/command logic
  selectors/       — read/query logic
  tests/           — model & integration tests
  migrations/      — generated in Step 2
"""
