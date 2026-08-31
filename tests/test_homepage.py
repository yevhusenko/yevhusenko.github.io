from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HomepageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_sidebar = False
        self.sidebar_text = []
        self.sidebar_images = []
        self.contact_title = ""
        self.profile_links = {}
        self._in_contact_title = False
        self._profile_link = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if tag == "aside" and "sidebar" in classes:
            self.in_sidebar = True
        elif self.in_sidebar and tag == "img":
            self.sidebar_images.append(attributes.get("src"))

        if tag == "h2" and "contact-title" in classes:
            self._in_contact_title = True

        if tag == "a" and "profile-link" in classes:
            self._profile_link = {
                "href": attributes.get("href"),
                "label": "",
            }

    def handle_endtag(self, tag):
        if tag == "aside":
            self.in_sidebar = False
        elif tag == "h2" and self._in_contact_title:
            self._in_contact_title = False
        elif tag == "a" and self._profile_link is not None:
            label = self._profile_link["label"].strip()
            self.profile_links[label] = self._profile_link["href"]
            self._profile_link = None

    def handle_data(self, data):
        text = data.strip()
        if self.in_sidebar and text:
            self.sidebar_text.append(text)
        if self._in_contact_title:
            self.contact_title += data
        if self._profile_link is not None:
            self._profile_link["label"] += data


class HomepageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = HomepageParser()
        cls.parser.feed((ROOT / "index.html").read_text())

    def test_sidebar_contains_only_the_portrait(self):
        self.assertEqual(self.parser.sidebar_text, [])
        self.assertEqual(self.parser.sidebar_images, ["avatar.JPG"])

    def test_profile_links_have_accessible_labels_and_destinations(self):
        self.assertEqual(self.parser.contact_title.strip(), "Get in touch:")
        self.assertEqual(
            self.parser.profile_links,
            {
                "Email": "mailto:yevhenii.usenko@colorado.edu",
                "LinkedIn": "https://www.linkedin.com/in/yevhenii-usenko/",
            },
        )


if __name__ == "__main__":
    unittest.main()
