from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def insert_before(path: str, marker: str, addition: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if marker not in text:
        raise RuntimeError(f"marker not found in {path}: {marker}")
    target.write_text(text.replace(marker, addition.strip() + "\n\n" + marker, 1), encoding="utf-8")


ARCH = r'''
### 19. 架构真正困难的是“时间”，不是把模块框画出来

很多系统图在静态时刻都看起来合理：材料在知识库里，Agent 在运行，结果最后进入数据库。真正让边界暴露价值的是时间。材料版本会变化，权限会撤销，模型和 Capability 会升级，旧 Plan 的并行结果会晚到，外部 Effect 会在本地不知道的时候已经发生。系统如果只描述“现在有哪些对象”，而不描述“一个事实在什么条件下还能继续被使用”，架构仍然是不完整的。

因此 Zuno 的多个版本号并不是为了追求形式化。DocumentVersion 保护材料身份，KnowledgeGeneration 保护可重建派生，PlanVersion 保护运行因果，Capability / Model version 保护计算语义，SecurityEpoch 保护授权新鲜度，DomainVersion 保护正式业务演进。它们不是一个全局大版本，因为这些事实变化的原因和 Owner 不同；强行统一版本反而会制造不必要耦合。

一个结果能否被继续使用，本质上取决于它的 causation 还是否成立。旧模型结果并不因为“旧”就必然无效；如果输入材料、专业语义和当前安全条件都没有改变，它可能仍可接受。反过来，一个刚算完的结果，如果依据的 Plan 或权限已经失效，也可能马上没有资格进入当前路径。时间新鲜度因此是按语义判断，不是简单比较 timestamp。

### 20. 跨模块一致性为什么不用一个超级事务解决

面对多个 Owner，最直觉的做法是希望“所有状态一次原子提交”，这样看起来不会不一致。但 Zuno 横跨数据库、索引、模型 Provider、外围法院系统和观测系统，其中很多参与者根本不能加入同一个数据库事务。为了追求全局原子性引入分布式 2PC，也不能让已经发出的外部 POST 回滚。

更可实现的策略是让每个 Owner 在自己的事务边界内保存足够强的事实，再通过 Receipt、版本和幂等身份形成可恢复因果。跨边界短暂不一致允许存在，但必须知道哪一个事实更权威、怎样最终收敛。例如 Domain 已提交而 Checkpoint 落后时，以 Domain Receipt 修复 Runtime；Effect 已确认而 Delivery projection 落后时，以 Effect truth 修复交付状态。

这是一种“可恢复一致性”而不是“所有东西永远同步一致”。代价是系统必须认真设计 recovery order；收益是故障不会因为一处 projection 失败就迫使已经成立的业务事实回滚，也不会依赖所有外部系统同时在线。

### 21. 为什么每个边界都要回答 Non-proof，而不只回答 Success

架构文档通常喜欢定义成功条件，却较少明确“什么看起来像成功，但其实不能证明更强事实”。Zuno 特别强调 Non-proof，是因为跨层误判经常发生在这里：Provider 200 不是专业质量证明，Capability success 不是 Domain admission，Checkpoint completed 不是正式提交，HTTP 200 不是所有远端业务流程完成，Trace exported 也不是强制审计已经满足。

把 Non-proof 写清楚，可以防止相邻模块为了方便不断升级自己的状态语义。每个 Owner 只承诺自己真正能证明的事情，上层需要更强结论时必须消费对应更强 Receipt / Decision。这种克制看起来增加了一些查询和对象，却大幅降低“一个 success 被整个系统误用”的风险。

同理，失败也不能统一成一个 ERROR。计算失败、输入过期、计划失效、安全拒绝、结果未知和人工待处理需要不同恢复方式。分类的目的不是做一张漂亮 taxonomy，而是决定系统下一步是否允许自动行动。

### 22. 性能优化为什么必须服从 Authority，而不是反过来

缓存、异步 Worker、批处理、并行、预取和多级索引都能提高性能，但它们经常把请求从原始 HTTP 上下文中分离。如果架构只在入口保存 tenant、权限或版本，后台优化越多，越容易丢掉原本保护正确性的上下文。

所以性能机制只能优化已有语义：Cache 可以加速派生结果，但不能延长授权寿命；并行可以提高 Capability 吞吐，但不能产生多个 Controller；异步 Delivery 可以解耦外部系统，但不能推迟 Domain invalidation；Read Replica 可以扩展查询，但不能让旧 projection 覆盖 Owner write truth。

这条原则给性能优化一个清楚边界：先证明优化不改变 Authority 和 causation，再讨论吞吐和延迟。必要时宁愿多一次当前安全检查或 Owner query，也不把一次旧决定变成永久 token。

### 23. Build / Buy / Extend / Defer 为什么要逐层判断

Zuno 不应该因为是研究型项目就默认自研所有基础设施。身份认证、Secret Manager、PostgreSQL、OpenTelemetry、通用 Checkpointer、消息队列和模型 SDK 都应优先复用成熟能力。项目真正需要自己拥有的是法律业务语义以及这些通用组件之间无法替代的 Authority 边界。

判断是否自研时先问最简单成熟方案能不能满足约束。如果能，Buy / Adopt；如果只缺一个法律语义薄层，Extend；如果当前没有真实需求或 Evidence，Defer。只有现成方案在正式状态、恢复、隔离或专业质量上存在明确缺口，而且这个缺口长期属于 Zuno 责任，才值得 Build。

这个原则同样适用于 Agent 框架。LangGraph 可以承担执行原语，但不自动拥有 Formal Admission；通用 Host 可以承担会话和 UI，但不自动拥有法律 Domain；Graph database 可以实现一种 Projection，但不自动证明 GraphRAG 值得保留。框架是能力来源，不是架构因果来源。

### 24. 降级为什么不能只有“换弱模型继续回答”

高可用并不意味着任何情况下都必须给出完整答案。真正合理的降级取决于缺失的是什么。如果强模型不可用但当前任务允许低成本模型且质量基线仍满足，可以路由降级；如果 Graph 路径不可用而 Hybrid Retrieval 对当前 query class 足够，可以退回简单检索。

但关键材料缺失时，正确降级可能是缩小 Scope；权限无法确认时是 fail closed；现实 Effect outcome unknown 时是等待 Reconcile；Judge 不可用时是 Evaluation BLOCKED。把所有降级都实现成“尽量生成一段文本”会把可用性优化变成正确性破坏。

因此每个模块都应定义自己能够安全降低的能力和不能越过的 floor。系统的韧性来自知道什么时候可以少做，而不是永远假装什么都能做。

### 25. 为什么 Evidence 不只是测试通过，还要能影响架构删除决定

代码测试可以证明某个 Contract 当前按预期工作，却不能证明这个 Contract 值得长期存在。复杂机制的保留需要另一类 Evidence：它是否在目标任务上改善了质量、恢复、延迟、成本或人工负担，并且收益是否超过维护复杂度。

例如 GraphRAG 的正确实现只能证明图检索“能工作”；只有对照实验才能证明它比更简单的 Hybrid Retrieval 有边际价值。Native Runtime 的 crash recovery 测试证明机制正确，但还需要和 Generic Host + Legal Backend 比较，才能知道是否值得承担长期自研宿主成本。

因此 Zuno 的架构不是单向“不断建设”。09 的评测应能够导致保留、缩小、替换或删除。一个设计能主动定义自己的退出条件，通常比“永远有理由继续加功能”更成熟。
'''

M01 = r'''
### 同步 API 和异步任务为什么要共享业务语义，而不是共享传输形态

同一个法律任务可能从 Web 同步请求进入，也可能由法院 Host 异步提交、随后轮询或接收回调。传输协议不同，不应该导致 READY、PARTIAL、Formal、Stale 等业务概念出现两套解释。

01 因此把协议适配和产品语义分开：Adapter 可以把 REST、消息或 Host SDK 统一成 canonical request；后续状态仍由相同 Owner facts 驱动。这样未来新增一个 Host 主要增加协议映射，而不是复制一套领域和安全规则。

同步接口也不应因为 HTTP 生命周期短就强迫复杂任务同步完成。真正需要长时间运行时，01 返回稳定 invocation identity，让客户端查询或订阅；简单问答仍可以直接返回。产品契约根据任务特征选择交互方式，而不是让传输机制反向决定内部架构。

### 发布决定为什么也需要新鲜度，而不能只在生成结束时判断一次

一个答案在生成完成时满足材料和安全要求，不代表几分钟后仍然允许发布。权限可能撤销，新 Evidence 可能让正式成果 stale，或者当前 consumer 的 Scope 已变化。

所以发布不是“生成完成后的固定副作用”，而是一个需要消费当前事实的边界。普通答案发布前重新确认当前安全和来源资格；正式 WorkProduct 则读取 02 的当前版本有效性。已经交付的历史不被改写，但新的下载、展示或继续使用可以被当前规则阻断。

这使 Application 层能够正确处理“结果存在但现在不该展示”的情况，而不是通过删除数据库结果来模拟权限变化。

### 为什么产品状态应该面向用户行动，而不是暴露内部状态机全集

内部可能同时存在 Run waiting、Knowledge partial、Approval pending、Delivery retrying 等状态。把这些原样全暴露给外部 Host，会让客户端绑定内部实现，未来任何模块演进都变成 API breaking change。

01 更适合组合成用户可行动的产品状态：等待材料、等待审批、正在处理、结果可查看、结果需复核、交付待确认等，同时保留诊断引用供受控排障。产品状态不是隐藏真实错误，而是把多个 Owner facts 翻译成稳定的消费者语义。

当调用方确实需要工程细节时，可以通过专门诊断接口查看 correlation 和 owner state，而不是让普通业务接口承担整个内部 observability schema。

### 多 Host 场景下为什么不能把一个消费者的确认当成全局完成

同一 WorkProduct 可能同时被 Web、法院业务系统和第三方归档服务消费。A 已经成功接收，并不能说明 B 也接收；B 离线也不应该让已经成立的 Domain WorkProduct 变回未完成。

因此 Delivery identity 与 consumer scope 一一绑定，01 记录每个目标的交付 observation，再按产品需求汇总。业务正式状态、发布资格和各消费者交付状态保持分层，才能支持“成果已成立，但某个下游仍在重试”的正常情况。

这也是为什么应用层的可靠性重点是可重复查询和可恢复传播，而不是制造一个跨所有消费者的全局提交事务。

### 01 的复杂度预算应该花在哪里

Application 层最容易膨胀，因为任何跨模块问题都可以被包装成“用户需要”。真正值得留在 01 的复杂度只应服务产品边界：稳定 request identity、Scope、对外状态、发布、交付和失效传播。

如果某段逻辑需要理解 Evidence 如何准入，应该回 02；如果需要理解索引覆盖，回 03；如果需要判断 Plan 是否可继续，回 04；如果需要确认外部 Effect，回 06；如果需要计算授权，回 08。把判断送回 Owner 看似多了一次调用，却避免 Application 成为第二套所有模块的影子实现。
'''

M02 = r'''
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
'''

M03 = r'''
### Processing Spec 为什么必须进入 generation 身份

同一批 DocumentVersion 用不同 OCR、parser、chunker、embedding 或 graph extractor 处理，会得到不同派生知识。如果 generation 只按“有哪些文件”标识，系统无法解释索引升级前后的差异，也无法可靠回滚。

因此 generation identity 需要能够绑定影响语义的 ProcessingSpec / provider versions。它不是要求把每个运行参数都暴露给业务，而是让可重建数据知道自己“由什么配方生成”。算法升级时构建新 generation，而不是静默覆盖旧 serving 数据。

这种版本化也为 Eval 提供了可比对象：质量变化可以关联到处理版本，而不是只看到数据库内容突然不同。

### Readiness 为什么必须按 Required Capability 判断

一个任务只需要文本定位，OCR + lexical / dense index 就绪可能已经足够；另一个任务需要跨文档关系分析，则还可能要求实体 / graph projection 可用。用单一全局 READY 会让前者无谓等待最慢组件，或者让后者在缺关键能力时过早运行。

Task Readiness 因此应结合 task class / required capability 和当前 Scope。它回答的是“为了完成这件事还缺什么”，不是“整个知识平台是否健康”。这一设计允许按需建设复杂派生，也让降级更具体：缺 Graph 时某些任务退回 Hybrid，缺关键 OCR 时则必须阻断完整分析。

### Retrieval Quality 为什么不仅是 Recall@K

高召回很重要，但法律任务还关心来源是否可追溯、覆盖是否足够、冲突材料是否同时出现，以及候选是否来自当前允许的 DocumentVersion。一个检索器返回很多相似片段，不代表已经找到支持结论所需的证据集合。

所以 03 的评测需要按 query / task class 看 retrieval recall、source correctness、evidence coverage、latency 和 cost；复杂 Agentic Retrieval 还要看额外 route 是否真正增加新证据。质量判断最终交给 09 的可复现实验，而不是由“Top-K 看起来相关”主观决定。

这也是停止条件的依据：继续检索只有在可以填补已知证据缺口时才有价值。

### Serving 切换为什么比“所有 Store 同时完成”更现实

一个 KnowledgeGeneration 可能包含 PostgreSQL metadata、Object Store artefacts、vector index 和 graph projection。要求它们跨 Store 原子 commit 很难实现，也没有必要。

更合理的是每个构建阶段记录自己的完成事实，generation-level validation 检查要求的 artefacts 和 manifest，最后只原子改变一个 ServingPointer / active generation reference。查询入口只消费已经验证的 generation，不直接跟踪后台写入进度。

如果某个可选 projection 构建失败，是否阻断激活取决于当前 generation profile；关键不是所有东西都成功，而是对外承诺和实际可用能力一致。

### 数据生命周期为什么要区分“停止召回”和“物理清除”

某份材料权限撤销或删除请求生效后，新检索应该立刻停止召回，即使底层向量段、缓存或对象存储还在按异步流程清理。相反，Legal Hold 可能要求物理字节继续保留，但业务上不再允许普通召回。

03 因此消费 08 的 lifecycle decision，先执行 recall eligibility，再让各派生 Store 完成 purge / rebuild。知识系统不能因为“向量还没删完”就继续返回，也不能因为查询层已经屏蔽就宣称物理删除全部完成。

这种分层使安全语义先收敛，昂贵的数据清理随后可恢复执行。
'''

M04 = r'''
### Controller 为什么要把“决定”和“执行”分离

如果 Planner 一生成下一步就直接执行，模型决策和现实动作之间没有稳定验收点。Zuno 更倾向于让 Controller 先形成计划/Step 意图，再由执行层调用 Capability、Model 或 Tool，结果回到 Controller 验收。

这种分离允许在派发前检查 Budget、Security、Capability eligibility 和输入 freshness，也允许执行并行而控制单写。模型可以提出更聪明的计划，但不能跳过确定性的安全与业务门。

它还使记录更清楚：计划说明当时为什么要做，Attempt 说明实际做了什么，Acceptance 说明结果为什么被当前计划接纳。三者混在一个 message stream 中时，很难在故障后重建因果。

### Dynamic Plan 为什么不等于“每一步都让 LLM 重规划”

动态意味着计划在证据变化或失败时可以形成新版本，并不意味着每执行一个 Step 都必须调用 Planner。稳定任务完全可以一次生成 DAG 后按确定性调度；只有已知假设失效时才值得 Replan。

过度规划会增加 token、延迟和行为漂移，也会让简单失败被模型放大成新路线。Controller 应尽量用确定性规则处理 ready queue、join、retry budget 和明显错误，把 LLM Planner 留给真正需要语义重构的情况。

这让 Agentic 不等于不可预测：动态性集中在少数明确决策点，其余控制语义保持可测试。

### 并行度为什么受正确性和资源双重约束

DAG 中多个 Step ready 并不表示应该无限同时执行。模型配额、数据库连接、外部 Tool 限流和同一事项的并发业务约束都可能限制实际 dispatch。

Controller 可以按 task priority、budget 和 provider capacity 做调度，但不得为了吞吐改变依赖语义。需要相同 Domain snapshot 的多个分支在提交前仍要接受版本冲突检查；会产生同一现实 Effect 的分支更不能只靠队列并发限制保证幂等。

因此 scheduler 优化的是“何时执行已经合法的工作”，不负责重新定义“哪些工作彼此可以并发”。

### 恢复为什么不能简单重放全部 Node

通用 workflow replay 常假设节点是纯函数或安全幂等。Zuno 的 Step 可能已经提交 Domain 或越过外部 send boundary，盲 replay 会重复业务事实或副作用。

恢复时先按 Step 类型确认外部 durable owner fact：纯计算可以依 checkpoint / input 重算；正式提交先查 AdmissionReceipt；现实动作先查 Effect / Reconciliation；等待人工则重新检查 Approval 和 Security freshness。然后 Controller 才决定 projection 修复或继续运行。

这使 Checkpointer 从“唯一恢复真相”回到合适位置：它保存控制状态，但更强的业务事实优先。

### Runtime 的复杂度什么时候应该退回普通 Workflow

如果任务没有动态依赖、长时间等待、正式 Domain commit 或现实副作用，一个普通同步 service / DAG engine 就可能足够。Native Runtime 不应因为已经存在就接管所有请求。

只有当 Replan、late result、multi-owner recovery、长任务 take-over 等机制在真实 task class 上频繁出现，并且通用 Host 很难以薄适配层满足时，Native Runtime 才值得保留完整复杂度。

这也是 04 最重要的删除条件：如果 B 方案——Generic Host + Zuno Legal Backend——已经提供同等正确性和更低维护成本，就应缩小 C 方案，而不是把“自研运行时”当项目身份的一部分。
'''

M05 = r'''
### Capability Version 什么时候应该变，Provider Version 什么时候应该变

如果只是模型权重、部署地址或运行优化改变，而专业输入输出语义保持兼容，通常属于 ProviderVersion 演进；如果“事件”的业务定义、字段含义、错误语义或可接受输出发生变化，则需要新的 CapabilityVersion。

这个区分让上层能够判断兼容性。Runtime 可以在同一 CapabilityVersion 下替换合格 Provider，而不重新理解业务；能力语义真正变化时，上层则明确选择是否迁移，而不是被隐藏升级影响。

版本规则不能只靠 semver 名字，关键是变化是否改变消费者必须理解的专业承诺。

### Deterministic Capability 和 Generative Capability 为什么可以共享能力边界

某些专业任务最适合规则或传统模型，另一些需要 LLM 开放推理。Capability 层不应该预设“专业能力就是 Agent”或“就是模型”。

只要输入输出和失败语义相同，deterministic provider、ML provider 和 LLM provider 可以竞争同一能力资格。这样团队可以用更便宜、更稳定的实现替换昂贵模型，也可以在规则覆盖不足时引入 LLM，而不改变 Runtime 的业务调用方式。

这也是研究工程化的重要价值：比较的是解决同一专业问题的方案，而不是比较框架品牌。

### Qualification 为什么要和 Release 生命周期绑定

一个 Provider 在 Dataset V3 上通过，不代表未来模型、Prompt、ProcessingSpec 或数据分布变化后永久合格。Qualification 需要绑定可复现配置和时间/版本范围，并在重大变化后重新评测。

同时不能把 Eval 服务临时不可用解释成 Provider 自动失败或自动通过。已有 qualification 是否仍在有效期、当前安全政策是否允许、任务是否落在已覆盖 profile，都需要分别判断。

这使 Eligibility 成为“当前任务现在能不能用”的组合，而不是 registry 中一个永远绿色的开关。

### Build / Buy 对专业能力意味着什么

课题组拥有研究成果，不等于所有能力都应该自研。成熟 OCR、通用 embedding、基础分类和模型 Provider 可以优先采购或复用；真正体现法律专业资产的语义、Eval 数据和特定算法可以自有。

判断标准是差异是否长期重要、是否有可维护 Evidence，以及替代成本。如果外部能力已经稳定满足专业契约，自研实现没有明显质量、隐私、成本或可控性收益，就不应为了“技术含量”重复建设。

Capability abstraction 的价值之一正是允许 Buy 和 Build 共存，而不是把所有 Provider 都吸收到一套自研框架里。

### 05 为什么不应该变成中央 Prompt / Plugin 市场

能力注册表很容易膨胀成所有 Prompt、Tool、MCP server 和插件元数据的统一市场。这样做看似平台化，却会把专业契约、模型调用、现实副作用和安全边界混在一个配置中心。

05 只拥有专业 Capability identity、版本、Provider conformance 与资格。Prompt 的具体业务语义跟随使用场景，Tool effect 由 06，模型 transport 由 07，安全策略由 08。保持这个窄边界，才能让能力层真正稳定。
'''

M06 = r'''
### Exactly-once 为什么通常不是可以对外承诺的现实语义

在单数据库事务里可以通过唯一约束实现“只写一次”，但远端法院系统、邮件、第三方 API 等现实副作用通常没有和 Zuno 共享事务。请求可能重复、响应可能丢失、双方都可能崩溃，所以端到端绝对 exactly-once 很难证明。

更诚实的目标是 logical exactly-once intent：同一个逻辑动作有稳定身份，本地重复提交被压缩，远端如果支持 idempotency key 就复用；结果不确定时通过 Reconcile 确认。最终系统能够证明“我们没有盲目创造第二个逻辑动作”，而不是宣称网络世界不会重复任何包。

对不能提供幂等或查询能力的远端，高风险动作可能必须人工确认。这是外部约束带来的真实限制，不应该被一个漂亮的 SDK abstraction 隐藏。

### Effect Class 为什么应该影响默认策略

只读查询、可安全重放的更新、具有远端幂等键的创建、可补偿动作和不可逆高风险动作，其 retry / approval / audit 要求不同。如果全部走最强门禁，简单 Tool 成本过高；全部走最弱策略，高风险动作又不安全。

Tool operation 因此需要表达足以决定恢复策略的 EffectClass。分类不是为了枚举完整，而是让系统在发送前知道：是否允许自动 Retry、是否必须 Approval、outcome unknown 时是否有机器 Reconcile 路径、是否需要强制审计。

新增 Tool 时先声明这些行为，比先写 SDK wrapper 更重要。

### Remote Idempotency 为什么必须被验证而不是相信文档一句话

供应商说“支持 idempotency”仍需要确认 key 的作用域、有效期、参数冲突行为和查询能力。如果 key 只保存几分钟，而本地任务可能数小时后恢复，就不能把它当永久保证。

06 应把远端能力作为 ToolVersion 的一部分 qualification：重复相同 key 是否返回同一效果，不同 payload 是否拒绝，超时后能否通过 key 查询。证据不足时按更保守的 EffectClass 处理。

这样恢复策略建立在已验证行为上，而不是对 Provider 的乐观假设。

### Reconciliation 为什么需要明确终止条件

无限轮询远端不是恢复。对账应有 deadline、退避、最大自动尝试和人工升级路径。远端最终返回明确结果时收敛；长期不可查询时保持 unresolved，并阻止可能冲突的新动作。

人工对账也要留下结构化结果和责任人，而不是在聊天里说“应该成功了”然后手工改状态。最终 ReconciliationReceipt 表达系统通过什么证据把 unknown 收敛成什么结论。

这使最坏情况依然有业务闭环：可能变慢、需要人工，但不会用猜测换取状态机绿色。

### Compensation 为什么不能被当作事务 rollback

补偿动作常常不能恢复原世界。例如已经发送通知后再发撤回通知，接收者仍然看到过第一次消息；外部记录删除也可能留下审计历史。

所以 Saga / compensation 表达的是“采取新的业务动作减轻或纠正先前效果”，不是 ACID rollback。原 Effect 保持历史事实，补偿拥有自己的权限、Approval、Attempt 和 Receipt。

只有把这个差异写清楚，系统才不会在 UI 上把 compensated 显示成 never happened，也不会在审计中丢失真实因果。
'''

M07 = r'''
### 模型版本漂移为什么即使 API 不变也值得治理

Provider 可以保持同一个 REST schema，却在底层模型升级后改变规划长度、抽取偏好、工具调用方式或拒答行为。对上层来说，这种 behavioral drift 可能比 API breaking change 更危险，因为它不一定触发编译错误。

因此 ModelVersion / qualification 要能标识真正影响行为的版本，关键 Role 在升级前后做回归。若 Provider 不提供稳定模型快照，系统至少记录可获得的版本标识和调用时间，并通过 Eval 监控漂移，而不是假设相同 model name 永远等价。

Gateway 不应该用隐蔽后处理强行把新行为伪装成旧行为；上层假设失效时应明确调整 Prompt、Capability 或 Plan。

### 路由稳定性为什么有时比每次选“当前最优”更重要

如果每个请求都根据瞬时价格、延迟或 benchmark 在多个模型间频繁切换，同一任务不同 Step 的行为可能不可预测，排障和评测也难以重现。

对需要一致性的长 Run，可以在开始时绑定允许的 routing profile / model family，在明确故障或 Replan 时再切换。对普通独立请求则可以更灵活地动态路由。稳定性和优化程度需要按任务权衡。

这说明路由目标不是单一最优函数，而是在质量、安全、成本、延迟和可复现性之间选择可解释策略。

### Deadline 为什么和 Budget 一样属于路由约束

一个强模型可能质量最好，但预计响应时间已经超过用户 deadline；一个便宜模型虽然快，却不满足最低质量。Gateway 需要把可用候选限制在同时满足 quality floor、security、quota 和时间预算的集合。

如果没有任何候选满足，正确结果不是一定找个模型调用，而是向上层报告不可满足，让 Runtime 调整计划、缩小任务或进入人工处理。路由层不应该通过偷偷放宽质量和安全条件来提高“成功率”。

### Provider outage 的降级为什么要区分 Role

Query rewrite Provider 故障时，可以直接使用原 query 或更简单 deterministic 规则；Planner 强模型故障时，简单任务也许退回固定 Plan；关键 legal synthesis 如果没有合格 fallback，则可能必须等待或 Review。

因此 degraded mode 与 Role 绑定，而不是 Gateway 统一写“主模型失败就用备用模型”。这种差异让系统可以安全少做，而不是在关键任务上无条件降质。

### Model Gateway 的缓存为什么要谨慎对待上下文安全

即使 prompt hash 相同，不同 tenant、matter、SecurityEpoch 或数据生命周期可能不允许共享响应。跨用户全局 cache 可以非常省钱，也可能成为数据泄露通道。

只有输入可公开共享、调用方明确允许且安全 Scope 相容时才适合复用。敏感法律任务默认把 tenant / matter / policy scope 纳入 identity，或者直接关闭响应缓存。成本优化不能扩大数据可见范围。
'''

M08 = r'''
### Policy Decision 和 Policy Enforcement 为什么必须分开

08 可以计算“当前允许/拒绝/需要审批”的安全决定，但真正读取文件的是 03，调用 Provider 的是 07，执行 Effect 的是 06，提交 Domain 的是 02。只有 Decision 没有 Enforcement，安全仍然只是纸面规则。

因此每个受保护边界既要知道去哪里取得权威 Decision，也要在自己的真实执行点 fail closed。08 不需要亲自代理所有 I/O，但要让消费者无法用“我已经拿到数据了”绕过当前政策。

这种分离也避免建立一个所有业务流量都必须穿过的巨大 Security Proxy；策略 Authority 集中，执行门分布在真正产生风险的位置。

### Security Freshness 为什么不等于把 TTL 设得极短

把授权缓存 TTL 设成一秒看似“持续”，却会制造大量远端 Policy 请求，同时仍不能精确表达策略何时变化。更有意义的是让 Decision 绑定 SecurityEpoch / resource version / purpose，并在新的受保护边界判断这些前提是否仍成立。

TTL 可以作为性能和最坏撤权延迟的一部分，但不是唯一正确性机制。关键政策变化可以推进 epoch，使旧 allow 立即失去复用资格；不相关配置变化则不必让所有缓存同时失效。

新鲜度设计最终应该能回答撤权传播上限，而不是只展示一个很小的缓存数字。

### Break-glass 为什么需要比普通管理员权限更强的审计

现实司法场景可能存在紧急访问：正常策略拒绝，但在法定条件下授权人员可以 break-glass。把它实现成一个永久 super-admin role 会让例外成为日常绕过。

更合理的是独立高风险流程：明确理由、时间限制、Scope、必要 Approval 和不可采样审计，并在事后进入 Review。Break-glass 仍然不能改变过去数据来源或替代 HumanDecision，它只扩大特定受保护动作的授权范围。

是否真的需要这类机制要由业务和合规证据决定；没有需求时不应为了“安全完整”提前实现。

### Audit 数据本身为什么也需要最小化和生命周期

审计必须足够解释谁在什么条件下做了什么，但不意味着把完整 Prompt、材料正文和 Secret 全量复制进审计库。过度记录会创造新的高敏感数据仓库。

Audit record 应优先保存身份引用、动作 hash、资源版本、Decision / Approval refs 和必要非敏感摘要，需要查看正文时回到受控 Owner store。审计自身同样受 Retention、Legal Hold 和访问控制约束。

这样耐久性和数据最小化可以同时成立，而不是“为了审计所以什么都永久保存”。

### 安全平台哪些应该 Buy，哪些必须由 Zuno 定义

身份 Provider、Secret Manager、KMS、Policy Engine 和标准审计存储都可以优先复用成熟产品。Zuno 不需要重新实现密码学、OIDC 或 Vault。

但“什么动作属于高风险法律 Effect”“什么材料允许发给哪个模型”“Approval 应绑定什么 action identity”“Formal Admission 前需要什么当前安全事实”是业务语义，不能期待通用产品自动知道。

所以 08 的自有价值在 policy model 和跨模块 Authority contract，而不是基础设施数量。成熟组件越多，Zuno 自己的安全代码反而应该越薄、越聚焦。
'''

M09 = r'''
### 好的 Observability 为什么从问题出发，而不是从“所有地方都打日志”出发

如果没有稳定 correlation 和 Owner fact，日志越多越可能只是噪音。观测设计应先列关键问题：一次结果为什么被拒绝、哪一步扩大了成本、现实 Effect 是否重复、哪个版本导致质量回退、权限撤销后是否仍有访问。

然后为这些问题提供最小可关联事件、指标和 trace attributes。高基数字段、敏感正文和每个 token 的细节只有在确有诊断价值时才记录。Observability 的目标是缩短解释时间，不是最大化数据量。

同样，Dashboard 只是 projection。事故裁决仍然回到 durable owner facts，避免“图上没有 span，所以事情没发生”的错误结论。

### Eval 为什么必须先定义 Decision，再选择 Metric

“我们要测准确率”不是完整评测目标。先要说清这次实验要决定什么：是否启用 GraphRAG、是否升级模型、是否保留 Reflection、是否允许某 Capability 进入高风险任务。不同 Decision 需要不同 case、指标和阈值。

例如判断 GraphRAG 是否保留，需要在关系型 / multi-hop query class 上和 Hybrid baseline 比质量、延迟与成本；判断 Tool Runtime 是否安全，需要 fault injection 和 duplicate-effect 指标，而不是法律问答准确率。

Metric 因 Decision 而存在，可以防止团队只展示最容易变绿的数字。

### Counterfactual / Ablation 为什么是复杂 Agent 架构的核心证据

复杂系统通常多项机制同时开启：更强模型、GraphRAG、Reflection、Memory、Specialist。最终分数提高时，很难知道到底谁贡献了收益。

Ablation 在尽量相同条件下关闭一个机制，观察质量、成本和恢复变化。必要时做 factorial / 分层实验，至少保证关键架构选择有 simpler baseline。没有这种对照，团队只能证明“整套系统能跑”，不能证明每一层复杂度值得存在。

这也是 Kill Test 的来源：如果关闭某机制几乎不影响目标指标，应该认真考虑删除，而不是寻找更多理由保留。

### 线上指标和离线 Eval 为什么互相不能替代

离线 Dataset 可复现、适合版本比较，却可能覆盖不了真实分布和运维故障；线上 telemetry 反映真实流量，但缺少稳定 ground truth，且受用户行为和版本混杂影响。

两者应互补：离线 Eval 做发布前质量和回归门，线上观测检查 drift、latency、cost、recovery 和真实失败分布，再把重要线上失败沉淀为新的 Eval cases。生产反馈进入数据集时还要遵守隐私和标注 provenance。

只看线下分数会错过运行问题，只看线上成功率又无法公平比较模型和架构版本。

### Release Gate 为什么应该能够说“不知道”

工程团队常希望 CI 最终只有绿色或红色，但质量证据有时就是不完整：样本不足、Judge 不可用、数据政策禁止运行某 profile、baseline 版本不兼容。这时 BLOCKED 比假 Pass 或假 Fail 更准确。

Release policy 可以规定某些关键 gate BLOCKED 就不能发布，也可以允许低风险 profile 在明确 exception 下继续，但必须记录是谁接受了未知风险。系统不能为了流水线顺畅把“没有测”解释成“没有问题”。

Measurement honesty 是 Evaluation 的架构职责之一。

### 成本归因为什么必须沿因果链，而不是只看 Provider 月账单

总账单只能告诉团队花了多少钱，无法解释为什么。真正优化需要知道某个 task class、Plan、Step、Capability 或模型 fallback 消耗了多少，以及这些成本是否换来质量收益。

07 提供模型 Usage，03/05/06 提供各自执行事实，09 沿 correlation 做归因和趋势。04 负责单次 Run 的预算控制，但长期“哪个机制值得删”由 09 的跨运行数据回答。

只有成本和质量共享可比较的实验身份，团队才能判断一个额外 Reflection 或 Graph route 是投资还是浪费。
'''


def main() -> None:
    insert_before("docs/architecture/architecture.md", "### 19. Current、Target、Evidence 和 Unknown 必须始终分开", ARCH)
    additions = {
        "docs/modules/01-application-integration.md": M01,
        "docs/modules/02-legal-domain-work-product.md": M02,
        "docs/modules/03-knowledge-evidence.md": M03,
        "docs/modules/04-agent-runtime-control.md": M04,
        "docs/modules/05-capability-skill.md": M05,
        "docs/modules/06-tool-runtime-effects.md": M06,
        "docs/modules/07-model-gateway.md": M07,
        "docs/modules/08-security-governance.md": M08,
        "docs/modules/09-observability-evaluation.md": M09,
    }
    for path, addition in additions.items():
        insert_before(path, "### 当前、目标与缺口", addition)
    Path(__file__).unlink()


if __name__ == "__main__":
    main()
