# PRD-A Product Runtime Handoff Implementation Status

status: `PRD_A1_IMPLEMENTED_SELECTED_VERIFIED / PRD_A2_IMPLEMENTED_SELECTED_VERIFIED`
current_main_evidence: `5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660 / run 35516807526 / 224 passed, 32 warnings`
source_freeze: [`prd-a-product-runtime-handoff-freeze-candidate.md`](prd-a-product-runtime-handoff-freeze-candidate.md)
production_readiness: `NOT_ESTABLISHED`

PRD-A freeze 把 CXL-B 的上游 Product runtime handoff拆成两层。A1回答“重启后的 consumer 到底能读取什么”，A2回答“这些 Owner facts 怎样稳定启动同一个 canonical runtime task/run”。A1 与 A2 都已经进入 main implementation 和 selected PostgreSQL verification；这仍然只关闭 Product → canonical runtime handoff，不表示整个 Product Runtime 或 CXL-B 已完成。

## PRD-A1 — Durable RuntimeExecutionSpec

**Current：IMPLEMENTED / SELECTED VERIFIED。**

Product RuntimeRequest 提交现在会在同一 Product transaction 内形成 typed/versioned `RuntimeExecutionSpec`。revision `20260920_61` 新增 `product_runtime_execution_specs`，保存 tenant / workspace / conversation / principal、runtime request / submission / client identities、active AgentVersion、受控 goal material、runtime surface / plan kind、knowledge refs / caller runtime budget limits、optional tool id / arguments，以及 `content_fingerprint / spec_version / spec_hash`。

任意 frontend payload不会整包进入 dispatch queue。Product outbox只携带 spec ref/hash与既有 identity；dispatch consumer按 tenant + spec ref重新读取 durable fact并验证 hash、runtime request、workspace、conversation、principal、submission、AgentVersion，以及 outbox row-level tenant / aggregate / ordering / idempotency identity。

Completion surface也不再只留下 `user_input_hash`。真实 `user_input` 作为受控 goal material进入 Product-owned spec，使 fresh worker可以只依赖 PostgreSQL恢复执行输入。

A1 的 fail-closed边界包括：same identity + same spec exact replay；same identity + changed spec conflict；Secret material拒绝；wrong tenant / outbox envelope / spec hash在 Agent Core owner write前拒绝；non-`SUBMIT_USER_GOAL` command不会被 runtime-dispatch consumer误当成新运行。

Current evidence 由最新 selected baseline 统一绑定 `main@5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660`、GitHub Actions run `35516807526`、`224 passed, 32 warnings in 44.42s`，artifact `10607311350`，digest `sha256:9516463f36a1f3e519db0751d92d15221907d74a5d8ef6b844732336ac6c06bf`。

这证明的是 durable handoff material，不是 canonical graph execution。

## PRD-A2 — Canonical execution binding

**Current：IMPLEMENTED / SELECTED VERIFIED。**

revision `20260920_62` 为 Product owner receipt 增加 `runtime_request_ref`、`canonical_task_id`、`canonical_run_id`、`runtime_execution_spec_ref/hash` 的耐久绑定。同一 tenant / workspace / runtime request 通过 deterministic mapping 得到同一个 canonical task/run；Agent Core owner fact 与 runtime store继续是两类事实，但现在共享明确 identity。

dispatch consumer 的顺序已经收敛为 owner-first：先 claim event、读取并校验 A1 spec、提交 Agent Core owner facts 与 canonical binding，再通过 server-owned `WorkspaceRuntimeComposition` 构造 `AgentRuntimeService`，对同一 task执行 start-or-recover。runtime 已存在时读取现有 snapshot，不创建第二个 run。

selected PostgreSQL probes证明三个关键窗口：正常 dispatch建立一个 canonical runtime；owner commit后 runtime start响应丢失时 redelivery使用原 binding继续启动同一 task；runtime 已创建但 outbox completion响应丢失时 redelivery不会产生第二个 `runtime_started` 或第二个 runtime row。当前 request可以真实到达 canonical runtime，并在 formal Budget owner未绑定时保持 blocked，而不是 synthetic approve。

A2 的证明边界仍然有限：selected test直接验证 application consumer与 PostgreSQL recovery；真实 production queue/worker transport、真实 Model/Tool Provider E2E、完整 owner gates和 Production Readiness没有因此成立。

## CXL-B relationship

PRD-A2 已关闭 CXL-B 原来的 canonical identity/start 上游 blocker：

```text
Product cancel token                         CURRENT
Runtime/Tool cancellation primitives         CURRENT
PRD-A1 durable RuntimeExecutionSpec           CURRENT / SELECTED VERIFIED
PRD-A2 canonical runtime identity/start       CURRENT / SELECTED VERIFIED
CXL-B cancel -> same live canonical run       READY FOR IMPLEMENTATION / NOT IMPLEMENTED
```

现在 CXL-B 可以使用 Product receipt里的 stable canonical task/run identity，把已有 cancel token映射到同一个 04 Runtime cancellation boundary；仍不允许 action consumer直接写 ToolCancellationReceipt绕过 Runtime，也不因为 A2完成就假定 provider cancel capability存在。

## Non-claims

本状态只证明 selected Product dispatch consumer能够以 stable durable identity到达 server-owned canonical runtime并在 response-loss/redelivery下恢复。它不表示 production queue/worker transport已单独 E2E qualification、Budget owner admission或新 Product Approval flow已实现、CXL-B 已闭环，或 Full CI / 真实 Provider E2E / Production Readiness 已建立。
