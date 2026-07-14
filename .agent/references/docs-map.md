# 文档同步 Skill

## When To Use

当任务触碰 `docs/`、`.agent/`、AGENTS.md、README、架构、状态、ADR、治理或术语边界时使用。

## Mental Model

```text
docs/architecture/ = 总架构四个支撑文件
docs/modules/      = 十一个领域模块唯一正式 Target 文档
docs/status/       = Current / Gap / Readiness
docs/decisions/    = ADR
docs/governance/   = Ownership 与共享 Contract
docs/evidence/     = 可复现证据
docs/history/      = History
.agent/architecture/ = 总架构字节级镜像
.agent/modules/      = 十一模块字节级镜像
.agent/programs/     = Current → Target 实施计划
```

## 正式架构入口

```text
docs/architecture/architecture.md
docs/architecture/architecture.html
docs/architecture/architecture-views.md
docs/status/production-readiness.md
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

`architecture-views.md` 是 HTML Mermaid 图源，不是第二份文字总架构。

## 十一个模块路由

| 模块 | 正式文档 | Agent 镜像 | Verifier |
| --- | --- | --- | --- |
| 01 Product Surface | `docs/modules/01-product-surface.md` | `.agent/modules/01-product-surface.md` | `python tools/scripts/verify_product_surface_target_protocols.py` |
| 02 Input / Document Ingestion | `docs/modules/02-input-document-ingestion.md` | `.agent/modules/02-input-document-ingestion.md` | `python tools/scripts/verify_architecture_document_set.py` |
| 03 Knowledge / Agentic GraphRAG | `docs/modules/03-knowledge-agentic-graphrag.md` | `.agent/modules/03-knowledge-agentic-graphrag.md` | `python tools/scripts/verify_architecture_document_set.py` |
| 04 Model Gateway | `docs/modules/04-model-gateway.md` | `.agent/modules/04-model-gateway.md` | `python tools/scripts/verify_model_gateway_target_protocols.py` |
| 05 Memory & Context | `docs/modules/05-memory-context.md` | `.agent/modules/05-memory-context.md` | `python tools/scripts/verify_memory_context_target_protocols.py` |
| 06 Agent Core / Planning & Control | `docs/modules/06-agent-core-planning-control.md` | `.agent/modules/06-agent-core-planning-control.md` | `python tools/scripts/verify_agent_core_target_protocols.py` |
| 07 Capability / Skill | `docs/modules/07-capability-skill.md` | `.agent/modules/07-capability-skill.md` | `python tools/scripts/verify_capability_skill_target_protocols.py` |
| 08 Tool Runtime | `docs/modules/08-tool-runtime.md` | `.agent/modules/08-tool-runtime.md` | `python tools/scripts/verify_tool_runtime_target_protocols.py` |
| 09 Security | `docs/modules/09-security.md` | `.agent/modules/09-security.md` | `python tools/scripts/verify_security_target_protocols.py` |
| 10 Observability & Eval | `docs/modules/10-observability-eval.md` | `.agent/modules/10-observability-eval.md` | `python tools/scripts/verify_observability_eval_target_protocols.py` |
| 11 Infrastructure | `docs/modules/11-infrastructure.md` | `.agent/modules/11-infrastructure.md` | `python tools/scripts/verify_infrastructure_target_protocols.py` |

## Must Preserve

- 每个模块只有一份 `docs/modules/<NN>-*.md` 正式 Target 文档。
- 十一份模块文档都有同名字节级 `.agent/modules/` 镜像。
- `docs/architecture/` 与 `.agent/architecture/` 只能包含 README、Markdown、Mermaid source 和 HTML 四个文件。
- 模块领域细节以对应 Owner 模块文档为准；总架构只做跨模块集成。
- Current 只由代码、Migration、测试、Trace、Eval 和运行证据证明。
- 历史分拆文档不得重新成为活跃事实源。
- Tool Runtime 拥有 `PreparedToolAction`、`ToolAttempt`、`EffectReceipt`、`EffectReconciliation`；Capability / Skill 只拥有能力语义、版本、可用性和选择。

## Docs Sync

修改模块设计时同步：

```text
docs/modules/<NN>-module.md
.agent/modules/<NN>-module.md
docs/modules/README.md
.agent/modules/README.md
.agent/system.yaml
对应 verifier / focused test
必要时同步 architecture.md / architecture-views.md / architecture.html
```

修改总架构时同步：

```text
docs/architecture/architecture.md
.agent/architecture/architecture.md
docs/architecture/architecture-views.md
.agent/architecture/architecture-views.md
docs/architecture/architecture.html
.agent/architecture/architecture.html
```

## Focused Tests

```text
git diff --check
python tools/scripts/verify_architecture_document_set.py
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_architecture_document_set.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Lessons Learned

文档同步不是在所有地方复制正文，而是让每个 surface 只承载自己的事实层级，并通过路由、镜像和机器校验保持一致。
