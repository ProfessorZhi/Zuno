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

## 验证

```powershell
git diff --check
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_repo_hygiene.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```
