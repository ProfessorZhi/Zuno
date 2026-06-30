# PHASE12 Validation Release Closure

status: pending

## 目标

完成大型 program 的 release closure：全量验证、八个方面产物证据、架构文档同步、历史归档、README 状态和推送证据。

## 步骤

- [ ] 运行全量 verifier 和 pytest。
- [ ] 生成 closure summary。
- [ ] 检查所有 Target / Future 未被误写成 Current。
- [ ] 检查 `.agent/programs/` 只保留当前 active program 或在 closure 后切换到 no-active。
- [ ] 归档本 program 到 `docs/history/programs/zuno-master-architecture-implementation-v1/`。
- [ ] 提交并推送。

## 验收

- 八个方面产物都有证据表。
- 所有验证命令通过或有明确阻塞说明。
- `main` 或 PR 分支状态可复现。
- 历史材料可追溯，前台路径干净。

## 验证

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q -p no:cacheprovider
```
