from django.test import TestCase


class SeoEndpointTests(TestCase):
    def test_robots_txt_lists_disallows_and_sitemap(self) -> None:
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        body = response.content.decode()
        self.assertIn("Disallow: /admin/", body)
        self.assertIn("Disallow: /korpa/", body)
        self.assertIn("Sitemap: http://testserver/sitemap.xml", body)

    def test_sitemap_xml_returns_urlset(self) -> None:
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response["Content-Type"])
        self.assertIn(b"<urlset", response.content)
        self.assertIn(b"/proizvodi/", response.content)
        self.assertIn(b"/kategorije/", response.content)
