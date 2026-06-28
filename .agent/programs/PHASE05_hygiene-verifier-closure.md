# PHASE05：Repo Hygiene Verifier Closure
> 状态：completed in branch `codex/program3-phase05-hygiene-verifier-closure`。等待主线程集成审查。

## 目标

把目录清理规则固化到 verifier 和 repo tests。

本 phase 要把 Program 3 的目录边界变成机器可检查规则，覆盖：

- 根目录允许的一等目录和本地产物忽略规则。
- `.agent/programs/` active / queued / history 边界。
- `docs/` 前台和 `docs/history/` 归档边界。
- `src/backend` 顶层和 `src/backend/zuno` 六层目标表达。
- 生成物、缓存、临时报告不能进入前台。

## PHASE01 输入

Thread C 的 guardrail 缺口：

- `tools/` 当前职责是维护、verify、eval、render、launcher、migration 工具，但还没有固定 tools 子目录允许集。
- `tests/` 当前是测试源，`tests/repo` 是仓库规则测试，但还需要禁止 cache/generated artifact 被 tracked。
- `examples/` 是可运行示例和示例数据，需要说明 runtime outputs 去向。
- `infra/` 是 DB/Docker 基础设施，需要禁止运行态 volume/cache 进入 tracked。
- `.test-tmp/`、`.pytest_cache/`、`tmp/`、`output/`、`apps/desktop/node_modules/` 应进入 required ignore / forbidden tracked prefixes。
- `data/`、`reports/` 需要白名单规则：示例输入和正式证据可 tracked，raw downloads、normalized/corpus/ingested、runtime reports 不可 tracked。

## 验证

```powershell
git diff --check
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_repo_hygiene.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## 完成证据

本线程把 PHASE01 Thread C 的 guardrail 缺口机器化：

- `.gitignore` 已明确覆盖 `.test-tmp/`、`.pytest_cache/`、`tmp/`、`output/`、`apps/desktop/node_modules/`、`apps/web/node_modules/`、`apps/web/dist/`、`data/evals/multihop/*` 生成数据和 `reports/evals/multihop/*` runtime 报告。
- `.agent/scripts/verify_repo_hygiene.py` 现在公开并执行 `REQUIRED_IGNORES`、`FORBIDDEN_TRACKED_PREFIXES`、`FORBIDDEN_TRACKED_PATTERNS` 和 `TRACKED_DATA_REPORTS_ALLOWLIST`，禁止 generated/cache/local path 被 tracked，并禁止粗暴忽略整个 `data/` 或 `reports/`。
- `tools/scripts/verify_repo_structure.py` 现在公开并执行 `TOP_LEVEL_RESPONSIBILITY_DIRECTORIES`、`ALLOWED_RESPONSIBILITY_SUBDIRS` 和 `ALLOWED_RESPONSIBILITY_FILES`，固定 `tools/`、`tests/`、`examples/`、`infra/` 的一等职责和允许子目录。
- `tests/repo/test_repo_hygiene.py` 增加生成物/cache required ignore、forbidden tracked prefix/pattern、`data/` / `reports/` 白名单语义断言。
- `tests/repo/test_repo_structure_consistency.py` 增加目录职责常量、实际子目录允许集和 `run_verification()` 接线防绕过断言。
