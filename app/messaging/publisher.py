import json
import uuid
from typing import Any

from aio_pika import DeliveryMode, ExchangeType, Message

from app.messaging.connection import RabbitMQ


async def publish_message(exchange_name:str, routing_key:str, payload:dict[str, Any], exchange_type:ExchangeType = ExchangeType.DIRECT, message_id:str| None = None) -> None:
    channel = await RabbitMQ.get_channel()
    exchange = await channel.declare_exchange(exchange_name, exchange_type, durable=True)
    body = json.dumps(payload).encode('utf-8')

    message = Message(
        body = body,
        delivery_mode = DeliveryMode.PERSISTENT,
        message_id = message_id or str(uuid.uuid4()),
        content_type = 'application/json',
    )

    await exchange.publish(message, routing_key=routing_key)
    print(f"Pubished to exchange name: {exchange_name}, routing key: {routing_key}, message id: {message.message_id}")