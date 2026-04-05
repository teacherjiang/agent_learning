from typing import Any, Dict

from agent_learning.llm import get_llm_response
from agent_learning.schemas import ToolExecutionRecord
from agent_learning.state import AgentState
from agent_learning.tools import get_tools


class _FakeResponse:
    def __init__(self, payload: Dict[str, Any], status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self) -> Dict[str, Any]:
        return self._payload


def test_default_provider_uses_mock(monkeypatch) -> None:
    monkeypatch.delenv("AGENT_LLM_PROVIDER", raising=False)
    state = AgentState(user_input="What's the weather in Tokyo?")
    output = get_llm_response(state, get_tools())
    assert output.action == "tool_call"
    assert output.tool_call is not None
    assert output.tool_call.tool_name == "get_weather"


def test_siliconflow_missing_key_returns_final_answer(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_LLM_PROVIDER", "siliconflow")
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    state = AgentState(user_input="What's the weather in Tokyo?")
    output = get_llm_response(state, get_tools())
    assert output.action == "final_answer"
    assert output.final_answer is not None
    assert "SILICONFLOW_API_KEY" in output.final_answer


def test_siliconflow_tool_call_parsing(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_LLM_PROVIDER", "siliconflow")
    monkeypatch.setenv("SILICONFLOW_API_KEY", "dummy-key")

    def _fake_post(*args, **kwargs):
        return _FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": "get_weather",
                                        "arguments": '{"city": "Tokyo"}',
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr("agent_learning.llm.requests.post", _fake_post)

    state = AgentState(user_input="What's the weather in Tokyo?")
    output = get_llm_response(state, get_tools())
    assert output.action == "tool_call"
    assert output.tool_call is not None
    assert output.tool_call.tool_name == "get_weather"
    assert output.tool_call.arguments["city"] == "Tokyo"


def test_siliconflow_short_circuit_after_successful_tool(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_LLM_PROVIDER", "siliconflow")
    monkeypatch.setenv("SILICONFLOW_API_KEY", "dummy-key")

    state = AgentState(user_input="What's the weather in Tokyo?")
    state.tool_history.append(
        ToolExecutionRecord(
            tool_name="get_weather",
            arguments={"city": "Tokyo"},
            success=True,
            result="Sunny, 22C",
        )
    )

    output = get_llm_response(state, get_tools())
    assert output.action == "final_answer"
    assert output.final_answer is not None
    assert "Sunny" in output.final_answer
