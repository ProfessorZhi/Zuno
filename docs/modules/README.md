# Zuno 模块架构

九个模块首先是一张**责任地图**：当一次法律任务跨越材料、模型、专业分析、正式结果、现实副作用和外部交付时，哪一类事实由谁最终负责，失败以后先相信谁。它们不是九段固定流水线，也不是九个微服务。

第一次阅读本目录，不需要先记 `AdmissionReceipt`、`PlanVersion`、`PreparedAction` 等内部对象。先理解三条任务路径和九个责任域为什么存在；真正实施时再进入每篇 Part B / Part C 查精确 Contract、状态和 Crash Window。

当前 Architecture 仍用 01–09 表示责任编号，便于与 ADR、历史审查和跨模块引用对应。物理目录不再把编号写进文件名：目录名表达长期责任语义，编号只属于当前 Target decomposition。

## 先用三条任务路径建立 mental model

### 简单法律问答

用户问“合同第 8 条写了什么”时，最短合理路径是：明确 Scope，检查当前授权，确认所需材料已经就绪，检索原文和稳定引用，受控调用模型，最后检查答案是否可以发布。

这条路径不默认需要 Native Runtime、Dynamic DAG、Multi-Agent、Long-term Memory 或 GraphRAG。通用 Host 如果遵守同样的安全、知识和发布边界，也完全可以承担会话和 UI。

### 复杂法律分析

多材料争议分析开始需要显式控制：系统先确认材料版本和知识覆盖，再由 Runtime 组织多步依赖、并行专业能力和必要人工复核。检索和模型产生的内容仍然只是候选，只有需要成为长期法律业务事实的结果才进入 02 Formal Admission。

这里最重要的不是“经过多少 Agent”，而是运行控制、专业计算和正式业务事实始终保持三个边界。Runtime 可以完成任务，但不能替 Domain 宣布正式结果。

### 带现实副作用的任务

如果系统要向外围法院系统提交结果，问题从“算得对不对”增加到“现实世界到底发生了什么”。动作发送前要重新确认授权、必要审批、幂等和强制审计；发送后 timeout 时先对账，禁止因为本地没有响应就盲重试。

06 负责现实 Effect truth，01 负责产品交付语义，08 负责当前是否允许。三个模块协作，但互不冒充对方的完成事实。

## 九个责任域分别为什么存在

| 编号 | 责任域 | 用一句人话说明它保护什么 | 文档 |
| --- | --- | --- | --- |
| 01 | Application & Integration | 把内部权威事实组合成稳定请求、发布、交付和失效传播语义 | [application](application/README.md) |
| 02 | Legal Domain & Work Product | 决定什么最终成为正式、长期、可审计的法律业务事实 | [domain](domain/README.md) |
| 03 | Knowledge & Evidence | 区分正式材料、可重建知识派生、任务就绪和检索候选 | [knowledge](knowledge/README.md) |
| 04 | Agent Runtime & Control | 控制长任务怎样计划、并行、暂停、重规划和恢复 | [runtime](runtime/README.md) |
| 05 | Capability & Skill | 把研究算法和 Provider 变成稳定、版本化、可替换的专业能力 | [capability](capability/README.md) |
| 06 | Tool Runtime & Effects | 在现实副作用发生前后保护动作身份、结果确认和对账 | [effects](effects/README.md) |
| 07 | Model Gateway | 把模型调用变成受质量、安全、预算和用量约束的依赖 | [model-gateway](model-gateway/README.md) |
| 08 | Security & Governance | 持续回答下一次受保护动作现在是否仍被允许 | [security](security/README.md) |
| 09 | Observability & Evaluation | 解释系统发生了什么，并验证复杂度是否值得保留 | [evaluation](evaluation/README.md) |

这些责任域按事实 Ownership 切分，不按技术栈切分。默认可以共处模块化 Python 后端；只有吞吐、安全隔离、故障半径或部署生命周期出现证据时才拆物理服务。

## Part A、Part B、Part C 应该怎么读

