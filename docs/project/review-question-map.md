<!--
status: canonical-review-question-map
canonical_question: 从产品、架构、工程事实到个人贡献，Reviewer 或技术面试官最可能追问什么，应该去哪里找权威答案？
owner: Project Documentation Owner
source_boundary: 本文只做问题路由和回答边界，不创建新的项目事实、Target Architecture 或 Current Evidence
-->

# Zuno 项目与架构审查问题地图

这篇文档不是一套背诵答案，也不重新复制项目、架构和模块正文。它的作用是把一个高级工程师、架构 Reviewer 或技术面试官可能追问的问题，路由到正确的事实源，并提醒回答时哪些地方可以明确说、哪些地方必须保留证据边界。

一个比较可靠的回答结构始终是：

```text
先说事实或问题
→ 再说为什么这样设计
→ 再说系统怎样工作和怎样失败
→ 最后说当前证据、缺口和取舍
```

如果一个问题同时涉及历史项目和当前 Target，先说“历史上能确认什么”，再说“今天的架构怎样解决这个问题”。不要用今天的设计反写过去，也不要用过去的 Demo 证明今天的架构已经完成。

## 1. 产品与立项

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| Zuno 到底是什么？ | 法律智能 Agent 平台；研究成果工程化；面向天津法院智慧平台相关场景；不是整个智慧法院项目 | [项目背景](./project-background.md) |
| 为什么这个项目值得立项？ | 法院侧需求 + LIPLAB 研究资产 + 研究成果到长期专业工作链之间的工程化缺口 | [产品定位与立项逻辑](./product-positioning-and-value.md) |
| 为什么不是普通知识库问答？ | 简单问答可以保持简单；复杂任务需要材料版本、正式证据、人工决定、失效、恢复和外部 Effect | [总体架构 Part A](../architecture/architecture.md) |
| 为什么不用通用 Agent 平台就结束？ | 通用宿主可以继续使用；Zuno 只拥有必须自己负责的法律业务语义 | [产品定位与立项逻辑](./product-positioning-and-value.md) |
| Zuno 和 Dify / Coze / 通用工作流平台的关系是什么？ | 不做无依据“平台做不到”比较；简单任务可直接复用，复杂法律状态和专业后端由 Zuno 承担 | [产品定位与立项逻辑](./product-positioning-and-value.md) |
| 你们真正的差异化是什么？ | Domain State、材料版本 / Readiness、Formal Admission、历史引用、失效传播、Effect Recovery、Research-to-Capability、Legal Eval | [产品定位](./product-positioning-and-value.md) + [模块入口](../modules/README.md) |
| 这些差异已经证明是优势了吗？ | 设计差异已形成；真实质量 / 成本 / 生产优势尚未充分测量 | [Current Evidence](../evidence/README.md) + [09](../modules/09-observability-evaluation.md) |
| 立项以后靠什么判断还值得继续投入？ | 看专业质量、人的效率、工程风险、交付效率和经济性，而不是 Demo 数和框架数量 | [产品定位](./product-positioning-and-value.md) + [09](../modules/09-observability-evaluation.md) |
| 真正可能形成长期优势的是什么？ | 领域 Contract、可复用专业能力、历史引用 / 正式结果、法律 Eval 和恢复经验形成的闭环；不是 LangGraph 本身 | [产品定位](./product-positioning-and-value.md) |
| 什么时候反而不应该用完整 Zuno？ | 一次性简单问答、无长期领域状态 / 高风险 Effect 时，通用宿主可能更合适 | [产品定位](./product-positioning-and-value.md) |
| 项目发展到了什么阶段？ | Internal Demo → 客户侧 Demo → 反馈 → Court-side Testing → Pilot Validation；Production 未建立 | [开发过程](./development-process.md) |
| 真实客户规模、SLA、QPS 是多少？ | 当前没有可靠历史资料，不编造；Pilot 不等于 Production | [事实来源说明](../governance/project-fact-provenance.md) + [Evidence](../evidence/README.md) |

