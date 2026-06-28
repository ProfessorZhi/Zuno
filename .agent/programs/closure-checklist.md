# 收口清单

关闭当前 phase 或 program 前使用这份清单。

## 当前无 Active Program 时

- `.agent/programs/` 只保留 `README.md`、`current.md`、`implementation-roadmap.md` 和 `closure-checklist.md`。
- 不保留任何已完成 program 的 `PHASE*.md`。
- `docs/history/programs/` 中有已完成 program 的归档证据。
- `.agent/architecture/future/programs/` 中只保留 queued draft。
- `docs/architecture/roadmap.md` 和 `.agent/references/current-program.md` 不把 queued draft 写成 active。

## 打开 Program 时

- 每次只打开一个 program。
- 每个新 program 从 `PHASE01` 开始编号。
- phase 文件平铺在 `.agent/programs/` 根目录，不建 program 子目录。
- 旧 active program 先归档到 `docs/history/programs/`。
- 修改 docs / agent workflow 后运行最小有效验证。

## Program Closure 自维护审查

每个 program 结束前必须完成这组检查：

- `AGENTS.md` 是否需要更新。
- `.agent/system.yaml` 的 route、docs_sync、verify 是否需要更新。
- `.agent/references/` 是否沉淀了新的 skill、lesson、pitfall 或 debug playbook。
- `.agent/templates/` 是否需要新增或修正模板。
- `.agent/programs/` 是否只保留当前 active program，或处于明确等待状态。
- completed program 是否已归档到 `docs/history/programs/`。
- `docs/architecture/current-architecture.md` 是否仍只写 Current。
- `docs/architecture/target-architecture.md` 是否需要吸收新的目标边界。
- `docs/architecture/roadmap.md` 是否反映最新状态。
- verifier / tests 是否覆盖新规则，避免下次漂移。

如果用户提醒“以后注意”，不能只留在对话里；必须分类并沉淀到 `.agent/references/`、`AGENTS.md`、`.agent/system.yaml` 或 verifier/test。

## 必跑检查

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
```

如果 phase 修改 runtime 或 eval 代码，还要补对应聚焦 runtime 或 eval 测试。
