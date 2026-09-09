# 02 Legal Domain & Work Product（法律领域与工作成果）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail_design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块回答的是“什么才算正式法律业务事实”

模型可以生成事实摘要、争议点和法律结论，检索可以找到相关材料，Runtime 可以把一条复杂流程跑完，但这些成功都不能自动说明法律业务已经正式接受了某个结果。正式结果需要长期存在、可追溯、可版本化，也需要在人机协作和新证据进入以后仍然解释得清楚。

02 的职责因此不是“保存模型输出”，而是拥有正式领域状态：哪些材料版本属于当前事项，哪些候选被接纳为证据，哪些结论经过了怎样的人工判断，最终工作成果引用了什么，以及新事实出现以后哪些历史成果需要复核。

### 最简单的“把最终答案存进数据库”为什么不够

最简单方案是把最终模型文本写进一张 result 表。对一次性 Demo 这可能完全够用，因为系统只需要展示最后输出。

长期业务一旦出现，单条文本无法回答：这个结论依赖哪份材料的哪个版本；模型建议是否被人工修改；后来新增证据后旧结果是否仍有效；系统崩溃时这次正式提交到底成功没有。为了恢复方便继续给 result 表加几十个状态字段，最终只会得到一张无法说明权威边界的万能表。

### 候选和正式事实必须有一道清楚的门

检索和模型先产生候选，是因为机器结果可能错、材料可能不完整、权限和专业判断也可能变化。正式 Evidence 必须由 Domain Owner 在满足业务约束后接纳，而不能因为 Retriever 命中就直接写入长期事实。

这个差异用工程术语可以写成：

```text
EvidenceCandidate（证据候选）
    ≠
Evidence（正式证据）
```

术语不是重点，重点是正式业务世界只接受经过明确准入的事实，机器计算成功本身没有这种权威。

### 为什么需要一组很小但稳定的领域对象

法律工作长期需要追踪的不是所有中间 DTO，而是少量具有业务身份的对象：事项、材料版本、主张、正式证据、正式结论、人工业务决定和工作成果。它们构成 Target 的七对象 Legal Domain Kernel。

七对象不是为了“领域建模漂亮”，而是为了让长期事实有稳定身份和版本。OCR chunk、embedding、模型 response、Runtime Step 都可以大量变化，却不应该取代这些正式业务对象的身份。

### Formal Admission 为什么必须留下耐久证明

当 Runtime 或 Capability 产生一个需要进入正式领域的结果时，Domain 不能只返回 `200 OK` 然后期待调用方记住成功。最危险的窗口是 Domain transaction 已经提交，而调用方在更新 Checkpoint 前崩溃。

所以正式提交必须同时得到可重放查询的因果证明。系统恢复时，以 `DomainVersion + matching AdmissionReceipt` 判断这次正式提交是否真的发生，再修复 Runtime。Receipt 不是日志装饰，而是跨故障窗口判断完成的耐久锚点。

### 为什么 DomainVersion 不能被 Runtime 的 completed 覆盖

Runtime 的任务是控制执行，Domain 的任务是维护业务事实。一个 Step 可以完成纯计算却不需要正式提交；另一个 Step 可能业务事务已提交但 Runtime 还没更新。

如果双方共享一个 `completed`，崩溃后就无法判断哪种完成更强。DomainVersion 记录正式业务世界的演进，Runtime Checkpoint 记录控制进度。它们通过 causation refs 关联，但谁也不能冒充对方。

### WorkProduct 为什么不能只保存最终文本

正式工作成果要能在未来解释“当时为什么这样写”。因此除了版本化正文，还需要保存它真正采用的 Evidence、Finding、HumanDecision 和材料位置。

这里的引用不是“当前重新检索可能找到什么”，而是历史成果在提交时真实绑定了什么。工程上把这种稳定历史依据表达为 `WorkProductCitationBinding`，它的生命周期跟工作成果走，而不是跟当前检索索引走。

### 检索引用为什么不能直接成为正式成果引用

Retriever 的 CitationLineage 解释当前候选从哪里来，索引重建、切分策略或 reranker 升级都可能改变它。正式工作成果却必须在几年后仍能回到当时采用的不可变材料版本和稳定位置。

因此 CitationLineage 可以帮助 Formal Admission 构造正式引用，但不能直接被当成长期业务 binding。正式化过程必须校验材料版本、位置和当前业务 Scope，再由 02 保存历史身份。

### 人工业务决定和安全审批为什么必须分开

专业人员可能接受、修改或拒绝一个 Finding，这属于法律业务判断；安全治理可能要求另一位有权限的人批准一次高风险外部动作，这属于安全审批。二者即使都发生在“人点按钮”的 UI 上，语义仍然不同。

所以必须保持 `HumanDecision（人工业务决定）和 ApprovalDecision（安全审批决定）` 的 Owner 分离。一个专家认可结论，不代表允许把它发送到外围系统；一个管理员批准发送，也不代表模型结论已经成为正式法律事实。

### 新证据出现以后为什么要保留历史而不是覆盖旧结果

假设 WorkProduct V3 基于当时全部正式 Evidence 生成，后来新增一份关键补充协议。V3 作为历史成果仍然真实存在，但当前继续使用它可能已经不合适。

02 因此需要记录依赖关系，并在新事实影响旧结论时形成 invalidation / stale 事实。系统不是把 V3 删除，也不是偷偷把 V3 内容改成新版本，而是明确“当时的版本存在；现在需要复核”。这同时保护审计和当前有效性。

### 为什么失效传播应该有界而不是一律全案重跑

一个事项新增材料不一定影响全部 Finding。只要正式对象保存了足够依赖关系，就可以沿 Evidence → Finding → WorkProduct 的因果边界判断哪些结果可能受到影响。

这使系统可以把重评限制在真实依赖范围内。过度精细的依赖图也会增加维护成本，所以 Target 只要求能够解释重要正式关系，不为了理论完美把所有模型 token 和中间变量都升级成领域对象。

### 并发正式提交为什么不能靠“最后写入者获胜”

