from typing import Any, Dict, List

from agent_learning.tools import get_weather
from agent_learning.utils import extract_city_for_weather

try:
    from langchain_core.runnables import RunnableLambda
    from langchain_core.tools import tool
except ImportError:
    RunnableLambda = None
    tool = None


if tool is not None:
    @tool
    def get_weather_tool(city: str) -> str:
        """Get weather by city name."""
        return get_weather(city)
else:
    get_weather_tool = None


def _planner(state: Dict[str, Any]) -> Dict[str, Any]:
    tool_history: List[Dict[str, Any]] = state["tool_history"]
    if tool_history:
        last_tool = tool_history[-1]
        if last_tool["success"]:
            city = str(last_tool["arguments"].get("city", "Unknown"))
            return {
                "action": "final_answer",
                "final_answer": f"The weather in {city} is {last_tool['result']}.",
            }
        return {
            "action": "final_answer",
            "final_answer": "I could not finish the task because tool execution failed.",
        }

    user_text = state["user_input"].lower()
    if "weather" in user_text:
        city = extract_city_for_weather(state["user_input"])
        return {
            "action": "tool_call",
            "tool_name": "get_weather",
            "arguments": {"city": city},
        }

    return {
        "action": "final_answer",
        "final_answer": "Hello! I am your minimal learning agent.",
    }


def run_langchain_variant(user_input: str, max_loops: int = 5) -> dict:
    if RunnableLambda is None or get_weather_tool is None:
        return {
            "variant": "langchain",
            "success": False,
            "message": (
                "LangChain is not installed. Run "
                "`python3 -m pip install -r requirements.txt` first."
            ),
            "input": user_input,
        }

    planner = RunnableLambda(_planner)
    tools = {"get_weather": get_weather_tool}
    state: Dict[str, Any] = {
        "user_input": user_input,
        "loop_count": 0,
        "steps": [],
        "tool_history": [],
    }

    while state["loop_count"] < max_loops:
        state["loop_count"] += 1
        decision = planner.invoke(state)
        state["steps"].append(
            f"loop_{state['loop_count']}_action={decision['action']}"
        )

        if decision["action"] == "final_answer":
            return {
                "variant": "langchain",
                "success": True,
                "final_answer": decision["final_answer"],
                "end_reason": "final_answer",
                "loops": state["loop_count"],
                "steps": state["steps"],
            }

        if decision["action"] != "tool_call":
            return {
                "variant": "langchain",
                "success": False,
                "final_answer": "Stopped because planner returned invalid action.",
                "end_reason": "invalid_action",
                "loops": state["loop_count"],
                "steps": state["steps"],
            }

        tool_name = decision["tool_name"]
        arguments = decision["arguments"]
        if tool_name not in tools:
            state["tool_history"].append(
                {
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "success": False,
                    "result": "Unknown tool",
                }
            )
            continue

        try:
            result = tools[tool_name].invoke(arguments)
            state["tool_history"].append(
                {
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "success": True,
                    "result": result,
                }
            )
        except Exception as exc:
            state["tool_history"].append(
                {
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "success": False,
                    "result": f"{type(exc).__name__}: {exc}",
                }
            )

    return {
        "variant": "langchain",
        "success": False,
        "final_answer": "Stopped because max loop count was reached.",
        "end_reason": "max_loops_reached",
        "loops": state["loop_count"],
        "steps": state["steps"],
    }
