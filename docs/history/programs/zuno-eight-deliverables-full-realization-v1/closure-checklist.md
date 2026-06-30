# 收口清单

关闭当前 phase 或 program 前使用这份清单。

## 当前 Active Program

- Program: `zuno-eight-deliverables-full-realization-v1`
- 当前只允许一个 active program。
- Active phase 文件必须平铺在 `.agent/programs/` 根目录，从 `PHASE01` 连续编号。
- `current.md`、`implementation-roadmap.md`、`.agent/references/current-program.md`、`docs/architecture/roadmap.md` 和 `AGENTS.md` 必须写同一个 active program。
- `.agent/architecture/future/programs/` 中的 queued drafts 只能作为参考输入，不能被写成 active。

## Phase 收口

- 每个 phase 必须说明完成了哪些八交付物。
- 修改 docs / `.agent` 时必须同步 verifier 或 repo tests，避免规则只留在文字里。
- 修改 runtime 或 eval 时必须补 focused tests 或 eval proof。
- Current / Target / Future / History 必须分开。
- 主线程默认开启线程内多 agent 协作；最终 diff、验证和提交判断仍由主线程负责。

## Program Closure 自维护审查

每个 program 结束前必须完成这组检查：

- `AGENTS.md` 是否需要更新。
- `.agent/system.yaml` 的 route、docs_sync、verify 是否需要更新。
- `.agent/references/` 是否沉淀了新的 skill、lesson、pitfall 或 debug playbook。
- `.agent/templates/` 是否需要新增或修正模板。
- `.agent/programs/` 是否已从 active program 归档回等待状态。
- completed program 是否已归档到 `docs/history/programs/`。
- 本 program 完成后是否已归档到 `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`。
- `docs/architecture/current-architecture.md` 是否仍只写 Current。
- `docs/architecture/target-architecture.md` 是否吸收已完成的目标边界。
- `docs/architecture/roadmap.md` 是否反映最新状态。
- verifier / tests 是否覆盖新规则，避免下次漂移。

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

如果 phase 修改 runtime 或 eval 代码，还要补对应聚焦 runtime 或 eval 测试。
