# RB-ARCH-001 Retest Record

本文件记录 `RB-ARCH-001` 的 Mutation Retest，不重写第一轮 100 问的 Transcript、Question、Score 或 Baseline Evidence。Retest 只验证 Commit A 建立的核心 Claim 是否能经受改变问法、替代方案、Failure、规模和部署约束后的连续攻击。

本轮采用的是**有来源约束的 Target 防守摘要**，不是对历史项目事实的补写。凡是涉及真实上线、实际 Provider、真实团队、真实用户、实际 Benchmark 或生产故障的判断，仍按 `UNKNOWN` / `CURRENT_EVIDENCE_GAP` 保留。

## RETEST-001

### Domain / Control Plane 与 Provider Boundary Mutation Retest

上一轮 Gap：CLUSTER-002、CLUSTER-004、CLUSTER-005、CLUSTER-006、CLUSTER-007、CLUSTER-008、CLUSTER-009、CLUSTER-010

Gap IDs：GAP-004, GAP-005, GAP-008, GAP-009, GAP-010, GAP-011, GAP-012, GAP-013, GAP-014, GAP-015, GAP-016, GAP-017, GAP-018, GAP-019, GAP-020, GAP-022, GAP-023, GAP-024, GAP-025

Change IDs：CHANGE-002, CHANGE-004, CHANGE-006, CHANGE-007, CHANGE-009, CHANGE-010

修复内容：验证 `Zuno Domain / Control Plane + Replaceable Capability Providers` 是否真的改变了原来的“通用能力全部自研”“Graph 必须存在”“目标设计等于当前实现”和“外部 Benchmark 等于 Zuno 质量”的错误因果链。`CHANGE-003`、`CHANGE-005`、`CHANGE-008` 仍是 `PARTIAL` 候选，不作为已完成修复引用；本轮只攻击它们的边界，不把 RAGFlow、OpenViking 或 Onyx 升级为 Final Adopt。

Mutation Variable：问法、反事实替代方案、Provider 成功/失败、Graph 删除、Memory 禁用、LangGraph 替换、Onyx 权限、MVP 规模、单人一周约束、Current/Target 边界。

Mutation Question：如果 WorkBuddy、RAGFlow、Coze、OpenViking、Onyx、LangGraph 或 GraphRAG 分别承担更多通用能力，Zuno 还剩什么；如果 Provider 或外部副作用在提交边界失败，谁拥有最终事实；如果只剩一个客户、一个开发者和一周时间，哪些能力必须留下？

Blue / User Answer：见下方 M01–M25 的逐题防守摘要。答案只使用当前 Canonical Target 和已记录的 Candidate 状态，不把 Target 当作历史实现。

Red Score：不计算会掩盖缺口的单一总分；逐题使用 `PASS` / `REOPEN`，并单独记录仍未证明的 Current Evidence。

Result：PASS

### 复测判定规则

- `PASS`：修复后的架构 Claim 在变体问法下仍能保持同一 Owner、边界和 Current/Target 诚实性；不代表实现、生产或候选 Provider 已被证明。
- `REOPEN`：旧的错误因果链再次出现，例如用“领域特殊”替代 Fit Analysis，用外部产品 Benchmark 替代 Zuno Eval，或把 Provider 输出直接当成 Canonical Fact。
- 本轮没有发现核心 Canonical Claim 的 `REOPEN`。尚未完成的 Spike、Runtime Trace、Fault Test、Benchmark、用户确认和生产证据保持原 Gap 状态，不被本次 `PASS` 关闭。

## 逐题攻击与判定

### M01｜WorkBuddy 已经有 Agent、Memory、Skill、MCP，为什么还需要 Zuno？

- 红队变体：把“有没有通用能力”改成“成熟通用 Agent Surface 已经覆盖全部交互能力，Zuno 是否只是重复造轮子？”
- 蓝队防守摘要：不再声称 Zuno 整体优于 WorkBuddy，也不把 Agent、Memory、Skill、MCP 当差异化。Zuno 的 Target 价值在受治理的 Domain / Control Plane：版本化 Domain Fact、Evidence / Provenance、Finding、Human Decision、Security Gate、Effect Assurance、Recovery 和 Eval Contract。WorkBuddy 可以是入口、Agent Surface 或 Future Skill/MCP/API 调用方。
- 红队判定：`PASS`。原来的“通用平台不够专业”根因没有复现。
- 当前边界：WorkBuddy 集成仍是 `FUTURE_INTEGRATION_CANDIDATE`，不是 Current Integration；Zuno 的用户价值仍需真实任务和用户证据验证。

