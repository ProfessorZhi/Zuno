# Zuno 项目证据地图

## 当前可复核入口

| 主张类型 | 证据入口 | 说明 |
|---|---|---|
| 总体架构 | `docs/project/architecture/` | 目标和架构边界，不能自动证明生产完成 |
| 历史模块设计 | `docs/history/superseded-document-taxonomy/project-modules/` | 上一阶段逻辑模块 Target 与 Contract，仅作迁移输入 |
| Current 状态 | `docs/project/status/` | 只记录实现和证据已经证明的内容 |
| 面试问题模式 | `docs/verification/interview-qa/` | 架构红队问题库，不拥有项目事实 |
| 代码与运行时 | `src/`、`apps/`、`infra/` | 用于验证实现，不以文档替代代码检查 |
| 测试与验证 | `tests/`、`tools/` | 用于复现质量、结构和协议约束 |
| 证据 | `docs/evidence/` | Trace、Eval、基线和收口证据 |

## 尚未自动推断

真实用户、客户、用户规模、团队人数、个人贡献、实际部署和业务指标仍必须由用户确认或提供外部证据。仓库里的目标架构、类名、目录和 Mock Test 不能单独证明这些事实。
