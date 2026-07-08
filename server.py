"""
HF Model Explorer — a local chatbot harness for exploring open foundational
and medical LLMs via Ollama. Everything runs on-device; no cloud calls.

Endpoints:
  GET  /                 -> serves the white chat UI
  GET  /api/catalog      -> curated model list (grouped) + which are installed
  GET  /api/models       -> models currently installed in Ollama
  POST /api/chat         -> streaming chat completion (proxies Ollama /api/chat)
  POST /api/pull         -> streaming model pull from Ollama library or Hugging Face
"""

import json
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
ROOT = Path(__file__).parent
CATALOG = json.loads((ROOT / "models.json").read_text())

app = FastAPI(title="HF Model Explorer")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (ROOT / "index.html").read_text()


@app.get("/api/models")
async def list_models() -> JSONResponse:
    """Return the tags (models) currently installed in Ollama."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{OLLAMA}/api/tags")
            r.raise_for_status()
            names = [m["name"] for m in r.json().get("models", [])]
            return JSONResponse({"installed": names})
    except Exception as e:  # Ollama not running / unreachable
        return JSONResponse({"installed": [], "error": str(e)}, status_code=200)


@app.get("/api/catalog")
async def catalog() -> JSONResponse:
    """Curated catalog plus the set of installed model names for badging."""
    installed = set()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{OLLAMA}/api/tags")
            r.raise_for_status()
            installed = {m["name"] for m in r.json().get("models", [])}
    except Exception:
        pass

    def is_installed(mid: str) -> bool:
        # Ollama appends :latest to library models with no explicit tag.
        return mid in installed or f"{mid}:latest" in installed

    groups = []
    for g in CATALOG["curated"]:
        groups.append({
            "group": g["group"],
            "models": [
                {**m, "installed": is_installed(m["id"])} for m in g["models"]
            ],
        })
    return JSONResponse({"groups": groups})


@app.post("/api/chat")
async def chat(request: Request) -> StreamingResponse:
    """Proxy a streaming chat completion from Ollama, forwarding NDJSON lines."""
    body = await request.json()
    payload = {
        "model": body["model"],
        "messages": body["messages"],
        "stream": True,
    }

    async def gen():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", f"{OLLAMA}/api/chat", json=payload) as r:
                    if r.status_code != 200:
                        text = await r.aread()
                        yield json.dumps({"error": text.decode("utf-8", "ignore")}) + "\n"
                        return
                    async for line in r.aiter_lines():
                        if line.strip():
                            yield line + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


@app.post("/api/pull")
async def pull(request: Request) -> StreamingResponse:
    """Pull a model from the Ollama library or Hugging Face (hf.co/...).

    Streams Ollama's pull progress as NDJSON so the UI can show a progress bar.
    """
    body = await request.json()
    model = body["model"].strip()

    async def gen():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST", f"{OLLAMA}/api/pull",
                    json={"model": model, "stream": True},
                ) as r:
                    if r.status_code != 200:
                        text = await r.aread()
                        yield json.dumps({"error": text.decode("utf-8", "ignore")}) + "\n"
                        return
                    async for line in r.aiter_lines():
                        if line.strip():
                            yield line + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