多人协作、后台 Agent 和异步恢复可能同时尝试更新同一个 Matter。如果两个提交都基于旧 DomainVersion，却无条件覆盖对方，就会丢失人工判断或正式证据。

因此正式准入需要 expected version / CAS 一类并发条件，冲突时重新读取当前 Domain facts 再判断。这里保护的是业务版本因果，不是为了追求分布式锁本身。

### 幂等为什么必须绑定 canonical 业务输入

客户端或 Runtime 崩溃重试时，同一次 Formal Admission 应能安全识别；但只比较一个字符串 key 不够，因为同 key 如果携带不同 canonical input，继续返回旧结果会隐藏业务冲突。

所以 Admission 的幂等身份必须和规范化业务输入、预期版本和重要 causation 绑定。相同逻辑提交可以返回既有 Receipt，不同业务内容复用同 key 应显式失败。

### 崩溃恢复为什么先读 Domain 而不是先重放 Agent

最重要的恢复原则是：先确认更强的业务事实是否已经存在，再决定控制流程要不要继续。Domain commit 成功而 Checkpoint 失败时，重放 Agent 可能重复正式提交；Checkpoint completed 而 Domain Receipt 不存在时，也不能因为控制状态漂亮就宣布业务完成。

因此恢复查询以 DomainVersion 和 matching Receipt 为锚点，Runtime 再修自己的 projection。这个顺序让 Domain 成为正式业务权威，而不是让 Checkpointer 在故障时意外升级成业务数据库。

### 02 不应该拥有什么

02 不负责 OCR、embedding、索引 serving，也不负责决定下一步 Agent Plan，更不负责模型路由和外部 Tool Effect。把这些职责收进 Domain 会让正式状态和可重建技术状态混在一起。

Domain 可以引用 Knowledge、Runtime、Capability、Security 和 Effect 产生的事实，但只在需要形成正式法律结果时接管。保持入口窄，才能让正式状态长期稳定而外围技术自由演进。

### 什么时候领域模型应该更简单

如果产品只是一次性问答，没有正式工作成果、人工业务决定、版本历史和长期失效语义，那么完整七对象 Kernel 可能没有必要。一个更轻的 answer record 完全可能足够。

只有当系统需要把结果作为长期业务事实保存、复核、追责和继续演进时，Domain Kernel 才值得存在。即使存在，也不应为了“DDD 完整”增加没有稳定业务身份的对象。

### 正式领域模型为什么描述业务关系，而不是模型推理过程

LLM 可能经过十次 Reflection 才得到一个 Finding，Retriever 可能融合多个 query route，Runtime 也可能多次 Replan。这些过程对调试有价值，却不应该全部升级为长期法律 Domain 对象。

02 只保留对未来业务仍有意义的关系：哪个 Evidence 支持或反驳哪个 Finding，哪次 HumanDecision 接受或修改了什么，哪个 WorkProduct 基于哪些正式版本形成。这样 Domain 不会随着 Agent 实现变化而频繁迁移。

如果未来替换模型或 Runtime，正式历史仍然能读懂；需要重放计算过程时再沿 causation refs 去 04、05、07、09 查运行证据。Domain 稳定性来自克制地只保存长期业务语义。

### “正式”为什么不是一个 boolean，而是一种事务边界

如果只在普通结果行上加 `formal=true`，系统仍然无法回答这个标志与引用、版本、人工决定是否同时成立。正式化应该是一组不可分割的业务约束：输入版本满足预期、必要 Evidence 存在、引用可回溯、权限与人工条件满足，然后在同一 Domain transaction 中形成新版本和 Receipt。

因此 Formal Admission 的价值不是多一个 API，而是把“从候选世界进入长期业务世界”变成明确边界。失败时要么本次领域变化没有提交，要么已经存在可查询 Receipt；不允许出现“正文写了但引用没写”“版本涨了但人工决定丢了”这类半正式状态。

字段和表可以在 Detail Freeze 时变化，但这种事务语义不能被实现便利削弱。

### Domain Version 为什么是乐观并发的因果保护，而不是数据库技巧

两个专业人员可能同时基于 V10 工作：一人新增 Evidence，另一人接受旧 Finding。如果第二个提交无条件覆盖，系统会把“基于旧世界的判断”写进新世界。

expected DomainVersion 让提交显式声明自己依据哪个业务快照。版本冲突不是纯技术异常，而是告诉调用方：你原本的前提已经变化，需要重新读取、合并或人工判断。对于 Agent，同样意味着可能需要 Replan，而不是自动最后写入获胜。

这种乐观并发比全事项长期加锁更适合复杂异步任务，因为人和 Agent 不需要一直持有锁；真正提交时才验证因果是否仍成立。

### 失效为什么要和删除区分

WorkProduct 因新 Evidence 需要复核，并不意味着它从历史中消失。审计、争议复盘和外部已接收版本都需要知道当时确实存在过 V3。

所以 stale / superseded 是有效性语义，delete / purge 是数据生命周期语义。前者由 02 根据业务依赖决定，后者受 08 Retention / Legal Hold 约束。把两者混成一个 `deleted=true`，既会破坏历史，也无法正确满足治理要求。

正式对象的版本历史因此更像不可改写的业务记录加当前有效性，而不是一张永远只保留“最新版”的文档表。

### 领域复杂度什么时候应该停止增长

法律业务很容易诱导无限建模：可以为每个推理步骤、每种证据强度和每个语言片段创建对象。但对象越多，Formal Admission、版本迁移和依赖传播的成本越高。

新增一级领域对象之前应问：它是否有独立生命周期、稳定业务身份、需要被长期引用或人工操作？如果只是某个 Capability 的中间输出、某种 Eval 标签或某种 UI projection，就不应该进入 Canonical Kernel。

七对象 Kernel 的价值恰恰在于给领域模型一个复杂度上限：先证明现有对象无法表达真实长期责任，再通过架构审查扩展。

### Human Review 为什么不能只保存“最终同意了”

专业人员介入的价值不仅是给模型结果盖章。人可能接受一部分、修改另一部分、拒绝某条 Finding，也可能因为材料不足要求补证。如果系统只保存最终 `approved=true`，未来无法解释哪些内容来自机器、哪些是人工修订，也无法把人工判断用于后续质量评测。

