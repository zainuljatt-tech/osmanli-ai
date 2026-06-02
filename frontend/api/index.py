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
    _import_error = f"Error: {e}\n{traceback.format_exc()}"
    MODULE_OK = False


def app(*args):
    if len(args) == 2:
        return _wsgi(args[0], args[1])
    return _asgi(args[0], args[1], args[2])


def _wsgi(environ, start_response):
    if not MODULE_OK:
        body = _import_error.encode("utf-8")
        start_response("500 ISE", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
    body = b'{"wsgi":"ok"}'
    start_response("200 OK", [("Content-Type", "application/json")])
    return [body]


async def _asgi(scope, receive, send):
    if not MODULE_OK:
        await send({"type": "http.response.start", "status": 500, "headers": [(b"content-type", b"text/plain")]})
        await send({"type": "http.response.body", "body": _import_error.encode("utf-8")})
        return
    await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": b'{"asgi":"ok"}'})
