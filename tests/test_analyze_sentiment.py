import unittest
from src.rss_feed import RssFeed

class TestRssFeedSentiment(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed("https://example.com/rss")
        # Add a sample entry to test sentiment analysis
        self.entry = {
            "title": "Sample Entry",
            "summary": "This is a sample summary for sentiment analysis.",
            "link": "https://example.com/sample-entry",
            "published": "2023-10-01",
            "authors": [],
            "topics": [],
            "sentiment": None,
            "emotion": None,
            "entities": [],
            "translation": None,
            "auto_category": None,
        }

    def test_analyze_sentiment(self):
        score = self.feed.analyze_sentiment(self.entry)
        self.assertIsInstance(score, float)  # Check that the score is a float
        self.assertEqual(score, 0.5)  # Check that the score is the expected fixed value

if __name__ == "__main__":
    unittest.main()