因此 HumanDecision 应绑定被判断的业务对象版本和决策内容，必要时保存结构化修改或理由引用。它仍然不是把所有编辑过程录屏，而是留下足以解释正式结果的专业责任链。新的对象版本产生后，旧 HumanDecision 是否仍适用也需要按因果重新判断，不能成为永久“人工已审”标签。

这条边界让人机协作真正进入 Domain，而不是停留在 UI 层按钮状态；同时 09 可以在不把人工决定改写成模型标签的前提下，统计 reviewer acceptance、修改类型和常见失败模式。

### “正式事实”为什么不是“客观法律真理”

Formal Admission 容易被误解成系统宣布某个法律结论绝对正确。实际上 02 拥有的是**Zuno 当前正式接受并愿意长期负责的业务记录**：它基于哪些材料、哪些 Evidence、什么人工判断和哪个版本形成。它可以被未来新证据推翻，也可以存在专业分歧。

因此 Formal 不应该抹掉 uncertainty、异议或来源。一个 Finding 被正式接纳，只说明它已经满足当前业务准入条件，不说明现实世界再也不会出现反例。这个区分既避免模型置信度冒充法律真理，也避免“正式”被错误实现成不可质疑的 boolean。

Domain 的职责是让系统能够解释当时为何接受、后来为何复核，而不是替专业法律判断消灭所有不确定性。

### 相互冲突的 Evidence 为什么可以同时正式存在

真实案件材料可能互相矛盾：两份证言描述不同时间，同一合同存在多个版本，银行流水和当事人陈述也可能冲突。最危险的建模方式，是为了保持数据库“整洁”而只允许一条 Evidence 成为 truth，把另一条覆盖或丢弃。

Evidence 的正式性表示来源和业务身份已经被接纳，不等于它与其他 Evidence 一致。Finding 可以记录自己依赖、支持或需要解释的证据关系，HumanDecision 可以处理冲突；新的 Evidence 进入后再触发受影响结果复核。

这样系统能够保存“我们当时面对的是一组有冲突的材料”，而不是事后只留下最终结论喜欢的那一部分。法律可解释性要求保留争议本身，而不仅是保存一个答案。

### 修正历史错误为什么应该形成新版本，而不是偷偷改旧记录

正式系统也会录错：材料元数据可能错误，人工决定可能需要更正，WorkProduct 也可能发现引用绑定有问题。发现错误以后直接 UPDATE 历史行看起来最简单，却会让已经交付的旧版本和审计记录突然指向一个从未存在过的新历史。

更安全的思路是保留原事实和更正原因，形成新的版本、supersede / invalidation 关系或受治理的修正记录；当前视图指向新的有效状态，历史仍能回答“当时系统实际保存了什么，后来为什么改”。具体表结构可以在 Detail Freeze 决定，但不能用静默覆盖牺牲时间一致性。

这同样解释了为什么删除、失效、纠错是三种不同语义：删除受生命周期政策约束，失效表示当前不再适用，纠错表示历史记录本身被后续正式事实修正。

### 当前、目标与缺口

Current 只能由现有代码、Migration、Test 和运行证据证明。完整 Target 文档不表示七对象表结构、Admission transaction、依赖传播或并发控制已经全部实现。

Target 已明确正式事实由 02 拥有，机器候选与正式事实分离，Formal Admission 以版本和 Receipt 形成恢复锚点，WorkProduct 保存稳定历史引用。Gap 仍包括字段级冻结、真实并发与崩溃测试、Migration 设计、失效传播测量，以及这些机制在真实法院工作流中的实际成本和收益。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

本模块是正式法律业务状态的唯一权威边界，遵守以下全局不变量：

1. 第一阶段 Canonical Kernel 仅包含 Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct；扩张必须另有架构依据。
2. Model、Knowledge、Capability、Specialist 和 Runtime 只产生 Proposal、Candidate、Observation、Reference 或 Receipt，不直接写 Canonical Domain State。
3. EvidenceCandidate != Evidence；CitationLineage != WorkProductCitationBinding。
4. Formal Admission 只有在持久化 Domain mutation 与匹配 AdmissionReceipt 成功后才成立。
5. 历史版本不可被静默覆盖；新证据通过依赖关系导致 review-required / stale 和新版本，而不是 destructive rewrite。
6. Runtime Checkpoint、Index write、Queue ACK、HTTP 2xx 和 Telemetry 都不能单独证明 Domain Success。
7. Domain Commit + AdmissionReceipt 与 Runtime Checkpoint 之间默认不使用跨 Store 2PC。

### B2 Responsibility / Ownership

| 责任 / 事实 | 本模块权限 | 其他边界权限 |
| --- | --- | --- |
| Matter / DocumentVersion identity | 创建、版本化、失效 / 生命周期执行 | 读取稳定引用，不自行创建替代身份 |
| Claim / Evidence / Finding | 正式准入、变更、依赖与失效 | 产生候选或读取快照 |
| HumanDecision | 保存正式人工业务决定 | UI / Host 可以采集输入，但不能拥有业务语义 |
| WorkProduct | 正式版本、有效性、历史保留 | 01 负责交付，不重算正式有效性 |
| AdmissionReceipt | 创建并与领域变更同事务提交 | 04 读取用于恢复，不修改 |
| WorkProductCitationBinding | 创建、验证、长期持久化 | 03 提供 CitationLineage / source refs，不拥有正式历史绑定 |
| Domain invalidation truth | 创建 / 变更 | 01 负责通知 Delivery / Ack observation |
| Retention / Deletion / Legal Hold policy | 不拥有政策，只执行本 Store 义务 | 08 是政策 Owner |
| Recovery truth | 领域版本 + AdmissionReceipt 是正式准入恢复锚点 | 04 修复 Runtime Control State |

**Does not own**：KnowledgeGeneration、ReadinessDecision、CitationLineage、Runtime Plan / Checkpoint、Authorization / Approval policy、Tool Effect truth、Delivery / Ack state、Telemetry projection。

### B3 Upstream / Downstream