## 2. 总体架构

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 系统整体怎么跑？ | 简单 QA、复杂法律分析、带现实副作用三条主线 | [总体架构](../architecture/architecture.md) + [模块入口](../modules/README.md) |
| 为什么要分九个模块？ | 按事实 Owner 和失败恢复语义切，不按团队 / 微服务切 | [总体架构 Part A/B](../architecture/architecture.md) |
| 九模块是不是九个微服务？ | 不是；逻辑责任域和物理部署分离，拆服务受证据门控制 | [总体架构](../architecture/architecture.md) + ADR-0012 |
| 为什么 Domain State 和 Runtime State 分开？ | 业务正式事实与执行控制状态语义不同；Checkpoint 不能证明正式业务提交 | [02](../modules/02-legal-domain-work-product.md) + [04](../modules/04-agent-runtime-control.md) |
| 为什么不做一张万能状态表？ | 不同 Owner 有不同完成证明、事务边界和恢复锚点 | [模块入口](../modules/README.md) |
| 哪些东西是 Zuno 自建，哪些复用？ | 法律业务语义自建；通用 Host、Model Provider、MCP、Telemetry Provider、基础设施原语优先复用 | [总体架构](../architecture/architecture.md) + [产品定位](./product-positioning-and-value.md) |
| 为什么不是微服务 / Kafka / K8s？ | 当前没有足够证据证明必要；模块化后端 + 必要 Worker 是默认物理起点 | [总体架构](../architecture/architecture.md) + ADR-0012 |
| 你们怎么保证模块边界不会越写越乱？ | 总体 Target + ADR + 模块 Part B/C + semantic validators + unique Owner | [Human-first 标准](../governance/human-first-documentation-standard.md) |
| 哪个文档说了算？ | Project 讲历史；Architecture 讲总体 Target；Modules 细化；Evidence 证明 Current；ADR 约束长期决策 | [docs/README](../README.md) |

## 3. Knowledge / RAG / GraphRAG

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 文件上传后为什么不能直接问？ | 上传成功不等于解析 / OCR / 索引 / 当前任务 Readiness 都完成 | [03](../modules/03-knowledge-evidence.md) |
| KnowledgeGeneration 是什么？ | 一代可重建的知识派生；和正式 DocumentVersion、task-level Readiness 分离 | [03](../modules/03-knowledge-evidence.md) |
| 为什么 Readiness 不是一个 `file.ready=true`？ | Ready 与任务 Scope、材料版本、Serving generation、最低能力要求和安全条件有关 | [03](../modules/03-knowledge-evidence.md) |
| EvidenceCandidate 和 Evidence 为什么分开？ | 检索只提出候选，02 才能正式接纳 Evidence | [03](../modules/03-knowledge-evidence.md) + [02](../modules/02-legal-domain-work-product.md) |
| CitationLineage 和正式引用为什么分开？ | 一个解释“怎么找到”，一个保存“正式成果当时真正采用什么” | [03](../modules/03-knowledge-evidence.md) + [02](../modules/02-legal-domain-work-product.md) |
| 索引重建以后历史引用会不会漂？ | 不应该；正式引用绑定不可变 DocumentVersion / 稳定位置，不依赖 chunk / vector id | [02](../modules/02-legal-domain-work-product.md) |
| 为什么需要 Hybrid / BM25 / Vector / GraphRAG？ | 它们都是可替换 Retrieval Provider；具体 query class 是否受益必须测量 | [03](../modules/03-knowledge-evidence.md) + [09](../modules/09-observability-evaluation.md) |
| 为什么不默认 GraphRAG？ | 成本和复杂度更高，只有特定问题类别测出收益才扩大使用 | [产品定位](./product-positioning-and-value.md) + [09](../modules/09-observability-evaluation.md) |
| Query Rewrite 会不会偷偷扩大权限范围？ | 不允许；改写检索表达不改变 task / resource Scope | [03](../modules/03-knowledge-evidence.md) + [08](../modules/08-security-governance.md) |
| 检索服务降级怎么办？ | 缩小能力、返回 Partial / Blocked、等待或 fallback；不能静默装成完整范围 | [03](../modules/03-knowledge-evidence.md) |

