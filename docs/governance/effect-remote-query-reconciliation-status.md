# Effect Remote-Query Reconciliation Status

status: `DEFERRED_BY_PROVIDER_CAPABILITY / MANUAL_CONCLUSIVE_FALLBACK_CURRENT`
base_main: `93097aefc3e79e894ea651a71d2eec389c6e5ba5`
source_review: `REPO_WIDE_PROVIDER_CAPABILITY_INVENTORY`
production_readiness: `NOT_ESTABLISHED`

06 Tool Runtime & Effects 已经能够把现实副作用的不确定性耐久保存为 Reconciliation，并通过 conclusive manual judgment 收敛为 `CONFIRMED_EXECUTED` 或 `CONFIRMED_NOT_EXECUTED`。restart replay 不会把 OPEN Reconciliation 升级成 completed，同一 authoritative manual judgment exact replay 幂等，不同第二结论 fail closed。

剩余的 remote-query gap 不是“少一个方法名”。真正自动对账至少需要两个条件同时成立：Provider 必须提供可以验证的远端状态查询能力；06 必须在 crash/restart 后仍持有执行这次查询所需的 durable query material。当前 source evidence 两端都没有成立。

## Current provider capability inventory

### OpenAPI / HTTP adapter

Current `OpenAPIToolAdapter` 支持 execute 与 connectivity test。Repo-wide search 没有找到按已发送 effect / business id 查询远端最终状态的 production capability，也没有 provider-specific status lookup contract。

普通 HTTP endpoint 当然可能由业务 API 自己暴露 GET/status，但 Current ToolDefinition / ProviderBinding 没有把“这个 operation 是原写动作的 authoritative reconciliation query”冻结成可消费能力。06 不能根据 URL 命名或 response shape 猜测。

### MCP adapter

Current MCP path 通过 `MCPToolExecutorAdapter -> ToolInvocationGateway -> provider tool` 执行现实动作。Repo-wide search 没有找到 MCP effect-status / reconciliation query extension 的 production consumer。

MCP 暴露了什么工具由 Provider 决定。若未来某个 MCP server 同时提供“send”和“query status”两个 tool，它们仍需要明确的 semantic binding；不能因为同属一个 server 就推断后者能确认前者的 Effect truth。

### CLI / Local / generic adapters

Current CLI / LocalFunction 等 adapter 没有通用 provider job/effect status API。对本地可证明未发送或已经完成的动作，现有 Attempt/Effect semantics 已经够用；没有必要为了接口对称性强迫所有 adapter 实现 remote query。

### Async external path

Current AsyncJob 拥有 `provider_job_id`、callback binding、deadline 与 callback ordering。CXL-A 已证明 cancel intent 之后真实 late callback 仍能更新最终 job truth。

这条 callback path 是 Provider push evidence，不等于 pull query capability。Repo-wide search 没有找到 production poll/status adapter。

## Durable query material 也尚未成立

`ToolEffectReconciliationInput` 在创建时包含 `reconciliation_query` 与 `reconciliation_payload`，但 Current PostgreSQL `tool_effect_reconciliations` 只持久化：

```text
reconciliation_query_hash
reconciliation_payload_hash
```

没有 durable raw query body / typed provider-query reference。

这个设计足以证明历史输入没有被静默改变，也足以支撑人工判断的 provenance，但无法在进程重启后重建一次自动 provider query。

因此即使今天增加：

```text
query_effect(...)
```

Current repository 仍没有 restart-safe input 可以喂给它。单独增加 Provider port 不能闭环 recovery。

## Decision

Remote-query reconciliation 当前选择：

```text
DEFERRED_BY_PROVIDER_CAPABILITY
```

这不是删除 Target Reconcile，也不是把人工判断当成长期唯一方案。它表示目前没有真实 Provider capability 足以证明新增 generic query abstraction / migration 的成本合理。

Current fallback 保持：

```text
UNKNOWN Effect
→ durable OPEN Reconciliation
→ replay remains reconciliation_required
→ escalation when needed
→ authorized durable one-shot manual judgment
→ conclusive EffectReceipt / resolved truth
```

没有 conclusive evidence 时继续 UNKNOWN。

## Reopen conditions

当第一个真实 Provider 满足以下条件时重新打开这一 slice：

1. Provider 拥有稳定的 effect/job/business identity；
2. Provider 提供可验证的 status/query API，而不是仅返回 transport success；
3. query 结果能区分至少 `CONFIRMED_EXECUTED | CONFIRMED_NOT_EXECUTED | STILL_UNKNOWN`；
4. Provider contract 说明 query 与原始现实动作的 semantic correlation；
5. Zuno 有真实任务需要自动恢复，而不是仅为了架构对称性；
6. fault probe 能够制造 response-loss / restart，并验证 query 后不会 duplicate dispatch。

满足这些条件以后，优先 Extend 现有 06 Owner，而不是建立新 Reconciliation Service。

## Minimal future extension

重新打开时，最小 Provider port 候选为：

```text
query_effect(
    provider_effect_id,
    provider_query_ref,
    current_credentials
)
→ CONFIRMED_EXECUTED
 | CONFIRMED_NOT_EXECUTED
 | STILL_UNKNOWN
 | UNSUPPORTED
```

同时只增加该 Provider 真正需要的 durable query material。优先保存 typed reference / minimal non-secret business key，而不是把任意 provider payload 整包塞入通用表。

任何 query operation 在调用前仍需消费当前 Security / Credential 条件。Secret material 不进入 reconciliation payload。

Conclusive query 结果复用现有 `resolve_effect_reconciliation()`；`STILL_UNKNOWN / UNSUPPORTED` 不写 resolved success，也不触发 blind retry。

## Required evidence when reopened

至少包含：

- remote executed + local response lost + process restart → query confirms executed → no redispatch；
- confirmed not executed → only then can a new action be considered after fresh checks；
- provider query outage / STILL_UNKNOWN → remains reconciliation_required；
- wrong tenant / provider effect id / query identity → fail closed；
- changed ProviderBinding / semantic version → old query capability 不能被无条件复用；
- Secret / SecurityEpoch 在等待期间变化 → query 前重新门禁；
- query 结果与已有 manual judgment 冲突 → fail closed / explicit review，不静默覆盖。

## Non-goals

本 Decision 不授权：

- generic Reconciliation microservice；
- 为所有 Tool 强制增加 query API；
- 新全局 Provider registry；
- 保存 Secret 或任意原始 provider payload；
- 因 provider query 失败而自动 retry 现实写动作；
- 把 `UNSUPPORTED` 当成 `CONFIRMED_NOT_EXECUTED`；
- 将人工 judgment 删除或降级为 telemetry。

## Current / Target boundary

**Current：** durable UNKNOWN ledger、typed restart replay、conclusive Effect convergence、durable one-shot manual judgment 与 CXL-A late-callback truth 已有 selected PostgreSQL evidence。

**Target：** 对真正支持 authoritative query 的 Provider，06 可以在 restart 后自动消费 durable query material 并收敛 Effect truth。

**Unknown / Measurement Needed：** 当前没有可验证的真实 Provider query capability，也没有生产任务数据证明自动 query 相对 manual fallback 的发生率、延迟或人工成本收益。

在这些证据出现前，继续使用简单方案比提前建设抽象更符合 Zuno 的复杂度门槛。
