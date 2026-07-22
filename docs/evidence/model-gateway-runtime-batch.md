# Model Gateway Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-MODEL-001` 到 `ARCH-MODEL-088`

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
- 已证明 Admission 覆盖 Global、Provider、Model、Operation 和 Role 五层容量检查。
- 已证明 Admission 支持租户公平限制、Reserved Capacity 和基于等待时长的防饥饿放行。
- 已证明排队请求保留 Deadline、Security Epoch、Budget Verdict 和不可变 Config Snapshot 绑定。
- 已证明 Overload 有显式 `NORMAL`、`BACKPRESSURE` 和 `LOAD_SHEDDING` 状态。
- 已证明 Overload/Load Shedding 不允许绕过 Security、Validation、Usage、Audit 和 Budget gate。
- 已证明 Provider Prompt Cache、Metadata Cache 和 Result Cache 使用独立 namespace/key。
- 已证明 Result Cache 默认关闭，并按 Tenant、Config、Schema、Model、Adapter 和 Security Epoch 版本隔离。
- 已证明 Cache Hit 产生 `ModelCacheReuseReceipt`，且不产生 Provider Attempt。
- 已证明 Revocation、Deletion、Model Retirement 和 Validity 变化均生成 Cache Tombstone 并失效 Cache。
- 已证明所有运维状态变化通过版本化 `ModelOperationalCommand` 表达，并以 expected generation 提交。
- 已证明高风险 Operational Command 必须具备 Authorization、Approval、Expected Generation 和 Audit。
- 已证明 Prompt、Response、Stream、Usage、Failure 和 Decision 均独立绑定 Retention Policy。
- 已证明 Delete 必须按 Tombstone、Visibility Revocation、Physical Cleanup、Verification 顺序推进，缺少 visibility revocation 时禁止物理清理。
- 已证明 Legal Hold 优先于物理删除，但不恢复业务可见性。
- 已证明 SLI/SLO 维度区分 Call、Attempt、Operation、Role、Tenant、Provider 和 Config。
- 已证明 Readiness 覆盖 Adapter、Security、Persistence、Usage、Reconcile、Capacity 和删除证据。
- 已证明无证据或 Mock-only Readiness 不得标记为 READY。
- 已证明 Adapter/API/SDK rollout 支持 Parallel、Canary、Drain 和 Rollback。
- 已证明 Provider API Sunset 保留 Migration、Rollback 和 Compatibility evidence。
- 已证明 Experiment 必须在 Security、Capability、Budget 和 Deadline Gate 之后。
- 已证明 Experiment Assignment 可复现并支持 Sticky Scope。
- 已证明 Shadow Call 独立记录 Security、Budget、Usage、Trace 和 Retention。
- 已证明 Shadow Result 不进入业务输出。
- 已证明 ResultValidity 变化事件化，并由事实 Owner 决定是否传播。
- 已证明 Provider-neutral Failure Code 稳定，并保留原始错误引用。
- 已证明 Suggested Control Action 不能替代 Agent Core 决策。
- 已证明 Domain Event 版本化、幂等、可排序、可重放并脱敏。
- 已证明 Trace、Audit、Eval Projection 不替代 Gateway 源事实。
- 已证明 Model Gateway Ownership Boundary 不允许跨 Owner 写。
- 已证明跨模块请求和事件使用版本化 Envelope。
- 已证明 PostgreSQL Domain Fact、Object Payload 和 Projection 分层。
- 已证明兼容 facade 具备旁路清单、禁止新增旁路和迁移期限。
- 已证明 Migration Integrity Gate 不允许伪造历史版本、Usage 或实现状态。
- 已证明未知安全枚举、未知终态和未知事件 fail closed 或 quarantine。
- 已证明高风险故障必须具备 Fault Injection 和恢复证据。
- 已证明 Target 转 Current 必须具备代码、Migration、测试、Trace、Eval 和运行证据引用。
- 已证明 Gateway 源文件不直接导入 OpenAI/Anthropic Provider SDK；Provider SDK 只存在 `src/backend/zuno/platform/model_gateway_adapters.py` adapter 边界。

未覆盖：

- Model Gateway 模块 `ARCH-MODEL-001` 到 `ARCH-MODEL-088` 已由本批 evidence 覆盖；PHASE07 closure 仍由独立 Pre-Closure Gate、Coordinator Decision 和 Post-Closure Gate 决定。

验证命令：

```powershell
python tools/scripts/verify_model_gateway_runtime_batch.py
python tools/scripts/verify_model_gateway_bypass.py --strict
pytest -q tests/platform/test_model_gateway.py -p no:cacheprovider
pytest -q tests/platform/test_model_gateway.py tests/evals/test_model_gateway_cost_latency.py tests/agent/runtime/test_runtime_real_execution.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
```

结果：

```text
Model Gateway runtime batch verification passed for ARCH-MODEL-001, ARCH-MODEL-002, ARCH-MODEL-003, ARCH-MODEL-004, ARCH-MODEL-005, ARCH-MODEL-006, ARCH-MODEL-007, ARCH-MODEL-008, ARCH-MODEL-009, ARCH-MODEL-010, ARCH-MODEL-011, ARCH-MODEL-012, ARCH-MODEL-013, ARCH-MODEL-014, ARCH-MODEL-015, ARCH-MODEL-016, ARCH-MODEL-017, ARCH-MODEL-018, ARCH-MODEL-019, ARCH-MODEL-020, ARCH-MODEL-021, ARCH-MODEL-022, ARCH-MODEL-023, ARCH-MODEL-024, ARCH-MODEL-025, ARCH-MODEL-026, ARCH-MODEL-027, ARCH-MODEL-028, ARCH-MODEL-029, ARCH-MODEL-030, ARCH-MODEL-031, ARCH-MODEL-032, ARCH-MODEL-033, ARCH-MODEL-034, ARCH-MODEL-035, ARCH-MODEL-036, ARCH-MODEL-037, ARCH-MODEL-038, ARCH-MODEL-039, ARCH-MODEL-040, ARCH-MODEL-041, ARCH-MODEL-042, ARCH-MODEL-043, ARCH-MODEL-044, ARCH-MODEL-045, ARCH-MODEL-046, ARCH-MODEL-047, ARCH-MODEL-048, ARCH-MODEL-049, ARCH-MODEL-050, ARCH-MODEL-051, ARCH-MODEL-052, ARCH-MODEL-053, ARCH-MODEL-054, ARCH-MODEL-055, ARCH-MODEL-056, ARCH-MODEL-057, ARCH-MODEL-058, ARCH-MODEL-059, ARCH-MODEL-060, ARCH-MODEL-061, ARCH-MODEL-062, ARCH-MODEL-063, ARCH-MODEL-064, ARCH-MODEL-065, ARCH-MODEL-066, ARCH-MODEL-067, ARCH-MODEL-068, ARCH-MODEL-069, ARCH-MODEL-070, ARCH-MODEL-071, ARCH-MODEL-072, ARCH-MODEL-073, ARCH-MODEL-074, ARCH-MODEL-075, ARCH-MODEL-076, ARCH-MODEL-077, ARCH-MODEL-078, ARCH-MODEL-079, ARCH-MODEL-080, ARCH-MODEL-081, ARCH-MODEL-082, ARCH-MODEL-083, ARCH-MODEL-084, ARCH-MODEL-085, ARCH-MODEL-086, ARCH-MODEL-087, ARCH-MODEL-088.
Model Gateway bypass strict verification passed.
42 passed in 35.02s
```
