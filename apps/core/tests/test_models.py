from django.test import TestCase

from apps.core.models import FooterSettings, HomepageSection, HomepageSectionType, SiteSettings


class CoreModelTests(TestCase):
    def test_site_settings_singleton(self) -> None:
        first = SiteSettings.load()
        second = SiteSettings.load()
        self.assertEqual(first.pk, 1)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_footer_settings_singleton(self) -> None:
        footer = FooterSettings.load()
        self.assertEqual(footer.pk, 1)

    def test_homepage_section_unique_type(self) -> None:
        HomepageSection.objects.create(
            section_type=HomepageSectionType.FEATURED,
            max_products=8,
        )
        with self.assertRaises(Exception):
            HomepageSection.objects.create(
                section_type=HomepageSectionType.FEATURED,
            )
