from aio_pika import RobustConnection, connect_robust

from app.config import settings


class RabbitMQ:
    connection : RobustConnection | None = None

    @classmethod
    async def connect(cls) -> RobustConnection:
        if cls.connection is None or cls.connection.is_closed:
            cls.connection = await connect_robust(settings.rabbitmq_url)
            print("RabbitMQ is connected")

        return cls.connection


    @classmethod
    async def get_channel(cls):
        connection = await cls.connect()
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        return channel

    @classmethod
    async def close_connection(cls):
        if cls.connection and not cls.connection.is_closed:
            await cls.connection.close()
            print("RabbitMQ connection is closed")

    
