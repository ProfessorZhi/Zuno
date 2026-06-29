# Zuno Program3 Thread D 目标模式：Resources / Compatibility 物理迁移

你必须使用 Codex UI 目标模式。本线程默认开启多 agent 模式，但多个 agent 不得同时编辑同一文件。

## Setup Gate

先确认：

```powershell
pwd
git status --short --branch
git branch --show-current
```

如果不是独立 worktree 或不是 `codex/program3-thread-d-resources-compatibility-migration` 分支，先在本 worktree 创建或切换到该分支。若无法确认，停止。

## 必读

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/PHASE06_backend-directory-clarity-audit.md`
- `.agent/programs/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- `src/backend/zuno/README.md`
- `tests/api/test_fastapi_jwt_auth_compat.py`
- `tools/scripts/verify_repo_structure.py`

## 目标

这轮必须做真实物理迁移，不再只写 README。

目标形态：

```text
src/backend/
  zuno/

src/backend/zuno/
  resources/
    prompts/
    fixtures/
    system_skills/
  compatibility/
    legacy/
    vendor/
```

优先完成：

1. `prompts/` -> `resources/prompts/`
2. `fixtures/` -> `resources/fixtures/`
3. `system_skills/` -> `resources/system_skills/`
4. `legacy/` -> `compatibility/legacy/`
5. `vendor/` -> `compatibility/vendor/`
6. 尝试彻底删除 `src/backend/fastapi_jwt_auth/` 顶层目录。

如果删除 `fastapi_jwt_auth/`，必须同时修正 runtime imports 和 vendored internal imports，并保留 focused tests。若确实不能删除，必须给出当前失败证据和下一步最小阻塞点。

## 允许修改

- `src/backend/zuno/resources/**`
- `src/backend/zuno/compatibility/**`
- `src/backend/zuno/prompts/**`
- `src/backend/zuno/fixtures/**`
- `src/backend/zuno/system_skills/**`
- `src/backend/zuno/legacy/**`
- `src/backend/zuno/vendor/**`
- `src/backend/fastapi_jwt_auth/**`
- import consumers required by the move
- `tests/api/test_fastapi_jwt_auth_compat.py`
- repo structure verifier / repo tests
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`

## 禁止

- 不改 DB schema。
- 不改 GraphRAG query semantics。
- 不拆 `general_agent.py`。
- 不把 Target 说成 Current，除非代码和 tests 已经证明。

## 验证

至少运行：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/api/test_fastapi_jwt_auth_compat.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

## 收尾

提交并推送。提交信息建议：

```text
refactor: consolidate backend resources and compatibility
```

最终报告必须说明哪些顶层目录被真正移走、哪些还留着以及原因。
