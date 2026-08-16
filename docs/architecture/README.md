# Zuno 总体架构文档

`docs/architecture/` 是唯一正式总体架构目录，只能保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 总体架构回答什么

总体架构回答的是：Zuno 怎样把法律领域状态、知识与证据、执行控制、安全、外部效果和可验证交付组合成一套可以恢复、替换和简化的目标架构。

它**不单独回答“为什么项目值得立项”**。这个问题先读 [`../project/product-positioning-and-value.md`](../project/product-positioning-and-value.md)：那里解释法院侧需求、研究成果工程化、通用 Agent 宿主已经能解决什么，以及 Zuno 为什么仍要拥有一部分法律业务语义。Architecture 从这个产品边界继续往下回答“既然这些语义必须由 Zuno 负责，系统应该怎样组织”。

Round 02 已完成，总体 Target Architecture（目标架构）和九个 Logical Responsibility Modules（逻辑责任域）已经冻结。九个责任域是事实和职责边界，不是九个进程、九个数据库或九个微服务。Platform / Infrastructure（平台与基础设施）继续是责任层，Memory / Context（记忆与上下文）继续是可选 Provider 边界。

## 为什么总体架构没有把 Zuno 设计成另一个通用平台

Zuno 当前有意保留一个明确的 Build / Buy / Reuse 边界：通用宿主可以继续负责入口、会话、基础工作流、普通模型调用、基础 RAG 和 UI；Zuno 只有在复杂法律任务需要材料版本、知识就绪、正式 Evidence / Finding / WorkProduct、人工决定、失效传播、外部 Effect Recovery、持续授权或法律 Eval 时，才承担相应专业语义。

这也是为什么简单问答允许留在 Generic Host（通用 Agent 宿主）中，而不是所有请求都强制进入原生 Agent Runtime。Native Runtime、GraphRAG、Long-term Memory、Specialist / Multi-Agent 和物理服务拆分都继续受测量或证据门控制。

因此“Zuno 与通用平台相比有什么优势”不能只在架构图上回答。总体架构能够说明**设计差异**，09 Observability & Evaluation（可观测性与评测）才负责把这些差异通过 A/B、消融、故障和真实任务测量升级为或否定为实际优势。

## 现在进行到哪里

总体架构冻结以后，九篇模块已经从 Design Baseline V1 继续深化到 **Deep Design V2 / Cross-Module Consistency**，并进一步扩充 Human-first Part A。当前每篇模块都包含：

```text
Part A — Human Narrative
  真实问题、正常流程、失败、取舍、当前 / 目标 / 缺口

Part B — Engineering / Agent Reference
  B1–B14 Owner / Contract / State / Failure / Recovery / Persistence / Evidence

Part C — Cross-Module Consistency
  完成证明、因果版本、新鲜度、取消、晚到结果、恢复顺序和一致性测试
```

当前治理状态：

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

下一道门不再是“把九篇文档继续写长”，而是进入字段级 Contract、状态转换 guard、并发 / 版本条件、幂等 namespace、事务边界、Crash Window、Schema Evolution 和 Failure Injection Matrix，再逐模块判断是否达到 Module Detail Freeze Candidate。

## 面对大厂系统设计追问时，Architecture 应该怎样回答

系统设计面试经常不会按模块顺序提问，而会直接问：“QPS 上来怎么办”“为什么不用微服务”“队列积压怎么办”“缓存放哪里”“为什么不用 2PC”“PostgreSQL 和 Checkpointer 为什么分开”“多租户怎么隔离”“HA / DR 怎么做”。这些问题仍然必须遵守同一条原则：**先找事实 Owner，再讨论物理实现。**

总体架构负责解释为什么逻辑责任和物理部署要分离、为什么 Owner 内部可以强一致而跨 Owner 通过 receipt / version / causation 恢复收敛、为什么 Worker / Queue / Cache 都不能成为新的业务 Truth Owner。具体的横向系统设计矩阵已经放在 [`../modules/README.md`](../modules/README.md)；需要回答具体实现和状态条件时，再进入对应模块 Part B / Part C。

