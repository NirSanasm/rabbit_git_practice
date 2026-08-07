# app/api/orders.py
import uuid
from fastapi import APIRouter, status
from pydantic import BaseModel
from aio_pika import ExchangeType
from app.messaging.publisher import publish_message

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderIn(BaseModel):
    customer_id: str
    product_id: str
    quantity: int
    total: float


class OrderOut(BaseModel):
    order_id: str
    status: str

class PaymentOut(BaseModel):
    order_id: str
    status: str
    payment_status: str

@router.post('/', response_model=OrderOut, status_code=status.HTTP_202_ACCEPTED)
async def create_order(order: OrderIn):
    order_id = str(uuid.uuid4())
    order_out = OrderOut(order_id=order_id, status="created")
    payload = order.dict()
    payload["order_id"] = order_id
    await publish_message(
        exchange_name="orders",
        routing_key="order.created",
        payload=payload
    )
    return order_out


@router.post('/payment', response_model= PaymentOut, status_code=status.HTTP_202_ACCEPTED)
async def process_payment(order: OrderIn):
    order_id = str(uuid.uuid4())
    payment = PaymentOut(order_id=order_id, status="processed", payment_status='success')
    payload = order.dict()
    payload['order_id'] = order_id
    await publish_message(
        exchange_name="payments",
        routing_key="payment.created",
        payload =payload
    )

    return payment