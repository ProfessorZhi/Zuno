# PHASE03 RuntimeDependencyFactory

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE03_runtime-dependency-factory
state: pending
```

## 目标

建立统一依赖装配入口，让 Completion / Workspace 通过 typed `RuntimeDependencies` 注入 Model Gateway、Memory、Knowledge、Tool 和 Trace。

## 范围

- `src/backend/zuno/agent/runtime/factory.py`
- `src/backend/zuno/agent/runtime/configuration.py`
- `src/backend/zuno/agent/runtime/protocols.py`
- `src/backend/zuno/agent/runtime/dependencies.py`
- `src/backend/zuno/api/services/completion.py`
- Workspace runtime service 相关入口
- `tests/agent/runtime/**`
- `tests/api/**`

## 禁止范围

- 不直接在 runtime 中调用 provider SDK。
- 不让核心依赖缺失时继续成功。
- 不创建外部 graph DB / vector DB / queue。

## 验收闸门

- `RuntimeDependencyFactory.for_completion()` 和 `for_workspace_task()` 存在。
- 核心依赖有 typed protocols。
- 缺失 Knowledge / Tool / Model 时返回 blocked observation 或 blocked runtime status。
- Completion / Workspace 不再自己拼接一套旁路依赖。

## 验证命令

```powershell
pytest -q tests/agent/runtime tests/api -p no:cacheprovider
python tools/scripts/verify_real_runtime_cutover.py --enforce-dependencies
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
git diff --check
```

