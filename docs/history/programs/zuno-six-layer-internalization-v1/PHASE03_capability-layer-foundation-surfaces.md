# PHASE03 Capability 层 Foundation Surfaces

状态：completed

## 目标

让 `src/backend/zuno/capability/` 拥有 capability contract、registry、selector、policy、execution 和 trace 的薄入口，同时保持工具 runtime wiring 不变。

## 完成内容

- `contracts.py`：CapabilityRecord、CapabilitySelection、CapabilitySelectionTrace 等 contract 入口。
- `registry.py`：CapabilityRegistry 和 default registry 入口。
- `selector.py`：DynamicCapabilitySelector 入口。
- `policy.py`：CapabilityPermission、CapabilityHealth、CapabilityCost 等策略相关入口。
- `execution.py`：CapabilityExecutionRequest / CapabilityExecutionResult 等执行 contract 入口。
- `trace.py`：selection trace 入口。

## 决策

`capability/tools/` 不按 CLI / API 拆成两类顶层目录。CLI / API 是 execution adapter、runtime type 或 provider metadata，不是 capability 的主分类。按 CLI / API 拆目录会把“怎么执行”误当成“能力是什么”，不利于后续 ToolCard、权限、健康状态和 selector 统一治理。

## 边界

本 phase 不改工具权限、执行模式、provider wiring、API response key 或旧 `zuno.services.application.capabilities` / `zuno.services.capability_registry` import path。

## 验证

```powershell
pytest -q tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
```
