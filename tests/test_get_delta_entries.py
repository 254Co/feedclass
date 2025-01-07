import unittest
from src.rss_feed import RssFeed

class TestRssFeedDeltaEntries(unittest.TestCase):
    def setUp(self):
        self.feed = RssFeed("https://example.com/rss")
        self.feed.entries = [
            {"title": "First Entry", "summary": "This is the first entry."},
            {"title": "Second Entry", "summary": "This is the second entry."},
        ]
        self.old_hash = self.feed._compute_feed_hash()

    def test_no_changes(self):
        new_entries = self.feed.get_delta_entries(self.old_hash)
        self.assertEqual(new_entries, [], "Expected no new entries.")

    def test_new_entry(self):
        self.feed.entries.append({"title": "Third Entry", "summary": "This is the third entry."})
        new_entries = self.feed.get_delta_entries(self.old_hash)
        self.assertEqual(len(new_entries), 1, "Expected one new entry.")
        self.assertEqual(new_entries[0]["title"], "Third Entry")

    def test_changed_entry(self):
        self.feed.entries[0]["summary"] = "This is the updated first entry."
        new_entries = self.feed.get_delta_entries(self.old_hash)
        self.assertEqual(len(new_entries), 1, "Expected one changed entry.")
        self.assertEqual(new_entries[0]["title"], "First Entry")

if __name__ == "__main__":
    unittest.main()