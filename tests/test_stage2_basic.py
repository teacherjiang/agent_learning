from agent_learning.agent import MinimalAgent


def test_weather_question_triggers_tool_and_returns_weather() -> None:
    agent = MinimalAgent()
    result = agent.run("What's the weather in Tokyo?")
    assert result.success is True
    assert "Tokyo" in result.final_answer
    assert "Sunny" in result.final_answer


def test_greeting_does_not_need_tool() -> None:
    agent = MinimalAgent()
    result = agent.run("Hello")
    assert result.success is True
    assert "Hello" in result.final_answer
    assert result.loops == 1


def test_unknown_city_has_fallback_weather() -> None:
    agent = MinimalAgent()
    result = agent.run("What's the weather in Mars?")
    assert result.success is True
    assert "Unknown weather" in result.final_answer


def test_max_loops_stop_condition_prevents_infinite_loop() -> None:
    agent = MinimalAgent(max_loops=0)
    result = agent.run("What's the weather in Tokyo?")
    assert result.success is False
    assert result.end_reason == "max_loops_reached"
