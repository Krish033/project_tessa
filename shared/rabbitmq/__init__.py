"""RabbitMQ shared messaging infrastructure."""

from shared.rabbitmq.connection import RabbitMQConnection, get_rabbitmq

__all__ = ["RabbitMQConnection", "get_rabbitmq"]
