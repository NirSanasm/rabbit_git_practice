import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from app.config import settings


class RabbitMQ:
    
    connection: AbstractRobustConnection | None = None

    @classmethod
    async def connect(cls) -> AbstractRobustConnection:
        if cls.connection is None or cls.connection.is_closed:
            cls.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            print("RabbitMQ is connected")

        return cls.connection


    @classmethod
    async def get_channel(cls) -> AbstractChannel:
        connection = await cls.connect()
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        return channel

    @classmethod
    async def close_connection(cls) -> None:
        if cls.connection and not cls.connection.is_closed:
            await cls.connection.close()
            print("RabbitMQ connection is closed")

    
