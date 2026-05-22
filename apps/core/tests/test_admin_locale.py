from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from apps.core.middleware import AdminSerbianLocaleMiddleware


class AdminSerbianLocaleMiddlewareTests(TestCase):
    def test_admin_path_uses_serbian(self) -> None:
        from django.http import HttpResponse

        factory = RequestFactory()
        request = factory.get("/admin/")
        request.LANGUAGE_CODE = "en"

        def get_response(req):
            return HttpResponse("ok")

        middleware = AdminSerbianLocaleMiddleware(get_response)
        middleware(request)
        self.assertEqual(request.LANGUAGE_CODE, "sr")

    def test_storefront_path_not_forced(self) -> None:
        from django.http import HttpResponse

        factory = RequestFactory()
        request = factory.get("/proizvodi/")
        request.LANGUAGE_CODE = "en"

        def get_response(req):
            return HttpResponse("ok")

        middleware = AdminSerbianLocaleMiddleware(get_response)
        middleware(request)
        self.assertEqual(request.LANGUAGE_CODE, "en")


class AdminBrandingTests(TestCase):
    def test_admin_index_uses_serbian_site_header(self) -> None:
        User = get_user_model()
        User.objects.create_superuser("admin", "admin@test.com", "pass")
        self.client.login(username="admin", password="pass")
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kod Pendule — administracija")
