# 当前程序

state: active
active_program: zuno-real-unified-runtime-cutover-v1
current_phase: PHASE01_real-runtime-baseline
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

`PHASE01_real-runtime-baseline` 只允许：

- 激活 program。
- 冻结当前 runtime / product / benchmark 事实。
- 建立 `verify_real_runtime_cutover.py` guardrail。
- 修正 workflow / verifier / repo tests，使 active program 状态可机器检查。
- 调查并处理 `python tools/scripts/verify_repo_structure.py` 的现有失败。

PHASE01 不修改生产 runtime。

## 当前已冻结的主要缺口

- `UnifiedAgentRuntimeService` 仍通过 `_run_from()` 手写 `while current_node != RuntimeNode.END` 控制主运行轨迹。
- Completion unified path 仍输出固定文本 `Unified runtime completed.`。
- `ModelStepExecutor` 仍是 deterministic completed observation，没有调用 Model Gateway。
- `ReActStepExecutor` 仍是 deterministic completed observation，没有真实执行单个 PlanStep 的 ReAct。
- `KnowledgeStepExecutor` 在 `knowledge_runtime` 缺失时仍会生成 synthetic evidence / citation。
- `src/backend/zuno/api/v1/completion.py` 默认仍走 `GeneralAgent`，unified runtime 需要 `product_mode == "unified_runtime"` 或 `ZUNO_COMPLETION_UNIFIED_RUNTIME=1`。
- fixed EnterpriseRAG paired benchmark 仍是 measurement blocked / quality not yet proven。

这些缺口是 PHASE02-PHASE07 的修复目标。PHASE01 不得把它们写成 Current fixed。

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