## 4. Agent Runtime / LangGraph

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 为什么用 Agent，而不是一次模型调用？ | 只有复杂任务才需要多步计划、依赖、工具、恢复和人工中断；简单任务不强制 Agent | [04](../modules/04-agent-runtime-control.md) |
| 为什么是 Single Controller？ | 一个 Run 只有一个控制权威，避免多 Agent 同时拥有计划和提交权 | [04](../modules/04-agent-runtime-control.md) |
| 你们是 Multi-Agent 吗？ | 产品可以有多个专业 Agent；单次 Run 默认仍是 Single Controller，Specialist 是 Step / Subgraph 执行方式 | [04](../modules/04-agent-runtime-control.md) |
| 每个任务为什么都要有 Plan？ | 进入原生 Runtime 后，控制、预算、Trace、AnswerPolicy 和 Outcome 都需要可追踪计划；简单任务用单步计划 | [04](../modules/04-agent-runtime-control.md) |
| Dynamic DAG 怎么并行？ | 依赖、输入、资源冲突、副作用、Budget、Quota、Security Gate 都满足的 Ready Step 才并行 | [04](../modules/04-agent-runtime-control.md) |
| 什么情况默认串行？ | 数据依赖、写同一资源、不可逆副作用、排他资源、Replan、Final Synthesis | [04](../modules/04-agent-runtime-control.md) |
| Retry 和 Replan 有什么本质区别？ | Plan 仍正确但执行失败才 Retry；假设 / 依赖 / 能力边界失效才 Replan | [04](../modules/04-agent-runtime-control.md) |
| Reconcile 又是什么？ | 外部现实结果未知时，对账确认实际发生了什么；不是普通重试 | [06](../modules/06-tool-runtime-effects.md) |
| Reflection 每一步都调用模型吗？ | 不是；每个 Action 有 Evaluation、每个 Step 有 Acceptance，Reflection 按失败 / 冲突 / 风险触发 | [04](../modules/04-agent-runtime-control.md) |
| Replan 时旧 Plan 怎么处理？ | PlanVersion 激活后不可变；创建新版本并通过 Replan Barrier，旧分支晚到要重新验收 | [04](../modules/04-agent-runtime-control.md) |
| Checkpointer 保存什么？ | 图控制状态；不保存或替代正式 Domain Truth | [04](../modules/04-agent-runtime-control.md) |
| 为什么 LangGraph 不是架构本身？ | LangGraph 提供 Send / reducer / checkpointer / subgraph 等运行原语，业务 Ownership 仍由 Zuno Contract 决定 | [04](../modules/04-agent-runtime-control.md) |

## 5. 法律领域状态与正式成果

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 为什么只有七个 Canonical Object？ | 先保持最小稳定内核，其他 Event / Conflict / Dispute 等先作为 Proposal / Projection | [02](../modules/02-legal-domain-work-product.md) |
| 为什么不直接建完整法律知识图谱 / 本体？ | 没有生命周期、身份、审计和长期业务必要性的对象不升级成 Canonical State | [02](../modules/02-legal-domain-work-product.md) |
| 模型怎样把结果写进数据库？ | 模型不能直接写正式状态，只能 Proposal；正式准入由 Domain Owner 控制 | [02](../modules/02-legal-domain-work-product.md) |
| AdmissionReceipt 有什么意义？ | 证明指定 run / plan / step 的候选确实导致了一次耐久领域提交 | [02](../modules/02-legal-domain-work-product.md) |
| Domain commit 成功、checkpoint 失败怎么办？ | 读取 matching AdmissionReceipt，以领域事实修复 Runtime | [02](../modules/02-legal-domain-work-product.md) + [04](../modules/04-agent-runtime-control.md) |
| Checkpoint 完成但没有 AdmissionReceipt 呢？ | 不能宣布正式业务提交成功；回查因果并修复 Runtime 推断 | [02](../modules/02-legal-domain-work-product.md) |
| 并发修改怎么避免覆盖？ | expected prior DomainVersion / 等价并发条件，版本冲突后重新读取和判断 | [02](../modules/02-legal-domain-work-product.md) |
| 新证据来了是不是全案重跑？ | 先沿正式依赖做有界重评；无法证明影响边界时扩大 Review，不盲目全量或静默忽略 | [02](../modules/02-legal-domain-work-product.md) |
| WorkProduct 怎么长期可追溯？ | 版本化成果 + 正式 Evidence / Finding / HumanDecision + 历史引用绑定 | [02](../modules/02-legal-domain-work-product.md) |

