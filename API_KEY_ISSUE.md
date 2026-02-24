# ⚠️ API Key Issue - How to Fix

## Current Problem

The Gemini API key in your `.env` file is returning a `400 Bad Request` error, which means it's invalid or expired.

```
Error: HTTP/1.1 400 Bad Request
API key not valid. Please pass a valid API key.
```

---

## ✅ Solution: Get a New API Key

### Step 1: Get a Valid Gemini API Key

1. **Visit Google AI Studio:**
   - Go to: https://aistudio.google.com/apikey
   - Or: https://makersuite.google.com/app/apikey

2. **Sign in** with your Google account

3. **Create API Key:**
   - Click "Create API Key" or "Get API Key"
   - Select a project or create a new one
   - Copy the API key (starts with `AIza...`)

### Step 2: Update Your `.env` File

```bash
# Edit the .env file
nano /workspace/Test-AI-Matchmaking/.env

# Find this line:
GOOGLE_API_KEY=AIzaSyBriDaAo5xs4BNwrMeAmD_RB90WAd55WTcw

# Replace with your new key:
GOOGLE_API_KEY=your_new_api_key_here
```

### Step 3: Restart the Server

```bash
# Stop the current server
pkill -f uvicorn

# Start it again
cd /workspace/Test-AI-Matchmaking
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

---

## ✅ Updated Model Configuration

I've already updated your `.env` to use the latest Gemini 3.1 Pro Preview model:

```env
GEMINI_MODEL=gemini-3.1-pro-preview
```

This model has:
- ✅ 1,048,576 input tokens
- ✅ 65,536 output tokens
- ✅ Better thinking and reasoning
- ✅ Optimized for agentic workflows
- ✅ Knowledge cutoff: January 2025

---

## 🎯 Quick Test After Getting New Key

Once you have a valid API key:

```bash
# Test the chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Layla in one sentence",
    "llm_provider": "gemini"
  }'
```

Expected response:
```json
{
  "response": "Layla is a long-range marksman...",
  "session_id": "...",
  "suggestions": [...]
}
```

---

## 🔄 Alternative: Use Anthropic Claude Instead

If you can't get a Gemini key, you can use Claude instead:

### Get Claude API Key:
1. Visit: https://console.anthropic.com/
2. Sign up for an account (they give free credits)
3. Go to API Keys section
4. Create a new key

### Update `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-your_key_here
DEFAULT_LLM_PROVIDER=claude
```

### Restart server:
```bash
pkill -f uvicorn
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

---

## 📋 Current Server Status

✅ **Server:** Running on port 8000
✅ **Model:** Updated to gemini-3.1-pro-preview
✅ **Frontend:** Port 3000 (ready for you to start manually)
⚠️ **API Key:** Needs to be updated

---

## 🐛 Common API Key Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Invalid API key | Get new key from Google AI Studio |
| 401 Unauthorized | Missing API key | Add key to .env file |
| 429 Too Many Requests | Rate limit exceeded | Wait or upgrade plan |
| 403 Forbidden | API not enabled | Enable Gemini API in Google Cloud Console |

---

## 📚 Resources

- **Google AI Studio:** https://aistudio.google.com/
- **Gemini API Docs:** https://ai.google.dev/gemini-api/docs
- **Get API Key:** https://aistudio.google.com/apikey
- **Anthropic Console:** https://console.anthropic.com/

---

## ✨ Next Steps

1. ✅ Get a valid Gemini API key from Google AI Studio
2. ✅ Update `/workspace/Test-AI-Matchmaking/.env`
3. ✅ Restart the server: `pkill -f uvicorn && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &`
4. ✅ Test in your browser via the frontend
5. ✅ Start chatting with your MLBB AI Coach!

---

**Your server is running and ready - just needs a valid API key!** 🚀
