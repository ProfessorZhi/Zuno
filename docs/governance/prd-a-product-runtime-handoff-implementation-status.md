# PRD-A Product Runtime Handoff Implementation Status

status: `PRD_A1_IMPLEMENTED_SELECTED_VERIFIED / PRD_A2_NOT_IMPLEMENTATION_PROVEN`
current_main_evidence: `cf31e67e1bbadbd63c6a5fac9e6cb408f19e01b3 / run 35502213125 / 221 passed, 29 warnings`
source_freeze: [`prd-a-product-runtime-handoff-freeze-candidate.md`](prd-a-product-runtime-handoff-freeze-candidate.md)
production_readiness: `NOT_ESTABLISHED`

PRD-A freeze 把 CXL-B 的上游 Product runtime handoff拆成两层。A1回答“重启后的 consumer 到底能读取什么”，A2回答“这些 Owner facts 怎样稳定启动同一个 canonical runtime task/run”。当前只有 A1 已经进入 main implementation 和 selected PostgreSQL verification。

## PRD-A1 — Durable RuntimeExecutionSpec

**Current：IMPLEMENTED / SELECTED VERIFIED。**

Product RuntimeRequest 提交现在会在同一 Product transaction 内形成 typed/versioned `RuntimeExecutionSpec`。revision `20260920_61` 新增 `product_runtime_execution_specs`，保存 tenant / workspace / conversation / principal、runtime request / submission / client identities、active AgentVersion、受控 goal material、runtime surface / plan kind、knowledge refs / caller runtime budget limits、optional tool id / arguments，以及 `content_fingerprint / spec_version / spec_hash`。

任意 frontend payload不会整包进入 dispatch queue。Product outbox只携带 spec ref/hash与既有 identity；dispatch consumer按 tenant + spec ref重新读取 durable fact并验证 hash、runtime request、workspace、conversation、principal、submission、AgentVersion，以及 outbox row-level tenant / aggregate / ordering / idempotency identity。

Completion surface也不再只留下 `user_input_hash`。真实 `user_input` 作为受控 goal material进入 Product-owned spec，使 fresh worker可以只依赖 PostgreSQL恢复执行输入。

A1 的 fail-closed边界包括：same identity + same spec exact replay；same identity + changed spec conflict；Secret material拒绝；wrong tenant / outbox envelope / spec hash在 Agent Core owner write前拒绝；non-`SUBMIT_USER_GOAL` command不会被 runtime-dispatch consumer误当成新运行。

Current evidence绑定 `main@cf31e67e1bbadbd63c6a5fac9e6cb408f19e01b3`、GitHub Actions run `35502213125`、PostgreSQL 16.15；selected suite得到 `221 passed, 29 warnings in 47.52s`，artifact `10602448636`，digest `sha256:d6b509a2c3d2b46a453e35c18198c3ad5f3d9a735efe7b5efb47b3c18d256c2f`。

这证明的是 durable handoff material，不是 canonical graph execution。

## PRD-A2 — Canonical execution binding

**Current：NOT IMPLEMENTATION-PROVEN。**

今天的 dispatch consumer仍只建立 Agent Core GoalVersion / TaskContract / AgentRun owner facts。它没有完成 freeze要求的 stable `runtime_request_ref → canonical_task_id → canonical_run_id` mapping，也没有调用 server-owned `WorkspaceAgentRuntime / AgentRuntimeService` start-or-recover。production Worker / startup binding也仍未证明。

因此 A1 不能被扩写成“Product RuntimeRequest 已执行”。owner commit后 runtime未启动、runtime store已存在但 Product update丢失、queue duplicate等 A2 fault windows仍需要自己的 PostgreSQL evidence。

## CXL-B relationship

CXL-B 的上游 blocker现在已经从“execution input也不耐久”缩小成 PRD-A2：

```text
Product cancel token                         CURRENT
Runtime/Tool cancellation primitives         CURRENT
PRD-A1 durable RuntimeExecutionSpec           CURRENT / SELECTED VERIFIED
PRD-A2 canonical runtime identity/start       NOT IMPLEMENTATION-PROVEN
CXL-B cancel -> same live canonical run       BLOCKED_BY_PRD_A2
```

在 A2 之前，不允许 action consumer根据字符串猜 task id，也不允许直接写 ToolCancellationReceipt绕过 04 Runtime cancellation intent。

## Non-claims

本状态不表示 Product RuntimeRequest 已进入 canonical graph、production Product dispatch worker 已绑定、Budget owner admission或新 Product Approval flow已实现、CXL-B 已闭环，或 Full CI / 真实 Provider E2E / Production Readiness 已建立。
