# QuodBall

Juego multijugador de palabras.

## Tecnologías

**Backend:** Python 3.11+, FastAPI, WebSockets, Pydantic

**Frontend:** React, Vite

## Requisitos

- Python 3.11 o superior
- Node.js 18 o superior
- uv (gestor de paquetes de Python)

## Instalación

### Backend

```bash
uv sync
```

### Frontend

```bash
cd frontend
npm install
```

## Ejecución

### Backend

```bash
uv run uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

## Tests

```bash
uv run pytest
```
