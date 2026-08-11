# Zuno 十一个逻辑模块

`docs/project/modules/` 保存 Zuno 十一个逻辑模块的唯一正式 Target 架构。每个模块只有一份正式模块文档；`.agent/` 不再保存模块镜像。

统一写作和阅读协议：[`docs/governance/architecture-document-writing-standard.md`](../../governance/architecture-document-writing-standard.md)。它约束模块叙事顺序和验证边界，不取代任何模块的 Canonical Contract。

## 规范优先级

```text
全局不可变原则与已接受 ADR
→ 对应领域模块的唯一正式 Target 文档
→ 总架构的跨模块集成视图
→ 已确认 .agent/programs Program
→ 代码、Migration、测试、Trace 与 Eval
```

总架构不能覆盖模块 Owner 的规范性 Contract。跨模块冲突必须修改总架构、协调模块文档，或通过 ADR / 共享 Contract Registry 解决，不能保留两套事实。

## Architecture Target Overlay 与 Provider 边界

Evidence-Driven Retrieval 的新目标已经通过以下 ADR 接受：

```text
docs/decisions/0006-evidence-driven-agentic-graphrag.md
```

该 ADR 定义：Broad Evidence Discovery、Evidence Deliberation、Knowledge Graph + Evidence Reasoning Graph、ClaimEvidenceState、Targeted Evidence Probe、安全停止和 Knowledge Health Diagnosis。

为了避免丢失原 Contract 基线，ADR 0006 继续作为证据检索 Target 输入；本轮同时由 ADR 0007 建立 Reuse-first 与 Provider Boundary。模块文档仍然是 Zuno Canonical Contract 的 Owner，不把 RAGFlow、OpenViking、Onyx、Coze 或其他候选标记为最终 Adopt；当前 `.agent/programs/` 为 `no-active`。

### Reuse First, Build Requires Evidence

11 个模块是 Logical Ownership，不是 11 个必须同时激活或分别部署的服务。通用能力优先通过 Provider / Adapter 接入：

```text
Complete Product → Fork → Reuse Subsystem → Framework → Component → Protocol / SDK → Build Delta
```

每项候选都必须经过 G1 Capability Fit、G2 Contract Fit、G3 Modification Surface、G4 Operational / License Fit、G5 Evidence。Provider 只能输出 Proposal、Observation、Candidate、Snapshot、Reference 或 Receipt；最终 Domain Fact、Evidence、MemoryVersion、RunOutcome、Effect、Audit 和 Eval Gate 仍由 Zuno Canonical Owner 提交。

Runtime 工程收口已完成并归档。下一阶段只做正式设计协调，不启动新的 Runtime Implementation Program：

```text
读取最新 Current
→ Project Workflow Consolidation：合并重复事实源和工作流入口
→ Canonical Architecture Deep Review
→ 将 ADR 0006 协调进 Module 03、总架构和相关模块
→ 更新共享 Contract Registry
→ Architecture Review
→ 用户明确激活新的 Implementation Program
→ 代码、Migration、测试、Trace、Eval 落地
```

这一版本路由不是两套并行事实：已接受 ADR 在冲突处优先；旧模块文档继续服务既有 Program；后续协调 PR 负责将新 Target 收敛回单一 Canonical 模块文档。

## 下一阶段的模块深度要求

下一阶段从面试官视角重新审查十一模块。每个模块不是只给“职责 + 类名 + 目录”，而必须把以下内容写成可追问、可验证的设计：

```text
模块问题与边界
→ Owner、Canonical Fact、输入输出与跨模块 Contract
→ 不变量、状态机、版本和并发规则
→ 完整 Runtime Flow 与关键时序
→ Failure、Retry、Timeout、Recovery、Reconciliation、Idempotency
→ Security、Approval、Budget、Audit 与 Information Flow
→ Trace、Metric、Eval、Release Gate 与证据来源
→ Current / Target / Gap / Future 的严格分层
→ 关键替代方案、取舍和面试追问清单
```

设计审查优先追问：谁拥有事实、谁可以拒绝动作、模型输出是否只是 Proposal、提交点在哪里、失败后如何恢复、重复执行如何证明安全、如何从证据区分“代码存在”和“运行已证明”。没有回答这些问题的文字，不得直接进入新的 Implementation Program。

## 十一个模块

