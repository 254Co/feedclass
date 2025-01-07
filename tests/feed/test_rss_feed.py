import unittest
from datetime import datetime
from src.rss_feed import RssFeed
import time

class TestRssFeed(unittest.TestCase):
    def test_initialization(self):
        feed_url = "https://www.utilitydive.com/feeds/news/"
        title = "Example Feed"
        description = "This is an example RSS feed."
        last_updated = datetime.utcnow()
        entries = []

        rss_feed = RssFeed(feed_url, title, description, last_updated, entries)

        self.assertEqual(rss_feed.feed_url, feed_url)
        self.assertEqual(rss_feed.title, title)
        self.assertEqual(rss_feed.description, description)
        self.assertEqual(rss_feed.last_updated, last_updated)
        self.assertEqual(rss_feed.entries, entries)

    def test_fetch_feed_updates_last_updated(self):
        feed = RssFeed("https://www.utilitydive.com/feeds/news/")  # Use a valid RSS feed URL
        initial_last_updated = feed.last_updated

        # Call the fetch_feed method
        feed.fetch_feed()

        # Check if last_updated has changed
        self.assertNotEqual(initial_last_updated, feed.last_updated)
        self.assertIsNotNone(feed.last_updated)  # Ensure it is not None

if __name__ == '__main__':
    unittest.main()