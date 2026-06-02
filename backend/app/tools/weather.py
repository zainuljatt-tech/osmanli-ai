import httpx
import logging

logger = logging.getLogger(__name__)


async def get_weather(location: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://wttr.in/{location}?format=%C+%t+%h+%w",
                headers={"User-Agent": "curl/8.0"},
            )
            if resp.status_code == 200:
                parts = resp.text.strip().split()
                return {
                    "location": location,
                    "conditions": parts[0] if len(parts) > 0 else "Unknown",
                    "temperature": parts[1] if len(parts) > 1 else "N/A",
                    "humidity": parts[2] if len(parts) > 2 else "N/A",
                    "wind": parts[3] if len(parts) > 3 else "N/A",
                }
            return {"location": location, "error": "Could not fetch weather"}
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return {"location": location, "error": str(e)}


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or location",
                }
            },
            "required": ["location"],
        },
    },
}
