# Goal05 PHASE22 Profile-aware Measurement Gate 证据

## 结论

本切片修复 PHASE22 measurement control 的一个合同不一致：

- `runtime_evidence_binding.py` 明确规定 `standard_rag`、`local_graphrag`、`deep_graphrag` 的 required receipts 为 `security_decision`、`trace`、`usage_receipt`、`budget_settlement`、`artifact_receipt`；
- `agentic_graphrag` 额外要求 `plan_version` 与 `run_outcome`；
- 但 `MeasurementTruthGate` 之前对所有 profile 都强制 `run_outcome_ref`，导致非 Agentic RAG profile 即使拥有合法 binding 所需 receipts，也会被错误挡在 `runtime_evidence_incomplete:run_outcome_missing`。

修复后：

- `agentic_graphrag` 仍强制 `run_outcome_ref` 与 `run_outcome_valid`；
- `standard_rag`、`local_graphrag`、`deep_graphrag` 不再强制 Agent Core `RunOutcome` receipt；
- 非 Agentic profile 在 snapshot、trace、budget settlement 和 artifact receipt 均有效时，可进入 Rule 6：`RUNTIME_OBSERVED`；
- reviewer approval、benchmark eligibility、formal credentials 和 formal execution request 仍会阻止 `MEASURED`；
- fake receipt strings 和 invalid receipt validation 仍保持 `BLOCKED`。

## 代码证据

- `tools/evals/zuno/rag_eval/measurement_gate.py`
  - `RunOutcome` validation 改为只对 `actual_profile == "agentic_graphrag"` 强制执行。
- `tests/evals/test_canonical_profile_runners.py`
  - `test_21b_standard_rag_does_not_require_agent_run_outcome_for_rule6` 验证 Standard RAG 与 runtime evidence binding 的 required receipts 对齐；
  - `test_20_run_outcome_invalid_blocked` 显式覆盖 Agentic profile 的 run outcome invalid 仍 blocked；
  - `test_22_fake_receipt_strings_cannot_reach_measured` 继续防止 fake receipt 进入 measured。

## 验证命令

```powershell
python -m pytest -q tests/evals/test_canonical_profile_runners.py tests/evals/test_runtime_evidence_binding.py tests/evals/test_phase22_measurement_control_contracts.py tests/repo/test_phase22_completion_blockers.py -p no:cacheprovider --tb=short
python -m py_compile tools/evals/zuno/rag_eval/measurement_gate.py tests/evals/test_canonical_profile_runners.py
```

## 边界

本证据不关闭 PHASE22，也不声明 fixed benchmark measured。

仍未完成：

- adapter 对 runtime evidence binding 的执行后绑定与校验接线；
- Product Runtime attestation；
- formal credentials / formal execution approval；
- public benchmark human review 与 eligible case；
- 四 profile measured runtime；
- full final verification、Production Readiness 决策和 Program archive。
