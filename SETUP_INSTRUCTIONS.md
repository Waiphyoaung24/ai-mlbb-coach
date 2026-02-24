# Setup Instructions for MLBB AI Coach

## Current Status

✅ All code files created
✅ .env file created
⚠️ Need to configure API keys
⚠️ Need to install Python packages

---

## Step-by-Step Setup

### Step 1: Configure API Keys

Edit the `.env` file and add your API keys:

```bash
nano .env
# OR
vi .env
# OR use any text editor
```

**Required API Keys:**

1. **Anthropic Claude API Key**
   - Get it from: https://console.anthropic.com/
   - Replace: `ANTHROPIC_API_KEY=your_anthropic_api_key_here`

2. **Google Gemini API Key**
   - Get it from: https://makersuite.google.com/app/apikey
   - Replace: `GOOGLE_API_KEY=your_google_api_key_here`

3. **Pinecone API Key**
   - Get it from: https://app.pinecone.io/
   - Replace: `PINECONE_API_KEY=your_pinecone_api_key_here`
   - Also set: `PINECONE_ENVIRONMENT=us-east-1` (or your region)

**Minimum .env configuration:**
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
GOOGLE_API_KEY=AIzaSyxxxxx
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east-1
DEFAULT_LLM_PROVIDER=claude
```

---

### Step 2: Install Python Dependencies

Since the system doesn't have venv, we have a few options:

#### Option A: Install system-wide (quickest for testing)

```bash
cd /workspace/Test-AI-Matchmaking
pip3 install --user -r requirements.txt
```

#### Option B: Use Docker (recommended for production)

```bash
# Make sure .env is configured first
docker-compose up -d
```

#### Option C: Install python3-venv (if you have sudo)

```bash
sudo apt update
sudo apt install -y python3.12-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 3: Initialize Pinecone Vector Database

After installing dependencies and configuring .env:

```bash
python3 scripts/ingest_data.py
```

This will:
- Create the Pinecone index
- Ingest all MLBB hero data
- Ingest item data
- Ingest strategy guides

**Expected output:**
```
Starting data ingestion...
Initializing Pinecone index...
✓ Ingested 25 hero documents
✓ Ingested 14 item documents
✓ Ingested 10 strategy documents
✅ Data ingestion complete!
```

---

### Step 4: Start the API Server

```bash
# If using system Python
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# OR if using venv
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 5: Open the Web Interface

**Option 1: Direct file access**
```bash
# Open in browser
xdg-open frontend/index.html  # Linux
open frontend/index.html      # Mac
```

**Option 2: Serve with Python**
```bash
cd frontend
python3 -m http.server 3000
```

Then visit: http://localhost:3000

**Option 3: Update frontend to use correct API URL**

Edit `frontend/index.html` line 132:
```javascript
const API_BASE = 'http://localhost:8000';  // Change if needed
```

---

## Quick Test

Once the server is running, test the API:

```bash
# Health check
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Layla", "llm_provider": "claude"}'
```

---

## Troubleshooting

### Issue: "No module named 'fastapi'"

**Solution:** Install dependencies first
```bash
pip3 install --user -r requirements.txt
```

### Issue: "No LLM providers configured"

**Solution:** Check .env file has valid API keys
```bash
cat .env | grep API_KEY
```

### Issue: "Pinecone index not found"

**Solution:** Run the ingestion script
```bash
python3 scripts/ingest_data.py
```

### Issue: "Redis connection failed"

**Solution:** This is optional - system will use in-memory storage
```bash
# Install Redis (optional)
sudo apt install redis-server
sudo systemctl start redis
```

### Issue: Port 8000 already in use

**Solution:** Use a different port
```bash
uvicorn app.main:app --reload --port 8001
```

---

## Docker Alternative (Easiest)

If you have Docker installed:

```bash
# 1. Configure .env file
nano .env

# 2. Build and start
docker-compose up -d

# 3. View logs
docker-compose logs -f api

# 4. Access
# Web: http://localhost
# API: http://localhost/api/
```

---

## What's Next?

Once running:
1. ✅ Test the health endpoint
2. ✅ Try the web interface
3. ✅ Ask questions about MLBB heroes
4. ✅ Get build recommendations
5. ✅ Analyze matchups

---

## Current Working Directory

All files are in:
```
/workspace/Test-AI-Matchmaking/
```

Navigate there:
```bash
cd /workspace/Test-AI-Matchmaking
ls -la
```

---

## Need Help?

- Check `GETTING_STARTED.md` for detailed setup
- Check `DEPLOYMENT.md` for production deployment
- Check API docs: http://localhost:8000/docs (when server is running)

---

## Summary Checklist

- [ ] Edit .env with API keys
- [ ] Install Python dependencies (`pip3 install --user -r requirements.txt`)
- [ ] Run data ingestion (`python3 scripts/ingest_data.py`)
- [ ] Start API server (`python3 -m uvicorn app.main:app --reload`)
- [ ] Open frontend/index.html in browser
- [ ] Test the chat!
