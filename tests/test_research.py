from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAPER_FILENAME = "Usenko_Large_Small_Depositors.pdf"
PAPER_TITLE = "Large depositors, retail depositors, and the deposits channel of monetary policy"
HIDDEN_PAPER_TITLE = "Inflation, Taxation, and Corporate Investment in the U.S. during the Great Inflation"


def normalize(text):
    return " ".join(text.split())


class ResearchPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_sidebar = False
        self.sidebar_text = []
        self.sidebar_images = []
        self.headings = []
        self.links = {}
        self.visible_text = []
        self.comments = []
        self._heading = None
        self._link = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if tag == "aside" and "sidebar" in classes:
            self.in_sidebar = True
        elif self.in_sidebar and tag == "img":
            self.sidebar_images.append(attributes.get("src"))

        if tag == "h2":
            self._heading = ""
        elif tag == "a":
            self._link = {"href": attributes.get("href"), "label": ""}

    def handle_endtag(self, tag):
        if tag == "aside":
            self.in_sidebar = False
        elif tag == "h2" and self._heading is not None:
            self.headings.append(normalize(self._heading))
            self._heading = None
        elif tag == "a" and self._link is not None:
            self.links[normalize(self._link["label"])] = self._link["href"]
            self._link = None

    def handle_data(self, data):
        text = normalize(data)
        if text:
            self.visible_text.append(text)
            if self.in_sidebar:
                self.sidebar_text.append(text)
        if self._heading is not None:
            self._heading += data
        if self._link is not None:
            self._link["label"] += data

    def handle_comment(self, data):
        self.comments.append(normalize(data))


class ResearchPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = ResearchPageParser()
        cls.parser.feed((ROOT / "research.html").read_text())
        cls.visible_text = " ".join(cls.parser.visible_text)
        cls.comment_text = " ".join(cls.parser.comments)

    def test_sidebar_contains_only_the_portrait(self):
        self.assertEqual(self.parser.sidebar_text, [])
        self.assertEqual(self.parser.sidebar_images, ["avatar.JPG"])

    def test_current_working_paper_is_visible_and_linked(self):
        self.assertEqual(self.parser.headings, ["Working Papers", "Publications"])
        self.assertEqual(self.parser.links[PAPER_TITLE], PAPER_FILENAME)
        self.assertTrue((ROOT / PAPER_FILENAME).is_file())
        self.assertFalse((ROOT / "jmp_Usenko.pdf").exists())
        self.assertIn("(November 2026)", self.visible_text)
        self.assertNotIn("Updated November 2026", self.visible_text)

    def test_previous_working_paper_is_commented_out(self):
        self.assertNotIn(HIDDEN_PAPER_TITLE, self.visible_text)
        self.assertIn(HIDDEN_PAPER_TITLE, self.comment_text)

if __name__ == "__main__":
    unittest.main()
