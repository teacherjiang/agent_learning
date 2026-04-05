import re


def extract_city_for_weather(user_text: str) -> str:
    """Very small parser for weather question examples."""
    match = re.search(r"weather\s+(in|on)\s+([A-Za-z]+)", user_text, re.IGNORECASE)
    if match:
        return match.group(2)
    return "Unknown"
