import unittest
from src.rss_feed import RssFeed

class TestRssFeedTranslation(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed("https://example.com/rss")
        self.entry = {
            "title": "Sample Entry",
            "summary": "This is a sample summary."
        }

    def test_translate_entry(self):
        translated_summary = self.feed.translate_entry(self.entry, target_language="es")
        expected_output = "[TRANSLATED to es] This is a sample summary."
        self.assertEqual(translated_summary, expected_output)

if __name__ == "__main__":
    unittest.main()