# AUD-L1 Pre-Send Mandatory Audit Abort Freeze Candidate

status: `READY_FOR_SCOPED_IMPLEMENTATION_AUTHORIZATION`
base_main: `d3096ca00ede6a4fb602e94493dea6536b91e878`
scope: `08 Security / Infrastructure mandatory-audit durability / 06 Tool send boundary`
implementation_authorization: `REQUESTED / NOT_YET_GRANTED`
production_readiness: `NOT_ESTABLISHED`

RB019 已经证明 `MANDATORY_BEFORE_EFFECT` 会在 provider dispatch 前消费 committed audit proof；后续实现又证明 provider dispatch 后 audit row 会从 `durable` 进入 `effect_observed`，并通过 revision `20260918_59` 把 audit channel / event 明确绑定 tenant。当前剩余的故障窗口发生在这两件事之间：proof 已经提交，但真正 send 还没有发生，之后 Security reauthorization、Sandbox 或其他本地 prerequisite 又把动作阻断。

这一窗口里外部 Effect 没有发生，因此不能把 audit row 写成 `effect_observed`。如果 row 永久停在 `durable`，它又会继续占用 mandatory-audit channel capacity。足够多的这种 pre-send abort 最终会让后续合法动作因为 `mandatory audit capacity exhausted` fail closed。

这不是新增审计系统的问题。现有 Infrastructure 已经把 `durable` 当作“proof 已提交、effect 还未观察”的占用状态，把 `effect_observed` 当作 send 后生命周期关闭。AUD-L1 只补一个明确的 pre-send terminal fact，使 capacity 可以释放，同时保留“该动作当时已经满足 mandatory-audit durability，但最终没有越过 send boundary”的历史证据。

## Current failure shape

当前 Tool send 顺序已经是：

```text
PreparedAction / Attempt intent durable
→ current Security / Approval checks
→ Secret lease
→ persist mandatory audit proof
→ commit
→ Security reauthorization
→ optional Sandbox
→ provider send
```

provider send 以后，Gateway 会调用 `mark_audited_effect_observed()`。send 以前如果发生以下情况：

- audit proof 提交后 SecurityEpoch 被撤销；
- audit proof 提交后 Approval / Authorization 不再成立；
- Sandbox policy 或 sandbox execution 在 provider send 前 fail closed；
- 其他明确证明 `NOT_DISPATCHED` 的本地 prerequisite 失败；

Gateway 会返回 blocked，并记录 ToolAttempt / ToolExecutionReceipt 为 `NOT_DISPATCHED / NO_EFFECT`，但 mandatory-audit row 仍保持 `durable`。

Current schema 的 audit event status 只有：

```text
durable
effect_observed
```

因此今天没有一种 durable fact 可以同时表达：

```text
audit proof was committed
+
provider effect was definitely not dispatched
+
this proof no longer occupies pre-effect capacity
```

## Minimal state extension

AUD-L1 允许在现有 `infra_mandatory_audit_events` 内增加一个最小 terminal status：

```text
dispatch_aborted
```

语义：

- audit proof 的历史事实仍然成立；
- 本地 send boundary 明确没有被越过；
- 该 row 不再计入 `durable` capacity；
- 它不能被解释成 `effect_observed`；
- 它不能证明远端撤销，因为远端调用根本没有发生。

可以增加 nullable timestamp：

```text
dispatch_aborted_at
```

不增加第二张 audit lifecycle 表，不增加新的 Audit Service，也不建立跨模块 2PC。

## Authority 与写入条件

Infrastructure 只拥有 audit durability / capacity execution fact；“为什么动作被阻断”仍由原 Owner 产生。

06 Tool Runtime & Effects 只有在自己的 durable Attempt / ExecutionReceipt 已明确记录：

```text
dispatch_certainty = NOT_DISPATCHED
effect_certainty = NO_EFFECT
```

并且当前 mandatory-audit binding 与 PreparedAction / tenant / requirement identity 仍匹配时，才可以请求 Infrastructure 将 audit event从：

```text
durable → dispatch_aborted
```

如果 dispatch certainty 是 `DISPATCHED`、`UNKNOWN` 或无法确认，禁止写 `dispatch_aborted`。这类情况继续使用 `effect_observed` 或 Effect/Reconciliation recovery，不允许用 audit lifecycle 猜现实结果。

08 Security 不直接修改 Infrastructure row。Security 只产生当前 Authorization / Approval / AuditRequirement事实；06 消费这些事实并根据 send boundary 的执行结果决定调用哪个 Infrastructure lifecycle primitive。

