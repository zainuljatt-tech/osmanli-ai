import sys
import io
import json


def execute_python(code: str) -> dict:
    try:
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        restricted_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool, "bytes": bytes,
                "chr": chr, "complex": complex, "dict": dict, "divmod": divmod,
                "enumerate": enumerate, "filter": filter, "float": float,
                "format": format, "frozenset": frozenset, "hash": hash, "hex": hex,
                "id": id, "int": int, "isinstance": isinstance, "issubclass": issubclass,
                "iter": iter, "len": len, "list": list, "map": map, "max": max,
                "min": min, "next": next, "object": object, "oct": oct, "ord": ord,
                "pow": pow, "print": print, "range": range, "repr": repr,
                "reversed": reversed, "round": round, "set": set, "slice": slice,
                "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
                "type": type, "zip": zip, "True": True, "False": False, "None": None,
            },
            "json": json,
            "math": __import__("math"),
            "random": __import__("random"),
            "datetime": __import__("datetime"),
            "collections": __import__("collections"),
            "itertools": __import__("itertools"),
        }

        exec(code, restricted_globals)
        output = buffer.getvalue()
        sys.stdout = old_stdout

        return {"output": output, "success": True}
    except Exception as e:
        sys.stdout = old_stdout
        return {"error": str(e), "success": False}


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "python_executor",
        "description": "Execute Python code in a sandboxed environment",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute",
                }
            },
            "required": ["code"],
        },
    },
}
