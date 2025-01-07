import unittest
from unittest.mock import patch
from src.rss_feed import RssFeed
from src.redis_client import RedisClient

class TestRssFeedTranslationCaching(unittest.TestCase):
    def setUp(self):
        self.redis_client = RedisClient()
        self.feed = RssFeed("https://example.com/rss", redis_client=self.redis_client)
        self.entry = {
            "title": "Sample Entry",
            "summary": "This is a sample summary."
        }

    @patch('src.rss_feed.Translator')
    def test_translation_caching(self, mock_translator):
        # Set up the mock translation response
        mock_translator.return_value.translate.return_value.text = "Esta es un resumen de muestra."

        # First translation should go to the translation service
        translated_summary_1 = self.feed.translate_entry(self.entry, target_language="es")
        self.assertEqual(translated_summary_1, "Esta es un resumen de muestra.")

        # Second translation should be retrieved from the cache
        translated_summary_2 = self.feed.translate_entry(self.entry, target_language="es")
        self.assertEqual(translated_summary_2, "Esta es un resumen de muestra.")
        self.assertEqual(translated_summary_1, translated_summary_2)  # Ensure both translations are the same

if __name__ == "__main__":
    unittest.main()