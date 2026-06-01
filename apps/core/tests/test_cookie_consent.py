"""Cookie consent banner and Google Maps gating."""

from django.conf import settings
from django.test import TestCase

from apps.core.cookie_consent import (
    CONSENT_LEVEL_ALL,
    CONSENT_LEVEL_ESSENTIAL,
    parse_consent_cookie,
)
from apps.core.storefront_urls import shop_reverse


class CookieConsentParserTests(TestCase):
    def test_parse_valid_levels(self) -> None:
        self.assertEqual(parse_consent_cookie("v1:all"), CONSENT_LEVEL_ALL)
        self.assertEqual(parse_consent_cookie("v1:essential"), CONSENT_LEVEL_ESSENTIAL)

    def test_parse_invalid(self) -> None:
        self.assertIsNone(parse_consent_cookie(""))
        self.assertIsNone(parse_consent_cookie("v2:all"))
        self.assertIsNone(parse_consent_cookie("invalid"))

    def test_maps_allowed(self) -> None:
        self.client.cookies[settings.COOKIE_CONSENT_COOKIE_NAME] = "v1:all"
        response = self.client.get(shop_reverse("core:home"))
        self.assertTrue(response.context["cookie_consent_maps"])

        self.client.cookies[settings.COOKIE_CONSENT_COOKIE_NAME] = "v1:essential"
        response = self.client.get(shop_reverse("core:home"))
        self.assertFalse(response.context["cookie_consent_maps"])


class CookieBannerViewTests(TestCase):
    def test_banner_shown_without_consent_cookie(self) -> None:
        response = self.client.get(shop_reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "shop-cookie-banner")
        self.assertContains(response, "js-cookie-consent-all")
        self.assertFalse(response.context["cookie_consent_given"])

    def test_banner_hidden_after_essential_consent(self) -> None:
        self.client.cookies[settings.COOKIE_CONSENT_COOKIE_NAME] = "v1:essential"
        response = self.client.get(shop_reverse("core:home"))
        self.assertNotContains(response, 'id="shop-cookie-banner"')
        self.assertTrue(response.context["cookie_consent_given"])

    def test_map_iframe_only_with_all_consent(self) -> None:
        response = self.client.get(shop_reverse("core:contact"))
        self.assertContains(response, "shop-map--placeholder")
        self.assertNotContains(response, "shop-map__iframe")

        self.client.cookies[settings.COOKIE_CONSENT_COOKIE_NAME] = "v1:all"
        response = self.client.get(shop_reverse("core:contact"))
        self.assertContains(response, "shop-map__iframe")
        self.assertNotContains(response, "shop-map--placeholder")

    def test_footer_cookie_settings_link(self) -> None:
        self.client.cookies[settings.COOKIE_CONSENT_COOKIE_NAME] = "v1:all"
        response = self.client.get(shop_reverse("core:home"))
        self.assertContains(response, "js-cookie-settings")
