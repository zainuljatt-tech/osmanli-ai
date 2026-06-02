# AI Assistant Platform

A production-ready AI assistant platform similar to ChatGPT, Claude, and Grok. Supports multiple AI models, RAG, web search, voice I/O, file analysis, and more.

## Features

- **Multi-Model AI** - OpenAI GPT-4o, Anthropic Claude 3.5, Google Gemini, Ollama local models
- **Streaming Chat** - Real-time streaming responses with markdown and code highlighting
- **RAG Pipeline** - Upload PDFs, DOCX, CSV, TXT files for semantic search and Q&A
- **Web Search** - Internet search with source citations and content extraction
- **Long-term Memory** - Persistent user memory with vector similarity search
- **Voice I/O** - Speech-to-text and text-to-speech capabilities
- **Agent Tools** - Calculator, Python execution, weather, and extensible tool system
- **User System** - JWT auth, OAuth/Google login, email verification, profile management
- **Subscription** - Stripe billing with Free, Pro ($20/mo), and Enterprise plans
- **Admin Dashboard** - User management, analytics, revenue tracking, error monitoring
- **Dark Mode** - Full dark/light theme support

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, TailwindCSS, Shadcn UI |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL 16 + pgvector, Redis |
| AI | OpenAI, Anthropic, Gemini, Ollama |
| Infrastructure | Docker, Docker Compose, Nginx |
| CI/CD | GitHub Actions |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)
- API keys for AI providers (optional for basic usage)

### Using Docker (Recommended)

```bash
# Clone and enter the project
git clone <repo-url> ai-assistant
cd ai-assistant

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

**Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
cp .env.example .env
# Edit .env

# Start PostgreSQL and Redis first, then:
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Full API documentation is available at `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc).

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Create account |
| POST | `/api/v1/auth/login` | Sign in |
| POST | `/api/v1/auth/google` | Google OAuth |
| POST | `/api/v1/chat` | Create chat |
| GET | `/api/v1/chat` | List chats |
| POST | `/api/v1/chat/{id}/messages` | Send message (streaming) |
| POST | `/api/v1/documents/upload` | Upload file for RAG |
| POST | `/api/v1/memory` | Save memory |
| POST | `/api/v1/memory/search` | Semantic memory search |
| POST | `/api/v1/websearch/search` | Search internet |
| POST | `/api/v1/voice/stt` | Speech-to-text |
| POST | `/api/v1/voice/tts` | Text-to-speech |
| GET | `/api/v1/admin/dashboard` | Admin stats |
| POST | `/api/v1/billing/create-checkout` | Stripe checkout |

## Project Structure

```
ai-assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # API routes
│   │   ├── core/          # Config, security, dependencies
│   │   ├── db/            # Database setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── agents/        # AI agent orchestrator
│   │   ├── rag/           # RAG pipeline
│   │   ├── voice/         # Speech services
│   │   ├── tools/         # Agent tools
│   │   └── main.py        # FastAPI application
│   ├── migrations/        # Alembic migrations
│   └── tests/             # Test suite
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & API client
│   │   ├── store/         # Zustand stores
│   │   └── types/         # TypeScript types
│   └── package.json
├── infra/
│   ├── nginx/             # Nginx config
│   └── monitoring/        # Monitoring setup
├── .github/workflows/     # CI/CD pipelines
├── docker-compose.yml
└── README.md
```

## Database Schema

- **users** - User accounts, roles, auth
- **chats** - Conversations with model config
- **messages** - Chat messages with token tracking
- **memories** - Vector-searchable user memories
- **documents** - Uploaded files metadata
- **document_chunks** - Chunked text with embeddings
- **subscriptions** - Stripe subscription data
- **payments** - Payment history
- **user_usage** - Daily usage tracking
- **api_logs** - API request logging

## Deployment

### Production with Docker

```bash
# Set production environment
cp .env.example .env
# Set DEBUG=false, configure real secrets

# Build and start
docker compose -f docker-compose.yml up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Create admin user
docker compose exec backend python -c "
from app.core.security import get_password_hash
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
# ... admin creation script
"
```

### Environment Variables

See `.env.example` for all configuration options.

## Security

- JWT access/refresh token authentication
- Bcrypt password hashing
- CORS origin validation
- Input sanitization and validation
- Rate limiting via Redis
- SQL injection prevention via SQLAlchemy
- Stripe webhook signature verification
- Sensible file upload restrictions

## License

MIT
