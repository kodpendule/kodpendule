# Kod Pendule — Webshop

Multilingual (Serbian / English) e-commerce for Serbia.  
**Stack:** Django 5 · SQLite (local) / PostgreSQL (Render) · django-parler · Bootstrap 5 · DRF · WhiteNoise · Gunicorn.

## Project root

This folder is the **Git repository root** and the **Django project root** (where `manage.py` lives).

`E:\Stefan Spremo\Firme\Projekti\Web development\Kod Pendule\kodpendule`

Open this folder in Cursor (**File → Open Folder**). Use the Python interpreter at `.venv\Scripts\python.exe`.

## Quick start

```powershell
cd "E:\Stefan Spremo\Firme\Projekti\Web development\Kod Pendule\kodpendule"
.\.venv\Scripts\Activate.ps1
pip install -r requirements/local.txt
copy .env.local.example .env.local
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Local database: **`db.sqlite3`** (created automatically).  
Detailed setup: **[docs/SETUP.md](docs/SETUP.md)**

Run the full test suite:

```powershell
python manage.py test apps config
```

### Storefront translations (Serbian Latin)

After any task that adds or changes translatable UI strings, agents must automatically:

1. `python manage.py makemessages -l sr`
2. Add/fill new entries in `scripts/fill_sr_translations.py` and run that script
3. `python manage.py compilemessages -l sr`

Full steps (dedupe, admin merge): **[docs/ADMIN_LOCALE.md](docs/ADMIN_LOCALE.md)** · **`.cursor/rules/i18n-after-changes.mdc`**

## Settings

| Module | Use | Database |
|--------|-----|----------|
| `config.settings.local` | Development | SQLite |
| `config.settings.production` | Render / Gunicorn | PostgreSQL |

Copy `.env.local.example` → `.env.local` for local development.

## Status

| Step | Description | Status |
|------|-------------|--------|
| 1–3 | Structure, models, settings | Done |
| 4 | Authentication | Done |
| 5 | Storefront (catalog, search, homepage) | Done |
| 6 | Cart & checkout (guest, COD) | Done |
| 7 | Order tracking & customer history | Done |
| 8 | Admin analytics dashboard | Done |
| 9+ | i18n URLs, … | Pending |

### Admin Serbian labels

Admin UI uses English `gettext` msgids and Serbian translations in `locale/sr/LC_MESSAGES/`. After editing `django.po`, compile:

```powershell
python manage.py compilemessages -l sr
```

On Windows without GNU gettext (`msgfmt`), use the project script instead (updates `django.po` storefront strings and compiles `django.mo`):

```powershell
python scripts/compile_sr_messages.py
```

### Analytics dashboard (Step 8)

Staff only: **[http://127.0.0.1:8000/admin/analitika/](http://127.0.0.1:8000/admin/analitika/)** (link also in admin header).

Filters: last 7/30/90 days, current month/year, specific month+year, or custom date range.

### Order tracking (Step 7)

| URL | Description |
|-----|-------------|
| `/narudzba/pracenje/` | Guest track (order number + email) |
| `/narudzba/<order_number>/` | Order detail (after track, checkout, or login) |
| `/nalog/narudzbe/` | Logged-in order history |
