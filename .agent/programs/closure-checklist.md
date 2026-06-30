# 收口清单

当前 active program：`zuno-architecture-detail-and-execution-plan-v1`

## Program Closure 自维护审查

本 program 结束前必须完成这组检查：

- `AGENTS.md` 是否需要更新 active program 状态。
- `.agent/system.yaml` 的 route、docs_sync、verify 是否需要更新。
- `.agent/references/diagram-inventory.md` 是否反映十类图二级组件要求。
- `.agent/references/current-program.md` 是否和 `.agent/programs/current.md` 一致。
- `.agent/programs/` 是否只保留本 active program 的 PHASE01-05，或收口时已归档回等待态。
- completed program 是否已归档到 `docs/history/programs/`。
- `docs/architecture/architecture.md` 是否仍只写 Current。
- `docs/architecture/architecture.md` 是否吸收新的目标边界。
- `docs/architecture/architecture.md` 是否反映最新 active program 状态。
- verifier / tests 是否覆盖新规则，包括 active program、十类图和生成 HTML 的新契约。

如果用户提醒“以后注意”，不能只留在对话里；必须分类并沉淀到 `.agent/references/`、`AGENTS.md`、`.agent/system.yaml` 或 verifier/test。

## 必跑检查

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

如果 phase 修改 runtime 或 eval 代码，还要补对应聚焦 runtime 或 eval 测试。本 program 当前不修改 runtime 或 eval 代码。
