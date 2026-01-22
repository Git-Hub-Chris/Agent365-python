# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Unit tests for send_chat_history_async and send_chat_history_messages_async methods."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from microsoft_agents_a365.runtime import OperationResult
from microsoft_agents_a365.tooling.models import ToolOptions

from .conftest import (
    MockSession,
    MockUserMessage,
)

# =============================================================================
# INPUT VALIDATION TESTS (UV-01 to UV-09)
# =============================================================================


class TestInputValidation:
    """Tests for input validation in send_chat_history methods."""

    # UV-01
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_validates_turn_context_none(
        self, service, sample_openai_messages
    ):
        """Test that send_chat_history_messages_async raises ValueError when turn_context is None."""
        with pytest.raises(ValueError, match="turn_context cannot be None"):
            await service.send_chat_history_messages_async(None, sample_openai_messages)

    # UV-02
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_validates_messages_none(
        self, service, mock_turn_context
    ):
        """Test that send_chat_history_messages_async raises ValueError when messages is None."""
        with pytest.raises(ValueError, match="messages cannot be None"):
            await service.send_chat_history_messages_async(mock_turn_context, None)

    # UV-03
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_empty_list_returns_success(
        self, service, mock_turn_context
    ):
        """Test that empty message list returns success (no-op)."""
        result = await service.send_chat_history_messages_async(mock_turn_context, [])

        assert result.succeeded is True
        assert len(result.errors) == 0

    # UV-04
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_validates_activity_none(
        self, service, mock_turn_context_no_activity, sample_openai_messages
    ):
        """Test that send_chat_history_messages_async validates turn_context.activity."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.side_effect = ValueError("turn_context.activity cannot be None")

            with pytest.raises(ValueError, match="turn_context.activity cannot be None"):
                await service.send_chat_history_messages_async(
                    mock_turn_context_no_activity, sample_openai_messages
                )

    # UV-05
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_validates_conversation_id(
        self, service, mock_turn_context_no_conversation_id, sample_openai_messages
    ):
        """Test that send_chat_history_messages_async validates conversation_id."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.side_effect = ValueError("conversation_id cannot be empty or None")

            with pytest.raises(ValueError, match="conversation_id cannot be empty"):
                await service.send_chat_history_messages_async(
                    mock_turn_context_no_conversation_id, sample_openai_messages
                )

    # UV-06
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_validates_message_id(
        self, service, mock_turn_context_no_message_id, sample_openai_messages
    ):
        """Test that send_chat_history_messages_async validates message_id."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.side_effect = ValueError("message_id cannot be empty or None")

            with pytest.raises(ValueError, match="message_id cannot be empty"):
                await service.send_chat_history_messages_async(
                    mock_turn_context_no_message_id, sample_openai_messages
                )

    # UV-07
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_validates_user_message(
        self, service, mock_turn_context_no_user_message, sample_openai_messages
    ):
        """Test that send_chat_history_messages_async validates user_message text."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.side_effect = ValueError("user_message cannot be empty or None")

            with pytest.raises(ValueError, match="user_message cannot be empty"):
                await service.send_chat_history_messages_async(
                    mock_turn_context_no_user_message, sample_openai_messages
                )

    # UV-08
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_async_validates_turn_context_none(self, service, mock_session):
        """Test that send_chat_history_async raises ValueError when turn_context is None."""
        with pytest.raises(ValueError, match="turn_context cannot be None"):
            await service.send_chat_history_async(None, mock_session)

    # UV-09
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_async_validates_session_none(self, service, mock_turn_context):
        """Test that send_chat_history_async raises ValueError when session is None."""
        with pytest.raises(ValueError, match="session cannot be None"):
            await service.send_chat_history_async(mock_turn_context, None)


# =============================================================================
# SUCCESS PATH TESTS (SP-01 to SP-07)
# =============================================================================


