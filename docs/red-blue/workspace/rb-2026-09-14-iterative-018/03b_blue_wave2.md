# Blue Wave 2 — rb-2026-09-14-iterative-018

mode: BATCH_WAVES
input_red_wave2_commit: 889fb67deb6f8394bd81b7a8c2f0e8d3c862f312
answer_count: 28

这一波明确区分 **Current / Historical Evidence** 与 **Target Proposal**。架构改进建议不冒充已经实现。

## Tool / routing

### R2-Q001
**answer:** 如果 `GeneralAgent` 或 middleware 被跨用户复用，而 `user_id` 是可变实例字段，那么只靠“调用时查配置”并不能保证隔离，我前面的结论就只能降级成“查找 API 支持 user_id”。更稳的 Target 是让 `user_id / scope / config snapshot` 来自不可变 `ExecutionContext` 或显式 call arguments，middleware 保持无请求级 mutable state，并用两个用户交错 await 的并发测试证明不串配置。
**classification_hint:** EVIDENCE_GAP + TARGET_PROPOSAL.

### R2-Q002
**answer:** 我会让 Tool/Capability 配置 Owner 产生不可变 `ConfigVersion`，Runtime 在 `Run/PlanVersion/StepRun` 派发时绑定版本引用。普通 retry 继续使用原 pinned version，保证同一次逻辑动作可重放；如果用户显式修改配置并要求生效，则触发 replan/new StepRun，而不是偷偷让旧 retry 换配置。这属于 Target Proposal，4 月历史实现没有这层 version contract。

### R2-Q003
**answer:** 我会拆三种名字：给模型看的 `display_name` 保持短且可读；路由使用稳定 `tool_id = provider/server identity + tool identity`；审计再绑定 `tool_version / provider_version`。LLM schema 不必暴露完整 UUID，可以用可读 alias，但 alias 最终必须唯一映射到 canonical id。这样显示、路由和审计不再用同一个字符串承担三种责任。

### R2-Q004
**answer:** 两层都需要，但职责不同。入口/route 前做 coarse authorization，决定这个用户是否有资格看到/选择某类 Capability；真正执行前由统一 Tool/Effect execution boundary 再做 continuous authorization、配置版本和副作用检查，防止长任务 TOCTOU。历史 direct route 目前没有证明这套完整边界，所以这是架构改进，不是 Current Claim。

### R2-Q005
**answer:** direct route 和 ReAct 不应该各自拥有一套执行逻辑。两条路径只产生同一种 `ToolIntent/PreparedInvocation`，最后统一进入一个 execution gateway；authorization、config resolution、audit、idempotency/effect handling 都在这里完成。route 只负责“选谁、参数候选是什么”，不负责“能不能安全执行”。这样才能避免两条路径安全语义漂移。

### R2-Q006
**answer:** 最终停止权应该在 Runtime budget，而不是 prompt。Prompt 可以提醒模型，但不能作为可靠控制面；Tool middleware 只能报告本次结果。Runtime 应拥有 max steps、wall-clock/token/cost budget、重复调用检测和 cancellation。连续可重试错误超过 policy 后由 Runtime 决定 stop/replan/escalate。历史 `GeneralAgent` 的完整 hard limit 仍未证明。

## GraphRAG

### R2-Q007
**answer:** 最小实验是 threshold sweep + holdout。先按 query class 在 development set 上扫 `GRAPH_PROMOTION_THRESHOLD` 和相关 tier 规则，记录 baseline regression rate、Recall/MRR、chain metrics、latency/cost；选出 Pareto 候选后在未参与调参的 holdout 上验证。只在原 5 条 bad case 上把 6 调好，不能证明它不是过拟合。

### R2-Q008
**answer:** 我会把它做成约束优化，而不是只最大化 Recall：例如最大化 multi-hop quality，同时要求 baseline regression rate 不超过预设上限、单跳 query 不显著退化，并满足 latency/cost budget。具体阈值不能凭空给数字，应由产品风险和 benchmark 分布确定。最后看 Pareto frontier，而不是追一个综合魔法分数。

### R2-Q009
**answer:** 先修 deterministic ranking。相同输入排序抖动会污染四层：eval 无法稳定复现、cache key/value 可能漂移、citation 顺序变化、debug 难以对比。最小改动是在现有 rank key 最后加入稳定的 canonical document/chunk identity 和 version，而不是依赖 retriever 输入顺序。

### R2-Q010
**answer:** 只加 entity type 不够。同名当事人、公司、法规至少还需要 stable entity identity，并结合来源文档、jurisdiction、时间/版本、组织标识等 disambiguation evidence。字符串 alias 只能做候选召回，不能直接完成 identity merge；无法唯一确认时应该保留多个 candidate，而不是强行归一。

