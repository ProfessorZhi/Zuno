# Goal05 PHASE22 Product Runtime Attestation Contract Evidence

日期：2026-08-02

## 结论

本证据记录 PHASE22 benchmark preflight 的 Product Runtime attestation 契约修复。

`product_runtime_attested=true` 现在不再足以通过 Runtime gate。每个 canonical profile 必须同时提供序列化的 `product_runtime_attestation`，并绑定 profile、runtime、snapshot、security epoch、formal adapter ref 和 canonical hash。缺失、类型错误、版本不一致、hash 不一致或绑定字段不一致均 fail-closed。

该修复只证明 preflight 不再接受裸布尔声明；不生成 Product Runtime 运行证据，不声明 fixed benchmark measured，不声明 quality proven，不声明 production ready。

## 代码边界

- `tools/evals/zuno/rag_eval/benchmark_preflight.py`
  - preflight contract 升级为 `phase22-benchmark-preflight.v5`；
  - 新增 `PRODUCT_RUNTIME_ATTESTATION_VERSION = "phase22-product-runtime-attestation.v1"`；
  - `ProfilePreflightInput` 新增 `product_runtime_attestation`；
  - Runtime gate 校验 serialized attestation；
  - attestation hash 使用 canonical JSON SHA-256，排除 `attestation_hash` 字段自身；
  - attestation mismatch 不覆盖原 Owner gate：例如 profile security epoch 缺失仍由 Security gate 报 `profile_security_epoch_missing`。

## 验证

```powershell
python -m pytest -q tests/evals/test_phase22_benchmark_preflight.py -p no:cacheprovider --tb=short
```

结果：`126 passed, 30 subtests passed`。

## 剩余未完成

- Product Runtime attestation 仍未由真实四 profile runtime 自动产出；
- Formal credentials、formal execution approval 和 reviewer-approved benchmark case set 仍未完成；
- Fixed benchmark 仍未达到 `MEASURED`；
- PHASE22 仍为 `in_progress`，Program 不能归档。
