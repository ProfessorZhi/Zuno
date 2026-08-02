# Goal05 PHASE22 Runtime, Credential, Reviewer and Approval Attestation Contract Evidence

日期：2026-08-02

## 结论

本证据记录 PHASE22 benchmark preflight 的 Product Runtime attestation、Formal Credential attestation、Reviewer attestation、Formal Execution approval attestation 与 Human Budget approval attestation 契约修复。

`product_runtime_attested=true` 现在不再足以通过 Runtime gate。每个 canonical profile 必须同时提供序列化的 `product_runtime_attestation`，并绑定 profile、runtime、snapshot、security epoch、formal adapter ref 和 canonical hash。缺失、类型错误、版本不一致、hash 不一致或绑定字段不一致均 fail-closed。

`credential_ref` + `has_formal_credentials=true` + `formal_execution_requested=true` 现在不再足以通过 Credentials gate。preflight 顶层必须同时提供序列化的 `formal_credential_attestation`，并绑定 eval run、credential ref、authorization ref、security epoch、formal execution ref 和 canonical hash。该 attestation 不包含 secret value。

`reviewer_status=approved` + `benchmark_eligible=true` 现在不再足以通过 Governance gate。preflight 顶层必须同时提供序列化的 `reviewer_attestation`，并绑定 eval run、case set、dataset version/hash、candidate count、reviewer status、benchmark eligibility 和 canonical hash。

`formal_execution_approved=true` 和 `human_budget_approved=true` 现在不再足以通过 Security / Budget gate。preflight 顶层必须同时提供序列化的 `formal_execution_attestation` 与 `human_budget_attestation`，并分别绑定 authorization/security epoch/formal execution request 与 budget policy/cost/token/deadline 的 canonical hash。

该修复证明两件事：

1. preflight 不再接受裸布尔声明；
2. canonical adapter 在 `runtime_evidence_binding` 已验证并达到 `RUNTIME_OBSERVED` 时，会把 profile 级 `product_runtime_attestation` 写入 benchmark metrics，供 preflight v7 复验；
3. MeasurementTruthGate 不再接受裸 reviewer approval / benchmark eligibility 声明进入 `MEASURED`；
4. preflight 不再接受裸 formal execution approval 或 human budget approval 声明进入 `READY`。

该路径仍不声明 fixed benchmark measured，不声明 quality proven，不声明 production ready。

## 代码边界

- `tools/evals/zuno/rag_eval/benchmark_preflight.py`
  - preflight contract 升级为 `phase22-benchmark-preflight.v8`；
  - 新增 `PRODUCT_RUNTIME_ATTESTATION_VERSION = "phase22-product-runtime-attestation.v1"`；
  - 新增 `FORMAL_CREDENTIAL_ATTESTATION_VERSION = "phase22-formal-credential-attestation.v1"`；
  - 新增 `REVIEWER_ATTESTATION_VERSION = "phase22-reviewer-attestation.v1"`；
  - 新增 `FORMAL_EXECUTION_ATTESTATION_VERSION = "phase22-formal-execution-attestation.v1"`；
  - 新增 `HUMAN_BUDGET_ATTESTATION_VERSION = "phase22-human-budget-attestation.v1"`；
  - `ProfilePreflightInput` 新增 `product_runtime_attestation`；
  - Runtime gate 校验 serialized attestation；
  - Credentials gate 校验 serialized `formal_credential_attestation`；
  - Governance gate 校验 serialized `reviewer_attestation`；
  - Security gate 校验 serialized `formal_execution_attestation`；
  - Budget gate 校验 serialized `human_budget_attestation`；
  - attestation hash 使用 canonical JSON SHA-256，排除 `attestation_hash` 字段自身；
  - attestation mismatch 不覆盖原 Owner gate：例如 profile security epoch 缺失仍由 Security gate 报 `profile_security_epoch_missing`。
- `tools/evals/zuno/rag_eval/canonical_profile_runners.py`
  - `CanonicalCaseResult` 新增 `product_runtime_attestation`；
  - `build_product_runtime_attestation(...)` 从已验证的 runtime evidence binding 生成 serialized attestation。
- `tools/evals/zuno/rag_eval/adapters/retrieval.py`
  - Standard / Local adapter 在 `RUNTIME_OBSERVED` 结果中写入 attestation。
- `tools/evals/zuno/rag_eval/adapters/deep_agentic.py`
  - Deep / Agentic adapter 在 `RUNTIME_OBSERVED` 结果中写入 attestation。
- `tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py`
  - canonical profile metrics 传播首个非空 `product_runtime_attestation`，并写入 `product_runtime_attested`。
- `tools/evals/zuno/rag_eval/measurement_gate.py`
  - MeasurementTruthGate 的 formal gate 增加 `formal_credential_attested`；
  - MeasurementTruthGate 的 formal gate 增加 `reviewer_attested`；
  - `reviewer_status=approved`、`benchmark_eligible=true`、`has_formal_credentials=true`、`formal_execution_requested=true` 不再足以进入 `MEASURED`；
  - 缺少 formal credential attestation 或 reviewer attestation 时只能进入 `RUNTIME_OBSERVED`，reason 分别包含 `formal_credential_attestation_missing` 或 `reviewer_attestation_missing`。

## 验证

```powershell
python -m pytest -q tests/evals/test_phase22_benchmark_preflight.py tests/evals/test_phase22_measurement_control_contracts.py tests/evals/test_canonical_profile_runners.py tests/evals/test_canonical_deep_agentic_runtime.py tests/repo/test_phase22_completion_blockers.py tests/repo/test_phase22_eval_package_contract.py -p no:cacheprovider --tb=short
```

结果：`208 passed, 30 subtests passed`。

Repository verifier：

```powershell
python tools/scripts/verify_current_program.py
python tools/scripts/verify_phase22_completion_blockers.py
python tools/scripts/verify_docs_entrypoints.py
git diff --check
```

结果：Current Program、PHASE22 completion blocker、documentation entrypoint 和 diff whitespace checks 均通过。

## 剩余未完成

- 仍缺正式四 profile runtime 全量 measured 结果；
- Formal credentials / formal execution approval 仍未由真实外部凭证系统和正式执行审批完成；当前只是 preflight attestation contract；
- Reviewer-approved benchmark case set 仍未完成；
- Fixed benchmark 仍未达到 `MEASURED`；
- PHASE22 仍为 `in_progress`，Program 不能归档。
