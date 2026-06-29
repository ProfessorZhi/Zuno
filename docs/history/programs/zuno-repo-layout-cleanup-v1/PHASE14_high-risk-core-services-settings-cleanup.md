# PHASE05 High Risk Core Services Settings Cleanup

> 状态：completed / archived。

## 目标

最后处理高风险 alias：`core.py`、`services.py`、`settings.py`。这一步只处理兼容入口位置，不做 runtime architecture upgrade。

## 高风险原因

- `zuno.core.*` 承接 Agent runtime 历史路径。
- `zuno.services.*` 承接大量 RAG、GraphRAG、queue、workspace、memory 历史路径。
- `zuno.settings` 影响 FastAPI startup、配置解析、tests monkeypatch 和 eval scripts。

## 需要修改的文件

- `src/backend/zuno/__init__.py`
- `src/backend/zuno/platform/compatibility/legacy_aliases.py`
- `src/backend/zuno/platform/settings.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/tools/test_config_system_tool_metadata.py`
- `tests/repo/test_repo_hygiene.py`
- `tests/repo/test_zuno_runtime_chain_guard.py`

## 禁止修改的文件

- `src/backend/zuno/main.py`
- `src/backend/zuno/agent/core/agents/general_agent.py`
- `src/backend/zuno/platform/services/**` 行为逻辑
- API / DB / frontend / eval baseline

## 验收闸门

- `import zuno.core.agents.general_agent` 继续通过。
- `import zuno.services.rag.handler` 继续通过。
- `from zuno import settings` 和 `from zuno.settings import app_settings` 继续通过。
- `pytest -q -p no:cacheprovider` 通过。

## 验证命令

```powershell
pytest -q tests/legacy_guards/test_zuno_alias_imports.py tests/tools/test_config_system_tool_metadata.py tests/repo/test_repo_hygiene.py tests/repo/test_zuno_runtime_chain_guard.py -p no:cacheprovider
pytest -q -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
