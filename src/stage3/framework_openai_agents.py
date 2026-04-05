import os
from typing import Any

from agent_learning.tools import get_weather

try:
    from agents import Agent, Runner, function_tool
except ImportError:
    Agent = None
    Runner = None
    function_tool = None


if function_tool is not None:
    @function_tool
    def get_weather_tool(city: str) -> str:
        """Get weather by city name."""
        return get_weather(city)
else:
    get_weather_tool = None


def run_openai_agents_variant(
    user_input: str,
    model: str = "gpt-4.1-mini",
    max_turns: int = 5,
) -> dict[str, Any]:
    if Agent is None or Runner is None or get_weather_tool is None:
        return {
            "variant": "openai_agents_sdk",
            "success": False,
            "message": (
                "OpenAI Agents SDK is not installed. "
                "Run `python3 -m pip install -r requirements.txt` first."
            ),
            "input": user_input,
        }

    if not os.getenv("OPENAI_API_KEY"):
        return {
            "variant": "openai_agents_sdk",
            "success": False,
            "message": (
                "OPENAI_API_KEY is missing. "
                "Set it before running the OpenAI Agents variant."
            ),
            "input": user_input,
        }

    agent = Agent(
        name="stage3_openai_agent",
        model=model,
        tools=[get_weather_tool],
        instructions=(
            "You are a compact weather helper.\n"
            "Rules:\n"
            "1) If user asks weather in a city, call get_weather once.\n"
            "2) If user sends greeting/chitchat, reply directly.\n"
            "3) After tool result, return one concise final sentence."
        ),
    )

    try:
        result = Runner.run_sync(
            starting_agent=agent,
            input=user_input,
            max_turns=max_turns,
        )
        final_answer = str(result.final_output)
        loops = len(result.raw_responses) if hasattr(result, "raw_responses") else None
        return {
            "variant": "openai_agents_sdk",
            "success": True,
            "final_answer": final_answer,
            "end_reason": "final_answer",
            "loops": loops,
        }
    except Exception as exc:
        return {
            "variant": "openai_agents_sdk",
            "success": False,
            "final_answer": (
                "OpenAI Agents SDK execution failed. "
                f"{type(exc).__name__}: {exc}"
            ),
            "end_reason": "execution_error",
            "input": user_input,
        }
