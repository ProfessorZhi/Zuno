# Program Roadmap

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-lean-complete-product-architecture-v1

## 当前路线状态

当前没有 active program。最近完成的 roadmap 已归档：

- `docs/history/programs/zuno-lean-complete-product-architecture-v1/implementation-roadmap.md`

## 后续 Target

短期后续工作以 `docs/architecture/production-readiness.md` 的 P0 / P1 / P2 closure gap 为准：

- P0 Agentic GraphRAG fixed benchmark 跑通并达到 baseline gate。
- P0 所有真实模型调用统一进入 Model Runtime / Gateway。
- P0 Agent run trace 持久化并可查看。
- P1 task / planner / retrieval / approval 状态本地持久化。
- P1 至少一个真实 PDF parser 跑通 source span citation。
- P1 2-3 个真实 Tool 完成 approval / timeout / trace 闭环。
- P1 Memory ContextPack 在真实 AgentChat 中可观测。
- P2 前端 E2E、项目演示脚本和可复现启动方式。

## 开新 program 规则

- 新 program 必须从 `PHASE01` 开始。
- 旧 phase 文件必须保留在 `docs/history/programs/`，不得复制回前台冒充 active。
- 每个 phase 的 Current 必须来自代码、测试、trace/eval 或 verifier。
