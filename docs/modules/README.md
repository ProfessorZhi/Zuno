# Zuno 十一个逻辑模块

`docs/modules/` 保存 Zuno 十一个逻辑模块的正式 Target 架构。每个逻辑模块只有一份正式模块架构文档；`.agent/modules/` 只保存字节级一致的 Agent 镜像。

## 规范优先级

```text
全局不可变原则与已接受 ADR
→ 对应领域模块的唯一正式 Target 文档
→ 总架构的跨模块集成视图
→ 已确认 Program
→ 代码、Migration、测试、Trace 与 Eval
```

总架构不能覆盖模块 Owner 的规范性 Contract。跨模块冲突必须修改总架构、协调模块文档，或通过 ADR 解决，不能保留两套事实。

## 十一个模块

| 编号 | 模块 | 唯一正式文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | [`01-product-surface.md`](./01-product-surface.md) | 单一完整实施级 Target 架构 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](./02-input-document-ingestion.md) | 单一完整实施级 Target 架构 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](./03-knowledge-agentic-graphrag.md) | 单一完整实施级 Target 架构 |
| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) | 单一完整实施级 Target 架构 |
| 05 | Memory & Context | [`05-memory-context.md`](./05-memory-context.md) | 单一完整实施级 Target 架构 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 单一完整实施级 Target 架构 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 单一完整实施级 Target 架构 |
| 08 | Tool Runtime | [`08-tool-runtime.md`](./08-tool-runtime.md) | 单一完整实施级 Target 架构 |
| 09 | Security | [`09-security.md`](./09-security.md) | 单一完整实施级 Target 架构 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) | 单一完整实施级 Target 架构 |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) | 单一完整实施级 Target 架构 |

## 正式架构文档集

正式设计事实共十三份：

```text
11 × docs/modules/<NN>-<module>.md
1  × docs/architecture/architecture.md
1  × docs/architecture/architecture.html
```

`docs/architecture/README.md` 是目录说明；`architecture-views.md` 是 HTML 的 Mermaid 渲染源。它们是维护支撑文件，不是额外的模块或第二份总架构。

## 状态边界

模块文档描述 Target，不自动证明 Current。Current、Gap、Measurement Blocked 与 Production Readiness 以：

```text
docs/status/production-readiness.md
最新 main 的代码、Migration、测试、Trace、Eval 和运行证据
```

为事实源。

允许的设计完成声明：

```text
design available
internally consistent
contract-complete
implementation-spec-complete
program-ready
```

不得仅凭文档声明：

```text
implementation available
quality proven
production ready
```

## 镜像与验证

十一份正式模块文档都必须有同名字节级镜像：

```text
docs/modules/<file>
.agent/modules/<file>
```

统一验证：

```text
python tools/scripts/verify_architecture_document_set.py
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_architecture_document_set.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

各模块专用 verifier 和 focused tests 继续验证该模块的 Requirement、状态机、Ownership 与完成证据。
