# Copyright (c) Microsoft. All rights reserved.

"""
Example usage of the chat history API to send chat history to the MCP platform.

This example demonstrates how to use the send_chat_history method to send
chat conversation history to the MCP platform for real-time threat protection analysis.
"""

import asyncio
from datetime import datetime, timezone

from microsoft_agents_a365.tooling.models import ChatHistoryMessage
from microsoft_agents_a365.tooling.services import McpToolServerConfigurationService


async def main():
    """Example of sending chat history to MCP platform."""

    # Create the service
    service = McpToolServerConfigurationService()

    # Create chat history messages
    messages = [
        ChatHistoryMessage(
            id="msg-1",
            role="user",
            content="Hello, I need help with my account",
            timestamp=datetime.now(timezone.utc),
        ),
        ChatHistoryMessage(
            id="msg-2",
            role="assistant",
            content="I'd be happy to help you with your account. What do you need assistance with?",
            timestamp=datetime.now(timezone.utc),
        ),
        ChatHistoryMessage(
            id="msg-3",
            role="user",
            content="I forgot my password",
            timestamp=datetime.now(timezone.utc),
        ),
    ]

    # Send chat history to MCP platform
    result = await service.send_chat_history(
        conversation_id="conv-123456",
        message_id="msg-4",
        user_message="Can you help me reset it?",
        chat_history_messages=messages,
        auth_token="your-auth-token-here",
    )

    # Check the result
    if result.succeeded:
        print("✅ Chat history sent successfully!")
    else:
        print(f"❌ Failed to send chat history: {result}")
        for error in result.errors:
            print(f"   - {error.message}")


if __name__ == "__main__":
    asyncio.run(main())
