import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(os.path.sep, 'tmp', 'app.db')}")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("SECRET_KEY", os.urandom(32).hex())
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("DEBUG", "false")

try:
    from app.main import app as fastapi_app
    MODULE_OK = True
except Exception as e:
    import traceback
    _import_error = f"Import error: {e}\n{traceback.format_exc()}"
    MODULE_OK = False


def app(environ, start_response):
    if not MODULE_OK:
        body = _import_error.encode("utf-8")
        start_response("500 Internal Server Error", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(body)))])
        return [body]
    
    path = environ.get("PATH_INFO", "")
    if path == "/api/debug":
        body = b'{"import":"ok","module":"fastapi_app loaded"}'
        start_response("200 OK", [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
        return [body]
    
    start_response("200 OK", [("Content-Type", "application/json")])
    return [b'{"status":"ok"}']
