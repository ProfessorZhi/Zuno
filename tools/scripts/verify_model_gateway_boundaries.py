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
    "src/backend/zuno/agent/core/agents/codeact_agent.py",
    "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
    "src/backend/zuno/agent/core/agents/structured_response_agent.py",
    "src/backend/zuno/agent/core/models/anthropic.py",
    "src/backend/zuno/agent/core/models/embedding.py",
    "src/backend/zuno/agent/core/models/manager.py",
    "src/backend/zuno/agent/core/models/reason_model.py",
    "src/backend/zuno/agent/core/models/tool_call.py",
    "src/backend/zuno/agent/core/models/usage_model.py",
    "src/backend/zuno/api/services/mcp_chat.py",
    "src/backend/zuno/capability/tools/resume_optimizer/action.py",
    "src/backend/zuno/platform/common/extract.py",
    "src/backend/zuno/platform/common/helpers.py",
    "src/backend/zuno/platform/model_gateway.py",
    "src/backend/zuno/platform/services/autobuild/client.py",
    "src/backend/zuno/platform/services/deepsearch/graph.py",
    "src/backend/zuno/platform/services/deepsearch/stream_graph.py",
    "src/backend/zuno/platform/services/mcp_openai/mcp_manager.py",
    "src/backend/zuno/platform/services/memory/client.py",
    "src/backend/zuno/platform/services/rag/doc_parser/image.py",
    "src/backend/zuno/platform/services/rag/embedding.py",
    "src/backend/zuno/platform/services/rag/parser.py",
    "src/backend/zuno/platform/services/rag/rerank.py",
    "src/backend/zuno/platform/services/rag/vl_embedding.py",
    "src/backend/zuno/platform/services/rewrite/markdown_rewrite.py",
    "src/backend/zuno/platform/services/rewrite/query_write.py",
    "src/backend/zuno/platform/services/simple_api_tool.py",
    "src/backend/zuno/platform/services/workspace/simple_agent.py",
    "src/backend/zuno/platform/services/workspace/wechat_agent.py",
}

DISALLOWED_ACTIVE_PATHS = {
    "src/backend/zuno/agent/core/agents/general_agent.py",
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

    general_agent = (REPO_ROOT / "src/backend/zuno/agent/core/agents/general_agent.py").read_text(encoding="utf-8")
    for phrase in [
        "from zuno.platform.model_gateway import ModelGateway, build_default_model_gateway",
        "self.model_gateway.get_chat_model",
        "role=ModelRole.EXECUTOR",
    ]:
        if phrase not in general_agent:
            errors.append(f"GeneralAgent missing gateway phrase: {phrase}")
    if "ModelManager.get_" in general_agent:
        errors.append("GeneralAgent must not call ModelManager.get_* directly after PHASE03")
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
