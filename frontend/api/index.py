import sys
import os
import asyncio
import json
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("VERCEL_PYTHON_ASGI_SUPPORT", "1")
os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(os.path.sep, 'tmp', 'app.db')}")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("SECRET_KEY", os.urandom(32).hex())
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("DEBUG", "false")

from app.main import app as asgi_app


def _build_scope(environ):
    path = environ.get("PATH_INFO", "/")
    qs = environ.get("QUERY_STRING", "")
    
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
    
    server = environ.get("SERVER_NAME", ""), int(environ.get("SERVER_PORT", "80"))
    client = environ.get("REMOTE_ADDR", ""), 0
    
    scheme = environ.get("wsgi.url_scheme", "http")
    
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": environ.get("REQUEST_METHOD", "GET"),
        "scheme": scheme,
        "path": path,
        "raw_path": path.encode(),
        "query_string": qs.encode(),
        "root_path": "",
        "headers": headers,
        "server": server,
        "client": client,
    }


def app(environ, start_response):
    try:
        return _wsgi_handler(environ, start_response)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        start_response("500 Internal Server Error", [("Content-Type", "text/plain; charset=utf-8")])
        return [f"Error: {e}\n{tb}".encode("utf-8")]


def _wsgi_handler(environ, start_response):
    scope = _build_scope(environ)
    
    status_code = 200
    response_headers = []
    response_body = []
    
    async def receive():
        body = environ.get("wsgi.input", None)
        if body:
            data = body.read(1024*1024)
            if data:
                return {"type": "http.request", "body": data, "more_body": False}
        return {"type": "http.request", "body": b"", "more_body": False}
    
    async def send(message):
        nonlocal status_code, response_headers
        if message["type"] == "http.response.start":
            status_code = message["status"]
            response_headers = [
                (k.decode(), v.decode()) for k, v in message["headers"]
            ]
        elif message["type"] == "http.response.body":
            response_body.append(message.get("body", b""))
    
    async def run():
        await asgi_app(scope, receive, send)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run())
    finally:
        loop.close()
    
    start_response(f"{status_code} {'OK' if status_code < 400 else 'Error'}", response_headers)
    return response_body
