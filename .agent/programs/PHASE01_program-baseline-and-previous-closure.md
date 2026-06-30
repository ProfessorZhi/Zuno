# PHASE01 Program Baseline And Previous Closure

status: active

## 目标

打开 `zuno-master-architecture-implementation-v1`，归档上一轮架构细化 program，修正前台 active 状态，让后续大型实施计划有唯一入口。

## 范围

允许修改 `.agent/programs/`、`.agent/references/current-program.md`、`README.md`、`AGENTS.md`、`docs/history/research/`、`docs/architecture/architecture.md`、verifier 和 repo tests 中与 active program、研究输入归档和架构源文档状态相关的规则。

禁止修改 runtime 代码、API 行为、DB schema、frontend product flow。

## 步骤

- [ ] 确认 branch 和工作区干净。
- [ ] 将旧 `zuno-architecture-detail-and-execution-plan-v1` 文件移入 `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`。
- [ ] 写入本 program 的 `current.md`、`README.md`、`implementation-roadmap.md` 和 `closure-checklist.md`。
- [ ] 创建 PHASE01-PHASE12 文件。
- [ ] 将用户提供的高质量架构 PDF 归档到 `docs/history/research/chatgpt-research-mode-artifacts/`，并保留 Markdown 抽取版。
- [ ] 更新 `.agent/references/current-program.md`、`README.md` 和 `AGENTS.md`。
- [ ] 更新 verifiers/tests 对 active program 的期望。

## 验收

- `.agent/programs/` 只保留本 program。
- 当前状态面都写 `zuno-master-architecture-implementation-v1`。
- 旧 program 在 `docs/history/programs/` 可追溯。
- 研究报告原始 PDF 和 Markdown 抽取版在 `docs/history/research/chatgpt-research-mode-artifacts/` 可追溯。
- repo verifier 和 program tests 通过。

## 验证

```powershell
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py -p no:cacheprovider
```
