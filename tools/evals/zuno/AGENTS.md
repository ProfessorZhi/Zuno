# Zuno Eval Agent 规则

修改 `tools/evals/zuno` 前先读：

1. `.agent/references/verification-map.md`
2. `.agent/references/task-routing.md`
3. `.agent/references/workflow.md`

规则：

- Smoke tests 不是 formal eval。
- Eval 配置、dataset、metrics 和输出路径必须可追踪。
- 不要覆盖历史 baseline。
- 本地运行 artifacts 必须和公开 evidence 分开。
- 如果本轮只是文档/验证器/测试同步，不要重新运行 full eval。