| 方向 | 责任域 | 本模块接收 / 输出 | 边界规则 |
| --- | --- | --- | --- |
| 上游 | 03 Knowledge & Evidence | EvidenceCandidate、CitationLineage、source / generation refs | 候选不能自动升级为正式 Evidence |
| 上游 | 05 Capability & Skill | Finding / analysis proposal | 只接受候选，不接受 Provider 自称“已正式提交” |
| 上游 | 04 Agent Runtime & Control | run / PlanVersion / StepRun causation、proposal identity | Runtime 只能请求 Admission |
| 上游 | 08 Security & Governance | AuthorizationDecision、ApprovalDecision / policy refs | Domain 消费，不重算安全政策 |
| 上游 | Human / 01 Application | Human review input | 采集边界与领域决定语义分开 |
| 下游 | 04 Agent Runtime & Control | AdmissionReceipt、resulting DomainVersion | 用于完成条件和恢复 |
| 下游 | 01 Application & Integration | WorkProductVersion、WorkProductInvalidationFact | 01 负责发布 / 交付 / 通知 |
| 下游 | 09 Observability & Evaluation | 脱敏 domain/version/review refs | Telemetry 不成为业务权威 |

### B4 Authoritative Facts / Core Objects

七对象最小内核的职责语义如下；这里冻结语义，不冻结 ORM 字段或表：

| 对象 | 业务身份 | 关键依赖 / 生命周期 |
| --- | --- | --- |
| Matter | 一次长期法律业务事项 | 约束材料、主张、证据、结论和成果的业务范围 |
| DocumentVersion | 不可变材料业务版本 | 是知识派生和历史引用的稳定来源锚点 |
| Claim | 被正式记录的主张 | 可被 Evidence 支持 / 反驳，并影响 Finding |
| Evidence | 正式采用的证据 | 来源于稳定 DocumentVersion / span，可建立 Claim / Finding 依赖 |
| Finding | 正式结论 | 依赖 Claim / Evidence / HumanDecision，可能因新证据失效 |
| HumanDecision | 人工业务判断 | 接受、修改、拒绝或要求补充；不同于 Security Approval |
| WorkProduct | 对外或对内长期工作成果 | 版本化、绑定 Finding / Evidence / citation、支持 stale / review-required |

`WorkProductVersion` 是 WorkProduct 的版本化表达，不因为需要版本号就自动创建新的一级聚合。Event、Conflict、Dispute、LegalIssue、ApplicableLaw、SimilarCase 等默认保持 Proposal / Projection / Derived View，除非后续独立评审证明需要正式身份和生命周期。

### B5 Cross-boundary Contracts

#### EvidenceCandidate + CitationLineage（消费）

- Purpose：把 03 找到的证据候选及其检索来源送入正式领域判断。
- Producer：03 Knowledge & Evidence。
- Consumer：02 Legal Domain & Work Product。
- Authoritative Owner：EvidenceCandidate / CitationLineage 归 03；正式 Evidence 归 02。
- Input / Output：DocumentVersion ref、KnowledgeGeneration ref、source location、candidate payload / refs、CitationLineage → admission input。
- Versioning：必须能绑定明确 DocumentVersion / generation / scope；字段未冻结。
- Validation：来源可定位、版本未漂移、当前 Scope / Security 可用。
- Failure Semantics：来源不稳定、版本不匹配或 evidence insufficient 时不得自动准入。
- Idempotency / Replay：候选可重放；正式 Admission 由领域 idempotency identity 去重。
- Security Requirements：消费当前授权，不因候选已缓存而绕过权限。
- Persistence Requirement：候选可以是派生事实；正式采用后必须保存领域侧稳定引用。
- Observability Requirement：记录 candidate / lineage identity，不导出敏感正文。
- Evidence：Citation Provenance Guard、后续真实 lineage lookup tests。

#### AdmissionReceipt（生产）

- Purpose：证明某次运行请求导致了哪一个正式领域版本。
- Producer / Authoritative Owner：02 Domain Admission boundary。
- Consumer：04 Runtime、Recovery、Audit / Review。
- Input / Output：run identity、PlanVersion、StepRun identity、proposal / admission identity、idempotency identity、expected prior DomainVersion → resulting DomainVersion receipt。
- Versioning：绑定唯一 resulting DomainVersion 与预期前置版本。
- Validation：Domain mutation 与 Receipt 必须同一 PostgreSQL transaction durability boundary。
- Failure Semantics：无匹配 Receipt 时，不得宣布要求 Formal Admission 的 Step 正式完成。
- Idempotency / Replay：同一 admission / idempotency identity 重放返回既有合法结果；同 key 不同输入拒绝。
- Security Requirements：提交时重新消费当前授权和必要 HumanDecision / Approval references。
- Persistence Requirement：durable Domain boundary；不能只存在 Checkpoint / Trace。
- Observability Requirement：Trace 只引用 Receipt identity。
- Evidence：当前 mutation evidence + 后续 admission causation fault tests。

#### WorkProductCitationBinding（生产）

- Purpose：保存正式 WorkProductVersion 当时实际使用的不可变材料位置。
- Producer / Authoritative Owner：02，在正式准入时建立或验证。
- Consumer：Review、Audit、01 Delivery、后续 staleness analysis。
- Input / Output：DocumentVersion、immutable source ref / hash、stable location / span、source representation identity / hash、必要 excerpt / evidence hash、可选 CitationLineage ref → durable binding。
- Versioning：绑定 WorkProductVersion；不能被新 Index / Graph / Chunk 替换。
- Validation：必须回到原始不可变表示；索引内部 ID 不可作为唯一长期权威。
- Failure Semantics：正式成果要求的绑定不完整时，不得 Formal Admit 该成果。
- Idempotency / Replay：同一 WorkProductVersion + binding identity 幂等。
- Security Requirements：引用最小化、按权限展示，必要正文不写普通 Trace。
- Persistence Requirement：Domain durable boundary。
- Observability Requirement：只暴露稳定 identity / completeness 结果。
- Evidence：后续 source replacement / historical citation tests。

#### WorkProductInvalidationFact（生产）

