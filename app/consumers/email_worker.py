import asyncio
import json
from aio_pika import ExchangeType, IncomingMessage
from app.messaging.connection import RabbitMQ

async def send_email(message: IncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body.decode())

        print(f"Sending email to {body['customer_id']} for order {body['order_id']}")
        print(f"   Subject: Order Confirmation - Order ID: {body['order_id']})")
        print(f"   Body: Your order with ID {body['order_id']} has been successfully created. Thank you for your purchase!")
        await asyncio.sleep(1)
        print(f"Email sent to {body['customer_id']} for order {body['order_id']}")

async def main() -> None:
    await RabbitMQ.connect()
    channel = await RabbitMQ.get_channel()
    exchange = await channel.declare_exchange("ecom_events", ExchangeType.TOPIC, durable=True)
    email_queue = await channel.declare_queue("email_queue", durable=True)
    await email_queue.bind(exchange, routing_key="order.created")
    await email_queue.consume(send_email)
    print("Email worker is running. Waiting for messages...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

    

