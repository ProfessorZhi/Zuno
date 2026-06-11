from __future__ import annotations

import argparse
import hashlib
import math
import re
import socket
import threading
import time
from contextlib import contextmanager
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


DEFAULT_MODEL_NAME = "zuno-local-embedding-dev"
DEFAULT_DIMENSION = 64
ASCII_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]{2,}")
CJK_BLOCK_PATTERN = re.compile(r"[\u4e00-\u9fff]+")
TECH_ALIAS_MAP: dict[str, tuple[str, ...]] = {
    "系统设计": ("architecture", "system design"),
    "架构": ("architecture",),
    "层次": ("levels", "layers"),
    "角色": ("roles",),
    "部署": ("deployment", "deploy"),
    "组成部分": ("parts", "components"),
    "核心组成部分": ("core parts", "components"),
    "持久化": ("persistence", "persist", "storage"),
    "默认后端": ("default backend",),
    "三类数据": ("three types of data",),
    "执行路径": ("execution path", "lifecycle"),
    "运行路径": ("execution path", "lifecycle"),
    "恢复": ("resume",),
    "中断": ("interrupt",),
    "精确匹配": ("exact matching",),
    "匹配逻辑": ("matching logic",),
    "威胁建模": ("threat modeling",),
    "攻击面": ("attack surface",),
    "过程": ("process",),
    "引言": ("introduction",),
    "挑战": ("challenges",),
    "指标": ("metrics",),
    "论文": ("paper",),
    "关系": ("relation", "relationship"),
    "作用": ("purpose", "use"),
    "保存什么": ("store what", "what is stored"),
    "分别保存什么": ("what does each store",),
}


class EmbeddingRequest(BaseModel):
    model: str = Field(default=DEFAULT_MODEL_NAME)
    input: str | list[str]
    encoding_format: str = Field(default="float")


def _normalize_inputs(payload: str | list[str]) -> list[str]:
    if isinstance(payload, str):
        return [payload]
    return [str(item or "") for item in payload]


def _embed_text(text: str, *, dimension: int = DEFAULT_DIMENSION) -> list[float]:
    normalized = _expand_aliases(str(text or "").lower())
    values = [0.0] * max(int(dimension), 8)
    for token in _tokenize(normalized):
        token_bytes = token.encode("utf-8")
        digest = hashlib.sha256(token_bytes).digest()
        bucket = int.from_bytes(digest[:4], "big") % len(values)
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        weight = 1.0 + min(len(token), 12) / 12.0
        values[bucket] += sign * weight

    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return values
    return [round(value / norm, 6) for value in values]


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    normalized = str(text or "")
    for token in ASCII_TOKEN_PATTERN.findall(normalized):
        tokens.append(token)
        if len(token) >= 4:
            tokens.extend(token[index : index + 3] for index in range(len(token) - 2))
    for block in CJK_BLOCK_PATTERN.findall(normalized):
        tokens.append(block)
        if len(block) >= 2:
            tokens.extend(block[index : index + 2] for index in range(len(block) - 1))
        else:
            tokens.append(block)
    return tokens


def _expand_aliases(text: str) -> str:
    expanded = str(text or "")
    extras: list[str] = []
    for phrase, aliases in TECH_ALIAS_MAP.items():
        if phrase in expanded:
            extras.extend(aliases)
    if extras:
        expanded = f"{expanded} {' '.join(extras)}"
    return expanded


def create_app(*, model_name: str = DEFAULT_MODEL_NAME, dimension: int = DEFAULT_DIMENSION) -> FastAPI:
    app = FastAPI(title="Zuno Local Embedding Dev Server", version="1.0.0")

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {"status": "ok", "model": model_name, "dimension": dimension}

    @app.post("/v1/embeddings")
    async def create_embeddings(request: EmbeddingRequest) -> dict[str, Any]:
        inputs = _normalize_inputs(request.input)
        data = [
            {
                "object": "embedding",
                "index": index,
                "embedding": _embed_text(text, dimension=dimension),
            }
            for index, text in enumerate(inputs)
        ]
        total_tokens = sum(max(1, len(text.split())) for text in inputs)
        return {
            "object": "list",
            "data": data,
            "model": request.model or model_name,
            "usage": {
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens,
            },
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
    raise TimeoutError(f"timed out waiting for local embedding server at http://{host}:{port}")


def _pick_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


@contextmanager
def run_dev_server(
    *,
    host: str = "127.0.0.1",
    port: int = 11434,
    model_name: str = DEFAULT_MODEL_NAME,
    dimension: int = DEFAULT_DIMENSION,
):
    import uvicorn

    resolved_port = _pick_free_port(host) if int(port) == 0 else int(port)
    config = uvicorn.Config(
        create_app(model_name=model_name, dimension=dimension),
        host=host,
        port=resolved_port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="zuno-local-embedding-server", daemon=True)
    thread.start()
    _wait_for_server(host, resolved_port)
    try:
        yield {
            "host": host,
            "port": resolved_port,
            "base_url": f"http://{host}:{resolved_port}/v1",
            "model_name": model_name,
            "dimension": dimension,
        }
    finally:
        server.should_exit = True
        thread.join(timeout=3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local OpenAI-compatible embedding dev server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=11434)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--dimension", type=int, default=DEFAULT_DIMENSION)
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        create_app(model_name=args.model_name, dimension=args.dimension),
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
