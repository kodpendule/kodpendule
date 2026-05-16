# URL Map (planned)

Admin and static paths are **outside** `i18n_patterns`. Storefront is prefixed with language (`/en/...`, default Serbian often unprefixed per `PREFIX_DEFAULT_LANGUAGE`).

## Global (non-i18n)

| Path | Handler |
|------|---------|
| `/admin/` | Django admin + custom dashboard |
| `/admin/dashboard/` | `dashboard.views` (stats) |
| `/robots.txt` | `core.views.robots` |
| `/sitemap.xml` | Django sitemap framework |
| `/i18n/setlang/` | Language switch |
| `/media/` | Dev only; production via WhiteNoise/S3 rules |

## Storefront (`i18n_patterns`)

| Path | App | Name |
|------|-----|------|
| `/` | `core` | `home` |
| `/kontakt/` | `core` | `contact` |
| `/kategorije/` | `categories` | `category_list` |
| `/kategorija/<slug>/` | `categories` | `category_detail` |
| `/proizvodi/` | `products` | `product_list` |
| `/proizvod/<slug>/` | `products` | `product_detail` |
| `/korpa/` | `cart` | `cart_detail` |
| `/korpa/dodaj/<pk>/` | `cart` | `cart_add` |
| `/korpa/ukloni/<pk>/` | `cart` | `cart_remove` |
| `/placanje/` | `checkout` | `checkout` |
| `/placanje/uspeh/<order_number>/` | `checkout` | `checkout_success` |
| `/porudzbina/pracenje/` | `orders` | `order_track` |
| `/porudzbina/<order_number>/` | `orders` | `order_detail` |
| `/nalog/porudzbine/` | `orders` | `order_history` |
| `/prijava/` | `accounts` | `login` |
| `/registracija/` | `accounts` | `register` |
| `/odjava/` | `accounts` | `logout` |

## API (DRF, optional prefix `/api/v1/`)

| Path | Purpose |
|------|---------|
| `/api/v1/shipping/price/?city=<id>` | JSON shipping price for checkout |
| `/api/v1/cart/` | Future headless cart |

English URL slugs can mirror Serbian paths under `/en/` or use translated slugs in Step 9.
