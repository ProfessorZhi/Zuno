# 验证地图

## 文档修改

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

## 架构修改

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
```

需要理解架构演进时，优先读取 `docs/red-blue/rounds/` 的新式 Round；更早的手工/自动记录只在 `docs/red-blue/archive/legacy/`。这些 review 记录都不拥有当前架构，不作为生产证据。

## Current code selected verification

当前 GitHub-native selected code gate 是 `.github/workflows/current-code-selected-verification.yml`。

它从 `poetry.lock` 建立 Python 3.12 环境，执行 compile、Model Gateway strict boundary、Knowledge / Capability / Tool / Model Gateway / Security runtime-batch verifier，以及跨 Domain、Citation、Application、Runtime、Retrieval、Observability 和 Eval 的 selected behavior tests。当前 workflow 还启动 PostgreSQL 16 service，使 `tests/domain/test_domain_mutation_sqlalchemy.py` 的 PostgreSQL transaction / concurrency / replay probes 真正执行，而不是环境 skip。

它的证据含义严格限定为：**workflow 明确列出的行为在该 run 对应 SHA 上通过。** PostgreSQL service 的存在只证明被显式接入 `ZUNO_TEST_DATABASE_URL` 的 Domain selected probes；不能扩写成所有平台数据库路径、Migration 或系统级 PostgreSQL qualification 已通过。

当前可引用的 main push 记录见 `docs/evidence/current-test-baseline.md`。涉及 Current 主张时优先引用那个 Evidence，而不是只说“workflow 存在”。

## Runtime / Owner-specific verification

Runtime 或其他 Owner 的变更仍需要按对应 B14.8 / failure matrix 补 focused integration、fault injection、migration 或 benchmark。Selected code gate 只提供稳定基础回归面，不替代模块级 Freeze Evidence。

02 / 04 当前已经获得 Wave-001 Domain mutation 的真实 PostgreSQL row-lock / expected-version / idempotent replay baseline；仍缺 Target `AdmissionReceipt` implementation、Domain commit → Runtime Checkpoint repair、checkpoint-complete / receipt-absent denial、SecurityEpoch drift、正式 invalidation / late proposal integration 和真实 Migration apply / rollback。

同理，Effect send boundary、Security revocation、Knowledge generation activation、Provider qualification 与长期运行恢复仍应单独建立可复现证明；文档验证或 selected tests 不能据此声称 Full CI、Benchmark 或 Production Readiness。
