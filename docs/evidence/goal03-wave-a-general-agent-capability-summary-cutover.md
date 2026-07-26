# Goal03 Wave A General Agent Capability Summary Cutover Evidence

status: partial_runtime_evidence
phase: PHASE14
commit_scope: GeneralAgent capability context summary cutover

本文只证明本次 Wave A 的默认 general agent 上下文组装切片：`GeneralAgent.prepare_context()` 使用当前 runtime tool inventory 做确定性 capability selection，传入模型上下文的 capability item 只保留摘要视图，不再实例化旧 `CapabilityRegistry` / `DynamicCapabilitySelector` 或直接暴露完整 `CapabilityRecord`。

## 已证明

- capability item 的 `content` 由摘要视图字符串生成，而不是完整 `CapabilityRecord.to_dict()`。
- `GeneralAgent.prepare_context()` 不再调用 `DynamicCapabilitySelector(CapabilityRegistry(...))`。
- 新增静态 guard 测试，禁止默认 GeneralAgent 上下文路径重新实例化 legacy selector / registry。
- 新增默认 Product / Agent Runtime 旁路 guard，禁止 `agent.planning`、`agent.runtime.service`、`api.services.completion` 和 `api.services.product.command_service` 重新导入 `zuno.agent.tool_bridge`、`DynamicCapabilitySelector` 或直接构造 `CapabilityRegistry(...)`。
- 摘要视图只包含：
  - `name`
  - `type`
  - `description`
  - `schema_keys`
  - `schema_hash`
  - `source`
- capability item metadata 额外保留 `capability_context_view`，用于 trace 和审计，但不把完整 record 送进模型上下文。
- 现有 selection trace 仍保留，`selected_names` 与 tool card trace 不变。
- memory task summary 读取对缺失 `source_event_ids` 的旧行做了确定性回退，避免旧摘要把 `GeneralAgent.prepare_context()` 直接炸掉。

## 已运行验证

```powershell
python -m pytest -q tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/test_capability_layer_surfaces.py tests/agent/test_planning_control_runtime.py tests/capability/test_capability_skill_layer.py -p no:cacheprovider
```

结果：

```text
8 passed
22 passed
```

## 未证明

- 本证据不证明 PHASE14 的所有 legacy facade 已删除；`zuno.capability.registry` / `zuno.capability.selector` 仍作为兼容 facade 存在。
- 该切片证明默认 GeneralAgent context selection、Planner 和 Product / Completion runtime service 文件已有 legacy registry / selector 旁路 guard。
