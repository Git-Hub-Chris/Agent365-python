# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


from microsoft_agents.hosting.aiohttp import CloudAdapter

from .message_logging_middleware import MessageLoggingMiddleware


class ObservabilityMiddlewareRegistrar:
    """
    Registrar for configuring and registering observability middleware.

    Usage:
        # Quick start with defaults
        ObservabilityMiddlewareRegistrar().with_message_logging().apply(adapter)

    """

    def __init__(self):
        """Initialize the registrar."""
        self._middleware_configs: list = []

    def with_message_logging(
        self,
        log_user_messages: bool = True,
        log_bot_messages: bool = True,
    ) -> "ObservabilityMiddlewareRegistrar":
        """Configure message logging middleware.

        Args:
            log_user_messages: Whether to log user messages (default: True)
            log_bot_messages: Whether to log bot messages (default: True)

        Returns:
            The registrar instance for chaining
        """
        self._middleware_configs.append(
            lambda: MessageLoggingMiddleware(
                log_user_messages=log_user_messages,
                log_bot_messages=log_bot_messages,
            )
        )
        return self

    def apply(self, adapter: CloudAdapter) -> None:
        """Apply all configured middleware to the adapter.

        Args:
            adapter: CloudAdapter to register middleware with
        """
        for create_middleware in self._middleware_configs:
            middleware = create_middleware()
            adapter.use(middleware)
