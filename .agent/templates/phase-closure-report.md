# Phase 收口报告模板

## 摘要

## 修改文件

## 关键决策

## 验证结果

## 多 agent 工作组结果

- Architecture / Docs Agent：
- Runtime / Code Agent：
- Verification Agent：
- Integration Reviewer Agent：

## Worker 身份与成本

| cost_scope | agent | model | worker | session_id | branch | PR / handoff | commit | duration_ms | api_cost_usd_estimated | provider_quota_basis | validation | risk |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |

成本和时间统计以单个 agent 的一次 PR / handoff 为基本单位，不以一轮对话为单位。同一 worker 为同一 PR 多次 resume、重跑或补丁时，追加 ledger 行并在该 PR 汇总。API 成本账来自 Claude Code `stream-json --verbose` 的 `total_cost_usd` / `modelUsage.*.costUSD` 和 token 字段。平台额度账必须单独记录；无法从 provider 后台核实时写 `provider_quota_basis=unknown`，不能把 API 估算成本当作真实平台扣费。

## 调度取舍

- Claude Code worker 承接的简单 / 重复 / 下载 / 环境任务：
- Codex coordinator 承接的复杂判断 / review / merge / final verification：
- worker blocker 与升级处理：
- 成本 / 速度取舍结论：

## 验收闸门结果

## 自维护审查

- `AGENTS.md`：
- `.agent/system.yaml`：
- `.agent/references/`：
- `.agent/templates/`：
- `.agent/programs/`：
- `docs/history/programs/`：
- `docs/architecture/architecture.md`：
- `.agent/architecture/architecture.md`：
- `docs/architecture/architecture.html`：
- `.agent/architecture/architecture.html`：
- verifier / tests：

## 剩余风险

## PR 信息

- PR URL：
- PR 类型：base / stacked
- PR 风险说明：
- PR 身份标签：`agent=<agent> model=<model> worker=<worker>`
- Coordinator 审查结论：
- Coordinator 合并状态：

## Git 同步

- 分支：
- 提交：
- 推送：
- 未提交修改：
