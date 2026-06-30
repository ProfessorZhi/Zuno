# PHASE12 Validation Release Closure

status: active

## 目标

完成大型 program 的 release closure：全量验证、八个方面产物证据、架构文档同步、历史归档、README 状态和推送证据。

## 步骤

- [ ] 运行全量 verifier 和 pytest。
- [ ] 生成 closure summary。
- [ ] 检查所有 Target / Future 未被误写成 Current。
- [ ] 检查 `.agent/programs/` 只保留当前 active program 或在 closure 后切换到 no-active。
- [ ] 归档本 program 到 `docs/history/programs/zuno-master-architecture-implementation-v1/`。
- [ ] 提交并推送。

## Closure Evidence 模板

closure summary 必须包含以下表格，不能只写自然语言总结：

### Phase Evidence

| Phase | 状态 | 主要文件 | 验证命令 | 结果 | remaining Target |
| --- | --- | --- | --- | --- | --- |
| PHASE01 | completed/pending | path list | command list | pass/fail/block | items |

### 八个方面目标产物证据

| 产物 | 对应 phase | Current 证据 | Target/Future 剩余项 | 可展示材料 |
| --- | --- | --- | --- | --- |
| D1 项目文件夹与代码布局治理 | PHASE02 | tests/verifier/ownership matrix | remaining moves | architecture docs |

### Verification Results

| Command | Exit code | Key output | Log path |
| --- | --- | --- | --- |
| `git diff --check` | 0/1 | summary | optional |

### Release Metadata

```text
branch:
commit:
merge_commit:
push_status:
pytest_summary:
eval_summary:
known_risks:
```

## Current / Target Audit

必须全文检查：

- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- `README.md`
- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/references/current-program.md`

审查问题：

- 是否把 Document Ingestion、LangGraph runtime、Memory DB、Tool approval、GraphRAG extraction/fusion、LangSmith trace/eval、security sandbox 写成未验证 Current。
- 是否把产品多 Agent 写成近期主线。
- 是否把研究 PDF 中的候选技术写成已实现事实。
- 是否留有旧 active program 状态。

## 验收

- 八个方面产物都有证据表。
- 所有验证命令通过或有明确阻塞说明。
- `main` 或 PR 分支状态可复现。
- 历史材料可追溯，前台路径干净。
- closure summary 必须能让下一轮 agent 不读聊天记录也知道每个 phase 做到哪里、哪些还在 Target。

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
