import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(os.path.sep, 'tmp', 'app.db')}")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("SECRET_KEY", os.urandom(32).hex())
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("DEBUG", "false")


async def simple_asgi(scope, receive, send):
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({
        "type": "http.response.body",
        "body": json.dumps({"status": "ok", "mode": "simple_asgi"}).encode(),
    })


def _build_scope(environ):
    headers = []
    for k, v in environ.items():
        if k.startswith("HTTP_"):
            name = k[5:].replace("_", "-").lower()
            headers.append((name.encode(), v.encode()))
    ct = environ.get("CONTENT_TYPE", "")
    if ct:
        headers.append((b"content-type", ct.encode()))
    cl = environ.get("CONTENT_LENGTH", "")
    if cl:
        headers.append((b"content-length", cl.encode()))
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": environ.get("REQUEST_METHOD", "GET"),
        "scheme": environ.get("wsgi.url_scheme", "http"),
        "path": environ.get("PATH_INFO", "/"),
        "query_string": environ.get("QUERY_STRING", "").encode(),
        "headers": headers,
        "server": (environ.get("SERVER_NAME", ""), int(environ.get("SERVER_PORT", "80"))),
        "client": (environ.get("REMOTE_ADDR", ""), 0),
    }


def app(environ, start_response):
    try:
        path = environ.get("PATH_INFO", "")
        
        if path == "/api/simple":
            body = b'{"simple":true}'
            start_response("200 OK", [("Content-Type", "application/json")])
            return [body]
        
        asgi_app = None
        if path.startswith("/api/v1/"):
            from app.main import app as fastapi_app
            asgi_app = fastapi_app
        
        if asgi_app is None:
            body = b'{"error":"no route"}'
            start_response("404 Not Found", [("Content-Type", "application/json")])
            return [body]
        
        scope = _build_scope(environ)
        status_code = 200
        response_headers = []
        response_body = b""
        
        async def receive():
            body_data = environ.get("wsgi.input")
            if body_data:
                data = body_data.read(1024 * 1024)
                if data:
                    return {"type": "http.request", "body": data, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}
        
        async def send(message):
            nonlocal status_code, response_headers, response_body
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = [(k.decode(), v.decode()) for k, v in message["headers"]]
            elif message["type"] == "http.response.body":
                response_body = message.get("body", b"")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(asgi_app(scope, receive, send))
        finally:
            loop.close()
        
        start_response(f"{status_code} {'OK' if status_code < 400 else 'Error'}", response_headers)
        return [response_body]
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        body = f"Handler error: {e}\n{tb}".encode("utf-8")
        start_response("500 ISE", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