### M02｜如果 WorkBuddy 直接作为 UI + Agent Surface，Zuno 还剩什么？

- 红队变体：移除 Zuno Native UI 和通用对话入口，只保留 WorkBuddy 作为用户界面。
- 蓝队防守摘要：Zuno 仍拥有 Matter / Review、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct、Plan / RunOutcome、Security Decision、Effect、Audit、Recovery 和 Eval Contract。WorkBuddy 只负责 Surface，不取得这些 Canonical Business Fact 的 Owner 权。
- 红队判定：`PASS`。产品价值不再依赖自己拥有聊天 UI。
- 当前边界：WorkBuddy 作为入口是 Future 结构，不能写入 Current Resume 或 Production Claim。

### M03｜如果 RAGFlow 负责 Ingestion、RAG 和 Agent，Zuno 还拥有什么？

- 红队变体：假定 RAGFlow 已经提供解析、切分、索引、检索、Agent 和 MCP，要求 Zuno 证明不是空壳。
- 蓝队防守摘要：RAGFlow 可以被评估为 `DocumentPipelineBackend` / `RetrievalBackend` 候选，输出解析结果、候选文段、引用或观察；Zuno 仍拥有 SourceObject、DocumentVersion、ParseSnapshot、SourceSpan、EvidenceRequirement、Evidence、Citation Lineage、Finding、权限和 Review Work Product。Provider 的输出必须先规范化，再由 Zuno Canonical Owner 确认。
- 红队判定：`PASS`，但只是 Provider Boundary 的 Target 防守。
- 当前边界：RAGFlow 仍是 `EXTEND_CANDIDATE / TO_REVIEW`；没有 Adapter Spike、Contract Conformance、License/部署和 Benchmark，不能说已经采用。

### M04｜为什么不直接 Fork RAGFlow？

- 红队变体：把“可以通过 Adapter 复用”升级成“那就 Fork 全部产品，拿到 80% 能力”。
- 蓝队防守摘要：先评估 Modification Surface，而不是凭品牌判断。若只需 Parser、Retriever、Prompt 或页面，Fork/Extend 可能合理；若要穿透上游 Domain Model、Runtime/State、Persistence、Security、Failure/Effect 和升级路径，则成为长期 Private Fork。当前策略优先使用 Official Extension Point、API、SDK、MCP、Provider 或 Adapter，并用 G1 Capability Fit、G2 Contract Fit、G3 Modification Surface、G4 Operational/License Fit、G5 Evidence 决策。
- 红队判定：`PASS`。回答不再是无证据的“RAGFlow 不企业级”。
- 当前边界：没有源码级 Fit Analysis 和 Spike，不能把 Fork Fit 结论写成已完成工程决定。

### M05｜为什么不直接 Fork Coze Studio？

- 红队变体：指出 Coze 也有 Agent、Workflow、Knowledge、Plugin、API/SDK 和二次开发，要求说明 Zuno 为什么不以它为母项目。
- 蓝队防守摘要：Coze 可以是完整产品反事实候选；评估重点是 Zuno Domain Fact、Plan/RunOutcome、Evidence、Security、Effect、Recovery 和 Eval Contract 是否需要穿透 Coze 的 Runtime、Persistence、权限和状态机。若穿透面过深，保留其能力或接口比绑定整个上游 Domain 更可控；若 Fit Analysis 证明修改面很浅，不能教条拒绝二开。
- 红队判定：`PASS`。接受“可能二开”的前提，并用 Modification Surface 决策。
- 当前边界：Coze 不被标记为 Adopt；源码、版本、License、部署和 Conformance 仍需研究。

### M06｜OpenViking 已经管理 Memory、Resource、Skill，为什么还需要 Zuno Memory？

