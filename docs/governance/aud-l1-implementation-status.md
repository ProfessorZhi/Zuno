# AUD-L1 Pre-Send Mandatory Audit Abort Implementation Status

status: `IMPLEMENTED / SELECTED VERIFIED / AUD_L2_OPEN`
current_main_evidence: `4d0dc6bc194fe31d257e4b6c2e441f5d82201ab9 / run 35482378509 / 219 passed, 27 warnings`
artifact: `10595624959 / sha256:bd1f34e77b0f41763401252a6a46056b7e9594bbf79379c9eb924b73d3b4a3fe`
source_freeze: [`aud-l1-pre-send-audit-abort-freeze-candidate.md`](aud-l1-pre-send-audit-abort-freeze-candidate.md)
production_readiness: `NOT_ESTABLISHED`

AUD-L1 关闭的是一个确定的 pre-send lifecycle leak。Mandatory audit proof 已经提交以后，如果 current Security reauthorization 或 Sandbox 在 provider send 前明确阻断动作，06 会先持久化 `NOT_DISPATCHED / NO_EFFECT`，随后 Infrastructure 把同一 tenant / audit / effect / owner binding 从 `durable` 推进到 `dispatch_aborted`。该 row 保留“proof 曾经提交”的历史，但不再占用 pre-effect capacity，也不会被解释为 `effect_observed`。

Revision `20260920_60` 只扩展现有 `infra_mandatory_audit_events`：增加 `dispatch_aborted_at` 和 `dispatch_aborted` terminal status。没有新增 Audit Service、第二张 lifecycle 表、Queue、Worker 或 remote transaction。

Current PostgreSQL probes 已证明：

- audit commit 后 SecurityEpoch revoke：executor=0，ToolAttempt 保持 `FAILED / NOT_DISPATCHED`，audit row=`dispatch_aborted`；
- capacity=1 时，上述 abort 后第二个独立合法动作仍可取得 capacity 并发送；
- audit commit 后 Sandbox block 同样形成 `dispatch_aborted`，不创建 EffectReceipt / Reconciliation；
- exact abort replay 幂等；
- wrong tenant / owner / effect identity fail closed；
- 已 `effect_observed` 的 row 不能回退为 `dispatch_aborted`；
- 已 abort 的 audit proof不能再次被当作 send proof复用。

此前 revision `20260918_59` 已把 mandatory-audit channel / event storage显式绑定 tenant。AUD-L1 在该 tenant-scoped基础上补 lifecycle，不重新定义 Security policy或 AuditRequirement class。

## Remaining boundary

AUD-L1 只处理进程仍然活着、已经能够确定 provider send 没发生的错误路径。

如果进程在：

```text
audit proof committed
→ before provider send
→ before durable NOT_DISPATCHED fact / dispatch_aborted transition
```

之间硬崩溃，重启时单凭 audit row仍不足以判断 send 是否发生。该窗口继续定义为 AUD-L2：

```text
AUD-L2 = crash/restart audit lifecycle repair
```

AUD-L2 需要独立 failure model 和 recovery evidence；当前没有 background reconciler，也不会通过时间阈值猜测远端 Effect truth。

## Non-claims

Current evidence 不代表：

- AuditRequirement class 已实现；
- mandatory-audit lifecycle 已完全 crash-safe；
- remote Effect 可以由 audit status推断；
- manual reviewer Authority 已闭合；
- CXL-B 已可用；
- Product / Effect path 已 Production Ready。

AUD-L1 的 closing evidence 是 selected PostgreSQL verification，不是 Full CI、真实 Provider E2E 或 Production Qualification。
