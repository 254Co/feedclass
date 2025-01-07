import unittest
from src.rss_feed import RssFeed

class TestRssFeedSentimentIntegration(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed("https://example.com/rss")
        self.feed.entries = [
            {
                "title": "Sample Entry 1",
                "summary": "This is a great day!",
                "link": "https://example.com/sample-entry-1",
                "published": "2023-10-01",
                "authors": [],
                "topics": [],
                "sentiment": None,
                "emotion": None,
                "entities": [],
                "translation": None,
                "auto_category": None,
            },
            {
                "title": "Sample Entry 2",
                "summary": "This is a terrible mistake.",
                "link": "https://example.com/sample-entry-2",
                "published": "2023-10-02",
                "authors": [],
                "topics": [],
                "sentiment": None,
                "emotion": None,
                "entities": [],
                "translation": None,
                "auto_category": None,
            }
        ]

    def test_analyze_sentiment(self):
        self.feed.apply_nlp_to_all_entries()
        for entry in self.feed.entries:
            self.assertIsInstance(entry["sentiment"], float)  # Check that the sentiment score is a float
            self.assertTrue(-1 <= entry["sentiment"] <= 1)  # Check that the score is within expected range

if __name__ == "__main__":
    unittest.main()