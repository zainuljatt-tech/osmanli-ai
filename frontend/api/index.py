import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("USE_SQLITE", "true")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(os.path.sep, 'tmp', 'app.db')}")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("SECRET_KEY", os.urandom(32).hex())
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("DEBUG", "false")

from app.main import app
from mangum import Mangum

handler = Mangum(app)
