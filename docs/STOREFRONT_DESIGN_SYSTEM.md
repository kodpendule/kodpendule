# Storefront design system (Frontend Phase 1)

Foundation only — page layouts unchanged. Loaded from `templates/base.html`:

1. `static/css/tokens.css` — `--shop-*` variables + Bootstrap bridge
2. `static/css/foundation.css` — typography, body, header, forms
3. `static/css/components.css` — buttons, badges, product cards, alerts
4. `static/css/main.css` — page-specific (carousel, gallery, orders)

## Brand

- Primary: `#0F5931`
- Accent (warm): `#C4A574` — optional highlights
- Neutrals: stone/warm gray palette

## Reusable classes

| Class | Use |
|-------|-----|
| `.shop-btn`, `.shop-btn--primary`, `--secondary`, `--ghost`, `--lg` | Standalone buttons |
| `.shop-badge`, `.shop-badge--sale`, `--success` | Labels |
| `.shop-card`, `.shop-card__body` | Generic panels |
| `.product-card` / `.shop-product-card` | Product grid items |
| `.shop-search` | Header search field |
| `.shop-alerts` | Flash messages wrapper |
| `.shop-price`, `.shop-price--sale`, `--was` | Pricing (templates in later phases) |
| `.shop-container`, `--narrow`, `--wide` | Max-width helpers |
| `.shop-lead`, `.shop-text-muted` | Copy hierarchy |

Bootstrap `.btn-primary`, `.form-control`, `.alert-*` inherit token colors via `--bs-*` overrides.

## Phase 2 — Header & navigation

- `static/css/header.css`, `static/js/header.js`
- `templates/includes/_header.html` — bar + desktop nav + mobile offcanvas
- `templates/includes/_header_nav_links.html` — shared links + active state
- `templates/includes/_language_switcher.html` — SR/EN pill toggle

## Phase 3 — Homepage

- `static/css/home.css` — hero, trust, categories, promos, CTA band
- `templates/pages/home.html` — section order and `extra_css`
- `templates/includes/_hero.html` — split hero (CMS banner or default), extra banners as horizontal scroll
- `templates/includes/_home_trust_strip.html`, `_home_trust_details.html`, `_home_categories.html`, `_home_cta_band.html`

## Next phases

Apply section layouts on PLP, PDP, checkout without changing backend.
