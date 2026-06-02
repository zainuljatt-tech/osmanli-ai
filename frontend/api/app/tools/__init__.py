from .calculator import calculate, TOOL_DEFINITION as CALC_TOOL
from .python_executor import execute_python, TOOL_DEFINITION as PYTHON_TOOL
from .weather import get_weather, TOOL_DEFINITION as WEATHER_TOOL

AVAILABLE_TOOLS = {
    "calculator": {"func": calculate, "def": CALC_TOOL},
    "python_executor": {"func": execute_python, "def": PYTHON_TOOL},
    "get_weather": {"func": get_weather, "def": WEATHER_TOOL},
}

TOOL_DEFINITIONS = [t["def"] for t in AVAILABLE_TOOLS.values()]
