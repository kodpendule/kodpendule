from django.test import TestCase

from apps.accounts.models import CustomerProfile, User


class UserModelTests(TestCase):
    def test_create_user(self) -> None:
        user = User.objects.create_user(username="ana", email="ana@example.com", password="pass")
        self.assertEqual(user.email, "ana@example.com")

    def test_profile_created_via_signal_not_required(self) -> None:
        user = User.objects.create_user(username="marko", password="pass")
        profile = CustomerProfile.objects.create(user=user, phone="+381601234567")
        self.assertEqual(profile.user, user)
