# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Chat Message Request model.
"""

from dataclasses import dataclass
from typing import List

from .chat_history_message import ChatHistoryMessage


@dataclass
class ChatMessageRequest:
    """
    Represents the request payload for a real-time threat protection check on a chat message.

    This class encapsulates the information needed to send chat history to the MCP platform
    for threat analysis.
    """

    #: The unique identifier for the conversation.
    conversation_id: str

    #: The unique identifier for the message within the conversation.
    message_id: str

    #: The content of the user's message.
    user_message: str

    #: The chat history messages.
    chat_history: List[ChatHistoryMessage]

    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.conversation_id:
            raise ValueError("conversation_id cannot be empty")
        if not self.message_id:
            raise ValueError("message_id cannot be empty")
        if not self.user_message:
            raise ValueError("user_message cannot be empty")
        if not self.chat_history:
            raise ValueError("chat_history cannot be empty")

    def to_dict(self):
        """
        Convert the request to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the request.
        """
        return {
            "conversationId": self.conversation_id,
            "messageId": self.message_id,
            "userMessage": self.user_message,
            "chatHistory": [msg.to_dict() for msg in self.chat_history],
        }
