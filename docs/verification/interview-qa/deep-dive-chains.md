# Architecture Red Team Deep-Dive Chains

本文件是红队发动攻击的入口，不是新的架构正文。每条链都从一个容易回答的母题开始，连续追问 5–15 层，直到暴露行为、算法、状态、版本、权限、失败、恢复或证据方面的薄弱点。

## 使用方式

```text
选择一条 Chain
→ 只读对应 Canonical Part A
→ 逐层回答，不先看 QA Expected Answer
→ 记录在哪一问开始无法继续
→ 判断 Gap Type
→ 修改正确的 Target Document 或转交实现 / Eval
→ 重新攻击并记录 Resolution / Evidence
```

四个诊断维度必须分开：

| 维度 | 含义 |
| --- | --- |
| `architecture_coverage` | 正式文档是否存在对应 Contract 或机制引用 |
| `human_explainability` | Part A 是否能用人话解释输入、判断、算法、异常和取舍 |
| `gap_type` | `NARRATIVE_GAP`、`ARCHITECTURE_GAP`、`CURRENT_EVIDENCE_GAP`、`MEASUREMENT_GAP` 或 `OUT_OF_SCOPE` |
| `resolution_state` | `OPEN`、`RETEST_REQUIRED`、`RESOLVED_BY_PART_A`、`RESOLVED_BY_CONTRACT`、`HELD_FOR_EVIDENCE` 或 `HELD_FOR_MEASUREMENT` |

`architecture_coverage=FULL` 不会自动推出 `human_explainability=YES`。每条链都必须人工复测；没有复测的链保持 `PARTIAL` 或 `UNASSESSED`。

## RT-ARCH-001 总体架构：一次合同审查到底怎样完成

- target_documents: `docs/project/architecture/architecture.md`、`docs/history/superseded-document-taxonomy/project-modules/01-product-surface.md`、`docs/history/superseded-document-taxonomy/project-modules/03-knowledge-agentic-graphrag.md`、`docs/history/superseded-document-taxonomy/project-modules/06-agent-core-planning-control.md`、`docs/history/superseded-document-taxonomy/project-modules/08-tool-runtime.md`、`docs/history/superseded-document-taxonomy/project-modules/09-security.md`
- architecture_coverage: `FULL`（由现有 Q001–Q267 引用矩阵检查）
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. Zuno 解决的法律工作是什么？
2. 为什么产品中心是 Matter 而不是 Chat？
3. 用户上传 V4 时为什么不能跟随 latest？
4. Agent 怎样判断需要 Knowledge、Memory、Tool 还是 Clarification？
5. Finding 为什么不是一段 Assistant Message？
6. 哪些 Claim 必须有 Evidence？
7. 模型为什么只能产生 Proposal？
8. Review、ReviewRun 和 AgentRun 失败时分别怎样变化？
9. 邮件 timeout 为什么不能直接 Retry？
10. PostgreSQL 和 Checkpoint 不一致时谁决定恢复动作？

### Weakness Record

- observed_weakness: 需要把完整法律业务故事与四个面试主战场的控制边界连成一条口述链。
- required_improvement: Part A 必须先讲业务，再讲 Need 分类、证据、Proposal、Tool Gate 和恢复；不能只按模块目录介绍。
- resolution_or_evidence: 已补充总体 Part A 的 Need 分类和按 Owner 定位失败段落；等待红队复测。

## RT-INGEST-001 文档摄取：PDF 怎样成为可引用知识

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/02-input-document-ingestion.md`、`docs/history/superseded-document-taxonomy/project-modules/03-knowledge-agentic-graphrag.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. 为什么不能 PDF → text → 500 Token？
2. Clause Tree 的层级候选从哪里来？
3. 哪些判断用规则，哪些允许模型 Proposal？
4. Defined Term 怎样绑定定义和引用位置？
5. Cross-reference 解析失败时为什么不能让模型猜？
6. OCR 低置信度页怎么办？
7. 两个 ParseSnapshot 哪个可以进入生产 Projection？
8. Redline 的增删改怎样回到 SourceSpan？
9. Chunk 超长时怎么切而不破坏法律语义？
10. Parser 升级为什么不创建新 DocumentVersion？