- Purpose：声明某个已存在 WorkProductVersion 因正式依赖变化而失效或需要复核。
- Producer / Authoritative Owner：02。
- Consumer：01 Delivery、04 targeted reevaluation、Review / current-validity query。
- Input / Output：new DocumentVersion / Evidence / dependency change → affected WorkProductVersion + invalidation reason / dependency refs。
- Versioning：绑定被影响的正式版本，不覆盖历史版本。
- Validation：必须能说明由哪个已接纳依赖变化触发；不能由一次检索排名变化直接改正式状态。
- Failure Semantics：依赖图不足时扩大复核范围或进入人工复核，不能假装局部影响已知。
- Idempotency / Replay：同一 invalidation cause 对同一版本幂等。
- Security Requirements：通知内容由 01 按当前权限最小化。
- Persistence Requirement：Domain durable fact。
- Observability Requirement：Telemetry 只记录失效 identity / reason code refs。
- Evidence：后续 new-evidence staleness / invalidation tests。

### B6 Normal Flow

**新正式结果：**

```text
EvidenceCandidate / proposal
→ validate DocumentVersion + source + dependency
→ consume current AuthorizationDecision
→ evaluate required HumanDecision
→ compare expected prior DomainVersion
→ idempotency check
→ atomic domain mutation + AdmissionReceipt
→ create / validate WorkProductCitationBinding when applicable
→ expose resulting DomainVersion / WorkProductVersion
```

如果 WorkProduct 的合法性依赖历史引用绑定，则准入事务不能先把成果标为正式有效，再异步“以后补引用”；要么引用绑定已经存在并被验证，要么作为同一领域提交所依赖的耐久事实一起成立。

**新证据导致失效：**

```text
new canonical DocumentVersion / Evidence
→ dependency lookup
→ mark affected Finding / WorkProduct review-required or stale
→ emit WorkProductInvalidationFact
→ request bounded reevaluation when safe
→ new proposal
→ HumanDecision when required
→ new Formal Admission / new version
```

### B7 State / Lifecycle

这里冻结状态语义族，不冻结最终 enum 名称。

**正式结果版本语义：**

```text
candidate（领域外）
→ admitted / current
→ review-required or stale  [依赖变化]
→ superseded by newer admitted version
```

旧版本即使被 superseded，也继续作为历史事实存在；默认不通过覆盖或删除消除过去发生过的正式结果。

**HumanDecision 语义族：** 接受、修改、拒绝、要求补充。是否需要更多状态由后续详细评审决定，但必须与 Security Approval 分开。

**WorkProduct 生命周期至少区分：** 已正式形成、当前有效、需要复核 / stale、存在更新版本但保留历史。Domain invalidation、01 的 Delivery state 和 Consumer acknowledgement 不允许压成一个 `WorkProduct.status`。

### B8 Failure Taxonomy

| 失败 | 检测 Owner | 正式事实 / 立即动作 | 是否可 Retry | 是否需要 Replan / Human |
| --- | --- | --- | --- | --- |
| expected DomainVersion 冲突 | 02 | 不覆盖写；返回 version conflict | 原请求不可盲重试 | 调用方重新读取后 Replan 或人工 |
| EvidenceCandidate 来源不稳定 | 02 + 03 refs | 不准入正式 Evidence / WorkProduct | 03 可修复派生处理 | 证据无法恢复时人工 |
| 证据不足 | 02 eligibility | 不创建正式 Finding | 单纯重复同输入无意义 | 补证据 / Replan / Abstain |
| Authorization 已失效 | 08 决定，02 执行 | fail closed / pause | 重新授权后才可继续 | 可能人工 |
| 缺必要 HumanDecision | 02 | 保持 proposal / review-required | N/A | Human required |
| 同一幂等 key 不同输入 | 02 | reject conflict | No | 调用方修正 |
| Domain transaction 失败 | 02 Store | DomainVersion 不推进 | 同输入可安全 Retry | 否，除非重复失败 |
| Domain commit 成功、Checkpoint 失败 | 04 检测 + 02 Receipt | 使用 Receipt 修复 Runtime | 不重复 Domain commit | Recovery |
| Checkpoint completed、Receipt 缺失 | 04 / 02 query | 不承认 Formal Admission | 不能以 checkpoint 重放提交 | Review / causation check |
| 新证据影响范围不确定 | 02 dependency | 扩大 review-required 范围 | N/A | bounded reevaluation 或 Human |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

- **Retry（重试）**：仅用于领域事务在提交前失败、且输入、前置版本、授权和准入条件仍成立的情况；同一幂等身份不得产生第二个正式结果。
- **Replan（重规划）**：DomainVersion 冲突、依赖结构改变、证据条件变化使原计划不再正确时，由 04 读取最新领域快照后决定新 PlanVersion；02 不自行规划任务。
- **Reconcile（对账）**：外部现实副作用由 06 负责。本模块只消费已经确认的 EffectReceipt / ReconciliationReceipt，不自行猜外部结果。
- **Recovery（恢复）**：正式准入恢复锚点是 DomainVersion + matching AdmissionReceipt + 必要 WorkProductCitationBinding，而不是 Runtime Checkpoint。
- **Idempotency（幂等）**：同一 idempotency identity + 同一规范化输入返回既有合法结果；同 identity 不同输入必须冲突失败。

### B10 Security / Approval / Audit

02 在正式读取 / 准入边界消费 08 的 AuthorizationDecision、Security Epoch 和必要 Approval reference，但不拥有授权政策。

HumanDecision 是业务事实；ApprovalDecision 是高风险动作是否允许执行的安全事实。两者可以引用同一 human principal，但不能共用状态语义。

Effective Lifecycle Policy（有效生命周期政策）由 08 拥有。本模块负责执行自己 Store 中的 retention、deletion、legal hold 和必要 purge / retention obligation，并保存执行事实；执行结果不能反向改变政策。

关键领域变更需要可审计，但普通 Telemetry 不能替代要求耐久化的 Audit Fact / AuditPersistenceReceipt。Secret 不进入普通 Domain payload。

### B11 Persistence / Transaction Boundaries

