from django.test import SimpleTestCase

from apps.dashboard.apps import DashboardConfig


class DashboardConfigScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(DashboardConfig.name, "apps.dashboard")
