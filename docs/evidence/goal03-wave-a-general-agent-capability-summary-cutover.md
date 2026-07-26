# Goal03 Wave A General Agent Capability Summary Cutover Evidence

status: partial_runtime_evidence
phase: PHASE14
commit_scope: GeneralAgent capability context summary cutover

本文只证明本次 Wave A 的默认 general agent 上下文组装切片：`GeneralAgent.prepare_context()` 继续使用 capability selection 结果，但传入模型上下文的 capability item 只保留摘要视图，不再直接暴露完整 `CapabilityRecord`。

## 已证明

- capability item 的 `content` 由摘要视图字符串生成，而不是完整 `CapabilityRecord.to_dict()`。
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
```

结果：

```text
passed
```

## 未证明

- 本证据不证明 PHASE14 的 full legacy registry cutover、安装/激活全链路或 supply-chain crash recovery 全部完成。
- 该切片只证明默认 model-visible context 已改为摘要视图。
