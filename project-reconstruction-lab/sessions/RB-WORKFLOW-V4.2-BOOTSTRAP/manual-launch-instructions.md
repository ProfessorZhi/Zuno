# V4.2 Manual Launch Instructions

本 Bootstrap 不自动启动 Round-006。ChatGPT 审查接受后，才允许人工创建新的 Red Session
与 Blue Session，并把同一个 BASE Snapshot 分别交给两个线程。

## 启动前检查

1. `python tools/scripts/verify_red_blue_workflow_v42.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-BOOTSTRAP`
2. 创建全新的 `red_session_id` 与 `blue_session_id`，不得复用 Round-005。
3. 固定相同 `canonical_snapshot_sha`。
4. Red 读取 `v4.2/red-thread-prompt.md` 与 Red-only calibration。
5. Blue 读取 `v4.2/blue-thread-prompt.md`，不得接收 calibration、业务代码或 Candidate。
6. Main 每次只 handoff 一个 Question、一个 Answer 或一个 Chain Decision。

## 停止条件

若发现预生成题单、Context 污染、Blue 修改 Canonical、hash 不一致或 Candidate 先于
`LIVE_ATTACK_COMPLETE`，立即停止并将 Round 标记为 `BLOCKED_BY_USER_GATE` 或验证失败；
不要用架构分数掩盖 Workflow 失败。
