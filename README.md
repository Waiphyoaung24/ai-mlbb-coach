# MLBB AI Coach

AI-powered coaching platform for Mobile Legends: Bang Bang, built for the Myanmar gaming community. Provides personalized hero guidance, build recommendations, matchup analysis, and team coaching through conversational AI — in both Burmese and English.

## Architecture

SaaS-ready monolith: FastAPI backend with JWT auth, PostgreSQL via async SQLAlchemy + Alembic, React + Vite + TypeScript frontend with i18n. LangChain/LangGraph RAG pipeline powers the coaching intelligence.

## Features

- **AI Coaching Chat** — Context-aware conversations powered by LangGraph workflows and RAG
- **Multi-LLM Support** — Anthropic Claude and Google Gemini
- **Hero Database** — Stats, builds, matchups, and role-specific advice
- **MLBB Account Linking** — Connect game accounts via MLBB Academy API
- **Burmese + English i18n** — Full localization for Myanmar market
- **JWT Authentication** — Secure user accounts with free/pro tiers

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| AI/ML | LangChain, LangGraph, Pinecone, Sentence Transformers |
| LLMs | Anthropic Claude, Google Gemini |
| Database | PostgreSQL (prod), SQLite (test) |
| Cache | Redis |
| Auth | JWT (python-jose, passlib) |

## Project Structure

```
ai-mlbb-coach/
├── app/
│   ├── api/
│   │   ├── v1/           # Versioned API routes (auth, chat, heroes, players)
│   │   └── deps.py       # Shared dependencies (auth, DB session)
│   ├── core/             # Config, security, database engine
│   ├── models/
│   │   ├── db/           # SQLAlchemy ORM models
│   │   └── schemas/      # Pydantic request/response schemas
│   ├── services/
│   │   ├── llm/          # LLM provider factory
│   │   ├── rag/          # Vector store + retrievers
│   │   ├── langgraph/    # Coaching graph workflows
│   │   └── mlbb_academy/ # MLBB Academy API client
│   ├── data/             # MLBB knowledge base (JSON)
│   └── utils/            # Session manager, helpers
├── frontend/             # React + Vite + TypeScript
│   └── src/
│       ├── pages/        # Login, Dashboard, Chat
│       ├── lib/          # API client, auth, i18n
│       └── locales/      # en.json, my.json
├── alembic/              # Database migrations
├── tests/                # pytest test suite
└── docs/                 # Design docs and plans
```

## Setup

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Run migrations (requires PostgreSQL)
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173, proxies API to :8000
```

### Tests

```bash
pytest -v
cd frontend && npm run build
```

## API Endpoints

### Auth
- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/auth/login` — Get JWT token
- `GET /api/v1/auth/me` — Current user profile

### Chat
- `POST /api/v1/chat/` — AI coaching conversation

### Heroes
- `GET /api/v1/heroes/` — List all heroes
- `GET /api/v1/heroes/{hero_id}` — Hero details

### Players
- `POST /api/v1/players/link-account` — Link MLBB game account
- `POST /api/v1/players/verify-account` — Verify linked account
- `GET /api/v1/players/me/profile` — Player profile
- `POST /api/v1/players/me/sync` — Sync match history

### Legacy (preserved)
- `POST /api/chat` — Original chat endpoint
- `GET /api/heroes` — Original heroes list
- `POST /api/builds/recommend` — Build recommendations
- `POST /api/matchup/analyze` — Matchup analysis

## Design Documentation

- [SaaS Design Doc](docs/plans/2026-02-24-mlbb-saas-coach-design.md)
- [Phase 1 Implementation Plan](docs/plans/2026-02-24-phase1-implementation.md)

## License

MIT License
