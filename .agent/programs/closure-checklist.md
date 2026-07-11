# Program Closure Checklist

state: active
active_program: zuno-real-unified-runtime-cutover-v1
current_phase: PHASE06_product-cutover
latest_completed_program: zuno-unified-agent-runtime-closure-v1

## Phase Closure

- [x] PHASE01 active program、truth source、PowerShell baseline、runtime gap facts 和 guardrail verifier 已冻结。
- [x] PHASE02 compiled LangGraph 成为 `UnifiedAgentRuntimeService` 执行引擎，手写主循环退出产品主路径。
- [x] PHASE03 `RuntimeDependencyFactory` 和 typed runtime protocols 接入 Completion / Workspace。
- [x] PHASE04 ModelStep / Planner / ReActStep / Grounded Synthesis 进入真实执行数据面。
- [x] PHASE05 Knowledge / Tool / Memory 真实接入，filesystem.read/write 和 PDF evidence vertical slice 通过。
- [ ] PHASE06 Completion / Workspace 默认 unified runtime，GeneralAgent 只保留 rollback flag。
- [ ] PHASE07 benchmark 输出 pass / fail / blocked，program 归档并恢复 no-active。

## Final Implementation Gate

- [ ] `UnifiedAgentRuntimeService` 真正调用 compiled LangGraph。
- [ ] 手写主运行 `while` loop 退出产品主路径。
- [x] `ModelStepExecutor` 真实调用 Model Gateway。
- [x] `ReActStepExecutor` 真实执行单个 PlanStep 的 ReAct。
- [x] 缺依赖时返回 blocked observation，不伪造 evidence、citation 或 completed。
- [x] Grounded Synthesis 产生真实 `final_answer`、claims、citation bindings 和 unsupported claims。
- [ ] Completion 默认进入 unified runtime。
- [ ] Workspace artifact 来自 unified runtime final state。
- [ ] GeneralAgent 只保留显式 rollback flag。
- [ ] SingleControllerDurableRuntime 不再是产品主 Controller。
- [x] 至少两个真实本地 Tool：安全的 filesystem.read 和经审批的 filesystem.write。
- [x] Memory 完成 pre-turn read、in-turn usage、post-turn write 和 approved Reflexion reuse。
- [x] PDF -> index -> corrective retrieval -> EvidenceLedger -> synthesis -> page citation 的真实纵向链路通过。
- [ ] Benchmark 诚实输出 pass、fail 或 blocked。

## 禁止的虚假关闭

- contract test 通过不等于 runtime complete。
- deterministic fixture 通过不等于真实 provider complete。
- benchmark prepared 不等于 measured。
- partial profile output 不等于 fixed paired benchmark。
- doc-level citation 不等于 source-span strict citation。
- implementation closure 不等于 quality gate pass。
