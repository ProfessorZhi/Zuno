# CXL-B Cancel Orchestration Freeze Candidate

status: `READY_FOR_REVIEW / IMPLEMENTATION_NOT_AUTHORIZED`
base_main: `4823611a47e950db47bb75d37300381b9c561f3f`
source_review: `REPO_WIDE_CURRENT_PATH_REVIEW`
production_readiness: `NOT_ESTABLISHED`

CXL-A 已经把一个确定的外部事实错误关掉：AsyncJob 进入 `CANCEL_REQUESTED` 后，匹配 durable provider job / callback binding 的真实 late callback 仍然可以推进最终 `COMPLETED`；伪造 binding 不推进状态；CancellationReceipt exact replay 保持同一事实，changed-content reuse fail closed。

这解决的是“取消意图不能覆盖现实结果”，还没有解决“谁在生产路径发起取消、什么时候调用 provider cancel、provider 不支持取消时如何收敛”。Current Evidence 因而仍把完整 cancel-in-flight orchestration 记为 CXL-B 未实现。

最简单的方案不是再造一个 Cancel Service。现有 04 Runtime 已经拥有 run / plan / step 控制事实，06 Tool Runtime & Effects 已经拥有 PreparedAction、Attempt、AsyncJob、CancellationReceipt 与最终 Effect truth。CXL-B 只需要把一条明确的控制命令接到这两个 Owner，并给能够取消的 Provider 一个可选 capability。

## Current source evidence

### Runtime 有“取消”概念，但没有 production Product→Tool orchestration

`SingleControllerDurableRuntime.cancel_task()` 可以把自己的 durable runtime task 标成 cancelled 并记录 `runtime_cancelled` 事件；它没有读取当前 Tool AsyncJob，也不会调用 `ToolInvocationGateway.record_cancellation_request()`。

`WorkSpaceSimpleAgent` 中的 “取消 / stop / cancel” 识别只用于工具创建向导，不是 AgentRun / Tool execution 的生产取消入口。

Repo-wide search 没有建立以下 Current call chain：

```text
Product / Host cancel command
→ current AgentRun / Plan / Step cancellation intent
→ locate pending Tool AsyncJob
→ ToolCancellationReceipt
→ optional provider cancel
→ late callback / timeout / confirmed effect truth
```

因此 Current 结论是：

```text
PRODUCTION_CANCEL_ENTRYPOINT = NOT_IMPLEMENTATION_PROVEN
RUNTIME_TO_TOOL_CANCEL_ORCHESTRATION = NOT_IMPLEMENTATION_PROVEN
```

### 06 已经有 cancellation durability primitive

`ToolInvocationGateway.record_cancellation_request()` 当前能够绑定 PreparedAction / Attempt / optional AsyncJob / provider job identity，并写 `ToolCancellationReceipt`。

CXL-A 已进一步证明：

- cancellation receipt exact replay 幂等；
- changed-content identity reuse fail closed；
- `CANCEL_REQUESTED` 不等于外部 Effect 已撤销；
- verified late callback 仍可以把 AsyncJob 推进到真实 `COMPLETED`。

这组 primitive 足以作为 CXL-B 的 06 Owner 锚点，不需要新 cancellation ledger。

### Current Provider boundary 没有 cancel capability

现有 Tool executor / adapter 调用面负责 execute；repo-wide search 没有找到 production `cancel_job / cancel_remote / provider_cancel` port。

因此 CXL-B 不能通过“本地写一条 CANCELLED”模拟 provider cancellation。Provider cancel 必须是显式可选能力；不支持、请求失败或结果不明确时，都继续保持外部撤销未证明。

## Ownership 与 Authority

01 Application & Integration 只负责接收 Host / Product 的取消命令，并把 tenant / workspace / task / run identity 交给 04。它不决定外部 Effect 是否已经撤销。

04 Agent Runtime & Control 拥有控制语义：

- 持久化 run / plan cancellation intent；
- 阻止尚未开始的新 Step；
- 找出已经 dispatch、仍可能在飞行的 Tool Step；
- 调用 06 的取消 orchestration；
- 在恢复时重新读取 06 已成立的 Effect / Cancellation facts。

06 Tool Runtime & Effects 拥有外部动作语义：

- PreparedAction / Attempt / AsyncJob 与 provider job identity；
- CancellationReceipt；
- provider cancel capability 的调用与结果解释；
- late callback / timeout / Effect truth 收敛。

08 Security 继续拥有 provider cancel 这个受保护外部动作是否允许执行的当前 Authorization / Credential / Audit 条件。CXL-B 不允许用原发送动作的旧 Approval 自动授权一个新的 provider cancel 操作。

远端 Provider 仍拥有其内部 job 最终状态。Zuno 只能保存可验证观察，不能凭本地 cancel intent 改写远端真相。

## Minimal Contract

### Runtime cancellation command

04 接收的最小命令应绑定：

```text
tenant_id
workspace_id
task_id / agent_run_id
plan_version / step_run_id when available
reason
requested_by_principal_id
idempotency identity
```

