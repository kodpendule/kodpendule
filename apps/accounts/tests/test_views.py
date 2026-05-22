from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from apps.accounts.forms import LoginForm
from apps.accounts.models import CustomerProfile
from apps.accounts.views import UserLoginView, UserRegisterView

User = get_user_model()


def _apply_middleware(request) -> None:
    """Attach session and user to a bare RequestFactory request."""
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()
    auth_middleware = AuthenticationMiddleware(lambda req: None)
    auth_middleware.process_request(request)
    message_middleware = MessageMiddleware(lambda req: None)
    message_middleware.process_request(request)


class AuthViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.factory = RequestFactory()

    def _get_view(self, view_class, path: str):
        request = self.factory.get(path)
        _apply_middleware(request)
        return view_class.as_view()(request)

    def test_register_page_loads(self) -> None:
        response = self._get_view(UserRegisterView, "/registracija/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self) -> None:
        response = self._get_view(UserLoginView, "/prijava/")
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_profile(self) -> None:
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "novi_korisnik",
                "email": "novi@example.com",
                "first_name": "Novi",
                "last_name": "Korisnik",
                "phone": "+381601112233",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
                "newsletter_opt_in": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:home"))
        user = User.objects.get(username="novi_korisnik")
        self.assertEqual(user.email, "novi@example.com")
        profile = CustomerProfile.objects.get(user=user)
        self.assertEqual(profile.phone, "+381601112233")
        self.assertTrue(profile.newsletter_opt_in)

    def test_register_logs_user_in(self) -> None:
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "logged_in",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
            },
        )
        self.assertTrue(User.objects.filter(username="logged_in").exists())
        self.assertTrue(
            self.client.session.get("_auth_user_id"),
            "User should be logged in after registration.",
        )

    def test_login_success(self) -> None:
        User.objects.create_user(username="pera", password="SecurePass123!")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "pera", "password": "SecurePass123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:home"))

    def test_login_invalid(self) -> None:
        User.objects.create_user(username="pera", password="SecurePass123!")
        form = LoginForm(data={"username": "pera", "password": "wrong"})
        self.assertFalse(form.is_valid())

    def test_logout(self) -> None:
        User.objects.create_user(username="pera", password="SecurePass123!")
        self.client.login(username="pera", password="SecurePass123!")
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_authenticated_user_redirected_from_register(self) -> None:
        User.objects.create_user(username="pera", password="SecurePass123!")
        self.client.login(username="pera", password="SecurePass123!")
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:home"))
