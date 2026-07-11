# Current Program Reference

state: active
active_program: zuno-real-unified-runtime-cutover-v1
current_phase: PHASE05_knowledge-tool-memory-integration
latest_completed_program: zuno-unified-agent-runtime-closure-v1

`.agent/programs/` 当前处于 active program 状态。最近完成并归档的 program 是 `zuno-unified-agent-runtime-closure-v1`。

归档入口：

- `docs/history/programs/zuno-unified-agent-runtime-closure-v1/`

## 当前 active program

- `.agent/programs/current.md`
- `.agent/programs/PHASE01_real-runtime-baseline.md`
- `.agent/programs/PHASE02_langgraph-execution-cutover.md`
- `.agent/programs/PHASE03_runtime-dependency-factory.md`
- `.agent/programs/PHASE04_real-agent-execution.md`
- `.agent/programs/PHASE05_knowledge-tool-memory-integration.md`

当前 program 是 `zuno-real-unified-runtime-cutover-v1`，目标是把 Completion / Workspace 产品主路径切到 `UnifiedAgentRuntimeService -> compiled LangGraph -> RuntimeDependencyFactory -> Model Gateway / Memory / Corrective Agentic GraphRAG / Tool Control Plane` 的真实统一 runtime。

当前 Phase 是 PHASE05。PHASE01 已完成 facts / guardrail 激活，PHASE02 已完成 compiled LangGraph cutover，PHASE03 已完成 `RuntimeDependencyFactory` 和 typed runtime protocols，PHASE04 已完成 ModelStep、ReActStep 和 Grounded Synthesis 真实执行数据面；PHASE05 目标是收口 Knowledge / Tool / Memory 真实集成。不得把 PHASE05-PHASE07 目标写成 Current、Completed 或 measured。

## 最近完成事实

`zuno-unified-agent-runtime-closure-v1` 已完成 PHASE01-PHASE13 的本地 unified runtime implementation baseline：

目标链路名称：Single Controller Agent Runtime。

- runtime contracts and state。
- Model Gateway closure。
- SQLite durable store、trace 和 idempotency。
- unified LangGraph runtime service。
- Strategy / Plan-and-Execute / ReAct step execution。
- Tool Control Plane approval/resume/idempotency。
- corrective Agentic GraphRAG / EvidenceLedger。
- Reflection / Replan / Grounded Synthesis。
- four-layer Memory / Reflexion reuse。
- Completion / Workspace API 和 SSE trace cutover。
- real text PDF SourceSpan vertical slice。
- EnterpriseRAG paired benchmark profile completeness / blocked-not-measured semantics。

## 当前质量边界

```text
implementation available
measurement blocked
quality not yet proven
```

PHASE13 sample-8 已运行但 blocked，原因是本地 embedding profile runner 未配置。sample-80 仍因仓库没有 tracked fixed 80-case set 而 blocked。

不得把本轮 program closure 写成 fixed EnterpriseRAG measured pass，也不得把 Agentic GraphRAG 稳定优于 baseline 写成已证明。

## 最近完成归档

1. `docs/history/programs/zuno-unified-agent-runtime-closure-v1/`
   - 状态：completed / archived。
   - 完成：本地 unified runtime implementation baseline。
   - 边界：fixed EnterpriseRAG measured pass 仍 blocked。
2. `docs/history/programs/zuno-lean-complete-product-architecture-v1/`
   - 状态：completed / archived。
   - 完成：目标架构事实源、HTML 展示、文档入口、renderer、verifier 和 tests 的收缩与同步。
   - 边界：没有修改核心 runtime，没有声称运行质量已经提升。
3. `docs/history/programs/zuno-evidence-span-agentic-graphrag-hardening-v1/`
   - 状态：completed / archived。
   - 完成：evidence-span hardening baseline。
   - 边界：release gate 输出面已完成；fixed EnterpriseRAG measured pass 仍 blocked。
4. `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`
   - 状态：completed / archived。
   - 完成：Program 3 Mega launchable enterprise Agentic GraphRAG product baseline。
   - 说明：Program 3 Mega 吸收并替代过的 suite / queued 输入仍是历史事实：`zuno-enterprise-agentic-graphrag-production-suite-v1`、`zuno-enterprise-ingestion-async-infrastructure-v1`、`zuno-runtime-subsystems-parallel-v1`、`zuno-agent-planning-integration-v1` 和 `zuno-enterprise-knowledge-eval-benchmark-v1`。
   - 历史 Program 3 final alias surface closure 已完成，旧 public import path 只通过 `legacy_aliases.py` 注册兼容。
5. `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
   - 状态：completed / archived。
   - 完成：Product V1 local durable ingestion baseline。
6. `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
   - 状态：completed / archived。
7. `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`
   - 状态：completed / archived。
   - 说明：一次性交付型成熟化 program，完成“成熟目标架构和四大总交付物完成”。
8. `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`
   - 状态：completed / archived。
   - 边界：runtime-first / vertical-slice-first closure evidence 保留在归档中。
   - 规则：只写 contract、schema 或 README 不能关闭 runtime phase。
9. `docs/history/programs/zuno-master-architecture-implementation-v1/`
   - 状态：completed / archived。
   - 边界：PHASE01-PHASE12。
10. `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
   - 状态：completed / archived。
   - 边界：PHASE01-PHASE10。
11. `docs/history/programs/zuno-six-layer-internalization-v1/`
   - 状态：completed / archived。
12. `docs/history/programs/zuno-repo-layout-cleanup-v1/`
   - 状态：completed / archived。
13. `zuno-runtime-architecture-upgrade-v1` 和 `zuno-architecture-visuals-v1`
   - 状态：future reference draft，不是 active program。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- no-active 状态下不得继续执行已归档 PHASE 文件。
- `.agent/programs/` 是当前 flat program directory；active program 打开时 PHASE 文件必须平铺在这里，关闭后必须归档离开前台。
- 新 program 必须从 PHASE01 开始；不得把已归档 phase 文件复制回前台当作 active truth source。
- runtime-first / vertical-slice-first closure guard 保持有效。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。
- completed program 必须归档到 `docs/history/programs/`。
