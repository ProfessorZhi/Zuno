# ROUND-001 Counter Attack / Retest

本文件记录 Counter Attack 的设计和当前状态。由于 Blue Change Set 尚未通过 User Gate，所有 Retest 都是 `NOT_STARTED`，不伪装成已经验证。

## RETEST-001

上一轮 Gap: GAP-V2-004, GAP-V2-020
Change IDs: NONE
Mutation Variable: 将 C 与 B 的模型、语料、工具、Token/Time Budget 固定，并加入 WorkBuddy Host + Legal Backend 与 Native Runtime 的同任务比较。
Red Counter Attack: 如果 C 只是在 Runtime 内重复 B 已完成的 Domain Conditions、Evidence Gate 和 Reconciliation，C 不能因 first-class 命名保留；如果 C 只增加 Calls/Latency/Cost，也必须删除或外部化。
Expected Evidence: A/B/C preregistration、trace、quality/efficiency metrics、attribution report。
Result: NOT_STARTED
Status: OPEN

## RETEST-002

上一轮 Gap: GAP-V2-013, GAP-V2-017
Change IDs: NONE
Mutation Variable: 在 Domain Commit、Checkpoint、Queue ACK、Tool Provider Success 四个交叉点注入 crash/timeout/restart。
Red Counter Attack: 如果任一恢复路径把 Node complete 当业务完成、把 timeout 当失败或盲目重试不可逆 Effect，Runtime/Tool/Data Contract 不能通过。
Expected Evidence: fault injection、EffectReceipt、provider operation ID、idempotency/reconcile trace。
Result: NOT_STARTED
Status: OPEN

## RETEST-003

上一轮 Gap: GAP-V2-015, GAP-V2-016
Change IDs: NONE
Mutation Variable: 注入恶意 PDF/Memory/Observation、撤销父 Grant、修改 ToolVersion/参数和改变 Approval Epoch。
Red Counter Attack: 如果内容能改变授权、旧审批能执行新参数或 Secret 出现在模型/Trace/Memory，安全 Gate 仍然 OPEN。
Expected Evidence: injection+tool、cross-tenant、revocation、stale credential、secret leakage、version mismatch tests。
Result: NOT_STARTED
Status: OPEN

## RETEST-004

上一轮 Gap: GAP-V2-018
Change IDs: NONE
Mutation Variable: 低用户数/单节点、重 CPU/GPU ingestion、长 Agent Run、Sandbox 高风险 effect 和独立发布分别施加资源/故障约束。
Red Counter Attack: 如果五个服务没有独立 scaling/failure/security/lifecycle收益，必须合并物理部署；如果 Knowledge/Sandbox 有强边界，不能用“一个服务更简单”掩盖风险。
Expected Evidence: workload/failure/security/deployment matrix and cost/latency comparison。
Result: NOT_STARTED
Status: OPEN

## RETEST-005

上一轮 Gap: GAP-V2-001, GAP-V2-002, GAP-V2-024
Change IDs: NONE
Mutation Variable: 只允许用户确认、Artifact 或仓库证据升级 Historical Claim；拒绝用 Target/论文/团队工作补齐个人贡献和法院 QA。
Red Counter Attack: 如果架构回答需要虚构客户流程、QA 数量、个人文件或生产指标，返回 Fact Recovery，而不是继续 Blue Architecture。
Expected Evidence: user confirmation/artifact ledger/commit-task mapping。
Result: NOT_STARTED
Status: OPEN

## 当前结论

`counter_attack_status: WAITING_FOR_USER_GATE`。当前下一执行阶段是 `RB-BLUE-REPAIR-001`，不是
Round-002。Repair Closure、Final P0、Evidence 和 User Architecture Gate 通过后，才重新设计
Round-002；届时至少 70% 是新问题，最多 30% Regression，不能因为 Round-001 分数较高而降低攻击难度。
