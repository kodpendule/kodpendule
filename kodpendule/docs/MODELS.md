# Data Model Plan (Step 2)

Entity-relationship overview for implementation in the next step.

## core

| Model | Key fields |
|-------|----------------|
| `SiteSettings` | singleton: site name, default meta |
| `FooterSettings` | phone, email, address, hours (parler) |
| `SocialLink` | platform, url, order |
| `HeroBanner` | image, link, order, active (parler: title, subtitle) |
| `PromoSection` | image, link, placement, active (parler) |
| `HomepageSection` | type enum: featured / recommended / sale |

## accounts

| Model | Key fields |
|-------|----------------|
| `User` | extends AbstractUser, email optional unique |
| `CustomerProfile` | phone, newsletter opt-in |
| `Address` | user FK, type billing/shipping, street, city, postal |

## categories

| Model | Key fields |
|-------|----------------|
| `Category` | parent self-FK, slug, image, active (parler: name, description, meta) |

## products

| Model | Key fields |
|-------|----------------|
| `Product` | category, slug, sku, price, discount_price, stock, min_stock_alert, flags, active, timestamps (parler: name, descriptions, SEO) |
| `ProductImage` | product FK, image, alt, sort_order |

## cart

| Model | Key fields |
|-------|----------------|
| Session cart | `session['cart']` dict product_id → qty |
| `SavedCart` (optional) | user FK, JSON lines |

## orders

| Model | Key fields |
|-------|----------------|
| `Order` | order_number, user nullable, guest_email, addresses JSON/text, status, payment_method, shipping_city, shipping_price, delivery_date, flexible_delivery, order_notes (required), totals |
| `OrderItem` | order, product, sku snapshot, price, quantity |
| `OrderStatus` | choices: pending → cancelled |

## shipping

| Model | Key fields |
|-------|----------------|
| `City` | name, slug, price (RSD), active |
| `ShippingMethod` | name, description, is_default (future) |

## newsletter

| Model | Key fields |
|-------|----------------|
| `Subscriber` | email unique, active, source, created_at |
| `EmailCampaign` | subject, body, status draft/sent, sent_at (future) |

## Cross-cutting

- **Money:** `DecimalField` max_digits=12, decimal_places=2, currency RSD display
- **Slugs:** `django-extensions` AutoSlugField or save() from translated name
- **Stock:** decremented in `orders.services.create_order`
- **Low stock:** `stock <= minimum_stock_alert` property + dashboard selector
