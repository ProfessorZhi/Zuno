# Round-004 Questions

每行是一个独立的 scenario-based Red Question。`Target Scenario` 只表示目标设计，不表示历史事实。

| ID | Type | 11+1 Lens | Canonical Owner Doc | Scenario | Question | Attack Intent | Required Evidence | Kill Condition |
|---|---|---|---|---|---|---|---|---|
| Q001 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | D12 上同时有新证据和旧 Run | 谁决定旧 Finding 能否继续交付？ | 检查 Domain/Runtime authority | version trace | Runtime 可直接发布旧结论 |
| Q002 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Host 与 Native Runtime 同时处理 Matter | 两条路径如何避免产生两个 Canonical Truth？ | 检查 Host boundary | admission log | Host 直接写 Finding |
| Q003 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Domain Commit 成功而消息发布失败 | 恢复时先看 Queue 还是 Domain State？ | 检查事实优先级 | outbox/replay trace | ACK 覆盖业务事实 |
| Q004 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Agent Checkpoint 停在 Tool 前 | 如何判断外部动作是否已经发生？ | 检查 checkpoint/reconciliation | EffectReceipt | 盲目 retry 不可避免 |
| Q005 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 两个服务都宣称拥有 Evidence | 谁能改变版本和 Provenance？ | 检查 owner registry | owner contract | 双写成立 |
| Q006 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Graph projection 落后于文档版本 | Planner 能否把旧边当事实？ | 检查 projection boundary | index version | stale graph 被静默使用 |
| Q007 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Service 拆分后网络失败 | 哪些结果可重试，哪些只能对账？ | 检查 failure taxonomy | fault test | 所有错误统一 retry |
| Q008 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Human Review 修改 Finding | Runtime 如何知道旧 Plan 已过期？ | 检查 review feedback | domain generation | Resume 覆盖人工决定 |
| Q009 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Provider 被替换 | 如何证明语义没有随 Provider 漂移？ | 检查 provider contract | substitution benchmark | Provider 直接拥有业务状态 |
| Q010 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | A/B/C 结果 C≈B | 哪一层复杂度应先撤回？ | 检查 reversal discipline | benchmark report | 复杂度默认保留 |
| Q011 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 旧 11 模块与新服务名冲突 | 阅读者从哪里获得唯一边界？ | 检查 taxonomy drift | docs verifier | 两套 Canonical truth |
| Q012 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 长 Run 跨部署版本恢复 | 哪个版本拥有 Resume 权？ | 检查 deployment/runtime contract | compatibility test | 不兼容 checkpoint 被执行 |
| Q013 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | 用户上传新证据后查看旧报告 | UI 如何解释 stale WorkProduct？ | 检查 product closure | review trace | 旧报告仍显示当前 |
| Q014 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Reviewer A 已批准 Reviewer B 修改 | 谁拥有最终 HumanDecision？ | 检查 review authority | decision audit | 多个最终决定无序 |
| Q015 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Host 提交 Run 后断线 | 用户如何知道 Run 与 Matter 版本？ | 检查 async UX contract | status trace | 只能靠聊天历史恢复 |
| Q016 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | 解析失败但部分页已可检索 | 产品显示什么可用范围？ | 检查 partial ingestion UX | document status | 部分材料伪装完整 |
| Q017 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Finding 被人工驳回 | 是否重跑、保留候选还是删除？ | 检查 review state | rejection trace | 驳回被当成功 |
| Q018 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | WorkProduct 导出时发现新冲突 | 导出动作如何被阻止或标注？ | 检查 delivery gate | export audit | stale 结果可交付 |
| Q019 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 同一 PDF 重传但内容 hash 相同 | 如何避免重复 DocumentVersion？ | 检查 identity/idempotency | hash trace | 重复版本污染引用 |
| Q020 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | OCR 完成一半 Worker 崩溃 | 重试从哪里开始？ | 检查 stage checkpoint | worker replay | 半成品被当完整 |
| Q021 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 页码映射在解析后变化 | SourceSpan 如何保持可追溯？ | 检查 citation lineage | span test | 引用漂移不被发现 |
| Q022 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 文档权限在索引后撤销 | 已生成的 Candidate 是否还能返回？ | 检查 ACL at retrieval | access trace | 索引绕过权限 |
| Q023 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 上传取消发生在对象存储写入后 | 如何清理或标记孤儿 Artifact？ | 检查 cancellation semantics | storage audit | 孤儿材料成为可见事实 |
| Q024 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 两个 parser 对同一版本给出不同 span | 谁能选择结果？ | 检查 provider proposal | comparison trace | parser 直接覆盖来源 |
| Q025 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | ingestion queue 重复投递 | Job 如何幂等并报告次数？ | 检查 queue contract | duplicate test | 重复 chunk/index |
| Q026 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Graph edge 来自旧 DocumentVersion | Retrieval 如何拒绝 stale edge？ | 检查 graph freshness | index generation | 旧边支持新 Finding |
| Q027 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Claim 需要跨三份材料闭环 | Evidence Sufficiency 在哪里判断？ | 检查 evidence gate | sufficiency report | 只返回 top-k |
| Q028 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Exact Statute 查询被 Graph 改写 | 为什么不走 Lexical/Hybrid？ | 攻击 always-Graph | ablation | Graph 无收益仍默认启用 |
| Q029 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Scope 选错 Matter | 检索层如何 fail closed？ | 检查 scope isolation | denied trace | 跨案召回 |
| Q030 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Rerank Provider 超时 | 返回 no_evidence 还是降级？ | 检查 typed failure | fallback test | 超时伪装空结果 |
| Q031 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Citation 指向 chunk 但非原文 span | 谁校验引用？ | 检查 citation owner | citation test | CitationCorrectness 不可测 |
| Q032 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | 新材料只影响 Graph projection | 是否重建全图？ | 检查 targeted rebuild | rebuild trace | 全量重建无界成本 |
| Q033 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Hybrid 与 Graph 返回冲突候选 | Agent 能直接挑一个吗？ | 检查 candidate semantics | conflict review | retrieval result 变事实 |
| Q034 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | IndexVersion 与 DomainVersion 不同 | 哪个版本可进入 Plan？ | 检查 version barrier | barrier test | 版本混用 |
| Q035 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | 召回结果来自被删除材料 | Citation 如何处理 tombstone？ | 检查 deletion lineage | deletion test | 删除后仍引用 |
| Q036 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Graph 成本高但质量不增 | 谁触发降级？ | 检查 component survival | kill report | Graph 永久锁定 |
| Q037 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Model timeout 后换 Provider | 如何保持预算和语义边界？ | 检查 gateway contract | provider trace | fallback 无限重试 |
| Q038 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Provider 返回不同 tool schema | 谁做归一化？ | 检查 adapter owner | schema test | Agent 处理供应商分支 |
| Q039 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | 同一 Run 发生 fallback | Token/cost 如何归属？ | 检查 usage receipt | cost trace | 预算不可解释 |
| Q040 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Model Gateway 暂时不可用 | Runtime 能否使用缓存计划？ | 检查 degraded mode | outage test | 隐式改变安全策略 |
| Q041 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Provider 版本升级 | Plan compatibility 如何保证？ | 检查 model policy | compatibility report | 旧 Run 无法解释 |
| Q042 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | A/B 比较使用不同 fallback | 如何避免把供应商差异当架构收益？ | 检查 benchmark controls | A/B manifest | 归因失真 |
| Q043 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory 写入一条被 Domain 拒绝的经验 | 下次 Recall 能否使用？ | 检查 promotion boundary | memory trace | 候选污染事实 |
| Q044 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Run crash 后重放 | working context 是否重复追加？ | 检查 replay idempotency | replay test | context 越跑越长 |
| Q045 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Matter 权限撤销后 Recall | Provider 如何过滤旧 Memory？ | 检查 scoped access | access trace | Memory 绕过 ACL |
| Q046 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | OpenViking Provider 被替换 | 哪些语义必须保持？ | 检查 memory provider contract | substitution test | Provider 成为事实源 |
| Q047 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | User preference 与 Case Fact 冲突 | Planner 信谁？ | 检查 memory/domain precedence | precedence test | 偏好覆盖案件事实 |
| Q048 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory stale 但索引仍命中 | 如何降权或拒绝？ | 检查 staleness | stale recall test | 旧经验无标记复用 |
| Q049 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | 多 Agent 共享 context | 谁能写入共享空间？ | 检查 delegation permission | write audit | 任意 Agent 污染共享记忆 |
| Q050 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory 召回使计划偏离 EvidenceRequirement | 是否需要 Replan？ | 检查 memory influence | plan trace | 隐式规划不可审计 |
| Q051 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | P7 基于 D12 创建后用户提交 D13 | Join 如何处理旧分支？ | 检查 replan barrier | generation trace | 旧结果直接合并 |
| Q052 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 必需 Worker 超时、可选 Worker 成功 | Run 是否结束？ | 检查 join policy | timeout matrix | 空结果伪装成功 |
| Q053 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 两个 BranchResult 同时提交 | Reducer 如何保证确定性？ | 检查 reducer authority | reducer replay | 顺序决定事实 |
| Q054 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Replan 发生时已有 Step 仍运行 | 哪些 Step 可取消？ | 检查 cancellation | cancel trace | 新旧计划同时提交 |
| Q055 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Reflection 发现权限不足 | 是否修改 Plan 还是停在 Review？ | 检查 permission boundary | deny trace | Reflection 提升权限 |
| Q056 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Budget 在并行分支耗尽 | 谁裁剪剩余工作？ | 检查 budget owner | budget trace | 分支无限运行 |
| Q057 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Coordinator 重启且 Checkpoint 半写 | Resume 从哪里开始？ | 检查 checkpoint atomicity | crash replay | 重复不可逆动作 |
| Q058 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Worker 返回未声明的 ReplanRequest | Coordinator 是否采纳？ | 检查 contract validation | schema rejection | 任意 Worker 改图 |
| Q059 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Plan 已激活但 Domain Review 修改事实 | 如何标记 Plan stale？ | 检查 domain generation | review replay | 旧计划继续写候选 |
| Q060 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 同一 Step 被队列投递两次 | 两次结果如何去重？ | 检查 step idempotency | duplicate job test | 双写 Proposal |
| Q061 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Join 缺一个证据分支但有足够候选 | 谁判断“足够”？ | 检查 evidence gate | sufficiency evidence | Coordinator 自行认定 |
| Q062 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Tool 调用 outcome_unknown | Plan 能否直接重试？ | 检查 effect reconciliation | operation id | 重复副作用 |
| Q063 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 用户取消 Run 后 Worker 返回结果 | 结果丢弃还是保留候选？ | 检查 cancellation state | cancel race test | 取消后提交事实 |
| Q064 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | LangGraph State 与 Domain State 不一致 | Recovery 谁先读？ | 检查 state separation | reconciliation trace | checkpoint 当业务事实 |
| Q065 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Event Provider 输出新字段 | Agent 是否需要改业务代码？ | 检查 capability contract | contract compatibility | 算法写死 Agent |
| Q066 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Conflict Provider 置信度下降 | 是否自动形成 ConflictVersion？ | 检查 proposal admission | admission test | Provider 直写事实 |
| Q067 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Fact-Article Provider 返回不同法条版本 | 谁校验 ApplicableLaw？ | 检查 statute version | version test | 版本混淆 |
| Q068 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Similar Case Provider 不可用 | Agent 如何降级？ | 检查 provider failure | fallback evidence | 伪造类案 |
| Q069 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Skill 指示与 Security Policy 冲突 | 以谁为准？ | 检查 policy precedence | denied tool trace | Skill 提升权限 |
| Q070 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | 同一 Capability 有 LLM 与本地实现 | 如何公平替换和评估？ | 检查 provider resolution | capability benchmark | 供应商差异隐藏 |
| Q071 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 外部写操作已成功但响应丢失 | Runtime 如何避免第二次写？ | 检查 unknown outcome | provider op id | 盲重试 |
| Q072 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Approval 在执行前被撤销 | Sandbox 是否仍执行？ | 检查 execute-time auth | revocation test | 旧批准有效 |
| Q073 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool 参数被文档注入污染 | 谁做参数校验？ | 检查 untrusted input boundary | injection trace | 文档控制 Tool |
| Q074 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 同一 EffectReceipt 被重复消费 | Tool 如何幂等？ | 检查 receipt identity | duplicate effect test | 重复副作用 |
| Q075 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Sandbox 崩溃但外部 Provider 未知 | 如何进入 reconciliation？ | 检查 crash boundary | receipt lookup | 直接 retry |
| Q076 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool timeout 与 network deny 同时发生 | 错误类型如何区分？ | 检查 typed failure | failure taxonomy | 所有错误同路径 |
| Q077 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Secret rotation 发生在长 Run 中 | 下一个 Tool Call 用哪个 Secret？ | 检查 secret epoch | rotation trace | 旧 Secret 继续使用 |
| Q078 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool Provider 版本不兼容 | 能否安全降级？ | 检查 provider compatibility | compatibility test | 结果格式静默变化 |
| Q079 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 用户取消不可逆 Effect | 取消点在哪里？ | 检查 cancellation boundary | cancel/effect trace | 取消承诺虚假 |
| Q080 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Effect 成功后 Domain Commit 失败 | 业务状态如何对账？ | 检查 effect/domain split | reconciliation report | EffectReceipt 被删除 |
| Q081 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | 用户失去 Matter 权限但 Run 尚未结束 | 下一次 Retrieval 如何重新授权？ | 回归 ACL 传播 | policy trace | 只在 Run 创建时授权 |
| Q082 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Prompt Injection 要求外传案件 | Security 如何阻断？ | 回归 untrusted content | no-egress test | 文档改变 policy |
| Q083 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Tenant A 的索引被 Tenant B 查询 | 哪一层做隔离？ | 回归 tenant boundary | cross-tenant test | 只靠 Prompt 隔离 |
| Q084 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Approval 与 SecurityEpoch 不一致 | 旧批准能否使用？ | 回归 approval epoch | revocation evidence | 旧批准继续执行 |
| Q085 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Tool 失败后错误信息含 Secret | Audit 如何脱敏？ | 回归 secret hygiene | audit scan | Trace 泄漏 Secret |
| Q086 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Sandbox 进程访问未授权文件 | 谁强制边界？ | 回归 sandbox isolation | escape test | 只做代码约束 |
| Q087 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | 权限撤销后重复 Job 到达 | Job 是否重新授权？ | 回归 retry auth | deny/retry trace | Retry 绕过撤权 |
| Q088 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | 外部 Host 发送越权 Proposal | Domain 如何拒绝？ | 回归 host boundary | admission denial | Host 被信任 |
| Q089 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | C 与 B 使用不同 Token Budget | 结果还能归因吗？ | 回归 fairness | eval manifest | 不可比仍发布 |
| Q090 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Retrieval 失败但最终答案存在 | 指标如何记录？ | 回归 failure visibility | raw trace | 只看最终文本 |
| Q091 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Reviewer 分母因 blocked case 改变 | 如何报告？ | 回归 denominator integrity | metric report | blocked 折零 |
| Q092 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Graph 只改善一个 QueryClass | 是否全局启用？ | 回归 conditional provider | kill graph report | 局部收益变全局锁定 |
| Q093 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Multi-Agent 多花一倍 Token 无质量增益 | 是否保留？ | 回归 component survival | ablation | 成本不进入结论 |
| Q094 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Service 拆分降低延迟但增加失败 | 如何权衡？ | 回归 service evidence | latency/fault report | 单指标发布 |
| Q095 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Rolling upgrade 遇到旧 Checkpoint | 新 Worker 如何读取？ | 回归 compatibility | upgrade replay | 任务静默丢失 |
| Q096 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Queue drain 时新 Run 持续进入 | 如何 backpressure？ | 回归 drain semantics | queue trace | drain 假成功 |
| Q097 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Knowledge GPU worker 饥饿 API | 如何隔离资源？ | 回归 resource profile | load test | 用户数成为唯一依据 |
| Q098 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Shared PostgreSQL 出现 schema drift | 谁阻止不兼容发布？ | 回归 schema compatibility | migration gate | 共享库随意改表 |
| Q099 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Worker 重启与消息重试同时发生 | 如何避免 retry storm？ | 回归 retry/backpressure | fault injection | 无限重试 |
| Q100 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | 生产证据只有 Compose 文件 | 能否宣称 HA？ | 回归 Current/Target boundary | deployment evidence | 配置冒充运行证据 |
