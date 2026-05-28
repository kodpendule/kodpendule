# Admin design system (Phase 1)

Foundation only — no page redesigns. Styles load from `templates/admin/base_site.html`:

1. `static/admin/css/tokens.css` — design tokens (`--kp-*`)
2. `static/admin/css/foundation.css` — Django admin variable bridge + shared UI
3. `static/admin/css/dashboard.css` — analytics layout (uses tokens)

## Brand

- Primary: `#0F5931`
- Neutrals: warm gray-greens for borders and surfaces

## Reusable classes (for later phases)

| Class | Use |
|-------|-----|
| `.kp-card` | Panel / section container |
| `.kp-btn`, `.kp-btn--primary`, `.kp-btn--secondary` | Actions |
| `.kp-badge`, `.kp-badge--success/warning/error/neutral/info` | Status labels |

## Admin language

- All `/admin/*` routes use `sr` via `AdminSerbianLocaleMiddleware`.
- Copy lives in `locale/sr/LC_MESSAGES/django.po` (Serbian **Latin** msgstr).
- Month names in charts/filters use `apps/core/locale_dates.py` (no Cyrillic CLDR months).
- Admin home: operational overview only; **sidebar** is the single navigation map.

## Phase 3 — Forms & tables (operational)

- Styles: `static/admin/css/operational.css`
- Display helpers: `apps/core/admin_display.py`
- Changelist rows: `templates/admin/change_list_results.html`
- Product/order admin: clearer fieldsets, badges, money/stock cells

## Phase 2 — Navigation

- Grouped menu: `apps/core/admin_navigation.py` + `templates/admin/includes/kp_nav_sections.html`
- Sidebar override: `templates/admin/nav_sidebar.html`
- Admin home cards: `templates/admin/index.html`
- Styles: `static/admin/css/navigation.css`, `static/admin/js/kp-nav.js`

Sections: Orders, Products, Categories, Shipping, Analytics, Customers, Newsletter, Settings (+ Other for unmapped models).

## Extending

- Add tokens in `tokens.css` only.
- Map Django admin variables in `foundation.css` (`:root` block).
- Page-specific layout stays in feature CSS (e.g. `dashboard.css`).
- New admin models: add their `app_label.modelname` key to `_NAV_SECTION_SPECS` in `admin_navigation.py`.
