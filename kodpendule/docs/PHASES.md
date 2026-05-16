# Implementation Checklist

Use this alongside [ARCHITECTURE.md](../ARCHITECTURE.md). Complete each step before moving on; run migrations and tests at the end of every step that touches models.

## Step 1 — Architecture & folder structure ✅

- [x] `config/` + `apps/*` packages
- [x] `services/`, `selectors/`, `tests/`, `migrations/` per app
- [x] `templates/`, `static/`, `media/`, `locale/`
- [x] Architecture docs (`ARCHITECTURE.md`, `docs/*`)
- [x] Docker/render/requirements placeholders

## Step 2 — Models ✅

- [x] Implement all models per [MODELS.md](MODELS.md)
- [x] Register in Django admin (inlines, list filters, low-stock highlight)
- [x] `makemigrations` + `migrate`
- [x] Serializer: `CitySerializer` (checkout shipping price)
- [x] `tests/test_models.py` per app (creation, constraints, parler)

## Step 3 — Settings & infrastructure

- [ ] Full `base.py` / `local.py` / `production.py`
- [ ] `requirements/*.txt` pinned versions
- [ ] `docker-compose.yml`, `Dockerfile`, `entrypoint.sh`
- [ ] `.env` examples documented in README

## Step 4 — Authentication

- [ ] Custom user model + migrations
- [ ] Login, register, logout templates
- [ ] Guest-capable session (no forced login)

## Step 5 — Products & categories

- [ ] Homepage category grid
- [ ] Product list/detail, pagination, SEO context

## Step 6 — Cart & checkout

- [ ] Session cart
- [ ] Checkout form: guest/login/register, addresses, delivery date, notes

## Step 7 — Orders & shipping

- [ ] `create_order` service, stock decrement
- [ ] City-based shipping price AJAX
- [ ] Order tracking + history

## Step 8 — Dashboard

- [ ] Admin index widgets: revenue, orders, low stock, recent orders
- [ ] Date picker for daily stats

## Step 9 — Multilingual

- [ ] Parler models + `locale` compilation
- [ ] Language switcher, translated slugs

## Step 10 — Deployment

- [ ] `render.yaml`, production static/media, README deploy section

## Step 11 — Testing & hardening

- [ ] Checkout integration test
- [ ] Rate limits, error pages, image constraints
