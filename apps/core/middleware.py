"""Project middleware."""

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils import translation
from django.utils.translation import check_for_language


def _language_from_cookie(request) -> str | None:
    code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if code and check_for_language(code):
        return code
    return None


class StorefrontDefaultSerbianMiddleware:
    """
    Storefront defaults to Serbian for new visitors.

    LocaleMiddleware may pick English from Accept-Language before LANGUAGE_CODE.
    If the user has not chosen a language via /jezik/ (language cookie), force sr.
    """

    ADMIN_PREFIX = "/admin/"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(self.ADMIN_PREFIX):
            if _language_from_cookie(request) is None:
                translation.activate("sr")
                request.LANGUAGE_CODE = "sr"
        return self.get_response(request)


class AdminSerbianLocaleMiddleware:
    """
    Force Serbian for Django admin URLs.

    Storefront language (LocaleMiddleware, session, /jezik/) is unchanged.
    Must be listed after django.middleware.locale.LocaleMiddleware.
    """

    ADMIN_PREFIX = "/admin/"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.ADMIN_PREFIX):
            translation.activate("sr")
            request.LANGUAGE_CODE = "sr"
        response = self.get_response(request)
        return response


class StorefrontLocalizedUrlMiddleware:
    """
    Redirect storefront URLs to the path that matches the active language.

    Example: English cookie + /kategorije/ -> /categories/
    """

    ADMIN_PREFIX = "/admin/"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.ADMIN_PREFIX):
            return self.get_response(request)

        from apps.core.storefront_urls import resolve_storefront_route, shop_reverse
        from apps.core.utils import get_shop_language

        route = resolve_storefront_route(request.path)
        if route is None:
            return self.get_response(request)

        active_language = get_shop_language(request)
        if route.language == active_language:
            return self.get_response(request)

        # Never redirect POST/PUT/PATCH/DELETE: browsers may follow 301/302 with GET,
        # which drops checkout form data and silently fails order placement.
        if request.method not in ("GET", "HEAD"):
            return self.get_response(request)

        kwargs = dict(route.kwargs)
        if "slug" in kwargs:
            from apps.core.storefront_urls import _slug_for_target_language

            kwargs["slug"] = _slug_for_target_language(
                route.viewname,
                kwargs["slug"],
                active_language,
            )

        localized_path = shop_reverse(
            route.viewname,
            language=active_language,
            **kwargs,
        )
        if localized_path == request.path:
            return self.get_response(request)

        query = request.META.get("QUERY_STRING", "")
        target = localized_path
        if query:
            target = f"{localized_path}?{query}"
        return HttpResponsePermanentRedirect(target)