### Weakness Record

- observed_weakness: 仅出现 Parser、OCR 或 Chunk 名称时，读者仍可能无法说明校验和质量门。
- required_improvement: Part A 解释 Source Profiling、规则/模型分工、Quality Evaluation、Redline 归一化和结构化 Chunking。
- resolution_or_evidence: 已补充 02 Part A 解析链、OCR/Redline/Chunking 段落；Parser Promotion 的正式细节仍以 Part B 为准。

## RT-RAG-001 Agentic GraphRAG：为什么不是直接 Vector Top-K

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/03-knowledge-agentic-graphrag.md`、`docs/history/superseded-document-taxonomy/project-modules/06-agent-core-planning-control.md`、`docs/history/superseded-document-taxonomy/project-modules/10-observability-eval.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. Vector 为什么不够？
2. BM25 解决什么精确匹配问题？
3. Raw Score 为什么不能直接相加？
4. RRF 的输入、输出和 `k` 作用是什么？
5. 为什么 RRF 后还要 Rerank？
6. 什么 Query Feature 才触发 Graph Local？
7. Graph Edge 怎样回到 SourceSpan？
8. Evidence Evaluation 与 Rerank 区别是什么？
9. 缺少 carve-out 时下一轮做什么？
10. 什么时候停止、请求用户或 Abstain？

### Weakness Record

- observed_weakness: “复杂问题跑 Graph”不足以成为可执行策略。
- required_improvement: Part A 说明 Query Features、确定性 Admission、模型 Proposal、Evidence Gap 和停止原因。
- resolution_or_evidence: 已补充 03 Strategy Decision、法律适用性和跨语言原文边界；LanguageContext 正式 Contract 仍需单独冻结。

## RT-MEM-001 Memory：一次对话怎样变成可治理记忆

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/05-memory-context.md`、`docs/history/superseded-document-taxonomy/project-modules/09-security.md`、`docs/history/superseded-document-taxonomy/project-modules/10-observability-eval.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. 为什么聊天记录不等于 Memory？
2. 模型怎样提出 StructuredObservation？
3. 为什么抽取结果不能直接写 Active Memory？
4. Entity Resolution 如何避免把“王总”强行合并？
5. Exact、Structured 和 Semantic Dedup 怎样分层？
6. 换公司是 succession 还是 contradiction？
7. Stale、Superseded、Quarantined 和 Revoked 区别是什么？
8. Recall 到的 Memory 为什么不能直接进 Prompt？
9. Context 太长时先保护什么？
10. 怎么测 Write Precision 和 Stale Injection？

### Weakness Record

- observed_weakness: 记忆系统最容易把抽取、写入、召回和注入混成一个 Vector Top-K。
- required_improvement: Part A 必须分别解释抽取校验、去重校准、时间冲突、召回类型、Protected Set 和压缩顺序。
- resolution_or_evidence: 已补充 05 Part A 算法解释；跨语言 Memory Contract 仍保留为待冻结边界。

## RT-PLAN-001 Agent Core：一句话怎样变成可恢复计划

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/06-agent-core-planning-control.md`、`docs/project/architecture/architecture.md`、`docs/history/superseded-document-taxonomy/project-modules/11-infrastructure.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. Task Understanding 输出哪些东西？
2. Reference Resolution 歧义时怎么办？
3. 为什么简单任务也要 Plan？
4. Complexity Classification 看哪些特征？
5. 什么样的 Step 太大？
6. ReadySet 为什么不等于可以并行？
7. ResourceClaim、Approval、Budget 和 Quota 如何过滤？
8. Retry、Repair、Fallback、Model Escalation 和 Replan 怎么区分？
9. Replan Barrier 怎样处理在途分支？
10. PostgreSQL、Checkpoint 和晚到结果如何恢复？

