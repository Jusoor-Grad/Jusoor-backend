from enum import Enum
from pydantic import BaseModel


class ChatWebSocketEvent(str, Enum):
    """
        Types of messages that will be sent by the streaming chat repsone
        form the chatbot agent
    """
    START = "chat.message_start"
    CONTENT = "chat.message_content"
    END = "chat.message_end"

class ChatWebSocketResponse(BaseModel):
    event: ChatWebSocketEvent = ChatWebSocketEvent.CONTENT
    data: str