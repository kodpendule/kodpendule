# Admin locale — Serbian Latin

Django’s built-in `sr` catalog (`django/contrib/.../locale/sr`) uses **Cyrillic**.  
This project overrides it via `LOCALE_PATHS` → `locale/sr/LC_MESSAGES/` with **Latin** msgstr values.

`AdminSerbianLocaleMiddleware` forces `sr` on `/admin/*` (storefront language is unchanged).

## After new translatable strings

```powershell
cd kodpendule
.\.venv\Scripts\python.exe manage.py makemessages -l sr --ignore=.venv
.\.venv\Scripts\python.exe scripts\fill_sr_translations.py
.\.venv\Scripts\python.exe scripts\generate_admin_latin.py
.\.venv\Scripts\python.exe scripts\merge_admin_latin.py
.\.venv\Scripts\python.exe scripts\generate_djangojs_latin.py
.\.venv\Scripts\python.exe scripts\merge_djangojs_latin.py
.\.venv\Scripts\python.exe scripts\merge_contrib_latin.py
.\.venv\Scripts\python.exe manage.py compilemessages -l sr
```

`merge_admin_latin.py` and `merge_djangojs_latin.py` also compile `.mo` via `polib` (required on Windows when `msgfmt` is not on PATH).

## Custom admin copy

Operational labels (nav groups, KPIs, etc.) live in templates and `django.po` under project-specific msgids — not in Django’s contrib catalogs.

Model `verbose_name` strings should stay English in Python; add Serbian Latin in `django.po` (e.g. `hero banner` → `Baner početne`).
