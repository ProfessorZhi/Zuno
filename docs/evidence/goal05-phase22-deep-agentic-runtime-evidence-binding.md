# Goal05 PHASE22 Deep / Agentic Runtime Evidence Binding 接线证据

## 结论

本切片补齐 PHASE22 canonical benchmark adapter-side evidence binding 的剩余 profile 缺口：

- Deep GraphRAG adapter 在 runtime payload 带 `runtime_evidence_binding` 时执行 `RuntimeEvidenceBindingValidator`；
- Agentic GraphRAG adapter 在 completed runtime payload 带 `runtime_evidence_binding` 时执行 `RuntimeEvidenceBindingValidator`；
- binding 为 `VALID` 后仍必须经过 `MeasurementTruthGate`；
- 当前 formal gate 未满足时最多进入 `RUNTIME_OBSERVED`，不会进入 `MEASURED`；
- binding 为 `BLOCKED` / `INVALID` / `INCOMPARABLE` 时 fail-closed，返回 `runtime_evidence_binding_blocked` 和固定 validator gap codes。

结合 `docs/evidence/goal05-phase22-adapter-runtime-evidence-binding.md`，Standard / Local / Deep / Agentic 四个 canonical boundary adapters 已具备 adapter-side runtime evidence binding validation。

## 代码证据

- `tools/evals/zuno/rag_eval/adapters/deep_agentic.py`
  - 新增 shared helper `_result_from_runtime_evidence_binding`；
  - Deep completed payload normalization 接入 binding validation；
  - Agentic completed payload normalization 接入 binding validation。
- `tests/evals/test_canonical_deep_agentic_runtime.py`
  - `test_unit_contract_deep_valid_runtime_evidence_binding_reaches_observed_not_measured`；
  - `test_unit_contract_deep_invalid_runtime_evidence_binding_fails_closed`；
  - `test_unit_contract_agentic_valid_runtime_evidence_binding_reaches_observed_not_measured`；
  - `test_unit_contract_agentic_invalid_runtime_evidence_binding_fails_closed`。

## 验证命令

```powershell
python -m pytest -q tests/evals/test_canonical_deep_agentic_runtime.py tests/integration/evals/test_canonical_deep_agentic_integration.py tests/evals/test_canonical_profile_runners.py tests/evals/test_runtime_evidence_binding.py tests/evals/test_phase22_measurement_control_contracts.py tests/repo/test_phase22_eval_package_contract.py tests/repo/test_phase22_completion_blockers.py -p no:cacheprovider --tb=short
python -m py_compile tools/evals/zuno/rag_eval/adapters/deep_agentic.py tests/evals/test_canonical_deep_agentic_runtime.py
```

## 边界

本证据不关闭 PHASE22。

仍未完成：

- Product Runtime attestation；
- formal credentials / formal execution approval；
- public benchmark human review 与 eligible case；
- 四 profile measured runtime；
- full final verification、Production Readiness 决策和 Program archive。
