"""
Base Agent Architecture & A2A Communication Engine.
Implements inter-agent messaging bus, structured logs, execution state, and agent handoffs.
"""

from abc import ABC, abstractmethod
import datetime
import uuid
from typing import List, Dict, Any, Optional
from models import AgentMessage, AgentMessageType


class A2AMessageBus:
    """Central Agent-to-Agent (A2A) Message Broker."""

    def __init__(self):
        self.messages: List[AgentMessage] = []

    def publish(
        self,
        sender: str,
        receiver: str,
        msg_type: AgentMessageType,
        content: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        msg = AgentMessage(
            message_id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
            sender_agent=sender,
            receiver_agent=receiver,
            message_type=msg_type,
            timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
            content=content,
            payload=payload or {}
        )
        self.messages.append(msg)
        return msg

    def get_history(self) -> List[AgentMessage]:
        return self.messages

    def clear(self):
        self.messages = []


class BaseAgent(ABC):
    """Abstract Base Agent for Specialist Compliance Agents."""

    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description

    @abstractmethod
    def process(self, context: Dict[str, Any], bus: A2AMessageBus) -> Dict[str, Any]:
        """
        Executes agent logic on current context, publishes A2A messages to bus,
        and returns updated context dictionary.
        """
        pass
