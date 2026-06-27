# Zuno Eval Agent 规则

修改 `tools/evals/zuno` 前先读：

1. `.agent/references/verification-map.md`
2. `.agent/references/task-routing.md`
3. `.agent/references/workflow.md`

规则：

- 冒烟测试不是正式 Eval。
- Eval 配置、数据集、指标和输出路径必须可追踪。
- 不要覆盖历史 baseline。
- 本地运行产物必须和公开 evidence 分开。
- 如果本轮只是文档、验证器或测试同步，不要重新运行完整 Eval。
