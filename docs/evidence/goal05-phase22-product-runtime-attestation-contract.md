# Goal05 PHASE22 Product Runtime Attestation Contract Evidence

日期：2026-08-02

## 结论

本证据记录 PHASE22 benchmark preflight 的 Product Runtime attestation 契约修复。

`product_runtime_attested=true` 现在不再足以通过 Runtime gate。每个 canonical profile 必须同时提供序列化的 `product_runtime_attestation`，并绑定 profile、runtime、snapshot、security epoch、formal adapter ref 和 canonical hash。缺失、类型错误、版本不一致、hash 不一致或绑定字段不一致均 fail-closed。

该修复证明两件事：

1. preflight 不再接受裸布尔声明；
2. canonical adapter 在 `runtime_evidence_binding` 已验证并达到 `RUNTIME_OBSERVED` 时，会把 profile 级 `product_runtime_attestation` 写入 benchmark metrics，供 preflight v5 复验。

该路径仍不声明 fixed benchmark measured，不声明 quality proven，不声明 production ready。

## 代码边界

- `tools/evals/zuno/rag_eval/benchmark_preflight.py`
  - preflight contract 升级为 `phase22-benchmark-preflight.v5`；
  - 新增 `PRODUCT_RUNTIME_ATTESTATION_VERSION = "phase22-product-runtime-attestation.v1"`；
  - `ProfilePreflightInput` 新增 `product_runtime_attestation`；
  - Runtime gate 校验 serialized attestation；
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
python -m pytest -q tests/evals/test_canonical_profile_runners.py tests/evals/test_canonical_deep_agentic_runtime.py tests/evals/test_phase22_benchmark_preflight.py tests/evals/test_phase22_measurement_control_contracts.py -p no:cacheprovider --tb=short
```

结果：`181 passed, 30 subtests passed`。

## 剩余未完成

- 仍缺正式四 profile runtime 全量 measured 结果；
- Formal credentials、formal execution approval 和 reviewer-approved benchmark case set 仍未完成；
- Fixed benchmark 仍未达到 `MEASURED`；
- PHASE22 仍为 `in_progress`，Program 不能归档。
