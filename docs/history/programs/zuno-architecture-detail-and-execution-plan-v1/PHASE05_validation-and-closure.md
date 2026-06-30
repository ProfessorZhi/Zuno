# PHASE05 验证与收口

status: pending

## 目标

完成文档、图、HTML、program 状态、verifier 和 repo tests 的闭环验证，为后续实现 program 留出清晰入口。

## 范围

验证与收口，不新增 runtime feature。

## 需要修改的文件

- `.agent/programs/closure-checklist.md`
- `.agent/scripts/verify_agent_system.py`
- `tools/scripts/verify_docs_entrypoints.py`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_docs_entrypoints.py`

## 禁止修改的文件

- 不为了通过验证而降低 Current / Target 边界。
- 不删除历史归档。

## 验收闸门

- Render check 通过。
- Agent system verifier 通过。
- Docs entrypoint verifier 通过。
- Repo tests 通过。
- `git diff --check` 通过。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```

## 需要返回的证据

- modified files
- validation results
- commit hash
- push result

## 历史影响

本 program 完成时再归档到 `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`。当前阶段不提前归档。