Part A 可以很长，它负责把概念设计讲透：问题是什么、最简单方案为什么不够、边界如何推导、典型失败怎样恢复、替代方案和删除条件是什么。长度应该来自推理，而不是名词密度。

Part B 把已经理解的设计精确化成 Owner、Contract、状态、事务、幂等、持久化和 Detail Freeze Candidate；Part C 再检查这些语义跨模块以后，完成证明、版本、新鲜度、取消、晚到和恢复是否仍然一致。

如果一个对象名必须先读 Part B 才知道它为什么存在，Part A 应补概念解释；反过来，如果 Part A 开始连续枚举字段、enum 和 crash-window 表格，则应该下沉到 Part B。

当前每个语义目录已经物理分成 `README.md` 与 `reference.md`：README 只保留 Human Narrative；reference 保存 Part B、B14 Detail Candidate 与 Part C。拆分只改变信息密度，不改变 Owner、Authority、Contract、Recovery 或 Current/Target。

> **第一次阅读到这里可以停。** 你现在只需要能说清三条任务路径的复杂度差异、九个责任域分别保护什么，以及什么时候读 Part A / B / C。下一步应按问题选择一到两个 Module Part A，而不是继续顺序背下面的 Ownership 表、Completion Proof、Cancellation、Late Result 和 Recovery Reference。下面开始更偏向架构维护者和跨模块审查。

## 修改一个模块时，先定位事实，不要先画调用链

跨模块设计最容易被“谁调用谁”带偏。A 调 B，并不表示 A 拥有 B 的结果；异步消息也不天然比同步 RPC 更解耦。先问当前变化涉及的事实是什么、由谁最终证明、消费者最多能做什么，再决定它通过函数调用、Queue、Event、数据库查询还是缓存传播。

例如 04 可以调用 02 请求 Formal Admission，但完成证明仍然来自 02；01 可以查询 06 的 Effect，但不能因为自己发起了 Delivery 就拥有现实结果；09 可以订阅所有模块事件，却不会因为信息最全就升级成业务 Authority。调用方向是实现拓扑，事实 Ownership 才是架构边界。

## 模块边界不等于同步 RPC 边界

九个责任域可以先共处一个进程，也可以在以后按吞吐或隔离需要拆开。即使物理共进程，也应该保持 Owner fact、版本和完成证明；即使物理拆成服务，也不意味着每次判断都必须远程同步调用。

对可重建 Projection，可以异步传播；对当前安全门，可以在受保护动作前消费仍有效的 Decision；对正式提交和现实 Effect，则要读取能够证明完成的 durable fact。通信方式应由一致性、延迟和恢复要求决定，而不是由“模块已经画了边界”自动推出。

## 一个跨模块改动至少要通过四个问题

第一，新增事实到底由谁拥有，是否出现两个 Owner；第二，消费者看到什么才算完成，什么明确不能作为证明；第三，Owner 已成功但消费者 Projection 失败时怎样恢复；第四，旧版本、晚到结果和权限变化后，这个事实是否仍然有资格继续使用。

如果四个问题只能靠“大家约定不要出错”回答，说明 Contract 还不够稳；如果为了回答它们必须创建一个全局万能状态表，说明责任边界可能被重新混在一起。Part C 的价值就是在这里检查局部正确的模块设计跨边界后是否仍然成立。

## 当前模块设计状态

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

**9/9 Detail Design Candidate 只表示 Target Design 已达到冻结前可审查粒度。** Current、实现、质量和生产资格继续回到 `docs/evidence/`；`DETAIL DESIGN CANDIDATE V1 AVAILABLE` 不等于 `Module Detail Freeze Review` 已通过。

## 工程 Reference

跨模块的事实 Ownership、Completion Proof、Cancellation、Late Result、Idempotency、Recovery、横向系统设计、Detail Candidate 与 Freeze Review 进入 [`reference.md`](reference.md)。README 到这里结束，第一次阅读不需要继续下钻。
