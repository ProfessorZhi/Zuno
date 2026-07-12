from __future__ import annotations

from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[2]


def replace_once(text: str, pattern: str, replacement: str, *, flags: int = 0) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"expected one replacement for pattern: {pattern!r}; got {count}")
    return updated


def sync_architecture() -> None:
    formal = ROOT / "docs/architecture/architecture.md"
    mirror = ROOT / ".agent/architecture/architecture.md"
    text = formal.read_text(encoding="utf-8")

    text = text.replace(
        "docs/architecture/production-readiness.md",
        "docs/status/production-readiness.md",
    )
    text = text.replace(
        "Agent Runtime 默认采用 **Single Controller**；",
        "Agent Runtime 默认采用 **Single Controller Agent Runtime**；",
    )
    text = text.replace(
        """Request
-> Context
-> Plan
-> ReAct Step
-> Reflection
-> optional Replan
-> Final Reflection
-> Finalize
-> Reflexion Candidate""",
        """Request
-> Context
-> Plan
-> ReAct Step
-> Reflection
-> optional Replan
-> FinalCandidate
-> Final Gate / Final Reflection
-> ArtifactVersion / Publication
-> RunOutcome
-> Reflexion Candidate""",
    )

    section = """# 5. Agent Core / Planning & Control

## 5.1 模块定位

Agent Core 是 Zuno 的 **Single Controller Agent Runtime**。它把目标、计划、执行、等待、恢复、质量判断和最终发布组织成一个不可绕过的受治理闭环。

完整 Target 由三份模块规范共同定义：

```text
docs/modules/06-agent-core-planning-control.md
    问题、概念架构、完整运行流程、目标代码和持久化规格。

docs/modules/06-agent-core-control-protocols.md
    架构不变量、状态机、DAG、并发、Interrupt、Signal、副作用、Finalization、Failure 与 Budget。

docs/modules/06-agent-core-consistency-lifecycle-protocols.md
    TaskContract、GoalVersion、控制命令仲裁、Domain/Checkpoint、ResultValidity、Event、Artifact、Reconciler 与时间语义。
```

发生冲突时，以模块规范为准，并必须在同一轮文档变更中消除冲突。

## 5.2 三层运行结构

```text
固定 AgentRunGraph
    管理 Run 生命周期、TaskContract、GoalVersion、Plan 激活、控制命令、预算、安全、恢复、Publication 和 RunOutcome。

动态 Plan DAG
    管理 Objective、StepDefinition、DependencyRule、ActivationCondition、并行、Join 和完成条件。

固定 StepExecutionGraph
    管理 Action Proposal、Validation、Execution、Observation、Evaluation、Acceptance 和条件 Reflection。
```

简单任务使用 Deterministic Single-Step Plan，复杂任务使用 Dynamic DAG Plan。不存在绕过 Plan、Trace、Budget、AnswerPolicy、Final Gate、Publication 或 RunOutcome 的正式回答路径。

## 5.3 完整闭环

```text
RuntimeRequest
-> TaskContract / GoalVersion
-> ExecutionContextSnapshot
-> Plan Proposal / Validation / Activation
-> ReadySet / Admission / Budget Reservation
-> Dispatch Commit
-> StepExecutionGraph / ReAct
-> BranchResultRef / Reducer / Join
-> Acceptance / conditional Reflection
-> Retry / Repair / Fallback / Replan Barrier
-> FinalCandidate
-> Evidence / Citation / ResultValidity Gate
-> ArtifactVersion
-> Publication / DeliveryReceipt
-> RunOutcome
-> Reflexion Candidate
```

## 5.4 核心控制原则

```text
模型只产生 Proposal，不能直接提交领域终态
PlanVersion 激活后不可变，Replan 创建新版本
一个 Run 同时最多一个 Active PlanVersion
并行 Worker 只返回不可变 BranchResultRef
Dispatch 必须先持久化后 Send
Controller 与 Worker 使用 controller_epoch / execution_epoch Fencing
一个 Run 可以同时存在多个 Pending Interrupt
Signal 必须鉴权、版本化、幂等且绑定 Interrupt
副作用遵循 Prepare / Approve / Claim / Execute / Reconcile
UNKNOWN 副作用禁止盲目重试
FinalCandidate、ArtifactVersion、Publication 与 RunOutcome 分离
PostgreSQL 保存领域事实，LangGraph Checkpointer 保存图控制状态
```

## 5.5 状态与终局

可恢复等待统一使用 `WAITING_CONDITION`；`BLOCKED` 是终态；取消必须经过 `CANCELLING`，以停止新 Dispatch、排空不可中断副作用并完成 Reconcile。

```text
COMPLETED
PARTIAL
ABSTAINED
REFUSED
BLOCKED
FAILED
CANCELLED
EXPIRED
```

## 5.6 一致性、Owner 与恢复

```text
PostgreSQL Domain Store
    领域事实、状态转换、Epoch、Generation、ResultValidity 和审计。

LangGraph Checkpointer
    Graph Node、Channel、Pending Send、Interrupt Cursor 和 Reducer 控制状态。

Object Store
    大型 Observation、Evidence Snapshot、Artifact 和调试包。
```

Domain Generation 是权威提交序列。Checkpoint 只能引用已提交的 Domain Generation。Agent Core 通过 typed Port 使用其他模块，是编排者而不是所有事实的 Owner。

## 5.7 Requirement 与完成证据

Agent Core Requirement 使用 `ARCH-AGENT-001` 至 `ARCH-AGENT-080`，由三份模块文档连续定义且不得重复。

Target 转为 Current 必须有代码、Alembic Migration、Unit/Integration/E2E、故障注入、Trace、Eval 和可复现运行证据。仅完成文档时只能声明：

```text
design available
internally consistent
contract-complete
implementation-spec-complete
program-ready
```

不得仅凭设计声明 `implementation available`、`quality not yet proven` 已被证明、CI 通过或 production ready。

---
"""
    text = replace_once(
        text,
        r"# 5\. Agent Core / Planning & Control\n.*?(?=\n# 6\. Input / Document Ingestion)",
        section.rstrip(),
        flags=re.S,
    )
    text = text.replace(
        """-> Final Reflection 验证答案
-> Claim/Evidence/Citation Binding
-> Finalize 输出 GroundedAnswer
-> Reflexion 形成受治理经验""",
        """-> FinalCandidate 与 Final Gate 验证答案
-> Claim/Evidence/Citation/ResultValidity Binding
-> ArtifactVersion 与 Publication 输出正式结果
-> RunOutcome 提交终局
-> Reflexion 形成受治理经验""",
    )

    formal.write_text(text, encoding="utf-8", newline="\n")
    mirror.write_text(text, encoding="utf-8", newline="\n")


