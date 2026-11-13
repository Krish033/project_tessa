"""RabbitMQ connection manager and event bus for inter-service communication."""

import asyncio
from contextlib import suppress
import json
import uuid
from collections.abc import Callable, Coroutine
from typing import Any, Optional

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractExchange

from shared.config.config import settings
from shared.config.logging import get_logger

logger = get_logger(__name__)


class RabbitMQConnection:
    """Singleton RabbitMQ connection manager."""

    _instance: Optional["RabbitMQConnection"] = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "RabbitMQConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._exchange: AbstractExchange | None = None
        self._rpc_exchange: AbstractExchange | None = None
        self._event_handlers: dict[str, list[Callable]] = {}
        self._rpc_handlers: dict[str, Callable] = {}
        self._service_name: str = "unknown"
        self._initialized = True

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and not self._connection.is_closed

    async def connect(self, service_name: str = "unknown") -> None:
        """Connect to RabbitMQ."""
        self._service_name = service_name
        rabbitmq_url = getattr(settings, "rabbitmq_url", "amqp://krishna:krishna@localhost:5672/")

        try:
            self._connection = await aio_pika.connect_robust(rabbitmq_url)
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=10)

            # Main event exchange (topic-based routing)
            self._exchange = await self._channel.declare_exchange(
                "signal.events",
                ExchangeType.TOPIC,
                durable=True,
            )

            # RPC exchange (direct routing for request-reply)
            self._rpc_exchange = await self._channel.declare_exchange(
                "signal.rpc",
                ExchangeType.DIRECT,
                durable=True,
            )

            logger.info("rabbitmq_connected", service=service_name)
        except Exception as e:
            logger.warning("rabbitmq_connection_failed_continuing", error=str(e), service=service_name)

    async def disconnect(self) -> None:
        """Disconnect cleanly from RabbitMQ, closing channels, cancelling consumers, and draining callbacks."""
        if self._channel and not self._channel.is_closed:
            try:
                await self._channel.close()
            except Exception as e:
                logger.debug("rabbitmq_channel_close_error", error=str(e))
            self._channel = None

        if self._connection and not self._connection.is_closed:
            try:
                await self._connection.close()
            except Exception as e:
                logger.debug("rabbitmq_connection_close_error", error=str(e))
            self._connection = None
            logger.info("rabbitmq_disconnected", service=self._service_name)

        self._exchange = None
        self._rpc_exchange = None
        self._event_handlers.clear()
        self._rpc_handlers.clear()

        # Allow any pending aio_pika background callback tasks (e.g. OneShotCallback)
        # to complete cleanly before event loop teardown.
        await asyncio.sleep(0.05)

    # ── Event Publishing ─────────────────────────────────────────────

    async def publish_event(self, routing_key: str, data: dict[str, Any]) -> None:
        """Publish an event to the event exchange.

        routing_key format: <service>.<entity>.<action>
        e.g. "discoveries.job.completed", "campaigns.email.sent"
        """
        if not self._exchange:
            logger.warning("rabbitmq_publish_skipped_not_connected", routing_key=routing_key)
            return

        body = json.dumps(data, default=str).encode()
        message = Message(
            body=body,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            message_id=str(uuid.uuid4()),
            headers={"source": self._service_name},
        )

        await self._exchange.publish(message, routing_key=routing_key)
        logger.debug("rabbitmq_event_published", routing_key=routing_key)

    # ── Event Subscribing ────────────────────────────────────────────

    async def subscribe(
        self,
        routing_key: str,
        handler: Callable[[dict[str, Any]], Coroutine],
        queue_name: str | None = None,
    ) -> None:
        """Subscribe to events matching a routing key pattern.

        routing_key can use wildcards: "discoveries.*.*", "campaigns.email.#"
        """
        if not self._channel or not self._exchange:
            logger.warning("rabbitmq_subscribe_skipped_not_connected", routing_key=routing_key)
            return

        q_name = queue_name or f"{self._service_name}.{routing_key}"
        queue = await self._channel.declare_queue(q_name, durable=True)
        await queue.bind(self._exchange, routing_key=routing_key)

        async def _process_message(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await handler(data)
                except Exception as e:
                    logger.error(
                        "rabbitmq_event_handler_error",
                        routing_key=routing_key,
                        error=str(e),
                    )

        await queue.consume(_process_message)
        logger.info("rabbitmq_subscribed", routing_key=routing_key, queue=q_name)

    # ── RPC (Request-Reply) ──────────────────────────────────────────

    async def register_rpc(
        self,
        method: str,
        handler: Callable[[dict[str, Any]], Coroutine],
    ) -> None:
        """Register an RPC handler for a method name.

        method format: <service>.<action>
        e.g. "warehouse.get_leads", "campaigns.get_status"
        """
        if not self._channel or not self._rpc_exchange:
            logger.warning("rabbitmq_rpc_register_skipped", method=method)
            return

        queue = await self._channel.declare_queue(f"rpc.{method}", durable=True)
        await queue.bind(self._rpc_exchange, routing_key=method)

        async def _process_rpc(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    result = await handler(data)
                    response_body = json.dumps(result, default=str).encode()
                except Exception as e:
                    logger.error("rabbitmq_rpc_handler_error", method=method, error=str(e))
                    response_body = json.dumps({"error": str(e)}).encode()

                # Send reply
                if message.reply_to:
                    await self._channel.default_exchange.publish(
                        Message(
                            body=response_body,
                            correlation_id=message.correlation_id,
                            content_type="application/json",
                        ),
                        routing_key=message.reply_to,
                    )

        await queue.consume(_process_rpc)
        self._rpc_handlers[method] = handler
        logger.info("rabbitmq_rpc_registered", method=method)

    async def rpc_call(
        self,
        method: str,
        data: dict[str, Any],
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Make an RPC call to another service and wait for the response."""
        if not self._channel or not self._rpc_exchange:
            raise RuntimeError("RabbitMQ not connected")

        # Create exclusive callback queue
        callback_queue = await self._channel.declare_queue(exclusive=True)
        correlation_id = str(uuid.uuid4())
        future: asyncio.Future[dict[str, Any]] = asyncio.get_event_loop().create_future()

        async def _on_response(message: aio_pika.IncomingMessage) -> None:
            if message.correlation_id == correlation_id:
                result = json.loads(message.body.decode())
                if not future.done():
                    future.set_result(result)

        consumer_tag = await callback_queue.consume(_on_response)

        # Publish the RPC request
        await self._rpc_exchange.publish(
            Message(
                body=json.dumps(data, default=str).encode(),
                correlation_id=correlation_id,
                reply_to=callback_queue.name,
                content_type="application/json",
                message_id=str(uuid.uuid4()),
            ),
            routing_key=method,
        )

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except TimeoutError:
            logger.error("rabbitmq_rpc_timeout", method=method, timeout=timeout)
            raise TimeoutError(f"RPC call to {method} timed out after {timeout}s")
        finally:
            with suppress(Exception):
                await callback_queue.cancel(consumer_tag)
            with suppress(Exception):
                await callback_queue.delete(if_unused=False, if_empty=False)


# Global singleton
_rabbit: RabbitMQConnection | None = None


def get_rabbitmq() -> RabbitMQConnection:
    """Get the RabbitMQ connection singleton."""
    global _rabbit
    if _rabbit is None:
        _rabbit = RabbitMQConnection()
    return _rabbit
