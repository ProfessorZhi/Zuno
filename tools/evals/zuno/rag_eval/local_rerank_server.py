from __future__ import annotations

import argparse
import socket
import threading
import time
from contextlib import contextmanager
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


DEFAULT_MODEL_NAME = "zuno-local-rerank-dev"


class RerankParameters(BaseModel):
    return_documents: bool = Field(default=True)
    top_n: int = Field(default=5)


class RerankInput(BaseModel):
    query: str
    documents: list[str]


class RerankRequest(BaseModel):
    model: str = Field(default=DEFAULT_MODEL_NAME)
    input: RerankInput
    parameters: RerankParameters = Field(default_factory=RerankParameters)


def _tokenize(text: str) -> set[str]:
    normalized = str(text or "").lower()
    tokens = [part.strip() for part in normalized.replace("\n", " ").split(" ") if part.strip()]
    return set(tokens)


def _char_ngrams(text: str, n: int = 2) -> set[str]:
    normalized = "".join(ch for ch in str(text or "").lower() if not ch.isspace())
    if len(normalized) < n:
        return {normalized} if normalized else set()
    return {normalized[index : index + n] for index in range(len(normalized) - n + 1)}


def _score(query: str, document: str) -> float:
    query_tokens = _tokenize(query)
    document_tokens = _tokenize(document)
    token_overlap = len(query_tokens & document_tokens)
    query_bigrams = _char_ngrams(query, 2)
    document_bigrams = _char_ngrams(document, 2)
    bigram_overlap = len(query_bigrams & document_bigrams)
    query_chars = set(ch for ch in str(query or "").lower() if not ch.isspace())
    document_chars = set(ch for ch in str(document or "").lower() if not ch.isspace())
    char_overlap = len(query_chars & document_chars)
    if not token_overlap and not bigram_overlap and not char_overlap:
        return 0.0
    token_score = min(1.0, token_overlap / max(1, len(query_tokens))) if query_tokens else 0.0
    bigram_score = min(1.0, bigram_overlap / max(1, len(query_bigrams))) if query_bigrams else 0.0
    char_score = min(1.0, char_overlap / max(1, len(query_chars))) if query_chars else 0.0
    if str(query or "").strip() and str(query).strip() in str(document or ""):
        return 1.0
    return round(max(token_score, 0.85 * bigram_score, 0.7 * char_score), 6)


def create_app(*, model_name: str = DEFAULT_MODEL_NAME) -> FastAPI:
    app = FastAPI(title="Zuno Local Rerank Dev Server", version="1.0.0")

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {"status": "ok", "model": model_name}

    @app.post("/rerank")
    async def rerank(request: RerankRequest) -> dict[str, Any]:
        query = request.input.query
        documents = list(request.input.documents or [])
        rows = [
            {
                "index": index,
                "relevance_score": _score(query, document),
                "document": document,
            }
            for index, document in enumerate(documents)
        ]
        rows.sort(key=lambda item: item["relevance_score"], reverse=True)
        top_n = max(1, int(request.parameters.top_n or len(rows)))
        return {
            "output": {
                "results": rows[:top_n],
            },
            "model": request.model or model_name,
        }

    return app


def _wait_for_server(host: str, port: int, *, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f"timed out waiting for local rerank server at http://{host}:{port}")


def _pick_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


@contextmanager
def run_dev_server(
    *,
    host: str = "127.0.0.1",
    port: int = 11435,
    model_name: str = DEFAULT_MODEL_NAME,
):
    import uvicorn

    resolved_port = _pick_free_port(host) if int(port) == 0 else int(port)
    config = uvicorn.Config(
        create_app(model_name=model_name),
        host=host,
        port=resolved_port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="zuno-local-rerank-server", daemon=True)
    thread.start()
    _wait_for_server(host, resolved_port)
    try:
        yield {
            "host": host,
            "port": resolved_port,
            "base_url": f"http://{host}:{resolved_port}/rerank",
            "model_name": model_name,
        }
    finally:
        server.should_exit = True
        thread.join(timeout=3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local rerank dev server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=11435)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        create_app(model_name=args.model_name),
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
