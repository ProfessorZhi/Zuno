# PHASE05：Program Closure 与 History 归档

## 目标

关闭 `zuno-workflow-doc-system-v1`，把执行证据归档，更新状态面，并为下一个 program 保持干净入口。

## 范围

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/references/current-program.md`
- `docs/architecture/roadmap.md`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- 必要的 verifier / repo tests

## 可并行线程

建议串行。Closure 涉及状态面和归档路径，主线程统一执行最稳。

## 不做

- 不打开下一个 program 的 phase。
- 不删除历史证据。
- 不把 Program 2-5 queued packs 当成已经完成。

## 验收

- 当前 program 的执行文件已归档到 `docs/history/programs/`。
- `.agent/programs` 进入“无 active phase”或下一个 program 已明确打开。
- `docs/architecture/roadmap.md` 与 `.agent/programs/current.md` 状态一致。

## 验证

```powershell
git status --short --branch
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_hygiene.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```