- 红队变体：将 Memory Engine 的功能完整性直接等同于法律/企业 Memory 的治理完整性。
- 蓝队防守摘要：Zuno 把 Memory 拆成 Memory Governance 与 MemoryBackend。OpenViking 可以负责存储、层级组织、基础召回、Session Extraction 或 Context Loading；Zuno 仍负责 StructuredObservation、MemoryCandidate、MemoryWriteDecision、MemoryVersion、Scope、Authority、Temporal Validity、Conflict、Supersede、Quarantine、Revocation、Provenance、Security、Applicability 和 ContextPack Policy。
- 红队判定：`PASS`。Engine 与 Governance 的边界能独立解释。
- 当前边界：OpenViking 是 `EXTEND_CANDIDATE / TO_REVIEW`，没有 License、版本、部署和接口 Spike，不能说已采用。

### M07｜OpenViking 自动抽取的用户偏好为什么不能直接成为长期事实？

- 红队变体：把“自动抽取”当成已经完成事实确认，追问为什么还要多一个 Candidate 层。
- 蓝队防守摘要：自动抽取最多产生 Observation/Candidate。写入长期 MemoryVersion 前必须检查来源、权限 Scope、时间有效性、Authority、与旧事实的冲突、Applicability、隐私策略和是否需要用户确认；不满足条件的内容可以留在 Session、Quarantine、Reference-only 或被拒绝。否则一次误抽取、Prompt Injection 或过期偏好就会污染未来 Context。
- 红队判定：`PASS`。原来的“有 Memory API 就等于有可靠长期事实”没有复现。
- 当前边界：Memory Governance 仍是 Target；写入/冲突/污染 Benchmark 尚未完成。

### M08｜如果 MemoryBackend 从 OpenViking 换成 Mem0，哪些 Zuno Contract 完全不变？

- 红队变体：要求给出可替换性边界，而不是泛泛说“都支持 Memory”。
- 蓝队防守摘要：不变的是 Zuno 的 MemoryCandidate、MemoryWriteDecision、MemoryVersion、Scope、Authority、Temporal Validity、Conflict/Supersede、Quarantine/Revocation、Provenance、Security、Applicability、ContextPack 和 UseTrace；变化的是 Backend 的存储、索引、层级上下文、基础召回和 Session Extraction 实现。Provider 迁移时必须通过 SPI、Conformance、重建/退出路径和质量评测。
- 红队判定：`PASS`。替换的是 Engine，不是 Governance Contract。
- 当前边界：OpenViking/Mem0 的具体替换实验未执行，属于 `CURRENT_EVIDENCE_GAP`。

### M09｜如果把 Graph 全删掉，合同审查还能不能完成？

- 红队变体：假定 Graph Store、Graph Extractor 和 Graph Retrieval Backend 全部不可用。
- 蓝队防守摘要：可以完成依赖精确条款、结构定位、关键词、语义相似和企业 Playbook 对照的基本 Review；Knowledge 仍可使用 Structural、Lexical、Dense、Hybrid Retrieval。Graph 被定义为可选 Retrieval Capability，不是 Matter、Review、Evidence 或 Finding 的唯一来源。无法完成的只是某些多跳关系、实体扩展或全局聚合能力，系统应按 Evidence Gap 降级、澄清或拒答。
- 红队判定：`PASS`。产品价值不依赖 Always-On Graph。

### M10｜什么 Query 真的需要 Graph，而不是 Hybrid Retrieval？

- 红队变体：要求给出路由判据，而不是列 GraphRAG 名称。
- 蓝队防守摘要：精确条款号、金额和 Defined Term 的直接命中优先 Structural/Lexical；表达不同但语义相近的内容使用 Dense + Rerank；需要跨 Clause 的 Defined Term、Cross Reference、Exception、实体关系或多跳依赖时，Graph Local/DRIFT 可能有收益；跨文档主题归纳才可能考虑 Global。路由依据是 Query Class、Evidence Requirement、关系依赖、权限、延迟、成本和已验证质量。
- 红队判定：`PASS`。Graph 的适用性被约束到证据需求，不是“越复杂越高级”。

### M11｜如果 Graph 质量比 Hybrid 差，Zuno 会不会自动关闭 Graph？

- 红队变体：加入错误 Relation、版本混淆、延迟超预算和 Graph 召回低于 Hybrid 的 Failure。
- 蓝队防守摘要：Target 策略允许按 Query Class、质量阈值、延迟/成本预算和错误率把 Graph 标为 unavailable/degraded，回退到 Hybrid、Structural、User Clarification 或 Abstain；Graph Relation 不能直接成为 Evidence，必须物化回原始 DocumentVersion/SourceSpan。自动关闭是待实现的 Policy/Health/Eval 行为，不宣称 Current 已经具备。
- 红队判定：`PASS`，并保留实现证据缺口。
- 当前边界：GAP-010/GAP-011 的 Query-Class Benchmark、Hard Case、参数和故障证据仍 `RESEARCH_REQUIRED`，未因本题关闭。

