import logging
from elasticsearch import Elasticsearch, NotFoundError

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

# Example usage
if __name__ == "__main__":
    es_client = ElasticsearchClient()
    es_client.test_query()