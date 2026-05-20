# Kod Pendule — Webshop

Multilingual (Serbian / English) e-commerce for Serbia.  
**Stack:** Django 5 · SQLite (local) / PostgreSQL (Render) · django-parler · Bootstrap 5 · DRF · WhiteNoise · Gunicorn.

## Project root

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
| 8+ | Admin dashboard, i18n URLs, … | Pending |

### Order tracking (Step 7)

| URL | Description |
|-----|-------------|
| `/narudzba/pracenje/` | Guest track (order number + email) |
| `/narudzba/<order_number>/` | Order detail (after track, checkout, or login) |
| `/nalog/narudzbe/` | Logged-in order history |
