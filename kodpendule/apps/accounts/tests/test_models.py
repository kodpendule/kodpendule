from django.test import TestCase

from apps.accounts.models import Address, AddressType, CustomerProfile, User


class UserModelTests(TestCase):
    def test_create_user(self) -> None:
        user = User.objects.create_user(username="ana", email="ana@example.com", password="pass")
        self.assertEqual(user.email, "ana@example.com")

    def test_profile_created_via_signal_not_required(self) -> None:
        user = User.objects.create_user(username="marko", password="pass")
        profile = CustomerProfile.objects.create(user=user, phone="+381601234567")
        self.assertEqual(profile.user, user)


class AddressModelTests(TestCase):
    def test_address_str(self) -> None:
        user = User.objects.create_user(username="pera", password="pass")
        address = Address.objects.create(
            user=user,
            address_type=AddressType.SHIPPING,
            street_line_1="Bulevar 1",
            city="Novi Sad",
            postal_code="21000",
        )
        self.assertIn("Novi Sad", str(address))