## 6. Capability / Skill / Research-to-Capability

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| Skill 和 Capability 有什么区别？ | Capability 是稳定专业语义；Skill 更偏实现 / 组合，不自动成为 Canonical Domain Object | [05](../modules/05-capability-skill.md) |
| 论文算法怎么进入产品？ | Research Artifact → Capability contract → versioned provider → Conformance → Eval → Eligibility | [05](../modules/05-capability-skill.md) |
| Provider 能调用就算 Capability 可用吗？ | 不算；schema conformance、专业质量、当前 eligibility、provider availability 分层 | [05](../modules/05-capability-skill.md) |
| Planner 怎么知道 Executor 能做什么？ | 通过 CapabilityRequirement、版本、precondition、cost / latency / security metadata 解析 | [05](../modules/05-capability-skill.md) + [04](../modules/04-agent-runtime-control.md) |
| Provider 503 怎么办？ | 语义没变时可 Retry / 等价 fallback；语义或 schema drift 则重新解析 / Replan | [05](../modules/05-capability-skill.md) |
| 为什么 Capability 不能直接执行 Tool Effect？ | 专业分析语义和现实副作用恢复语义不同，副作用必须走 06 / 08 | [05](../modules/05-capability-skill.md) + [06](../modules/06-tool-runtime-effects.md) |

## 7. Tool Calling / 外部副作用

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| Tool Calling 最大风险是什么？ | 不是“调用失败”，而是调用已经改变现实世界但本地不知道 | [06](../modules/06-tool-runtime-effects.md) |
| HTTP 200 为什么不能等于成功？ | transport success 和业务 effect success 不是同一层事实 | [06](../modules/06-tool-runtime-effects.md) |
| POST timeout 怎么恢复？ | known-not-executed 才可安全 Retry；known-executed 复用回执；unknown 先 Reconcile | [06](../modules/06-tool-runtime-effects.md) |
| 幂等键为什么还不够？ | 同一 key 必须绑定同一 action hash；远端无幂等时还要 query / unique constraint / manual reconciliation | [06](../modules/06-tool-runtime-effects.md) |
| Approval 应该绑定什么？ | 具体 action identity / hash、ToolVersion 和关键动作语义；参数变了旧审批失效 | [06](../modules/06-tool-runtime-effects.md) + [08](../modules/08-security-governance.md) |
| Compensation 和 Reconciliation 有什么区别？ | Reconcile 先确认旧动作发生没有；Compensation 是旧动作已确认后的新反向业务动作 | [06](../modules/06-tool-runtime-effects.md) |
| cancel 时请求已经在路上怎么办？ | cancel 不证明未执行；Outcome Unknown 仍需继续对账 | [06](../modules/06-tool-runtime-effects.md) |

## 8. Model Gateway

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 为什么要模型网关？ | 统一角色、资格、路由、凭证边界、Budget / Quota、Usage / Cost 和 fallback | [07](../modules/07-model-gateway.md) |
| 为什么用 Model Role 而不是写死模型名？ | 业务需要的能力比 Provider 名更稳定；模型替换不应变成业务语义改写 | [07](../modules/07-model-gateway.md) |
| 强模型和弱模型怎么分工？ | 最小充分模型 + 失败升级，复杂规划 / 关键 Reflection 用强模型，提取 / 改写等优先轻模型 | [07](../modules/07-model-gateway.md) |
| fallback 为什么不能随便换模型？ | 必须继续满足角色、质量、安全、数据外发和预算约束 | [07](../modules/07-model-gateway.md) |
| 模型返回合法 JSON 就算成功吗？ | 只证明 schema / transport 层完成；Capability / Step / Domain / Publication 还要各自验收 | [07](../modules/07-model-gateway.md) |
| 为什么不把 Security Gate 交给 LLM？ | 能确定性完成的检索执行、schema、引用、安全和审批门禁优先用代码 | [07](../modules/07-model-gateway.md) |
| Prompt / Chain-of-thought 要不要长期存？ | 业务 Contract 不依赖隐藏推理；敏感正文和秘密也不能默认进入长期 Trace | [07](../modules/07-model-gateway.md) + [09](../modules/09-observability-evaluation.md) |

