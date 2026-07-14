from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# One-time deterministic integration finalizer. Delete after successful application.


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.write_text(content, encoding="utf-8", newline="\n")


def patch_architecture() -> None:
    formal = ROOT / "docs/architecture/architecture.md"
    content = formal.read_text(encoding="utf-8")
    marker = "## 0. 正式事实源与文档边界\n"
    compatibility = """## 0.1 统一术语与状态边界\n\n本文也是 **Zuno Target Architecture Atlas** 的文字总架构，回答“项目定位与架构目标”，整合十一逻辑模块与六个物理运行域。产品 Runtime 继续采用 **Single Controller Agent Runtime**。跨模块消息使用 `CrossModuleEnvelope` / `CrossModuleEnvelopeV1` 语义。\n\n设计完成不能冒充工程完成。允许声明 `design available`、`contract-complete`、`implementation-spec-complete` 和 `program-ready`；只有代码、Migration、测试和运行证据齐备后才能声明 `implementation available`。本文不声明 `quality proven` 或 `production ready`。\n\n"""
    if compatibility not in content:
        content = content.replace(marker, marker + "\n" + compatibility, 1)
    write("docs/architecture/architecture.md", content)
    write(".agent/architecture/architecture.md", content)


def patch_agents() -> None:
    path = ROOT / "AGENTS.md"
    content = path.read_text(encoding="utf-8")
    block = """\n## 十一模块正式路由\n\n架构和实现任务必须读取对应领域 Owner 的唯一正式模块文档：\n\n```text\ndocs/modules/01-product-surface.md\ndocs/modules/02-input-document-ingestion.md\ndocs/modules/03-knowledge-agentic-graphrag.md\ndocs/modules/04-model-gateway.md\ndocs/modules/05-memory-context.md\ndocs/modules/06-agent-core-planning-control.md\ndocs/modules/07-capability-skill.md\ndocs/modules/08-tool-runtime.md\ndocs/modules/09-security.md\ndocs/modules/10-observability-eval.md\ndocs/modules/11-infrastructure.md\n```\n\n总架构只负责跨模块集成，不覆盖模块 Owner。Tool Runtime 任务必须读取 `docs/modules/08-tool-runtime.md`；Capability / Skill 与 Tool Runtime 的 Ownership 以 07、08 两份唯一模块文档共同对齐。\n\n统一验证至少包含：\n\n```text\npython tools/scripts/verify_architecture_document_set.py\npython tools/scripts/verify_agent_core_target_protocols.py\npython tools/scripts/verify_tool_runtime_target_protocols.py\n```\n"""
    if "## 十一模块正式路由" not in content:
        content = content.rstrip() + "\n" + block
    write("AGENTS.md", content)


def patch_tool_verifier() -> None:
    path = ROOT / "tools/scripts/verify_tool_runtime_target_protocols.py"
    content = path.read_text(encoding="utf-8")
    old = '''CAPABILITY_REQUIRED = [\n    "07 只保存 Capability、Skill 和 Planner Projection",\n    "08 保存权威 Tool Definition、Version、Prepare、Attempt、Observation、Effect 和 Reconciliation",\n    "MCP Tool execution\\n    08 Tool Runtime",\n]\n'''
    new = '''CAPABILITY_REQUIRED = [\n    "ToolCapabilityDescriptor",\n    "ToolDefinitionRef",\n    "ToolDefinition、PreparedToolAction、ToolAttempt、EffectReceipt 或 EffectReconciliation",\n    "真实 API、CLI、MCP、SDK、Browser、RPC 或数据库执行",\n    "连接、执行或确认外部效果",\n    "08 Tool Runtime",\n]\n'''
    if old not in content:
        raise RuntimeError("Tool Runtime verifier capability block not found")
    content = content.replace(old, new, 1)
    write("tools/scripts/verify_tool_runtime_target_protocols.py", content)


def patch_workflow() -> None:
    path = ROOT / ".github/workflows/architecture-document-set.yml"
    content = path.read_text(encoding="utf-8")
    replacements = {
        "run: |\n          python -m py_compile": "run: |\n          set -o pipefail\n          python -m py_compile",
        "run: python tools/scripts/verify_architecture_document_set.py 2>&1 | tee": "run: set -o pipefail; python tools/scripts/verify_architecture_document_set.py 2>&1 | tee",
        "run: python tools/agent/render_architecture.py --check 2>&1 | tee": "run: set -o pipefail; python tools/agent/render_architecture.py --check 2>&1 | tee",
        "run: |\n          {\n            python tools/scripts/verify_docs_entrypoints.py": "run: |\n          set -o pipefail\n          {\n            python tools/scripts/verify_docs_entrypoints.py",
        "run: |\n          pytest -q": "run: |\n          set -o pipefail\n          pytest -q",
    }
    for old, new in replacements.items():
        if old not in content:
            raise RuntimeError(f"workflow marker not found: {old}")
        content = content.replace(old, new, 1)
    write(".github/workflows/architecture-document-set.yml", content)


def main() -> None:
    patch_architecture()
    patch_agents()
    patch_tool_verifier()
    patch_workflow()
    print("Wave 2 architecture integration finalization applied.")


if __name__ == "__main__":
    main()
