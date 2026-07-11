# Program Roadmap

state: active
active_program: zuno-real-unified-runtime-cutover-v1
current_phase: PHASE07_benchmark-and-closure
latest_completed_program: zuno-unified-agent-runtime-closure-v1

## Program 目标

把 Completion / Workspace 产品主路径切到真实统一 runtime：

```text
UnifiedAgentRuntimeService
-> compiled LangGraph
-> RuntimeDependencyFactory
-> Model Gateway / Memory / Corrective Agentic GraphRAG / Tool Control Plane
-> GroundedAnswer / SSE / Artifact
```

## Phase 顺序

1. `PHASE01_real-runtime-baseline`：激活 program，冻结事实，建立 guardrail，不改生产 runtime。
2. `PHASE02_langgraph-execution-cutover`：让 compiled LangGraph 接管 `UnifiedAgentRuntimeService` 执行，手写主循环退出产品路径。
3. `PHASE03_runtime-dependency-factory`：建立 `RuntimeDependencyFactory` 和 typed protocols，停止核心依赖 `Any | None` 默认成功。
4. `PHASE04_real-agent-execution`：ModelStep 走 Model Gateway，ReActStep 执行单步 ReAct，Grounded Synthesis 产生真实 final answer / claims / bindings。
5. `PHASE05_knowledge-tool-memory-integration`：Knowledge、filesystem.read/write、Memory pre/in/post-turn 和 Reflexion reuse 接入统一 runtime。
6. `PHASE06_product-cutover`：Completion / Workspace 默认走 unified runtime，GeneralAgent 只保留显式 rollback flag。
7. `PHASE07_benchmark-and-closure`：运行或诚实阻塞 benchmark，输出 implementation / measurement / quality gate 三段状态，归档并恢复 no-active。

## 每个 Phase 的固定节奏

```text
读取当前 Phase
-> 审计真实代码
-> 实现
-> focused tests
-> regression tests
-> verifier
-> 更新 Current/Target 文档
-> 更新 Program 状态
-> git diff --check
-> 独立 commit
-> push
-> 自动进入下一 Phase
```

## 不变关闭定义

不得把 PHASE02-PHASE07 目标写成 Current、Completed 或 measured；每个目标只有在代码、测试、trace 或 eval 证明后才能关闭。

1. 目标代码进入唯一 owner。
2. focused unit/integration tests 通过。
3. 至少一个真实或 deterministic vertical scenario 通过；涉及真实 provider 时不能用 deterministic fixture 伪装。
4. trace 能说明关键决策和失败。
5. 需要 restart 证明的 Phase 必须重建进程后读取。
6. Current/Target 文档按事实更新。
7. `git diff --check` 通过。
8. 不以 mock/fixture/prepared/partial profile 结果冒充 measured quality。
