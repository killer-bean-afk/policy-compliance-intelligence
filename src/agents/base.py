import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.schemas import AgentMessage, AgentStepTrace

class AgentMessageBus:
    """Central Agent-to-Agent (A2A) communication bus and audit log."""

    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.traces: List[AgentStepTrace] = []

    def send_message(
        self,
        sender: str,
        receiver: str,
        stage: str,
        content: str,
        payload: Optional[Dict[str, Any]] = None,
        handoff_reason: Optional[str] = None
    ) -> AgentMessage:
        msg = AgentMessage(
            sender=sender,
            receiver=receiver,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            stage=stage,
            content=content,
            payload=payload or {},
            handoff_reason=handoff_reason
        )
        self.messages.append(msg)
        return msg

    def record_trace(
        self,
        agent_name: str,
        stage: str,
        action: str,
        thought: str,
        output_summary: str,
        execution_time_ms: float,
        confidence: float,
        data: Optional[Dict[str, Any]] = None
    ) -> AgentStepTrace:
        trace = AgentStepTrace(
            agent_name=agent_name,
            stage=stage,
            action=action,
            thought=thought,
            output_summary=output_summary,
            execution_time_ms=round(execution_time_ms, 2),
            confidence=round(confidence, 3),
            data=data
        )
        self.traces.append(trace)
        return trace

    def get_messages(self) -> List[AgentMessage]:
        return self.messages

    def get_traces(self) -> List[AgentStepTrace]:
        return self.traces

class BaseComplianceAgent(ABC):
    """Abstract base class for all specialist compliance agents."""

    def __init__(self, agent_id: str, name: str, role: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.description = description

    @abstractmethod
    def execute(self, state: Dict[str, Any], bus: AgentMessageBus) -> Dict[str, Any]:
        """Executes the agent's specialist task, logs A2A messages, and updates shared workflow state."""
        pass