## 9. Security / Governance

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 为什么入口鉴权还不够？ | 长任务中权限、政策、审批、凭证和数据外发条件可能变化，需要持续授权 | [08](../modules/08-security-governance.md) |
| Authorization、Approval、HumanDecision 有什么区别？ | 权限、执行审批、专业业务判断分别属于不同责任域 | [08](../modules/08-security-governance.md) + [02](../modules/02-legal-domain-work-product.md) |
| 用户权限中途被撤销怎么办？ | 后续新的受保护访问重新消费当前 SecurityEpoch；历史已完成事实不被抹掉 | [08](../modules/08-security-governance.md) |
| Prompt Injection 怎么防？ | 多层门禁：材料只是数据，模型只能 Proposal，工具执行前再做 schema / authorization / approval / audit | [08](../modules/08-security-governance.md) |
| Secret 为什么不能直接写 Checkpoint？ | 恢复只需要 CredentialVersionRef / lease 等引用，明文秘密不进入普通状态和 Trace | [08](../modules/08-security-governance.md) |
| 删除和 Legal Hold 冲突怎么办？ | Future Recall、Retention Policy 和各 Store 的 Physical Purge Completion 分开 | [08](../modules/08-security-governance.md) |
| Policy Engine 挂了是不是先放行？ | 高风险读取、外发、Secret、Effect、正式准入默认 fail closed / review | [08](../modules/08-security-governance.md) |

## 10. Observability / Eval / 生产资格

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| Trace 能不能作为审计证据？ | 普通 Telemetry 不是 Durable Audit，也不是 Business Truth | [09](../modules/09-observability-evaluation.md) |
| 为什么选 OpenTelemetry？ | 用 provider-neutral correlation / telemetry contract 解耦 LangSmith / Grafana / on-prem backend | [09](../modules/09-observability-evaluation.md) |
| LangSmith 在架构里是什么角色？ | Agent / LLM trace + Eval Provider，不是业务事实 Owner | [09](../modules/09-observability-evaluation.md) |
| 法律 RAG 怎么评？ | Evidence Sufficiency、Citation Correctness、Unsupported Claim、Applicability、Reviewer Acceptance 等 | [09](../modules/09-observability-evaluation.md) |
| 为什么不能只用 LLM Judge？ | 需要 deterministic checks、人工标注、真实任务结果和 Judge 校准共同支持 | [09](../modules/09-observability-evaluation.md) |
| 为什么平均分高还不能发布？ | 严重越权、错误引用、重复 Effect 等尾部故障必须单独 gate | [09](../modules/09-observability-evaluation.md) |
| Benchmark 为什么是 BLOCKED？ | 缺正式 runtime / credentials / dataset / attestation 时必须明确受阻，不能用 0 样本假装 PASS | [Current Eval](../evidence/current-eval-baseline.md) |
| Production Ready 了吗？ | 没有；当前明确 NOT_ESTABLISHED | [Evidence README](../evidence/README.md) |
| GraphRAG / Memory / Multi-Agent 值不值得？ | 全部要做消融 / A-B / complexity kill test | [09](../modules/09-observability-evaluation.md) |

## 11. 系统设计：数据、性能、扩展和可靠性

