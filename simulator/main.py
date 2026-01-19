import time
import random
import os
import sys
import logging
import dotenv
from core.producer import EcommerceEventSimulator

dotenv.load_dotenv()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting ecommerce event simulator...")

    simulator = EcommerceEventSimulator()
    logger.info("Simulator initialized")
    logger.info("Starting E-commerce event simulator...")
    logger.info(f"Kafka Topic: {os.getenv('KAFKA_TOPIC')}")

    try:
        event_count = 0
        while True:
            events = simulator.generate_events()

            if events:
                for event in events:
                    simulator.send_to_kafka(event)
                    event_count += 1

                    if event_count % 10 == 0:
                        logger.info(f"Sent {event_count} events to Kafka")

                time.sleep(random.uniform(1, 3))

    except KeyboardInterrupt:
        logger.info("Shutting down simulator...")
        simulator.shutdown()
        logger.info("Simulator shut down successfully")
        sys.exit(0)