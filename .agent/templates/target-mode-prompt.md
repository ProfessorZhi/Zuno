# 目标架构模式提示模板

按用户提供的验收闸门执行。

用于挂机模式的主线程，也用于多线程模式中每个独立 `codex/` 分支的子线程。这个模板只是给真正 Codex UI 目标模式线程使用的提示词骨架；提示词目标模式不等于 Codex UI 目标模式。若用户要求真实 UI 目标模式而工具 API 不能开启，主线程只能输出本模板并等待用户在 UI 里手动创建目标模式线程。

## 规则

1. 先读取目标来源。
2. 用户要求执行时，不停在建议层。
3. 修改保持在允许范围内。
4. 声称完成前必须运行验证。
5. 验证通过后才提交并推送。
6. 如果被阻塞，返回精确命令、输出摘要、已改文件和下一步建议。
7. 作为多线程模式子线程时，默认在线程内开启多 agent 模式来处理互相独立的子任务；只有高冲突、禁止并行或用户明确要求单线程时，才禁用并说明原因。
8. 作为 Claude Code worker 时，提示词必须显式包含 `agent`、`model`、`worker`、`session_id` 获取方式、worktree、branch、允许范围、禁止范围、commit message、PR title 和 handoff 字段。
9. worker 的 branch、commit、evidence 文件、PR 标题和 PR 描述必须带 `agent + model + worker` 身份标签。
10. worker 完成后必须返回 identity、session_id、branch、commit、changed files、validation、risk、duration、API 成本估算和 provider quota basis。
11. API 成本账来自 `stream-json --verbose` 的 token / cost / duration 字段；平台额度账单独记录，无法核实时写 `provider_quota_basis=unknown`。
12. worker 只提交候选结果；最终审查、合并、集成验证和 push 由 coordinator 完成。
13. 成本和时间统计以单个 agent 的一次 PR / handoff 为单位，不以一轮对话为单位。
14. 简单、大量、重复、下载/环境/格式类任务优先交给 Claude Code worker；复杂判断、根因定位、安全边界、合并和最终验证由 coordinator 收口。
15. 新建 Claude Code session 时必须使用 `--output-format stream-json --verbose`，从 final `type=result` 事件记录真实 `session_id`；同一 PR / handoff 的后续修复必须优先 `--resume <session_id>`。
16. worker 不得声称自己的结果已合并；只能报告候选 branch / commit / PR 和 handoff 回执。
17. worker 必须为 coordinator review 准备自评分输入：范围是否越界、验证是否可复现、evidence 是否真实、风险与 blocker 是否完整、是否存在安全或并发修改阻断项。

## Claude Code Worker Handoff

```text
agent=<agent>
model=<model>
worker=<worker>
cost_scope=single-agent-pr-handoff
session_id=<actual session id from stream-json result>
resume_policy=use --resume <session_id> for follow-up work on the same PR / handoff
worktree=<absolute worktree path>
branch=<codex/...>
commit=<sha or none>
pr=<url or none>
changed_files=<files>
validation=<commands and pass/fail summary>
api_cost_usd_estimated=<total_cost_usd sum for this PR / handoff>
provider_quota_basis=token | request | percent | credit | unknown
duration_ms=<sum for this PR / handoff>
risk=<remaining risk or none>
blockers=<blockers or none>
```

Coordinator 会按 100 分 scorecard 审查 worker 输出。缺身份、缺可复现 evidence、伪造测试、绕过安全门、覆盖并发修改或把 Target 写成 Current 会直接 block。
