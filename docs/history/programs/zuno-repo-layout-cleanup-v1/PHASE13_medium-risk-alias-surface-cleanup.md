# PHASE04 Medium Risk Alias Surface Cleanup

> 状态：completed / archived。

## 目标

收口中风险 alias，继续减少 `src/backend/zuno` 根级 `.py` 文件。

## 第二批候选

- `mcp_servers.py`
- `middleware.py`
- `database.py`
- `schema.py`
- `tools.py`
- `utils.py`

## 需要修改的文件

- `src/backend/zuno/__init__.py`
- `src/backend/zuno/platform/compatibility/legacy_aliases.py`
- `src/backend/zuno/platform/database/**`
- `src/backend/zuno/api/dto/**`
- `src/backend/zuno/capability/tools/**`
- `src/backend/zuno/platform/common/**`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_zuno_runtime_chain_guard.py`
- `tools/scripts/verify_repo_structure.py`

## 禁止修改的文件

- `core.py`
- `services.py`
- `settings.py`
- runtime 主循环
- DB schema
- API response contract

## 验收闸门

- 中风险旧 import path 继续可用。
- 根目录 alias 文件数量继续下降。
- 所有 monkeypatch/importlib 相关测试仍通过。

## 验证命令

```powershell
pytest -q tests/legacy_guards/test_zuno_alias_imports.py tests/repo/test_zuno_runtime_chain_guard.py tests/tools/test_send_email_cli.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