def sync_architecture_readme() -> None:
    content = """# 架构文档

`docs/architecture/` 与 `.agent/architecture/` 都只保留四个 canonical 架构入口：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 文件职责

- `architecture.md`：目标总架构文字事实源。
- `architecture-views.md`：4+1、Views & Beyond 与 Zuno Product Core 的 Mermaid 规范图源。
- `architecture.html`：读取 `architecture-views.md` 的 Architecture Atlas。
- `README.md`：目录边界、镜像和验证规则。

`.agent/architecture/` 是正式总架构的字节级镜像，不是独立事实源。

## 其他正式文档

```text
docs/modules/       十一个逻辑模块的实施级 Target 设计
docs/status/        Current、Gap、Blocked、Completed、Future Optional
docs/decisions/     正式 ADR
docs/governance/    Ownership 与文档治理
docs/evidence/      可复现证据
docs/history/       历史材料与研究附件
```

Agent Core Target 文档集：

```text
docs/modules/06-agent-core-planning-control.md
docs/modules/06-agent-core-control-protocols.md
docs/modules/06-agent-core-consistency-lifecycle-protocols.md
```

Current / Gap 事实源：`docs/status/production-readiness.md`。

禁止在 architecture 目录新增模块专题、状态报告、ADR、Program、实施计划、附件目录或其他文件。

## 更新与验证

```text
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_agent_core_target_protocols.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

修改总架构、图源或 HTML 后必须同步正式文件和 `.agent` 镜像。模块设计镜像放在 `.agent/modules/`。
"""
    for relative in [
        "docs/architecture/README.md",
        ".agent/architecture/README.md",
    ]:
        (ROOT / relative).write_text(content, encoding="utf-8", newline="\n")


