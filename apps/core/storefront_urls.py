"""Language-specific storefront URL paths (sr / en without /en/ prefix)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.urls import NoReverseMatch, path, resolve, reverse
from django.urls.exceptions import Resolver404

from django.utils.functional import lazy

from apps.core.utils import get_shop_language

ROUTE_PREFIX = "__shop__"
STOREFRONT_ROUTE_PATHS: list[str] = []


@dataclass(frozen=True)
class RouteMatch:
    viewname: str
    kwargs: dict
    language: str


def _internal_name(viewname: str, language: str) -> str:
    return f"{ROUTE_PREFIX}{viewname.replace(':', '__')}__{language}"


def _viewname_from_internal(name: str) -> tuple[str, str] | None:
    if not name.startswith(ROUTE_PREFIX):
        return None
    body = name[len(ROUTE_PREFIX) :]
    if "__sr" not in body and "__en" not in body:
        return None
    for language in dict(settings.LANGUAGES):
        suffix = f"__{language}"
        if body.endswith(suffix):
            route_body = body[: -len(suffix)]
            if "__" in route_body:
                app_name, _, name = route_body.partition("__")
                if not app_name or not name:
                    return None
                viewname = f"{app_name}:{name}"
            else:
                viewname = route_body
            if not viewname:
                return None
            return viewname, language
    return None


def localized_path(
    viewname: str,
    view,
    *,
    sr: str,
    en: str,
):
    """Register Serbian and English paths for the same named storefront route."""
    patterns = {"sr": sr, "en": en}
    for pattern in patterns.values():
        if pattern:
            STOREFRONT_ROUTE_PATHS.append(pattern)
    routes = []
    for language, pattern in patterns.items():
        routes.append(
            path(
                pattern,
                view,
                name=_internal_name(viewname, language),
            )
        )
    return routes


def _reverse_localized(viewname: str, language: str, **kwargs) -> str:
    internal = _internal_name(viewname, language)
    if ":" in viewname:
        app_name = viewname.split(":", 1)[0]
        return reverse(f"{app_name}:{internal}", kwargs=kwargs)
    return reverse(internal, kwargs=kwargs)


def shop_reverse(
    viewname: str,
    *,
    language: str | None = None,
    **kwargs,
) -> str:
    lang = language or get_shop_language()
    if lang not in dict(settings.LANGUAGES):
        lang = settings.PARLER_DEFAULT_LANGUAGE_CODE
    return _reverse_localized(viewname, lang, **kwargs)


shop_reverse_lazy = lazy(shop_reverse, str)


def resolve_storefront_route(path: str) -> RouteMatch | None:
    try:
        match = resolve(path)
    except Resolver404:
        return None
    parsed = _viewname_from_internal(match.url_name or "")
    if parsed is None:
        return None
    viewname, language = parsed
    return RouteMatch(viewname=viewname, kwargs=dict(match.kwargs), language=language)


def _slug_for_target_language(viewname: str, slug: str, target_language: str) -> str:
    if viewname == "categories:detail":
        from apps.categories.selectors import get_category_by_slug
        from apps.core.slugs import localized_slug

        category = get_category_by_slug(slug)
        if category is not None:
            return localized_slug(category, target_language) or slug
    if viewname == "products:detail":
        from apps.core.slugs import localized_slug
        from apps.products.selectors import get_product_by_slug

        product = get_product_by_slug(slug)
        if product is not None:
            return localized_slug(product, target_language) or slug
    if viewname == "cart:add_by_slug":
        from apps.core.slugs import localized_slug
        from apps.products.selectors import get_product_by_slug

        product = get_product_by_slug(slug)
        if product is not None:
            return localized_slug(product, target_language) or slug
    return slug


def translate_storefront_url(url: str, target_language: str) -> str:
    """Map a storefront URL to the equivalent path in another language."""
    if target_language not in dict(settings.LANGUAGES):
        target_language = settings.PARLER_DEFAULT_LANGUAGE_CODE

    parts = urlsplit(url)
    route = resolve_storefront_route(parts.path)
    if route is None:
        return url

    kwargs = dict(route.kwargs)
    if "slug" in kwargs:
        kwargs["slug"] = _slug_for_target_language(
            route.viewname,
            kwargs["slug"],
            target_language,
        )

    try:
        new_path = shop_reverse(route.viewname, language=target_language, **kwargs)
    except NoReverseMatch:
        return url

    return urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))


def storefront_paths_for_robots() -> list[str]:
    """Unique path prefixes for robots.txt Disallow rules."""
    prefixes: set[str] = set()
    for pattern in STOREFRONT_ROUTE_PATHS:
        segment = pattern.strip("/").split("/")[0]
        if segment:
            prefixes.add(f"/{segment}/")
    return sorted(prefixes)