同一 cancel identity + 同一 payload 是 replay；同一 identity + changed payload 必须 conflict。

### Tool cancellation request

04 只有在该 Step 已经对应 durable 06 fact 时，才向 06 发取消请求。06 必须从自己的 ledger 读取并验证：

```text
prepared_tool_action_id
attempt_id
async_job_id when applicable
provider_job_id / external operation ref
current Tool / Provider version
```

调用方不能自报一组未与 durable job 匹配的 provider ids。

### Provider-facing optional cancel capability

只对声明支持 cancellation 的 adapter 暴露最小 port：

```text
cancel_effect(provider_job_id, provider_context)
    -> CONFIRMED_CANCELLED
     | CANCEL_REQUEST_ACCEPTED
     | NOT_SUPPORTED
     | STILL_UNKNOWN
```

语义：

- `CONFIRMED_CANCELLED`：Provider 给出可验证保证，该 job 不会再产生目标 Effect；06 才可以记录 `external_effect_revoked=true`。
- `CANCEL_REQUEST_ACCEPTED`：只证明 provider 接收了取消请求，不证明 Effect 已撤销；CancellationReceipt 保持 `external_effect_revoked=false`。
- `NOT_SUPPORTED`：记录 `NOT_GUARANTEED`，不盲目 fallback 到“本地取消成功”。
- `STILL_UNKNOWN`：保持未知，等待 callback / query / timeout / manual reconciliation。

Provider cancel 调用不放在数据库事务里，不引入 remote 2PC。

## State ordering

最小顺序：

```text
Product / Host cancel command
→ 04 persist cancellation intent
→ stop future undispatched work
→ locate durable in-flight Tool facts
→ 08 refresh authorization for cancel operation when provider call is needed
→ 06 persist cancellation request identity
→ COMMIT local cancellation intent / receipt prerequisite
→ optional provider cancel call
→ persist provider cancel observation
→ continue consuming callback / timeout / Effect truth
→ 04 recovery reads 06 final facts
```

取消发生在 send 前时，06 可以证明没有 dispatch 的动作继续保持 NO_EFFECT。

取消发生在 send 后时，04 的 run 可以停止未来调度，但已经发生或可能发生的现实 Effect 仍由 06 收敛。CXL-A 的 late callback 规则在这里保持不变。

## Required fault probes

CXL-B 实现只有在下面的 PostgreSQL-backed probes 成立后才可以升级 Current：

1. **cancel before Tool dispatch**：未来 Step 不再 dispatch；没有伪造 EffectReceipt。
2. **async provider supports cancel / confirmed**：CancellationReceipt 绑定正确 job；provider 明确确认取消后，`external_effect_revoked=true`；后续 forged callback 不改变状态。
3. **provider accepts cancel but不保证结果**：保持 `NOT_GUARANTEED`；late completed callback 仍收敛成真实完成。
4. **provider does not support cancel**：不调用第二套 fallback provider；run 停止未来工作，AsyncJob / Effect truth继续独立收敛。
5. **response loss after cancel request**：同一 cancellation identity replay 不重复制造不同取消事实。
6. **wrong tenant / job / provider identity**：fail closed，provider cancel executor=0。
7. **restart after local cancel intent**：新的 Runtime instance 从 durable cancellation + Tool facts 恢复，不靠旧内存状态猜结果。

## Non-goals

本 slice 不授权：

- 新独立 Cancel Service；
- 新 cancellation table / 第二套 idempotency key；
- 把 Runtime `cancelled` 直接映射成 Tool `CANCELLED`；
- 对不支持 cancel 的 Provider 做隐藏 retry / compensation；
- remote-query reconciliation；
- Formal Admission；
- Audit class / composed SecurityEpoch 扩张；
- GraphRAG、Memory、Multi-Agent、Native Runtime 扩张。

## Implementation slices

若本 Freeze Candidate 通过 review，实施拆成两个最小 slice：

```text
CXL-B1  04/01 production cancellation command → durable Runtime cancellation intent → 06 current in-flight Tool lookup
CXL-B2  06 optional provider cancel capability → CancellationReceipt update → callback/timeout recovery
```

先做 B1，不要求所有 Provider 都支持 cancel。B2 只为确实有可验证 cancel API 的 Adapter 实现 capability；没有该能力的 Adapter保持 `NOT_SUPPORTED / NOT_GUARANTEED`。

## Acceptance boundary

CXL-B 完成后允许写：

```text
production cancel command is durably orchestrated
supported provider cancel is capability-gated
cancel intent does not overwrite external effect truth
unsupported/unknown provider cancellation remains explicit
restart and late callback preserve owner facts
```

仍不允许写：

```text
all external effects are cancellable
cancel is exactly-once
remote cancellation is guaranteed
cancel rolls back completed work
cancel-in-flight is Production Ready
```

Current / production readiness 仍由 selected PostgreSQL evidence、真实 Provider E2E 与后续 qualification 分别证明。
