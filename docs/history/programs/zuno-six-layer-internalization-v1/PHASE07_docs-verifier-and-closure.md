# PHASE07 Docs / Verifier / Closure

状态：completed

## 目标

把六层 thin surfaces 的完成事实同步到 README、architecture docs、Agent program 状态、verifier、repo tests，并将当前 program 归档。

## 完成内容

- 六层 README 同步 Current / Target / 禁止事项 / Focused tests。
- `docs/architecture/current-architecture.md` 只记录已完成 thin surfaces，不提升 runtime 成熟度。
- `docs/architecture/roadmap.md` 将 `zuno-six-layer-internalization-v1` 标为 completed / archived。
- `.agent/programs/` 改为无 active program 状态，并移除前台 `PHASE*.md`。
- `.agent/references/current-program.md` 改为 no active program，保留 queued draft。
- `verify_repo_structure.py`、`verify_agent_system.py`、`verify_doc_boundaries.py`、`verify-workflow.ps1` 固定完成态。
- repo tests 覆盖 no-active state、archive required paths、thin surface import guard 和 backend layer internal surfaces。

## 验收

完成态要求：

- `.agent/programs/` 不再保留 `PHASE*.md`。
- `docs/history/programs/zuno-six-layer-internalization-v1/` 保留 README、current、roadmap 和 PHASE01-07。
- 旧 public import path 仍可用。
- target-layer 新入口内部不依赖 `zuno.services`、`zuno.core` 等 legacy alias 路径。

## 验证

```powershell
pytest -q
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
git diff --check
```
