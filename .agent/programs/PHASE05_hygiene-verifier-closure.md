# PHASE05：Repo Hygiene Verifier Closure
> 状态：pending。等待 PHASE01-04 收口后执行。

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
pytest -q tests/repo/test_repo_hygiene.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```
