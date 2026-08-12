# Track A — State / Ownership / Recovery

## Q005

Verification-only `DomainOwnerSpike` 覆盖 non-owner mutation、两个 concurrent proposals、
duplicate replay、same expected version conflict 和 stale commit。测试通过，但当前仓库没有
可指向的 Canonical Domain Owner persistence implementation，因此结论是
`IMPLEMENTATION_DEPENDENT`，不是 Current V4 closure。

## Q016

当前 `SQLiteAgentRunStore` + `AgentRuntimeService` 实际执行 restart/resume：checkpoint 和
pending interrupt 可以恢复，resume 后 Runtime 完成。当前没有 Domain Fact store 参与同一
故障矩阵，因此只接受为 Runtime control-state narrow claim。

## Q053

Verification-only spike 拒绝 stale PlanVersion 并要求 replan，重复 plan id 返回幂等 replay。
当前代码没有可执行的 PlanVersion/DomainVersion 联合写回 contract，结论为
`IMPLEMENTATION_DEPENDENT`。

## Q097

Verification-only recovery model 把 Domain 作为 authoritative、Checkpoint 作为 rebuildable、
Unknown Effect 作为 reconcile-before-retry。当前缺 Domain/Checkpoint/Effect/Queue 四方真实
故障注入，不能关闭 Q097。

## Track A result

```text
Executable results: available
Current cross-state V4: not established
Accepted: 0
Implementation-dependent: Q005/Q053/Q097
Narrow claim: Q016
```
