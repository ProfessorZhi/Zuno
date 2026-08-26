# Zuno 总体架构文档

`docs/architecture/` 是 Zuno 唯一的总体架构入口。第一次阅读这里时，不需要先理解全部 Contract、状态机或内部对象；先回答三个问题：**Zuno 为什么需要比普通 RAG 多承担一些责任、这些责任为什么必须分开、系统失败以后靠什么事实恢复。**

如果还不知道项目为什么存在，先读 [`../project/project.md`](../project/project.md)。如果已经理解项目背景，直接进入 [`architecture.md`](architecture.md) 的 Part A。要追某一个责任域，再进入 [`../modules/README.md`](../modules/README.md) 和对应模块 Part A。

## 四个文件分别负责什么

`docs/architecture/` 只保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

- `architecture.md`：唯一总体 Target Architecture 正文。Part A 解释概念设计和因果，Part B 保存跨模块精确工程约束。
- `architecture-views.md`：总体 Mermaid 图源，用图帮助理解，不拥有第二套架构事实。
- `architecture.html`：图形展示入口，消费同一份 Mermaid 源。
- `README.md`：告诉读者从哪里开始、当前设计处在哪个治理阶段，以及怎样区分 Target 和 Current。

不得创建第五个总体架构文件，也不得建立 `.agent/architecture/` 或 `.agent/modules/` 镜像。一个设计只保留一套 Canonical Truth。

## 先理解一个最重要的边界

Zuno 不是“把九个模块都串起来才算一次请求”。简单法律问答可以只做当前授权、知识就绪、检索、模型和发布；复杂分析才需要显式 Runtime、专业 Capability 和正式 Domain Admission；只有现实副作用任务才需要 Effect Control、Approval 和 Reconciliation。

九个模块首先是**事实 Ownership 和失败恢复边界**，不是九个微服务。默认可以运行在模块化 Python 后端和按工作负载拆分的 Worker 中。只有独立吞吐、安全隔离、部署生命周期或故障半径有证据时，才按 ADR-0012 考虑物理拆分。

## Part A 为什么允许很长

Part A 不是 Executive Summary，也不是删掉几个字段后的 Part B。复杂架构要把问题、最简单方案、失败反例、概念边界、恢复、替代方案和 Trade-off 讲清楚，本来就可能需要较长篇幅。

新的 [`../governance/architecture-narrative-quality-standard.md`](../governance/architecture-narrative-quality-standard.md) 明确要求：长度来自概念设计和因果推导，而不是 Object / State / Contract 名称数量。术语用于压缩已经理解的概念，不能代替解释；推荐推理链不是固定标题模板。

因此阅读 Part A 时，应该先记住“为什么这样设计”，再去 Part B 查 `AdmissionReceipt`、`PlanVersion`、`PreparedAction` 等精确对象。

## 当前 Target 的核心思想

总体设计把机器候选、正式业务事实、知识派生、运行控制、现实副作用和安全决定分开，让每一种更强事实都拥有明确 Owner。恢复时先找最强 durable owner fact，再修复 Checkpoint、Cache、Delivery 或 Telemetry projection。

复杂度继续受 Evidence Gate。Native Runtime、GraphRAG、Long-term Memory、Specialist / Multi-Agent、强模型路由和物理服务拆分都不是“有了就永久保留”的能力；09 必须通过 baseline、ablation 和 kill test 证明边际收益。

研究成果也按同样原则进入架构。ADR-0015 接受的是 Research Artifact → stable Capability semantics → versioned Provider → Conformance / Eval → Eligibility → Runtime use 的路径，而不是因为某篇论文、某个开源框架或某项课题组成果存在，就反向制造 Zuno 的业务需求。

## Current、Target、Future 和 Evidence 怎么读

`architecture.md` 与九篇模块主要描述 **Target**。Target 设计完整，不代表代码、数据库、Provider、HA / DR 或生产流程已经存在。

判断 **Current** 必须回到 [`../evidence/`](../evidence/)。Pilot Validation 不等于 Production，设计差异也不等于已经测出优势。没有真实 Eval、容量、恢复演练或安全资格时，应保留 Unknown / Measurement Needed。

历史 Red / Blue 记录解释设计怎样形成，但不重新拥有当前事实。当前阶段先做文档质量提升，不需要为了历史问题机械扩展架构。

## 审查一次架构改动时，先问什么

新增一个 Provider、字段、队列或缓存，通常还不算新的架构问题。真正需要回到总体架构审查的，是它改变了“谁拥有事实、什么算完成、失败以后先相信谁、旧版本怎样继续被解释”这些跨模块语义。

一次改动至少先问五个问题：它解决的真实约束是什么；最简单方案为什么不够；它有没有改变 Owner 或 Authority；失败以后由哪个耐久事实恢复；如果收益没有被测出来，怎样回退或删除。五个问题答不清楚时，先不要用新对象和新服务把不确定性冻结进架构。

反过来，如果只是 ORM 字段、SDK、Provider 地址、内部 Queue、Cache 或部署参数变化，而且既有 Owner、完成证明和恢复语义完全不变，它更可能是实现或 Detail Design 变化。这样可以防止总体架构随着每次工程调整不断抖动。

## 架构稳定不等于实现冻结

Zuno 希望稳定的是少数长期不变量：机器候选不能冒充正式事实；Runtime Checkpoint 不能冒充 Domain Commit；结果未知不能被盲 Retry；新的受保护动作要消费当前安全事实；复杂机制必须允许 simpler baseline 和删除条件。

实现则应该允许持续替换。LangGraph、模型 Provider、索引实现、消息队列、缓存、数据库表和物理部署都可能演进。一个好的逻辑边界应该让这些替换发生时，不需要重新发明业务真相。

因此阅读 Target 时，不要把“当前写了某个技术名词”理解为永久技术绑定。真正需要长期保护的是语义和恢复顺序；具体实现只有在 Evidence 证明其必要时才获得更强约束。

## 九模块当前治理状态

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

`Detail Design Candidate V1` 表示模块已经有足够精度进入冻结前审查，不表示字段、表、enum、Migration、API、服务拆分或实现已经冻结。下一道架构门仍然是 Module Detail Freeze Review；冻结也不自动产生 Implementation Authorization。

## 推荐阅读顺序

第一次建立 mental model：

```text
../project/project.md
→ architecture.md Part A
→ ../modules/README.md
→ 目标模块 Part A
```

需要实施或审查时，再结合 [`../decisions/`](../decisions/) 中的 ADR 进入：

```text
architecture.md Part B
→ 目标模块 Part B / Part C
→ 相关 ADR
→ docs/evidence/
→ docs/governance/
```

如果读完 Part A 只能记住几十个内部名词，却说不清为什么需要这些边界，应该优先修正文档，而不是继续增加 Contract。

## 维护原则

总体架构负责跨模块 Authority 与 Target 整合；模块文档只能细化已接受边界，不能局部改变九模块 Owner、Canonical Legal Kernel、Formal Admission、Knowledge / Domain authority、Retry / Replan / Reconcile、安全政策或 Effect truth。

跨层语义变化才修改 `architecture.md` 或 ADR；模块内部精度下沉到 `../modules/`；Current 证据进入 `../evidence/`；项目历史和 Ownership 叙事进入 `../project/`。图形变化同步 `architecture-views.md` 与 `architecture.html`。

常用验证：

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