def sync_renderer() -> None:
    path = ROOT / "tools/agent/render_architecture.py"
    text = path.read_text(encoding="utf-8")
    start = text.index("def validate_design(content: str) -> list[str]:")
    end = text.index("\n\ndef validate_source", start)
    function = '''def validate_design(content: str) -> list[str]:
    errors: list[str] = []
    required_sections = [
        "# Zuno Target Architecture Atlas",
        "# 1. 项目定位与架构目标",
        "# 2. 质量属性与架构约束",
        "# 3. 架构视图总览",
        "# 4. 全局事实源与数据所有权",
        "# 5. Agent Core / Planning & Control",
        "# 6. Input / Document Ingestion",
        "# 7. Knowledge / Agentic GraphRAG",
        "# 8. Memory & Context",
        "# 9. Model Gateway",
        "# 10. Capability / Skill",
        "# 11. Tool Runtime",
        "# 12. Product Surface",
        "# 13. Security & Governance",
        "# 14. Observability & Eval",
        "# 15. Infrastructure",
        "# 16. 关键端到端运行序列",
        "# 19. 测试与验证架构",
        "# 22. Target Completion Criteria",
    ]
    for section in required_sections:
        if section not in content:
            errors.append(f"architecture.md missing canonical target section: {section}")

    required_terms = [
        "十一逻辑模块",
        "六个物理运行域",
        "Single Controller Agent Runtime",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "TaskContract",
        "GoalVersion",
        "FinalCandidate",
        "Publication",
        "DeliveryReceipt",
        "PostgreSQL",
        "RabbitMQ",
        "Milvus",
        "Neo4j",
        "EvidenceLedger",
        "ContextPack",
        "MCP",
        "ToolCallIntent",
        "Recall@K",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
        "architecture-views.md",
        "docs/status/production-readiness.md",
    ]
    for term in required_terms:
        if term not in content:
            errors.append(f"architecture.md missing required target term: {term}")

    mermaid_count = content.count("```mermaid")
    if mermaid_count < 2:
        errors.append("architecture.md should retain supporting Mermaid diagrams")
    if mermaid_count > 8:
        errors.append("architecture.md must stay text-first; move detailed diagrams to architecture-views.md")
    if len(content) < 20000:
        errors.append("architecture.md is too short for the normative target design")
    return errors
'''
    path.write_text(text[:start] + function + text[end:], encoding="utf-8", newline="\n")


def sync_docs_entrypoint_verifier() -> None:
    path = ROOT / "tools/scripts/verify_docs_entrypoints.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '    "06-agent-core-planning-control.md",\n    "07-capability-skill.md",',
        '    "06-agent-core-planning-control.md",\n    "06-agent-core-control-protocols.md",\n    "06-agent-core-consistency-lifecycle-protocols.md",\n    "07-capability-skill.md",',
    )
    text = text.replace(
        '    "docs/modules/06-agent-core-planning-control.md",\n    "docs/status/production-readiness.md",',
        '    "docs/modules/06-agent-core-planning-control.md",\n    "docs/modules/06-agent-core-control-protocols.md",\n    "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",\n    "docs/status/production-readiness.md",',
    )
    text = text.replace(
        '    ".agent/modules/06-agent-core-planning-control.md",\n    "docs/history/architecture-surface-cleanup',
        '    ".agent/modules/06-agent-core-planning-control.md",\n    ".agent/modules/06-agent-core-control-protocols.md",\n    ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",\n    "docs/history/architecture-surface-cleanup',
    )
    text = replace_once(
        text,
        r'    architecture = _read\("docs/architecture/architecture\.md"\)\n    for phrase in \[.*?\n    \]:\n        if phrase not in architecture:\n            errors\.append\(f"docs/architecture/architecture\.md missing phrase: \{phrase\}"\)',
        '''    architecture = _read("docs/architecture/architecture.md")
    for phrase in [
        "Zuno Target Architecture Atlas",
        "项目定位与架构目标",
        "十一逻辑模块",
        "六个物理运行域",
        "Single Controller Agent Runtime",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "TaskContract",
        "FinalCandidate",
        "Publication",
        "EvidenceLedger",
        "docs/status/production-readiness.md",
    ]:
        if phrase not in architecture:
            errors.append(f"docs/architecture/architecture.md missing phrase: {phrase}")''',
        flags=re.S,
    )
    text = replace_once(
        text,
        r'    agent_core = _read\("docs/modules/06-agent-core-planning-control\.md"\)\n    for phrase in \[.*?\n    \]:\n        if phrase not in agent_core:\n            errors\.append\(f"Agent Core module doc missing phrase: \{phrase\}"\)',
        '''    agent_core = _read("docs/modules/06-agent-core-planning-control.md")
    for phrase in [
        "Single Controller Agent Runtime",
        "Plan DAG",
        "TaskContract",
        "pending_interrupt_refs",
        "prepare_publication",
        "PostgreSQL",
    ]:
        if phrase not in agent_core:
            errors.append(f"Agent Core module doc missing phrase: {phrase}")''',
        flags=re.S,
    )
    old_pair = '''        (
            "docs/modules/06-agent-core-planning-control.md",
            ".agent/modules/06-agent-core-planning-control.md",
        ),
    ]'''
    new_pairs = '''        (
            "docs/modules/06-agent-core-planning-control.md",
            ".agent/modules/06-agent-core-planning-control.md",
        ),
        (
            "docs/modules/06-agent-core-control-protocols.md",
            ".agent/modules/06-agent-core-control-protocols.md",
        ),
        (
            "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
            ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
        ),
    ]'''
    if old_pair not in text:
        raise RuntimeError("Agent Core mirror pair block not found")
    path.write_text(text.replace(old_pair, new_pairs), encoding="utf-8", newline="\n")


