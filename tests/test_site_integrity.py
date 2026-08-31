from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
HTML_PAGES = ("index.html", "research.html")


class ReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        attribute = {
            "a": "href",
            "img": "src",
            "link": "href",
            "script": "src",
        }.get(tag)
        if attribute and attributes.get(attribute):
            self.references.append(attributes[attribute])


class SiteIntegrityTests(unittest.TestCase):
    def test_all_internal_page_assets_and_links_exist(self):
        missing = []
        for page_name in HTML_PAGES:
            parser = ReferenceParser()
            parser.feed((ROOT / page_name).read_text())
            for reference in parser.references:
                parsed = urlparse(reference)
                if parsed.scheme or reference.startswith("//"):
                    continue
                target = reference.split("#", 1)[0].split("?", 1)[0]
                if target and not (ROOT / target).exists():
                    missing.append(f"{page_name}: {reference}")

        self.assertEqual(missing, [])

    def test_sitemap_and_robots_use_the_canonical_domain(self):
        domain = (ROOT / "CNAME").read_text().strip()
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap = ET.parse(ROOT / "sitemap.xml")
        locations = [element.text for element in sitemap.findall("sm:url/sm:loc", namespace)]

        self.assertEqual(
            locations,
            [f"https://{domain}/", f"https://{domain}/research.html"],
        )
        self.assertIn(
            f"Sitemap: https://{domain}/sitemap.xml",
            (ROOT / "robots.txt").read_text(),
        )


if __name__ == "__main__":
    unittest.main()
