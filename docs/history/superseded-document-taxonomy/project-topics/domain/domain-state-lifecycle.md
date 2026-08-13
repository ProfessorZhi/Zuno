# Domain State Lifecycle：新证据如何改变业务状态？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 新证据、版本变化和并行执行如何使 Domain State 失效、重算和恢复？
owner: Legal Domain Lifecycle Owner
replaces: old module domain-state sections（Superseded）

## Part A — Architecture Narrative

### 生命周期要回答的核心问题

法律结论不是一次模型输出后永久成立的文本。它依赖材料版本、适用法律、其他事实和人工判断；新的 Evidence 可能只改变一个 Fact，也可能使 Conflict、Dispute、ApplicableLaw、Finding 和已经准备交付的 WorkProduct 失效。生命周期设计的任务，是让系统知道什么变 stale、为什么 stale、谁可以重新评价，以及执行控制状态是否仍可安全恢复。

### Target Scenario：新证据到来

这是 Target Scenario，不是历史事实：

Matter 已经有 FindingVersion F7，Review 也已完成。用户上传新的 DocumentVersion，Knowledge 生成 EvidenceCandidate，Domain Owner 接受为 EvidenceVersion E9。依赖关系显示 F7 使用的 FactVersion F3 受到影响，于是 Fact、相关 Conflict 和 Finding 被标记 stale 或 review_required；旧 WorkProduct 仍可审计，但不能被当作当前结论。系统可以按 EvidenceRequirement 发起新的受限 Agent Run，Run 必须以最新 DomainVersion 为输入，重新经过 Evidence Gate 和 Human Review。

### Domain State 与 Runtime State

Domain State 表达业务世界中已提交的事实、版本、来源、依赖、Review 和 WorkProduct。Runtime State 表达某次 Run 的 Plan、Step、Branch、Reducer、Interrupt、Checkpoint 和预算。二者有关联但不是同一事实源：Checkpoint 可以帮助恢复控制流程，却不能证明 Fact 已提交；Domain Commit 可以成功，即使 Checkpoint 尚未落盘。

### 责任、非责任与执行边界

Domain Owner 负责提交、版本、依赖和 stale 传播；Runtime Owner 负责执行位置、并行分支和恢复位置；Knowledge Owner 负责投影和证据候选；Review Owner 负责 HumanDecision。生命周期文档不负责选择 LangGraph、队列或数据库 Provider，也不把 Event Sourcing、2PC 或 Saga 作为默认答案。

### 主要失败故事

一种失败是 Domain Commit 成功、Checkpoint 写入失败；恢复时必须从 DomainGeneration 和已存在的 Receipt 判断哪些步骤已经完成。另一种失败是 Checkpoint 显示 Node 完成、Domain Transaction 回滚；恢复不能假装业务成功。第三种失败是并行分支基于不同 DomainVersion，Join 只能阻塞、重新读取 Snapshot 或触发 Replan。工具已执行但 Runtime 超时，则必须依据 Provider Operation ID 对账，不能盲目重试。

### 为什么保留版本和失效传播

只保存当前 JSON 可以实现最短路径，但无法表达旧结论为什么失效、哪一条证据触发重算、人工决定针对哪一版材料。版本、依赖和对账增加存储和实现成本，却使复核、审计和恢复可解释。若实际任务不需要跨文档依赖、版本更新和复核，则可以退化为 Matter DB 加简单 Checkpoint；如果它能通过同样的质量和恢复测试，就不保留更复杂的传播图。

### Current / Target / Gap

Current 只由代码、Migration、测试、Trace 或运行证据证明；Target 是 PostgreSQL Canonical Domain State 与独立 Runtime Control State；Hypothesis 是 stale/dependency 能减少错误复用并提高复核效率；Gap 是真实证据更新流程、依赖精度、恢复重放、Review 触发和性能测量。

## Part B — Detailed Architecture Specification

### Version and state Contract

DomainVersion 单调递增并绑定变更来源；PlanVersion 激活后不可变；每个 Step 记录输入 DomainVersion、Snapshot Hash 和 SecurityEpoch。对象状态至少区分 accepted、review_required、stale、rejected 和 superseded；状态语义由 Domain Owner 统一定义，不在 Runtime 或 Knowledge 文档重复。

### Staleness propagation

EvidenceVersion 提交后，依赖索引计算受影响对象集合。直接依赖的 Fact/Conflict/Finding 先进入 stale 或 review_required；下游 Dispute、ApplicableLaw 和 WorkProduct 根据风险策略继续传播。Propagation 必须保留原因、触发版本、affected object identity 和待处理 Run/Review reference。没有依赖证据时不得宣称对象已失效。

New Evidence is an input event, not an automatic conclusion。它首先进入 EvidenceVersion，再按照显式 dependency graph 传播 stale、review_required 或 re-evaluation；是否触发新的 Agent Run 由风险策略、权限和预算决定，不能因为有新材料就默认启动无限循环。

### CAS、并发与触发

Domain Mutation 使用 compare-and-set 检查 expected DomainVersion；冲突返回 version_conflict，不静默覆盖。并行 Agent 分支只能提交 Proposal，Join 前校验同一 Domain Snapshot 或显式重读。Staleness 可以触发新的 AgentRun，但触发记录不等于 Run 成功，也不自动提交 Finding。

### Recovery reconciliation

恢复顺序是：读取最后合法 DomainVersion；比较 Runtime Generation 和 Domain Commit；检查 Queue JobId、EffectReceipt、Provider Operation ID、Outbox/Inbox；根据结果 Resume、Retry、Replan、Quarantine 或 Human Review。若 Domain 已提交而 Checkpoint 落后，禁止重复 Mutation；若 Checkpoint 超前而 Domain 未提交，回到最后合法版本。

Failure 必须带错误类别、触发版本和恢复方向；Retry 只适用于有幂等保证的 transient work，Recovery 不能用 Checkpoint 代替 Domain Commit。

### Audit、security 与验证

每次版本变化记录 Principal、Matter、source reference、dependency reason、Policy Epoch、Trace 和 Review。测试必须覆盖新 Evidence、重复投递、CAS 冲突、分支版本不一致、Checkpoint 丢失、Tool timeout、权限撤销和重放。真正的时延、成本、stale 准确率和恢复成功率仍需 Benchmark/Trace 证明。
