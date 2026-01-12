# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging
from collections.abc import Awaitable, Callable

from microsoft_agents.activity import Activity
from microsoft_agents.hosting.core.middleware_set import Middleware, TurnContext
from microsoft_agents_a365.observability.core.agent_details import AgentDetails
from microsoft_agents_a365.observability.core.execution_type import ExecutionType
from microsoft_agents_a365.observability.core.request import Request
from microsoft_agents_a365.observability.core.spans_scopes.input_scope import InputScope
from microsoft_agents_a365.observability.core.tenant_details import TenantDetails


class MessageLoggingMiddleware(Middleware):
    """
    Lightweight middleware for logging input and output messages.
    """

    def __init__(
        self,
        logger: logging.Logger | None = None,
        log_user_messages: bool = True,
        log_bot_messages: bool = True,
    ):
        """
        Initialize the message logger middleware.

        Args:
            logger: Custom logger instance (defaults to module logger)
            log_user_messages: Whether to log incoming user messages
            log_bot_messages: Whether to log outgoing bot messages
        """
        self.logger = logger or logging.getLogger("agents. observability")
        self.log_user_messages = log_user_messages
        self.log_bot_messages = log_bot_messages

    async def on_turn(self, turn_context: TurnContext, logic: Callable[[TurnContext], Awaitable]):
        input_scope = None

        # Start InputScope for the entire turn if we have user message
        if self.log_user_messages and turn_context.activity.text:
            input_scope = self._create_input_scope(turn_context.activity)
            input_scope.__enter__()
            self.logger.info(f"📥 User:  {turn_context.activity.text}")

        try:
            # Hook into outgoing messages
            if self.log_bot_messages:
                turn_context.on_send_activities(self._create_send_handler())

            # Execute bot logic
            await logic()
        except Exception as exc:
            # Clean up and propagate exception (let __exit__ handle error recording)
            if input_scope:
                input_scope.__exit__(type(exc), exc, exc.__traceback__)
                input_scope = None  # Prevent double cleanup
            raise
        finally:
            # Clean up the input scope if not already done
            if input_scope:
                input_scope.__exit__(None, None, None)

    def _create_input_scope(self, activity: Activity) -> InputScope:
        """Create InputScope for tracing the entire turn"""
        # Extract details from activity
        agent_details = AgentDetails(
            agent_id=activity.recipient.id if activity.recipient else "unknown",
            agent_name=activity.recipient.name if activity.recipient else None,
            conversation_id=activity.conversation.id if activity.conversation else None,
        )

        tenant_details = TenantDetails(
            tenant_id=activity.conversation.tenant_id
            if activity.conversation and hasattr(activity.conversation, "tenant_id")
            else "unknown"
        )

        request = Request(
            content=activity.text or "",
            execution_type=ExecutionType.HUMAN_TO_AGENT,
            session_id=activity.conversation.id if activity.conversation else None,
        )

        return InputScope.start(agent_details, tenant_details, request)

    def _create_send_handler(self):
        """Create handler for outgoing bot messages"""

        async def send_handler(ctx, activities, next_send):
            # Log each outgoing message
            for activity in activities:
                if activity.text:
                    self.logger.info(f"📤 Bot: {activity.text}")

            return await next_send()

        return send_handler
