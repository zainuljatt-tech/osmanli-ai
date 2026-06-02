from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.database import init_db, close_db
from app.api.v1 import auth, chat, memory, documents, websearch, voice, admin, billing
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"DB init failed: {e}")
    yield
    logger.info("Shutting down...")
    close_db()


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)

cors_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if cors_origins == ["*"] else cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = int((time.time() - start) * 1000)
    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(websearch.router, prefix="/api/v1/websearch", tags=["Web Search"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "api": "/api/v1",
    }


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION, "service": settings.APP_NAME}


@app.get("/api/v1/models")
def get_models():
    return {
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI", "description": "Most capable GPT model", "supports_tools": True, "supports_streaming": True},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI", "description": "Fast and affordable", "supports_tools": True, "supports_streaming": True},
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "provider": "Anthropic", "description": "Best-in-class coding and analysis", "supports_tools": True, "supports_streaming": True},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "provider": "Google", "description": "Google's most capable model", "supports_tools": False, "supports_streaming": True},
            {"id": "ollama/llama3.1", "name": "Llama 3.1 (Local)", "provider": "Ollama", "description": "Local Llama 3.1 8B", "supports_tools": False, "supports_streaming": True},
        ]
    }
