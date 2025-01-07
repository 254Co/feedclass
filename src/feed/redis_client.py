import redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        """
        Initializes the Redis client.
        :param host: Redis server hostname (default is localhost).
        :param port: Redis server port (default is 6379).
        :param db: Redis database number (default is 0).
        """
        self.client = redis.Redis(host=host, port=port, db=db)
        self.verify_connection()

    def verify_connection(self):
        """
        Verifies the connection to the Redis server by pinging it.
        """
        try:
            if self.client.ping():
                logging.info("Successfully connected to Redis server.")
        except redis.ConnectionError as e:
            logging.error(f"Failed to connect to Redis server: {e}", exc_info=True)
            raise

# Example usage
if __name__ == "__main__":
    redis_client = RedisClient()