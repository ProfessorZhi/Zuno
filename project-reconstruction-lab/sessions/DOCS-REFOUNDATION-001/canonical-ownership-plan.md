# Canonical Ownership 计划

状态：`PROPOSED` / 本轮迁移边界

| Canonical Question | 唯一 Owner | 允许引用 | 不再拥有 |
| --- | --- | --- | --- |
| 历史项目发生了什么 | `docs/project/history/` | 证据、事实状态、Lab 恢复记录 | Target 架构 Contract |
| 当前仓库被什么证明 | `docs/project/status/current-reality.md` | 代码、测试、Migration、Trace、Eval、`docs/evidence/` | 历史推断 |
| Target 处于什么状态 | `docs/project/status/target-status.md` | accepted ADR、架构正文、Benchmark/Gaps | Current 运行事实 |
| 生产是否已证明 | `docs/project/status/production-readiness.md` | Current evidence、Qualification | 目标愿望 |
| 跨层架构为什么这样设计 | `docs/project/architecture/architecture.md` | Domain/Runtime/Service/State 的已定边界、ADR | 历史项目事实、实施计划 |
| 架构图如何展示 | `architecture-views.md` + `architecture.html` | `architecture.md` 的概念 | 新事实或第二份状态机 |
| 事实证据如何复现 | `docs/evidence/` | 代码、测试、Trace、Eval | Target 设计 |
| 决策为何成立 | `docs/decisions/` | Red/Blue、证据、用户 Gate | 当前实现证明 |
| 规则和 Owner 如何治理 | `docs/governance/` | Canonical 文件和验证入口 | 产品状态 |

## 迁移后判定

旧专题、旧模块和事实矩阵不再拥有当前 Canonical；它们只能作为 Git 可追溯的 Superseded 原始材料。Logical Capability、Physical Service、Worker、Process、Container 和 Team 不做一一映射。
