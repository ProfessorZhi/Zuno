# 当前程序

Program: `zuno-eight-deliverables-full-realization-v1`
state: active
current_phase: `PHASE07_hooks-evidence-trace-artifact-system.md`
execution_mode: 主线程目标模式 + 默认开启线程内多 agent 协作；这是 Codex 执行协作，不是 Zuno runtime 架构；不是多线程模式

## 目标

本 program 要把 Zuno 最终成品的八个内部交付物完整落到文档、目标架构、代码结构、runtime contracts、验证和收口证据中。它不是最小实现，也不是只改 architecture markdown / HTML；每个 phase 都必须形成可验证的 PR 边界。

八个交付物：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 模板与执行计划系统。
4. 正式架构文档系统。
5. 架构 HTML 展示系统。
6. 完善的 Zuno 目标架构。
7. 清晰干净的代码和目录。
8. 一致性与验证系统。

对外表达仍是五个成熟系统：Agent 工作流文档系统、元工作流自我维护系统、正式架构文档系统、架构 HTML 展示系统、干净清晰且可验证的代码结构。

## 当前事实

Program 3 / `zuno-repo-layout-cleanup-v1` 已完成 `src/backend/zuno` 顶层目录和 root alias surface closure。`src/backend/zuno` 顶层目录仍只允许：

- `api/`
- `agent/`
- `memory/`
- `capability/`
- `knowledge/`
- `platform/`
- `__init__.py`
- `main.py`

Program 3 固定的六层顶层表达是 `api / agent / memory / capability / knowledge / platform`。

Program 4 / `zuno-six-layer-internalization-v1` 已完成并归档；六层内部已有第一批无副作用薄入口、README、focused tests 和 verifier guard。它不表示 GeneralAgent 主循环、DB schema、API 行为、eval baseline、production memory、dynamic capability orchestration、retrieval fusion 或 model gateway runtime 已完成。

`docs/architecture.md` 和 `docs/architecture.html` 已经成为当前架构总览和唯一 HTML 展示入口；旧 architecture HTML surface 不再作为前台目标。

## Active Phase 列表

1. `PHASE01_program-boot-baseline.md`：打开 program、同步状态面、更新 verifier/tests。
2. `PHASE02_workflow-self-maintenance-system.md`：落实 Agent 工作流、元工作流、模板与 program 生命周期。
3. `PHASE03_architecture-docs-html-system.md`：正式架构文档和 HTML 展示系统收口。
4. `PHASE04_query-router-mode-policy.md`：completed。普通 / 增强 / 自动模式和 `basic / local / global / drift` 方法策略已形成 runtime / trace / eval contract。
5. `PHASE05_context-builder-memory-system.md`：completed。Context Pack、五类记忆、source ids、compression / extraction policy 和 review contract 已形成 foundation slice。
6. `PHASE06_capability-toolcard-mcp-system.md`：completed。ToolCard contract、Native BM25 ToolCard retrieval foundation、MCP/local tool policy trace 已形成 focused tests。
7. `PHASE07_hooks-evidence-trace-artifact-system.md`：active。Hooks、Evidence Check、Trace、Artifact 证据链。
8. `PHASE08_graphrag-knowledge-runtime-system.md`：GraphRAG、RAG fusion、knowledge extraction 和 drift 检索。
9. `PHASE09_runtime-upgrade-integration.md`：GeneralAgent 主路径集成和六层代码目录落实。
10. `PHASE10_validation-release-closure.md`：全量验证、文档同步、归档、提交和推送收口。

## 执行规则

- 每个 phase 可以对应一个或多个 PR，但必须有清晰验收证据。
- 主线程默认开启同一目标模式线程内的多 agent 模式，用多 agent 做并行审计或独立实现切片；主线程保留最终 diff 审查和验证责任。
- 当前不是多线程模式，不生成 `.agent/programs/thread-prompts/` 子线程提示词，除非用户后续明确切换到多线程。
- 不把 Java、微服务、事件驱动 worker 或 product/runtime 默认多 Agent 模式作为近期实现。
- Current 只写代码、测试和可复现结果已经证明的事实；Target 写本 program 目标；Future 写暂不实施方向；History 只放归档事实。

## 参考输入

queued drafts 现在是本 program 的参考输入，不是 active program：

- `.agent/architecture/future/programs/zuno-query-router-and-mode-policy-v1/`
- `.agent/architecture/future/programs/zuno-context-builder-and-memory-v1/`
- `.agent/architecture/future/programs/zuno-hooks-evidence-trace-v1/`
- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