这一组问题是高级后端 / Agent 工程岗位最容易继续追问的地方。回答时要先说 Target 设计，再明确 Current 是否已有负载或生产证据。

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| QPS 上来以后首先扩哪里？ | 不按九模块机械拆服务；先识别 HTTP、知识构建、模型、Eval、Tool 等不同工作类型，再独立扩热点 Worker / Provider capacity | [模块入口：横向系统设计](../modules/README.md) + [总体架构](../architecture/architecture.md) |
| 为什么不是一开始就微服务？ | 同进程边界已经能保 Ownership；只有独立扩缩容、故障 / 安全隔离、可用性或部署生命周期证据才拆网络服务 | [总体架构](../architecture/architecture.md) + ADR-0012 |
| 长任务为什么不能一直占 HTTP 连接？ | 受理、执行、发布是不同事实；复杂任务应支持异步 invocation / status / result，而断开客户端不等于取消 Run | [01](../modules/01-application-integration.md) + [04](../modules/04-agent-runtime-control.md) |
| 队列积压怎么办？ | 显式 Backpressure；限制新工作、暂停 Ready Step、尊重 Provider quota；不能让队列 success 代替业务 success | [模块入口](../modules/README.md) + [04](../modules/04-agent-runtime-control.md) |
| 模型限流或 Provider 容量不足怎么办？ | 07 根据 role / quota / budget / security 做等待、fallback 或升级；fallback 仍需满足角色资格 | [07](../modules/07-model-gateway.md) |
| 哪些地方可以缓存？ | 只缓存可重建 Projection / read optimization；缓存必须受 version / freshness 约束，不能成为 Admission / Approval / Effect truth | [模块入口](../modules/README.md) |
| 缓存命中能不能跳过鉴权？ | 不能；新的受保护使用仍需满足当前 SecurityEpoch / policy | [08](../modules/08-security-governance.md) |
| PostgreSQL 为什么适合保存 Domain State？ | Target 需要事务、版本、幂等和因果回执；具体容量 / schema / index 仍要以模块 B11/B14 和 Migration 设计证明 | [02](../modules/02-legal-domain-work-product.md) |
| 为什么 Checkpoint 不也放进 Domain 表？ | Runtime control 与业务正式事实的完成证明、恢复语义和生命周期不同；可以同一物理 PostgreSQL，但不能同一语义 Owner | [02](../modules/02-legal-domain-work-product.md) + [04](../modules/04-agent-runtime-control.md) |
| 为什么不用跨数据库 2PC？ | Owner 内部用自己的事务给 durable proof；跨 Owner 通过 receipt / version / causation + recovery 收敛，避免全局事务耦合 | [模块入口](../modules/README.md) + ADR-0014 |
| Domain 已提交但 Checkpoint 未写，这算不一致吗？ | 是可预期短暂不一致；matching AdmissionReceipt 是恢复锚点，不重复 Domain commit | [02](../modules/02-legal-domain-work-product.md) + [04](../modules/04-agent-runtime-control.md) |
| 并发两个用户同时改同一事项怎么办？ | expected prior DomainVersion / CAS 等并发条件拒绝静默覆盖；失败后重读最新事实再决定 Retry / Review | [02](../modules/02-legal-domain-work-product.md) |
| 知识索引怎么扩容？ | generation 内 ingestion / OCR / embedding / index item 可并行；Serving pointer 只切到完整校验的一代 | [03](../modules/03-knowledge-evidence.md) |
| 向量库挂了能不能直接返回旧结果？ | 只有旧 generation 仍在允许的 serving / freshness / security 条件下才可显式降级；不能无条件返回 stale projection | [03](../modules/03-knowledge-evidence.md) |
| 如何做多租户 / 案件隔离？ | Security & Governance 拥有授权和数据外发边界；各 Store / retrieval / model / tool 执行边界必须按当前 scope enforcement | [08](../modules/08-security-governance.md) |
| Trace 里可以放 tenant / 案件名方便查吗？ | 默认只传播 opaque correlation ref；敏感业务语义和 Secret 不因为可观测性方便就放进 baggage | [模块入口](../modules/README.md) + [09](../modules/09-observability-evaluation.md) |
| 怎么做限流和预算？ | 入口 admission / 04 调度 Budget / 07 model quota / 06 external quota 各自负责，不能只靠 API Gateway 一个全局 QPS | [01](../modules/01-application-integration.md) + [04](../modules/04-agent-runtime-control.md) + [07](../modules/07-model-gateway.md) |
| P95 很高先优化什么？ | 先用 09 分解 retrieval、model、tool、queue、human wait 等阶段，再按任务类别优化；不要先上缓存或微服务 | [09](../modules/09-observability-evaluation.md) + [模块入口](../modules/README.md) |
| Token 成本怎么控制？ | Model Role、最小充分模型、Budget、并行 / Reflection 触发、Context / Retrieval 控制和复杂度消融共同决定 | [07](../modules/07-model-gateway.md) + [04](../modules/04-agent-runtime-control.md) + [09](../modules/09-observability-evaluation.md) |
| HA 怎么做？ | 目标需定义 DB / object / checkpoint / worker takeover / fencing / effect recovery；当前没有证据支持已完成 HA | [模块入口](../modules/README.md) + [Evidence](../evidence/README.md) |
| DR 的 RPO / RTO 是多少？ | 当前未建立，不编造；Production Readiness 前必须通过明确 profile 和演练证据证明 | [Evidence](../evidence/README.md) + [Operations](../operations/) |
| 你能支撑多少并发 / 多少文件？ | 没有正式负载数据时不能从架构推算生产数字；给出测量方案和瓶颈分解，而不是编一个 QPS | [Current Eval](../evidence/current-eval-baseline.md) + [09](../modules/09-observability-evaluation.md) |