### R2-Q011
**answer:** stable entity id 更适合在 ingestion/entity-resolution 阶段生成，因为 retrieval 时才临时编号无法支撑跨查询版本引用。merge/split 不能直接复用旧字符串映射：需要 entity revision、alias/redirect/tombstone 关系，让旧引用可追溯到新 identity，同时保留当时使用的 EntityVersion，避免历史结果被静默改写。

### R2-Q012
**answer:** Knowledge Owner 应该首先拒绝版本不匹配。retrieval result 必须携带 `DocumentVersion / IndexVersion / graph snapshot` 依赖；Context/Runtime 在消费前检查 freshness，正式进入业务事实前 Domain Admission 再验证依赖是否仍有效。旧 graph path 可以留作审计，但不能悄悄作为当前 Evidence 继续使用。Target 文档已有 version/freshness 方向，具体 GraphRAG 历史链未完全实现。

### R2-Q013
**answer:** 正式 benchmark 至少分：单跳事实、关键词/语义检索、多跳关系、实体歧义/同名、版本更新后的 freshness 类。baseline 至少有 BM25、Vector、Hybrid+rerank；GraphRAG 作为增量。质量看 Recall@K/MRR、multi-hop chain hit、citation/evidence correctness；工程看 p50/p95 latency、token/cost、fallback/错误率。kill condition 是：目标 query class 没有稳定增益，或增益不足以覆盖 latency/cost/维护和 regression 风险，就不进入默认路径。

### R2-Q014
**answer:** 简历不主动把 `26.6s vs 19.0s` 当指标卖点。面试官追成本时可以说：“5 条 development smoke 里 GraphRAG 延迟明显更高，大约是 26.6s 对 19.0s，但样本太小，不能当性能 benchmark；它只提醒我们 GraphRAG 必须同时受质量和延迟 gate。”这样信息真实，但不制造稳定性能结论。

## Context / Memory

### R2-Q015
**answer:** “哪些 scope 字段必须存在”应该由 use-case/invocation policy 在进入 Memory Service 前明确，并由 Memory Service fail-closed 校验，而不是让任意 caller 自由决定。可以定义 typed `ScopePolicy`：某类任务要求 user+project+thread，缺一个直接拒绝；跨 thread 的长期 memory 则走另一条明确 policy。`MemoryScope` 只是数据结构，不能替代 policy authority。

### R2-Q016
**answer:** task summary 和 structured memory 都只是 Context Candidate，本身不拥有正式事实 Authority。若冲突涉及案件正式事实，应回到 Domain/Evidence owner；若只是个人偏好/任务经验，由 Memory owner 根据 source、freshness、review decision 做仲裁。未能解决时我倾向把冲突标记为 unresolved 并阻止它们作为确定陈述注入，而不是让 token priority 决定“谁是真的”。必要时可以把冲突本身作为带 provenance 的提示交给模型，但必须明确非权威状态。

### R2-Q017
**answer:** PostgreSQL 里我会让 `scope identity + layer + dedupe_key` 进入唯一性边界，而不是只有裸 `dedupe_key`，否则不同用户/项目可能互相冲突。若允许同一逻辑 Memory 多版本，则唯一键还要区分 active/revision 语义，例如稳定 logical_memory_id + revision，并通过 partial unique constraint 保证同一 scope 只有一个 active revision。具体 Schema 需要结合现有 durable store 再冻结。

### R2-Q018
**answer:** 两个事务从同一 source event set 生成不同 summary，unique constraint 不能判断语义正确。我会先用 canonical source-set hash 建立同一 summarization job identity，再用 optimistic version/CAS 让一个结果成为当前 proposal；不同内容仍保留为 candidate/revision，并由 deterministic merge policy 或 review 选择。不能用“谁先 commit 谁正确”当业务规则。

### R2-Q019
**answer:** ContextPacket 应绑定 `MemorySnapshotVersion / ReviewEpoch` 以及具体 memory refs。Memory Owner 产生版本，ContextOrchestrator 只装配并保存引用；在真正 model invocation 前，由统一 invocation/runtime boundary 向 Memory/Security owner 做 freshness check。若 epoch 已变化，packet 进入 stale，重新 prepare，而不是继续使用旧 APPROVED 快照。

