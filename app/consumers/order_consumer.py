# app/consumers/order_consumer.py
import asyncio
import json

from aio_pika import ExchangeType
from aio_pika.abc import AbstractIncomingMessage

from app.messaging.connection import RabbitMQ


async def process_payment(message: AbstractIncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body.decode())
        print(body)
        print(f'💰 Processing payment for order {body["order_id"]} for customer {body["customer_id"]}')
        await asyncio.sleep(7)
        print(f"✅ Payment for order {body['order_id']} processed")

async def process_order(message: AbstractIncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body.decode())
        print(body)
        print(f"📦 Processing order {body['order_id']} for customer {body['customer_id']}")
        print(f"   Product: {body['product_id']} x {body['quantity']} = ${body['total']}")

        await asyncio.sleep(7)

        print(f"✅ Order {body['order_id']} processed")


async def main() -> None:
    await RabbitMQ.connect()
    order_channel = await RabbitMQ.get_channel()
    payment_channel = await RabbitMQ.get_channel()

    exchange = await order_channel.declare_exchange(
        "orders", ExchangeType.DIRECT, durable=True
    )

    payment_exchange = await payment_channel.declare_exchange("payments", ExchangeType.DIRECT, durable = True)
    
    # 👇 RENAMED to order_queue to avoid clashing with Python's built-in 'queue' module
    order_queue = await order_channel.declare_queue("order_processing", durable=True)
    payment_queue = await payment_channel.declare_queue('payment_processing', durable=True)
    await payment_queue.bind(payment_exchange, routing_key="payment.created")
    await order_queue.bind(exchange, routing_key="order.created")

    await order_queue.consume(process_order)
    await payment_queue.consume(process_payment)
    print("🚀 Consumer waiting for orders on queue 'order_processing and payment on payment_processing'...")

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())