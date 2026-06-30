# Agent 侧总架构文档

## 用途

这是 `.agent/architecture/` 根部的总架构维护文档，用于帮助 Agent 在执行任务时快速理解 Zuno 的整体架构、文档职责和下一步实施落点。

正式人类总架构文档是 [docs/architecture/overall-architecture.md](../../docs/architecture/overall-architecture.md)。本文必须与其保持一致，但不替代它；如果两者冲突，以 `docs/architecture/overall-architecture.md` 为准，并同步修正本文。

## 一句话架构

```text
Zuno target
  = Local-first Enterprise Private Knowledge Agent Workspace
  = 本地优先的企业私有知识库与多功能 Agent 助手
```

Zuno 近期不是普通 RAG 问答 demo，也不是默认多 Agent runtime。它的目标是把企业内部文档、合同、制度、项目资料、技术文档、HR / 简历资料和个人项目证据变成可检索、可引用、可追踪、可评测、可治理的 Agent Workspace。

## Current / Target 快速边界

Current：

- monorepo。
- Vue Web + Electron Desktop。
- FastAPI backend。
- `src/backend/zuno` 六层边界。
- `GeneralAgent` single loop。
- Knowledge / GraphRAG query path。
- Query Router、Context / Memory、ToolCard、GraphRAG、Evidence / Citation / Trace / Eval foundation。

Target：

- Single Controller Agent Runtime。
- Document Ingestion / Parse Gateway。
- Context / Memory write-manage-read。
- Tool Control Plane。
- Agentic RAG + GraphRAG。
- Security / Approval / Sandbox。
- LangSmith-compatible Trace / Eval。
- Workspace / Artifact / Event Flow。

不能写成 Current：

- 完整产品级 LangGraph runtime。
- 生产级 Memory DB 和成熟 memory retrieval / consolidation。
- 完整动态工具编排。
- 统一多格式 Parse Gateway。
- 成熟 LangSmith 产品化评测。
- 完整安全沙箱、credential broker、DLP 和高风险工具审批闭环。
- 默认产品级多 Agent runtime。

## 根部总架构维护面

`.agent/architecture/` 根部现在有两个总入口：

- `README.md`：解释 `.agent/architecture/` 的目录职责。
- `overall-architecture.md`：解释 Agent 执行时要遵守的总架构判断和同步规则。

详细目标设计仍在：

- `near-term/01-target-runtime-architecture.md`
- `near-term/02-context-memory-architecture.md`
- `near-term/03-capability-tool-retrieval-architecture.md`
- `near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `near-term/05-repository-boundaries-and-acceptance-gates.md`

未来方向仍在：

- `future/future-horizon.md`
- `future/programs/`

执行计划仍在：

- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE*.md`

## 与 HTML 图页的关系

Zuno 有两种总架构表达：

1. 文字总架构文档：`docs/architecture/overall-architecture.md` 和本文。
2. 图形总览：`docs/architecture/architecture.md` 作为 Mermaid 源，`docs/architecture/architecture.html` 作为生成 HTML 展示页。

不要在 `.agent/architecture/` 复制新的 HTML。HTML 只从 `docs/architecture/architecture.md` 生成；`.agent/architecture/` 只保存 Agent 侧目标设计和维护规则。

## 目标分层

维护架构时按这十个平面思考：

| 平面 | 判断重点 |
| --- | --- |
| Presentation / Workspace | 用户如何进入会话、上传文件、查看产物和 trace。 |
| API / Session | 请求、session、task、event stream、upload / download 如何暴露。 |
| Agent Core Runtime | planning、ReAct、reflection、replan 和 post-turn commit 如何串起来。 |
| Context / Memory | Raw Event Log、summary、structured memory 和 Context Pack 如何 write-manage-read。 |
| Capability / Tool | ToolCard、selector、policy、approval、executor、sandbox 和 result normalizer 如何协作。 |
| Knowledge / Retrieval | `basic / local / global / drift`、GraphRAG、fusion、evidence、citation 如何治理。 |
| Document Ingestion | PDF、Office、图片、代码、文本等多格式如何解析、切块、保留 provenance 和 ACL。 |
| Security / Governance | 输入、检索、工具、输出四道闸如何防泄密、防越权、防 prompt injection。 |
| Trace / Eval | LangSmith-compatible trace、dataset、offline / online eval 和 release gate 如何闭环。 |
| Platform | storage、model gateway、worker、artifact、observability 和 provider 如何支撑。 |

## 维护规则

当用户要求“完善总架构”“细化架构图”“合并架构文档”“改目标架构”“改实施计划”时，按下面顺序处理：

1. 先读 `docs/architecture/overall-architecture.md`。
2. 再读 `docs/architecture/current-architecture.md` 和 `docs/architecture/target-architecture.md`，确认 Current / Target 边界。
3. 如果涉及图，读 `docs/architecture/architecture.md` 和 `.agent/references/diagram-inventory.md`。
4. 如果涉及工作流，读 `.agent/references/architecture-docs-map.md`、`.agent/references/documentation-governance.md` 和 `.agent/references/architecture-update-policy.md`。
5. 如果要落执行计划，只更新 `.agent/programs/`，不要把 phase 细节塞回 `.agent/architecture/`。
6. 改完必须同步 verifier / tests，至少覆盖 `verify_docs_entrypoints.py` 和 `tests/repo/test_docs_entrypoints.py`。

## 一致性锚点

以下短语必须在两份总架构文档或入口中保持一致：

- `总架构文档`
- `本地优先的企业私有知识库与多功能 Agent 助手`
- `文字总架构文档`
- `架构 HTML`
- `docs/architecture/overall-architecture.md`
- `.agent/architecture/overall-architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.html`
- `Document Ingestion / Parse Gateway`
- `Tool Control Plane`
- `LangSmith-compatible Trace / Eval`

这些锚点由 docs verifier 和 repo tests 保护。
