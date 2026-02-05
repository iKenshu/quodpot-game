"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .websocket.handler import get_ws_handler

app = FastAPI(
    title="Maze Game",
    description="Multiplayer maze game with hangman mechanics",
    version="0.1.0",
)

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def index():
    """Serve the game client."""
    return FileResponse(STATIC_DIR / "index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for game connections."""
    handler = get_ws_handler()
    await handler.handle_connection(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