## 12. Current 工程事实与实现深度

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 现在代码到底实现到什么程度？ | 只按 Current Runtime Baseline 和实现证据说，不从 Target 倒推 | [Runtime Baseline](../evidence/current-runtime-baseline.md) |
| 测试怎么样？ | 看具体测试基线；focused docs CI 不能冒充 Full CI 或产品质量 | [Test Baseline](../evidence/current-test-baseline.md) |
| 当前 Eval 结果？ | 正式测量仍受阻；框架存在不等于质量已证明 | [Eval Baseline](../evidence/current-eval-baseline.md) |
| 哪些功能是 Target 还没落地？ | 每个模块 B13 Current / Target / Gap 单独列出 | [模块入口](../modules/README.md) |
| 为什么文档比实现更完整？ | 当前阶段先冻结边界和 Contract，再授权 Codex 实现；设计完成不等于模块完成 | [Human-first 标准](../governance/human-first-documentation-standard.md) |
| 全 CI 通过了吗？ | 只有实际完整 CI 跑过才能这么说；文档 PR 只报告实际 focused 验证 | [Evidence](../evidence/README.md) |

## 13. 团队与个人贡献

| 常见追问 | 回答主线 | 权威阅读入口 |
| --- | --- | --- |
| 团队多大？ | 可恢复的核心研发规模约 7–8 人，完整组织图未恢复 | [团队与开发分工](./team-and-contributions.md) |
| 你什么时候加入？ | 约 2026 年 3 月；加入时已有产品和简单前端 | [团队与开发分工](./team-and-contributions.md) |
| 你具体做了什么？ | Agent、Memory、OpenViking、Tool Calling Strategy、数据库查看 / 调试等已确认方向 | [团队与开发分工](./team-and-contributions.md) |
| 你是不是整个项目架构负责人？ | 历史上没有证据支持这样扩大描述；当前仓库文档维护角色和历史项目角色要分开 | [团队与开发分工](./team-and-contributions.md) |
| GraphRAG / LangGraph 是你完整实现的吗？ | 目前只能说开发期间学习和接触；不能扩成完整 Owner | [团队与开发分工](./team-and-contributions.md) |
| 你能讲一个具体 Bug / 性能优化吗？ | 现有历史资料还没有恢复到任务级 Cause → Fix → Metric；不能编造 | [团队与开发分工](./team-and-contributions.md) |
| 客户反馈后你们怎么优化的？ | 能确认“回答质量需要提高”和后续迭代，但根因 / 修复 / 指标尚未恢复 | [开发过程](./development-process.md) |

## 14. 回答深度怎样逐层升级

如果只是 30 秒项目介绍，读 [项目说明](./README.md) 和 [产品定位](./product-positioning-and-value.md) 前半部分。

如果是 3–5 分钟系统设计追问，读 [总体架构 Part A](../architecture/architecture.md) 和 [模块 README](../modules/README.md)。

如果面试官开始问“谁拥有这个状态、崩溃在哪里恢复、重复请求怎么去重、权限中途变化怎么办”，进入对应模块 Part B / Part C。

如果面试官开始问“QPS 上来怎么办、缓存怎么做、为什么不用 2PC、HA / DR 怎么办、P95 和成本怎么压”，先读 [模块 README 的横向系统设计](../modules/README.md)，再进入对应 01 / 02 / 03 / 04 / 07 / 08 / 09 模块。

如果面试官问“你说这个实现了，证据呢”，立即切到 [`docs/evidence/`](../evidence/README.md)。

如果面试官问“你个人做了什么”，只从 [团队与开发分工](./team-and-contributions.md) 已确认内容回答，不用当前架构文档反推历史个人贡献。

如果问题超出现有证据，最好的回答不是补一个听起来合理的故事，而是明确：**这是当前 Target / 推断 / 尚未恢复事实，需要什么证据才能确认。** 对高级工程岗位来说，这种边界感本身就是架构能力的一部分。