### Weakness Record

- observed_weakness: 术语齐全时仍可能讲不清 Scheduler 的实际过滤顺序。
- required_improvement: Part A 说明 Task Understanding、ReadySet Admission、资源冲突、公平性和 Replan Barrier 的因果关系。
- resolution_or_evidence: 已补充 06 Part A 任务理解、调度和失败分类；等待逐题复测。

## RT-MODEL-001 Model Gateway：模型到底怎样被选择

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/04-model-gateway.md`、`docs/history/superseded-document-taxonomy/project-modules/10-observability-eval.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. 为什么业务请求 Role 而不是模型名？
2. Hard Constraint Filter 过滤什么？
3. Soft Ranking 比较什么？
4. Provider Health 怎样进入 Circuit Breaker？
5. 429 为什么不是计划错误？
6. Retry Budget 怎样限制 backoff？
7. Fallback 为什么不能跨 Residency？
8. 弱模型什么时候升级？
9. Embedding V3 → V4 为什么不能无感 fallback？
10. ModelAttempt 怎样解释成本和历史结果？

### Weakness Record

- observed_weakness: 只写“按成本、质量、延迟路由”无法说明选择顺序。
- required_improvement: Part A 必须展示 Hard Filter → Health/Circuit → Soft Ranking → Attempt 的行为链。
- resolution_or_evidence: 已补充 04 Part A 路由、健康、Retry、Fallback 和 Embedding 版本段落；等待复测。

