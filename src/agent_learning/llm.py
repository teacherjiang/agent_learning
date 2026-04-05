from .schemas import ModelOutput, ToolCall
from .state import AgentState
from .utils import extract_city_for_weather


def mock_llm(state: AgentState) -> ModelOutput:
    """A replaceable mock model that emits structured actions."""
    if state.tool_history:
        last_tool = state.tool_history[-1]
        if last_tool.success:
            city = str(last_tool.arguments.get("city", "Unknown"))
            return ModelOutput(
                action="final_answer",
                final_answer=f"The weather in {city} is {last_tool.result}.",
            )
        return ModelOutput(
            action="final_answer",
            final_answer="I could not finish the task because tool execution failed.",
        )

    user_text = state.user_input.lower()
    if "weather" in user_text:
        city = extract_city_for_weather(state.user_input)
        return ModelOutput(
            action="tool_call",
            tool_call=ToolCall(tool_name="get_weather", arguments={"city": city}),
        )

    return ModelOutput(
        action="final_answer",
        final_answer="Hello! I am your minimal learning agent.",
    )
