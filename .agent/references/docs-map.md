# 文档同步 Skill

## When To Use

当任务触碰 `docs/`、`.agent/`、AGENTS.md、README、架构、状态、ADR、治理或术语边界时使用。

## Mental Model

```text
docs/architecture/ = 总架构正文与架构图展示配对
docs/modules/      = 十一个领域模块唯一正式 Target 文档
docs/status/       = Current / Gap / Readiness
docs/decisions/    = ADR
docs/governance/   = Ownership 与共享 Contract
docs/evidence/     = 可复现证据
docs/history/      = History
.agent/              = 项目级 Agent Skill、路由、验证器、模板和执行状态
.agent/programs/     = Current → Target 实施计划；无 active 时保持 no-active
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

`architecture-views.md` 与 `architecture.html` 是不可拆分的 HTML Mermaid 展示配对，不是第二份文字总架构，也不拥有独立架构事实。

两层阅读路径：

```text
人类理解：architecture.md Part A → module Part A → module Part B（按需）
工程实现：architecture.md Part B → Owner module Part B → ADR/Contract → Status/Evidence → Program
```

Part A 和 Part B 必须共存于同一 Canonical Markdown；禁止创建 `*-human.md`、`*-spec.md` 或新的架构镜像。

总架构和模块的统一信息架构、标题、Mermaid、Current/Target 和 QA 引用规则见：

`docs/governance/architecture-document-writing-standard.md`

## 十一个模块路由

| 模块 | 唯一正式文档 | Verifier |
| --- | --- | --- |
| 01 Product Surface | `docs/modules/01-product-surface.md` | `python tools/scripts/verify_product_surface_target_protocols.py` |
| 02 Input / Document Ingestion | `docs/modules/02-input-document-ingestion.md` | `python tools/scripts/verify_architecture_document_set.py` |
| 03 Knowledge / Agentic GraphRAG | `docs/modules/03-knowledge-agentic-graphrag.md` | `python tools/scripts/verify_architecture_document_set.py` |
| 04 Model Gateway | `docs/modules/04-model-gateway.md` | `python tools/scripts/verify_model_gateway_target_protocols.py` |
| 05 Memory & Context | `docs/modules/05-memory-context.md` | `python tools/scripts/verify_memory_context_target_protocols.py` |
| 06 Agent Core / Planning & Control | `docs/modules/06-agent-core-planning-control.md` | `python tools/scripts/verify_agent_core_target_protocols.py` |
| 07 Capability / Skill | `docs/modules/07-capability-skill.md` | `python tools/scripts/verify_capability_skill_target_protocols.py` |
| 08 Tool Runtime | `docs/modules/08-tool-runtime.md` | `python tools/scripts/verify_tool_runtime_target_protocols.py` |
| 09 Security | `docs/modules/09-security.md` | `python tools/scripts/verify_security_target_protocols.py` |
| 10 Observability & Eval | `docs/modules/10-observability-eval.md` | `python tools/scripts/verify_observability_eval_target_protocols.py` |
| 11 Infrastructure | `docs/modules/11-infrastructure.md` | `python tools/scripts/verify_infrastructure_target_protocols.py` |

## Must Preserve

- 每个模块只有一份 `docs/modules/<NN>-*.md` 正式 Target 文档。
- `docs/architecture/` 物理上只保留 README、`architecture.md`、`architecture-views.md` 和 `architecture.html`；其中正式文字设计是 `architecture.md`，后两者是展示配对；`.agent/` 不保存架构镜像。
- 模块领域细节以对应 Owner 模块文档为准；总架构只做跨模块集成。
- Current 只由代码、Migration、测试、Trace、Eval 和运行证据证明。
- 历史分拆文档不得重新成为活跃事实源。
- Tool Runtime 拥有 `PreparedToolAction`、`ToolAttempt`、`EffectReceipt`、`EffectReconciliation`；Capability / Skill 只拥有能力语义、版本、可用性和选择。

## Docs Sync

修改模块设计时同步：

```text
docs/modules/<NN>-module.md
docs/modules/README.md
.agent/system.yaml
对应 verifier / focused test
必要时同步 architecture.md；如果图形关系变化，把 architecture-views.md 与 architecture.html 作为一个整体同步
```

修改总架构时同步：

```text
docs/architecture/architecture.md
docs/architecture/architecture-views.md + docs/architecture/architecture.html（展示配对）
```

如果修改的是文档结构或阅读顺序，还要同步写作标准入口和写作标准 verifier；不在 `.agent/` 创建架构正文镜像。

## Focused Tests

```text
git diff --check
python tools/scripts/verify_architecture_document_set.py
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_deep_dive_architecture.py
python tools/scripts/verify_architecture_interview_qa.py
python tools/scripts/verify_markdown_internal_links.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_architecture_document_set.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Lessons Learned

文档同步不是在所有地方复制正文，而是让 `docs/` 保持唯一正式事实源，让 `.agent/` 只维护路由、执行状态和可复用工作流，并通过机器校验防止重复事实源回归。
