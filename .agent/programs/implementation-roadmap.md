# Program Roadmap

state: active
active_program: zuno-unified-agent-runtime-closure-v1
current_phase: PHASE05_unified-langgraph-runtime-skeleton
baseline_commit: 72488a25fde59bc5ef86b2b1c84f25d42cb946ca

## Program Definition

```text
Zuno Unified Agent Runtime
=
Plan-and-Execute for macro control
+ ReAct for step execution
+ deterministic/model Reflection
+ trajectory-changing Replan
+ governed Reflexion
+ four-layer Memory
+ Tool Control Plane
+ Corrective Agentic GraphRAG
+ durable state and trace
+ fixed paired benchmark
```

## Phase Roadmap

| Phase | 文件后缀 | 主要目标 | 主要变更域 |
| --- | --- | --- | --- |
| PHASE01 | `truth-source-baseline-and-program-activation` | completed：冻结真实基线、命令、failure semantics、sample case set 和 program 状态；未修改生产 runtime | docs/workflow only |
| PHASE02 | `unified-runtime-contracts-and-state` | completed：建立 AgentRuntimeState、Observation、Strategy、Plan、limits、snapshot 与兼容适配器；未关闭 gateway/store/graph/product cutover | runtime contracts |
| PHASE03 | `model-gateway-closure` | completed：ModelRole、ModelCall aliases、role trace、GeneralAgent gateway adapter 和 direct-call verifier 已完成；legacy SDK wrappers 显式 allowlist 保留 | model runtime |
| PHASE04 | `durable-store-trace-and-idempotency` | completed：SQLite-backed run/checkpoint/event/interrupt/plan/observation/tool claim store、local trace store 和 restart resume evidence 已完成；完整 graph restart 等 PHASE05/11 | persistence |
| PHASE05 | `unified-langgraph-runtime-skeleton` | 建立真实 StateGraph、conditional routes、stream、interrupt、resume | agent graph |
| PHASE06 | `strategy-plan-and-react-step-execution` | 把 Plan-and-Execute 和 ReAct 组合成真实逐步执行器 | planning execution |
| PHASE07 | `tool-control-plane-and-approval-integration` | ToolCallIntent -> policy/approval/credential/execution/observation 闭环 | tool runtime |
| PHASE08 | `corrective-agentic-graphrag-and-evidence-ledger` | 多轮检索、EvidenceLedger、quality gate、corrective action | knowledge runtime |
| PHASE09 | `reflection-replan-grounded-synthesis` | 确定性 gate、可选 critic、真实 replan、rewrite、citation finalization | quality control |
| PHASE10 | `four-layer-memory-and-reflexion-reuse` | 四层 Memory 读/用/写、Reflexion review 与未来任务复用 | memory closure |
| PHASE11 | `product-api-sse-ui-and-recovery-cutover` | Completion/Workspace/SSE/approval/trace/UI 切换到统一 runtime | product integration |
| PHASE12 | `real-pdf-source-span-vertical-slice` | PyMuPDF PDF -> IR -> CitationChunk -> SourceSpan -> grounded answer | document vertical |
| PHASE13 | `paired-benchmark-release-gate-and-program-closure` | sample-8、sample-80、release gate、旧主路径退出与文档收口 | quality closure |

## 依赖顺序

```text
PHASE01 -> PHASE02 -> PHASE03 -> PHASE04 -> PHASE05 -> PHASE06
-> PHASE07 -> PHASE08 -> PHASE09 -> PHASE10 -> PHASE11 -> PHASE12 -> PHASE13
```

后续 Phase 可以在独立 worktree 并行准备，但合并必须遵守依赖顺序。

## 每个 Phase 的关闭定义

1. 目标代码进入唯一 owner。
2. focused unit/integration tests 通过。
3. 至少一个真实或 deterministic vertical scenario 通过。
4. trace 能说明关键决策和失败。
5. 持久状态可序列化；需要 restart 证明的 Phase 必须重建进程后读取。
6. Current/Target 文档按事实更新。
7. `.agent/programs/current.md` 和 roadmap 同步。
8. PowerShell 命令兼容 Windows PowerShell 5.1。
9. `git diff --check` 通过。
10. 不以 mock/fixture 结果冒充真实模型、真实工具、真实解析或 measured quality。
