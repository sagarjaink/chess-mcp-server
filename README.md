# Chess MCP Server

Chess analysis MCP server with Stockfish and Lichess integration - Deploy without any command line tools!

## Features

- **Stockfish Engine Integration** - Deep position analysis and best move calculation
- **Lichess API Integration** - Fetch user games, cloud evaluations, and opening database
- **Web-Based Deployment** - No CLI required, all through browser interfaces
- **Claude.ai Integration** - Connect directly to Claude Pro/Max/Team/Enterprise
- **Free Hosting** - Deploy on Google Cloud Run free tier

## MCP Tools Available

Once deployed, Claude.ai can use these tools:

1. **analyze_position** - Deep analysis with evaluation scores and principal variations
2. **get_best_move** - Calculate the best move for any position
3. **validate_move** - Check if a move is legal
4. **get_legal_moves** - List all legal moves in a position
5. **fetch_user_games** - Get recent games from any Lichess user
6. **get_cloud_eval** - Access Lichess master game database

---

# Deployment Guide - No Command Line Required!

**This guide uses only web browsers - no terminal, no CLI tools needed.**

## What You'll Use

- GitHub Web Interface - Create files in your browser
- Google Cloud Console - Deploy using web UI
- Claude.ai Settings - Web interface for connection

**Time Required:** 1-2 hours
**Technical Level:** Beginner-friendly

---

## Prerequisites

You need accounts (all free):
- [ ] GitHub account - https://github.com/signup
- [ ] Google Cloud account - https://console.cloud.google.com
- [ ] Lichess account - https://lichess.org/signup
- [ ] Claude.ai Pro/Max/Team/Enterprise - https://claude.ai

---

## PART 1: Get Lichess API Token

### Step 1: Create Lichess Token

1. Go to https://lichess.org and sign in
2. Go to https://lichess.org/account/oauth/token
3. Under **"Personal API access tokens"**, click **"New token"**
4. Fill in:
   - **Token description:** `Chess MCP Server`
   - **Scopes:** Check these boxes:
     - ✅ **Read preferences**
     - ✅ **Read games**
5. Click **"Create"**
6. **Copy the token** - you'll need it in the next step
   - ⚠️ Save it somewhere safe! You won't see it again.

---

## PART 2: Set Up Google Cloud

### Step 2.1: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Sign in with your Google account
3. Click on the project dropdown (top left, says "Select a project")
4. Click **"NEW PROJECT"**
5. Fill in:
   - **Project name:** `chess-mcp-server`
   - **Location:** Leave as default
6. Click **"CREATE"**
7. Wait 30 seconds, then select your new project from the dropdown

### Step 2.2: Enable Billing (Required for Free Tier)

1. In left menu, click **"Billing"** or go to https://console.cloud.google.com/billing
2. Click **"Link a billing account"** or **"Create billing account"**
3. Follow steps to add payment method
   - ✅ You get **$300 free credits**
   - ✅ Won't be charged if you stay in free tier
   - ✅ Can set billing alerts

### Step 2.3: Enable Required APIs

1. Go to **APIs & Services** → **Library** or https://console.cloud.google.com/apis/library
2. Search for and enable each of these (click on them, then click **"ENABLE"**):
   - **Cloud Run API**
   - **Cloud Build API**
   - **Artifact Registry API**
   - **Secret Manager API**

Each takes 10-30 seconds to enable.

### Step 2.4: Create Secret for Lichess Token

1. Go to **Secret Manager** in left menu or https://console.cloud.google.com/security/secret-manager
2. Click **"CREATE SECRET"**
3. Fill in:
   - **Name:** `lichess-token`
   - **Secret value:** Paste your Lichess API token from Step 1
4. Click **"CREATE SECRET"**

---

## PART 3: Deploy to Cloud Run

### Step 3.1: Open Cloud Run

1. Go to **Cloud Run** in left menu or https://console.cloud.google.com/run
2. Click **"CREATE SERVICE"**

### Step 3.2: Configure Deployment

Fill in the form:

**Container section:**
1. Choose **"Continuously deploy from a repository (source-based)"**
2. Click **"SET UP WITH CLOUD BUILD"**
3. In the popup:
   - **Repository provider:** Select **"GitHub"**
   - Click **"AUTHENTICATE"** and authorize Google Cloud to access GitHub
   - **Repository:** Select your `chess-mcp-server` repository (or your fork)
   - **Branch:** `^main$` (or `^master$` depending on your default branch)
   - **Build type:** **"Dockerfile"**
   - Click **"SAVE"**

