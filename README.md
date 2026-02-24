# MLBB AI Coach - RAG-Powered Coaching System

An intelligent AI coach for Mobile Legends Bang Bang (MLBB) built with LangChain, LangGraph, and FastAPI. Focuses on Marksman (MM) role coaching with plans to expand to all roles and SEA region optimization.

## Features

- **Multi-LLM Support**: Choose between Anthropic Claude and Google Gemini
- **RAG-Powered Responses**: Context-aware coaching using vector database
- **LangGraph Workflows**: Intelligent conversation flows for different coaching scenarios
- **Hero-Specific Guidance**: Detailed advice for MM heroes (Layla, Miya, Moskov, Granger, etc.)
- **Build Recommendations**: Items, emblems, and spell combinations
- **Matchup Analysis**: Counter-picks and strategy suggestions
- **Conversation Memory**: Personalized coaching based on user history

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI Framework**: LangChain, LangGraph
- **Vector Database**: Pinecone
- **LLM Providers**: Anthropic Claude, Google Gemini
- **Database**: PostgreSQL (user data, history)
- **Cache**: Redis (sessions, temporary data)
- **Deployment**: Docker

## Project Structure

```
mlbb-ai-coach/
├── app/
│   ├── api/              # FastAPI routes
│   ├── core/             # Core configuration
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   │   ├── llm/          # LLM integrations
│   │   ├── rag/          # RAG implementation
│   │   └── langgraph/    # LangGraph workflows
│   ├── data/             # MLBB data (heroes, items, etc.)
│   └── utils/            # Utilities
├── frontend/             # Web interface
├── scripts/              # Utility scripts
├── tests/                # Test suite
└── docker/               # Docker configuration
```

## Setup

1. **Clone and Install Dependencies**
```bash
cd /workspace/Test-AI-Matchmaking
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Initialize Database**
```bash
# Coming soon
```

4. **Run Development Server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/chat` - Main coaching chat endpoint
- `GET /api/heroes` - Get hero information
- `POST /api/builds/recommend` - Get build recommendations
- `POST /api/matchup/analyze` - Analyze matchups
- `GET /api/health` - Health check

## Quick Start

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

```bash
# 1. Setup
bash scripts/setup.sh
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure .env with your API keys

# 3. Ingest MLBB data
python scripts/ingest_data.py

# 4. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Open frontend/index.html in your browser
```

## Development Roadmap

- [x] Project setup and structure
- [x] Multi-LLM provider integration (Claude + Gemini)
- [x] Vector database setup (Pinecone)
- [x] MLBB data ingestion pipeline
- [x] LangGraph coaching workflows
- [x] RAG implementation with specialized retrievers
- [x] FastAPI endpoints (chat, builds, matchups)
- [x] Conversation memory and session management
- [x] Web interface
- [x] Docker deployment configuration
- [ ] Expand hero coverage beyond Marksman
- [ ] Add SEA region localization
- [ ] Implement analytics and monitoring
- [ ] Mobile app development
- [ ] Integration with MLBB APIs

## License

MIT License