### M12｜如果 LangGraph 被换掉，PlanVersion / RunOutcome 为什么仍然存在？

- 红队变体：把 AgentRuntime Provider 替换成另一套执行引擎，追问 Zuno 是否还需要自己的计划和结果对象。
- 蓝队防守摘要：PlanVersion、StepRun、AgentRun、RunOutcome、Proposal、Final Gate、业务完成和 Security/Budget Constraint 是 Zuno Domain/Control Plane 的业务语义；LangGraph 只拥有 Graph Execution、Checkpoint、Interrupt、Resume Mechanics。换执行引擎只替换控制状态实现，不改变 Review 业务身份、版本化计划、业务完成和最终发布判断。
- 红队判定：`PASS`。
- 当前边界：LangGraph 仍是 Target AgentRuntime Provider；替换 Provider Spike 和 Runtime Conformance 未执行。

### M13｜LangGraph Checkpoint 和 PostgreSQL Domain Fact 冲突时信谁？

- 红队变体：制造“Checkpoint 认为节点完成，但业务事实没有提交”以及“业务 Effect 已成功，Checkpoint 仍停在调用前”两种冲突。
- 蓝队防守摘要：PostgreSQL 是 Review、PlanVersion、Finding、Approval、EffectReceipt 等业务事实的 Canonical Source；Checkpoint 是图执行控制状态，不能冒充 Domain Fact。恢复时必须做 Checkpoint/Domain Fact Reconciliation：缺少业务提交不能伪造完成；外部 Effect 已成功而 Checkpoint 落后时不能重发，应依赖 Idempotency/Receipt/Effect Reconciliation 决定 Resume、Wait、Abort 或人工处理。
- 红队判定：`PASS`。
- 当前边界：该边界是 Target Contract；完整 Trace、Crash Test、迟到分支和替换 Runtime 证据仍属于 GAP-009/GAP-025。

### M14｜如果 Onyx 已经有大量 Connector，为什么 Zuno 还要 Connector 模块？

- 红队变体：把“已有大量连接器”改成“Zuno 自己维护 Connector 没有任何价值”。
- 蓝队防守摘要：Zuno 不必重新实现所有 Connector。Onyx 可以是 `ConnectorBackend` 候选，负责 Driver、Sync Job、Cursor、Polling/Webhook 和源系统认证；Zuno 仍拥有 SourceObject、DocumentVersion、Tenant/Workspace Scope、Access Contract、Permission Projection、Sync Observation、Audit 和 Evidence 引用。模块的价值是 Canonical Source/Permission/Version 边界，不是连接器数量。
- 红队判定：`PASS`。
- 当前边界：Onyx 是 `ADOPT_CANDIDATE / TO_REVIEW`，CE/EE、权限同步、License、退出和覆盖面尚未验证。

### M15｜Onyx Permission Sync 能不能直接成为 Zuno 权限事实？

- 红队变体：假定 Onyx 已同步了源系统权限，要求 Zuno 直接信任其 ACL。
- 蓝队防守摘要：不能直接成为 Zuno Authorization Fact。Onyx 输出的是 Source Permission Observation/Projection，Zuno Security 仍要按 Tenant、Workspace、Matter、DocumentVersion、Data Classification、当前 Security Epoch 和本地 Policy 做重新解释与约束；必须处理版本、删除、延迟、权限撤销和 CE/EE 能力差异。
- 红队判定：`PASS`。Permission Provider 与 Security Canonical Owner 没有混淆。
- 当前边界：实际 Permission Sync 的版本与发行版证据仍未完成。

### M16｜为什么 Eval 必须由 Zuno 自己拥有？

