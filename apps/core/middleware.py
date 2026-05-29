"""Project middleware."""

from django.conf import settings
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
