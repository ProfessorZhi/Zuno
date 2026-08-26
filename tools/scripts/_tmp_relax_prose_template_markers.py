from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def replace_block(path: Path, start_marker: str, end_marker: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def main() -> None:
    render = ROOT / "tools/agent/render_architecture.py"
    replace_block(
        render,
        "    required_sections = [\n",
        "    required_terms = [\n",
        '''    required_sections = [
        "# Zuno 总体 Target 架构",
        "## Part A — Architecture Narrative",
        "## Part B — Detailed Architecture Specification",
        "### B1 Scope and Global Invariants",
        "### B2 Responsibility / Ownership Map",
        "### B3 Cross-boundary Contracts",
        "### B5 State Machines",
        "### B6 Retry / Replan / Reconcile",
        "### B7 Failure Semantics",
        "### B8 Security / Approval / Audit",
        "### B9 Recovery and Idempotency",
        "### B10 Persistence Boundaries",
        "### B11 Observability / Evaluation",
        "### B12 Current / Target / Gap",
        "### B13 Evidence / Verification",
        "### B14 Code / Database / Migration Constraints",
    ]
''',
    )
    replace_block(
        render,
        "    required_terms = [\n",
        "    errors: list[str] = []\n",
        '''    required_terms = [
        "模块化 Python 后端",
        "独立网络服务",
        "Application & Integration",
        "Legal Domain & Work Product",
        "Knowledge & Evidence",
        "Agent Runtime & Control",
        "Capability & Skill",
        "Tool Runtime & Effects",
        "Model Gateway",
        "Security & Governance",
        "Observability & Evaluation",
        "Platform / Infrastructure",
        "FastAPI",
        "LangGraph",
        "PostgreSQL",
        "Checkpoint",
        "Reconciliation",
        "Current",
        "Target",
        "History",
        "Logical Responsibility",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
    ]
''',
    )
    text = render.read_text(encoding="utf-8")
    text = text.replace(
        '''    if "9 个 Target Logical Modules" not in content or "Round 02" not in content:
        errors.append("architecture.md must record the frozen nine-module target and its Round 02 source")

''',
        "",
    )
    render.write_text(text, encoding="utf-8")

    document_set = ROOT / "tools/scripts/verify_architecture_document_set.py"
    text = document_set.read_text(encoding="utf-8")
    text = text.replace(
        '''    if "9 个 Target Logical Modules" not in design or "Round 02" not in design:
        errors.append("architecture.md must record the frozen nine-module Target and Round 02 source")

''',
        "",
    )
    replace_block(
        document_set,
        "    narrative_markers = (\n",
        "    for marker in narrative_markers:\n",
        '''    narrative_markers = (
        "Zuno 面向智慧司法和法律专业工作",
        "简单问答",
        "为什么按“事实谁负责”切架构",
        "九个责任域不是九段必须依次经过的流水线",
        "一项复杂机制什么时候应该主动删除",
        "Single Controller",
        "Runtime Control State（运行控制状态）",
        "AdmissionReceipt",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
        "Retry != Replan != Reconcile",
        "EffectReceipt",
        "AuditPersistenceReceipt",
    )
''',
    )
    old_module_markers = '''        "01 应用与集成",
        "02 法律领域",
        "03 知识证据",
        "04 运行控制",
        "05 专业能力",
        "06 工具外部效果",
        "07 模型网关",
        "08 安全治理",
        "09 可观测性评测",
'''
    new_module_markers = '''        "01-application-integration.md",
        "02-legal-domain-work-product.md",
        "03-knowledge-evidence.md",
        "04-agent-runtime-control.md",
        "05-capability-skill.md",
        "06-tool-runtime-effects.md",
        "07-model-gateway.md",
        "08-security-governance.md",
        "09-observability-evaluation.md",
'''
    text = document_set.read_text(encoding="utf-8")
    if old_module_markers not in text:
        raise RuntimeError("cannot locate old modules README phrase markers")
    document_set.write_text(text.replace(old_module_markers, new_module_markers), encoding="utf-8")

    Path(__file__).unlink()


if __name__ == "__main__":
    main()