- 红队变体：外部产品已经有 Benchmark 和 Demo，要求直接用它们证明 Zuno 质量。
- 蓝队防守摘要：外部 Benchmark 只能说明 Provider 在其任务和数据上的表现，不能证明 Zuno 的 Evidence Sufficiency、Citation Correctness、Unsupported Claim、Abstention、Finding Quality、Reviewer Agreement、Permission Violation、Effect Correctness、UNKNOWN/Reconciliation、Recovery、Latency 和 Cost。10 必须拥有 Eval Contract、Dataset/Version、Release Gate 和质量证据。
- 红队判定：`PASS`。
- 当前边界：Eval Contract 是 Target；实际 Dataset、运行报告和 Release Gate 仍未建立。

### M17｜如果 RAGFlow Benchmark 很好，为什么不能证明 Zuno 很好？

- 红队变体：把 Provider 的 Recall/Answer Demo 直接等同于 Zuno 的法律 Work Product 质量。
- 蓝队防守摘要：因为 Zuno 的评价单位不是单段相似文本，而是从具体 DocumentVersion/SourceSpan 到 Claim、Evidence、Finding、Human Decision 和 WorkProduct 的完整链路；还要加入权限、版本、拒答、错误 Graph、工具副作用和恢复。RAGFlow Benchmark 可作为 Provider Evidence，但不能替代 Zuno Query-Class、Document-Version、Permission、Failure 和 Work Product 分层评测。
- 红队判定：`PASS`。
- 当前边界：跨候选对比和生产收益仍是 GAP-019/GAP-020/GAP-022/GAP-023。

### M18｜“Provider 不得写 Canonical Fact”在 Runtime 中到底意味着什么？

- 红队变体：要求从调用返回、持久化、版本和审计层面解释，而不是复述一句原则。
- 蓝队防守摘要：Provider 返回只能是 Proposal、Observation、Candidate、Snapshot、Reference 或 Receipt；Zuno Adapter/Owner 负责 Schema/Contract 校验、Source/Version/Permission/Quality 检查、幂等键和审计，然后由对应 Canonical Owner 提交 Domain Fact。Provider 的 HTTP 200、向量写成功或外部系统“看起来完成”都不能直接让 Review、Evidence、MemoryVersion、Approval 或 Effect 进入最终状态。
- 红队判定：`PASS`。
- 当前边界：这是 accepted-target Contract；端到端 Provider Conformance 仍未执行。

### M19｜Provider 成功但 Zuno Commit 失败，如何恢复？

- 红队变体：Provider 已经生成 Candidate/Receipt，但 Zuno Canonical Owner 在提交事务时崩溃、超时或发生版本冲突。
- 蓝队防守摘要：先区分可重建的候选输出与不可逆的外部 Effect。普通 Retrieval/Parsing Candidate 不得因为 Provider 成功就升级为事实；保留 Provider Reference/Attempt，按幂等键重试适配和 Canonical Commit，或重新生成 Snapshot。若涉及外部副作用，则以 ToolAttempt、Provider Operation ID、Receipt 和 Reconciliation 确认实际效果，不能盲目重发。Canonical Commit 失败应让 Run 等待、重试、冲突处理或人工对账，而不是伪造成功。
- 红队判定：`PASS`，但属于 Target Failure Contract。
- 当前边界：完整事务、Outbox/Inbox、Fencing、Fault Test 和 Trace 仍是 GAP-009/GAP-025 的实现证据缺口。

### M20｜Provider 超时但外部副作用实际成功，怎么办？

- 红队变体：发送邮件后客户端超时，Provider 没有返回 Receipt，但邮件已经发出。
- 蓝队防守摘要：ToolAttempt 进入 `UNKNOWN` / Reconciliation Required，不能直接 Retry。Runtime 使用 Idempotency Key、Provider Operation ID、消息查询或目标资源状态确认 EffectReceipt/EffectReconciliation；只有确认未执行或 Provider 明确支持安全幂等后才能重新执行，否则转人工对账。Prepare/Execute Gate、Security Epoch 和 Approval 不因一次超时失效或自动放行。
- 红队判定：`PASS`。
- 当前边界：这不是“邮件已安全发送”的 Current 事实；Provider Conformance 和故障演练尚未完成。

### M21｜11 个模块中哪些是 MVP 必须激活的？

