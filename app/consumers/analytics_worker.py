import asyncio
import json
from aio_pika import ExchangeType, IncomingMessage
from app.messaging.connection import RabbitMQ

async def track_event(message: IncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body.decode())
        routing_key = message.routing_key
        print(f"Analytics: Received event with routing key: {routing_key} and payload: {body}")
        await asyncio.sleep(1)
        print(f"pushed to data warehouse")

async def main() -> None:
    await RabbitMQ.connect()
    channel = await RabbitMQ.get_channel()
    exchange = await channel.declare_exchange("ecom_events", ExchangeType.TOPIC, durable=True)

    analytics_queue = await channel.declare_queue("analytics_queue", durable=True)
    await analytics_queue.bind(exchange, routing_key="order.*")
    await analytics_queue.consume(track_event)
    print("Analytics worker is running. Waiting for messages...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())