# Goal03 Wave A Knowledge Package A Replay Receipt Evidence

status: partial_runtime_evidence
phase: PHASE12
commit_scope: Package A snapshot handoff replay receipt validation repair

本文只证明本次修复切片：`PackageAProductionIngestionRuntime` 的重复 delivery 回放校验不再把缺失的 `handoff_envelope_hash` 当成重复场景的首要阻断点；回放校验现在只会在预期侧确实提供该字段时才比较它，避免把后续更具体的 `document_version_id`、`quality_decision_id`、`visibility_ref`、`outbox_payload_idempotency_key` 等 mismatch 误遮蔽掉。

## 已证明

- 重复 delivery 的 worker inbox 路径可使用 runtime worker identity。
- `handoff_envelope_hash` 只有在预期 replay 实际携带时才参与比较。
- `tests/knowledge/test_package_a_delivery_settlement.py` 中的重复成功回放 mismatch 用例恢复到按字段精确失败。
- `tests/knowledge` 套件恢复为全绿。

## 已运行验证

```powershell
python -m pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
python -m pytest -q tests/knowledge -p no:cacheprovider
git diff --check
python tools/scripts/verify_repo_structure.py
```

结果：

```text
49 passed in 2.32s
214 passed in 42.64s
Repository structure verification passed.
```

## 未证明

- 这只证明重复回放校验顺序恢复正确，不证明 PHASE12 完整完成。
- 生产数据库、外部索引和 Wave A Gate 仍需更大范围证据。
