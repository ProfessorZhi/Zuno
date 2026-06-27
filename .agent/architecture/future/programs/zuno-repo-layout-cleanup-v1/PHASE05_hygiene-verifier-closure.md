# PHASE05：Repo Hygiene Verifier Closure

## 目标

把目录清理规则固化到 verifier 和 repo tests。

## 验证

```powershell
git diff --check
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_repo_hygiene.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```
