# PHASE02 Import Smoke And Compat Registry Design

> 状态：completed / archived。

## 目标

先补 legacy import smoke matrix，再设计内部兼容注册机制，避免为了视觉清爽破坏旧 public import path。

## 范围

- 新增或扩展 legacy import tests。
- 设计 `platform/compatibility` 下的 alias registry 方案。
- 不删除根级 alias 文件。

## 需要修改的文件

- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_repo_structure_consistency.py`
- `tools/scripts/verify_repo_structure.py`
- `src/backend/zuno/platform/compatibility/README.md`
- 可新增：`src/backend/zuno/platform/compatibility/legacy_aliases.py`

## 禁止修改的文件

- `src/backend/zuno/main.py`
- `src/backend/zuno/platform/services/**` 行为逻辑
- `src/backend/zuno/agent/core/**` 行为逻辑
- API / DB / frontend / eval baseline

## 必须覆盖的旧 import path

```text
zuno.services.*
zuno.core.*
zuno.database.*
zuno.schema.*
zuno.tools.*
zuno.utils.*
zuno.config.*
zuno.resources.*
zuno.compatibility.*
zuno.settings
zuno.mcp_servers.*
zuno.middleware.*
zuno.evals.*
```

## 验收闸门

- smoke tests 在根级 alias 文件尚未删除时先通过。
- registry 设计只注册兼容路径，不改变 runtime 调用语义。

## 验证命令

```powershell
pytest -q tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