当前可以解释 Target 上的扩容、背压、一致性、缓存、异步长任务、成本和恢复策略；但如果被问“实际支撑多少 QPS、多少文件、什么 RPO / RTO”，必须切换到 Evidence。没有正式负载、生产环境和 DR 演练时，不能从架构图反推出生产数字。

## 阅读顺序

如果第一次接触 Zuno，建议：

```text
项目背景
→ 产品定位 / 立项逻辑
→ architecture.md Part A
→ modules/README.md
→ 目标模块 Part A
```

一个不了解 Zuno 的高级工程师只读 `architecture.md` Part A，应该能够解释：为什么简单问答保持简单；复杂法律分析怎样形成正式工作成果；新证据怎样使旧结果失效；外部 POST 超时为什么不能盲重试；Domain Commit 和 Runtime Checkpoint 不一致时怎样恢复；九个责任域为什么这样分。

如果面试官或 Reviewer 进一步追问“为什么不直接用通用平台、为什么项目可以立项、这些差异是否真的带来优势”，回到 [`../project/product-positioning-and-value.md`](../project/product-positioning-and-value.md)。如果开始按具体问题连续盘问，可使用 [`../project/review-question-map.md`](../project/review-question-map.md) 定位到 Project / Architecture / Module / Evidence 的正确 Owner。

如果追问进入并发、缓存、Backpressure（背压）、一致性、容量、HA / DR、成本或数据库恢复，先读 [`../modules/README.md`](../modules/README.md) 的“横向系统设计问题”，再进入 01 / 02 / 03 / 04 / 07 / 08 / 09 的 Part B / Part C。这里的设计回答仍属于 Target；实际容量和生产资格只从 Evidence 回答。

需要实现、测试或审查工程细节时，再读 `architecture.md` Part B、模块 Part B / Part C、相关 ADR 和 Evidence。

Part A 采用中文优先：普通概念能用中文清楚表达时不用多余英文；确实需要代码、框架或正式 Contract 名称时，第一次出现使用 `English（中文）`，后续优先用中文或正式标识。

## 文件职责

- `architecture.md`：跨层 Target、九个责任域、全局不变量、跨模块 Contract、状态、失败和恢复。
- `architecture-views.md`：总体架构的 Mermaid 图源，只做图形表达，不拥有第二套架构事实。
- `architecture.html`：图源展示入口，不维护平行语义。
- `README.md`：目录边界、状态和阅读入口。
- `../project/`：项目为什么存在、产品定位、开发背景和团队故事，不拥有 Target 架构。
- `../modules/`：九个责任域的 Deep Design V2、Human-first Part A 和跨模块一致性设计。
- `../decisions/`：长期有效且具有反转成本的 ADR。
- `../evidence/`：Current 的代码、测试、Migration、Trace、Eval 和运行证据。
- `../history/red-blue/`：架构质询和裁决历史，只解释“为什么”，不拥有当前 Target。

## 一致性规则

总体架构是当前 Target 的整合表达；模块文档只能细化它，不能局部改写九模块 Owner、Canonical Kernel、Formal Admission、Knowledge / Domain authority、Retry / Replan / Reconcile 或安全政策 Owner。较早 ADR 的宽泛措辞如果已被后续 ADR 明确 supersede / refine（取代 / 细化），按后续决定解释。

Project 文档可以解释“为什么值得这样做”，但不能反过来修改 Architecture Truth。产品差异化如果需要新增模块、扩大 Canonical Domain Kernel 或改变跨模块 Owner，必须重新进入正式架构决策流程。

如果模块深化发现必须改变跨层语义，应停止局部设计并记录 Architecture Gap，而不是把新决定藏进 Part B、数据库字段或代码实现。

## 维护与验证

跨层含义变化时修改 `architecture.md`；模块内部设计进入 `../modules/`；产品来源和定位进入 `../project/`；图形关系变化时同步 `architecture-views.md` 与 `architecture.html`。

当前常用验证：

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

不得创建第五个架构文件、`.agent/architecture/` 或 `.agent/modules/` 镜像，也不得建立第二套 Domain / Runtime / Service / State registry。