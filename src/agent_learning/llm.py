import json
import os
from typing import Any, Dict, List

import requests

from .schemas import ModelOutput, ToolCall
from .state import AgentState
from .tools import ToolDefinition
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


def get_llm_response(state: AgentState, tools: List[ToolDefinition]) -> ModelOutput:
    provider = os.getenv("AGENT_LLM_PROVIDER", "mock").strip().lower()
    if provider == "siliconflow":
        return siliconflow_llm(state, tools)
    return mock_llm(state)


def siliconflow_llm(state: AgentState, tools: List[ToolDefinition]) -> ModelOutput:
    # Guardrail: some models may keep emitting the same tool call repeatedly.
    # If we already have a successful tool result, close the loop with final answer.
    if state.tool_history:
        last_tool = state.tool_history[-1]
        if last_tool.success:
            city = str(last_tool.arguments.get("city", "Unknown"))
            return ModelOutput(
                action="final_answer",
                final_answer=f"The weather in {city} is {last_tool.result}.",
            )

    api_key = os.getenv("SILICONFLOW_API_KEY", "").strip()
    if not api_key:
        return ModelOutput(
            action="final_answer",
            final_answer=(
                "SILICONFLOW_API_KEY is missing. "
                "Set AGENT_LLM_PROVIDER=mock or configure the key."
            ),
        )

    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1").strip()
    model = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct").strip()

    payload = {
        "model": model,
        "messages": _build_siliconflow_messages(state),
        "tools": _build_tools_payload(tools),
        "tool_choice": "auto",
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return ModelOutput(
            action="final_answer",
            final_answer=f"SiliconFlow request failed: {type(exc).__name__}: {exc}",
        )

    return _parse_siliconflow_response(data)


def _build_tools_payload(tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
    payload: List[Dict[str, Any]] = []
    for tool in tools:
        payload.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema,
                },
            }
        )
    return payload


def _build_siliconflow_messages(state: AgentState) -> List[Dict[str, str]]:
    system_prompt = (
        "You are a minimal agent planner.\n"
        "Return either a tool call or a final answer.\n"
        "If weather is requested and no tool result exists, call get_weather.\n"
        "If tool_history already has a successful result, produce final answer."
    )
    context = {
        "user_input": state.user_input,
        "loop_count": state.loop_count,
        "tool_history": [
            {
                "tool_name": item.tool_name,
                "arguments": item.arguments,
                "success": item.success,
                "result": item.result,
            }
            for item in state.tool_history
        ],
        "scratchpad": state.scratchpad,
    }
    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Current state JSON:\n"
                f"{json.dumps(context, ensure_ascii=False)}\n"
                "Respond according to state."
            ),
        },
    ]


def _parse_siliconflow_response(data: Dict[str, Any]) -> ModelOutput:
    message = (
        data.get("choices", [{}])[0].get("message", {})
        if isinstance(data, dict)
        else {}
    )
    tool_calls = message.get("tool_calls", [])
    if tool_calls:
        first_call = tool_calls[0]
        function = first_call.get("function", {})
        tool_name = function.get("name", "")
        raw_arguments = function.get("arguments", "{}")
        arguments = _safe_load_json_dict(raw_arguments)
        return ModelOutput(
            action="tool_call",
            tool_call=ToolCall(tool_name=tool_name, arguments=arguments),
        )

    content = str(message.get("content", "")).strip()
    if not content:
        return ModelOutput(
            action="final_answer",
            final_answer="SiliconFlow returned empty content.",
        )

    parsed = _try_parse_action_json(content)
    if parsed:
        action = parsed.get("action")
        if action == "tool_call":
            tool_name = str(parsed.get("tool_name", ""))
            arguments = parsed.get("arguments", {})
            if isinstance(arguments, dict):
                return ModelOutput(
                    action="tool_call",
                    tool_call=ToolCall(tool_name=tool_name, arguments=arguments),
                )
        if action == "final_answer":
            return ModelOutput(
                action="final_answer",
                final_answer=str(parsed.get("final_answer", "")),
            )

    return ModelOutput(action="final_answer", final_answer=content)


def _try_parse_action_json(text: str) -> Dict[str, Any] | None:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.replace("```json", "").replace("```", "").strip()
    try:
        loaded = json.loads(candidate)
    except Exception:
        return None
    if isinstance(loaded, dict):
        return loaded
    return None


def _safe_load_json_dict(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return {}
    return {}
