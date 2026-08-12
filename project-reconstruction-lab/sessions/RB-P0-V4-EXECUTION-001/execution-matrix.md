# V4 Execution Matrix

> `Actual` 是当前执行结果；`Decision` 是证据范围判断，不是自动 Closure。所有 Original P0 仍保留。

| P0 / Derived | Track | Verification Level | Environment | Command / Fixture | Actual | Exit Code | Decision | Red Decision | Counter Retest | Final Closure |
|---|---|---|---|---|---|---:|---|---|---|---|
| Q005 | A | V4 verification-only spike | Python/pytest，当前仓库无 Domain Owner 实现 | `test_q005_v4_spike_owner_concurrency_duplicate_and_stale_rejection` | owner/非 owner、并发 stale、duplicate replay 通过 | 0 | IMPLEMENTATION_DEPENDENT | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q016 | A | V3 current + restart fault path | SQLite runtime store | `test_q016_current_runtime_restarts_without_treating_checkpoint_as_domain_fact` | restart/resume 通过；无 Domain store | 0 | NARROW_CLAIM | NARROW_CLAIM | NOT_RUN | OPEN |
| Q033 | B | V3 current approval path | Current Tool/Approval contract | `test_q033_current_runtime_requires_approval_before_effect` | no approval → approval required 通过 | 0 | NARROW_CLAIM | NARROW_CLAIM | NOT_RUN | OPEN |
| Q039-C | D | V4 fixture + negative case | Current synthesis + versioned fixture | `test_q039_citation_fixture_abstains_when_retrieval_has_no_citation`; wrong-span xfail | missing citation 通过；wrong span 未被拒绝 | 0 / XFAIL | OPEN | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q039-B | D | V5 | Court QA 不可用 | A/B/C legal benchmark | 未执行 | — | V5_BENCHMARK_REQUIRED | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q053 | A | V4 verification-only spike | Python/pytest，无 Plan/Domain current contract | `test_q053_v4_spike_rejects_stale_plan_and_replays_idempotently` | stale conflict/replan/idempotent replay 通过 | 0 | IMPLEMENTATION_DEPENDENT | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q061 | B | V3 existing only | Security/Tool batch contract | existing Tool/Security batch verifiers | prepare/default deny 通过；execute-time revoke 未执行 | 0 | IMPLEMENTATION_DEPENDENT | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q063 | B | V4 loopback provider emulator | 127.0.0.1 HTTP | `test_q063_v4_loopback_provider_response_loss_is_idempotent` | response lost 后同 key replay，effect count=1 | 0 | NARROW_CLAIM | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q064 | B | V4 loopback provider emulator | 127.0.0.1 HTTP | `test_q064_v4_unknown_outcome_reconciles_before_safe_retry` | committed/not committed 分别先 reconcile | 0 | NARROW_CLAIM | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q066 | C | V3 contract only / V4 blocked | Docker、Deno 均不可用 | `docker version`; `deno --version` | 无真实隔离运行时 | — | BLOCKED_EXTERNAL | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q067 | C | V3 current security path | SecurityRuntimeBatch | `test_q067_untrusted_context_cannot_authorize_tool` | untrusted flow 被拒绝 | 0 | NARROW_CLAIM | NARROW_CLAIM | NOT_RUN | OPEN |
| Q070 | B | V3 current partial trace | ToolControlPlane read-only path | `test_q070_current_readonly_trace_has_correlation_fields` | readonly trace correlation 通过；effect path 未完成 | 0 | NARROW_CLAIM | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |
| Q097 | A | V4 verification-only recovery spike | Python/pytest，无三方 current state store | `test_q097_v4_spike_recovery_keeps_unknown_effect_out_of_retry` | authoritative/reconcile-before-retry 通过 | 0 | IMPLEMENTATION_DEPENDENT | REQUEST_MORE_EVIDENCE | NOT_RUN | OPEN |

## 统计

```text
Original P0: 12
Scope Split: 1 (Q039 → Q039-C / Q039-B)
V4 execution records: 6 (Q005/Q039-C/Q053/Q063/Q064/Q097)
V3 current/narrow records: 5 (Q016/Q033/Q061/Q067/Q070)
V4 accepted by Red: 0
Counter Retest PASS: 0
P0 CLOSED: 0
```
