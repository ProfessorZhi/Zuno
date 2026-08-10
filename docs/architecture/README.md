# Zuno 架构文档

`docs/architecture/` 与 `.agent/architecture/` 只能保留：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 正式设计事实

Zuno 正式架构设计事实共十三份：

```text
11 × docs/modules/<NN>-<module>.md
 1 × docs/architecture/architecture.md
 1 × docs/architecture/architecture.html
```

职责：

- `architecture.md`：十一模块的跨模块集成架构、全局不变量和端到端流程。
- `architecture.html`：总体架构的 Mermaid 可视化入口。
- `architecture-views.md`：HTML 的 Mermaid 渲染源，不是第二份文字总架构。
- `README.md`：目录、镜像和维护规则，不是架构正文。
- `docs/modules/`：每个领域 Owner 的唯一详细 Target 架构；领域细节冲突时以对应模块文档为准。
- `.agent/modules/06-agent-core-planning-control.md`：Agent Core 正式模块文档的字节级镜像示例；十一模块均遵循同一镜像规则。

`.agent/architecture/` 是字节级镜像，不是独立事实源。

## Architecture v1 与 v2 路由

已归档的 `zuno-canonical-architecture-runtime-realization-v1` Program 与 PHASE01–PHASE22 使用过以下冻结的 Architecture v1 基线；该基线现在作为 History 证据保留：

```text
c9d099d64a1af28102231751ce55df8217173e89
```

新的 Evidence-Driven Agentic GraphRAG 目标由以下正式 ADR 独立定义：

```text
docs/decisions/0006-evidence-driven-agentic-graphrag.md
```

这样做是为了避免用新 Target 静默改变已归档 Program 的 Contract 和验收条件。ADR 0006 是 `accepted-target`，优先于旧模块中的冲突描述，但不授权本次收口立即实现，也不证明任何 v2 Runtime 已成为 Current。

PHASE22 已完成 Engineering Closure 并归档；当前 `.agent/programs/` 为 `no-active`。下一阶段不是 PHASE23，也不是新的 Runtime Program，而是独立的设计与整理工作：

```text
Latest Current Review
→ Repository Consolidation
→ 11 Module Architecture Deep Review
→ ADR 0006 Canonical Coordination
→ Cross-module Contract Review
→ Architecture / Mermaid / HTML Sync
→ Architecture Review
→ 设计确认后才决定是否建立新的 Implementation Program
```

历史路由说明见：

```text
docs/history/architecture-v1-baseline.md
```

## 从云端同步到本地

本仓库架构文档以 GitHub `main` 为共享基线。已有 checkout 时先快进同步：

```powershell
git status --short --branch
git pull --ff-only origin main
```

全新机器先 clone：

```powershell
git clone https://github.com/ProfessorZhi/Zuno.git
Set-Location -LiteralPath .\Zuno
```

同步后先读四处：

```text
docs/modules/README.md
docs/architecture/architecture.md
docs/decisions/0006-evidence-driven-agentic-graphrag.md
.agent/programs/current.md
```

`docs/modules/` 说明十一模块既有完整 Target；`architecture.md` 说明跨模块集成；ADR 0006 说明新的 v2 Target overlay；`.agent/programs/current.md` 说明当前是否存在 active program 和 Current / Gap 边界。clone 或 pull 只证明文件同步，不证明 Target 已成为 Current。

## 规范优先级

```text
全局不可变原则、已接受 ADR、共享 Contract Registry
→ 十一份 Canonical Owner 模块文档
→ architecture.md 跨模块集成
→ architecture-views.md 说明性 Mermaid
→ architecture.html 渲染
```

模块文档更新后，总架构和图必须向模块对齐；禁止根据旧 Mermaid 反向修改新模块 Contract。已接受 ADR 与模块文本冲突时，先按 ADR 执行决策治理，再通过后续文档协调 PR 消除冲突。

## 状态、决策与治理入口

```text
docs/status/production-readiness.md
docs/evidence/
docs/decisions/
docs/governance/
最新 main 的代码、Migration、测试、Trace、Eval 与运行证据
```

- `docs/status/` 和 `docs/evidence/` 负责 Current、Gap、Measurement 和 Production Readiness。
- `docs/decisions/` 保存正式 ADR。
- `docs/governance/` 保存跨模块 Contract Registry、Ownership 和文档治理。
- Target 文档存在不能自动提升状态。

## 更新与验证

模块含义变化时先更新对应模块唯一文档，再同步总架构的跨模块关系。图形关系变化时同步 `architecture-views.md` 和 HTML。

```text
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_architecture_document_set.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

禁止在 architecture 目录放置模块专题、状态报告、ADR、Program、Migration 计划或附件目录。
