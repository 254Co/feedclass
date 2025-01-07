import unittest
from src.rss_feed import RssFeed

class TestRssFeedTranslationIntegration(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed("https://example.com/rss")
        self.entry = {
            "title": "Sample Entry",
            "summary": "This is a sample summary."
        }

    def test_translate_entry(self):
        translated_summary = self.feed.translate_entry(self.entry, target_language="es")
        self.assertIsInstance(translated_summary, str)  # Check if the output is a string
        self.assertNotEqual(translated_summary, self.entry['summary'])  # Ensure translation is different

if __name__ == "__main__":
    unittest.main()