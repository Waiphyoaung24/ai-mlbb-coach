# 🌐 Accessing MLBB AI Coach in Remote VSCode

## ✅ Current Status

Both servers are running:
- **Backend API**: Port 8000 (FastAPI)
- **Frontend Web**: Port 3000 (HTTP Server)

---

## 🔌 Method 1: VSCode Port Forwarding (Recommended)

VSCode automatically detects and forwards ports from your remote environment.

### Steps:

1. **Open the PORTS panel in VSCode**
   - Look at the bottom of your VSCode window
   - Click on the **"PORTS"** tab (next to TERMINAL, PROBLEMS, OUTPUT)
   - You should see ports 8000 and 3000 listed

2. **Access the Frontend**
   - Find port **3000** in the PORTS panel
   - Right-click on it → Select **"Open in Browser"**
   - Or click the globe icon (🌐) next to port 3000

   **Alternative:** Copy the forwarded address (usually something like):
   ```
   https://xxxxx-3000.preview.app.github.dev
   ```

3. **Access the API Documentation**
   - Find port **8000** in the PORTS panel
   - Right-click → "Open in Browser"
   - Add `/docs` to the URL to see interactive API docs
   ```
   https://xxxxx-8000.preview.app.github.dev/docs
   ```

---

## 🔌 Method 2: Manual Port Forwarding

If ports aren't automatically forwarded:

1. Click on **"PORTS"** tab at the bottom
2. Click **"Forward a Port"** button (or + icon)
3. Enter **3000** for frontend
4. Enter **8000** for backend API
5. VSCode will give you URLs to access each

---

## 🔧 Method 3: Direct Access (If Running Locally)

If you're running VSCode locally (not remote):

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📱 What You'll See

### Frontend (Port 3000)
You'll see a beautiful chat interface with:
- Purple gradient header
- Chat conversation area
- LLM provider selector (Gemini/Claude)
- Input field for questions
- Suggestion buttons

### API Docs (Port 8000/docs)
Interactive Swagger UI with:
- All available endpoints
- Try-it-out functionality
- Request/response examples
- Schema definitions

---

## 🧪 Test It's Working

### Test 1: Check Frontend is Loading
```bash
curl http://localhost:3000/ | head -20
# Should show HTML content
```

### Test 2: Check API is Responding
```bash
curl http://localhost:8000/health
# Should return JSON with status: "healthy"
```

### Test 3: Check Available Heroes
```bash
curl http://localhost:8000/api/heroes
# Should return list of hero names
```

---

## 🔍 Troubleshooting

### Port Not Showing in VSCode?

**Option 1:** Manually add the port
1. PORTS panel → "Forward a Port"
2. Enter 3000 or 8000
3. Click enter

**Option 2:** Restart the port forwarding
```bash
# VSCode Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
# Type: "Forward a Port"
# Enter the port number
```

### Can't Access the Forwarded URL?

1. **Check servers are running:**
   ```bash
   ps aux | grep -E "uvicorn|http.server"
   ```

2. **Restart servers if needed:**
   ```bash
   # Stop all
   pkill -f uvicorn
   pkill -f "http.server"

   # Restart backend
   cd /workspace/Test-AI-Matchmaking
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

   # Restart frontend
   cd /workspace/Test-AI-Matchmaking/frontend
   python3 -m http.server 3000 &
   ```

3. **Check port visibility:**
   - In PORTS panel, make sure port visibility is set to "Public" (not Private)
   - Right-click port → "Port Visibility" → "Public"

### Frontend Can't Connect to API?

If the frontend loads but can't make API calls:

**Edit the frontend to use the correct API URL:**

```bash
nano /workspace/Test-AI-Matchmaking/frontend/index.html
```

Find line ~132:
```javascript
const API_BASE = 'http://localhost:8000';
```

Change to your forwarded backend URL:
```javascript
const API_BASE = 'https://xxxxx-8000.preview.app.github.dev';
```

Or use a relative path if both are on same domain:
```javascript
const API_BASE = window.location.origin.replace('3000', '8000');
```

---

## 🎮 Quick Start Commands

### Start Both Servers
```bash
cd /workspace/Test-AI-Matchmaking

# Backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd frontend && python3 -m http.server 3000 &
```

### Stop Both Servers
```bash
pkill -f uvicorn
pkill -f "http.server"
```

### Check Server Status
```bash
# List running servers
ps aux | grep -E "uvicorn|http.server" | grep -v grep

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000/ | head -10
```

---

## 📋 VSCode Remote Development Tips

### Enable Port Auto-Forwarding

Add to your VSCode settings:
```json
{
  "remote.autoForwardPorts": true,
  "remote.autoForwardPortsSource": "process"
}
```

### Set Port Labels

In PORTS panel:
- Right-click port 3000 → "Set Label" → "MLBB Frontend"
- Right-click port 8000 → "Set Label" → "MLBB API"

### Make Ports Public

For sharing with others:
- Right-click port → "Port Visibility" → "Public"
- Share the forwarded URL

---

## 🎯 Current Server URLs

Based on your VSCode port forwarding, you'll have URLs like:

**Frontend:**
```
https://[workspace-id]-3000.[vscode-domain]
```

**API:**
```
https://[workspace-id]-8000.[vscode-domain]
```

**API Docs:**
```
https://[workspace-id]-8000.[vscode-domain]/docs
```

Look in the **PORTS** tab to see your actual URLs!

---

## ✨ You're All Set!

1. Open VSCode **PORTS** panel (bottom of screen)
2. Find port **3000**
3. Click the **🌐 globe icon** to open in browser
4. Start chatting with your MLBB AI Coach!

(Remember: You still need a valid Gemini or Claude API key for actual AI responses)

---

## 📞 Need Help?

- **Servers not running?** See "Quick Start Commands" above
- **Ports not showing?** See "Troubleshooting" section
- **Connection issues?** Check CORS settings in `.env`

**Current working directory:** `/workspace/Test-AI-Matchmaking/`
**Servers:** Running and ready! ✅
