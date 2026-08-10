# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.messaging.connection import RabbitMQ
from app.api.orders import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the connection on startup
    await RabbitMQ.connect()
    yield
    # Close cleanly on shutdown
    await RabbitMQ.close_connection()


app = FastAPI(title="Ecom API", lifespan=lifespan)
app.include_router(orders_router)