### R2-Q020
**answer:** 最小改动不是只把 dataclass 字段藏起来，而是把 Candidate 与 Review Decision 分开持久化：Candidate 状态不能由普通写路径直接改成 APPROVED；只有受授权的 review service 可以追加 `MemoryReviewDecision`，当前有效状态由 ledger 派生。contract 可以减少直接构造 APPROVED 的便利入口，store/service boundary 再真正 enforce authorization。

### R2-Q021
**answer:** 我会按 revocation 原因分级。隐私删除/权限撤销属于强撤销：Memory/Security 发 invalidation，Runtime 在继续 model/tool/effect 前检查 epoch，当前 run 至少暂停并重新构造 context；已经发出的外部 Effect 不能假装没发生，仍要 reconcile。普通事实更正可以把 packet 标 stale 后 replan。决定严重性的 Authority 在 Memory/Security/Domain 对应 owner，Runtime 负责执行 cancel/replan，不自己判断事实。

## Agent topology / architecture

### R2-Q022
**answer:** 我会用“是否拥有独立决策生命周期”作为主要分界。Subgraph 即使有自己的步骤，只要父 Runtime 决定它何时启动/结束、共享父 checkpoint/policy、没有独立 goal/context recovery，它仍是受控工作流。升级为 Agent 至少要有独立的 planning loop、tool/capability policy、context boundary、checkpoint/recovery 和明确 handoff contract；否则只是换名字。

### R2-Q023
**answer:** 检索 Agent、事实审查 Agent、文书 Agent 都只能产生 proposal/evidence/work product，不能直接写正式案件事实。正式 Domain state 仍由 Domain Owner 的 admission transaction 写入，并记录依赖的 EvidenceVersion、Capability/Agent result refs 和必要的人审。Multi-Agent 改变执行拓扑，不改变 Domain Authority。

### R2-Q024
**answer:** Specialist result 必须带 `run_id + PlanVersion + StepRun/dispatch id + input-version set + SecurityEpoch`。Supervisor/Runtime 收到后先比较当前 active plan 和依赖版本：已被 replan supersede 的结果不进入当前控制流，但可以耐久存档；如果它仍可能对新 plan 有价值，应经过显式 re-evaluation/admission，而不是自动复用。若结果已经触发现实副作用，则即使 stale 也不能简单丢弃，Effect owner 继续 reconcile。

### R2-Q025
**answer:** Specialist 的 working memory 用 `agent_id + task/thread` scope 隔离；全局长期 memory 仍由统一 Memory Owner 管理。Agent 只能提交 MemoryCandidate，不能各自维护一套不可见的长期真值库。dedupe、review、revocation 都围绕统一 logical memory identity/source provenance 做，这样一个 Specialist 的撤销能传播到其它消费者。

### R2-Q026
**answer:** Single logical controller + parallel workers 已经能获得并行执行、step-level retry/failure isolation 和清晰的单写者计划版本；它缺少的是 Specialist 自己长期目标、独立 context/tool policy、自主 replan 和跨任务生命周期。如果业务不需要这些自治性，我会一直停在 controller+workers，因为它更简单。只有测到角色自治本身带来质量/隔离收益，才升级 Persistent Multi-Agent。

### R2-Q027
**answer:** baseline 应至少包含 single Agent、single controller + Subgraph/workers，以及能复用时的 Generic Agent Host；Persistent Multi-Agent 是 challenger。除了任务质量，还看 latency、token/cost、tool-selection error、context leakage、replan/recovery 成功率、duplicate/unknown effects、协调消息量、人工介入、可复现性和 failure blast radius。没有这些系统指标，只看最终回答质量很容易把协调成本藏掉。

### R2-Q028
**answer:** 如果 Generic Host + Zuno Backend 在质量、成本和恢复上不差，我会删/外置自研 planner loop、generic checkpoint、Tool/MCP plumbing、通用 multi-agent supervisor、generic memory/RAG orchestration。Zuno 仍保留法律材料/证据版本与 readiness、Capability 资格与稳定专业语义、Domain Admission/正式事实、必要的 Security/Effect authority、失效传播和法律 Evaluation。执行拓扑可以买，业务 Authority 不能因为换 Host 就消失。

## Blue Wave 2 conclusion

Wave 2 暴露出的架构方向不是“应该全面改成 Multi-Agent”。更强的结论是：**把 Agent topology 从架构 Authority 中降级成可替换、可测量的执行策略**。当前更值得优先补的是统一 Tool execution gate、版本化配置与结果、Memory approval/freshness authority、Knowledge version binding，以及 Runtime 对 stale/late result 的处理。Multi-Agent 只有在 Specialist autonomy、context/tool isolation 或并行 failure ownership 上产生可测收益后再进入默认路径。
