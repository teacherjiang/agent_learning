from stage3.framework_langchain import run_langchain_variant


def test_langchain_weather_question_works() -> None:
    result = run_langchain_variant("What's the weather in Tokyo?")
    assert result["success"] is True
    assert "Tokyo" in result["final_answer"]
    assert "Sunny" in result["final_answer"]


def test_langchain_greeting_direct_answer() -> None:
    result = run_langchain_variant("Hello")
    assert result["success"] is True
    assert "Hello" in result["final_answer"]
    assert result["loops"] == 1


def test_langchain_unknown_city_has_fallback() -> None:
    result = run_langchain_variant("What's the weather in Mars?")
    assert result["success"] is True
    assert "Unknown weather" in result["final_answer"]
