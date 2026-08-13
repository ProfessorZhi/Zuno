# Lab Migration Map

## 迁移原则

本次迁移只改变 Lab 的组织方式，不删除历史 Red/Blue 材料，不修改 Zuno Runtime、Migration、数据库或生产 Infra。

## 旧到新

| 旧材料 | 处置 | 新职责 |
|---|---|---|
| `00-charter.md` | `MOVE → legacy/numbered/00-charter.md` | 规则历史保留；新规则拆入 `00-charter/` |
| `01-project-facts.md` | `MOVE → legacy/numbered/01-project-facts.md` | 历史版本保留；当前事实工作视图在 `01-facts/` |
| `02-project-model.md` | `MOVE → legacy/numbered/02-project-model.md` | 历史模型保留；产品问题拆入 `04-product/` |
| `03-team-ownership.md` | `MOVE → legacy/numbered/03-team-ownership.md` | 历史模型保留；团队事实进入 `02-history/` |
| `04-attack-taxonomy.md` | `MOVE → legacy/numbered/04-attack-taxonomy.md` | 攻击词典保留；当前 Registry 在 `05-red-blue/` |
| `05-interviewer-personas.md` | `MOVE → legacy/numbered/05-interviewer-personas.md` | Persona 保留；当前面试入口在 `07-interview-red-team/` |
| `06-red-team-protocol.md` | `MOVE → legacy/numbered/06-red-team-protocol.md` | 旧协议保留；当前流程由 `README.md` 和 `05-red-blue/` 组合 |
| `07-blue-team-protocol.md` | `MOVE → legacy/numbered/07-blue-team-protocol.md` | 旧协议保留；当前 Blue/Counter 在 `05-red-blue/` |
| `08-gap-register.md` | `MOVE → legacy/numbered/08-gap-register.md` | Gap 分类保留；实施 Gap 在 `09-implementation/` |
| `09-open-source-review.md` | `MOVE → legacy/numbered/09-open-source-review.md` | Build/Buy 资料保留；决策候选在 `08-decisions/` |
| `10-delivery-evolution.md` | `MOVE → legacy/numbered/10-delivery-evolution.md` | 历史候选保留；事实时间线在 `02-history/` |
| `sources/` | `KEEP` | 公开资料与仓库侦察快照 |
| `sessions/` | `KEEP` | 已完成 Campaign 的审计记录 |
| `workflows/` | `KEEP` | 旧执行材料，逐步由新 README 路由 |
| `skill/` | `MOVE → skills/legacy/` | 旧 Skill Spec 保留；新三份 Spec 在 `skills/` |

## Canonical Sync

| Lab 输出 | 正式去向 |
|---|---|
| 确认历史事实 | `docs/history/` |
| 当前仓库证据 | `docs/evidence/` / `docs/status/` |
| Survived Target | `docs/architecture/`、ADR；未来专题若需要必须另行通过文档治理 |
| Ownership / 文档规则 | `docs/governance/` |
| 被替换的旧架构 | `docs/history/superseded-document-taxonomy/` |
| 可执行实现任务 | `.agent/programs/`，用户明确激活后才创建 |

## 禁止的迁移捷径

- 不把 `legacy/` 重新作为第二个主入口。
- 不把候选事实复制成 `docs/` Current。
- 不把 Session 的 Blue Change Set 自动当成 Accepted Architecture。
- 不因为新目录数量增加而创建空的专题事实源。
