import os

os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(os.path.sep, 'tmp', 'app.db')}")

def app(environ, start_response):
    body = b'{"hello":"world"}'
    start_response("200 OK", [("Content-Type", "application/json")])
    return [body]
