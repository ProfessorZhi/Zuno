# Round-004 Blue Answers

答案先给可执行结论，再说明边界。`Target` 表示目标设计，不是 Current 证据。

| ID | Blue Answer | Current / Target / Future / History | Owner | State Transition | Failure / Recovery | Tradeoff | Evidence | Document Impact |
|---|---|---|---|---|---|---|---|---|
| Q001 | 不能直接交付旧 Finding；Domain 校验 D13 后必须重新评估 | Target | Domain Owner | Finding fresh→stale→review | 旧 WorkProduct blocked，创建 bounded re-evaluation | 版本检查增加延迟 | stale propagation test | BOTH |
| Q002 | 两条路径都只能提交 Proposal，唯一 Admission 形成 Canonical Version | Target | Domain Owner | Proposal→admission | 冲突进入 review，不双写 | Host 集成少一步自由度 | host/native A-B trace | BOTH |
| Q003 | 先读 Domain State，再由 Outbox/Reconciliation 补发消息 | Target | Domain + Data | commit→outbox_pending→published | 重试按 idempotency key，不重复事实 | Outbox 增加存储和运维 | crash replay | BOTH |
| Q004 | Checkpoint 只说明控制位置，EffectReceipt 和 ProviderOperationId 决定是否已执行 | Target | Tool + Data | unknown→reconcile→resume/review | 无法确认时人工介入 | 对账比直接 retry 慢 | fault injection | BOTH |
| Q005 | 只有 Domain Owner 可写 EvidenceVersion，其他边界发布 Reference/Proposal | Target | Domain Owner | candidate→admission | 双写检测并拒绝 | 需要明确 owner registry | contract test | BOTH |
| Q006 | Planner 必须携带 IndexVersion 并拒绝超出 freshness policy 的 Graph | Target | Knowledge | indexed→stale/denied | 退回 Hybrid 或 no_evidence | freshness 检查减少召回 | graph stale test | BOTH |
| Q007 | 按 typed failure 分类；可重试错误 retry，不确定副作用先 reconcile | Target | Runtime Coordinator | failed→retry/reconcile | 超过预算进入 review | 错误分类增加协议复杂度 | failure matrix | BOTH |
| Q008 | HumanDecision 提升 DomainGeneration，旧 Plan 只能结束或 replan | Target | Domain + Runtime | reviewed→new generation | Resume 发现 generation mismatch | 人工反馈会打断长任务 | review replay | BOTH |
| Q009 | Provider 只实现 Capability Contract，输出 Proposal/Receipt，替换用同一数据集验证 | Target | Capability Owner | provider candidate→validated | schema/quality 不兼容拒绝 | 适配层增加维护成本 | substitution benchmark | BOTH |
| Q010 | C≈B 时缩减 Native Runtime，保留已经证明有价值的 Legal Backend | Target | Eval Owner | accepted→deferred/deleted | 保留回滚开关但不声称收益 | 删除会损失未测的探索空间 | A/B/C report | PART_A |
| Q011 | 新 taxonomy 是唯一 Canonical；旧 11 模块只作为 History | Current/Target | Architecture Owner | legacy→superseded | verifier 阻止双入口 | 迁移期间需维护链接 | docs boundary test | PART_A |
| Q012 | 只在 checkpoint compatibility window 内 Resume；否则 replan 或人工恢复 | Target | Runtime + Deployment | paused→compatible_resume/replan | 不兼容状态不得执行 | 兼容窗口延长发布成本 | upgrade replay | BOTH |
| Q013 | UI 显示 stale 原因、受影响版本和 Review 入口，不继续显示为当前结果 | Target | Product Owner | deliverable→stale→review | 导出 gate 阻止旧结果 | 状态更多但责任清楚 | product flow test | PART_A |
| Q014 | Review Policy 决定顺序和冲突；最终 HumanDecision 有版本和审计记录 | Target | Domain Owner | pending→approved/rejected | 并发冲突进入 review merge | 多 Reviewer 需要额外协调 | decision audit | BOTH |
| Q015 | Run Status 关联 MatterSnapshot 和 RunId，断线后从状态接口恢复 | Target | Product + Runtime | submitted→running→resumable | status read 不改变事实 | 需要异步状态面 | status trace | PART_A |
| Q016 | 只展示已完成页和明确 partial 状态，未解析页不能进入完整证据集 | Target | Knowledge + Product | uploading→partial/failed | 重试解析，保留原始 Artifact | 部分可用性增加 UX 分支 | document status | BOTH |
| Q017 | 驳回形成显式 Decision，不删除候选；是否重跑由 Review Policy 决定 | Target | Domain Owner | proposed→rejected/revise | 重跑使用新 generation | 保留历史增加存储 | rejection trace | BOTH |
| Q018 | Export 前重新检查 DomainGeneration、Review 和 stale；不满足则阻止或带清晰警告 | Target | Product + Domain | ready→blocked/exported | 新冲突触发 review | 交付多一次检查 | export gate | BOTH |
| Q019 | 内容 hash 用于幂等识别，但来源、上传者和权限变化可产生新版本引用 | Target | Knowledge + Domain | upload→dedup/new version | 重复 job 返回已有 receipt | identity 规则需要解释 | hash test | BOTH |
| Q020 | Stage checkpoint 记录已完成页和 parser version，从最后幂等边界恢复 | Target | Knowledge | parsing→partial→resumed | 半成品不可作为完整 index | checkpoint 增加状态量 | worker replay | BOTH |
| Q021 | SourceSpan 绑定 DocumentVersion 和 parser mapping，映射变化生成新 lineage | Target | Knowledge | span→remapped/stale | 旧引用标 stale，不静默移动 | 版本化引用更复杂 | citation test | BOTH |
| Q022 | Retrieval 时重新校验 ACL，已索引内容也不能绕过当前授权 | Target | Security + Knowledge | visible→denied | 返回 scope_denied 并审计 | 每次检索增加授权成本 | ACL trace | BOTH |
| Q023 | 取消产生可审计 cancel state；孤儿 Artifact 延迟清理但不可见 | Target | Knowledge + Data | uploading→cancelled/garbage_pending | 清理失败进入 maintenance queue | 垃圾回收增加运维 | storage audit | PART_B |
| Q024 | Parser 结果是 Candidate，按版本、质量和策略选择后再 Admission | Target | Knowledge Owner | candidates→selected/review | 冲突保留供人工比较 | 多 Provider 增加评估成本 | parser comparison | BOTH |
| Q025 | JobId 加内容/version/idempotency key，重复投递返回同一 receipt | Target | Knowledge + Queue | queued→processing→completed | duplicate 进入 no-op 或 reconcile | key 管理增加协议字段 | duplicate test | PART_B |
| Q026 | Graph edge 携带 source version 和 projection generation，过期就降级或拒绝 | Target | Knowledge | fresh→stale | 回退 Hybrid/no_evidence | 新鲜度降低召回 | graph freshness | BOTH |
| Q027 | Evidence Sufficiency 由 Claim 与 Requirement 检查，不由 top-k 数量决定 | Target | Knowledge + Domain | candidate→sufficient/insufficient | insufficient 触发补证据或 review | 需要结构化 requirement | sufficiency report | BOTH |
| Q028 | Exact Statute 默认走 Lexical/Hybrid，Graph 只有实验或条件路径 | Target | Knowledge | query→provider resolution | Graph 失败不影响基础检索 | provider routing 更复杂 | ablation | PART_A |
| Q029 | Scope 在检索入口和索引过滤同时执行，失败 closed | Target | Security + Knowledge | request→allowed/denied | denied 不返回候选 | 过滤成本增加 | isolation test | BOTH |
| Q030 | Rerank timeout 是 typed provider_unavailable，可用明确降级，不伪造 no_evidence | Target | Knowledge | rerank→fallback/unavailable | retry 有预算和 deadline | 降级质量需测量 | timeout matrix | BOTH |
| Q031 | Citation 必须落到 SourceSpan，chunk 只能作为中间投影 | Target | Knowledge | candidate→citable/non_citable | 不可定位则拒绝引用 | 精确 span 建设成本高 | citation correctness | BOTH |
| Q032 | 依据受影响 projection 定向重建，不默认全量建图 | Target | Knowledge | changed→affected rebuild | backlog 可观测并阻止 stale 使用 | dependency graph 维护成本 | rebuild trace | PART_B |
| Q033 | 冲突候选回到 Agent/Review，不由检索层替业务选择 | Target | Domain + Knowledge | candidates→comparison/review | 无法选择则 insufficient | 交互增加但语义不漂移 | conflict test | BOTH |
| Q034 | Plan 记录可接受 IndexVersion 范围，超界触发 refresh 或 replan | Target | Runtime + Knowledge | planned→barrier_pass/replan | 不混合版本 | 等待索引会增加 latency | barrier test | BOTH |
| Q035 | 被删除材料保留 tombstone 和 lineage，引用显示不可用而非静默移除 | Target | Knowledge + Domain | visible→deleted/stale | Finding 进入复核 | 历史追踪增加存储 | deletion test | BOTH |
| Q036 | Graph 只在关系型任务的 Kill Test 有增益时保留为条件 Provider | Target | Eval + Knowledge | provider→conditional/deferred | 无增益撤回 | 删除可降低能力覆盖 | kill graph report | PART_A |
| Q037 | Fallback 受同一 Run deadline、budget 和 model policy 约束 | Target | Model/Runtime | primary→fallback/exhausted | exhausted 进入 typed failure | 可用性换来成本 | provider trace | PART_B |
| Q038 | Gateway 归一化 schema，Agent 只看稳定 Tool Contract | Target | Model Gateway | provider schema→normalized | 不兼容拒绝 | 适配器有维护成本 | schema test | BOTH |
| Q039 | Usage Receipt 记录 provider、model、tokens、latency 和 fallback chain | Target | Model Gateway + Eval | call→receipt | 缺 receipt 不计为可比结果 | 观测字段增加 | cost trace | PART_B |
| Q040 | Gateway outage 只能进入显式 degraded mode，不能偷偷改变安全或预算 | Target | Runtime | running→degraded/blocked | deadline 到达则 review | 降级策略需要预演 | outage test | PART_A |
| Q041 | Model policy 和 PlanVersion 记录模型契约，升级需兼容测试 | Target | Model Gateway | versioned→compatible/replan | 不兼容旧 Run 停止 | 发布速度降低 | compatibility report | PART_B |
| Q042 | A/B 固定 fallback policy 或单独分层报告，否则不能归因 | Target | Eval | run→comparable/incomparable | incomparable 不发布结论 | 控制变量更严格 | eval manifest | PART_A |
| Q043 | Memory 先标 candidate/experience，只有显式 promotion 才能进入 Domain | Target | Domain + Memory | candidate→promoted/rejected | rejected 不得作为事实 Recall | promotion 流程增加延迟 | memory trace | BOTH |
| Q044 | Replay 使用 context item idempotency key，working context 不重复追加 | Target | Runtime + Memory | active→replayed | 重复 item no-op | 去重元数据增加 | replay test | PART_B |
| Q045 | Recall 按当前 Matter/Tenant/Policy Epoch 过滤，撤权立即生效 | Target | Security + Memory | visible→denied | 不可恢复到旧授权 | 召回多一次 policy check | access trace | BOTH |
| Q046 | Provider 只承诺 scoped context、expiry、lineage 和 deletion semantics | Target | Memory Owner | provider→contract-compatible | 不兼容替换或降级 | Provider 选择减少 | substitution test | BOTH |
| Q047 | Matter Fact 优先于 User Preference；冲突进入解释或 Review | Target | Domain Owner | context→conflict/review | 不让偏好覆盖事实 | Planner 需要 precedence | precedence test | PART_A |
| Q048 | Stale Memory 降权或拒绝，必须携带 captured_at 和 source generation | Target | Memory Owner | recalled→fresh/stale | stale 不进入 evidence gate | 新鲜度维护成本 | stale recall | PART_B |
| Q049 | 共享 Context 由 Coordinator 按 capability 和 permission 写入 | Target | Runtime + Security | private→shared candidate | 越权写入拒绝并审计 | 协调成本增加 | write audit | BOTH |
| Q050 | Memory 只能影响候选计划；改变 EvidenceRequirement 必须显式 Replan | Target | Runtime | recall→plan_candidate/replan | 隐式影响不被采纳 | 可追踪性优先于简洁 | plan trace | BOTH |
| Q051 | D12 与 D13 的 BranchResult 不能直接 Join，先过 Replan Barrier | Target | Runtime + Domain | join_pending→barrier/replan | 旧分支保留 receipt 但不提交 | 重新计算增加 latency | generation trace | BOTH |
| Q052 | 必需分支失败阻止成功；可选分支可带 degraded outcome | Target | Runtime | waiting→degraded/blocked | deadline 后 review | 任务完成率下降但不造假 | timeout matrix | BOTH |
| Q053 | Reducer 按 BranchId 和输入 generation 做确定性归并 | Target | Runtime | branch_result→reduced | duplicate result no-op | reducer 规则更严格 | replay test | PART_B |
| Q054 | Replan 先冻结旧 Plan，新 Plan 继承可复用 receipt，未安全取消的 Step 对账 | Target | Runtime + Tool | active→replan_pending | effect unknown 不重发 | 状态管理复杂 | cancel trace | BOTH |
| Q055 | 权限不足是 hard stop 或 Review，不是 Reflection 的自助升级 | Target | Security + Runtime | proposing→denied/review | 保留原因，不能 retry 绕过 | 任务可能中断 | deny trace | BOTH |
| Q056 | Coordinator 拥有预算裁剪，记录未运行分支和原因 | Target | Runtime | running→budget_limited | 不以缺失分支伪装完成 | 成本可控但覆盖减少 | budget trace | PART_B |
| Q057 | Checkpoint 与 Step lease 原子记录；恢复从最后安全边界开始 | Target | Runtime | crashed→resume/reconcile | 未知 Effect 先对账 | 原子写和存储成本 | crash replay | BOTH |
| Q058 | 未声明 ReplanRequest 按 schema 拒绝并作为 worker failure | Target | Runtime | result→rejected | 不改变 Plan | 合约验证增加延迟 | schema rejection | PART_B |
| Q059 | Review 形成新 DomainGeneration，旧 Plan 只能 replan 或结束 | Target | Domain + Runtime | planned→stale | 不允许旧 Plan Admission | 人工介入增加等待 | review replay | BOTH |
| Q060 | StepId 加 PlanVersion 和 input generation，重复消费返回已有 result | Target | Runtime | queued→completed/no-op | duplicate 不触发第二 Proposal | key 设计复杂 | duplicate job | PART_B |
| Q061 | Evidence Gate 依据 Claim、Requirement 和 source lineage，不由 Coordinator 主观判断 | Target | Knowledge + Domain | candidate→sufficient/research_more | 不足则补 Step 或 review | gate 需要标注数据 | sufficiency evidence | BOTH |
| Q062 | outcome_unknown 先进入 Effect reconciliation，不能直接 retry | Target | Tool + Runtime | tool_call→unknown/reconciled | Provider id 显示已执行则 no-op | 速度让位于安全 | operation id | BOTH |
| Q063 | 取消后完成的结果可保留为候选 Receipt，但不得自动提交 Canonical | Target | Runtime + Domain | cancelled→late_result/quarantined | 用户重新发起时显式采用 | 需要清理策略 | cancel race | PART_B |
| Q064 | Recovery 先读 DomainGeneration 与 EffectReceipt，再读 Checkpoint 控制位置 | Target | Data + Runtime | recover→resume/replan/review | 两者矛盾进入 reconciliation | 恢复路径更长 | reconciliation trace | BOTH |
| Q065 | Agent 绑定 Capability Contract，不绑定算法内部字段 | Target | Capability Owner | request→resolved provider | provider schema 变化由 adapter 吸收 | Adapter 维护成本 | contract test | PART_B |
| Q066 | 置信度只影响 Review/排序，不能绕过 Admission | Target | Domain Owner | proposal→review/admitted | 低置信度拒绝或人工确认 | 自动化率下降 | admission test | BOTH |
| Q067 | ApplicableLaw 必须绑定 StatuteVersion，版本不一致退回研究 | Target | Domain + Capability | mapping→version_checked | 不得混用新旧法条 | 需要版本数据 | version test | BOTH |
| Q068 | 类案 Provider 不可用时返回 unavailable，Agent 可继续无类案路径但标记缺口 | Target | Capability Owner | call→unavailable/degraded | 不伪造 SimilarCase | 结果覆盖减少 | fallback evidence | PART_A |
| Q069 | Security Policy 优先于 Skill；冲突记录 denied Tool intent | Target | Security | intent→denied | 不能由 Skill retry 改写 | 灵活性下降 | denied trace | BOTH |
| Q070 | Provider resolution 记录实现、版本和指标，比较时固定变量 | Target | Capability + Eval | candidate→selected/compared | 不可比则阻塞结论 | 记录成本增加 | capability benchmark | PART_B |
| Q071 | EffectReceipt 与 ProviderOperationId 是 unknown outcome 的唯一重试依据 | Target | Tool Owner | prepared→unknown→reconciled | 已执行则 no-op | 对账需要 Provider 支持 | fault injection | BOTH |
| Q072 | 执行时重新校验 SecurityEpoch，撤权立即阻断 | Target | Security + Tool | approved→revoked/execute | 旧批准不再有效 | 每次动作有延迟 | revocation test | BOTH |
| Q073 | 文档内容只能作为 untrusted input，Tool 参数由 schema/policy 重新生成 | Target | Tool + Security | content→proposal→validated | 注入字段丢弃并审计 | 参数校验更严格 | injection trace | BOTH |
| Q074 | Effect identity 加幂等键，重复 receipt 只返回既有结果 | Target | Tool | attempted→completed/no-op | 不重复外部副作用 | Provider 适配复杂 | duplicate effect | PART_B |
| Q075 | Sandbox crash 后读取 receipt 和 operation id，再决定 reconcile/retry | Target | Tool + Data | crashed→unknown/reconciled | 无证据不重发不可逆动作 | 恢复等待更久 | crash test | BOTH |
| Q076 | timeout、network_denied、provider_error 分开编码并分别定义 retry | Target | Tool | attempted→typed_failure | 只有安全失败可直接 retry | 错误分类维护成本 | failure taxonomy | PART_B |
| Q077 | Secret Scope 绑定 SecurityEpoch，rotation 后新动作必须重新取 Secret | Target | Security | authorized→epoch_changed | 旧凭据失效 | rotation 传播复杂 | secret trace | BOTH |
| Q078 | ToolVersion 与输入输出 schema 做兼容性检查，不兼容进入 provider_unavailable | Target | Tool | resolved→compatible/blocked | 不能静默解析不同结果 | 发布需兼容窗口 | compatibility test | PART_B |
| Q079 | 取消只阻止尚未开始的 Effect；已开始的动作必须走 unknown/reconcile | Target | Tool + Runtime | prepared→cancelled/started | 不承诺不可能的撤销 | 用户体验更复杂 | cancel trace | PART_A |
| Q080 | EffectReceipt 保留，即使 Domain Commit 失败；后台对账补状态或人工处理 | Target | Tool + Domain | effect_success→domain_pending/reconciled | 不删除副作用证据 | 数据清理更难 | reconciliation | BOTH |
| Q081 | Retrieval 和 Tool 每次使用当前 Policy Epoch，Run 创建时授权不够 | Target | Security | authorized→recheck/denied | denied 不再 retry | 长 Run 延迟增加 | policy trace | BOTH |
| Q082 | Prompt Injection 无权修改 Grant 或 egress policy，外发动作需要独立 Approval | Target | Security | untrusted→blocked/review | no-egress 与审计保留 | 安全边界牺牲便利 | no-egress test | BOTH |
| Q083 | Tenant/Matter/Scope 在索引、API 和 Tool 三层校验 | Target | Security | request→allowed/denied | 任一层失败 closed | 多层策略成本 | cross-tenant test | BOTH |
| Q084 | Approval 必须带 SecurityEpoch，epoch 变化后重新审批 | Target | Security | approved→invalid/reapproved | 旧审批不能执行 | 审批次数增加 | epoch test | PART_B |
| Q085 | Secret 和敏感材料进入 Trace 前脱敏，原始值不进入 Error | Target | Security + Observability | error→redacted_audit | 泄漏事件进入 security review | 调试信息减少 | audit scan | BOTH |
| Q086 | Sandbox 由 OS/container/network boundary 强制，代码约束只是补充 | Target | Tool/Security | job→isolated/escaped | escape fail closed 并隔离 | 隔离运维成本高 | escape test | PART_A |
| Q087 | Retry 前重新做权限检查，撤权后的旧 Job 进入 denied | Target | Security + Queue | retry→recheck/denied | 不绕过 epoch | 重试吞吐下降 | retry auth trace | BOTH |
| Q088 | External Host 与 Native Runtime 使用同一 Domain Admission，不信任 Host 身份 | Target | Domain + Security | external proposal→admission/reject | 越权只产生拒绝记录 | 集成需要明确 Contract | admission denial | BOTH |
| Q089 | A/B/C 固定模型、工具、数据和预算；fallback 差异单独记录 | Target | Eval | run→comparable/incomparable | 不可比阻塞结论 | 试验设计成本高 | eval manifest | BOTH |
| Q090 | Retrieval failure 作为 Trace FailureClass，最终文本不能掩盖 | Target | Eval | run→failed_with_output | 结果可展示但不计为无错误 | 指标更保守 | raw trace | PART_A |
| Q091 | blocked/unavailable/incomparable 单独报告，不改变有效分母 | Target | Eval | result→classified | 报告保留原因 | 分析复杂度增加 | metric report | PART_B |
| Q092 | Graph 只对通过 QueryClass Kill Test 的任务启用 | Target | Eval + Knowledge | graph→conditional | 无收益回 Hybrid | 路由配置增加 | graph report | BOTH |
| Q093 | Token、Latency 与质量一起评估，成本无收益则撤回 Multi-Agent | Target | Eval + Agents | component→keep/defer/delete | 结论受预算约束 | 更少自动化 | ablation | PART_A |
| Q094 | Service evidence 同时报告 latency、failure、resource 和 recovery | Target | Eval + Services | boundary→validated/rejected | 失败增益不足则合并 | 测试矩阵较大 | fault report | BOTH |
| Q095 | 新 Worker 先做 Checkpoint compatibility read，再逐步切换 writer | Target | Deployment + Runtime | old→compatible→rolled | 不兼容暂停 rollout | 双读窗口增加成本 | upgrade replay | BOTH |
| Q096 | Queue drain 先停止接收或设置 backpressure，Job 状态可查询 | Target | Deployment | running→draining→drained | 新 Job 不静默丢失 | 发布期间吞吐下降 | queue trace | BOTH |
| Q097 | API、Knowledge 和 Agent 使用不同 resource profile/queue，避免 GPU 饥饿 API | Target | Deployment | shared→isolated pools | starvation 触发 backpressure | 资源利用率可能下降 | load test | PART_A |
| Q098 | Shared PostgreSQL 仍按逻辑 ownership 和 compatibility gate 管理 schema | Target | Data + Deployment | schema→compatible/blocked | drift 阻止发布 | 集中库治理成本 | schema check | BOTH |
| Q099 | Retry 有 deadline、attempt 上限、DLQ 和 backpressure，重启不放大风暴 | Target | Deployment + Queue | retrying→dead_letter/reconciled | unknown effect 不自动重试 | 失败恢复更慢 | fault injection | BOTH |
| Q100 | Compose 只能证明运行配置，HA 需要真实故障和恢复证据 | Current/Target | Deployment | configured→measured/unproven | 无证据保持 NOT_ESTABLISHED | 不夸大生产状态 | deployment evidence | PART_A |
