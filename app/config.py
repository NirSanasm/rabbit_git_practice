from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbitmq_url: str = "amqp://admin:admin@localhost:5672/"
    class Config:
        env_file = ".env"


settings = Settings()