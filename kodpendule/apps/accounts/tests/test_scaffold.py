from django.test import SimpleTestCase

from apps.accounts.apps import AccountsConfig


class AccountsScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(AccountsConfig.name, "apps.accounts")
