# Track B — Approval / Authorization / Side Effect

## Q033

当前 `ApprovalGate` 对 WRITE_EXTERNAL + APPROVAL_REQUIRED Tool 在无 Approval 时返回
`allowed=false`、`approval_required=true`。这只覆盖 gate decision，不覆盖 Subject/Tenant/
ToolVersion/Arguments/SecurityEpoch 绑定和恢复后的真实 Effect。

## Q061

既有 Tool/Security batch 验证了 default deny、policy/epoch contract，但本轮没有可执行的
prepare-allowed → revoke → execute current integration。该 P0 保持 `IMPLEMENTATION_DEPENDENT`。

## Q063 / Q064

loopback HTTP provider emulator 实际模拟 response loss、commit-before-response-loss、not-
committed timeout、status query 和 duplicate request。结果证明 harness 的 idempotency/reconcile
contract；`Emulated Boundary` 不推断真实 Provider Reliability。

## Q070

当前 read-only Tool path 生成可关联的 task/trace/audit/tool request 字段；side-effect path
没有已配置的三方 persistence UOW，因此没有完整 request→effect→receipt 链。

## Track B result

```text
V4 emulator results: Q063/Q064
Current narrow results: Q033/Q070
Existing V3 only: Q061
Accepted: 0
```
