# Zuno 十一个逻辑模块镜像

`.agent/modules/` 保存十一份正式模块架构的字节级镜像；`docs/modules/` 是正式事实源。镜像不能独立修改或覆盖正式文档。

## 规范优先级

```text
全局不可变原则与已接受 ADR
→ 对应领域模块的唯一正式 Target 文档
→ 总架构的跨模块集成视图
→ 已确认 .agent/programs Program
→ 代码、Migration、测试、Trace 与 Eval
```

总架构不能覆盖模块 Owner 的规范性 Contract。跨模块冲突必须修改总架构、协调模块文档，或通过 ADR / 共享 Contract Registry 解决，不能保留两套事实。

## 十一个模块

| 编号 | 模块 | 正式文档 | 唯一 Target 镜像 | 状态 |
| --- | --- | --- | --- | --- |
| 01 | Product Surface | `docs/modules/01-product-surface.md` | [`.agent/modules/01-product-surface.md`](./01-product-surface.md) | 单一完整 Target 架构 |
| 02 | Input / Document Ingestion | `docs/modules/02-input-document-ingestion.md` | [`.agent/modules/02-input-document-ingestion.md`](./02-input-document-ingestion.md) | 单一完整 Target 架构 |
| 03 | Knowledge / Agentic GraphRAG | `docs/modules/03-knowledge-agentic-graphrag.md` | [`.agent/modules/03-knowledge-agentic-graphrag.md`](./03-knowledge-agentic-graphrag.md) | 单一完整 Target 架构 |
| 04 | Model Gateway | `docs/modules/04-model-gateway.md` | [`.agent/modules/04-model-gateway.md`](./04-model-gateway.md) | 单一完整 Target 架构 |
| 05 | Memory & Context | `docs/modules/05-memory-context.md` | [`.agent/modules/05-memory-context.md`](./05-memory-context.md) | 单一完整 Target 架构 |
| 06 | Agent Core / Planning & Control | `docs/modules/06-agent-core-planning-control.md` | [`.agent/modules/06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 单一完整 Target 架构 |
| 07 | Capability / Skill | `docs/modules/07-capability-skill.md` | [`.agent/modules/07-capability-skill.md`](./07-capability-skill.md) | 单一完整 Target 架构 |
| 08 | Tool Runtime | `docs/modules/08-tool-runtime.md` | [`.agent/modules/08-tool-runtime.md`](./08-tool-runtime.md) | 单一完整 Target 架构 |
| 09 | Security | `docs/modules/09-security.md` | [`.agent/modules/09-security.md`](./09-security.md) | 单一完整 Target 架构 |
| 10 | Observability & Eval | `docs/modules/10-observability-eval.md` | [`.agent/modules/10-observability-eval.md`](./10-observability-eval.md) | 单一完整 Target 架构 |
| 11 | Infrastructure | `docs/modules/11-infrastructure.md` | [`11-infrastructure.md`](./11-infrastructure.md)；`.agent/modules/11-infrastructure.md` | 单一完整实施级 Target；唯一 Target 镜像 |

## 本地阅读路径

不同读者不要从同一个入口硬读到底：

| 读者 / 任务 | 推荐路径 | 结束时应知道什么 |
| --- | --- | --- |
| 新 clone 的开发者 | 本 README → `docs/architecture/architecture.md` → `.agent/programs/current.md` | 十一模块 Target、跨模块总图、当前 Program 处于哪个 Phase |
| Runtime 实现者 | 对应模块文档 → `docs/governance/wave1-cross-module-contract-registry.md` → 当前 Phase | Owner、Contract、Failure、Recovery Owner 和允许修改范围 |
| 前端 / 产品实现者 | `01-product-surface.md` → `06-agent-core-planning-control.md` → 当前 Phase 的 Product Surface 任务 | 前端只消费 Projection 和 AvailableAction，不拥有领域事实 |
| RAG / GraphRAG 实现者 | `03-knowledge-agentic-graphrag.md` → `10-observability-eval.md` → Release Gate 相关 Phase | Evidence、Citation、Benchmark 和 blocked-not-measured 的边界 |
| 安全 / 工具实现者 | `09-security.md` → `08-tool-runtime.md` → `07-capability-skill.md` | Proposal、Approval、Effect、Reconciliation 和 Audit 的分工 |

模块文档用于定义 Target，不用于证明 Current。读完模块后必须回到 `.agent/programs/current.md`、`docs/status/production-readiness.md` 和最新测试 / Trace / Eval 证据判断当前实现状态。

## 模块验证入口

```text
python tools/scripts/verify_product_surface_target_protocols.py
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_memory_context_target_protocols.py
python tools/scripts/verify_agent_core_target_protocols.py
python tools/scripts/verify_capability_skill_target_protocols.py
python tools/scripts/verify_tool_runtime_target_protocols.py
python tools/scripts/verify_security_target_protocols.py
python tools/scripts/verify_observability_eval_target_protocols.py
python tools/scripts/verify_infrastructure_target_protocols.py
```

## Wave 1 共享 Contract

Wave 1 的跨模块 Contract 已确认为 `CONFIRMED_TARGET`：

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

共享基线包括 `CrossModuleEnvelopeV1`、`PreparedToolAction`、Security Epoch、Credential / Secret、Audit、Model Usage、Index Publish、Failure Namespace 与 Recovery Ownership。物理实现归 `src/backend/zuno/platform/**`；模块镜像不得复制或改写这些共享事实。

## 单文档治理

### Model Gateway Target 镜像

```text
docs/modules/04-model-gateway.md
.agent/modules/04-model-gateway.md
```

历史 Contract Freeze 与 Operations Conformance 附录已经吸收到唯一主文档，不再维护，不得重新创建。

### Agent Core Target 镜像

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md
```

Target 架构与执行 Program 的边界明确：模块设计在正式文档和镜像，Current → Target 的实施、迁移、切流和收口计划进入 `.agent/programs/`。

### Infrastructure Target 镜像

```text
docs/modules/11-infrastructure.md
.agent/modules/11-infrastructure.md
```

这是唯一 Target 镜像。不得寻找或重新创建 Infrastructure 数据服务、Consistency 或 Lifecycle 分拆规范；原附录已经吸收到唯一主文档，不再维护。

## 正式架构文档集

正式设计事实共十三份：

```text
11 × docs/modules/<NN>-<module>.md
1  × docs/architecture/architecture.md
1  × docs/architecture/architecture.html
```

`docs/architecture/README.md` 是目录说明；`architecture-views.md` 是 HTML 的 Mermaid 渲染源。它们是维护支撑文件，不是额外模块或第二份总架构。

## 状态边界

模块文档描述 Target，不自动证明 Current。Current、Gap、Measurement Blocked 与 Production Readiness 以：

```text
docs/status/production-readiness.md
最新 main 的代码、Migration、测试、Trace、Eval 和运行证据
```

为事实源。

不得仅凭文档声明 `implementation available`、`quality proven` 或 `production ready`。

## 统一验证

```text
python tools/scripts/verify_architecture_document_set.py
python tools/agent/render_architecture.py --check
python tools/scripts/verify_wave1_contract_freeze.py
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_architecture_document_set.py tests/repo/test_docs_entrypoints.py tests/repo/test_wave1_contract_freeze.py -p no:cacheprovider
```
