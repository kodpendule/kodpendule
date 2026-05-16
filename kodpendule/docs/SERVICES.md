# Services & Selectors (planned API)

Naming convention: `verb_noun` for services, `get_*` / `list_*` for selectors.

## `apps.orders.services`

| Function | Responsibility |
|----------|----------------|
| `create_order(...)` | Validate cart, snapshot prices/SKU, decrement stock, generate `order_number`, set status `pending` |
| `update_order_status(order, status, user)` | Admin status change + optional customer email hook |
| `cancel_order(order)` | Restore stock if not shipped |

## `apps.cart.services`

| Function | Responsibility |
|----------|----------------|
| `clear_cart(session)` | After successful checkout |
| `merge_session_cart(session, user)` | On login (optional v2) |

## `apps.shipping.selectors`

| Function | Responsibility |
|----------|----------------|
| `get_active_cities()` | Ordered list for checkout dropdown |
| `get_shipping_price(city_id) -> Decimal` | Used in checkout total |

## `apps.products.selectors`

| Function | Responsibility |
|----------|----------------|
| `get_featured_products(limit)` | Homepage |
| `get_recommended_products(limit)` | Homepage |
| `get_sale_products(limit)` | Homepage |
| `get_product_by_slug(slug, language)` | Detail view |
| `list_products(category, filters, page)` | Listing with prefetch |

## `apps.dashboard.selectors`

| Function | Responsibility |
|----------|----------------|
| `get_daily_stats(date)` | Revenue, order count, units sold |
| `get_low_stock_products()` | `stock <= minimum_stock_alert` |
| `get_recent_orders(limit)` | Admin widget |

## `apps.newsletter.services`

| Function | Responsibility |
|----------|----------------|
| `import_subscribers_csv(file)` | Dedupe by email |
| `export_subscribers_csv()` | HttpResponse for admin download |

## Payment providers (`apps.orders.payments`)

```python
class PaymentProvider(Protocol):
    def charge(self, order: Order) -> PaymentResult: ...
    def get_display_name(self) -> str: ...
```

Implementations: `CashOnDeliveryProvider` (v1), stubs for `StripeProvider`, `PayPalProvider`.
