import json
import pika
from pydantic import ValidationError
from app.config.settings import settings
from app.models.message import ResetPasswordMessage
from app.services.db_service import client as mongo_client, save_message, mark_as_sent
from app.services.email_service import send_email
import logging

logger = logging.getLogger(__name__)

def process_message(ch, method, properties, body):
    logger.info(f"Message received: {body}")  
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON received, discarding message")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    #validates the data
    try:
        message = ResetPasswordMessage(**data)
    except ValidationError as e:
        logger.warning(f"Message validation failed: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    #process the message inside a MongoDB transaction
    with mongo_client.start_session() as session:
        try:
            with session.start_transaction():
                save_message(session, message)
                send_email(
                    to=message.email_address,
                    subject=message.subject,
                    body=message.body,
                )
                mark_as_sent(session, str(message.id))

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Successfully processed message {message.id}")

        except Exception as e:
            logger.error(f"Failed to process message {message.id}: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consuming():
    connection = pika.BlockingConnection(
        pika.URLParameters(settings.RABBITMQ_URL)
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange="dead-letter-exchange",
        exchange_type="direct",
        durable=True,
    )
    channel.queue_declare(
        queue="reset-password-dead-letter",
        durable=True,
        arguments={
            "x-queue-type": "quorum",
        },
    )
    channel.queue_bind(
        queue="reset-password-dead-letter",
        exchange="dead-letter-exchange",
        routing_key="reset-password-stream",
    )
    channel.queue_declare(
        queue="reset-password-stream",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "dead-letter-exchange",
            "x-dead-letter-routing-key": "reset-password-stream",
            "x-max-delivery-count": 5,
            "x-queue-type": "quorum",
        },
    )
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="reset-password-stream",
        on_message_callback=process_message,
    )
    print("Waiting for messages...")
    channel.start_consuming()