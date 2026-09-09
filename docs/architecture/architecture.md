# Zuno 目标架构：从一条法律任务的失效过程理解系统边界

法律智能系统最容易被低估的地方，不是模型能不能回答问题，而是一个答案离开当前请求以后会经历什么。

设想一项合同争议分析。用户上传合同、补充协议、聊天记录和几份扫描附件，希望系统梳理付款义务、违约事实和可引用的材料。第一版产品完全可以很简单：应用层确认访问范围，RAG 找相关文本，模型生成回答，页面把引用展示出来。对于“合同第 8 条写了什么”这类问题，这条路径已经足够，继续增加 Agent、状态机和服务只会让系统更慢、更难维护。

Zuno 的 Target Architecture 不是从“我们想做九个模块”开始的。它从同一项工作不断变长以后出现的失败开始：材料还没准备齐，研究模型要被替换，机器结论要经过专业人员接纳，任务运行中进入新证据，正式提交和运行进度先后落盘，外部系统超时，权限又在等待期间发生变化。每一次失败都迫使系统回答一个更具体的问题：**现在到底发生了什么，谁有资格证明它，崩溃以后应该先相信哪一份记录。**

下面的场景描述的是 Target 设计用来解决的问题，不代表这些机制已经全部在 Current 代码或真实法院环境中验证。Current 的实现、测试、Trace、Eval 和运行证据只以 [`docs/evidence/`](../evidence/README.md) 为准。

<!--
status: normative-target
architecture_state: ACCEPTED_TARGET
overall_architecture_state: ROUND_02_FROZEN
target_logical_module_count: 9
final_module_count: 9
module_decomposition_gate: OPEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_detail_freeze: NOT_YET
implementation_authorization: NO
owner: Cross-cutting Architecture Owner
canonical_question: Zuno 作为一个长期法律智能工作系统，应该怎样划分事实权威、执行控制、知识能力、安全和现实副作用，使系统可以解释、恢复和演进？
project_source: docs/project/README.md
module_source: docs/modules/
decision_source: docs/decisions/
evidence_source: docs/evidence/
research_source: docs/research/
-->

## Part A — Human Narrative（人类技术叙事）

### 从一条足够简单的路径出发

先把最常见的任务做对。用户问一个材料中已经明确存在的问题，应用服务确认用户可以读哪些文件，检索系统找到条款，模型在这些材料上组织答案，最后检查引用和当前发布条件。这里没有长期计划，没有外部副作用，也没有需要正式保存数月的专业工作成果。受控 RAG、成熟模型 SDK 和普通后端已经可以承担大部分工作。

这种简单方案值得保留，因为后面的每一层复杂度都应该有具体触发条件。系统拥有 Runtime，不意味着所有请求都先构造动态 DAG；系统拥有 GraphRAG 路径，不意味着所有查询都走图；系统定义 Formal Admission，也不意味着普通问答必须进入正式法律领域状态。

问题从任务拥有生命周期开始。

同一个事项可能有合同 v1、v2、v3，补充协议刚刚上传，关键附件仍在 OCR，聊天记录又在分析过程中补入。专业人员会修改机器建议，某个工作成果可能已经交付，外部系统也可能在 Zuno 崩溃以后继续保持先前动作的结果。此时“最后一次模型输出”已经不足以描述这项工作。

### 当一次回答变成一项长期工作

先看材料。

用户上传了一百份材料，九十八份已经完成解析和索引，两份扫描附件还没有 OCR。后台如果只看“上传成功”或“向量库里已经有数据”，很容易开始一次声称覆盖全案的分析。偏偏缺失的两份可能正好决定付款日期。

这时需要分开的第一件事，是**材料本身的正式身份**和**围绕材料建立的可重建知识**。合同 v3 作为业务材料版本需要长期稳定；OCR、切分、Embedding、图结构和索引可以因为算法升级而重建。即使这一代知识已经可以 serving，当前任务仍要判断自己的材料范围是否足够。简单条款定位也许已经能做，全案违约金额判断却仍应等待或明确缩小范围。

