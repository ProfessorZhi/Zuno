# Zuno 十一个逻辑模块

`docs/modules/` 保存 Zuno 十一个逻辑模块的唯一正式 Target 架构。每个模块只有一份正式模块文档；`.agent/modules/` 保存同名字节级镜像。

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

| 编号 | 模块 | 唯一正式文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | [`01-product-surface.md`](./01-product-surface.md) | 单一完整 Target 架构；实施规格可用 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](./02-input-document-ingestion.md) | 单一完整 Target 架构；实施规格可用 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](./03-knowledge-agentic-graphrag.md) | 单一完整 Target 架构；实施规格可用 |
| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) | 单一完整 Target 架构；实施规格可用 |
| 05 | Memory & Context | [`05-memory-context.md`](./05-memory-context.md) | 单一完整 Target 架构；实施规格可用 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 单一完整 Target 架构；实施规格可用 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 单一完整 Target 架构；实施规格可用 |
| 08 | Tool Runtime | [`08-tool-runtime.md`](./08-tool-runtime.md) | 单一完整 Target 架构；实施规格可用 |
| 09 | Security | [`09-security.md`](./09-security.md) | 单一完整 Target 架构；实施规格可用 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) | 单一完整 Target 架构；实施规格可用 |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) | 单一完整实施级 Target；唯一正式 Target 文档 |

## 模块验证入口

| 模块 | Verifier | Focused Test |
| --- | --- | --- |
| 01 | `python tools/scripts/verify_product_surface_target_protocols.py` | `pytest -q tests/repo/test_product_surface_target_protocols.py -p no:cacheprovider` |
| 02 | `python tools/scripts/verify_architecture_document_set.py` | `pytest -q tests/repo/test_architecture_document_set.py -p no:cacheprovider` |
| 03 | `python tools/scripts/verify_architecture_document_set.py` | `pytest -q tests/repo/test_architecture_document_set.py -p no:cacheprovider` |
| 04 | `python tools/scripts/verify_model_gateway_target_protocols.py` | `pytest -q tests/repo/test_model_gateway_target_protocols.py -p no:cacheprovider` |
| 05 | `python tools/scripts/verify_memory_context_target_protocols.py` | `pytest -q tests/repo/test_memory_context_target_protocols.py -p no:cacheprovider` |
| 06 | `python tools/scripts/verify_agent_core_target_protocols.py` | `pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider` |
| 07 | `python tools/scripts/verify_capability_skill_target_protocols.py` | `pytest -q tests/repo/test_capability_skill_target_protocols.py -p no:cacheprovider` |
| 08 | `python tools/scripts/verify_tool_runtime_target_protocols.py` | `pytest -q tests/repo/test_tool_runtime_target_protocols.py -p no:cacheprovider` |
| 09 | `python tools/scripts/verify_security_target_protocols.py` | `pytest -q tests/repo/test_security_target_protocols.py -p no:cacheprovider` |
| 10 | `python tools/scripts/verify_observability_eval_target_protocols.py` | `pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider` |
| 11 | `python tools/scripts/verify_infrastructure_target_protocols.py` | `pytest -q tests/repo/test_infrastructure_target_protocols.py -p no:cacheprovider` |

## Wave 1 共享 Contract

Wave 1 的跨模块 Contract 已确认为 `CONFIRMED_TARGET`：

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

共享基线包括 `CrossModuleEnvelopeV1`、`PreparedToolAction`、Security Epoch、Credential / Secret、Audit、Model Usage、Index Publish、Failure Namespace 与 Recovery Ownership。物理实现归 `src/backend/zuno/platform/**`；模块文档不得复制或改写这些共享事实。

## 单文档治理

### Model Gateway 文档边界

```text
docs/modules/04-model-gateway.md
.agent/modules/04-model-gateway.md
```

历史 Contract Freeze 与 Operations Conformance 附录已经吸收到唯一主文档，不再维护，不得重新创建。

### Agent Core 文档边界

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md
```

Target 架构与执行 Program 的边界明确：模块设计在本目录，Current → Target 的实施、迁移、切流和收口计划进入 `.agent/programs/`。

### Infrastructure 文档边界

```text
docs/modules/11-infrastructure.md
.agent/modules/11-infrastructure.md
```

原数据服务与一致性生命周期附录已经吸收到唯一正式 Target 文档，不再维护，不得寻找或重新创建分拆规范。

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
