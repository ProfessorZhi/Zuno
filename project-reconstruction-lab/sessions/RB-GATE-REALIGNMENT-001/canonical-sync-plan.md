# Canonical Sync Plan

```text
Status: APPLIED
User Gate: APPROVED
Applied Commit SHA: recorded in final handoff
```

## 候选同步范围

| 目标 | 候选 Owner | 变更 | 本轮状态 |
|---|---|---|---|
| Gate maturity / Current-Target wording | `docs/project/architecture/architecture.md` | 区分 Accepted Target、Implemented、Verified、Measured、Production | APPLIED |
| Domain / Runtime state contract | `docs/project/domain/`、`docs/project/agents/`、`docs/project/data/` | 写入已批准的 Owner/Recovery Contract | APPLIED |
| Citation provenance | `docs/project/knowledge/`、`docs/project/eval/` | 写入 Q039-C Target Contract 和 evidence gap | APPLIED |
| Tool/Sandbox qualification | `docs/project/security/`、`docs/project/services/` | 写入 Q061/Q063/Q064/Q066/Q070 边界 | APPLIED |
| Program / status references | `.agent/programs/`、`docs/status/` | 仅在用户确认后同步状态，不升级 Current | APPLIED |

本轮已修改的 `docs/governance/architecture-gate-policy.md` 只记录治理规则；本次同步没有新增
ADR，因为 ADR-0008/0009/0010/0011 已经承载对应的架构决定。同步不改变 Current、Measurement
或 Production Readiness。

## 取消条件

如果用户拒绝、要求重做或新增 A-P0，以上候选全部保持未应用。若后续 Benchmark、Spike 或
外部资格证明简单方案足够，必须在同步前把相关 Target 标记为 `DEFERRED`、`REJECTED` 或
`SIMPLIFY`。
