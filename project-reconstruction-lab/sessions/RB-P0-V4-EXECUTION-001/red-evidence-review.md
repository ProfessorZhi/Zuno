# Red Evidence Review

## Review 状态

Blue 不自我批准。Red 对每个 Execution Record 重新检查 Evidence Boundary、Actual、Cannot Infer
和 Failure Result。

| P0 / Derived | Red Decision | Reason |
|---|---|---|
| Q005 | REQUEST_MORE_EVIDENCE | model spike 不是 Current Domain Owner persistence |
| Q016 | NARROW_CLAIM | 只证明 SQLite Runtime restart，缺 Domain/Effect reconciliation |
| Q033 | NARROW_CLAIM | 只证明无 Approval 时 gate，不证明绑定/撤销/旁路 |
| Q039-C | SCOPE_SPLIT_ACCEPTED + REQUEST_MORE_EVIDENCE | missing citation 可 gate；wrong span 仍被当前实现接受 |
| Q039-B | REQUEST_MORE_EVIDENCE | 必须 V5 Court QA/A-B/C |
| Q053 | REQUEST_MORE_EVIDENCE | model conflict 不是 Current Plan/Domain transaction |
| Q061 | REQUEST_MORE_EVIDENCE | 没有 execute-time revoke integration |
| Q063 | REQUEST_MORE_EVIDENCE | emulator 不是第三方 Provider |
| Q064 | REQUEST_MORE_EVIDENCE | emulator 可控，不证明 Provider 可查询 |
| Q066 | REQUEST_MORE_EVIDENCE | Docker/Deno unavailable，真实 Sandbox 未执行 |
| Q067 | NARROW_CLAIM | untrusted flow gate 通过，缺完整 injection→Tool path |
| Q070 | REQUEST_MORE_EVIDENCE | readonly correlation 通过，缺 side-effect receipt chain |
| Q097 | REQUEST_MORE_EVIDENCE | recovery model 不是四方 current state store |

## Red acceptance count

```text
ACCEPT_EVIDENCE: 0
NARROW_CLAIM: 3 (Q016/Q033/Q067)
SCOPE_SPLIT_ACCEPTED: 1 (Q039)
REQUEST_MORE_EVIDENCE: 9
REJECT_EVIDENCE: 0
Counter Retest: NOT_RUN
```

`SCOPE_SPLIT_ACCEPTED` 只接受 Q039 的分类，不接受 Q039-C 或 Q039-B Closure。

## Red 禁止升级

- verification-only model 不得升级成 Current；
- loopback Provider 不得升级成第三方可靠性；
- xfail 不得升级为 PASS；
- batch verifier 不得升级为 V4 integrated evidence；
- 没有 Court QA 不得生成 Historical Result；
- Q066 不得在缺少隔离运行时的情况下 PASS。
