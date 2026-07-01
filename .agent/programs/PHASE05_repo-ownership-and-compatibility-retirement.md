# PHASE05 Repo Ownership and Compatibility Retirement

status: pending

## 目标

让文件夹结构和代码 ownership 真正清晰，减少零碎和凑合的兼容层，把真实 runtime owner 收回六层目录。

## 范围

- 盘点 `src/backend/zuno/api`、`agent`、`memory`、`capability`、`knowledge`、`platform`。
- 盘点 `platform/services`、`platform/compatibility`、`platform/vendor`、provider tree、legacy alias。
- 设计 import matrix、迁移顺序、兼容桥保留条件和退休条件。

## 禁止范围

- 不无测试删除 public import path。
- 不把 compatibility 当成新功能 owner。
- 不进行无关大重构。

## 验收闸门

- owner map 与 repo-ownership matrix 更新。
- legacy / compatibility / vendor guard 有测试。
- 至少完成一批低风险物理迁移或明确 blocked evidence。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider
```
