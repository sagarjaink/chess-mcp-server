FROM python:3.11-slim

# Install Stockfish chess engine
RUN apt-get update && \
    apt-get install -y --no-install-recommends stockfish && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Environment variables
ENV STOCKFISH_PATH=/usr/games/stockfish
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "server.py"]
```

---

### FILE 4: requirements.txt

**Location:** Root of your GitHub repository  
**Action:** Copy this ENTIRE file (NO CHANGES from your original)
```
fastmcp>=1.0.0
python-chess>=1.10.0
httpx>=0.27.0
aiohttp>=3.9.0
uvicorn>=0.27.0
starlette>=0.27.0
python-dotenv>=1.0.0
```

---

### FILE 5: .dockerignore

**Location:** Root of your GitHub repository  
**Action:** Copy this ENTIRE file (NO CHANGES from your original)
```
.git/
.gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.log
.env
README.md
docs/
tests/
```

---

### FILE 6: .gitignore

**Location:** Root of your GitHub repository  
**Action:** Copy this ENTIRE file (NO CHANGES from your original)
```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[codz]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environments
.env
.envrc
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Logs
*.log

# IDE
.vscode/
.idea/
```

---

# 📋 COMPLETE DEPLOYMENT STEPS

## STEP 1: Get Lichess Token

1. Go to: https://lichess.org/account/oauth/token
2. Click **"New token"**
3. Token description: `Chess MCP Server`
4. Check: **"Read preferences"** ✅ (this is enough!)
5. Click **"Create"**
6. **COPY THE TOKEN** and save it somewhere

---

## STEP 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `chess-mcp-server`
3. Set to **Public**
4. Click **"Create repository"**
5. Upload these 6 files (use the "Add file" → "Upload files" button):
   - cloudbuild.yaml
   - server.py
   - Dockerfile
   - requirements.txt
   - .dockerignore
   - .gitignore

---

## STEP 3: Deploy to Cloud Run

1. Go to: https://console.cloud.google.com/run
2. Click **"CREATE SERVICE"**
3. Select: **"Continuously deploy from a repository"**
4. Click **"SET UP WITH CLOUD BUILD"**
5. In the popup:
   - Repository provider: **GitHub**
   - Click **"AUTHENTICATE"** and authorize Google Cloud
   - Select your repository: `chess-mcp-server`
   - Branch: `^main$`
   - Build type: **Dockerfile**
   - Click **"SAVE"**

6. Back on the main form:
   - Service name: `chess-mcp-server`
   - Region: `us-central1`
   - Authentication: **"Allow unauthenticated invocations"**

7. Click **"CONTAINER, NETWORKING, SECURITY"**

8. **Container tab:**
   - Container port: `8080`
   - Memory: `2 GiB`
   - CPU: `2`
   - Request timeout: `300`

9. **Variables & Secrets tab:**
   - Click **"ADD VARIABLE"** and add:
     - Name: `STOCKFISH_PATH` Value: `/usr/games/stockfish`
   - Click **"ADD VARIABLE"** and add:
     - Name: `STOCKFISH_DEPTH` Value: `18`
   - Click **"ADD VARIABLE"** and add:
     - Name: `PORT` Value: `8080`
   - Click **"ADD VARIABLE"** and add:
     - Name: `PYTHONUNBUFFERED` Value: `1`
   - Click **"ADD VARIABLE"** and add:
     - Name: `LICHESS_TOKEN` Value: **[PASTE YOUR LICHESS TOKEN HERE]**

10. **Autoscaling:**
    - Minimum instances: `0`
    - Maximum instances: `10`

11. Click **"CREATE"**

12. Wait 3-5 minutes

13. When done, **COPY YOUR SERVICE URL** (looks like: `https://chess-mcp-server-xxxxx-uc.a.run.app`)

---

## STEP 4: Test Your Deployment

Open these in your browser:

**Test 1:**
```
https://YOUR-SERVICE-URL.run.app/health
```
Should show: `{"status":"healthy","service":"chess-mcp-server"}`

**Test 2:**
```
https://YOUR-SERVICE-URL.run.app/mcp
```
Should show: HTTP 405 error (this is correct!)

If both work, you're good! ✅

---

## STEP 5: Connect to Claude.ai

1. Go to: https://claude.ai
2. Click **Settings** (gear icon, bottom-left)
3. Click **"Integrations"** tab
4. Find **"Custom Connectors"**
5. Click **"Add Connector"** or **"+"**
6. Fill in:
   - Display Name: `Chess Analysis`
   - Description: `Analyze chess with Stockfish and Lichess`
   - Server URL: `https://YOUR-SERVICE-URL.run.app/mcp` ⚠️ **MUST end with /mcp**
   - API Key: **Leave blank**
7. Click **"Save"**
8. **Toggle it ON** (should turn blue)

---

## STEP 6: Test with Claude!

In a new Claude conversation, try:
```
My Lichess username is YourUsername. 
Fetch my last 5 games and analyze my performance.
