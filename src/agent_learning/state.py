from dataclasses import dataclass, field
from typing import Any, Dict, List

from .schemas import ToolExecutionRecord


@dataclass
class AgentState:
    user_input: str
    loop_count: int = 0
    steps: List[str] = field(default_factory=list)
    tool_history: List[ToolExecutionRecord] = field(default_factory=list)
    scratchpad: Dict[str, Any] = field(default_factory=dict)
    final_answer: str = ""
    tool_failures: int = 0

    def add_step(self, message: str) -> None:
        self.steps.append(message)