工程实现把这两层派生语义称为 `KnowledgeGeneration` 和 `ReadinessDecision`。名字放到这里才有意义：前者描述一代知识加工结果，后者描述“为了完成当前任务，现在够不够用”。

材料准备以后，第二个变化来自专业能力。

课题组已有事件抽取模型能够返回结构化事件，新的 LLM 也能返回类似 JSON。让 Runtime 直接调用某个 Python class 是最快的接入方式，但一旦更换实现，上层会被迫重新理解字段含义、失败语义、支持的案件范围和质量假设。两个实现都能返回 JSON，并不能证明它们对“事件”的专业定义相同，也不能证明它们都适合当前任务。

Zuno 因此先稳定“这项专业能力承诺什么”，再选择谁来实现。这个稳定专业承诺称为 Capability；研究模型、规则、LLM 或外部服务是 Provider。Provider 能接上接口只是起点，是否能服务某类任务还要有独立的 Conformance、Qualification 和 Eval 证据。研究成果由此可以进入工程系统，而 Runtime 不必绑定论文模型的具体实现。

接下来，机器已经找到材料，也已经形成一个看起来很合理的违约判断。专业人员阅读后修改了其中一处时间认定，并接受剩余部分作为正式工作依据。

到这里，“机器认为是什么”和“业务愿意长期负责什么”第一次真正分开。检索命中、模型答案、Capability 输出都先停留在候选世界；正式 Evidence、Finding、HumanDecision 和 WorkProduct 由 Legal Domain 在满足材料版本、专业规则、必要人审和当前安全条件后接纳。以后模型再强，也不能通过一次成功调用直接改写正式业务事实。

这条边界不是为了给模型输出多加一层审批，而是为了让系统几年后仍能解释：当时采用了哪一版材料，机器建议是什么，人改了什么，最终结果为什么成立，新证据进来以后哪一版工作成果需要复核。

### 故障让“完成”这个词失去统一含义

长期任务里最危险的窗口，经常发生在两个系统都各自“成功”以后。

假设 Domain 已经完成正式提交，新的 WorkProduct 和业务版本都已经落盘；Runtime 正准备写下一份 Checkpoint，进程却在这几毫秒内崩溃。重启以后，如果 Controller 只看旧 Checkpoint，就会以为正式提交还没发生，并再次执行同一动作。

恢复顺序因此必须反过来：先到拥有业务权威的地方确认正式事实是否已经存在，再修 Runtime 的控制进度。正式准入会留下能够重放查询的 `AdmissionReceipt`，它和对应的 DomainVersion 一起证明“这次业务提交已经发生”。Checkpoint 仍然重要，但它证明的是控制流程走到了哪里，不负责宣布法律业务已经成立。

同一个区别也出现在计划变化里。任务运行二十分钟后，新证据进入，Controller 形成新的计划；旧计划中的一个并行分析此时才返回，而且结果本身质量很高。系统不能因为“计算成功”就自动接纳它，也不能因为“晚到”就自动丢弃。它需要检查这份结果基于哪一版计划、哪一版材料和哪些仍然有效的前提，再决定继续使用、重新验收或重做。

Zuno 用 `Single Controller` 收敛这类全局控制：专业计算可以并行，多模型和 Specialist 也可以并行，但计划版本的激活、Replan、Join、Budget、取消和晚到结果接纳由一个逻辑写者维持因果顺序。需要改变计划时创建新的 PlanVersion，而不是在已经派发出去的旧计划上原地改写。

再往外一步，失败的含义又变了。

系统准备把一份正式成果提交到外围法院系统。请求已经发出，连接却在响应到达前超时。此时本地只知道“没有拿到结果”，不知道远端没执行，还是已经执行成功而响应丢失。把 timeout 写成 Failed 然后自动 retry，可能制造第二次提交。

