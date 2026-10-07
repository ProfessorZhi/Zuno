# Zuno 模块架构

Zuno 当前的九个责任域是一张事实所有权地图。一次法律任务可能同时涉及材料版本、检索候选、专业分析、长期业务结果、运行控制、模型调用、现实副作用和外部交付。系统发生故障时，恢复顺序取决于哪一个责任域拥有能够证明结果已经成立的耐久事实，而不是哪个模块离用户最近，也不是哪个状态看起来最完整。

当前 Architecture 仍用 01–09 表示责任编号，便于与 ADR、历史审查和跨模块引用对应。目录使用语义名称；编号属于当前 Target decomposition，不属于永久文件系统 schema。

## 研究成果进入真实案件，需要经过一条完整产品链

一项事件抽取、冲突识别、法条推荐或事实—法条对应方法，最初只是 Research Artifact。05 先把它放到稳定的专业能力语义下面，说明输入、输出、适用范围、失败条件和版本；具体论文模型、规则、LLM 或外部服务只是 Provider。03 再把这些能力作用在明确的 DocumentVersion 和 KnowledgeGeneration 上，形成案件研究可复用的候选结构。

04 Runtime 可以围绕这些结构组织长任务、动态检索、并行研究和人工等待。它负责“接下来做什么”，却不拥有专业结论。专业人员在 02 中修改、接受、拒绝或要求补证；需要长期承担责任的结果经过正式业务提交后成为 WorkProduct 和相应的长期业务事实。

真实使用随后给 09 提供最有价值的评测信号：哪些候选经常被专家改动，哪些检索经常缺证，哪个 Provider 在复杂案件上退化，哪种 Agent 机制只增加成本却没有改善结果。09 把经过治理的数据转成 Regression、baseline、ablation 和 release evidence，再反馈给 05 的 Qualification / Eligibility。

```text
Research Artifact
  → 05 Stable Capability / Provider Qualification
  → 03 Case-level knowledge structures and candidates
  → 04 Agent orchestration / research process
  → 02 HumanDecision / Formal WorkProduct
  → 09 Functional Eval / Regression / Ablation
  → 05 re-qualification or retirement
```

这是一条产品化因果链，不是一条固定同步调用链。简单问答可能跳过大部分环节；Eval 也只能消费满足数据治理和标注条件的反馈，不能把每次人工修改自动当作金标准。

## 三种任务，对应三种复杂度

用户问“合同第 8 条写了什么”时，最短合理路径很短：明确 Scope，检查当前授权，确认材料已经就绪，检索稳定原文和引用，受控调用模型，再判断答案是否允许发布。受控 RAG 加普通应用服务能够承担这类任务；Native Runtime、Dynamic DAG、Multi-Agent、Long-term Memory 和 GraphRAG 都没有默认出现的理由。

多材料争议分析会暴露更强约束。系统要先确认材料版本和覆盖范围，再组织多步依赖、专业能力和必要人工复核。检索与模型输出仍然只是候选；只有需要成为长期法律业务事实的结果才进入 02 的 Formal Admission。运行控制可以结束一次任务，却不能替 Domain 宣布正式结果。

如果任务还要向外围系统写入结果，系统必须继续区分“想做什么”和“现实世界发生了什么”。发送前重新检查当前授权、必要审批、幂等和审计；发送后出现 timeout 时先确认远端结果，再决定是否重试。06 拥有现实 Effect truth，01 拥有产品交付语义，08 决定当前动作是否仍被允许。

## 九个责任域来自事实所有权

| 编号 | 责任域 | 用一句人话说明它保护什么 | 文档 |
| --- | --- | --- | --- |
| 01 | Application & Integration | 把内部权威事实组合成稳定请求、发布、交付和失效传播语义 | [application](application/README.md) |
| 02 | Legal Domain & Work Product | 拥有 Matter / DocumentVersion canonical identity，并决定什么最终成为正式、长期、可审计的法律业务事实 | [domain](domain/README.md) |
| 03 | Knowledge & Evidence | 围绕正式材料版本管理可重建知识派生、任务就绪和检索候选 | [knowledge](knowledge/README.md) |
| 04 | Agent Runtime & Control | 控制长任务怎样计划、并行、暂停、重规划和恢复 | [runtime](runtime/README.md) |
| 05 | Capability & Skill | 把研究算法和 Provider 变成稳定、版本化、可替换的专业能力 | [capability](capability/README.md) |
| 06 | Tool Runtime & Effects | 在现实副作用发生前后保护动作身份、结果确认和对账 | [effects](effects/README.md) |
| 07 | Model Gateway | 把模型调用变成受质量、安全、预算和用量约束的依赖 | [model-gateway](model-gateway/README.md) |
| 08 | Security & Governance | 持续回答下一次受保护动作现在是否仍被允许，并拥有 Recall / Lifecycle policy | [security](security/README.md) |
| 09 | Observability & Evaluation | 解释系统发生了什么，并验证复杂度是否值得保留 | [evaluation](evaluation/README.md) |

这些责任域按事实 Ownership 切分，不按技术栈或调用方向切分。默认可以共处模块化 Python 后端。吞吐、安全隔离、故障半径或部署生命周期真正形成证据以后，才需要把逻辑责任进一步拆成独立 Worker、进程或网络服务。

## 跨模块规则由总体架构统一解释

责任地图只回答“谁拥有哪类事实”。Memory / Context 是否形成权威、恢复时为什么先查 Owner fact、版本漂移怎样沿依赖链重新验收，都属于跨模块机制；完整推导保留在 [Overall Architecture](../architecture/architecture.md)，精确不变量和恢复顺序保留在 [Architecture Engineering Reference](../architecture/reference.md)。

这里保留三个导航结论：Context / Memory 不增加新的业务 Authority；跨模块恢复先读取真正拥有结果的耐久事实，再修 Runtime 或 Projection；各责任域判断自己拥有的版本和资格是否仍兼容，Runtime 记录依赖关系但不成为统一 Version Service。具体到某个责任域时，再进入对应 Module Human Narrative。

## 当前设计状态

```text
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

9/9 Detail Design Candidate 只表示 Target Design 已达到冻结前可审查粒度。Current、实现、质量和生产资格继续由 `docs/evidence/` 证明；`DETAIL DESIGN CANDIDATE V1 AVAILABLE` 不等于 `Module Detail Freeze Review` 已通过。

模块入口只维护 Target decomposition 和设计成熟度，不复制快速变化的 implementation-wave 状态。某个责任域今天已经实现到哪一层、哪些 fault window 已经转绿、哪些 blocker 仍存在，由 [`docs/evidence/`](../evidence/README.md) 与对应 scoped governance status 绑定具体 SHA / run 证明。旧负向 probe 在修复后继续作为 History 保留，但不会在这里继续描述为当前失败。

跨模块的事实 Ownership、Completion Proof、Cancellation、Late Result、Idempotency、Recovery、Detail Candidate 与 Freeze Review 记录在 [`reference.md`](reference.md)。各责任域的 Human Narrative 从上表对应的语义目录继续展开。
