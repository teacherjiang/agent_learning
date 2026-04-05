from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

ActionType = Literal["final_answer", "tool_call"]


@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]


@dataclass
class ModelOutput:
    action: ActionType
    final_answer: Optional[str] = None
    tool_call: Optional[ToolCall] = None


@dataclass
class ToolExecutionRecord:
    tool_name: str
    arguments: Dict[str, Any]
    success: bool
    result: str


@dataclass
class AgentResult:
    success: bool
    final_answer: str
    end_reason: str
    loops: int
    trace: Dict[str, Any] = field(default_factory=dict)
