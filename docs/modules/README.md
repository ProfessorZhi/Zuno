# Zuno 模块架构

Zuno 当前的九个责任域是一张事实所有权地图。一次法律任务可能同时涉及材料版本、检索候选、专业分析、长期业务结果、运行控制、模型调用、现实副作用和外部交付。系统发生故障时，恢复顺序取决于哪一个责任域拥有能够证明结果已经成立的耐久事实，而不是哪个模块离用户最近，也不是哪个状态看起来最完整。

当前 Architecture 仍用 01–09 表示责任编号，便于与 ADR、历史审查和跨模块引用对应。目录使用语义名称；编号属于当前 Target decomposition，不属于永久文件系统 schema。

## 三种任务，对应三种复杂度

用户问“合同第 8 条写了什么”时，最短合理路径很短：明确 Scope，检查当前授权，确认材料已经就绪，检索稳定原文和引用，受控调用模型，再判断答案是否允许发布。受控 RAG 加普通应用服务能够承担这类任务；Native Runtime、Dynamic DAG、Multi-Agent、Long-term Memory 和 GraphRAG 都没有默认出现的理由。

多材料争议分析会暴露更强的约束。系统要先确认材料版本和覆盖范围，再组织多步依赖、专业能力和必要人工复核。检索与模型输出仍然只是候选；只有需要成为长期法律业务事实的结果才进入 02 的 Formal Admission。运行控制可以结束一次任务，却不能替 Domain 宣布正式结果。

如果任务还要向外围法院系统写入结果，系统必须继续区分“想做什么”和“现实世界发生了什么”。发送前重新检查当前授权、必要审批、幂等和审计；发送后出现 timeout 时先确认远端结果，再决定是否重试。06 拥有现实 Effect truth，01 拥有产品交付语义，08 决定当前动作是否仍被允许。

## 九个责任域来自事实所有权

| 编号 | 责任域 | 用一句人话说明它保护什么 | 文档 |
| --- | --- | --- | --- |
| 01 | Application & Integration | 把内部权威事实组合成稳定请求、发布、交付和失效传播语义 | [application](application/README.md) |
| 02 | Legal Domain & Work Product | 拥有 Matter / DocumentVersion canonical identity，并决定什么最终成为正式、长期、可审计的法律业务事实 | [domain](domain/README.md) |
| 03 | Knowledge & Evidence | 围绕 02 的正式材料版本管理可重建知识派生、任务就绪和检索候选 | [knowledge](knowledge/README.md) |
| 04 | Agent Runtime & Control | 控制长任务怎样计划、并行、暂停、重规划和恢复 | [runtime](runtime/README.md) |
| 05 | Capability & Skill | 把研究算法和 Provider 变成稳定、版本化、可替换的专业能力 | [capability](capability/README.md) |
| 06 | Tool Runtime & Effects | 在现实副作用发生前后保护动作身份、结果确认和对账 | [effects](effects/README.md) |
| 07 | Model Gateway | 把模型调用变成受质量、安全、预算和用量约束的依赖 | [model-gateway](model-gateway/README.md) |
| 08 | Security & Governance | 持续回答下一次受保护动作现在是否仍被允许 | [security](security/README.md) |
| 09 | Observability & Evaluation | 解释系统发生了什么，并验证复杂度是否值得保留 | [evaluation](evaluation/README.md) |

这些责任域按事实 Ownership 切分，不按技术栈或调用方向切分。默认可以共处模块化 Python 后端。吞吐、安全隔离、故障半径或部署生命周期真正形成证据以后，才需要把逻辑责任进一步拆成独立 Worker、进程或网络服务。

## 跨模块设计先看谁拥有事实

A 调用 B 并不会把 B 的结果变成 A 的事实。04 可以请求 02 完成 Formal Admission，完成证明仍来自 02；01 可以读取 06 的 Effect 结果，不能因为自己发起 Delivery 就拥有远端现实；09 可以观察全部模块，也不会因为信息最全就升级成业务 Authority。函数调用、Queue、Event 和缓存只是传播方式，Owner fact 才决定恢复时先相信谁。

一个典型故障是 Domain transaction 已经成功，而 Runtime 还没写新的 Checkpoint 就崩溃。重启后如果只相信 Checkpoint，系统可能重复正式提交；正确顺序是先读取 Domain 的耐久完成事实，再修 Runtime projection。外部 POST timeout 也同样不能靠调用方的 `failed` 状态裁决：远端可能已经执行，06 必须保留逻辑动作身份并 Reconcile，确认效果以后上层才能收敛。

跨模块改变最终都要回答同一组因果问题：新增事实由谁最终证明；消费者看到什么才算完成；Owner 已成功而 Projection 失败时怎样恢复；旧版本、晚到结果和权限变化后，事实是否仍有资格继续使用。答案应落在对应 Owner 与 reference Contract 中，而不是新增一张全局万能状态表。

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

跨模块的事实 Ownership、Completion Proof、Cancellation、Late Result、Idempotency、Recovery、Detail Candidate 与 Freeze Review 记录在 [`reference.md`](reference.md)。各责任域的 Human Narrative 从上表对应的语义目录继续展开。
