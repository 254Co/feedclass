import unittest
from src.rss_feed import RssFeed

class TestRssFeed(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed(feed_url="https://example.com/rss")
        self.feed.entries = [
            {
                "title": "Sample Entry",
                "summary": "This is a summary of the sample entry."
            }
        ]

    def test_summarize_entry(self):
        summary = self.feed.summarize_entry(self.feed.entries[0])
        expected_summary = "Sample Entry: This is a summary of the sample entry."
        self.assertEqual(summary, expected_summary)

if __name__ == '__main__':
    unittest.main()