**Service settings:**
- **Service name:** `chess-mcp-server`
- **Region:** Choose one close to you (e.g., `us-central1`)
- **CPU allocation:** Select **"CPU is only allocated during request processing"**

**Authentication:**
- Select **"Allow unauthenticated invocations"** (for now - can secure later)

**Container settings** (click "Container, Networking, Security"):
- **Container port:** `8080`
- **Memory:** `2 GiB`
- **CPU:** `2`
- **Maximum requests per container:** `10`
- **Timeout:** `60` seconds
- **Minimum instances:** `0`
- **Maximum instances:** `5`

**Environment Variables** (in "Variables & Secrets" tab):
1. Click **"ADD VARIABLE"**
   - **Name:** `STOCKFISH_PATH`
   - **Value:** `/usr/games/stockfish`
2. Click **"ADD VARIABLE"**
   - **Name:** `STOCKFISH_DEPTH`
   - **Value:** `18`

**Secrets** (in same "Variables & Secrets" tab):
1. Click **"REFERENCE A SECRET"**
   - **Secret:** Select `lichess-token`
   - **Version:** `latest`
   - **Exposed as environment variable:** ✅
   - **Name:** `LICHESS_TOKEN`

### Step 3.3: Deploy!

1. Click **"CREATE"** at the bottom
2. Wait 3-5 minutes for deployment
   - You'll see a building animation
   - Can click **"LOGS"** to watch progress

When you see ✅ green checkmark, you're done!

### Step 3.4: Get Your Service URL

1. You'll see your service URL at the top, like:
   ```
   https://chess-mcp-server-abc123xyz-uc.a.run.app
   ```
2. **Copy this URL** - you'll need it for Claude.ai

---

## PART 4: Connect to Claude.ai

### Step 4.1: Add Custom Connector

1. Go to https://claude.ai
2. Sign in with your Pro/Max/Team/Enterprise account
3. Click **Settings** (gear icon in bottom-left)
4. Click **Integrations** tab
5. Scroll to **"Custom Connectors"** section
6. Click **"Add Connector"** or **"+"** button

### Step 4.2: Configure Connector

Fill in the form:

- **Display Name:** `Chess Analysis`
- **Description (optional):** `Analyze chess games with Stockfish and Lichess`
- **Server URL:** `https://your-cloud-run-url.run.app/mcp`
  - ⚠️ **Important:** Add `/mcp` at the end!
  - Example: `https://chess-mcp-server-abc123-uc.a.run.app/mcp`
- **API Key (optional):** Leave blank for now

### Step 4.3: Save and Enable

1. Click **"Add"** or **"Save"**
2. Find your connector in the list
3. Toggle it **ON** (should turn blue/active)

---

## PART 5: Test with Claude!

### Try these commands:

**Test 1: Analyze a position**
```
Analyze this chess position:
rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1

What should Black play?
```

**Test 2: Get best move**
```
What's the best move for White in this position?
FEN: r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4
```

**Test 3: Fetch Lichess games**
```
Show me the last 5 games from Lichess user "DrNykterstein"
```

If Claude responds using your tools and gives you chess analysis, **it's working!**

---

## Troubleshooting

### Issue: "Deployment failed"
- Go to **Cloud Build** → **History** in Google Cloud Console
- Click on the failed build and read error logs

### Issue: "Claude can't connect"
- Verify your URL ends with `/mcp`
- Check connector is enabled (toggled on)
- Make sure you have Claude Pro/Max/Team/Enterprise

### Issue: "Stockfish not found"
- Check that `STOCKFISH_PATH` environment variable is set to `/usr/games/stockfish`
- Review Cloud Run logs for errors

---

## Cost Information

**Monthly cost:** $0 (stays in free tier for typical usage)

Google Cloud Run free tier includes:
- 2 million requests per month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds

This is more than enough for personal chess analysis use.

---

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Technical Details

- **Language:** Python 3.11
- **Framework:** FastMCP (Model Context Protocol)
- **Chess Engine:** Stockfish
- **Chess Library:** python-chess
- **HTTP Client:** httpx
- **Container:** Docker on Cloud Run

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Cloud Run logs in Google Cloud Console
3. Open an issue on GitHub

---

**You now have a live chess analysis server integrated with Claude.ai!**