## RT-TOOL-001 Tool Governance：从新增 MCP 到发送邮件

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/01-product-surface.md`、`docs/history/superseded-document-taxonomy/project-modules/07-capability-skill.md`、`docs/history/superseded-document-taxonomy/project-modules/08-tool-runtime.md`、`docs/history/superseded-document-taxonomy/project-modules/09-security.md`、`docs/history/superseded-document-taxonomy/project-modules/11-infrastructure.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NONE`
- resolution_state: `RESOLVED_BY_CONTRACT`

### Attack Chain

1. Agent 需要的是 Capability 还是 Tool？
2. 用户能不能指定 Gmail？
3. Tool 怎样进入企业 Catalog？
4. Registration、Installation、Connection、Authorization 有什么区别？
5. ToolGrant 和 DelegationGrant 如何分 Use / Delegate？
6. 父 Grant 撤销后子 Grant 怎么办？
7. ToolVersion 变化时 Grant、Selection 和 PreparedAction 各自怎样失效？
8. Approval 为什么绑定 Action Hash 和 Epoch？
9. Email timeout 为什么进入 UNKNOWN？
10. Worker crash 后怎样避免重复发送？

### Weakness Record

- observed_weakness: 第一轮红队暴露了跨模块 Tool Governance 未冻结的问题。
- required_improvement: 冻结 ToolConnection / ProviderInstance、Grant Lineage、四类 Approval、Operation Scope 和 PreparedAction pinning。
- resolution_or_evidence: `90c064b` 已完成 Contract 冻结；本链当前重点是验证 Part A 是否能准确口述该 Contract，不重新设计 Owner。

## RT-SEC-001 Security：用户权限为什么不能直接传给 Agent

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/09-security.md`、`docs/history/superseded-document-taxonomy/project-modules/01-product-surface.md`、`docs/history/superseded-document-taxonomy/project-modules/08-tool-runtime.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. Authentication 和 Authorization 区别是什么？
2. 用户能看合同为什么 Agent 仍可能不能外发？
3. Tenant、OrgUnit、Workspace 和 Task 怎样组合？
4. Use Scope 和 Delegation Scope 为什么分开？
5. Connection Scope 为什么影响授权？
6. Prompt Injection 为什么不是 System Prompt 问题？
7. Prepare Gate 与 Execute Gate 为什么都要做？
8. Security Epoch 如何传播撤权？
9. ReviewerDecision 和 Runtime Approval 为什么不能互换？

### Weakness Record

- observed_weakness: 容易把“用户允许”简化成 Agent 自动继承全部权限。
- required_improvement: Part A 说明权限交集、委派收缩、撤权传播、不可信内容和四类 Approval。
- resolution_or_evidence: 已补充 09 Part A Delegation 与 Approval 分层；等待红队复测。

## RT-EVAL-001 Eval：我们怎么证明架构和系统真的有效

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/10-observability-eval.md`、`docs/history/superseded-document-taxonomy/project-modules/03-knowledge-agentic-graphrag.md`、`docs/history/superseded-document-taxonomy/project-modules/05-memory-context.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `MEASUREMENT_GAP`
- resolution_state: `HELD_FOR_MEASUREMENT`

### Attack Chain

1. Trace、Log 和 Audit 分别证明什么？
2. Retrieval Recall 够不够？
3. Evidence Sufficiency 怎样标注？
4. Memory Write Precision 怎样测？
5. Retry/Replan 正确性怎样测？
6. UNKNOWN Effect Reconciliation 怎样做故障测试？
7. Feedback 怎样进入 DatasetVersion？
8. Train、Validation 和 Eval 怎样隔离？
9. Candidate Artifact 怎样经过 Release Gate？
10. 没有线上数据时能不能说提升 30%？

### Weakness Record

- observed_weakness: 架构指标已有定义，但真实数据、标注和生产质量尚未自动成立。
- required_improvement: 保持 Dataset Lifecycle、Experiment、Benchmark 和 Release Gate 的边界，不虚构数字；由 Eval Program 补证据。
- resolution_or_evidence: 已补充 10 Part A Dataset Lifecycle；Current Measurement 保持未建立。

## RT-INFRA-001 Infrastructure：Worker、队列和恢复怎样不丢业务

- target_documents: `docs/history/superseded-document-taxonomy/project-modules/11-infrastructure.md`、`docs/history/superseded-document-taxonomy/project-modules/06-agent-core-planning-control.md`、`docs/history/superseded-document-taxonomy/project-modules/08-tool-runtime.md`
- architecture_coverage: `FULL`
- human_explainability: `PARTIAL`
- gap_type: `NARRATIVE_GAP`
- resolution_state: `RETEST_REQUIRED`

### Attack Chain

1. RabbitMQ 消息和 AgentRun 是一回事吗？
2. At-least-once 为什么需要 Inbox？
3. DB Commit 成功、Publish 失败怎么办？
4. ACK 丢失为什么会重投？
5. Lease 与 Fencing 怎样阻止旧 Worker？
6. Checkpoint 和 Domain Commit 不一致怎么办？
7. Projection 挂了是否都能降级？
8. 一万个 PDF 怎样 Backpressure？
9. 一个 Tenant 怎样不占满所有 Worker？
10. Graceful Drain 怎样让新版本接管？

### Weakness Record

- observed_weakness: 基础设施名词容易被误读为业务成功证明。
- required_improvement: Part A 必须把 Transaction、Outbox/Inbox、Lease/Fencing、Checkpoint Reconciliation、Backpressure 和 Drain 串成恢复故事。
- resolution_or_evidence: 已补充 11 Part A 消息链、对账和容量段落；等待故障路径复测。

## 闭环记录模板

新增红队攻击不得只追加一个 QID；使用下面的记录结构：

```text
Question:
Deep Dive:
Observed Weakness:
Gap Type: NARRATIVE_GAP | ARCHITECTURE_GAP | CURRENT_EVIDENCE_GAP | MEASUREMENT_GAP | OUT_OF_SCOPE
Target Document:
Required Improvement:
Resolution State:
Resolution / Evidence:
Retest Result:
```

若 `Gap Type=ARCHITECTURE_GAP`，在 Part B / ADR 确认前停止把它写成已解决；若 `CURRENT_EVIDENCE_GAP` 或 `MEASUREMENT_GAP`，不得通过修改 Target 文档消除。
