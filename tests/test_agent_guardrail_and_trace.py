from agent_learning.agent import MinimalAgent
from agent_learning.schemas import ModelOutput, ToolCall


def test_trace_is_present_in_result() -> None:
    agent = MinimalAgent()
    result = agent.run("Hello")
    assert isinstance(result.trace, dict)
    assert result.trace["user_input"] == "Hello"
    assert isinstance(result.trace["steps"], list)


def test_repeated_tool_call_guardrail(monkeypatch) -> None:
    calls = {"n": 0}

    def _always_same_tool_call(*args, **kwargs):
        calls["n"] += 1
        return ModelOutput(
            action="tool_call",
            tool_call=ToolCall(tool_name="get_weather", arguments={"city": "Tokyo"}),
        )

    monkeypatch.setattr("agent_learning.agent.get_llm_response", _always_same_tool_call)

    agent = MinimalAgent(max_loops=10, max_same_tool_call_repeats=2)
    result = agent.run("What's the weather in Tokyo?")

    assert result.success is False
    assert result.end_reason == "repeated_tool_call_guardrail"
    assert "repeated the same tool call" in result.final_answer
    assert any("guardrail=repeated_tool_call_guardrail" in s for s in result.trace["steps"])
