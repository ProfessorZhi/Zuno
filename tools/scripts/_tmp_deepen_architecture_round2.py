from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def insert_before(path: str, marker: str, addition: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if marker not in text:
        raise RuntimeError(f"marker not found in {path}: {marker}")
    if addition.strip() in text:
        return
    target.write_text(text.replace(marker, addition.strip() + "\n\n" + marker, 1), encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"text not found in {path}: {old}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


ARCH_README = r'''
## 审查一次架构改动时，先问什么

新增一个 Provider、字段、队列或缓存，通常还不算新的架构问题。真正需要回到总体架构审查的，是它改变了“谁拥有事实、什么算完成、失败以后先相信谁、旧版本怎样继续被解释”这些跨模块语义。

一次改动至少先问五个问题：它解决的真实约束是什么；最简单方案为什么不够；它有没有改变 Owner 或 Authority；失败以后由哪个耐久事实恢复；如果收益没有被测出来，怎样回退或删除。五个问题答不清楚时，先不要用新对象和新服务把不确定性冻结进架构。

反过来，如果只是 ORM 字段、SDK、Provider 地址、内部 Queue、Cache 或部署参数变化，而且既有 Owner、完成证明和恢复语义完全不变，它更可能是实现或 Detail Design 变化。这样可以防止总体架构随着每次工程调整不断抖动。

## 架构稳定不等于实现冻结

Zuno 希望稳定的是少数长期不变量：机器候选不能冒充正式事实；Runtime Checkpoint 不能冒充 Domain Commit；结果未知不能被盲 Retry；新的受保护动作要消费当前安全事实；复杂机制必须允许 simpler baseline 和删除条件。

实现则应该允许持续替换。LangGraph、模型 Provider、索引实现、消息队列、缓存、数据库表和物理部署都可能演进。一个好的逻辑边界应该让这些替换发生时，不需要重新发明业务真相。

因此阅读 Target 时，不要把“当前写了某个技术名词”理解为永久技术绑定。真正需要长期保护的是语义和恢复顺序；具体实现只有在 Evidence 证明其必要时才获得更强约束。
'''

MODULES_README = r'''
## 修改一个模块时，先定位事实，不要先画调用链

跨模块设计最容易被“谁调用谁”带偏。A 调 B，并不表示 A 拥有 B 的结果；异步消息也不天然比同步 RPC 更解耦。先问当前变化涉及的事实是什么、由谁最终证明、消费者最多能做什么，再决定它通过函数调用、Queue、Event、数据库查询还是缓存传播。

例如 04 可以调用 02 请求 Formal Admission，但完成证明仍然来自 02；01 可以查询 06 的 Effect，但不能因为自己发起了 Delivery 就拥有现实结果；09 可以订阅所有模块事件，却不会因为信息最全就升级成业务 Authority。调用方向是实现拓扑，事实 Ownership 才是架构边界。

## 模块边界不等于同步 RPC 边界

九个责任域可以先共处一个进程，也可以在以后按吞吐或隔离需要拆开。即使物理共进程，也应该保持 Owner fact、版本和完成证明；即使物理拆成服务，也不意味着每次判断都必须远程同步调用。

对可重建 Projection，可以异步传播；对当前安全门，可以在受保护动作前消费仍有效的 Decision；对正式提交和现实 Effect，则要读取能够证明完成的 durable fact。通信方式应由一致性、延迟和恢复要求决定，而不是由“模块已经画了边界”自动推出。

## 一个跨模块改动至少要通过四个问题

第一，新增事实到底由谁拥有，是否出现两个 Owner；第二，消费者看到什么才算完成，什么明确不能作为证明；第三，Owner 已成功但消费者 Projection 失败时怎样恢复；第四，旧版本、晚到结果和权限变化后，这个事实是否仍然有资格继续使用。

如果四个问题只能靠“大家约定不要出错”回答，说明 Contract 还不够稳；如果为了回答它们必须创建一个全局万能状态表，说明责任边界可能被重新混在一起。Part C 的价值就是在这里检查局部正确的模块设计跨边界后是否仍然成立。
'''

ARCH = r'''
### 27. 什么必须稳定，什么应该允许替换

架构最容易走向两个极端：要么所有东西都被称为“可替换”，最后没有任何稳定责任；要么把当前框架、数据库和对象结构全部写成不可改变的架构事实，导致任何升级都要重新设计系统。Zuno 需要稳定的是语义不变量，不是今天的实现形态。

必须稳定的包括：机器结果先是候选，正式业务事实由 Domain Owner 准入；Runtime Checkpoint 不能单独证明 Domain Commit；现实结果未知不能被 blind retry；授权在新的受保护动作前重新判断；每个更强事实都有明确完成证明和恢复顺序。这些不变量如果变化，通常意味着真正的 Architecture Revision。

应该允许替换的包括 Provider、模型、检索算法、Checkpointer 实现、Queue、Cache、ORM、表结构和大部分物理部署。替换它们时，如果上层仍然可以依赖同一个 Owner、同一种完成语义和同一条恢复链，说明抽象边界是健康的；如果换一个 SDK 就必须重新解释“什么算正式成功”，说明实现细节已经泄漏进 Authority。

这也是 Detail Freeze 应该克制的原因：冻结足以保证跨模块正确性的字段和约束，而不是把所有当前实现偏好永久写进 Contract。

### 28. 架构演进为什么要设计迁移，而不能只设计最终状态

Target 架构最终长什么样只是问题的一半。真实系统升级时，旧 Run 可能仍在执行，旧 WorkProduct 仍要被审计，旧 Provider 版本仍被历史记录引用，数据库也不可能在一个瞬间让所有数据和消费者同时切换。

因此兼容性首先是时间问题。新版本可以服务新请求，旧运行继续按自己已经绑定的 Plan、Capability、Model 或 Contract 解释；可重建 Projection 可以 backfill 或重建，但历史 Domain / Effect / Audit fact 不能因为迁移方便被改写。需要切换 Owner 存储时，也不能长期双写出两套都声称权威的事实源。

安全的迁移更像：先让新实现能够读取和解释旧事实，再建立可验证的新写路径，必要时重建非权威 Projection，最后在完成证明和恢复演练都成立后切换流量。迁移成功的定义不是“新代码部署了”，而是旧任务能恢复、历史结果能解释、失败时知道回到哪个 Authority。

这个原则同样限制物理服务拆分。把一个模块搬到独立服务，如果需要一段迁移期，就必须保持逻辑 Owner 不变；网络拓扑变化不能创造第二个业务真相。

### 29. 过载和局部故障为什么不能升级成错误业务事实

系统在高负载下最容易为了维持绿色指标而模糊边界：Queue 满了仍无限受理，Policy 服务不可用时沿用旧 allow，模型超时后把任务标成业务失败，Telemetry 丢失后认为动作没有发生。这些做法把容量问题升级成正确性问题。

Zuno 更希望每个责任域定义自己的安全降级和背压。知识构建拥塞可以让新 generation 排队，但不能污染当前已验证 serving；模型容量不足可以等待、换合格候选或明确降级，却不能偷偷放宽质量和外发政策；安全事实不可确认时高风险路径 fail closed；Effect outcome unknown 时进入 Reconcile 而不是为了释放队列强行写 Failed。

隔离的目标也不是“每个模块一个服务”，而是防止一个工作负载把另一个责任域的正确性拖垮。批量 OCR、Eval、模型调用和在线 validity query 的资源特征不同，可以先通过 Worker pool、quota、priority 和 admission control 隔离；只有证据证明进程级隔离不够，再考虑网络服务。

可用性因此不是任何时候都生成结果，而是在压力下仍能区分：哪些事情可以晚一点做，哪些可以少做，哪些必须停止，哪些事实即使系统很忙也绝不能猜。
'''

M01 = r'''
### Application Projection 为什么可以缓存，但不能成为新的业务真相

产品为了快速展示，往往需要把多个 Owner 的状态组合成一个 read model：当前任务是否等待材料、结果是否可查看、哪个消费者还在重试。这样的 Projection 很有价值，但它本质上是可重建视图。

如果 Projection 落后，而 02 已经把 WorkProduct 标成 stale，01 不能继续因为本地 `status=READY` 就发布；如果 06 已经确认 Effect 成功，而 Delivery read model 还在 retrying，也应该由 owner fact 修复 Projection。性能优化可以让普通查询先读缓存，但在会产生新的受保护动作或强业务结论时，必须知道什么时候回查更强事实。

这给 01 一个重要恢复原则：自己的 read model 可以丢、可以重建、可以最终一致；真正不能丢的是 request / publication / delivery 中由 01 自己拥有的产品事实，以及它们引用的上游 Authority。

### API 兼容为什么不仅是字段能不能解析

新增一个 optional field 往往是 schema-compatible，但语义未必兼容。旧客户端如果把新的 `PARTIAL` 当成过去的 `READY`，或者把“交付已受理”理解成“远端已经采用”，即使 JSON 解析完全成功，业务仍然错误。

因此 Host Contract versioning 应保护状态含义、完成条件、错误分类和幂等语义，而不仅是字段形状。新增状态时要问旧消费者会怎样解释未知值；改变默认路径时要问重复请求是否仍指向同一 logical invocation；交付协议升级时要保留旧版本的可恢复性。

真正需要 breaking version 的，是消费者必须改变行为才能继续正确工作的语义变化。内部对象重命名或增加诊断字段则不应轻易升级成产品级 breaking change。

### 入口过载时为什么要拒绝、排队或降级，而不是无限接受

一个入口层如果只追求“请求都收到了”，很容易把容量问题转移成更难恢复的长队列。知识构建堵塞、模型 quota 耗尽、Runtime backlog 或外部法院系统不可用时，继续无界创建 Invocation 只会增加超时、重复请求和取消风暴。

01 应把 admission control 当成产品语义的一部分：哪些请求可以立即处理，哪些可以排队，哪些应该让客户端稍后重试，哪些简单任务可以走更短路径。不同 tenant / task class 还可能需要公平性和配额，避免一个批量任务耗尽所有交互式容量。

这里不要求 01 自研完整流量平台。成熟 Gateway、Queue 和限流器都可以复用；Zuno 自己需要定义的是过载时哪些业务承诺仍然成立，以及拒绝/排队不能绕过幂等、授权和 Scope 语义。
'''

M02 = r'''
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
'''

M03 = r'''
### “没检索到”为什么不能直接解释成“材料里没有”

Retrieval 是概率性和覆盖受限的。一次 Top-K 没找到某条信息，可能因为 OCR 失败、query 表达不佳、索引路线不合适、reranker 漏排或当前 Scope 没覆盖相关材料。把 retrieval miss 直接写成“没有证据”会把搜索能力边界伪装成法律事实。

因此否定性结论需要更强证据：至少知道任务要求的材料范围是否 READY、相关 query class 是否使用了足够路线、关键来源是否真正被处理。无法证明覆盖时，正确结果可以是“当前没有找到”或“证据不足”，而不是“事实不存在”。

这个边界也让 09 的 Eval 更真实：不仅测命中什么，还要测系统在找不到时是否诚实表达 coverage 和 uncertainty。

### 检索结果为什么要保留来源多样性，而不是只追求相似度最高

法律分析里，Top-10 全部来自同一份文件的相邻 chunk，可能拥有很高相关分，却无法代表多材料事项的证据覆盖。相反，一条支持材料、一条反驳材料和一条关键时间线来源，可能对专业判断更有价值。

所以融合和 rerank 的目标不能只有单点相似度，还要考虑 source diversity、版本、冲突材料和任务所需 coverage。具体算法可以变化，但系统应该避免把重复片段数量误当成证据数量。

这也是 Graph / entity 路线可能有价值的地方之一：帮助发现跨文档关系；但如果简单 source-aware Hybrid 已经达到同样覆盖，就没有理由为“多样性”永久保留更复杂图路径。

### 新一代知识构建失败时，为什么旧 Serving 不应该一起被拖垮

后台正在构建 KnowledgeGeneration V8 时，V7 可能仍然是最后一个经过完整校验的 serving 版本。某个新 embedding Provider 故障或 graph projection 失败，不应该原地破坏 V7，让所有在线查询同时不可用。

更稳妥的做法是把构建和 serving 隔离：V8 在独立 generation 中完成、验证后再切换。失败时继续服务 V7，只能覆盖 V7 已经声明包含的 DocumentVersion 和能力；如果用户任务明确要求 V8 才包含的新材料，Readiness 就应该 BLOCKED / PARTIAL，而不是假装旧索引已经包含新事实。

这同时解决可用性和正确性的冲突：旧 verified generation 可以保住已有能力，但不能借“降级”名义隐瞒新材料缺失。

### Ingestion 和 Retrieval 为什么需要不同的资源隔离

OCR、解析、embedding 和 graph build 是重 CPU / GPU / I/O 的批处理，在线 Retrieval 更关注低延迟。如果两者无界共享同一个 Worker / connection pool，大批材料导入可能把已经就绪的在线查询一起拖死。

第一步通常不是拆微服务，而是区分 queue、并发、quota 和 backpressure，让 serving 有稳定资源下限，批处理按容量排队。只有当负载、故障半径或部署生命周期长期不同，才需要进一步物理拆分。

资源隔离的目标是保护“已验证知识仍可被使用”，而不是为了架构对称把每个 processing stage 都服务化。
'''

M04 = r'''
### “等待”为什么有时是正确进展，而不是 Runtime 卡死

长任务不一定一直有可执行 Step。关键材料未就绪、Approval pending、Effect outcome unknown、预算不足或人工 Review 都可能让 Run 暂时没有合法下一步。为了让 Dashboard 看起来有进展而强行 Replan 或继续调用模型，反而会绕过真实门禁。

因此 Controller 需要区分 deadlock / bug 和有明确 Owner 条件的合法等待。后者应该保存等待原因和唤醒条件，在对应事实变化后重新判断 freshness；前者才需要超时、告警或人工介入。

一个成熟 Runtime 的表现不是“永远在执行”，而是知道什么时候必须停止自动行动。

### Plan 激活前为什么要证明它至少可执行，而不是只看 LLM 输出像不像计划

Planner 可以生成结构漂亮但实际上不可执行的 DAG：依赖循环、引用不存在的 Capability、预算明显超限、要求当前 Scope 不允许的材料，或者计划了无法安全恢复的 Effect。等运行到一半才发现这些问题，会放大成本和失败面。

因此计划进入 active 状态前，应该先做尽可能确定性的结构与可行性检查，再判断它是否真的比简单路线有用。模型可以负责提出语义方案，Controller / Capability / Security / Budget facts 负责证明当前世界允许它执行。

这不是要求构建万能静态证明器，而是把明显错误挡在派发前。越能在激活前确定的条件，越不应该留给运行中靠 Retry 猜。

### Runtime Admission Control 为什么和 Step 并行度是两个问题

即使单个 Run 内并行度受控，系统仍可能同时启动成千上万个复杂 Run，把 Checkpointer、模型 quota 和 Worker pool 压垮。入口 01 可以做产品级限流，04 仍需要知道自己当前能承载多少 active / waiting / runnable 工作。

运行时 admission control 可以按 task class、priority、budget 和资源 profile 决定立即激活、排队或拒绝；已经激活的 Run 再由 scheduler 决定哪些 Ready Step 现在派发。两层分开，避免“每个 Run 都守规矩，但所有 Run 加起来把系统打满”。

具体 Queue / scheduler 可以复用成熟基础设施，04 自己需要保护的是控制语义和公平性，而不是自研通用集群调度器。

### Checkpoint 为什么不应该无限长成完整事件仓库

长 Run 可能产生大量尝试、模型输出和中间结果。如果为了恢复把所有历史都复制进每个 Checkpoint，状态会不断膨胀，恢复延迟和存储成本也会随运行时间增长。

Checkpoint 应保存继续控制所需的最小稳定状态和 Owner refs；不可变的 Domain / Effect / Usage / Audit 历史留在各自 Owner，诊断细节由 09 关联。必要时可以做 checkpoint compaction / snapshot，但不能因为压缩而丢掉 PlanVersion、causation 和尚未收敛的等待条件。

这让 Runtime state 保持“可继续执行”，而不是变成第二套业务历史数据库。
'''

M05 = r'''
### Schema 兼容为什么不等于 Capability 语义兼容

两个 Provider 都返回同样的 JSON，不代表它们真的实现同一个专业能力。一个事件抽取器可能把“付款发生日”解释为到账日，另一个解释为合同约定日；字段名完全一致，业务含义却已经不同。

因此 Conformance 除了 schema，还要覆盖关键语义样例、边界条件和 failure behavior。CapabilityVersion 是否兼容，最终看消费者能否在不改变专业理解的情况下继续使用，而不是看 Pydantic 能不能 parse。

这也是 Provider adapter 不应该做过度“修复”的原因：如果必须靠大量隐藏规则把一个 Provider 的输出猜成目标语义，更可能说明它没有真正 Conform，而不是 adapter 还不够聪明。

### 资格为什么应该绑定已验证范围，而不是给 Provider 一个全局绿色勾

一个模型在中文合同事件抽取上表现很好，不代表它对扫描 OCR 噪声、英文材料、超长案件或高风险正式结论同样合格。全局 `qualified=true` 会把局部 Evidence 放大成所有场景资格。

更合理的是让资格能够说明它覆盖的 task class、输入 profile、风险等级和版本。任务落在未验证范围时，可以选择更保守 Provider、降级、Review 或明确 insufficient，而不是让模型 confidence 自己决定是否“应该能做”。

资格越具体，05 越能支持真实 Build / Buy 比较：外部 Provider 也可以只在它真正有优势的范围内被采用，不需要赢得整个 Capability。

### Provider 退役为什么要考虑正在运行和历史结果

发现新 Provider 更好以后，直接删除旧版本会让正在运行的 Plan 失去自己绑定的实现，也让历史 Eval 无法解释。新请求可以逐步切到新 Provider，但已激活 Run 是否继续旧版本，要看兼容和风险；必要时由 04 明确 Replan，而不是 05 在后台热替换。

旧 Provider 即使不再可调用，它的 version identity、qualification 和历史 invocation refs 仍可能需要保留，用于解释过去 WorkProduct 或 Eval。退役的是“未来可选资格”，不是把历史事实从系统里抹掉。

这使 Capability 生命周期拥有清楚的 migration 语义：新增、限制、降级、停止新流量、最终移除执行能力，都不需要改写过去。

### 研究结果进入 Capability 为什么必须能被复现，而不是只引用论文结论

研究论文、实验 notebook 或一次 Demo 可以证明方向值得探索，但 Provider qualification 需要知道实际使用的代码、模型/规则版本、数据处理方式和 Eval 条件。否则团队无法判断后续质量变化来自算法、数据还是运行环境。

Zuno 不需要把研究工程变成沉重 MLOps 平台，但至少要把影响专业语义和质量的 artefact/version refs 与 Eval 绑定。论文是来源证据，能够复现实验并在当前任务上通过资格门，才是工程 Provider 的 Evidence。

这样研究资产可以持续进入产品，又不会因为“这是我们自己的论文算法”获得永久豁免。
'''

M06 = r'''
### 幂等为什么解决不了两个“不同但冲突”的动作

Action identity 可以防止同一个逻辑动作因为网络重试被执行两次，但它不能阻止两个不同请求对同一远端资源产生冲突。例如两个 Run 分别认为自己应该提交不同版本，二者都有不同且合法的 idempotency key，仍可能在远端互相覆盖。

是否需要 resource version、业务唯一约束、串行化或远端 CAS，要由具体 Tool 语义决定。06 至少必须让 ToolDefinition 表达这种并发前提，而不能把“我们有 idempotency key”误写成“所有并发都安全”。

这再次说明幂等是重复执行问题的一部分，不是分布式正确性的万能答案。

### Outcome Unknown 积压为什么本身就是一种运行风险

单个未知效果可以进入 Reconcile；如果外围系统长期故障，成百上千个 action 都停在 unknown，系统会积累大量“现实世界可能已经发生、也可能没有发生”的债务。此时继续产生新的冲突动作，会让后续对账越来越难。

因此 Reconciliation backlog 应影响新的执行决策：同一资源或同类高风险操作存在未收敛 effect 时，可以暂停冲突动作、降低自动化程度或升级人工。重点不是给 unknown 设置一个漂亮状态，而是限制不确定性继续扩散。

09 可以测量 unknown 数量、持续时间和人工负担；这些指标也能反过来判断某个外部系统是否适合继续自动化集成。

### 远端 API schema 没变，Effect 语义也可能已经漂移

外部 Provider 可能仍返回相同 JSON，却改变幂等窗口、异步处理方式、业务唯一键、错误码含义或“accepted”之后的真实流程。普通 contract test 可能全部通过，恢复假设却已经失效。

因此高风险 Tool 的 qualification 需要包含真正影响 retry / reconcile / confirmation 的行为，而不只检查 OpenAPI schema。发生语义漂移时，04 可能需要暂停相关 Plan，06 重新评估 RetrySafety，而不是靠 Adapter 把新错误翻译成旧枚举继续运行。

ToolVersion 的意义就在这里：版本保护的是现实动作语义和恢复假设，不只是 SDK 版本号。

### 自动化边界为什么应该受“可确认性”约束

一个 Tool 也许技术上能 POST，但如果执行后没有幂等键、查询 API、业务唯一标识，也没有可靠人工确认渠道，那么高风险动作自动化程度应该非常有限。能调用不等于能安全恢复。

因此在决定“要不要让 Agent 自动执行”之前，先问发生 timeout 后怎样确认；答案如果只能是“希望不会超时”，说明执行链还没有闭环。某些场景最成熟的设计反而是只生成 PreparedAction，让人或受控外部流程完成最终执行。

自动化价值应该和可恢复性一起衡量，而不是只比较操作节省了多少点击。
'''

M07 = r'''
### 模型调用的“可复现”为什么只能是有边界的可复现

即使记录了同一个 ModelVersion、Prompt 和 temperature，外部模型服务仍可能因为底层实现、并行采样或未公开升级返回不同文本。工程上不能承诺“未来重放一定逐 token 相同”。

真正可要求的是可解释重放：知道当时使用的 Role、Provider/Model version、Prompt / input refs、generation config、时间和安全范围，并能在同一资格条件下比较行为。需要强确定性的步骤应该优先用 deterministic checker / rule，而不是把法律正确性建立在模型逐字复现上。

这让历史审计关注“当时基于什么受控输入和模型资格得到这个候选”，而不是追求一个现实上无法保证的随机过程完全重现。

### Model Gateway 为什么不应该决定“哪些证据放进 Prompt”

Gateway 最容易因为拥有 token window 和 Provider API，逐渐把 context packing、证据选择和业务 Prompt 都收进自己。这样模型层就会悄悄开始决定法律材料范围，绕过 03 的 Readiness / Retrieval 和 05 的专业语义。

07 可以负责 token limit、transport format、provider-specific encoding 和调用约束，但“哪些业务事实应进入这次推理”由上游 task / Capability / Knowledge 语义决定，08 再决定哪些内容允许外发。Gateway 可以报告输入过大并要求上层缩减，不能自己随意丢掉它认为不重要的 Evidence。

这种边界让换模型时不会顺便改变案件证据选择，也让 context 优化仍然可被专业 Eval 检查。

### Quota 紧张时为什么要保护任务级公平，而不是谁先重试谁占满

Provider 限流或成本预算紧张时，多个 Run 可能同时 Retry / fallback。如果每个调用方独立指数重试，容易形成 thundering herd，也可能让一个大任务耗尽整个 tenant 或系统 quota。

07 可以提供 reservation / consumption facts 和当前 quota signal，04 再按 Run Budget 调度；必要时按 tenant、Role 或风险等级做公平限制。目标不是让 Gateway 变成通用 scheduler，而是让资源事实可见，避免“技术上还能发请求”被误解成“这个任务仍有预算资格”。

过载时正确行为可能是排队、换已合格的低成本模型、缩小任务或明确无法满足，而不是用无限 fallback 把 Provider 故障放大成账单故障。

### 价格变化为什么也可能让原来的路由策略失效

模型行为没变，Provider 调价或计费单位变化也可能让一个原本合理的 fallback 变得不可接受。只把质量 qualification 版本化，却把成本常量硬编码在代码里，会让 Budget 判断长期漂移。

07 应把实际 Usage / Cost settlement 与路由时的预算假设分开：路由根据当前可获得价格和 quota 做决定，事后以真实账单事实结算；09 再观察长期 cost/quality trade-off。成本变化通常不改变 Capability 语义，但可以改变某个模型在特定 profile 下是否值得选。

这样“更便宜/更贵”影响优化策略，不会偷偷改变正式业务正确性。
'''

M08 = r'''
### Authorization 到真正执行之间为什么还存在 TOCTOU 风险

即使 08 在某一时刻返回 ALLOW，执行模块真正读取文件、发送模型请求或越过 Tool send boundary 之前仍可能经过排队、重试和人工等待。期间 SecurityEpoch、资源版本或 Approval 都可能变化，这就是典型的 time-of-check / time-of-use 问题。

解决方式不是把所有动作塞进一个巨大安全事务，而是让 Decision 绑定关键前提，并在真正产生风险的边界尽量晚地验证当前适用性。已经发生的历史动作不回滚，尚未发生的新动作则不能拿旧 allow 当永久票据。

因此“拿到 AuthorizationDecision”只是满足门禁的一部分，消费者还必须确认它仍匹配当前资源、动作和 policy epoch。

### 后台 Worker 为什么不能继承用户的全部长期权限

异步任务离开 HTTP 请求以后，如果直接保存一个长期用户 token 或管理员 Secret，任何后续 Step 都可能拥有超过自己需要的权限，凭证泄露的影响面也会被放大。

更合理的是传播稳定 principal / scope refs，在每个受保护边界获得当前 Decision，并让 Secret 通过受用途和时间限制的 lease 使用。Specialist、Subgraph 或 Tool Worker 的权限上限不能高于触发它的合法 Scope，也不能因为它是“系统内部服务”就自动绕过政策。

这是一种 least-privilege delegation：长期保存的是身份和因果，不是无限期可执行所有动作的能力。

### “允许执行”为什么不等于“这个动作业务上是正确的”

08 可以证明当前主体有权执行某个动作、数据允许外发、审批满足政策，但它不负责判断模型结论是否正确、Evidence 是否充分、Tool 参数是否符合专业语义。安全 Authority 也不能变成新的 God Validator。

例如一个动作完全有权限，却引用了错误案件版本；这应该由 01/02/03/05/06 的业务与执行语义拦截。反过来，一个专业结果再正确，如果当前没有授权，也不能越过 08。

把 permission 与 correctness 分开，可以防止“Security 已经 allow，所以后面无需校验”的危险推断。

### Policy 版本升级为什么也需要兼容和可回溯

安全策略会演进：某类模型 Provider 可能被禁止，Approval 门槛可能提高，数据生命周期规则也可能变化。如果只覆盖一份全局配置，事后很难解释历史动作为什么当时被允许，也无法区分旧决定是“当时合法”还是“现在仍适用”。

SecurityEpoch / PolicyVersion 的价值就是把历史 Decision 绑定到当时规则，同时让新动作识别政策已经变化。策略发布机制可以复用成熟 Policy Engine，但 Zuno 需要保留足够版本和 reason，支持回溯、撤权传播和安全回归测试。

策略升级的目标不是让过去瞬间变非法，而是让未来受保护动作按新规则收敛，并能解释这个边界发生在什么时候。
'''

M09 = r'''
### SLO 和 Eval 为什么不能合成一个“系统分数”

SLO 更关注运行服务是否在承诺时间内可用、延迟和错误率是否受控；Eval 关注法律结果、证据、恢复和复杂机制的质量是否达到目标。一个系统可以 P99 很漂亮但引用质量很差，也可以离线准确率很高却经常因为外部 Effect unknown 无法完成真实任务。

因此运行可靠性和结果质量需要分别定义，再按 task class 一起看。SLO 告诉团队“服务有没有稳定工作”，Eval 告诉团队“稳定工作出来的东西是否值得”。把二者压成一个总分，很容易让高流量简单请求掩盖低频高风险错误。

09 可以把两类 Evidence 关联到同一版本和发布决策，但不能让一个维度自动替另一个维度通过。

### Correlation 为什么能帮助解释，却不能证明因果

Trace 可以显示 GraphRAG 打开时某次请求更慢，也可以显示 Reflection 发生后结果最终通过，但这只是同一时间线上的相关性。要证明某机制导致质量提升，需要尽量控制其他变量的 A/B、ablation 或 counterfactual 比较。

这就是 Observability 和 Evaluation 的互补：前者帮助找到假设，后者用实验验证假设。仅凭 Dashboard 上两个曲线同时变化，就决定永久增加一个架构组件，很容易把偶然相关写成设计因果。

反过来，实验发现收益后仍要回到线上观察真实分布和故障面，避免离线环境的因果结论在生产条件下失效。

### Metric 变成目标以后，为什么要主动防 Goodhart

一旦团队知道 release gate 只看某个数字，就会自然优化这个数字：检索器可能通过返回更多重复片段提高某种 recall，模型可能学会 Judge 偏好的表达，人工标注也可能逐渐适应系统输出。指标继续变绿，不代表真实法律工作更好。

所以关键决策要保留多维指标、critical failure、holdout / exposure provenance 和人工抽查，并定期检查“这个 Metric 是否仍然代表原始目标”。尤其 LLM Judge 不能成为唯一自我循环的裁判。

Evaluation 的职责不是制造一个永远上涨的分数，而是持续发现现有指标在哪些情况下会说谎。

### Eval 成本为什么需要分层，而不是所有提交都跑最贵 Judge

确定性 schema、引用、幂等和安全 Contract 可以在每次变更快速检查；小规模高价值案例适合常规回归；昂贵 LLM Judge、fault injection、长任务恢复和大样本 benchmark 可以按风险与发布阶段运行。把所有验证都放在同一层，要么 CI 慢到没人愿意跑，要么为了速度被迫把深度测试删掉。

因此 Evaluation 可以形成测试金字塔：便宜、确定的 gate 高频运行；高成本专业 Eval 在影响相关能力时运行；更大规模 baseline / ablation 在架构或发布决策前执行。具体自动化频率是工程选择，原则是让证据成本与风险匹配。

这也帮助保持 BLOCKED 的诚实语义：高成本条件暂时不具备时，可以明确哪些证据缺失，而不是用一组便宜测试冒充完整质量证明。

### 事故案例进入 Dataset 时为什么要防止测试集被慢慢训练掉

把线上失败沉淀成回归 case 很有价值，但如果同一 case 立刻被 Prompt tuning、few-shot 或人工规则直接针对，随后又继续留在“独立测试集”，分数会越来越乐观。

因此生产事故进入 Eval 后需要记录 exposure：它可以成为 regression set，验证同类错误不再出现；真正评估泛化能力仍要保留未暴露 holdout 或新的代表性样本。线上反馈、训练资产和测试证据不能因为都在一个仓库里就失去边界。

这让“系统从事故中学习”和“我们仍然有可信的独立评测”可以同时成立。
'''


def main() -> None:
    insert_before("docs/architecture/README.md", "## 九模块当前治理状态", ARCH_README)
    insert_before("docs/modules/README.md", "## 当前模块设计状态", MODULES_README)
    insert_before("docs/architecture/architecture.md", "### 19. Current、Target、Evidence 和 Unknown 必须始终分开", ARCH)
    replace_once("docs/architecture/architecture.md", "### 19. Current、Target、Evidence 和 Unknown 必须始终分开", "### 30. Current、Target、Evidence 和 Unknown 必须始终分开")
    replace_once("docs/architecture/architecture.md", "### 20. 读完整体架构后应该留下什么", "### 31. 读完整体架构后应该留下什么")

    insert_before("docs/modules/01-application-integration.md", "### 当前、目标与缺口", M01)
    insert_before("docs/modules/02-legal-domain-work-product.md", "### 当前、目标与缺口", M02)
    insert_before("docs/modules/03-knowledge-evidence.md", "### 当前、目标与缺口", M03)
    insert_before("docs/modules/04-agent-runtime-control.md", "### 当前、目标与缺口", M04)
    insert_before("docs/modules/05-capability-skill.md", "### 当前、目标与缺口", M05)
    insert_before("docs/modules/06-tool-runtime-effects.md", "### 当前、目标与缺口", M06)
    insert_before("docs/modules/07-model-gateway.md", "### 当前、目标与缺口", M07)
    insert_before("docs/modules/08-security-governance.md", "### 当前、目标与缺口", M08)
    insert_before("docs/modules/09-observability-evaluation.md", "### 当前、目标与缺口", M09)

    Path(__file__).unlink()


if __name__ == "__main__":
    main()