Tool Runtime 会在发送前固定这次现实动作的身份和内容，形成 `PreparedAction`；越过 send boundary 后，如果结果未知，就保留这种不确定性并进入 Reconcile。系统优先使用远端幂等键、业务唯一键、查询接口或人工方式确认过去究竟发生了什么，确认以后再形成 `EffectReceipt` 或对账结果。Retry 用来重复仍然安全的同一计算，Replan 用来改变已经失效的计划，Reconcile 用来查清过去的现实动作；三者处理的是不同问题。

### 时间还会改变权限和业务有效性

长任务也把安全问题从“入口鉴权”变成了时间问题。

任务开始时，用户有权读取附件 A。系统随后等待 OCR、运行检索、调用模型并进入人工确认。二十分钟后，Matter 归属或用户权限发生变化。过去那次合法读取仍然是历史事实，但下一次重新读取正文、向模型外发数据、取得 Secret 或执行高风险 Tool 时，不能继续把任务开始时的 allow 当永久通行证。

Security & Governance 因而在新的受保护边界出现时重新判断当前主体、当前资源、用途、政策版本和必要 Approval。它不替专业人员决定法律结论；专业 HumanDecision 仍然属于 Domain。安全审批也不因为专家认可结论就自动成立。

新材料则从另一方向改变“当前有效”。WorkProduct V3 可能在昨天完全合理，今天新 Evidence 进入以后需要复核。系统保留 V3 当时真实存在以及为什么成立，同时形成 stale、superseded 或新的版本关系。历史记录不能被今天的答案静默覆盖，否则审计、交付和复盘都会失去时间一致性。

### 九个责任域在这些问题之后才出现

走完这条案件时间线以后，九个责任域不再是一张先验分类表，而是九类不同事实的长期 Owner。它们是逻辑责任边界，不等于九个进程、九个数据库或九个网络服务。

| 责任域 | 它长期回答的问题 |
| --- | --- |
| **01 Application & Integration** | 外部请求怎样被接收、发布、查询和交付，多个 Owner 的事实怎样组合成稳定产品行为 |
| **02 Legal Domain & Work Product** | 哪些材料和专业结果已经成为正式业务事实，历史版本和失效关系怎样保存 |
| **03 Knowledge & Evidence** | 正式材料怎样变成可重建知识，当前任务是否准备好，检索候选从哪里来 |
| **04 Agent Runtime & Control** | 长任务当前按哪个计划运行，哪些 Step 可以执行，等待、取消、Replan 和恢复怎样收敛 |
| **05 Capability & Skill** | “事件抽取、冲突识别、类案检索”等专业能力承诺什么，哪些实现当前有资格提供它 |
| **06 Tool Runtime & Effects** | 系统准备让现实世界发生什么，实际发出过什么，结果未知时怎样对账 |
| **07 Model Gateway** | 某次模型调用为什么选择这个 Provider / Model，真实调用和 Usage 是什么 |
| **08 Security & Governance** | 当前这一刻能不能继续读、外发、取 Secret、审批或执行受保护动作 |
| **09 Observability & Evaluation** | 一次执行发生了什么，以及某层复杂度是否通过可重复实验证明值得保留 |

Platform / Infrastructure 位于这些责任域下面。PostgreSQL、Object Store、Queue、Checkpointer、Secret Manager、身份系统、OpenTelemetry、模型 SDK 等成熟基础设施优先复用。Zuno 自己必须拥有的是基础设施无法替法律业务决定的语义：什么正式成立，什么材料足够，什么时候计划已经过期，外部动作究竟是否发生，当前权限是否仍允许下一步。

更精确的 Authority、Contract、状态、完成证明、恢复顺序和跨 Store 约束在 [`reference.md`](reference.md) 以及各模块的 Engineering Reference 中维护；总体图见 [`architecture-views.md`](architecture-views.md)。

### 正常运行、恢复和交付是一条连续链

正常情况下，01 先把外部请求归一化成可信主体、Matter 和任务范围。08 判断当前访问是否允许，03 确认任务需要的材料和知识已经具备。简单问题可以直接走检索和模型短路径；真正需要长期等待、并行分析、人工介入或正式提交的任务才交给 04。

