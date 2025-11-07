"""Chess MCP Server - Streamable HTTP with Stockfish and Lichess"""

import os
import logging
from typing import Any
import chess
import chess.engine
import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from official MCP SDK
from mcp.server.fastmcp import FastMCP

# Configuration
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")
STOCKFISH_DEPTH = int(os.getenv("STOCKFISH_DEPTH", "18"))
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")
LICHESS_API_BASE = "https://lichess.org/api"
PORT = int(os.getenv("PORT", 8080))

# Global engine instance
engine = None

async def get_engine():
    """Get or create Stockfish engine instance."""
    global engine
    if engine is None:
        try:
            engine = await chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            logger.info(f"Stockfish initialized: {engine.id['name']}")
        except Exception as e:
            logger.error(f"Failed to initialize Stockfish: {e}")
            raise
    return engine

# Initialize MCP server
mcp = FastMCP("chess-mcp-server")

@mcp.tool()
async def analyze_position(fen: str, depth: int = None) -> dict[str, Any]:
    """
    Analyze a chess position using Stockfish engine.

    Args:
        fen: Position in Forsyth-Edwards Notation (FEN)
        depth: Search depth (default: 18, max: 25)

    Returns:
        Analysis with evaluation score, best move, and principal variation
    """
    try:
        if depth is None:
            depth = STOCKFISH_DEPTH

        board = chess.Board(fen)
        engine_instance = await get_engine()
        actual_depth = min(depth, 25)

        result = await engine_instance.analyse(
            board,
            chess.engine.Limit(depth=actual_depth, time=5.0)
        )

        score = result["score"].white()
        best_move = str(result["pv"][0]) if result["pv"] else None
        pv = [str(move) for move in result["pv"][:5]]

        return {
            "fen": fen,
            "evaluation": {
                "type": "mate" if score.is_mate() else "centipawns",
                "value": score.mate() if score.is_mate() else score.score(),
            },
            "best_move": best_move,
            "principal_variation": pv,
            "depth": actual_depth,
            "turn": "white" if board.turn else "black"
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"error": str(e)}

@mcp.tool()
async def get_best_move(fen: str) -> dict[str, Any]:
    """Calculate the best move for a chess position."""
    try:
        board = chess.Board(fen)
        engine_instance = await get_engine()

        result = await engine_instance.play(
            board,
            chess.engine.Limit(time=5.0, depth=STOCKFISH_DEPTH)
        )

        return {
            "best_move_uci": str(result.move),
            "best_move_san": board.san(result.move),
            "from_square": chess.square_name(result.move.from_square),
            "to_square": chess.square_name(result.move.to_square),
            "fen": fen
        }
    except Exception as e:
        logger.error(f"Best move calculation failed: {e}")
        return {"error": str(e)}

@mcp.tool()
async def validate_move(fen: str, move_uci: str) -> dict[str, Any]:
    """Check if a move is legal in a given position."""
    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(move_uci)
        is_legal = move in board.legal_moves

        result = {
            "is_legal": is_legal,
            "move_uci": move_uci,
            "original_fen": fen
        }

        if is_legal:
            san = board.san(move)
            board.push(move)
            result["move_san"] = san
            result["resulting_fen"] = board.fen()
            result["check"] = board.is_check()
            result["checkmate"] = board.is_checkmate()

        return result
    except Exception as e:
        logger.error(f"Move validation failed: {e}")
        return {"is_legal": False, "error": str(e)}

@mcp.tool()
async def get_legal_moves(fen: str) -> dict[str, Any]:
    """Get all legal moves for a position."""
    try:
        board = chess.Board(fen)
        legal_moves_uci = [str(move) for move in board.legal_moves]
        legal_moves_san = [board.san(move) for move in board.legal_moves]

        return {
            "fen": fen,
            "legal_moves_uci": legal_moves_uci,
            "legal_moves_san": legal_moves_san,
            "count": len(legal_moves_uci),
            "turn": "white" if board.turn else "black"
        }
    except Exception as e:
        logger.error(f"Failed to get legal moves: {e}")
        return {"error": str(e)}

