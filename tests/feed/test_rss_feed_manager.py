import unittest
from src.rss_feed import RssFeed
from src.rss_feed_manager import RssFeedManager
import logging

class TestRssFeedManager(unittest.TestCase):
    def setUp(self):
        self.manager = RssFeedManager()
        self.feed = RssFeed("https://example.com/rss")
        self.manager.add_feed(self.feed)

    def test_initialization(self):
        self.assertEqual(self.manager.feeds, {})  # Check that feeds dictionary is empty

    def test_add_feed(self):
        feed = RssFeed("https://example.com/rss", "Example Feed")
        self.manager.add_feed(feed)
        self.assertIn(feed.feed_url, self.manager.feeds)  # Check that the feed is added

    def test_remove_feed(self):
        feed = RssFeed("https://example.com/rss", "Example Feed")
        self.manager.add_feed(feed)
        self.manager.remove_feed(feed.feed_url)
        self.assertNotIn(feed.feed_url, self.manager.feeds)  # Check that the feed is removed

        # Test removing a feed that does not exist
        logging.info("Attempting to remove a non-existent feed.")
        self.manager.remove_feed("https://nonexistent.com/rss")  # Should log a warning

    def test_list_feeds(self):
        feed1 = RssFeed("https://example.com/rss", "Example Feed 1")
        feed2 = RssFeed("https://another.com/rss", "Example Feed 2")
        self.manager.add_feed(feed1)
        self.manager.add_feed(feed2)
        feeds = self.manager.list_feeds()
        self.assertEqual(len(feeds), 2)  # Check that the correct number of feeds is returned
        self.assertIn(feed1.feed_url, feeds)
        self.assertIn(feed2.feed_url, feeds)

    def test_feed_hash_changes_on_entry_modification(self):
        initial_hash = self.feed._compute_feed_hash()

        # Modify an entry
        self.feed.entries.append({
            "title": "New Title",
            "link": "https://example.com/new",
            "summary": "Updated summary.",
            "published": "2023-01-01T00:00:00Z",
            "authors": [],
            "topics": [],
            "sentiment": None,
            "emotion": None,
            "entities": [],
            "translation": None,
            "auto_category": None,
        })

        new_hash = self.feed._compute_feed_hash()

        self.assertNotEqual(initial_hash, new_hash, "Hash should change when entries are modified.")

if __name__ == "__main__":
    unittest.main()