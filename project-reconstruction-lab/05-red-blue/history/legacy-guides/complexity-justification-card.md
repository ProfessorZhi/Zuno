# Complexity Justification Card

本卡是 Red/Blue 评审工作材料，不是正式架构事实。每个重要组件、服务、数据库、Provider
或运行时机制在进入 `KEEP` / `REFINE` / `BUILD` 前必须填写。

```yaml
component:
status: PROPOSED
problem:
why_needed:
trigger:
responsibility:
not_responsible_for:
upstream:
downstream:
canonical_owner:
state_owned:
failure_modes:
retry:
recovery:
idempotency:
security_boundary:
observability:
scale_or_resource_reason:
alternative:
open_source_alternative:
simpler_alternative:
why_simpler_alternative_insufficient:
deletion_condition:
benchmark:
evidence_ids: []
decision: KEEP | REFINE | REPLACE | DELETE | DEFER
remaining_gap:
```

## 评审原则

- “更企业级”“以后会扩展”“大厂都这样做”不是证据；
- `Target`、`Hypothesis`、`PUBLIC_CONTEXT` 不能证明历史使用或 Current 行为；
- Provider 可以返回 Proposal、Candidate、Observation、Reference、Snapshot 或 Receipt，不能绕过 Canonical Owner 写入最终业务事实；
- 合并服务不自动更简单，拆服务也不自动更可靠；必须比较 Failure、Security、Resource、Ownership、Recovery、Latency 和运维成本；
- 删除条件必须可执行，通常绑定 Kill Test、Benchmark、Spike 或用户事实恢复。