@mcp.tool()
async def fetch_user_games(
    username: str,
    max_games: int = 10,
    time_control: str = None
) -> dict[str, Any]:
    """Fetch recent games from a Lichess user."""
    try:
        # Check if token is set
        if not LICHESS_TOKEN:
            return {
                "error": "LICHESS_TOKEN environment variable not set. Please add it in Cloud Run settings.",
                "status": "configuration_error"
            }
        
        headers = {
            "Authorization": f"Bearer {LICHESS_TOKEN}",
            "Accept": "application/x-ndjson"
        }
        max_games = min(max_games, 50)
        
        params = {
            "max": max_games,
            "pgnInJson": "true",
            "clocks": "false",
            "evals": "false",
            "opening": "true",
            "moves": "false",
            "tags": "true"
        }

        if time_control:
            params["perfType"] = time_control

        url = f"{LICHESS_API_BASE}/games/user/{username}"
        
        logger.info(f"Fetching games for user: {username}")

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            
            # Log response for debugging
            logger.info(f"Lichess API status: {response.status_code}")
            logger.info(f"Response content type: {response.headers.get('content-type')}")
            
            # Check if response is successful
            if response.status_code != 200:
                error_text = response.text[:500]  # First 500 chars
                logger.error(f"Lichess API error: {response.status_code} - {error_text}")
                return {
                    "error": f"Lichess API returned status {response.status_code}",
                    "status_code": response.status_code,
                    "response_preview": error_text,
                    "possible_causes": [
                        "Username doesn't exist" if response.status_code == 404 else None,
                        "Authentication failed - check LICHESS_TOKEN" if response.status_code == 401 else None,
                        "Token permissions insufficient" if response.status_code == 403 else None
                    ]
                }

            # Try to parse NDJSON response
            games = []
            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        import json
                        game_data = json.loads(line)
                        games.append({
                            "id": game_data.get("id"),
                            "pgn": game_data.get("pgn", ""),
                            "white": game_data.get("players", {}).get("white", {}).get("user", {}).get("name"),
                            "black": game_data.get("players", {}).get("black", {}).get("user", {}).get("name"),
                            "winner": game_data.get("winner"),
                            "opening": game_data.get("opening", {}).get("name"),
                            "time_control": game_data.get("speed"),
                            "rated": game_data.get("rated"),
                            "url": f"https://lichess.org/{game_data.get('id')}"
                        })
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse game line: {line[:100]}")
                        logger.error(f"JSON error: {e}")
                        continue

            if not games:
                return {
                    "username": username,
                    "games_count": 0,
                    "message": "No games found. User might have no public games or username doesn't exist.",
                    "games": []
                }

            return {
                "username": username,
                "games_count": len(games),
                "games": games
            }
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching games: {e}")
        return {
            "error": f"HTTP error: {e.response.status_code}",
            "details": str(e)
        }
    except Exception as e:
        logger.error(f"Failed to fetch games: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "username": username
        }

@mcp.tool()
async def get_cloud_eval(fen: str) -> dict[str, Any]:
    """Get cloud evaluation from Lichess opening database."""
    try:
        url = f"{LICHESS_API_BASE}/cloud-eval"
        params = {"fen": fen}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            pvs = data.get("pvs", [])
            best_pv = pvs[0] if pvs else {}

            return {
                "fen": fen,
                "cloud_eval": best_pv.get("cp"),
                "depth": data.get("depth"),
                "best_moves": [pv.get("moves", "").split()[0] for pv in pvs[:3] if pv.get("moves")],
                "knodes": data.get("knodes")
            }
    except Exception as e:
        logger.error(f"Cloud eval failed: {e}")
        return {"error": str(e)}

# Get the ASGI app for Cloud Run
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Chess MCP Server on port {PORT}")
    logger.info(f"Stockfish path: {STOCKFISH_PATH}")
    logger.info(f"Analysis depth: {STOCKFISH_DEPTH}")
    
    # Log token status (without exposing the actual token)
    if LICHESS_TOKEN:
        logger.info(f"LICHESS_TOKEN is set (starts with: {LICHESS_TOKEN[:8]}...)")
    else:
        logger.warning("LICHESS_TOKEN is NOT set!")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
