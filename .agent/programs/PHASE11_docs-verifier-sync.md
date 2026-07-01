# PHASE11 Docs / Verifier Sync

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE11_docs-verifier-sync
mode: docs-verifier

## 目标

把 Program 3 已证明的 async ingestion infrastructure Current 写入正式文档、Agent docs、architecture mirrors、verifier 和 repo tests。只把代码和 tests 已证明的能力写成 Current；真实 PostgreSQL / RabbitMQ / Redis / MinIO / OCR / VLM provider 若未接入，必须保持 Target / target-blocked。

## 范围

- 更新 `docs/architecture/architecture.md`。
- 更新 `docs/architecture/production-readiness.md`。
- 更新 `docs/architecture/document-ingestion-foundation.md`。
- 运行 `python tools/agent/render_architecture.py --write` 同步 architecture mirrors。
- 更新 `README.md`、`AGENTS.md`、`.agent/references/current-program.md`。
- 更新 `.agent/system.yaml`、verifier 和 repo tests。

## 禁止范围

- 不把 Target 写成 Current。
- 不恢复退休 front path。
- 不改写 Program 1 / Program 2 closure evidence。
- 不在 README / AGENTS 里重复过长 phase 细节。

## 验收闸门

- architecture Markdown / HTML mirrors 同步。
- front path 摘要只写当前状态和入口，不重复完整 phase 目录。
- repo tests / verifiers 知道 Program 3 active / Program 4-6 queued。
- Current / Target / Future / History 边界清楚。

## 验证命令

```powershell
python tools/agent/render_architecture.py --write
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 需要先读取

- `AGENTS.md`
- `README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `.agent/references/current-program.md`
- `.agent/system.yaml`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_repo_structure_consistency.py`
- `.agent/scripts/verify_agent_system.py`
- `tools/scripts/verify_repo_structure.py`

## 需要修改的文件

- `AGENTS.md`
- `README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `.agent/architecture/architecture.md`
- `docs/architecture/architecture.html`
- `.agent/architecture/architecture.html`
- `.agent/references/current-program.md`
- `.agent/system.yaml`
- verifier / repo tests

## 执行拆解

1. 写文档 diff。
2. 渲染 architecture mirrors。
3. 更新 verifier / tests。
4. 跑 docs + repo verifier。
5. 修正 drift。

## 多 agent 分工

- Docs Agent：审 Current / Target 边界。
- Verification Agent：审 verifier / tests。
- Integration Reviewer Agent：审 front path 不重复。

## 需要返回的证据

- 文档同步文件列表。
- render architecture 输出。
- verifier 输出。
- Current / Target 边界摘要。

## 停止条件

- 代码证据不足以支撑 Current 文案。
- HTML mirror 与 Markdown 无法同步。
- verifier 改动会放松关键边界。
