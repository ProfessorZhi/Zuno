# Model Gateway Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-MODEL-001` 到 `ARCH-MODEL-052`

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
- 已证明 Embedding 固定 Revision、Dimension、Normalization 和 Index Generation，并支持 batch item 级终态和部分失败。
- 已证明 Rerank 保留 Item ID、Score 和批量 rank 语义。
- 已证明 Vision/OCR 保留页码、坐标和 Source Lineage。
- 已证明 Transcription 保留 Segment、Timestamp 和 Partial 语义。
- 已证明 Classification 支持 Threshold、Calibration 和 Abstain。
- 已证明 Judge 调用通过 Gateway budget audit，且 Judge result 不能作为唯一质量证明。
- 已证明 Context Compression 保留 Lineage、约束、冲突和失真风险。
- 已证明 Memory 模型输出只能形成 `ModelOutputCandidate`，不能直接 commit。
- 已证明 Security 模型输出只能形成 `ModelRiskProposal`，不能直接 enforce。
- 已证明 Tool 模型输出只能形成 `ModelActionProposal`，不能直接 execute。
- 已证明每个 Attempt 包括失败和 fallback 都产生 Usage 事实。
- 已证明 Usage Observed、Settled 和 Correction 分离，Correction 不回写历史 Receipt。
- 已证明 Pricing Version 固定在历史 Receipt 上，settle/correction 继承原 pricing version。
- 已证明 Quota 与业务 Budget 分离，Quota 通过 generation CAS 处理 race，并显式返回 quota exhausted。
- 已证明 Provider Health 基于窗口证据；无成功/失败证据或无 evidence ref 时状态为 `UNKNOWN`，不会默认为健康。
- 已证明 Circuit key 按 Provider、Model、Region、Operation 和 Adapter Version 隔离，健康窗口只影响同 key circuit。
- 已证明 Capability 生命周期支持 `DEGRADED`、`STALE` 和 `REVOKED`，撤销能力禁止 dispatch，异常状态需要 operator review。
- 已证明 Adapter Conformance Suite 按 Operation-specific 生成，Generate 与 Embed 不共享 conformance hash。
- 已证明 SDK/API version 或 Model Mapping version 变化会使既有 Conformance Verdict 失效并要求重验。
- 已证明未知 Provider enum/event/error signal fail closed，不能默认为 success。
- 已证明 Gateway Config Snapshot 使用 canonical JSON 内容寻址，版本和 generation 一起固定 snapshot id。
- 已证明 Config Activation 必须经过 Validation、Replay、Canary、CAS 和 Rollback snapshot gate，generation mismatch 不会激活。
- 已证明每个 Call 可以绑定不可变 Config Snapshot，保留 snapshot id、version 和 content hash。
- 已证明 Provider/Model 生命周期覆盖 Probe、Enable、Deprecate、Drain、Disable 和 Retire，Drain/Disable/Retire 不接受新 dispatch。
- 已证明 Emergency Disable 阻止新 dispatch，并为迟到结果生成 quarantine ref。
- 已证明 Retirement 保留历史 Attempt、Usage 和 Audit 语义，不删除历史记录。
- 已证明 Gateway 源文件不直接导入 OpenAI/Anthropic Provider SDK。

未覆盖：

- `ARCH-MODEL-053` 以后仍需后续批次证明。

验证命令：

```powershell
python tools/scripts/verify_model_gateway_runtime_batch.py
pytest -q tests/platform/test_model_gateway.py -p no:cacheprovider
pytest -q tests/platform/test_model_gateway.py tests/evals/test_model_gateway_cost_latency.py tests/agent/runtime/test_runtime_real_execution.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
```

结果：

```text
Model Gateway runtime batch verification passed for ARCH-MODEL-001, ARCH-MODEL-002, ARCH-MODEL-003, ARCH-MODEL-004, ARCH-MODEL-005, ARCH-MODEL-006, ARCH-MODEL-007, ARCH-MODEL-008, ARCH-MODEL-009, ARCH-MODEL-010, ARCH-MODEL-011, ARCH-MODEL-012, ARCH-MODEL-013, ARCH-MODEL-014, ARCH-MODEL-015, ARCH-MODEL-016, ARCH-MODEL-017, ARCH-MODEL-018, ARCH-MODEL-019, ARCH-MODEL-020, ARCH-MODEL-021, ARCH-MODEL-022, ARCH-MODEL-023, ARCH-MODEL-024, ARCH-MODEL-025, ARCH-MODEL-026, ARCH-MODEL-027, ARCH-MODEL-028, ARCH-MODEL-029, ARCH-MODEL-030, ARCH-MODEL-031, ARCH-MODEL-032, ARCH-MODEL-033, ARCH-MODEL-034, ARCH-MODEL-035, ARCH-MODEL-036, ARCH-MODEL-037, ARCH-MODEL-038, ARCH-MODEL-039, ARCH-MODEL-040, ARCH-MODEL-041, ARCH-MODEL-042, ARCH-MODEL-043, ARCH-MODEL-044, ARCH-MODEL-045, ARCH-MODEL-046, ARCH-MODEL-047, ARCH-MODEL-048, ARCH-MODEL-049, ARCH-MODEL-050, ARCH-MODEL-051, ARCH-MODEL-052.
17 passed in 23.40s
27 passed in 27.72s
```
