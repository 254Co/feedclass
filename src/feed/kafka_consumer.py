import logging
from kafka import KafkaConsumer
import json
from .nlp_processor import NlpProcessor  # Import the NLP processor

class KafkaConsumerService:
    def __init__(self, topic: str, nlp_processor: NlpProcessor, bootstrap_servers='localhost:9092'):
        """
        Initializes the Kafka Consumer.
        :param topic: The Kafka topic to consume messages from.
        :param nlp_processor: The NLP processor to handle incoming feed entries.
        :param bootstrap_servers: The Kafka server address.
        """
        self.nlp_processor = nlp_processor  # Initialize NLP processor
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='rss-feed-consumer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Deserialize messages from JSON
        )
        logging.info(f"Kafka Consumer initialized for topic: {topic}")

    def consume_messages(self):
        """
        Consumes messages from the Kafka topic and processes them with the NLP processor.
        """
        logging.info("Starting to consume messages...")
        try:
            for message in self.consumer:
                logging.info(f"Consumed message: {message.value}")
                
                # Validate the structure of the message
                if isinstance(message.value, dict) and "feed_url" in message.value:
                    # Process the message with the NLP processor
                    self.nlp_processor.process_entry(message.value)
                    logging.info("Successfully processed the entry.")
                else:
                    logging.warning(f"Message format is invalid: {message.value}")
                    
        except Exception as e:
            logging.error(f"Error while consuming messages: {e}", exc_info=True)

    def close(self):
        """
        Closes the Kafka consumer connection.
        """
        self.consumer.close()
        logging.info("Kafka Consumer closed.")