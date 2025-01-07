import logging
from elasticsearch import Elasticsearch, NotFoundError
from typing import Dict

class ElasticsearchClient:
    def __init__(self, hosts=None):
        """
        Initializes the Elasticsearch client.
        :param hosts: List of Elasticsearch server addresses.
        """
        self.hosts = hosts or ['localhost:9200']
        self.client = Elasticsearch(self.hosts)
        self.verify_connection()

    def verify_connection(self):
        """
        Verifies the connection to the Elasticsearch server by performing a simple query.
        """
        try:
            if self.client.ping():
                logging.info("Successfully connected to Elasticsearch.")
            else:
                logging.error("Elasticsearch ping failed.")
        except Exception as e:
            logging.error(f"Failed to connect to Elasticsearch: {e}", exc_info=True)
            raise

    def test_query(self):
        """
        Performs a simple query to test the connection.
        """
        try:
            response = self.client.cat.indices(format="json")  # Get list of indices
            logging.info("Indices in Elasticsearch: %s", response)
            return response
        except NotFoundError as e:
            logging.error("Elasticsearch index not found: %s", e)
            return None
        except Exception as e:
            logging.error(f"Error performing query: {e}", exc_info=True)
            return None

    def upsert_entry(self, index_name: str, entry: Dict) -> None:
        """
        Inserts or updates an RSS feed entry in the Elasticsearch index.
        :param index_name: The name of the Elasticsearch index.
        :param entry: The entry dictionary containing feed data.
        """
        try:
            # Use the title as the unique ID for the document
            document_id = entry["title"]
            # Prepare the document data for Elasticsearch
            document = {
                "title": entry["title"],
                "link": entry["link"],
                "summary": entry["summary"],
                "published": entry["published"],
                "authors": entry["authors"],
                "topics": entry["topics"],
                "sentiment": entry["sentiment"],
                "emotion": entry["emotion"],
                "entities": entry["entities"],
                "translation": entry["translation"],
                "auto_category": entry["auto_category"],
            }

            # Perform the upsert operation
            self.client.index(index=index_name, id=document_id, body=document, op_type='update')
            logging.info(f"Upserted entry '{document_id}' into index '{index_name}'.")
        except Exception as e:
            logging.error(f"Error upserting entry '{entry['title']}': {e}", exc_info=True)

# Example usage
if __name__ == "__main__":
    es_client = ElasticsearchClient()
    es_client.test_query()