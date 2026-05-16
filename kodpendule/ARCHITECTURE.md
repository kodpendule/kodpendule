# Kod Pendule Webshop — Architecture

Production-ready multilingual e-commerce for Serbia (**Serbian** default, **English**).

**Project root:** `E:\Stefan Spremo\Firme\Projekti\Web development\Kod Pendule\kodpendule`

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (Browser)                         │
│         Bootstrap 5 · django-parler i18n · SEO meta tags         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
┌────────────────────────────▼────────────────────────────────────┐
│              Django 5.x (Gunicorn + WhiteNoise)                  │
│                                                                  │
│  Presentation:  templates/  ·  class-based & function views      │
│  API (optional): DRF serializers in */serializers.py             │
│  Business logic: */services/  (writes, transactions)             │
│  Queries:        */selectors/ (reads, prefetch, filters)         │
│                                                                  │
│  ┌────────┐ ┌──────────┐ ┌──────┐ ┌──────────┐ ┌────────┐       │
│  │  core  │ │ products │ │ cart │ │ checkout │ │ orders │       │
│  └────────┘ └──────────┘ └──────┘ └──────────┘ └────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌───────────┐ ┌─────────┐ │
│  │ accounts │ │categories│ │shipping │ │ dashboard │ │newsletter│ │
│  └──────────┘ └──────────┘ └─────────┘ └───────────┘ └─────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   PostgreSQL    │
                    │  (local / Render)│
                    └─────────────────┘
```

---

## Key Architectural Decisions

| Topic | Choice | Rationale |
|-------|--------|-----------|
| **i18n content** | `django-parler` | Translatable model fields with clean admin; fits SR/EN product copy and SEO fields |
| **i18n UI** | Django `i18n` + `locale/` | Standard URL prefix (`/en/...`) and gettext for templates |
| **Settings** | `config/settings/{base,local,production}.py` | Single switch via `DJANGO_SETTINGS_MODULE` and `.env` |
| **Database** | `dj-database-url` + `DATABASE_URL` | Same code path for Docker, local Postgres, Render managed DB |
| **Cart** | Session dict (`apps.cart.cart`) | Guest checkout without accounts; optional persisted cart later |
| **Checkout** | Dedicated `checkout` app | Orchestrates cart + shipping + payment + order creation |
| **Payments** | Strategy pattern (`orders/payments/`) | COD now; Stripe/PayPal/Serbian gateways plug in later |
| **Stock** | Decrement in `orders.services` | Atomic updates inside `transaction.atomic()` |
| **Admin analytics** | `dashboard` app + custom Admin index | Revenue/orders without external BI for v1 |
| **Celery** | **Not used in v1** | Newsletter “send later” prepared via models; async when volume requires it |
| **API** | DRF where useful | Checkout shipping price AJAX, future mobile headroom |

---

## Repository Layout

```
Kod Pendule/
├── config/                      # Project package (settings, urls, wsgi)
│   ├── settings/
│   │   ├── base.py              # Shared: apps, middleware, i18n, static
│   │   ├── local.py             # DEBUG, dev tools, local DB
│   │   └── production.py        # WhiteNoise, security, Render
│   ├── urls.py                  # Root URLconf + i18n patterns
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        # Domain Django apps (see docs/APPS.md)
│   ├── core/                    # Site/footer/homepage CMS, SEO helpers
│   ├── accounts/                # User, profile, addresses, auth views
│   ├── categories/
│   ├── products/
│   ├── cart/
│   ├── checkout/
│   ├── orders/                  # Orders, items, payment strategies
│   ├── shipping/                # Cities, dynamic shipping prices
│   ├── dashboard/               # Admin stats & low-stock widgets
│   └── newsletter/              # Subscribers, import/export, campaigns prep
│
├── templates/                   # Global templates (app-specific → apps/*/templates)
├── static/                      # Source static (collected to staticfiles/)
├── media/                       # User uploads (products, categories, banners)
├── locale/                      # gettext .po files (sr, en)
│
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── requirements.txt             # Points to production for Render
│
├── docker/
│   └── entrypoint.sh
├── scripts/
│   ├── dev.sh
│   └── sync_scaffold_from_cursor.ps1
│
├── docs/                        # Design docs per implementation step
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── .env.example
├── .env.local.example
└── .env.production.example
```

---

## Per-App Package Convention

Every domain app follows the same internal layout (see `apps/_app_scaffold.py`):

```
apps/<app_name>/
├── apps.py
├── models.py
├── admin.py
├── views.py
├── urls.py
├── forms.py                 # If user-facing forms exist
├── serializers.py           # DRF, if API endpoints exist
├── services/                # Commands: create_order, import_emails, …
│   └── __init__.py
├── selectors/               # Queries: get_featured_products, low_stock, …
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── migrations/
│   └── __init__.py
└── templates/<app_name>/    # Only when templates are app-scoped
```

**Rule:** Views stay thin — call `services` for writes and `selectors` for reads.

---

## Request Flow (Checkout Example)

```
GET  /checkout/          → checkout.views.checkout
                           → selectors: cart lines, cities, user addresses
POST /checkout/          → checkout.forms.CheckoutForm
                           → shipping.selectors.get_price(city_id)
                           → orders.services.create_order(...)
                           → cart.services.clear(session)
                           → redirect orders:confirmation

GET  /api/shipping-price/ → DRF (city_id) → shipping.selectors (Step 7)
```

---

## Multilingual Strategy

1. **Database content** (product name, category, footer, banners): `TranslatableModel` + `TranslatedFields` via parler.
2. **Slugs:** Language-specific slugs stored on translation model; fallback to Serbian.
3. **Templates/static UI:** `{% trans %}` / `{% blocktrans %}` with `locale/sr` and `locale/en`.
4. **URLs:** `i18n_patterns()` wrapping storefront URLs; admin stays `/admin/`.

---

## Security & Performance (built across steps)

- CSRF on all POST forms; `SECURE_*` in production
- `LoginRequiredMixin` only where needed; guest checkout allowed
- `select_related` / `prefetch_related` in selectors
- Pagination on product lists and order history
- Pillow thumbnails or constrained upload sizes (Step 6+)
- `django-ratelimit` on auth and tracking endpoints (Step 14)
- Messages framework for user feedback

---

## Deployment Topology (Render)

```
Internet → Render Web Service (Gunicorn)
              ├── WhiteNoise (static)
              ├── DATABASE_URL → Render PostgreSQL
              └── MEDIA: Render disk or S3 (config in Step 10)
```

Local: `docker-compose` runs `web` + `db`; `.env.local` overrides `DATABASE_URL`.

---

## Implementation Phases

| Step | Scope | Status |
|------|--------|--------|
| **1** | Architecture & folder structure | ✅ Current |
| **2** | Models, admin, migrations, basic tests | Next |
| **3** | Settings, env, Docker, requirements | |
| **4** | Authentication (login/register/guest) | |
| **5** | Products & categories (views, templates) | |
| **6** | Cart & checkout | |
| **7** | Orders & shipping | |
| **8** | Admin dashboard | |
| **9** | Parler translations & locale | |
| **10** | Render deployment, README ops | |
| **11** | Integration tests & hardening | |

---

## Related Docs

- [docs/APPS.md](docs/APPS.md) — App responsibilities and boundaries
- [docs/MODELS.md](docs/MODELS.md) — Entity plan for Step 2
- [docs/URLS.md](docs/URLS.md) — URL map (storefront + admin)
- [docs/PHASES.md](docs/PHASES.md) — Step-by-step checklist
- [docs/SERVICES.md](docs/SERVICES.md) — Planned service/selectors API
