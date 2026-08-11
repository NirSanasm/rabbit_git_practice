# app/main.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.orders import router as orders_router
from app.messaging.connection import RabbitMQ


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Warm up the connection on startup
    await RabbitMQ.connect()
    yield
    # Close cleanly on shutdown
    await RabbitMQ.close_connection()


app = FastAPI(title="Ecom API", lifespan=lifespan)
app.include_router(orders_router)