from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from apps.core.middleware import StorefrontDefaultSerbianMiddleware


class StorefrontDefaultSerbianMiddlewareTests(TestCase):
    def test_first_visit_ignores_accept_language(self) -> None:
        response = self.client.get(
            reverse("core:home"),
            HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.9",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Početna")
        self.assertNotContains(response, ">Home</a>")

    def test_language_cookie_is_respected(self) -> None:
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "en"
        response = self.client.get(
            reverse("core:home"),
            HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.9",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">Home</a>")
        self.assertNotContains(response, ">Početna</a>")

    def test_middleware_forces_sr_without_cookie(self) -> None:
        from django.http import HttpResponse
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get(
            "/proizvodi/",
            HTTP_ACCEPT_LANGUAGE="en",
        )
        request.COOKIES = {}

        def get_response(req):
            return HttpResponse("ok")

        middleware = StorefrontDefaultSerbianMiddleware(get_response)
        middleware(request)
        self.assertEqual(request.LANGUAGE_CODE, "sr")