PostgreSQL 是第一阶段 Canonical Domain State 的默认耐久边界。至少需要保存正式对象版本、依赖、HumanDecision、WorkProductCitationBinding 和 AdmissionReceipt；具体表结构和 Migration 尚未冻结。

关键事务边界：

```text
expected DomainVersion check
+ canonical domain mutation
+ matching AdmissionReceipt
+ admission-critical citation binding / dependency facts when required
= one Domain transactional durability boundary
```

不在该事务中等待 LangGraph Checkpointer、远端 Consumer acknowledgement 或其他远端服务提交，因此默认不引入跨 Store 2PC。

Knowledge index、Runtime checkpoint、Telemetry、Delivery state 都可以在各自边界稍后恢复，但不得被解释成已经替代 Domain commit。

### B12 Observability / Evaluation

Telemetry 需要关联 Matter、DocumentVersion、DomainVersion、Claim / Evidence / Finding / WorkProduct refs、AdmissionReceipt identity、human review outcome 和 invalidation event，但默认不导出敏感正文。

评测至少覆盖：

- provenance completeness / citation binding correctness；
- unsupported formal admission rate；
- Human review acceptance / modification / rejection；
- stale / review-required propagation correctness；
- bounded reevaluation correctness；
- admission idempotency / version conflict；
- Domain commit vs Runtime checkpoint fault recovery。

这些测量证明模块行为，不等于整个产品 production ready。

### B13 Current / Target / Gap / Evidence

**Current**：[`implementation-wave-001.md`](../evidence/implementation-wave-001.md) 证明有限 Domain mutation、CAS、幂等、事务失败保护和 Citation Provenance Guard；真实 PostgreSQL race、完整正式准入链仍未证明。

**Target**：完整七对象最小领域内核、Formal Admission + AdmissionReceipt、正式 Evidence、历史引用绑定、版本化 WorkProduct、HumanDecision、依赖失效和受控局部重评。

**Gap**：真实 PostgreSQL integration / concurrency、Admission causation fault injection、HumanDecision E2E、WorkProduct version lifecycle、新证据 bounded re-evaluation、historical citation replacement test、lifecycle enforcement 和跨运行 invalidation。

**Evidence required before Current upgrade**：代码 / Migration、真实 PostgreSQL 集成、单元 / 集成测试、故障注入、E2E、审计 / Trace 关联与评测结果。文档完整度不是实现证据。

### B14 Code / Database / Migration Constraints

后续实现必须先冻结对象 identity、version、dependency、admission、HumanDecision、historical citation 和 invalidation 语义，再讨论 ORM、table、index 和 Migration。

不得因为现有数据库字段、模型抽取结果或某个 Provider 返回结构存在，就把 Proposal 自动升级为 Canonical Object。Migration 必须保留历史版本和已发布成果的依据，不能通过 destructive rewrite 抹掉旧 WorkProductVersion 的来源。

本 Design Baseline 不授权新增 God Domain Service，不要求独立 Domain 微服务，不授权 Event Sourcing、跨 Store 2PC 或完整数据库重构。实现授权需要独立任务和验收标准。

#### B14.1 Detail Freeze Candidate：正式准入输入与回执字段组

下面冻结的是 **Target 语义字段组**，不是最终 ORM class、表名或 API JSON。字段名允许在实现评审时调整，但语义、唯一性和绑定关系不得在 Codex 实现阶段自行改变。

**AdmissionCommand candidate** 至少包含：

| 字段组 | 必需语义 |
| --- | --- |
| Scope | `tenant_id`、`matter_id`、`scope_ref` |
| Admission identity | `admission_id`、`idempotency_key`、`canonical_input_hash` |
| Concurrency | `expected_domain_version` |
| Causation | `proposal_ref`；Runtime 驱动时带 `run_id`、`plan_version`、`step_run_id` |
| Mutation | `mutation_type`、规范化 canonical payload / refs |
| Dependencies | `DocumentVersion`、既有 `Evidence / Claim / Finding / WorkProduct` version refs |
| Human authority | 需要人工业务判断时带 `human_decision_refs` |
| Security | `authorization_decision_ref`、`security_epoch_ref`、`principal_ref` |
| Provenance | 必要 `KnowledgeGeneration / CitationLineage / CapabilityVersion` refs，仅作来源，不升级为 Domain identity |

**AdmissionReceipt candidate** 至少包含：

```text
admission_id
idempotency_key
canonical_input_hash
tenant_id / matter_id
expected_domain_version
prior_domain_version
resulting_domain_version
admitted_object_version_refs
human_decision_refs when required
citation_binding_refs when required
run_id / plan_version / step_run_id when runtime-driven
proposal_ref
authorization_decision_ref / security_epoch_ref
committed_at
```

Receipt 不保存模型隐藏推理、Secret 或大段原始材料。正式成果正文、证据、引用和 HumanDecision 各自进入对应领域事实；Receipt 只证明“哪组输入以什么因果导致了哪次提交”。

逻辑幂等 namespace 至少按 `(tenant, matter, idempotency_key)` 隔离。同 key + 同 `canonical_input_hash` 重放返回既有合法结果；同 key + 不同 hash 必须冲突。当前 Wave-001 已有相近的 mutation 语义，但完整 AdmissionReceipt 仍是 Target，不得把当前 mutation record 直接宣称为最终 Receipt。

#### B14.2 Detail Freeze Candidate：七对象的 Identity / Version 规则

为避免“表里有一行就是业务身份”，第一阶段按以下语义实现：

- `Matter`：稳定 `matter_id` 是聚合根身份；每次正式变更推进该 Matter 的 `DomainVersion`。
- `DocumentVersion`：版本本身不可变，必须能绑定 source artifact identity、source representation hash / content hash 和业务可解释来源元数据；修订材料创建新 DocumentVersion，而不是覆盖旧版本。
- `Claim / Evidence / Finding / WorkProduct`：拥有稳定 logical identity，并以 immutable version record 表达历史；更新产生新 object version，不原地改写已经被 WorkProduct / Receipt 引用的旧版本。
- `HumanDecision`：默认是不可变业务决定记录；如果专业人员改变决定，创建新的决定事实并通过后续 Admission 改变当前业务结果，不回写旧决定。
- `DomainVersion`：对 `(tenant, matter)` 单调推进，只表达正式领域提交顺序，不代表 Runtime Step、Tool Effect 或 Publication 顺序。

