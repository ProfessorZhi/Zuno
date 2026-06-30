# PHASE12 release-gate-full-e2e-closure

status: active

## 目标

以完整 vertical slice 做 release closure：真实链路可跑、证据可追、指标过线、文档同步、program 归档、commit、merge 和 push。

## 范围

- 运行 repo verifier、focused pytest、完整 e2e task 回放、parser golden、retrieval/eval/security baseline。
- 更新 architecture Markdown / HTML、README、AGENTS、current-program 和 closure summary。
- 归档本 program 到 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。

## 禁止范围

- 不用“contracts 都齐了”作为 release closure。
- 不留下 active phase 文件和 archived program 双前台。
- 不跳过 main 与 origin/main 对齐证明。

## 验收闸门

- e2e 回放覆盖：上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback。
- full pytest 和 workflow/repo/architecture verifiers 通过。
- Current / Target / Future / History 边界在 docs 和 `.agent` 中一致。

## 验证命令

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
