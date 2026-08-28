import asyncio
import json
from aio_pika import ExchangeType, IncomingMessage
from app.messaging.connection import RabbitMQ

processed_message_ids = set()

async def send_email(message: IncomingMessage) -> None:

    if message.message_id in processed_message_ids:
        print(f"Duplicate message detected: {message.message_id}. Skipping processing.")
        await message.ack()
        return
    
    try:
        body = json.loads(message.body.decode())
        if body.get("customer_id") == "cus_fail_me":
            raise ConnectionError("Simulated email sending failure for testing purposes.")
        print(f"Sending email to {body['customer_id']} for order {body['order_id']}")
        print(f"   Subject: Order Confirmation - Order ID: {body['order_id']})")
        print(f"   Body: Your order with ID {body['order_id']} has been successfully created. Thank you for your purchase!")
        await asyncio.sleep(1)
        print(f"Email sent to {body['customer_id']} for order {body['order_id']}")
        processed_message_ids.add(message.message_id)
        await message.ack()

    except Exception as e:
        print(f"Failed to send email: {e}")
        
        # RabbitMQ automatically tracks deaths in the 'x-death' header
        deaths = message.headers.get('x-death', [])
        retry_count = 0
        
        # Find the death record specifically for our main queue
        for death in deaths:
            if death.get('queue') == 'email_queue':
                retry_count = death.get('count', 0)
                break
        if retry_count >= 4:
            print(f"Max retries reached for {message.message_id}. Burying message.")
            await message.ack() 
        else: 
            print(f"Retry {retry_count + 1}/4. Sending to retry queue via DLX...")
            await message.nack(requeue=False)

            
async def main() -> None:
    await RabbitMQ.connect()
    channel = await RabbitMQ.get_channel()
    exchange = await channel.declare_exchange("ecom_events", ExchangeType.TOPIC, durable=True)
    retry_exchange = await channel.declare_exchange("ecom_events_retry", ExchangeType.TOPIC, durable=True)
    email_queue = await channel.declare_queue("email_queue", durable=True, arguments={
        "x-dead-letter-exchange": "ecom_events_retry",
        "x-dead-letter-routing-key": "email_retry_route"

    })
    await email_queue.bind(exchange, routing_key="order.created")

    email_retry_queue = await channel.declare_queue("email_retry_queue", durable=True, arguments={
        "x-message-ttl": 15000,
        "x-dead-letter-exchange": "ecom_events",
        "x-dead-letter-routing-key": "order.created"
    })
    await email_retry_queue.bind(retry_exchange, routing_key="email_retry_route")

    await email_queue.consume(send_email, no_ack=False)
    print("Email worker is running. Waiting for messages...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

    

