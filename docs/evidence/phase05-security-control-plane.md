# PHASE05 Security Control Plane Evidence

status: partial_implementation_available

phase_completion: `not_approved`

date: 2026-07-19

## 目标

记录 PHASE05 Security Control Plane 的当前可复现证据，覆盖审批事实持久化、fail-closed、mandatory audit requirement 和最小 security eval。本文不是 Phase Closure Decision。

## 已证明

- Security-owned PostgreSQL schema 已提供 Principal、Epoch、Authorization Decision、Approval Request、Approval Decision、Secret Ref、Secret Lease、Redaction Decision、Audit Requirement 和 Security Outbox 事实表。
- Tool Runtime approval path 可通过 `PostgresSecurityApprovalFactSink` 写入 Security facts。
- blocked path 会在 effect 前写入 `failed_closed_before_effect` fact，并记录 `DENY` authorization decision、`failed_closed` audit requirement 和 Security outbox event。
- Security sink outage 会在 side effect executor 前中断。
- 最小 eval evidence 覆盖：
  - adaptive attack side-effect request must require approval or deny；
  - benign read-only request must preserve utility；
  - security sink outage must fail closed before effect。

## 可复现验证

```powershell
python tools/scripts/verify_phase05_security_persistence.py
python tools/scripts/verify_phase05_security_eval.py
pytest -q tests/security/test_phase05_security_eval_gate.py tests/fault/security/test_phase05_security_sink_fail_closed.py tests/integration/test_phase05_security_persistence_runtime.py -p no:cacheprovider
```

## 未证明

- 尚未覆盖完整 PEP/PDP cutover。
- 尚未覆盖所有 Security fault matrix。
- 尚未形成 PHASE05 closure decision。
- PHASE07 与 PHASE11 不得引用本文作为依赖已完成证明。
