# 当前程序

当前 active program：`zuno-architecture-detail-and-execution-plan-v1`

state: active
current_phase: PHASE04_execution-roadmap-from-architecture

## 目标

本 program 先细化 Zuno 的目标架构文档、十类 Mermaid 架构图和生成 HTML，再从细化后的架构图反推出下一阶段执行计划。细化重点包括 Agent Core Runtime、Memory Layer、Tool Control Plane、Document Ingestion、企业私有知识库主叙事、安全 / 沙箱治理、Trace / Eval 和 LangSmith 适配。

它不是 runtime feature implementation，不新增 API / DB schema / frontend 行为，不把 Target 写成 Current。

本 program 还负责新增并登记总架构文档治理：`docs/architecture/architecture.md` 作为正式文字总架构文档，`.agent/architecture/architecture.md` 作为 Agent 侧总架构维护文档；图形总览继续由 `docs/architecture/architecture.md` 生成到 `docs/architecture/architecture.html`。

## 范围

允许修改：

- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.html`
- `.agent/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `AGENTS.md`
- `README.md`
- `.agent/programs/*`
- `.agent/references/current-program.md`
- `.agent/references/docs-map.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `.agent/references/architecture-update-policy.md`
- `.agent/references/workflow.md`
- `.agent/references/diagram-inventory.md`
- `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/programs/README.md`
- `tools/agent/render_architecture.py`
- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify_doc_boundaries.py`
- `tools/scripts/verify_docs_entrypoints.py`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_docs_entrypoints.py`

禁止修改：

- Runtime 代码、API 行为、DB schema、frontend product flow。
- `src/backend/zuno/**`，除非后续单独打开实现 program。
- 历史归档内容，除非本 program 收口时归档自身。

## 当前阶段

- `PHASE01_architecture-state-and-program-boot.md`：completed。
- `PHASE02_target-architecture-detailing.md`：completed。
- `PHASE03_mermaid-html-detail-refresh.md`：completed。
- `PHASE04_execution-roadmap-from-architecture.md`：active。
- `PHASE05_validation-and-closure.md`：pending。

## 下一阶段落点

附件评估确认：继续堆总览图的边际收益已经不高，真正增量在把目标架构转成可执行产品 program。PHASE04 当前要把下一轮实现拆成四条可执行主线：

1. `Document Ingestion / Parse Gateway`：多格式解析、Canonical Document IR、chunk/provenance、BM25/vector/graph indexing。
2. `Runtime + Memory + Tool Plane`：Context Pack、summary compression、structured extraction、ToolCard manifest、executor registry、approval flow。
3. `Eval / Observability`：LangSmith trace 映射、dataset、RAGAS / DeepEval 指标、citation coverage 和 CI regression gate。
4. `Security + Enterprise Scenarios`：PII / 商业秘密脱敏、prompt injection 防护、ACL、输出 DLP、Policy / Workspace / Execution / Network-Credential Sandbox、高风险工具人工审批，以及企业知识库 / HR 简历库场景。

## 当前边界

最近完成并归档的 program 仍是 `zuno-eight-deliverables-full-realization-v1`，它完整落实八个交付物：

- 历史目录：`docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
- 范围：PHASE01-PHASE10。
- 状态：completed / archived。
- 执行方式：主线程目标模式 + 线程内多 agent 协作；这是 Codex 执行协作，不是 Zuno runtime 架构；不是多线程模式。

本 program 继承上一个 program 的 Current / Target 纪律：PHASE04-PHASE09 foundation slices 是当前已证明事实；完整产品级 LangGraph runtime、生产级 Memory DB、成熟 memory read/write/promotion/decay、动态工具编排、完整 parser gateway、LangSmith 产品化、安全闸门和前端 trace 面板仍是 Target。
