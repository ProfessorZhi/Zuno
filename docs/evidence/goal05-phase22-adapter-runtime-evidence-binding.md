# Goal05 PHASE22 Adapter Runtime Evidence Binding 接线证据

## 结论

本切片修复 PHASE22 canonical benchmark 的两个默认路径缺口：

1. Standard / Local retrieval canonical adapter 原先只消费 runtime payload，不校验 `runtime_evidence_binding`；
2. canonical benchmark 聚合函数原先把所有 canonical profile 结果强行写成 `BLOCKED`，即使 adapter 返回 `RUNTIME_OBSERVED` 也会被压平。

修复后：

- Standard / Local retrieval adapters 在 payload 带 `runtime_evidence_binding` 时调用 `RuntimeEvidenceBindingValidator`；
- binding 为 `VALID` 后仍必须经过 `MeasurementTruthGate`；
- 当前 reviewer / benchmark eligible / formal credentials / formal execution request 未满足，因此最多进入 `RUNTIME_OBSERVED`；
- binding 为 `BLOCKED` / `INVALID` / `INCOMPARABLE` 时 fail-closed，返回固定 failure class `runtime_evidence_binding_blocked` 和 validator gap codes；
- canonical benchmark 聚合保留每个 profile 的 `runtime_status` 与 `measurement_state`，不再把 `RUNTIME_OBSERVED` 压成 `BLOCKED`；
- 顶层 benchmark 仍保持 `blocked_not_measured`，不声明 fixed benchmark measured、quality proven 或 production ready。

## 代码证据

- `tools/evals/zuno/rag_eval/adapters/retrieval.py`
  - Standard / Local adapter normalization path 校验 `runtime_evidence_binding`；
  - VALID binding 进入 `MeasurementTruthGate`；
  - invalid binding fail-closed。
- `tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py`
  - canonical profile aggregation 保留 adapter 返回的 `runtime_status` / `measurement_state`。
- `tests/evals/test_canonical_profile_runners.py`
  - `test_09d_standard_adapter_validates_runtime_evidence_binding_to_observed_not_measured`；
  - `test_09e_standard_adapter_invalid_runtime_evidence_binding_fails_closed`；
  - `test_06c_canonical_benchmark_preserves_runtime_observed_profile_state`。

## 验证命令

```powershell
python -m pytest -q tests/evals/test_canonical_profile_runners.py tests/evals/test_runtime_evidence_binding.py tests/evals/test_phase22_measurement_control_contracts.py tests/evals/test_canonical_deep_agentic_runtime.py tests/integration/evals/test_canonical_deep_agentic_integration.py tests/repo/test_phase22_eval_package_contract.py tests/repo/test_phase22_completion_blockers.py -p no:cacheprovider --tb=short
python -m py_compile tools/evals/zuno/rag_eval/adapters/retrieval.py tools/evals/zuno/rag_eval/adapters/deep_agentic.py tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py tests/evals/test_canonical_profile_runners.py
```

## 边界

本证据不关闭 PHASE22。

仍未完成：

- Deep / Agentic adapter-side runtime evidence binding validation；
- Product Runtime attestation；
- formal credentials / formal execution approval；
- public benchmark human review 与 eligible case；
- 四 profile measured runtime；
- full final verification、Production Readiness 决策和 Program archive。
