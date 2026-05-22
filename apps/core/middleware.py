"""Project middleware."""

from django.utils import translation


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
