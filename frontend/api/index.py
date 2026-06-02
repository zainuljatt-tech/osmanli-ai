import os

os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(os.path.sep, 'tmp', 'app.db')}")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("SECRET_KEY", os.urandom(32).hex())
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("DEBUG", "false")

try:
    from app.main import app as fastapi_app
    _err = None
except Exception as e:
    import traceback
    _err = f"Import error: {e}\n{traceback.format_exc()}"

if _err:
    def app(environ, start_response):
        body = _err.encode("utf-8")
        start_response("500 ISE", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
else:
    def app(environ, start_response):
        return fastapi_app(environ, start_response)
