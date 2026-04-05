from stage3.framework_openai_agents import run_openai_agents_variant


def test_openai_agents_variant_requires_api_key() -> None:
    result = run_openai_agents_variant("What's the weather in Tokyo?")
    if result["success"] is False:
        # In local learning environments without key, this is expected.
        assert "OPENAI_API_KEY" in result["message"]
    else:
        # If a key exists in env, ensure result structure is still correct.
        assert "final_answer" in result
        assert result["end_reason"] == "final_answer"
