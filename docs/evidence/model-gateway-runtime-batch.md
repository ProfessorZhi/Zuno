# Model Gateway Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-MODEL-001` 到 `ARCH-MODEL-023`

范围说明：

- 已证明统一 `ModelGateway` 是 Agent Runtime 模型调用入口。
- 已证明 Role、Operation、Provider/Model、Config、Prompt、Schema、Adapter、Pricing、Security Epoch 在 `ModelGatewayBinding` 中不可变固定。
- 已证明 Dispatch 前 Budget Gate 阻止 Provider 调用。
- 已证明每个 Provider Dispatch 形成独立 `ModelAttemptReceipt`，同一 Call 只选择一个成功 Attempt。
- 已证明 Timeout 进入 `UNKNOWN_RECONCILE`，并在 fallback 前保留需对账状态。
- 已证明 Cancel-before-dispatch 不产生 Provider Attempt，但仍产生 Usage 事实。
- 已证明 Usage Estimate 与 Observed Receipt 分离，Receipt 不回写。
- 已证明 Structured Output 在本地 Schema 校验后才返回结构化结果。
- 已证明 Repair 保留原始输出 hash，并形成确定性 `ModelRepairRecord`。
- 已证明 Provider Stream Chunk、Gateway Stream Chunk 和 Product Stream Event 分层。
- 已证明 Gateway Stream Chunk 按 sequence 排序、去重、内容 hash 校验并保持 provisional 语义。
- 已证明 Provider 可能已执行的 Timeout 进入 `UNKNOWN_RECONCILE`，并产生独立 Reconcile control action。
- 已证明 Retry/Fallback、Repair、Escalation 和 Replan Proposal 是不同 `ModelControlAction`，且 Replan Proposal 归 Agent Core。
- 已证明 Gateway 对 PlanVersion activation 和 RunOutcome update 请求 fail closed，不修改 Agent Core 领域状态。
- 已证明 Gateway 源文件不直接导入 OpenAI/Anthropic Provider SDK。

未覆盖：

- `ARCH-MODEL-024` 以后仍需后续批次证明。

验证命令：

```powershell
python tools/scripts/verify_model_gateway_runtime_batch.py
pytest -q tests/platform/test_model_gateway.py -p no:cacheprovider
pytest -q tests/platform/test_model_gateway.py tests/evals/test_model_gateway_cost_latency.py tests/agent/runtime/test_runtime_real_execution.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
```

结果：

```text
Model Gateway runtime batch verification passed for ARCH-MODEL-001, ARCH-MODEL-002, ARCH-MODEL-003, ARCH-MODEL-004, ARCH-MODEL-005, ARCH-MODEL-006, ARCH-MODEL-007, ARCH-MODEL-008, ARCH-MODEL-009, ARCH-MODEL-010, ARCH-MODEL-011, ARCH-MODEL-012, ARCH-MODEL-013, ARCH-MODEL-014, ARCH-MODEL-015, ARCH-MODEL-016, ARCH-MODEL-017, ARCH-MODEL-018, ARCH-MODEL-019, ARCH-MODEL-020, ARCH-MODEL-021, ARCH-MODEL-022, ARCH-MODEL-023.
12 passed in 29.35s
```
