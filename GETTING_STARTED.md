# Getting Started with MLBB AI Coach

Complete guide to set up and run the MLBB AI Coach system.

## Prerequisites

- Python 3.11 or higher
- API Keys:
  - Anthropic API key (for Claude)
  - Google API key (for Gemini)
  - Pinecone API key (for vector database)
- Docker (optional, for containerized deployment)
- Redis (optional, for session management)

## Quick Start

### 1. Clone and Setup

```bash
cd /workspace/Test-AI-Matchmaking

# Run setup script
bash scripts/setup.sh

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file with your API keys:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
PINECONE_API_KEY=your_pinecone_key_here

# Pinecone Configuration
PINECONE_ENVIRONMENT=us-east-1  # or your region
PINECONE_INDEX_NAME=mlbb-coach

# Choose default LLM
DEFAULT_LLM_PROVIDER=claude  # or gemini
```

### 3. Initialize Vector Database

Ingest the MLBB knowledge base into Pinecone:

```bash
python scripts/ingest_data.py
```

This will:
- Create the Pinecone index
- Load hero data (Marksman heroes: Layla, Miya, Moskov, Granger, Bruno)
- Load item data (equipment, builds)
- Load strategy guides (positioning, farming, team fights)

### 4. Start the API Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# OR use the dev script
bash scripts/dev.sh
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 5. Open the Web Interface

Open `frontend/index.html` in your browser, or serve it with:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 3000
```

Then visit: http://localhost:3000

## Docker Deployment

For production deployment with Docker:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services included:
- FastAPI backend (port 8000)
- Nginx web server (port 80)
- Redis (session storage)
- PostgreSQL (user data)

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List available providers
curl http://localhost:8000/api/providers

# Chat request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Layla",
    "llm_provider": "claude"
  }'
```

### Using the test script

```bash
python scripts/test_api.py
```

## Usage Examples

### Basic Chat

```python
import requests

response = requests.post("http://localhost:8000/api/chat", json={
    "message": "How do I play Miya effectively?",
    "llm_provider": "claude"
})

print(response.json()["response"])
```

### Get Build Recommendations

```python
response = requests.post("http://localhost:8000/api/builds/recommend", json={
    "hero_name": "Granger",
    "situation": "ahead",
    "enemy_composition": ["Natalia", "Chou", "Kagura"]
})

build = response.json()
print(f"Core items: {build['core_items']}")
print(f"Reasoning: {build['reasoning']}")
```

### Analyze Matchups

```python
response = requests.post("http://localhost:8000/api/matchup/analyze", json={
    "your_hero": "Layla",
    "enemy_hero": "Natalia",
    "lane": "Gold Lane"
})

matchup = response.json()
print(f"Difficulty: {matchup['difficulty']}")
print(f"Tips: {matchup['tips']}")
```

## Project Structure

```
mlbb-ai-coach/
├── app/
│   ├── api/              # FastAPI routes
│   ├── core/             # Configuration
│   ├── models/           # Data models
│   ├── services/
│   │   ├── llm/          # LLM providers (Claude, Gemini)
│   │   ├── rag/          # RAG & vector store
│   │   └── langgraph/    # Coaching workflows
│   ├── data/             # MLBB knowledge base
│   └── utils/            # Session management
├── frontend/             # Web interface
├── scripts/              # Utility scripts
├── docker/               # Docker configs
└── tests/                # Test suite
```

## Features

### 1. Multi-LLM Support
- Switch between Claude (Anthropic) and Gemini (Google)
- Dynamic model selection per request
- Automatic fallback handling

### 2. RAG-Powered Coaching
- Vector database with MLBB knowledge
- Context-aware responses
- Specialized retrievers for heroes, builds, strategies

### 3. LangGraph Workflows
- Intent classification
- Dynamic context retrieval
- Structured coaching conversations

### 4. Conversation Memory
- Session-based chat history
- Redis-backed storage
- User context tracking

### 5. Specialized Endpoints
- `/api/chat` - General coaching chat
- `/api/builds/recommend` - Build recommendations
- `/api/matchup/analyze` - Matchup analysis
- `/api/heroes` - Hero information

## Adding More Content

### Add New Heroes

1. Create hero data in `app/data/heroes/`:

```json
{
  "id": "new_hero",
  "name": "New Hero",
  "role": "Marksman",
  "strengths": [...],
  "weaknesses": [...]
}
```

2. Re-run ingestion:

```bash
python scripts/ingest_data.py
```

### Add New Strategies

Add strategy guides in `app/data/strategies/`:

```json
{
  "title": "Advanced Positioning",
  "category": "positioning",
  "role": "Marksman",
  "content": "..."
}
```

## Troubleshooting

### API Keys Not Working

- Verify keys are correctly set in `.env`
- Check if keys have proper permissions
- Test with `/api/providers` endpoint

### Vector Store Issues

- Ensure Pinecone API key is valid
- Check index name matches configuration
- Re-run ingestion script

### LangChain/LangGraph Errors

- Update dependencies: `pip install -U langchain langgraph`
- Check Python version (3.11+ required)

### Redis Connection Failed

- Redis is optional for development
- System will fall back to in-memory storage
- Install Redis: `sudo apt install redis-server` (Linux)

## Next Steps

1. **Expand Hero Coverage**: Add more heroes beyond Marksman
2. **Meta Updates**: Add current patch notes and meta information
3. **Pro Player Builds**: Integrate professional player statistics
4. **Analytics**: Add usage tracking and response quality monitoring
5. **SEA Optimization**: Add localization for Southeast Asian languages
6. **Mobile App**: Build React Native or Flutter mobile client

## Performance Tips

- Use Redis for production (better session management)
- Enable response caching for common queries
- Use connection pooling for database
- Monitor LLM token usage and costs
- Optimize vector search parameters (top_k, threshold)

## Production Checklist

- [ ] Set strong SECRET_KEY in .env
- [ ] Use PostgreSQL for persistent data
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup for database
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Configure CDN for static assets
- [ ] Set up CI/CD pipeline

## Support

- GitHub Issues: [Report bugs or request features]
- Documentation: See `README.md`
- API Docs: http://localhost:8000/docs

## License

MIT License - See LICENSE file for details
