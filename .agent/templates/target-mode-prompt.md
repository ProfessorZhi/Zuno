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
