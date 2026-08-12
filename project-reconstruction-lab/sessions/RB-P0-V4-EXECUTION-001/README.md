# RB-P0-V4-EXECUTION-001 — Critical Architecture Verification Execution

## 会话定位

本会话承接：

```text
RB-WORKFLOW-V2-001
→ RB-BLUE-REPAIR-001
→ RB-EVIDENCE-CLOSURE-001
→ RB-P0-V4-EXECUTION-001
```

本轮不是 Round-002、Implementation Program 或 Canonical Architecture Sync。它只把已有
Verification Plan 中可以安全执行的部分转化为 V4 executable evidence，并明确哪些仍然
属于 V3、IMPLEMENTATION_DEPENDENT、BLOCKED_EXTERNAL 或 V5 benchmark gap。

## Baseline

```text
BASE_SHA: 71630f16edf027b610e9b0ca7f17a6a4c0fc9080
Original P0: 12
V3 narrow evidence: 10 / 12
V4 accepted: 0 / 12
V5 legal benchmark: 0 / 12
P0 closed: 0 / 12
Counter Retest: NOT_RUN
Round-002: BLOCKED
Canonical Sync: NOT_APPLIED
```

## 证据边界

- `tests/architecture/test_p0_v4_execution.py` 是 verification-only harness，不是产品 Runtime；
- Q005/Q053/Q097 的并发和恢复模型只能证明候选不变量的行为，不能证明当前产品已有实现；
- Q063/Q064 使用 loopback HTTP provider emulator，证明 Emulated Boundary，不推断第三方 Provider；
- Q066 因 Docker/Deno 不可用而 `BLOCKED_EXTERNAL`，不能 PASS；
- Q039 被拆为 Critical Citation Invariant 与 V5 Product Benchmark，原始 Q039 保留。

## 入口

1. [Scope Audit](scope-audit.md)
2. [Execution Matrix](execution-matrix.md)
3. [Track A — State/Ownership/Recovery](track-a-state-recovery.md)
4. [Track B — Approval/Authorization/Effect](track-b-tool-effect.md)
5. [Track C — Sandbox/Context Security](track-c-security.md)
6. [Track D — Legal Evidence/Citation](track-d-legal-evidence.md)
7. `p0/*.md`
8. `results/command-log.md`、`results/fixtures/README.md`
9. [Red Evidence Review](red-evidence-review.md)
10. [Counter Retest](counter-retest.md)
11. [Closure Scorecard](closure-scorecard.md)
12. [Canonical Sync Candidate](canonical-sync-candidate.md)

## Closure rule

本轮执行通过不等于 P0 关闭。只有 `Execution PASS + Red ACCEPT_EVIDENCE + Counter Retest PASS`
同时成立时才允许 `CLOSED`。当前没有任何项目满足三项。
