import logging
from src.kafka_consumer import KafkaConsumerService

def main():
    logging.basicConfig(level=logging.INFO)

    # Initialize the Kafka consumer
    consumer_service = KafkaConsumerService(topic='test_topic')

    # Start consuming messages
    consumer_service.consume_messages()

if __name__ == "__main__":
    main()