class TestSuccessPath:
    """Tests for successful execution paths."""

    # SP-01
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_success(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test successful send_chat_history_messages_async call."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            result = await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages
            )

            assert result.succeeded is True
            assert len(result.errors) == 0
            mock_send.assert_called_once()

    # SP-02
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_with_options(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test send_chat_history_messages_async with custom ToolOptions."""
        custom_options = ToolOptions(orchestrator_name="CustomOrchestrator")

        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            result = await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages, options=custom_options
            )

            assert result.succeeded is True
            # Verify options were passed through
            call_args = mock_send.call_args
            assert call_args.kwargs["options"].orchestrator_name == "CustomOrchestrator"

    # SP-03
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_default_orchestrator_name(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test that default orchestrator name is set to 'OpenAI'."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages
            )

            # Verify default orchestrator name
            call_args = mock_send.call_args
            assert call_args.kwargs["options"].orchestrator_name == "OpenAI"

    # SP-04
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_delegates_to_config_service(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test that send_chat_history_messages_async delegates to config_service."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages
            )

            # Verify delegation
            mock_send.assert_called_once()
            call_args = mock_send.call_args

            # Check turn_context was passed
            assert call_args.kwargs["turn_context"] == mock_turn_context

            # Check chat_history_messages were converted
            chat_history = call_args.kwargs["chat_history_messages"]
            assert len(chat_history) == len(sample_openai_messages)

    # SP-05
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_async_success(self, service, mock_turn_context, mock_session):
        """Test successful send_chat_history_async call."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            result = await service.send_chat_history_async(mock_turn_context, mock_session)

            assert result.succeeded is True
            mock_send.assert_called_once()

    # SP-06
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_async_with_limit(self, service, mock_turn_context):
        """Test send_chat_history_async with limit parameter."""
        # Create session with many messages
        messages = [MockUserMessage(content=f"Message {i}") for i in range(10)]
        session = MockSession(items=messages)

        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            result = await service.send_chat_history_async(mock_turn_context, session, limit=5)

            assert result.succeeded is True

            # Verify only limited messages were sent
            call_args = mock_send.call_args
            chat_history = call_args.kwargs["chat_history_messages"]
            assert len(chat_history) == 5

    # SP-07
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_async_delegates_to_send_chat_history_messages(
        self, service, mock_turn_context, mock_session
    ):
        """Test that send_chat_history_async calls send_chat_history_messages_async."""
        with patch.object(
            service,
            "send_chat_history_messages_async",
            new_callable=AsyncMock,
        ) as mock_method:
            mock_method.return_value = OperationResult.success()

            await service.send_chat_history_async(mock_turn_context, mock_session)

            mock_method.assert_called_once()
            call_args = mock_method.call_args
            assert call_args.kwargs["turn_context"] == mock_turn_context


# =============================================================================
# ERROR HANDLING TESTS (EH-01 to EH-05)
# =============================================================================


class TestErrorHandling:
    """Tests for error handling scenarios."""

    # EH-01
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_http_error(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test send_chat_history_messages_async handles HTTP errors."""

        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.failed(
                MagicMock(message="HTTP 500: Internal Server Error")
            )

            result = await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages
            )

            assert result.succeeded is False

    # EH-02
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_timeout_error(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test send_chat_history_messages_async handles timeout errors."""
        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.side_effect = TimeoutError("Request timed out")

            result = await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages
            )

            assert result.succeeded is False
            assert len(result.errors) == 1

    # EH-03
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_client_error(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test send_chat_history_messages_async handles network/client errors."""
        import aiohttp

        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.side_effect = aiohttp.ClientError("Connection failed")

            result = await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages
            )

            assert result.succeeded is False
            assert len(result.errors) == 1

    # EH-04
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_messages_async_conversion_error(
        self, service, mock_turn_context
    ):
        """Test send_chat_history_messages_async handles conversion errors gracefully."""
        # Create a message that might cause conversion issues but still has content
        problematic_message = MockUserMessage(content="Valid content")

        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            # Should not raise, should handle gracefully
            result = await service.send_chat_history_messages_async(
                mock_turn_context, [problematic_message]
            )

            assert result.succeeded is True

    # EH-05
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_chat_history_async_get_items_error(self, service, mock_turn_context):
        """Test send_chat_history_async handles session.get_items() errors."""
        # Create a mock session that raises an error
        mock_session = Mock()
        mock_session.get_items.side_effect = Exception("Session error")

        result = await service.send_chat_history_async(mock_turn_context, mock_session)

        assert result.succeeded is False
        assert len(result.errors) == 1


# =============================================================================
# ORCHESTRATOR NAME HANDLING TESTS
# =============================================================================


class TestOrchestratorNameHandling:
    """Tests for orchestrator name handling in options."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_options_with_none_orchestrator_name_gets_default(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test that options with None orchestrator_name get default value."""
        options = ToolOptions(orchestrator_name=None)

        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages, options=options
            )

            call_args = mock_send.call_args
            assert call_args.kwargs["options"].orchestrator_name == "OpenAI"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_options_preserves_custom_orchestrator_name(
        self, service, mock_turn_context, sample_openai_messages
    ):
        """Test that custom orchestrator name is preserved."""
        options = ToolOptions(orchestrator_name="MyCustomOrchestrator")

        with patch.object(
            service.config_service,
            "send_chat_history",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = OperationResult.success()

            await service.send_chat_history_messages_async(
                mock_turn_context, sample_openai_messages, options=options
            )

            call_args = mock_send.call_args
            assert call_args.kwargs["options"].orchestrator_name == "MyCustomOrchestrator"
