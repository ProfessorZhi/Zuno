# Goal03 Wave A Capability Progressive Loading Budget Evidence

status: partial_runtime_evidence
phase: PHASE14
commit_scope: Capability progressive loading budget and planner exposure guard

本文只证明本次 Wave A 新增的 PHASE14 纵切：默认 Capability Router 会为 Planner 生成受预算约束的 `planner_exposure`，并且只暴露授权摘要和 schema 级信息，不暴露 capability policy、dependency probe、credential 细节或旧 registry 整体对象。

## 已证明

- `CapabilityRouteRequest` 增加 `planner_context_budget_chars`，用于限制 Planner 可见暴露面。
- `CapabilityRouteDecision` 增加 `planner_exposure`，字段包含：
  - `visibility = planner_authorized_summary_schema_only`
  - `skill` 摘要
  - `capabilities` 摘要
  - `budget`
  - `omitted_capability_ids`
  - `exposure_ref`
- capability 暴露项只包含 `capability_id`、`capability_type`、`description`、`side_effect_level`，以及 tool 的 `input_schema` / `output_schema` / `schema_hash`。
- 暴露串行化结果不包含 `dependency_probe`、`required_roles`、`credential_policy` 或其他 policy / adapter 内部字段。
- 当预算不足时，后续 capability 会被确定性地加入 `omitted_capability_ids`，而不是扩大模型可见上下文。
- `StrategySelector` 将 `planner_exposure` 引用写入 `CapabilityPlan.risk_summary`，并在 trace 中保留 `planner_exposure_ref` 和 visibility 证据。

## 已运行验证

```powershell
python -m pytest -q tests/capability/test_capability_skill_layer.py tests/agent/test_planning_control_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
python tools/scripts/verify_capability_skill_target_protocols.py
git diff --check
```

结果：

```text
16 passed
4 passed
Capability / Skill target architecture verification passed.
```

## 未证明

- 这只证明 Planner 可见 exposure 受预算和摘要边界控制，不单独证明 PHASE14 的 installation / activation CAS、revocation propagation、ordered transition crash recovery 或 legacy registry cutover；这些需结合对应 evidence 做 Closure Gate 汇总。
- PHASE14 仍是 `in_progress`，不能据此关闭 Wave A Gate。
