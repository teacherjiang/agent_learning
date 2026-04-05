from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    func: Callable[..., str]


def get_weather(city: str) -> str:
    weather_map = {
        "tokyo": "Sunny, 22C",
        "beijing": "Cloudy, 18C",
        "shanghai": "Rainy, 20C",
        "shenzhen": "Humid, 26C",
    }
    return weather_map.get(city.lower(), "Unknown weather")


def _validate_get_weather_arguments(arguments: Dict[str, Any]) -> None:
    if "city" not in arguments:
        raise ValueError("Missing required argument: city")
    if not isinstance(arguments["city"], str):
        raise ValueError("Argument city must be a string")
    if not arguments["city"].strip():
        raise ValueError("Argument city cannot be empty")


def get_tools() -> List[ToolDefinition]:
    return [
        ToolDefinition(
            name="get_weather",
            description="Get weather by city name",
            parameters_schema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. Tokyo",
                    }
                },
                "required": ["city"],
                "additionalProperties": False,
            },
            func=get_weather,
        )
    ]


def get_tool_map() -> Dict[str, ToolDefinition]:
    return {tool.name: tool for tool in get_tools()}


def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> None:
    if tool_name == "get_weather":
        _validate_get_weather_arguments(arguments)
        return
    raise ValueError(f"No validator for tool: {tool_name}")