- 红队变体：要求不能用“11 个都重要”逃避范围问题。
- 蓝队防守摘要：11 个是 Logical Ownership，不是 11 个微服务或 11 个第一版全量激活组件。一个最小 Review MVP 至少需要 Product/Matter、DocumentVersion/最低摄取、Evidence Retrieval、Agent Core/Deterministic Plan、Model Gateway、最小 Security、最小 Eval/Observability 和可恢复基础设施；Memory、Graph、复杂 Tool Governance、多租户和生产 DR 可按 Task Profile、风险和证据延期或关闭。07/08 只有在任务需要可控外部动作时才激活。
- 红队判定：`PASS`。模块数量与 Capability Activation、Implementation Maturity 已分离。
- 当前边界：具体 MVP Profile、团队和交付证据仍是 Project Reality/Implementation Gap，不能反推历史版本。

### M22｜如果只有一个客户、一个开发者、一周 MVP，会删掉什么？

- 红队变体：加入最小人力、时间和预算约束，要求给出可交付切片。
- 蓝队防守摘要：保留一个 Matter/DocumentVersion/Review、结构化文档入口、有限的 Lexical/Hybrid Evidence、Hosted Model Provider、Finding/Report 和人工确认；复用成熟 Parser/Index/Runtime 组件。关闭 Graph Global、长期 Memory、多租户委派、复杂外部 Tool、副作用自动执行、GPU、自研 Fine-tuning、Production DR 和大规模 Connector。这样保留的是可验证的 Domain Work Product，而不是 11 个模块的空实现。
- 红队判定：`PASS`，因为回答明确做了 Scope Down。
- 当前边界：这是 Target MVP 候选，不是历史项目的一周交付证明；需要独立 MVP/Eval 任务和用户确认。

### M23｜如果删掉 Long-term Memory，旗舰任务会坏在哪里？

- 红队变体：把 Memory 从系统中完全关闭，检查 Zuno 的核心价值是否仍成立。
- 蓝队防守摘要：基于当前 Contract/Review 的单次合同审查仍可用 Matter、DocumentVersion、当前 Session、Playbook、Evidence 和 Human Review 完成；被削弱的是跨 Review 的偏好、历史决策复用、长期经验和跨任务上下文。系统应显式标记 Long-term Memory Disabled，而不是伪造长期事实。Memory 是可按 Profile 启用的能力，不是所有任务的硬前置。
- 红队判定：`PASS`。
- 当前边界：长期 Memory 的真实历史需求和性能收益仍 UNKNOWN；Memory Gap 不因“可禁用”而关闭。

### M24｜如果删掉 Tool Runtime，产品价值还成立吗？

- 红队变体：不允许任何外部写操作，只允许分析和生成文档。
- 蓝队防守摘要：Evidence、Finding、Reviewer Decision、Report 和 Redline 等纯 Work Product 仍能成立；但向邮件、DMS、审批或业务系统执行外部副作用的分支必须不可用或转为人工下载/复制。Tool Runtime 不是所有阅读任务的前置，但它是任何受控外部 Effect 的必要边界；不能让 Agent 直接调用 Provider 绕过 Prepare、Security、Approval、Idempotency 和 Reconciliation。
- 红队判定：`PASS`。
- 当前边界：Tool Governance 的目标架构保留，具体邮件 Provider Conformance 仍是实现证据 Gap。

### M25｜如果所有通用能力都来自开源，Zuno 最小不可替代 Delta 到底是什么？

- 红队变体：同时替换 LangGraph、RAGFlow、OpenViking、Onyx、GraphRAG、模型 Provider、向量数据库和 Graph Store。
- 蓝队防守摘要：仍留下 Domain Task、Matter/Review、DocumentVersion、Claim、Evidence/Provenance、Finding、HumanDecision、WorkProduct、Plan/PlanVersion、RunOutcome、Security Decision、Approval、Effect、Recovery Contract、Audit 和 Zuno Eval Contract。替换 Provider 会改变执行、索引、解析、存储或连接实现，但不应改变这些业务事实、证据、权限、人工决定、外部效果保证和质量闸门。若某 Provider 替换会让这些语义消失，说明 Contract 尚未抽取完整，不能把该 Provider 当作可替换基础设施。
- 红队判定：`PASS`，这是本轮最关键的核心 Claim 检验。
- 当前边界：这证明的是 Target 的最小 Delta 定义，不证明所有 Provider 已完成替换或系统已生产运行。

## Gap 级结果

