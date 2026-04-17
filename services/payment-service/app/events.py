import json
import logging
import pika
from app.config import settings

logger = logging.getLogger(__name__)


def publish_payment_event(event_type: str, data: dict):
    """Publish a payment event to RabbitMQ."""
    try:
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.RABBITMQ_URL)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange="payment_events", exchange_type="topic", durable=True)

        message = json.dumps({"event_type": event_type, "data": data})
        channel.basic_publish(
            exchange="payment_events",
            routing_key=f"payment.{event_type}",
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),  # persistent
        )
        connection.close()
        logger.info(f"Published payment event: {event_type}")
    except Exception as e:
        logger.warning(f"Failed to publish payment event: {e}")
