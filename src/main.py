"""FastAPI application entry point."""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from websocket.handler import get_ws_handler

app = FastAPI(
    title="Multi-Game Platform",
    description="Multiplayer gaming platform featuring Hangman and Arcane Duels",
    version="0.2.0",
)

STATIC_DIR = Path(__file__).parent / "static"

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
    return {"status": "ok", "games": ["hangman", "duels"]}


app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for game connections."""
    handler = get_ws_handler()
    await handler.handle_connection(websocket)


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the SPA for all routes (catch-all for client-side routing)."""
    file_path = STATIC_DIR / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