def sync_entrypoint_tests() -> None:
    path = ROOT / "tests/repo/test_docs_entrypoints.py"
    text = path.read_text(encoding="utf-8")
    old = '''    assert (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(
        encoding="utf-8"
    ) == (REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md").read_text(
        encoding="utf-8"
    )'''
    new = '''    for file_name in [
        "06-agent-core-planning-control.md",
        "06-agent-core-control-protocols.md",
        "06-agent-core-consistency-lifecycle-protocols.md",
    ]:
        assert (REPO_ROOT / "docs/modules" / file_name).read_bytes() == (
            REPO_ROOT / ".agent/modules" / file_name
        ).read_bytes()'''
    if old not in text:
        raise RuntimeError("module mirror assertion block not found")
    text = text.replace(old, new)
    text = text.replace(
        '        "06-agent-core-planning-control.md",\n        "07-capability-skill.md",',
        '        "06-agent-core-planning-control.md",\n        "06-agent-core-control-protocols.md",\n        "06-agent-core-consistency-lifecycle-protocols.md",\n        "07-capability-skill.md",',
    )
    text = replace_once(
        text,
        r'    for phrase in \[\n        "Zuno Target Architecture Atlas",.*?\n    \]:\n        assert phrase in design',
        '''    for phrase in [
        "Zuno Target Architecture Atlas",
        "项目定位与架构目标",
        "十一逻辑模块",
        "六个物理运行域",
        "Single Controller Agent Runtime",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "TaskContract",
        "FinalCandidate",
        "Publication",
        "EvidenceLedger",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
    ]:
        assert phrase in design''',
        flags=re.S,
    )
    text = text.replace(
        '''            "Agent Core / Planning & Control",
            "Plan DAG",
            "默认最大化安全并行",
            "PostgreSQL",
            "Alembic Migration",''',
        '''            "Agent Core / Planning & Control",
            "Single Controller Agent Runtime",
            "Plan DAG",
            "TaskContract",
            "pending_interrupt_refs",
            "prepare_publication",
            "PostgreSQL",''',
    )
    text = text.replace(
        '''    for phrase in [
        "Agent 架构工作区",
        ".agent/modules/06-agent-core-planning-control.md",
        "docs/status/production-readiness.md",
    ]:
        assert phrase in agent_architecture_index''',
        '''    for phrase in [
        "架构文档",
        "docs/modules/06-agent-core-planning-control.md",
        "docs/modules/06-agent-core-control-protocols.md",
        "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
        "docs/status/production-readiness.md",
    ]:
        assert phrase in agent_architecture_index''',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def sync_doc_boundary_verifier() -> None:
    path = ROOT / ".agent/scripts/verify_doc_boundaries.py"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        r'    required_phrases = \[.*?\n    \]\n    for phrase in required_phrases:',
        '''    required_phrases = [
        "Zuno Target Architecture Atlas",
        "项目定位与架构目标",
        "十一逻辑模块",
        "六个物理运行域",
        "Single Controller Agent Runtime",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "TaskContract",
        "FinalCandidate",
        "Publication",
        "EvidenceLedger",
        "docs/status/production-readiness.md",
        "docs/architecture/architecture-views.md",
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.md",
    ]
    for phrase in required_phrases:''',
        flags=re.S,
    )
    text = text.replace(
        '        "Future Optional",\n        "不是微服务",',
        '        "Future Optional",\n        "近期不追求",\n        "不要求一开始拆成大量微服务",\n        "不是微服务",',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def archive_architecture_assets() -> None:
    assets = ROOT / "docs/architecture/assets"
    historical = ROOT / "docs/history/research/chatgpt-research-mode-artifacts"
    second = assets / "zuno-agentic-rag-graphrag-ideal-architecture.pdf"
    if second.exists():
        historical.mkdir(parents=True, exist_ok=True)
        destination = historical / second.name
        if not destination.exists():
            shutil.copy2(second, destination)
    if assets.exists():
        shutil.rmtree(assets)


def main() -> None:
    sync_architecture()
    sync_architecture_readme()
    sync_renderer()
    sync_docs_entrypoint_verifier()
    sync_entrypoint_tests()
    sync_doc_boundary_verifier()
    archive_architecture_assets()
    print("Agent Core target documentation surfaces synchronized.")


if __name__ == "__main__":
    main()
