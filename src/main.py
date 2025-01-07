import logging
import subprocess

from feed.rss_feed_manager import RssFeedManager
from feed.redis_client import RedisClient
from feed.kafka_producer import KafkaProducerService
from feed.kafka_consumer import KafkaConsumerService
from feed.elasticsearch_client import ElasticsearchClient

logging.basicConfig(level=logging.INFO)

def start_kafka():
    logging.info("Starting Kafka...")
    process = subprocess.Popen(['bin/kafka-server-start.sh', 'config/server.properties'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        logging.error(f"Kafka failed to start: {stderr.decode().strip()}")
    else:
        logging.info("Kafka started successfully.")

def create_topic():
    logging.info("Creating topic 'test'...")
    process = subprocess.Popen(['bin/kafka-topics.sh', '--create', '--topic', 'test', '--bootstrap-server', 'localhost:9092', '--partitions', '1', '--replication-factor', '1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        logging.error(f"Failed to create topic: {stderr.decode().strip()}")
    else:
        logging.info("Topic 'test' created successfully.")

def main():
    logging.info("Starting the application...")
    # Initialize Kafka producer service
    kafka_producer = KafkaProducerService(bootstrap_servers='localhost:9092')

    # Pass the Kafka producer to the RssFeedManager
    feed_manager = RssFeedManager(kafka_producer=kafka_producer)
    logging.info("RssFeedManager initialized.")

    # Initialize NLP processor
    nlp_processor = NlpProcessor(feed_manager)  # Initialize NLP processor with feed manager
    kafka_consumer = KafkaConsumerService(topic="feed-events", nlp_processor=nlp_processor)  # Pass NLP processor to consumer

    # Example of adding a feed (this can be modified as needed)
    try:
        new_feed = RssFeed("https://example.com/rss", "Example Feed")  # Create a new RssFeed instance
        feed_manager.add_feed(new_feed)  # Register the new feed
        logging.info(f"Feed added: {new_feed.feed_url}")

        # Attempting to list all feeds
        logging.info("Attempting to list all feeds.")
        feeds = feed_manager.list_feeds()
        logging.info(f"Current feeds listed: {feeds}")

        # Start Kafka and create topic
        start_kafka()
        create_topic()

        # Start consuming messages
        kafka_consumer.consume_messages()

    except Exception as e:
        logging.error("Error adding feed: %s", e, exc_info=True)  # Log the error with traceback

if __name__ == "__main__":
    main()