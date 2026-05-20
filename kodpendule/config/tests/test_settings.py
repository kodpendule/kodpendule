from django.test import SimpleTestCase


class LocalSettingsTests(SimpleTestCase):
    def test_local_uses_sqlite(self) -> None:
        from config.settings import local

        engine = local.DATABASES["default"]["ENGINE"]
        self.assertIn("sqlite", engine)

    def test_local_database_configured(self) -> None:
        from config.settings import local

        self.assertIn("default", local.DATABASES)


class BaseSettingsTests(SimpleTestCase):
    def test_auth_user_model(self) -> None:
        from config.settings import base

        self.assertEqual(base.AUTH_USER_MODEL, "accounts.User")

    def test_parler_languages(self) -> None:
        from config.settings import base

        codes = [lang["code"] for lang in base.PARLER_LANGUAGES[None]]
        self.assertEqual(codes, ["sr", "en"])
