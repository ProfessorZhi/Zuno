# 当前程序

state: active
active_program: zuno-real-unified-runtime-cutover-v1
current_phase: PHASE03_runtime-dependency-factory
latest_completed_program: zuno-unified-agent-runtime-closure-v1
baseline_commit: d90dc0013c1721a56828a6dc6f889e209454b346

## 当前目标

本轮 program 的目标不是继续扩大架构层，也不是只优先 benchmark。当前目标是把产品主路径从并存的 `GeneralAgent` legacy path、`UnifiedAgentRuntimeService` 手写 runtime loop 和 deterministic executor baseline，切到：

```text
Completion / Workspace
-> UnifiedAgentRuntimeService
-> compiled LangGraph
-> RuntimeDependencyFactory
   -> Model Gateway
   -> Memory Engine
   -> Corrective Agentic GraphRAG
   -> Tool Control Plane
-> Plan-and-Execute
-> real ReAct step
-> Observation
-> Reflection
-> true Replan
-> Reflexion
-> GroundedAnswer
-> SSE / Artifact
```

## 当前 Phase

`PHASE03_runtime-dependency-factory` 正在建立 `RuntimeDependencyFactory` 和 typed runtime protocols，目标是让统一 runtime 只通过显式依赖工厂装配 Model Gateway、Memory、Knowledge、Tool、Planner、Reflection 和 Synthesis 能力。

PHASE01 已完成 program 激活、事实冻结和 guardrail。PHASE02 已完成 compiled LangGraph cutover：`UnifiedAgentRuntimeService` 现在通过 compiled graph `invoke` 执行，产品主路径不再依赖 `_run_from()` 手写主循环，resume 不再强制改成 PASS。

PHASE03 不修改 Completion 默认产品入口；默认产品切换属于 PHASE06。

## 当前已冻结的主要缺口

- Completion unified path 仍输出固定文本 `Unified runtime completed.`。
- `ModelStepExecutor` 仍是 deterministic completed observation，没有调用 Model Gateway。
- `ReActStepExecutor` 仍是 deterministic completed observation，没有真实执行单个 PlanStep 的 ReAct。
- `KnowledgeStepExecutor` 在 `knowledge_runtime` 缺失时仍会生成 synthetic evidence / citation。
- `src/backend/zuno/api/v1/completion.py` 默认仍走 `GeneralAgent`，unified runtime 需要 `product_mode == "unified_runtime"` 或 `ZUNO_COMPLETION_UNIFIED_RUNTIME=1`。
- fixed EnterpriseRAG paired benchmark 仍是 measurement blocked / quality not yet proven。

这些缺口是 PHASE03-PHASE07 的修复目标。不得把它们写成 Current fixed。

## 前台 Phase 文件

- `PHASE01_real-runtime-baseline.md`
- `PHASE02_langgraph-execution-cutover.md`
- `PHASE03_runtime-dependency-factory.md`
- `PHASE04_real-agent-execution.md`
- `PHASE05_knowledge-tool-memory-integration.md`
- `PHASE06_product-cutover.md`
- `PHASE07_benchmark-and-closure.md`

## 质量边界

```text
implementation in progress
measurement blocked
quality not yet proven
```

不得把 prepared、blocked、runtime observed、partial profile 或 deterministic fixture 写成 measured。