第一阶段不要求每个对象独立维护一套全局序列。只要 logical identity、object version 与 Matter-level DomainVersion 能稳定关联，就足以支持历史和因果；不要为了“版本化完整”提前引入 Event Sourcing。

#### B14.3 Detail Freeze Candidate：依赖、引用与失效字段组

正式依赖至少需要表达：

```text
source_object_version_ref
→ dependent_object_version_ref
dependency_type
created_by_admission_id
created_at
```

`dependency_type` 只表达业务上确实影响有效性的关系，例如 Evidence supports / contradicts Claim、Finding depends on Evidence / Claim、WorkProduct includes / relies on Finding。检索相似度、模型 attention、向量邻居不自动成为正式依赖。

`WorkProductCitationBinding` 至少绑定：

```text
work_product_version_ref
evidence_ref when applicable
document_version_ref
stable_source_location
source_artifact_ref / source_representation_hash
excerpt_hash or evidence_hash when required
optional citation_lineage_ref
binding_identity
```

Stable location 可以按 PDF page/span、结构化 section/row/cell 等格式化表示；具体 locator schema 在文档格式详细设计中确定，但禁止只保存 Chunk ID / Vector ID / Graph Node ID。

失效事实至少绑定 `affected_object_version_ref + cause_object_version_ref + cause_type + invalidation_identity + created_at`。同一 cause 对同一版本必须幂等。01 的通知重试不能新增第二个 Domain invalidation fact。

#### B14.4 Detail Freeze Candidate：状态转换 Guard

本模块不把所有对象压成一个状态 enum，但正式版本至少遵守以下 Guard：

```text
proposal / candidate（领域外）
  --[版本匹配 + 来源有效 + 安全有效 + 人审满足 + 幂等合法]-->
admitted/current

admitted/current
  --[新的正式依赖变化且影响成立]-->
review-required 或 stale

review-required
  --[新的 HumanDecision / re-evaluation + 新 Admission]-->
新的 admitted version 或确认仍有效的新的 revalidation fact

admitted/current 或 stale
  --[新的 admitted version 成为当前版本]-->
superseded（历史仍保留）
```

禁止通过直接修改 `status='CURRENT'` 清除曾经发生的失效。若人工复核认为旧结论仍成立，也要保存新的决定 / revalidation 因果，而不是抹掉过去的 invalidation。

Formal Admission Guard 至少同时检查：

1. `expected_domain_version == current_domain_version`；
2. `canonical_input_hash` 与该 idempotency identity 已有记录一致；
3. 所有 admission-critical DocumentVersion / object version refs 仍存在且未被不允许的生命周期政策排除；
4. 需要正式来源的 Evidence / WorkProduct 已拥有可验证稳定引用；
5. 需要 HumanDecision 的规则已满足；
6. 当前受保护操作仍消费有效的 AuthorizationDecision / SecurityEpoch；
7. late proposal 的 causation 仍适用于当前业务版本。

任一 Guard 失败都不能靠“SQL 再试一次”转成成功。

#### B14.5 Detail Freeze Candidate：PostgreSQL 并发与事务候选

第一实现候选采用 **Matter-level serialized admission**：同一 `(tenant, matter)` 的正式 Admission 在短事务内串行化，不同 Matter 仍可并行。当前 `SqlAlchemyCanonicalDomainStore` 在 PostgreSQL 方言下已经使用 aggregate head `SELECT ... FOR UPDATE`，但真实 PostgreSQL race 尚未验证；本节只是把这一思路提升为 Target candidate，而不是把现有实现升级成 Production Evidence。

候选事务顺序：

```text
BEGIN
→ establish tenant / security execution context
→ read idempotency record by admission namespace
→ same key + same hash: return existing receipt
→ same key + different hash: reject
→ lock / compare Matter aggregate head
→ verify expected DomainVersion
→ validate admission-critical dependency refs
→ insert new immutable object versions / dependencies / citation bindings
→ advance Matter aggregate head
→ insert matching AdmissionReceipt
COMMIT
```

事务中禁止等待模型、远端 Tool、人工输入、LangGraph interrupt/resume 或外部 Consumer ACK。所有高延迟工作在进入 Domain transaction 前完成；提交窗口只做确定性校验和持久化。

PostgreSQL deadlock / serialization abort 属于数据库事务失败，只有在重新读取当前 DomainVersion、授权和依赖仍满足后才能重试。业务版本冲突则不是数据库 transient error，返回 `VERSION_CONFLICT` 类语义给调用方重新判断。

如果未来证明“同一 Matter 高频并发正式写”成为真实瓶颈，再评估更细粒度锁、optimistic concurrency 或分区；在没有 Load Evidence 前不为理论吞吐放弃简单、可证明的单聚合写顺序。

#### B14.6 Detail Freeze Candidate：Crash Window 与恢复矩阵

| Crash Window | Durable truth | 恢复动作 | 禁止动作 |
| --- | --- | --- | --- |
| 事务提交前进程退出 | 无 matching Receipt / DomainVersion 不推进 | 同 idempotency identity 重新校验后 Retry | 猜测“可能写了一半”并推进 Runtime |
| COMMIT 成功但响应丢失 | DomainVersion + matching Receipt 已存在 | 重放查询 Receipt，返回 ALREADY_APPLIED / committed result | 产生第二个版本 |
| Domain commit 成功、Checkpoint 失败 | 02 Receipt 是准入真相 | 04 读取 matching Receipt 修复 Step / Run control | 回滚领域或再次 Admission |
| Checkpoint 显示 completed、Receipt 缺失 | Formal Admission 未被证明 | 04 取消 formal-complete 推断并进入 causation check / review | 用更高 DomainVersion 冒充本 Step 结果 |
| Invalidation commit 成功、通知失败 | 02 invalidation truth 已成立 | 01 重试 Delivery；Pull validity 返回 stale | 因 Consumer 离线恢复为 current |
| proposal 计算完成后新 Evidence 先提交 | current DomainVersion / dependencies 已变化 | Admission Guard 拒绝旧 expected version；04 Replan / Human | 自动把旧 proposal 合并进新版本 |