## Repository contract

Infrastructure 增加最小操作：

```text
mark_audited_effect_dispatch_aborted(
    audit_id,
    effect_id,
    owner_id
)
```

要求：

- current tenant 与 row tenant 一致；
- audit / effect / owner identity 全匹配；
- 只有 `status='durable'` 可以首次推进；
- exact replay 对已是 `dispatch_aborted` 的同一 row 幂等；
- `effect_observed` 不允许回退为 `dispatch_aborted`；
- wrong tenant / wrong owner / wrong effect id fail closed。

capacity 统计继续只计算 `status='durable'`。因此 `effect_observed` 与 `dispatch_aborted` 都退出 pre-effect capacity，但二者保留不同现实语义。

## Gateway ordering

AUD-L1 不改变 provider call 的 transaction boundary。

最小顺序：

```text
persist mandatory audit proof
COMMIT
→ re-check Security / Approval
→ prepare Sandbox when required
→ if local pre-send gate fails:
     persist ToolAttempt / ExecutionReceipt = NOT_DISPATCHED / NO_EFFECT
     mark audit dispatch_aborted
     return blocked
→ else provider send
→ mark effect_observed
→ continue existing Effect / Reconciliation flow
```

DB transaction / lock 不跨 provider call。

为了避免 audit lifecycle 成为业务真相 Owner，Gateway 必须先完成或至少在同一失败处理中形成明确的 Tool `NOT_DISPATCHED / NO_EFFECT` fact，再关闭 audit capacity。单纯捕获任意 exception 不足以写 `dispatch_aborted`。

## Crash window

AUD-L1 只关闭“正常错误处理已经知道 send 未发生，但 audit row 泄漏 capacity”的窗口。

如果进程在：

```text
audit proof committed
→ before provider send
→ before Tool NOT_DISPATCHED fact / audit dispatch_aborted write
```

之间硬崩溃，重启后仅凭 audit row 仍不能知道 provider send 是否发生。这个 crash/replay ambiguity 不在 AUD-L1 中通过猜测解决。

因此：

```text
AUD-L1 = deterministic pre-send abort lifecycle
AUD-L2 = crash/restart repair of audit lifecycle
```

AUD-L2 需要单独 fault model / recovery evidence，不在本 slice 增加 background reconciler。

## Required PostgreSQL probes

实施 AUD-L1 后至少需要进入 selected verification：

1. **Security revoked after audit commit**  
   matching audit proof 已提交；send 前 SecurityEpoch 被撤销；executor=0；ToolAttempt / ExecutionReceipt 明确 NOT_DISPATCHED / NO_EFFECT；audit row=`dispatch_aborted`；capacity 可被下一动作复用。

2. **Sandbox blocks after audit commit**  
   executor=0；audit row=`dispatch_aborted`；不得创建 EffectReceipt / Reconciliation。

3. **Exact abort replay**  
   同一 audit binding 重复关闭返回同一 terminal fact，不报假 conflict，也不重复占 capacity。

4. **Observed effect cannot abort**  
   已 `effect_observed` 的 row 再请求 dispatch-aborted 必须 fail closed。

5. **Wrong tenant / owner / effect identity**  
   fail closed，不能修改目标 row。

6. **Capacity=1 regression**  
   第一个动作 audit proof 提交后 pre-send abort；第二个独立合法动作仍可获得 audit capacity 并越过 send boundary。

## Non-goals

AUD-L1 不授权：

- AuditRequirement `BEST_EFFORT / DURABLE / MANDATORY_BEFORE_EFFECT` class redesign；
- provider remote-query reconciliation；
- CXL-B Product cancel orchestration；
- manual reviewer Authority；
- Target composed SecurityEpoch；
- crash/restart audit lifecycle reconciler；
- 新 Audit Service / Queue / Worker；
- 跨 Store / remote 2PC；
- GraphRAG、Memory、Multi-Agent 或 Native Runtime 扩张。

## Exit condition

AUD-L1 完成后允许写：

```text
mandatory-audit proofs that are deterministically aborted before provider dispatch
leave durable pre-effect capacity without being mislabeled as observed effects
```

仍不允许写：

```text
mandatory-audit lifecycle is fully crash-safe
all audit classes are implemented
audit proof means provider effect occurred
Production Ready
```

Current 仍由 main PostgreSQL selected evidence证明；没有对应 fault probe 的 lifecycle 语义继续保持 Unknown / Not Proven。
