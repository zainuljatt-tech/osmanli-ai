import math
import re


def calculate(expression: str) -> dict:
    try:
        sanitized = re.sub(r'[^0-9+\-*/().,%^ ]', '', expression)
        result = eval(sanitized, {"__builtins__": {}}, math.__dict__)
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e), "expression": expression}


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
}
