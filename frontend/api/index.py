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
    path = environ.get("PATH_INFO", "")
    if path == "/api/test":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"Simple WSGI works"]
    
    try:
        from app.main import app as fastapi_app
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [f"Import error: {e}\n{tb}".encode()]
    
    return fastapi_app(environ, start_response)
