import unittest
from src.elasticsearch_client import ElasticsearchClient

class TestElasticsearchClient(unittest.TestCase):
    def setUp(self):
        self.es_client = ElasticsearchClient()
        self.index_name = "rss_entries"
        self.entry = {
            "title": "Test Entry",
            "link": "http://example.com/test-entry",
            "summary": "This is a test summary.",
            "published": "2023-01-01T00:00:00Z",
            "authors": ["Author 1"],
            "topics": ["Test"],
            "sentiment": 0.5,
            "emotion": {"joy": 0.5, "sadness": 0.0},
            "entities": ["Test Entity"],
            "translation": "Translated text",
            "auto_category": "Test Category",
        }

    def test_upsert_entry(self):
        # Insert the entry
        self.es_client.upsert_entry(self.index_name, self.entry)
        # Check if the entry is in the index
        response = self.es_client.client.get(index=self.index_name, id=self.entry["title"])
        self.assertEqual(response["_source"]["title"], self.entry["title"])

        # Update the entry
        updated_entry = self.entry.copy()
        updated_entry["summary"] = "This is an updated test summary."
        self.es_client.upsert_entry(self.index_name, updated_entry)

        # Check if the updated entry reflects the change
        response = self.es_client.client.get(index=self.index_name, id=self.entry["title"])
        self.assertEqual(response["_source"]["summary"], updated_entry["summary"])

if __name__ == "__main__":
    unittest.main()