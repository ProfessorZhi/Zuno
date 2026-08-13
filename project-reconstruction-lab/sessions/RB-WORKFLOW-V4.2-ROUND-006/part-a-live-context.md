# Part-A Live Context

本文件是 Round-006 Live Context Payload，只包含 Canonical Part A；Part B 未复制或交付。

## Part A — Architecture Narrative

### 这套架构要解决的业务问题

Zuno 的目标不是增加一个聊天入口，而是帮助司法或专业法律人员把分散的案件材料转化为可追溯、可复核的工作成果。这个任务同时包含业务事实、证据来源、长期执行、人工判断和可能改变外部世界的工具动作。若把它们都压缩进聊天上下文或某个 Agent Checkpoint，用户就无法判断结论基于哪一版材料，也无法解释新证据到来后旧结论为何失效。

### 一个完整的案件分析场景

这是 Target Scenario，不是历史事实：

用户创建 Matter 并上传材料；系统生成带 hash、来源和权限的 DocumentVersion，Knowledge 层解析 SourceSpan 并提供 EvidenceCandidate。Agent Runtime 根据任务形成 Plan，协调证据、争议和法律研究工作，Legal Capability 产生 FactProposal、ConflictProposal 或 FindingProposal。Domain Owner 在证据、版本、权限和必要人工复核通过后提交 Canonical Domain Version；Review 产生 HumanDecision，最终形成 WorkProduct。若需要外部动作，Tool/Security 边界只执行已授权 PreparedAction 并返回 EffectReceipt。

这条路径的关键不是组件数量，而是每一步都知道自己在处理什么类型的对象，以及哪个 Owner 可以把候选提升为正式事实。

### 业务语义、逻辑能力与物理部署

Zuno 的三层关系是：

Product / Domain：定义 Matter、Evidence、Finding、Review 和 WorkProduct 等业务语义；
Logical Capability：定义检索、法律智能、规划、工具、安全和评测等可替换能力；
Physical Service / Deployment：承载 API、长任务、重型 Worker、对象存储和索引 Provider。

本文将第二层称为 Logical Capability Architecture，将第三层称为 Physical Service / Deployment Architecture。上一阶段的 11 Logical Modules + 1 Architecture 只属于 History，不是当前物理服务清单。

业务语义需要稳定，计算 Provider 可以替换，Agent Profile 可以组合。Logical Capability 不等于 Service，Service 不等于 Process，Process 不等于 Container，也不等于团队。这个分离使 WorkBuddy 等外部 Host 可以调用 Legal Backend，也使 Native Runtime 能在公平评测中被保留或删除。

### 责任边界与不拥有的事实

Platform/Domain Owner 拥有 Canonical Business State；Agent Runtime 拥有 Run、Plan、Step、Checkpoint 等控制状态；Knowledge Owner 拥有解析、索引、检索投影和证据候选；Tool Owner 拥有 EffectReceipt 和对账；Security Owner 拥有授权、Approval 和 SecurityEpoch；Eval Owner 拥有数据集、结果和 Release Decision。

任何 Provider、Queue、Checkpoint、Memory 或 Graph 都不能直接声称法律事实。它们不负责创建 FindingVersion、HumanDecision 或 WorkProduct。跨边界只传 Proposal、Candidate、Reference、Snapshot、Receipt 或明确版本的 Query Result。

### 为什么需要这些边界

最小替代方案是 WorkBuddy 或其他 Host 加 Legal Backend；另一个替代方案是模块化 Python 服务加独立 Worker。Zuno 只有在复杂案件中证明 Domain State、Evidence Gate、Staleness、Human Review 或恢复对账带来可重复收益时，才有理由保留更强的 Native Runtime。Python-only 是目标约束，但 CPU-heavy OCR、Embedding、Graph Build 和 Eval 必须离开 API 请求线程；Microservice 是部署目标，但服务数量仍由独立扩缩容、故障、安全、资源和生命周期证据决定。每个候选都要回答 Why service? Why not library? Why not worker?。

### 最危险的失败与恢复

最危险的情况是 Domain Commit 已经成功，而 Runtime Checkpoint 仍停在执行前；或者 Tool 已经执行，Queue 又重复投递，Agent 误以为副作用未发生。另一类危险是新 Evidence 使旧 Fact、Conflict 或 Finding stale，但旧 WorkProduct 仍被展示为最终答案。恢复时先读取 Domain Owner 的最后合法版本，再比较 Runtime 控制版本、Knowledge Projection、EffectReceipt 和当前授权；只有在这些边界完成对账后，才选择 Resume、Retry、Replan 或 Human Review。这个顺序会牺牲一部分恢复速度，却避免把 HTTP 200、Queue ACK 或 Checkpoint 误当成业务成功。

### 取舍与反转条件

这套架构付出的成本是版本、跨服务序列化、可观测性、恢复测试和部署运维复杂度。它换取的是业务状态不被 Runtime Provider 污染、证据链可追溯、外部动作可审计和服务资源可以隔离。若 A/B/C Benchmark 显示 C 与 B 没有稳定增益，应缩减 Native Runtime；若 Hybrid RAG 已经覆盖 Graph 任务，应让 Graph 退为条件 Provider；若模块化服务加 Worker 已满足同样的隔离和恢复语义，应合并服务。当前代码只证明部分 Python/FastAPI/Worker 表面；服务收益、质量收益、安全证明和生产状态仍属于 Current、Target、Hypothesis、Future 或 History 边界中的 Gap。

<!-- PART_B_EXCLUDED_FROM_LIVE_CONTEXT -->
