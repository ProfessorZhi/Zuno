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
