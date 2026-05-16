# Kod Pendule — Webshop

Multilingual (Serbian / English) e-commerce for Serbia.  
**Stack:** Django 5 · PostgreSQL · django-parler · Bootstrap 5 · DRF · WhiteNoise · Gunicorn · Docker · Render.

## Project root

`E:\Stefan Spremo\Firme\Projekti\Web development\Kod Pendule\kodpendule`

Open the **`kodpendule`** folder in Cursor (**File → Open Folder**).

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, phases, decisions |
| [docs/APPS.md](docs/APPS.md) | App boundaries |
| [docs/MODELS.md](docs/MODELS.md) | Entity plan (Step 2) |
| [docs/URLS.md](docs/URLS.md) | URL map |
| [docs/SERVICES.md](docs/SERVICES.md) | Services/selectors API |
| [docs/PHASES.md](docs/PHASES.md) | Implementation checklist |

## Implementation status

| Step | Description | Status |
|------|-------------|--------|
| 1 | Architecture & folder structure | **Done** |
| 2 | Models, admin, migrations, tests | Next |
| 3 | Settings, env, Docker, requirements | Pending |
| 4–11 | Features, i18n, deploy, tests | Pending |

## Local setup (after Step 3)

```powershell
cd "E:\Stefan Spremo\Firme\Projekti\Web development\Kod Pendule\kodpendule"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements/local.txt
copy .env.local.example .env.local
# Configure PostgreSQL, then:
python manage.py migrate
python manage.py runserver
```

Docker (Step 10): `docker compose up --build`

## App layout

```
apps/
  core/ accounts/ categories/ products/
  cart/ checkout/ orders/ shipping/
  dashboard/ newsletter/
```

Each app includes `services/`, `selectors/`, `tests/`, and `migrations/`.
