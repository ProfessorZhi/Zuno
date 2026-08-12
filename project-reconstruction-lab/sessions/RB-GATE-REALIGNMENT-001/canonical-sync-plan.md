# Canonical Sync Plan

```text
Status: NOT_APPLIED
User Gate: PENDING_USER_DECISION
Applied Commit SHA: NONE
```

## 候选同步范围

| 目标 | 候选 Owner | 变更 | 本轮状态 |
|---|---|---|---|
| Gate maturity / Current-Target wording | `docs/project/architecture/architecture.md` | 区分 Accepted Target、Implemented、Verified、Measured、Production | NOT_APPLIED |
| Domain / Runtime state contract | `docs/project/domain/`、`docs/project/agents/`、`docs/project/data/` | 写入已批准的 Owner/Recovery Contract | NOT_APPLIED |
| Citation provenance | `docs/project/knowledge/`、`docs/project/eval/` | 写入 Q039-C Target Contract 和 evidence gap | NOT_APPLIED |
| Tool/Sandbox qualification | `docs/project/security/`、`docs/project/services/` | 写入 Q061/Q063/Q064/Q066/Q070 边界 | NOT_APPLIED |
| Program / status references | `.agent/programs/`、`docs/status/` | 仅在用户确认后同步状态，不升级 Current | NOT_APPLIED |

本轮已修改的 `docs/governance/architecture-gate-policy.md` 只记录治理规则，不是
Canonical Target Architecture 的内容同步；本轮没有新增 ADR，也没有修改 `docs/project/`
或 `docs/decisions/` 的架构事实。

## 取消条件

如果用户拒绝、要求重做或新增 A-P0，以上候选全部保持未应用。若后续 Benchmark、Spike 或
外部资格证明简单方案足够，必须在同步前把相关 Target 标记为 `DEFERRED`、`REJECTED` 或
`SIMPLIFY`。
