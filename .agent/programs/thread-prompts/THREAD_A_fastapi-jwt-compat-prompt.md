# Zuno Program3 Thread A 目标模式：fastapi_jwt_auth 兼容壳降噪与退休路径落地

你必须使用 Codex UI 目标模式。本线程默认开启多 agent 模式，但多个 agent 不得同时编辑同一文件。

## 工作模式

这是 Program3 continuation：`zuno-repo-layout-cleanup-v1`。

每轮开始必须先确认：

```powershell
pwd
git status --short --branch
git branch --show-current
```

如果当前不是独立 worktree 或不是独立 `codex/` 分支，先在本 worktree 内创建或切换到：

```text
codex/program3-thread-a-fastapi-jwt-compat
```

如果无法确认独立 worktree / 独立分支，停止并回报，不要编辑。

## 必读

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/PHASE06_backend-directory-clarity-audit.md`
- `.agent/programs/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`
- `tests/api/test_fastapi_jwt_auth_compat.py`
- `src/backend/fastapi_jwt_auth/__init__.py`

## 目标

让 `src/backend/fastapi_jwt_auth/` 不再像乱放的业务目录，而是清楚地表现为 compatibility shell。

优先做低风险落地：

1. 明确它是 compatibility shell，不是业务代码。
2. 尽量减少 shell 内部文件数量，前提是不破坏 public imports：
   - `from fastapi_jwt_auth import AuthJWT`
   - `from fastapi_jwt_auth.auth_config import AuthConfig`
   - `from fastapi_jwt_auth.config import LoadConfig`
   - `from fastapi_jwt_auth.exceptions import AuthJWTException`
3. 如果可以安全改成单文件 shell，更新 compat test。
4. 如果不能安全改成单文件 shell，添加清晰 README / module doc，并把原因写进 PHASE07。
5. 不直接删除 public import compatibility。

## 允许修改

- `src/backend/fastapi_jwt_auth/**`
- `tests/api/test_fastapi_jwt_auth_compat.py`
- `.agent/programs/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`
- 必要时 `tools/scripts/verify_repo_structure.py`
- 必要时 `tests/repo/test_repo_structure_consistency.py`

## 禁止修改

- 不改业务逻辑。
- 不改数据库。
- 不改 GraphRAG / retrieval runtime。
- 不做大规模 import 迁移。
- 不删除 `src/backend/zuno/vendor/fastapi_jwt_auth/`。

## 验证

必须运行：

```powershell
git diff --check
pytest -q tests/api/test_fastapi_jwt_auth_compat.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
```

## 收尾

提交并推送。提交信息建议：

```text
chore: clarify fastapi jwt compatibility shell
```

最终回复必须包含：

- branch
- commit hash
- push 状态
- 改了哪些文件
- `fastapi_jwt_auth` 是否减少了视觉噪音
- tests 结果
- 仍不能删除的原因
