# PHASE03 Low Risk Alias Surface Cleanup

> 状态：completed / archived。

## 目标

第一批收口低风险 alias，让兼容实现进入 `platform/compatibility` 或目标层内部，同时保持旧 import path 可用。

## 第一批候选

- `compatibility.py`
- `evals.py`
- `resources.py`
- `config.py`

## 需要修改的文件

- `src/backend/zuno/__init__.py`
- `src/backend/zuno/platform/compatibility/legacy_aliases.py`
- `src/backend/zuno/platform/compatibility/**`
- `src/backend/zuno/platform/resources/**`
- `src/backend/zuno/platform/config/**`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tools/scripts/verify_repo_structure.py`

## 禁止修改的文件

- `services.py`
- `core.py`
- `settings.py`
- `database.py`
- `schema.py`
- `tools.py`
- `utils.py`
- runtime 主循环

## 验收闸门

- 根目录第一批 alias 文件被移除或变成内部注册，不再作为目标完成态的一部分。
- `import zuno.config.es_index`、`import zuno.resources.prompts.completion`、`import zuno.compatibility.vendor.fastapi_jwt_auth`、`import zuno.evals.rag_eval.run_stackless_local_eval` 继续通过。

## 验证命令

```powershell
pytest -q tests/legacy_guards/test_zuno_alias_imports.py tests/api/test_fastapi_jwt_auth_compat.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
