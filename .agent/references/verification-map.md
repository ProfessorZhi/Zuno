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

它从 `poetry.lock` 建立 Python 3.12 环境，执行 compile、Model Gateway strict boundary、Knowledge / Capability / Tool / Model Gateway / Security runtime-batch verifier，以及跨 Domain、Citation、Application、Runtime、Retrieval、Observability 和 Eval 的 selected behavior tests。每次 run 上传 JUnit、日志和 commit / environment context。

它的证据含义严格限定为：**workflow 明确列出的行为在该 run 对应 SHA 上通过。** 它不是 Full CI，也不自动证明真实 PostgreSQL、Redis、RabbitMQ、Object Store、Model / Tool Provider、浏览器、外部 Host、benchmark、HA / DR 或 Production Readiness。

当前可引用的 main push 记录见 `docs/evidence/current-test-baseline.md`。涉及 Current 主张时优先引用那个 Evidence，而不是只说“workflow 存在”。

## Runtime / Owner-specific verification

Runtime 或其他 Owner 的变更仍需要按对应 B14.8 / failure matrix 补 focused integration、fault injection、migration 或 benchmark。Selected code gate 只提供稳定的基础回归面，不替代这些模块级 Freeze Evidence。

尤其真实数据库并发、跨 Owner crash window、Effect send boundary、Security revocation 和长期运行恢复仍应单独建立可复现证明；文档验证或 selected unit/integration tests 不能据此声称 Full CI。
