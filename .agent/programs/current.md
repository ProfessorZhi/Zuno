# 当前程序

state: active
active_program: zuno-real-unified-runtime-cutover-v1
current_phase: PHASE07_benchmark-and-closure
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

`PHASE07_benchmark-and-closure` 正在运行或诚实阻塞 benchmark，并完成 program closure / archive。

PHASE01 已完成 program 激活、事实冻结和 guardrail。PHASE02 已完成 compiled LangGraph cutover。PHASE03 已完成 `RuntimeDependencyFactory`、typed runtime protocols、Completion / Workspace 工厂装配入口，以及核心依赖缺失时 blocked observation 的边界。PHASE04 已完成 ModelStep 经 Model Gateway 调用、ReAct 单步 runner 和 Grounded Synthesis `final_answer` / claims / citation bindings / unsupported claims 输出。PHASE05 已完成 Knowledge / Tool / Memory 集成，以及 PDF -> index -> corrective retrieval -> EvidenceLedger -> synthesis -> page citation unified runtime vertical slice。PHASE06 已完成 Completion 默认 unified runtime、legacy rollback flag 和 SSE product event surface。

PHASE07 不得把 benchmark blocked / partial / prepared 写成 measured。

## 当前已冻结的主要缺口

- fixed EnterpriseRAG paired benchmark 仍是 measurement blocked / quality not yet proven。

这些缺口是 PHASE07 的修复目标。不得把它们写成 Current fixed。

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
