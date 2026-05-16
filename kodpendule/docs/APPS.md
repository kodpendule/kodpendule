# Application Boundaries

Each Django app owns one bounded context. Cross-app imports should go **up** through services/selectors, not circular model imports.

## `apps.core`

**Owns:** Site-wide CMS and SEO helpers.

- `SiteSettings` (singleton)
- `FooterSettings`, `SocialLink`
- `HeroBanner`, `PromoSection`, `HomepageSection` (which product flags appear on home)
- Context processors: footer, cart count, site meta
- Sitemap/robots helpers (Step 14)

**Does not own:** Products, orders, users.

---

## `apps.accounts`

**Owns:** Identity and saved addresses.

- Custom `User` (email login optional; phone for Serbia)
- `CustomerProfile`, `Address` (billing/shipping)
- Login, register, password views
- DRF serializers for “current user” if needed

**Does not own:** Order placement (checkout app calls accounts selectors for saved addresses).

---

## `apps.categories`

**Owns:** Category tree for navigation and homepage grid.

- `Category` with optional `parent`, image, slug, SEO fields (parler)

**Does not own:** Product inventory logic (products FK here).

---

## `apps.products`

**Owns:** Catalog and merchandising flags.

- `Product`, `ProductImage`
- Listing, detail, search/filter views
- Selectors: featured, recommended, on-sale, by category

**Does not own:** Cart totals or order snapshots.

---

## `apps.cart`

**Owns:** Session cart only (v1).

- `Cart` session wrapper (`cart.py`)
- Add/update/remove line views
- No prices stored in session — always resolved from DB at checkout

---

## `apps.checkout`

**Owns:** Checkout UX and validation orchestration.

- Multi-step or single-page checkout form
- Guest / login / register choice
- Delivery date picker, required order notes, flexible delivery flag
- Calls `orders.services.create_order` on success

---

## `apps.orders`

**Owns:** Order lifecycle and payment abstraction.

- `Order`, `OrderItem`, status workflow
- `orders/payments/` — `CashOnDeliveryProvider`, future `StripeProvider`, etc.
- Order tracking (guest: order number + email)
- Order history for authenticated users

---

## `apps.shipping`

**Owns:** Geography-based shipping pricing.

- `City` (or `ShippingLocation`) with price in RSD
- Selector used by checkout (and optional DRF endpoint for live price update)

---

## `apps.dashboard`

**Owns:** Admin-only analytics UI (not storefront).

- Custom `/admin/` index or `/admin/dashboard/`
- Daily revenue, order counts, low stock, recent orders
- Date-filtered stats

Uses selectors from `orders`, `products` — does not duplicate business rules.

---

## `apps.newsletter`

**Owns:** Subscriber list and email marketing prep.

- `Subscriber`, import/export CSV
- `EmailCampaign` model (draft/sent) for future sends
- Admin actions: export emails, bulk import

---

## Dependency Graph (allowed direction)

```
core          → (none)
accounts      → core
categories    → core
products      → categories, core
cart          → products (selectors only)
checkout      → cart, shipping, orders, accounts
orders        → products, accounts, shipping
shipping      → core
dashboard     → orders, products
newsletter    → accounts (optional FK)
```
