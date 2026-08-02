# Goal05 PHASE22 Runtime and Credential Attestation Contract Evidence

日期：2026-08-02

## 结论

本证据记录 PHASE22 benchmark preflight 的 Product Runtime attestation 与 Formal Credential attestation 契约修复。

`product_runtime_attested=true` 现在不再足以通过 Runtime gate。每个 canonical profile 必须同时提供序列化的 `product_runtime_attestation`，并绑定 profile、runtime、snapshot、security epoch、formal adapter ref 和 canonical hash。缺失、类型错误、版本不一致、hash 不一致或绑定字段不一致均 fail-closed。

`credential_ref` + `has_formal_credentials=true` + `formal_execution_requested=true` 现在不再足以通过 Credentials gate。preflight 顶层必须同时提供序列化的 `formal_credential_attestation`，并绑定 eval run、credential ref、authorization ref、security epoch、formal execution ref 和 canonical hash。该 attestation 不包含 secret value。

该修复证明两件事：

1. preflight 不再接受裸布尔声明；
2. canonical adapter 在 `runtime_evidence_binding` 已验证并达到 `RUNTIME_OBSERVED` 时，会把 profile 级 `product_runtime_attestation` 写入 benchmark metrics，供 preflight v6 复验。

该路径仍不声明 fixed benchmark measured，不声明 quality proven，不声明 production ready。

## 代码边界

- `tools/evals/zuno/rag_eval/benchmark_preflight.py`
  - preflight contract 升级为 `phase22-benchmark-preflight.v6`；
  - 新增 `PRODUCT_RUNTIME_ATTESTATION_VERSION = "phase22-product-runtime-attestation.v1"`；
  - 新增 `FORMAL_CREDENTIAL_ATTESTATION_VERSION = "phase22-formal-credential-attestation.v1"`；
  - `ProfilePreflightInput` 新增 `product_runtime_attestation`；
  - Runtime gate 校验 serialized attestation；
  - Credentials gate 校验 serialized `formal_credential_attestation`；
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

## 验证

```powershell
python -m pytest -q tests/evals/test_phase22_benchmark_preflight.py tests/evals/test_phase22_measurement_control_contracts.py -p no:cacheprovider --tb=short
```

结果：`135 passed, 30 subtests passed`。

## 剩余未完成

- 仍缺正式四 profile runtime 全量 measured 结果；
- Formal credentials / formal execution approval 仍未由真实外部凭证系统和正式执行审批完成；当前只是 preflight attestation contract；
- Reviewer-approved benchmark case set 仍未完成；
- Fixed benchmark 仍未达到 `MEASURED`；
- PHASE22 仍为 `in_progress`，Program 不能归档。
