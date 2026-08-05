from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PATTERNS = [
    "ModelManager.get_",
    "ChatOpenAI(",
    "OpenAI(",
    "AsyncOpenAI(",
    "Anthropic(",
]

ALLOWED_LEGACY_PATHS = {
    "src/backend/zuno/agent/core/agents/structured_response_agent.py",
    "src/backend/zuno/api/services/mcp_chat.py",
    "src/backend/zuno/platform/common/helpers.py",
    "src/backend/zuno/platform/model_gateway.py",
    "src/backend/zuno/platform/model_gateway_adapters.py",
    "src/backend/zuno/platform/services/deepsearch/graph.py",
    "src/backend/zuno/platform/services/deepsearch/stream_graph.py",
    "src/backend/zuno/platform/services/memory/client.py",
    "src/backend/zuno/platform/services/rag/rerank.py",
    "src/backend/zuno/platform/services/rag/vl_embedding.py",
    "src/backend/zuno/platform/services/rewrite/markdown_rewrite.py",
    "src/backend/zuno/platform/services/rewrite/query_write.py",
    "src/backend/zuno/platform/services/simple_api_tool.py",
    "src/backend/zuno/platform/services/workspace/simple_agent.py",
    "src/backend/zuno/platform/services/workspace/wechat_agent.py",
}

DISALLOWED_ACTIVE_PATHS = {
    "src/backend/zuno/agent/runtime",
}


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def verify_model_gateway_boundaries() -> list[str]:
    errors: list[str] = []
    for path in (REPO_ROOT / "src/backend/zuno").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        relative = _relative(path)
        text = path.read_text(encoding="utf-8")
        hits = [pattern for pattern in PATTERNS if pattern in text]
        if not hits:
            continue
        if relative in ALLOWED_LEGACY_PATHS:
            continue
        if relative in DISALLOWED_ACTIVE_PATHS or any(relative.startswith(item) for item in DISALLOWED_ACTIVE_PATHS):
            errors.append(f"active runtime path bypasses Model Gateway: {relative}: {', '.join(hits)}")
            continue
        errors.append(f"unclassified direct model call path: {relative}: {', '.join(hits)}")

    # GeneralAgent was retired in the PHASE22 backend semantic legacy cleanup;
    # its model-gateway compliance is no longer checked because the module no
    # longer exists. The canonical runtime routes every model call through the
    # Model Gateway (see zuno.agent.runtime.execution.model_step.ModelStepExecutor).
    if (REPO_ROOT / "src/backend/zuno/agent/core/agents/general_agent.py").exists():
        errors.append("retired GeneralAgent module must not exist")
    return errors


def main() -> int:
    errors = verify_model_gateway_boundaries()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Model Gateway boundary verification failed.")
        return 1
    print("Model Gateway boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
