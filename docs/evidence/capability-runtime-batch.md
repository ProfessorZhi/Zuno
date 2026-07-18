# Capability Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-CAP-001` 到 `ARCH-CAP-080`

范围说明：

- 已证明 Capability / Skill 只拥有业务能力语义、方法包、版本目录、可用性快照和选择治理，不执行 Tool，不提交其他模块事实。
- 已证明 Capability、Skill、Tool、Function Calling、MCP、API、CLI、Provider 和治理对象保持独立 taxonomy。
- 已证明模型输出只能形成 proposal，未知 version/enum/hash/generation/tenant/security context fail closed 或 quarantine。
- 已证明 CrossModuleEnvelopeV1 带版本、payload hash、tenant、trace 和 security epoch。
- 已证明 SkillVersion 不可变，结构化保存 Metadata、Instruction、ResourceManifest、CapabilityRequirement 和 AcceptanceCriteria。
- 已证明 Skill discovery metadata-only，Skill load 固定版本、资源 hash、load policy 和 budget。
- 已证明 Skill resource 按类型、数据等级、完整性、来源和可执行性分类，脚本不得由 loader 直接执行。
- 已证明 allowed_tools/allowed_capabilities 只能缩小候选，外部 skill 需要签名、完整性、策略和风险校验。
- 已证明 CapabilityDefinition 使用稳定业务语义身份，CapabilityVersion 固定 input/output schema、风险、依赖、兼容和验收语义。
- 已证明 Binding 只能经确定性治理 gate 激活，model-only proposal 不得 active。
- 已证明 ProviderConformanceRecord 覆盖输入、输出、副作用、幂等、Reconciliation、安全和错误语义。
- 已证明 Tool 名称不作为 Capability 等价依据，Provider failure domain 记录 family、backend、quota 和 effect domain。
- 已证明 Connector Pack 激活后拆分为 provider definition、tool manifest、capability mapping、scope mapping、contract test 和 reconciliation extension。
- 已证明 Availability Snapshot 不可变、版本化、带 TTL 和 source generation。
- 已证明 AVAILABLE 仅表示候选，不推断 authorization、approval 或 execution readiness，并覆盖全部 availability status。
- 已证明 SelectionResult 记录候选、硬过滤、评分、binding、instance/pool 和 fallback order，最终 commit 确定性执行。
- 已证明 StepFeasibility 仍归 Agent Core，Capability 只提供 requirement、snapshot、selection 和未满足约束。
- 已证明 fallback candidate 保持 output contract、风险上限、tenant、data residency 和 side-effect 语义。
- 已证明 Skill/Capability version range 解析为精确版本，Plan/Prepared action 固定 capability、binding、tool definition 和 schema hash。
- 已证明 inventory generation 变化触发 tool definition version 和 binding revalidation，不允许 schema 原地修改。
- 已证明 deprecated/revoked/unknown version、plan mutation boundary、result validity 和 reuse guard 语义。
- 已证明 ProviderInstance、CredentialScope 和 CapabilityConstraint 不混合，07 不保存 secret/token/credential material。
- 已证明 Constraint 包含 tenant、workspace、region、data residency、identity mode、resource scope 和 provider trust。
- 已证明 Security policy 优先于 Skill instruction，side-effect class 与 08/09 对齐，model visibility 最小披露。
- 已证明 mandatory audit requirement 在 selection 中传播，persistence receipt 属于 11，audit event 属于 10。
- 已证明 PostgreSQL domain facts、Object Store payload refs、Projection refs 分层，Projection 不成为事实源。
- 已证明 publish、active pointer、transition、selection 和 outbox 原子事务边界。
- 已证明状态转换使用 expected generation/CAS 并产生 transition record。
- 已证明 outbox at-least-once，consumer 以 event_id 幂等。
- 已证明 crash recovery 覆盖 resource commit、version publish、active switch、snapshot build 和 revocation propagation，并有 reconciler、claim、fencing 和 human escalation。
- 已证明时间敏感语义通过 generation/TTL/ref 记录，运行耗时不作为领域事实。
- 已证明核心代码无 provider-specific branch，只暴露通用 adapter families。
- 已证明 CLI 操作需要结构化 manifest，OpenAPI/MCP/CLI discovery 只生成 draft proposal。
- 已证明 custom extension 仅限声明式 mapping 不足场景，多 provider fallback 不把同源 backend 冒充独立容灾。
- 已证明 UNKNOWN side-effect retry forbidden before Tool Runtime reconciliation。
- 已证明 Discovery、Load、Binding、Availability、Selection、Fallback 和 Revocation Trace/Event 均结构化、脱敏并可 hash。
- 已证明 Target 转 Current 必须具备代码、Migration、Unit、Integration、Fault、E2E、Trace、Eval 和运行证据引用。

未覆盖：

- Capability / Skill 模块 `ARCH-CAP-001` 到 `ARCH-CAP-080` 已由本批 evidence 覆盖；其他模块仍需后续批次证明。

验证命令：

```powershell
python tools/scripts/verify_capability_runtime_batch.py
pytest -q tests/capability/test_capability_runtime_batch.py tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
```

结果：

```text
Capability runtime batch verification passed for ARCH-CAP-001, ARCH-CAP-002, ARCH-CAP-003, ARCH-CAP-004, ARCH-CAP-005, ARCH-CAP-006, ARCH-CAP-007, ARCH-CAP-008, ARCH-CAP-009, ARCH-CAP-010, ARCH-CAP-011, ARCH-CAP-012, ARCH-CAP-013, ARCH-CAP-014, ARCH-CAP-015, ARCH-CAP-016, ARCH-CAP-017, ARCH-CAP-018, ARCH-CAP-019, ARCH-CAP-020, ARCH-CAP-021, ARCH-CAP-022, ARCH-CAP-023, ARCH-CAP-024, ARCH-CAP-025, ARCH-CAP-026, ARCH-CAP-027, ARCH-CAP-028, ARCH-CAP-029, ARCH-CAP-030, ARCH-CAP-031, ARCH-CAP-032, ARCH-CAP-033, ARCH-CAP-034, ARCH-CAP-035, ARCH-CAP-036, ARCH-CAP-037, ARCH-CAP-038, ARCH-CAP-039, ARCH-CAP-040, ARCH-CAP-041, ARCH-CAP-042, ARCH-CAP-043, ARCH-CAP-044, ARCH-CAP-045, ARCH-CAP-046, ARCH-CAP-047, ARCH-CAP-048, ARCH-CAP-049, ARCH-CAP-050, ARCH-CAP-051, ARCH-CAP-052, ARCH-CAP-053, ARCH-CAP-054, ARCH-CAP-055, ARCH-CAP-056, ARCH-CAP-057, ARCH-CAP-058, ARCH-CAP-059, ARCH-CAP-060, ARCH-CAP-061, ARCH-CAP-062, ARCH-CAP-063, ARCH-CAP-064, ARCH-CAP-065, ARCH-CAP-066, ARCH-CAP-067, ARCH-CAP-068, ARCH-CAP-069, ARCH-CAP-070, ARCH-CAP-071, ARCH-CAP-072, ARCH-CAP-073, ARCH-CAP-074, ARCH-CAP-075, ARCH-CAP-076, ARCH-CAP-077, ARCH-CAP-078, ARCH-CAP-079, ARCH-CAP-080.
25 passed in 56.60s
```