#### B14.7 Detail Freeze Candidate：Schema Evolution / Migration 规则

具体表名仍由 Codex 任务设计，但 Migration 必须遵守以下约束：

1. 历史 `DocumentVersion / WorkProductVersion / HumanDecision / AdmissionReceipt / CitationBinding` 不做 destructive rewrite；旧版本必须继续可解释。
2. 新增 admission-critical 字段采用“新增 → backfill / verify → 约束收紧”的阶段式迁移；不能先加不可满足的强约束再临时伪造默认值。
3. 新的唯一性 / foreign-key / validation 约束上线前先检查历史冲突；发现冲突必须形成数据修复或显式 blocked migration，不静默丢数据。
4. `canonical_input_hash` 的规范化算法需要版本标识；未来算法变化时旧 Receipt 继续按原 hash algorithm/version 解释，不能重算后覆盖。
5. Citation locator / source representation schema 升级必须提供向后读取；不能因为新解析器上线就使旧 WorkProductCitationBinding 不可解析。
6. DomainVersion 不重新编号；Matter 合并、拆分或 tenant 迁移如果未来出现，必须单独 ADR / Migration 设计，不能在普通 schema cleanup 中处理。
7. 大表索引、约束和 backfill 的在线策略必须在实现任务里给出锁影响、回滚方案和实际数据库验证；本文不宣称零停机迁移已经成立。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

02 只有在以下最小矩阵通过后，才有资格从 `detail_design: candidate-v1` 进入 Module Detail Freeze Review：

| 场景 | 必须证明 |
| --- | --- |
| same idempotency key + same hash 重放 | 只返回同一 committed result，不新增版本 |
| same key + different hash | fail closed，不覆盖历史 |
| 两个 Admission 同时基于 D0 | 最多一个提交到 D1；另一个明确 VERSION_CONFLICT 或等价结果 |
| DB error / process crash before commit | DomainVersion 与 Receipt 均不推进 |
| response lost after commit | 重试能够通过 Receipt 恢复，不产生 D2 |
| Domain commit 后 Checkpoint 失败 | Runtime 从 matching Receipt 修复 |
| 新 Evidence 在旧 proposal Admission 前提交 | 旧 proposal 被 freshness / version Guard 拒绝或进入人工复核 |
| 缺失 required HumanDecision | 不创建正式 Finding / WorkProduct |
| SecurityEpoch 已变化 | 新 Admission 不使用旧 allow |
| Citation binding wrong-document / wrong-span | 正式成果准入失败 |
| WorkProduct stale 时 Consumer offline | Domain stale 不回滚；01 可独立重试通知 |
| 索引 / chunk 重建 | 历史 WorkProductCitationBinding 仍指向原 DocumentVersion / stable location |

Freeze Review 还需要真实 PostgreSQL integration、Migration apply / rollback 或等价安全验证、并发测试、故障注入和 Current Evidence 更新。只补完本节字段表不构成 implementation available。

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

02 唯一能够证明正式准入成功的锚点，是**匹配当前因果身份的 DomainVersion + AdmissionReceipt**，并满足本次准入要求的引用绑定和依赖事实。以下都不是正式准入证明：Runtime Checkpoint、RunOutcome、Model success、Capability success、Knowledge Retrieval、HTTP 2xx、Queue ACK、Telemetry span 或“发现了更高 DomainVersion”。

`WorkProductCitationBinding` 证明正式成果当时采用的历史来源；`WorkProductInvalidationFact` 证明某个正式版本已经失效 / 需复核。01 的 Delivery / Ack、09 的 Trace 都不能改变这两个领域事实。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

正式 Admission 至少可追到：

```text
Matter / expected prior DomainVersion
+ DocumentVersion / admitted Evidence dependencies
+ run_id / PlanVersion / StepRun when runtime-driven
+ proposal / admission identity
+ domain idempotency identity
+ current AuthorizationDecision / SecurityEpoch refs
→ resulting DomainVersion + AdmissionReceipt
```

对 CapabilityVersion、Model / Provider、KnowledgeGeneration 等非领域版本只保存必要 provenance ref，不把它们升级成 Domain identity。准入时必须检查与业务正确性相关的来源版本仍然有效；不能把旧 Readiness、旧授权或旧 proposal 静默用于新的 DomainVersion。

领域幂等身份只去重同一规范化领域变更，不与 Step、Tool Effect、Delivery、Model Attempt 等幂等 namespace 共用。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

Run / request cancellation 不撤销已经提交的 Domain transaction。已经正式存在的历史版本继续存在，是否 current / stale / superseded 由领域生命周期决定。

旧 PlanVersion、旧 Capability / Model invocation 或晚到并行分支产生的 Proposal，在进入 Admission 前必须重新校验 causation、DocumentVersion、expected prior DomainVersion、当前授权和必要 evidence / human-decision 条件；任何一个关键绑定过期，都不能因“计算已经完成”而直接准入。

新 Evidence / DocumentVersion 只在经过领域接纳以后触发依赖失效。03 的 stale KnowledgeGeneration、09 的质量告警或一次新的检索排序变化，本身不能直接把 WorkProduct 改成 stale；它们可以触发复核请求或新的候选输入。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

02 恢复正式业务事实时先读自己的 durable store，再帮助其他模块修复投影：

```text
Domain objects / versions
→ matching AdmissionReceipt / historical citation / dependency facts
→ current 08 lifecycle / authorization policy when继续受保护操作
→ 04 修复 Runtime Control State
→ 01 修复 publication / delivery projection
→ 09 补诊断视图
```

必须至少覆盖：Domain commit 后 checkpoint 失败；checkpoint completed 但 receipt 缺失；同 admission key 不同规范化输入；新证据在旧 Plan 并行分支运行期间到达；取消 Run 后 Admission 已经提交；旧 proposal 晚到；WorkProduct 已 stale 但旧 Delivery Ack 晚到；历史索引重建后 WorkProductCitationBinding 仍能回到原始 DocumentVersion。