Runtime 在执行过程中调用 05 的专业能力、07 的模型和 03 的检索。它们产生候选结果和运行事实，必要时由 02 完成正式准入。只要结果仍然只是 Draft 或 Candidate，系统就可以自由重算、替换 Provider 或调整检索路线；一旦进入正式 Domain，就需要稳定版本、引用和业务因果。

如果结果需要离开 Zuno，01 继续拥有“应该交付什么”的产品语义；真正改变外围世界的发送交给 06。08 在受保护边界重新检查当前条件，09 用 correlation 把这一整条时间线串起来供诊断和评测，但 Trace 本身不会升级成业务真相。

故障恢复也沿这条边界反向确认。先问哪个 Owner 已经留下更强的耐久事实：Domain 是否已经提交，外部 Effect 是否已经确认，当前安全条件是否仍允许继续，知识版本是否仍能服务这次任务。随后 Runtime 修复自己的 Checkpoint 和计划投影，Application 再恢复对外状态。这样进程崩溃不会把较旧的控制记录升级成全系统唯一真相。

### 复杂度必须接受删除

Zuno 的复杂能力都应该有退出条件。

如果语料规模小、文本干净、没有多版本和复杂 Scope，03 可以只保留一个版本化 Hybrid Retrieval；GraphRAG 不需要存在。如果专业能力只有几个稳定内部函数，没有多 Provider 和独立质量门槛，05 可以薄到 Python Protocol + tests。任务不跨越等待、恢复和正式提交时，04 可以退回普通 workflow 甚至同步调用。外围 Tool 都是只读或强幂等时，06 不需要给每个 GET 套完整 Effect 状态机。

同样，Generic Host 已经提供成熟会话、UI、工作流和 Checkpoint 时优先复用。逻辑责任域只有在独立扩缩容、Secret 隔离、网络出口、故障半径、合规或部署生命周期形成真实约束时，才值得拆成独立网络服务。默认起点仍然是**模块化 Python 后端**和按资源需求拆出的 Worker，而不是按九个责任域画九个微服务。

GraphRAG、Memory、Reflection、Specialist、更贵模型和 Native Runtime 都应该和更简单 baseline 做可比实验。09 的任务之一就是让已经实现的复杂度可以被删除。某个机制在同任务、同语料和可比预算下长期没有稳定收益，最合理的架构动作就是关闭它或缩回更简单路径。

### Current / Target / Evidence / Unknown

**Target：** 当前接受的总体设计仍然是九个逻辑责任域，围绕事实 Authority、完成证明、因果版本和恢复顺序协作。模块 Design Baseline 与 Cross-Module Consistency 已有文档基线，但 `module_detail_freeze: NOT_YET`，`implementation_authorization: NO`。

**Current：** 代码库中已经存在部分 Agent、Knowledge、Model Gateway、Tool、评测和基础设施实现，也有历史测试与 Eval 证据；这些实现覆盖到什么程度，不能从 Target 文档反推。Current 只由 [`docs/evidence/`](../evidence/README.md)、代码、Migration、Test、Trace 和可复现 Eval 证明。

**Evidence：** 历史提交可以证明部分 PostgreSQL 迁移、知识流水线、GraphRAG 实验、Context / Memory、Tool Calling、模型与 Eval 基础工作。它们证明局部工程事实，不证明九个 Target 责任域已经全部落地，更不证明 Production Ready。

**Unknown：** 真实长任务的系统级崩溃恢复、外部 Effect 对账、持续授权、正式 Domain Admission、容量、HA / DR、法院侧完整结果和生产资格仍需要对应证据。设计文档把这些边界说明得再完整，也不能替代测试和运行证明。

单个责任域的连续 Human Narrative 见 [`docs/modules/`](../modules/README.md)；总体 Engineering / Agent 精确参考见 [`reference.md`](reference.md)。长期架构决策进入 [`docs/decisions/`](../decisions/README.md)，研究候选进入 [`docs/research/`](../research/README.md)。