| 编号 | 模块 | 唯一正式文档 | 状态 |
| --- | --- | --- | --- |
| 01 | 企业法律工作怎样进入 Zuno？<br>*Product Surface* | [`01-product-surface.md`](./01-product-surface.md) | 单一完整 Target 架构；实施规格可用 |
| 02 | 一份法律文档怎样变成机器可理解、可追溯的知识？<br>*Input / Document Ingestion* | [`02-input-document-ingestion.md`](./02-input-document-ingestion.md) | 单一完整 Target 架构；实施规格可用 |
| 03 | 一个法律结论怎样找到足够可靠的证据？<br>*Knowledge / Conditional Evidence Retrieval* | [`03-knowledge-agentic-graphrag.md`](./03-knowledge-agentic-graphrag.md) | Evidence-driven Target；Graph 只是条件 Retrieval Backend，ADR 0006 定义证据检索 overlay |
| 04 | Agent 需要模型时，系统怎样选择和治理调用？<br>*Model Gateway* | [`04-model-gateway.md`](./04-model-gateway.md) | 完整模块规范；新的 Evidence 任务边界待架构协调 |
| 05 | Agent 怎样形成长期记忆，又怎样避免记错？<br>*Memory & Context* | [`05-memory-context.md`](./05-memory-context.md) | 单一完整 Target 架构；实施规格可用 |
| 06 | Agent 怎样理解任务、制定计划并控制执行？<br>*Agent Core / Planning & Control* | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 完整 Single Controller 规范；v2 Knowledge 边界待协调 |
| 07 | 平台怎样描述、组合和选择可执行能力？<br>*Capability / Skill* | [`07-capability-skill.md`](./07-capability-skill.md) | 单一完整 Target 架构；实施规格可用 |
| 08 | Agent 怎样安全地执行真实世界操作？<br>*Tool Runtime* | [`08-tool-runtime.md`](./08-tool-runtime.md) | 单一完整 Target 架构；实施规格可用 |
| 09 | 为什么企业敢把敏感数据和操作权限交给 Agent？<br>*Security* | [`09-security.md`](./09-security.md) | 单一完整 Target 架构；实施规格可用 |
| 10 | 我们怎样知道 Agent 做得对不对？<br>*Observability & Eval* | [`10-observability-eval.md`](./10-observability-eval.md) | 完整模块规范；v2 Evidence Eval 边界待协调 |
| 11 | 一个长运行 Agent 系统怎样稳定地跑起来？<br>*Infrastructure* | [`11-infrastructure.md`](./11-infrastructure.md) | 单一完整实施级 Target；唯一正式 Target 文档 |

## 本地阅读路径

不同读者不要从同一个入口硬读到底：

第一次阅读单个模块时，先读该文档的 Part A，按“问题 → 场景 → Owner/边界 → 决策 → 正常流程 → 状态/失败 → 取舍”阅读；需要实现或审查时再读同一文件的 Part B。现有 Part I–IX 标题和 QA 锚点保持稳定，它们是 Part A/Part B 下面的详细章节，不是第二套事实。

| 读者 / 任务 | 推荐路径 | 结束时应知道什么 |
| --- | --- | --- |
| 新 clone 的开发者 | 本 README → `architecture.md` Part A → 感兴趣模块 Part A → `.agent/programs/current.md` | Zuno 是什么、一次任务怎么跑、当前是否存在 active Program |
| Runtime 实现者 | `architecture.md` Part B → 对应模块 Part B → Contract Registry → Status / Evidence | Owner、Contract、Failure、Recovery Owner 和允许修改范围 |
| 前端 / 产品实现者 | `01-product-surface.md` Part A → `06-agent-core-planning-control.md` Part B → Status / Evidence | 前端只消费 Projection 和 AvailableAction，不拥有领域事实 |
| RAG / GraphRAG 实现者 | `03-knowledge-agentic-graphrag.md` Part A → Part B → ADR 0006 → `10-observability-eval.md` Part B | 为什么需要证据闭环、v2 Target、Benchmark 与 blocked-not-measured 边界 |
| 安全 / 工具实现者 | `09-security.md` Part A → `09` Part B → `08` Part B → `07` Part B | Proposal、Approval、Effect、Reconciliation 和 Audit 的分工 |

模块文档用于定义 Target，不用于证明 Current。读完模块后必须回到 `.agent/programs/current.md`、`docs/status/production-readiness.md` 和最新测试 / Trace / Eval 证据判断当前实现状态。

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

ADR 0006 尚未改变 Wave 1 冻结 Contract。后续实现 Program 若需要新增 Evidence、Claim、Probe 或 Diagnosis 跨模块 Contract，必须先更新 Contract Registry 并通过独立 ADR / Program 评审。

## 单文档治理

### Model Gateway 文档边界

```text
docs/project/modules/04-model-gateway.md
```

历史 Contract Freeze 与 Operations Conformance 附录已经吸收到唯一主文档，不再维护，不得重新创建。

### Agent Core 文档边界

```text
docs/project/modules/06-agent-core-planning-control.md
```

Target 架构与执行 Program 的边界明确：模块设计在本目录，Current → Target 的实施、迁移、切流和收口计划进入 `.agent/programs/`。

### Infrastructure 文档边界

```text
docs/project/modules/11-infrastructure.md
```

原数据服务与一致性生命周期附录已经吸收到唯一正式 Target 文档，不再维护，不得寻找或重新创建分拆规范。

## 正式架构文档集

正式设计事实共十二份：

```text
11 × docs/project/modules/<NN>-<module>.md
1  × docs/project/architecture/architecture.md
```

`docs/project/architecture/README.md` 是目录说明；`architecture-views.md` 与 `architecture.html` 是不可拆分的架构图展示配对。它们是维护支撑文件，不是额外模块或第二份总架构。

## 状态边界

模块文档和 accepted-target ADR 描述 Target，不自动证明 Current。Current、Gap、Measurement Blocked 与 Production Readiness 以：

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