| 原 Gap / Cluster | 本轮判定 | 说明 |
|---|---|---|
| GAP-004, GAP-005 / CLUSTER-002 | `PASS`（Target 边界） | Build-vs-Buy 不再用“领域特殊”作结论，改用 Provider Boundary 和 G1–G5；源码 Fit、Spike、License、Benchmark 仍 `RESEARCH_REQUIRED`。 |
| GAP-008, GAP-024 / CLUSTER-004 | `PASS`（Scope Down 原则） | 已能在 MVP/单人一周反事实下收缩能力；历史项目规模、真实用户和目标适配仍 UNKNOWN。 |
| GAP-009, GAP-025 / CLUSTER-005 | `PASS`（语义边界） | Provider、Checkpoint、Domain Fact、Effect 和 Recovery 的责任未混淆；Runtime Trace、Fault Test 和实现证据仍 OPEN。 |
| GAP-010, GAP-011 / CLUSTER-006 | `PASS`（架构策略） | Graph 改为 Conditional Evidence Retrieval；Query-Class Benchmark 和质量阈值仍 OPEN。 |
| GAP-012 / CLUSTER-007 | `PASS`（治理边界） | Memory Engine 与 Governance 已分开；实际 Backend、污染测试、召回质量和历史使用仍 OPEN。 |
| GAP-013, GAP-014, GAP-015 / CLUSTER-008 | `PASS`（Target/History 边界） | LangGraph、Model、Fine-tuning 和 Legal Profile 未被本轮写成历史事实；个人贡献、调用 Trace、Artifact 和部署仍需 User Fact Gate。 |
| GAP-016, GAP-017, GAP-018 / CLUSTER-009 | `PASS`（安全语义） | Tool/Permission/Effect/Recovery 的 Canonical Owner 没有被 Provider 替代；安全和 Provider Conformance 证据仍 OPEN。 |
| GAP-019, GAP-020, GAP-022, GAP-023 / CLUSTER-010 | `PASS`（Eval Ownership） | Zuno Eval Contract 与外部 Benchmark 已区分；数据集、运行、成本、压测、线上收益和 Release Gate 仍 OPEN。 |

本表的 `PASS` 是“旧 Root Cause 在本轮目标攻击中没有重新出现”，不是“对应 Gap 已经拥有 Current Evidence”。本轮没有 `REOPEN`，也没有把任何 `PARTIAL` Candidate 变成 `APPLIED`。

## Meta Review

### Baseline Integrity

- 第一轮 `transcript.md`、原始问题、原始评分和 Baseline Evidence 未修改。
- 本轮不是新的 100 问 Campaign，不改变 `question_budget`、`actual_question_count` 或第一轮停止原因。
- 本轮的 25 个 M 编号是 Retest 内部攻击编号，不是新的 Q 编号，也不构成新的 Campaign。

### Core Claim Outcome

本轮验证通过的不是“Zuno 自己实现所有组件”，而是以下更窄的 Claim：

> 即使通用能力由 WorkBuddy、RAGFlow、OpenViking、Onyx、LangGraph、GraphRAG 或其他 Provider 提供，Zuno 仍可通过 Domain / Control Plane 拥有版本化业务事实、Evidence/Provenance、Human Decision、Security、Effect、Recovery 和 Eval Contract。

### Remaining Risk

- `CHANGE-003`、`CHANGE-005`、`CHANGE-008` 仍为 `PARTIAL` / Candidate；RAGFlow、OpenViking、Onyx 均不是 Final Adopt。
- `GAP-009`、`GAP-010`、`GAP-011`、`GAP-012`、`GAP-016`、`GAP-017`、`GAP-018`、`GAP-019`、`GAP-020`、`GAP-022`、`GAP-023`、`GAP-025` 的 Runtime、Security、Benchmark、Fault、Recovery 或生产证据仍未建立。
- 历史合同审查起点、真实用户、团队完整分工、上线、模型部署和 Fine-tuning 仍按事实边界保持 `UNKNOWN`。
- `unsupported_rate`、`unknown_rate`、`current_evidence_missing_rate` 和 `target_not_defined_rate` 本轮不伪造百分比；本轮只给出逐题和逐 Gap 的定性结果。

### 后续状态

本轮 Mutation Retest 完成；不启动 `RB-ARCH-002`，不启动下一轮 Retest，不修改正式架构，不实现 Runtime、Migration、Adapter、Benchmark、Program 或 `SKILL.md`。后续是否进入新的 Campaign，只能在另行定义范围、输入版本和 User Gate 后决定。
