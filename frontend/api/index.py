import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(os.path.sep, 'tmp', 'app.db')}")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("SECRET_KEY", os.urandom(32).hex())
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("DEBUG", "false")


def app(environ, start_response):
    try:
        from app.main import app as fastapi_app
    except Exception as e:
        import traceback
        body = f"Import error: {e}\n{traceback.format_exc()}".encode("utf-8")
        start_response("500 ISE", [("Content-Type", "text/plain; charset=utf-8")])
        return [body]
    
    return fastapi_app(environ, start_response)
