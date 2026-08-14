<!-- Archive metadata: normalized without rewriting the historical record. -->
series: ARCHITECTURE_INTERVIEW
round_id: 01
execution_mode: MANUAL
status: ARCHIVED
base_sha: b00f5bb3fb0bad9168a1dce96d9e4817a60d9773
archive_commit: RECORDED_IN_FINAL_HANDOFF
architecture_revision_commit: NOT_CHANGED_IN_THIS_TASK
round_format: LEGACY_PACKET
source_session: manually coordinated across three ChatGPT threads; archived in this file

# Red / Blue Round 01 — Overall Architecture Narrative

archive_status: completed
round: 01
round_base_sha: b00f5bb3fb0bad9168a1dce96d9e4817a60d9773
main_theme: Overall Architecture Narrative
auxiliary_theme: Project Reality + Build/Buy + End-to-End Runtime Chain
round_owner: Main Architecture Coordinator
archive_role: historical adversarial architecture record
round_sequence: first Red / Blue adversarial round
execution_mode: manually coordinated across three ChatGPT threads
canonical_fact_source: docs/project/
canonical_target_source: docs/architecture/
canonical_decision_source: docs/decisions/

> 本文是 Append-only Red / Blue 对抗历史记录。
> Red Questions、Blue Answers、Red Review 和 Blue Reflection
> 保留当时原文，不代表所有内容最终被 Main 接受。
> 正式架构结论以 STAGE E — MAIN COORDINATOR JUDGMENT
> 以及后续 Canonical Architecture / ADR 为准。

================================================== ZUNO RED / BLUE ROUND PACKET

PACKET_VERSION: 1

ROUND: 01

BASE_SHA: b00f5bb3fb0bad9168a1dce96d9e4817a60d9773

STATUS: BLUE_REFLECTION_COMPLETED

MAIN_THEME: Overall Architecture Narrative

AUXILIARY_THEME: Project Reality + Build/Buy + End-to-End Runtime Chain


---

STAGE A — RED INTERVIEW QUESTIONS

看完 Part A，我这一轮首先想确认：Zuno 讲的是一个真实业务逐步长出来的系统，还是把很多 Agent 能力组合成了一个看起来完整的平台。 第二，我会严格区分历史项目、当前仓库和后来重新设计的 Target，尤其不会把 Pilot、代码目录或架构文档当成生产证据。 第三，我想知道 Zuno 真正必须自己拥有的东西是什么，哪些完全可以交给 LangGraph、WorkBuddy、Dify、OpenViking、MCP 或普通后端。 最后我会让一个真实任务从头跑到尾，再制造故障、冲突和规模变化，看现在的整体边界是不是还能讲通。

Q1.

先把 LangGraph、GraphRAG、Memory 这些词都放一边。

如果我是第一次听这个项目，你用几分钟告诉我：

Zuno 最开始为什么会有？谁遇到了什么问题？原来这个工作是怎么做的？

我尤其想知道真实项目里最初的需求是什么，而不是现在重新设计完以后，你觉得它应该解决什么。

Q2.

那这个问题为什么不能用一个普通的企业知识库解决？

比如：

上传法律材料 → BM25 / 向量检索 → 大模型回答 → 人工检查

你给我举一个真实、具体的业务任务。

这个任务到底在哪一步让这种简单方案开始不够用了？

如果简单 RAG 已经能解决大多数问题，Zuno 剩下的复杂度是为了哪一小部分问题存在的？

Q3.

现在 Part A 明显把系统聚焦在法律、司法、高风险任务上。

这个定位是历史项目当时就明确存在的，还是你们后来重新梳理 Architecture 时进一步收窄出来的 Target？

如果我把“法律”两个字拿掉，Zuno 剩下的是不是一个普通的 Agent + RAG 平台？

如果不是，真正还剩下什么区别？

Q4.

再讲一下团队。

你加入这个项目的时候，项目已经有什么？

团队大概怎么分工？

然后只讲你自己的部分：

你实际接过什么任务，改过什么东西，遇到过什么问题？

像 Agent、Memory、OpenViking 接入、Tool Calling、GraphRAG、后端、部署这些能力里，哪些确实是你做的，哪些只是团队能力，哪些是你后来参与架构重构才深入设计的？

如果现在让我打开代码，你最愿意现场讲哪两三块？

Q5.

这个项目实际交付到哪一步？

我会严格区分：

内部 Demo、客户 Demo、法院人员测试、Pilot、正式 Production。

你们实际到过哪一级？

在那个阶段里，用户真的做过什么任务？

规模、人数、运行时间、部署环境这些如果你知道就讲；不知道也可以明确说不知道。

然后告诉我：哪些东西你绝对不会在面试里说成“已经上线”。

Q6.

历史上客户明确提过“回答质量还需要提高”。

这个反馈当时到底表现成什么？

是没找到材料、找到错材料、跨文档关系没理解、引用不对、模型推理错，还是答案虽然对但不能复核？

你当时有没有亲自参与过其中某个问题的定位和修改？

如果这部分历史没有恢复出来，你会怎么区分：

“当时真实解决过的问题”

和

“我们现在认为应该这样解决的问题”？

Q7.

好，现在我开始看整体设计。

假设公司今天说：

“Zuno 太复杂了，只允许保留三个真正有价值的核心能力。”

你会留哪三个？

为什么是它们？

我不想听数据库、队列、向量库这种基础设施，我想知道：

到底什么东西构成 Zuno 本身，而不是任何 Agent 平台都有的东西？

Q8.

那为什么需要自己维护这么多平台能力？

WorkBuddy、Dify 这类 Host 已经可以提供：

界面、Conversation、模型调用、Workflow、Knowledge、Tool / MCP 和一般 Agent 编排。

如果我让它们负责这些通用能力，只把法律相关能力接到后面，Zuno 还必须自己做什么？

哪些东西你认为一定要自己拥有？

哪些东西如果成熟平台已经做好，你反而不应该再做一遍？

Q9.

再看 Agent Runtime。

LangGraph 本身已经能做图执行、Checkpoint、Interrupt、Resume 这类事情。

所以我想知道：

Zuno 所谓自己的 Runtime，到底是在 LangGraph 上面补什么？

如果最后实验发现：

现成 Agent Host + Zuno 的法律后端

和

Zuno 自己维护完整 Runtime

效果几乎一样，你会不会真的把自己的 Runtime 缩掉甚至删掉？

还是说现在已经有某些理由证明它必须存在？

Q10.

Memory 也一样。

你历史上实际接触过 OpenViking 这一类方案，那么现在重新设计 Zuno 时，为什么 Architecture 里还需要保留自己的 Memory / Context 概念？

哪些能力可以直接使用现成方案？

哪些东西即使换了 OpenViking、换了另一套 Memory Provider，Zuno 自己仍然必须控制？

如果最后发现长期 Memory 对法律任务没有明显收益，你是否接受根本不保留这一层？

Q11.

我现在看到 Part A 里面有：

GraphRAG、Agentic Retrieval、Memory、Planning、并行 Worker、Multi-Agent 候选、Tool Runtime、Microservice 等很多高级能力。

你把它们分成两类告诉我：

哪些是系统成立的基础；

哪些现在其实只是待验证的高级能力。

如果 Benchmark 一直证明不了收益，你最先愿意删哪几个？

反过来说，有没有哪项能力即使模型越来越强，你仍然认为不能交给模型自己解决？

Q12.

好，我们不再按模块聊。

现在给你一个具体任务：

一个律师上传了一批合同、补充协议和历史沟通材料，让系统判断几个争议点，给出证据和依据，生成审查结果；其中某一步可能还要调用外部系统或发出通知。

你从用户点下“开始”以后一直讲到最终结果返回。

不要讲内部类名。

我想听：

系统先做什么，什么时候检索，什么时候需要规划，Memory 在哪里介入，模型负责什么，Tool 在哪里介入，什么时候需要人确认，以及最后什么东西会真正被系统长期保存。

Q13.

沿着刚才这条链路继续。

这里面哪些东西是业务世界里的长期事实，哪些只是这一次 Agent 为了完成任务产生的临时执行状态？

比如系统已经分析出一个正式结论，但是 Agent 自己的执行流程还没有完全结束。

这两类状态为什么不能混在一起？

用户把浏览器关了，甚至服务器重启以后，哪些东西必须还在，哪些东西重新算一次也没关系？

Q14.

再制造一个冲突。

当前合同最新版本写的是 A；

知识库里还有旧版本材料写的是 B；

长期 Memory 里又记着这个用户过去一直按 C 的方式处理。

Agent 这次回答的时候到底应该怎么理解这三个来源？

谁可以影响答案，谁可以改变正式业务事实？

你怎么避免一条过期 Memory 因为“模型觉得它很相关”就把最新材料盖掉？

Q15.

继续刚才那个任务。

假设最后需要调用一个 MCP Tool，把审查结果发送到外部业务系统。

Agent 是在什么条件下才能真的执行这个动作？

模型提出“我要调用工具”以后，谁还需要判断它有没有权限、是否需要审批、参数是否合法？

MCP 在这里到底只是工具接入方式，还是它会替 Zuno 负责这些业务安全判断？

如果明天 MCP Server 换了，你希望 Zuno 哪些责任完全不受影响？

Q16.

任务已经完成，用户也拿到了结论。

第二天又上传了一份新证据，而这份材料可能推翻昨天的一部分判断。

系统怎么知道：

昨天哪些结果可能已经不可信了？

是所有东西全部重新跑一遍，还是应该只重新检查受到影响的部分？

更重要的是，用户第二天回来时，系统怎么避免继续把昨天那个已经过时的结果当成最新结论？

Q17.

现在开始出故障。

同一个复杂任务正在执行：

Graph 检索挂了；

Memory 服务也暂时不可用；

强模型调用还开始超时。

这个时候 Zuno 是整个任务直接失败，还是还能提供一个降级结果？

哪些能力失败以后可以退化成更简单方案继续跑，哪些失败以后你认为必须停止？

如果系统确实降级了，怎么避免用户把“降级结果”误认为和正常结果质量完全一样？

Q18.

再来一个更麻烦的。

Agent 调用外部系统发送了一封审批邮件。

外部系统其实已经执行成功了，但是 Zuno 没收到返回，然后 Runtime 也刚好重启。

恢复以后你不知道邮件到底发没发。

你怎么办？

为什么不能简单把这个 Step 再执行一次？

系统恢复时最应该先相信哪些已经落下来的事实，怎么决定下一步是继续、重试，还是交给人处理？

Q19.

现在两个任务同时处理同一个案件。

任务 A 开始时看到的是旧材料和旧权限；

任务 B 随后上传了新证据，同时管理员又撤销了任务 A 操作者的一部分权限。

任务 A 还在跑。

它最后还能不能提交自己的结果？

系统应该在什么时候发现：

“我开始执行时看到的世界，已经和现在不一样了”

如果两个任务最后得出了互相冲突的结果，谁有资格决定哪个能成为正式状态？

Q20.

最后看规模。

假设明天不是几个 Pilot 用户，而是同时有很多案件、大量文档、很多长任务在运行。

你认为最先扛不住的会是哪几块？

哪些东西确实需要独立扩展，哪些其实一个模块化后端加几个 Worker 就够了？

我尤其想知道：

为什么现在要保留 Microservice 方向，而不是直接冻结成很多服务？

如果今天让你重新做一遍，在保证核心业务价值不丢的前提下，你最想先砍掉哪一层复杂度？为什么？


---

STAGE B — BLUE INITIAL ANSWERS

开始回答前，我重新检查了 main。当前 HEAD 仍然是本 Packet 的 BASE_SHA：b00f5bb3fb0bad9168a1dce96d9e4817a60d9773，没有发生基线漂移。

Q1

回答：

如果严格讲历史，我不能把现在 Part A 的故事倒推成当时最初的需求。

现在能确认的是，这个项目来自智慧法院 / 智慧司法研发背景，属于其中一个产品。项目不是我从零开始做的，我大约 2026 年 3 月加入的时候已经有代码和一个比较简单的自研前端。后来确实做过内部 Demo、客户侧 Demo、法院侧人员测试和 Pilot，而且客户明确提过回答质量还需要提高。

但“最早是谁提出第一版需求”“法院人员原来具体怎么完成这个工作”“最耗时的是哪一步”，目前材料没有恢复出来，我不能为了面试完整去编。

我们现在能重建出一个合理的法律工作链，比如读材料、核对不同陈述、找证据和法律依据、形成结果再人工复核，但这个目前只能叫业务流程候选，不能说“客户当时就是这么提的”。

所以如果面试官问历史，我宁愿把已知和未知说清楚，而不是拿后来的 Target Architecture 补历史故事。

Q2

回答：

这里我也不能给你编一个“历史真实 Bad Case”。

当前历史材料只能证明客户认为回答质量还不够，不能证明当时具体是某个合同争议任务，也没有恢复出一条完整的“简单 RAG 在第几步失败”的真实记录。真实输入材料、法院测试题和具体 Bad Case 都还是未知。

如果讨论现在 Target 为什么值得验证，那简单 RAG 仍然应该是默认基线。比如只问“这份合同的违约责任是什么”，BM25 / 向量检索找到正确条款，再让模型回答，完全可能已经够了。

真正可能需要额外复杂度的是少数跨材料、跨版本、需要持续更新的任务：比如合同正文、补充协议和后续沟通互相影响，需要判断哪个版本有效、多个说法是否冲突、每个结论到底依赖哪些证据；第二天又来新材料以后，还要知道昨天哪些结论失效。

如果 Benchmark 最后证明这些复杂场景并没有明显收益，那 Zuno 就应该退回简单 RAG，而不是为了保留 GraphRAG 或 Agent 概念强行复杂化。这也是当前 Part A 明确写出的 Kill Test。

Q3

回答：

“法律 / 智慧司法”这个业务方向是历史上就存在的，不是后来为了架构故事才加上的；但现在 Part A 里面强调的“高风险法律任务、版本化 Domain State、证据依赖、Finding stale、Human Review”这一整套边界，是后来重新梳理 Target 时进一步收窄和明确出来的。

所以这两件事不能混在一起。

如果把“法律”两个字完全拿掉，大量能力确实会退化成一个普通 Agent + RAG 平台：模型调用、检索、Workflow、Tool、Memory、Checkpoint，本身都不构成 Zuno 的独特性。

还能抽象留下来的，是“有长期业务状态、证据依赖、版本变化、人工决策和受控副作用的高风险任务”这种架构模式。但如果连具体领域都没有，我不会继续声称 Zuno 有明显产品差异，因为那会重新变成一个很宽泛的通用平台故事。

Q4

回答：

我加入的时候项目已经有代码和一个比较简单的自研前端，不是我从零搭建的。历史核心研发规模现在能确认的大约是 7～8 人，有一位学硕学长承担主要技术负责人角色；更细的前后端、算法、测试、部署各有几个人，目前没有可靠记录，我不会现编。

只讲我自己的部分，目前能确认的是：

我参与过部分 Agent 开发；Memory 是加入后比较早的一批工作；参与过 OpenViking 在 Memory / Context 区域的接入；也参与过 Tool Calling Strategy。

LangGraph、GraphRAG 是开发过程中学习和接触过的，但不能因此说完整 LangGraph Runtime 或完整 GraphRAG 是我实现的。数据库我进去查过、调试过，但也不能说数据库是我主责。完整后端、完整 RAG、部署和整体架构都属于团队或后续重构范围，不能算成我的历史个人 Ownership。

至于“我具体改了哪几个文件、遇到哪个 Bug、怎么修的”，历史材料现在还没有恢复到代码级，我不会编。

如果现在让我现场打开代码，我优先挑和已确认经历最接近的三块：Memory / Context、OpenViking 接入、Tool Calling / Agent 调用链。但我会明确说，我现在打开的是当前仓库代码，它不能自动证明每一行都是我当时写的。

Q5

回答：

目前最准确的交付描述是：

内部 Demo → 客户 / 智慧法院项目组 Demo → 后续迭代 → 法院侧真实人员测试 → Pilot Validation。

没有正式 Production 证据。

具体 Pilot 有多少用户、运行多少天、部署在哪台机器、处理多少案件、QPS 和 SLA 是多少，现在都不知道。法院侧真实测试人员到底执行了哪些具体任务、多少道题、有没有标准答案，目前也没有恢复出来。

所以我绝对不会说：

“已经正式上线法院生产系统”；

“已经服务全部 22 家法院”；

“已经达到生产 SLA”；

“当前仓库里的全部组件就是当时客户现场运行的完整技术栈”；

或者“Pilot 就等于正式生产”。

当前仓库自己的 Production Readiness 也仍然是 NOT_ESTABLISHED。

Q6

回答：

这部分现在最大的事实就是：我们知道客户说过回答质量还需要提高，但不知道具体是哪一种质量问题。

目前没有证据让我判断是 Recall 不够、检索错了、跨文档关系错了、引用错了，还是模型推理问题，也没有恢复出正式评分方式和 Bad Case。

我本人是否亲自定位过其中某一个客户 Bad Case、做了什么修改、修改以后指标提高多少，也没有可靠材料支持。

所以面试里我会把两件事拆开：

“客户当时反馈回答质量需要提高”——这是历史事实。

“现在我们认为应该通过 Hybrid Retrieval、证据引用、冲突检测、版本化结果、Eval 等方式解决”——这是后来架构重构形成的 Target 方案。

我不会说“因为客户当时出现了跨文档冲突问题，所以我做了 GraphRAG”，除非以后能找到真实任务、提交或者测试证据。

Q7

回答：

如果只能保留三个，我不会留 GraphRAG、Memory 或 Multi-Agent 这些名字。

第一，我会留证据和结论之间可追溯的关系。不是只返回一段看起来相关的文本，而是知道一个结论到底被哪些材料、哪些版本支撑，证据够不够。

第二，我会留长期、版本化的法律业务结果。昨天形成的判断不能永远是“聊天记录里的一段答案”；新材料进来以后，要知道哪些旧判断受影响、哪些需要重新复核。

第三，我会留高风险动作和正式结果的控制边界。模型可以提出建议，但不能自己决定权限、自己批准副作用、自己把一个候选结论写成正式业务事实。

这三个留下以后，UI、Agent Host、模型网关、Memory Provider、Graph Provider、工作流框架都可以替换。

如果这三个最后也证明不了实际价值，那我认为 Zuno 就没有必要维持今天这套 Target 差异化。

Q8

回答：

我不认为 Zuno 必须自己维护一整套通用 Agent 平台。

以 Dify 为例，它当前官方能力已经覆盖 Workflow、Knowledge Retrieval、Agent 节点、Tool，并且已经支持原生双向 MCP：既可以调用 MCP Server，也可以把 Workflow / Agent 暴露成 MCP Server。

所以如果成熟 Host 能解决 Conversation、UI、模型接入、普通 Workflow、Knowledge 管理和 Tool 接入，我倾向于直接复用。

Zuno 真正需要自己拥有的是和法律业务正确性绑定的那部分，例如：

哪些材料和版本构成当前案件状态；

一个候选结论在什么证据条件下才能成为正式结果；

结论依赖哪些证据，新材料来了以后哪些结果需要 stale；

谁有权确认或修改正式业务结果；

高风险动作的业务审批和审计规则。

至于 UI、普通聊天历史、模型 SDK 封装、通用 Workflow、MCP 协议实现、通用向量检索，成熟方案够用就不应该重复建设。

当前 Part A 本身也已经把 Generic Host + Zuno Legal Backend 作为正式比较方案，而不是默认 Native Runtime 一定存在。

Q9

回答：

LangGraph 已经解决了很多我不应该重复实现的 Runtime 基础能力。

它现在官方就有 Checkpoint Persistence、Interrupt、Resume 和故障恢复能力；持久化 Checkpoint 可以在失败以后从成功步骤恢复，Interrupt 也能保存状态以后继续执行。

所以如果 Zuno 保留 Runtime，它真正应该增加的不是“我也实现一个图执行器”，而是业务层控制：

这次任务基于哪个业务版本执行；

什么时候允许规划和并行；

预算和权限有没有变化；

模型产生的结果什么时候只能算候选；

什么时候允许提交正式业务状态；

副作用 unknown outcome 时怎么和外部事实对账。

LangGraph 是执行框架，Zuno 如果有 Runtime，价值应该在这些领域约束和控制策略，而不是重新造 Checkpoint。

而且目前没有证据证明 Native Runtime 一定必须存在。Part A 的 A/B/C Kill Test 已经明确：如果 Generic Host + Legal Backend 和 Zuno Native Runtime 效果基本相同，就应该缩掉 Native Runtime。

我接受真正删掉它。

Q10

回答：

我会先区分“Memory 这项能力”和“自己造一个 Memory 数据库”。

OpenViking 现在本身已经能统一管理 Resource、Memory 和 Skill，也有 Session、长期 Memory 抽取和上下文组织能力，所以这些通用能力完全可以作为 Provider 复用。

Zuno 真正需要控制的不是底层怎么存 Memory，而是：

什么信息允许进入当前任务；

Memory 属于谁、作用范围是什么；

过期或者撤销以后还能不能继续使用；

最关键的是，Memory 永远不能冒充正式法律事实。

例如 OpenViking 记住了某个用户过去习惯按某种方式处理案件，这可以帮助组装上下文，但不能覆盖最新合同版本，也不能直接修改正式 Finding。

所以我愿意把 OpenViking 或其他方案放在 Provider 层。

而如果实验最后证明长期 Memory 对法律任务几乎没有收益，我也接受直接删除长期 Memory，只保留当前任务上下文和必要的业务状态。当前 Architecture 已经把 Memory 标成 PROPOSED / DEFERRED，并明确写了不值得就删除的反转条件。

Q11

回答：

我会把基础和高级能力切得比较狠。

系统真正成立的基础，我认为是：

最基本的可靠检索和引用；

明确的业务状态和版本；

权限、审批和人工复核；

一次任务最小可恢复的执行控制；

以及模型只能产生 Proposal，不能自己把结果变成正式事实。

剩下很多现在都属于高级能力或者待验证能力：

GraphRAG、Agentic Retrieval、长期 Memory、复杂动态 Planning、大规模并行 Worker、Persistent Multi-Agent、完整 Native Runtime、提前拆很多 Microservice。

其中我最先愿意删的是 Persistent Multi-Agent、无条件 GraphRAG 和没有收益证明的长期 Memory；物理服务也不会为了“微服务架构”提前拆。

即使模型再强，我也不会把权限判断、人工审批、不可逆副作用控制、正式业务状态提交、幂等和恢复对账完全交给模型。模型可以建议，但这些需要确定性的系统约束，因为一次“模型大概率判断正确”不能替代权限和业务一致性。

Q12

回答：

我会这样跑。

用户上传合同、补充协议和沟通材料以后，第一步不是让 Agent 马上回答，而是先把文档身份、版本和访问范围确认下来，完成解析和基础索引。

用户点开始以后，系统先理解这次任务到底要判断哪些争议点。简单问题可以直接进入检索；如果有多个争议点、互相依赖或者需要外部动作，再形成一个有限的执行计划，不需要为了所有问题都生成复杂 DAG。

然后针对每个争议点检索证据。基础路径还是关键词和向量检索，只有关系型、多跳问题确实需要时才考虑 Graph。

Memory 如果存在，是在组装上下文时介入：比如用户偏好、之前工作上下文，但它只是辅助。当前合同、正式案件状态和证据版本优先从业务数据读取。

模型负责理解材料、提出争议点、形成事实或结论候选、判断还缺什么信息；它不直接提交正式结果。

如果中间需要调用 Tool，模型只能提出“我要执行这个动作”。系统再检查权限、参数、风险和审批；高风险操作需要人工确认。

最后，在证据、版本、权限和必要的人审都满足以后，系统才提交一个新的正式审查结果版本，并把证据引用、人工决定一起保存。

长期真正需要保存的是：原始材料和版本、有效证据、正式业务结果及其版本、依赖关系、人工决定、必要的 Tool 执行结果和审计记录。

这次 Agent 临时怎么思考、用了哪条执行分支，不应该自动变成长期业务事实。这个正是当前 Part A 把 Knowledge、Legal Intelligence、Domain State、Memory 和 Runtime 分开的原因。

Q13

回答：

我会把“这个案件现在被系统承认的事实”与“Agent 为了干完这次任务走到了哪一步”分开。

长期业务状态包括：文档版本、证据、确认后的事实和冲突、正式审查结论、人工决定和最后交付结果。

临时执行状态包括：这次 Run、计划走到哪一步、哪个检索分支完成了、模型调用是否重试、剩余预算是多少。

两者不能混，因为它们的生命周期完全不同。

比如正式结论已经成功提交，但 Runtime 在写最后一个 Checkpoint 前宕机。如果恢复以后只相信 Checkpoint，很可能把已经提交成功的业务操作重新做一次。

所以服务器重启后，正式业务状态必须还在；有价值的长任务 Checkpoint 也应该能恢复。但一些没有副作用、成本又很低的临时计算结果重新算一次并没有问题。

当前 Target 也明确把 PostgreSQL 的 Canonical Business / Domain State 与 LangGraph Checkpoint 的执行控制状态分开。

Q14

回答：

我不会给这三个来源设置一个简单的“Memory > Knowledge”或者“Knowledge > Memory”固定优先级，而是先看它们是什么。

最新合同 A 是当前业务材料，所以讨论“合同现在写了什么”时，以 A 为准。

旧版本 B 不能删除，它仍然可以解释历史变化，也可能是争议证据，但不能假装自己还是当前版本。

Memory 里的 C 是“这个用户过去通常怎么处理”，它可以影响建议方式或者提醒 Agent 去检查某些事情，但不能改变合同事实。

模型组装上下文时应该知道每条信息的来源、版本和状态。发现 B 和 A 不一样，可以告诉用户合同发生过变化；发现 C 和 A 冲突，应该降低或丢弃 Memory 的影响，而不是让模型自己觉得 C 更相关就覆盖 A。

真正能改变正式业务状态的是受规则约束的 Domain Owner，必要时还需要人复核。模型、Retrieval 和 Memory 都只能提供候选信息。

Q15

回答：

模型提出 Tool Call 后，不代表 Tool 就可以执行。

我至少还要检查：

当前用户和工作区有没有权限；

这次权限有没有在等待期间被撤销；

参数是不是符合 Tool Schema 和业务限制；

这个动作有没有不可逆副作用；

是否需要人工审批；

以及有没有幂等标识，防止恢复以后重复执行。

MCP 在这里首先是工具能力发现和调用的协议边界，不应该替 Zuno 决定“这个案件的这个用户是否允许发送这份结果”。

MCP 自己确实有传输层授权机制，而且最新规范仍在继续强化授权；但 MCP 官方的授权范围解决的是 Client / Server 之间如何授权访问，业务系统自己的审批、案件权限和副作用规则并不会因此自动消失。

所以明天换一个 MCP Server，我希望 Zuno 的业务权限、风险分级、审批、参数校验、幂等、审计和结果对账原则都不变。

变化的只是“怎么连接这个 Tool、它现在暴露什么能力和参数”。

Q16

回答：

如果昨天的正式结果保存了“它依赖哪些证据和材料版本”，那第二天新证据进来以后，不需要默认把整个案件所有东西重新跑一遍。

系统先看这份新证据影响了哪些事实、冲突或者结论依赖。

能确定影响范围，就把对应结果标记为 stale 或 review required，只重新检查受影响部分。

如果依赖关系不完整，或者新材料影响范围很大，那宁愿扩大重算范围，甚至整个任务重新评估，也不能假装能够精确增量更新。

最重要的一点是：昨天的结果不能静默继续当“当前结果”。

用户第二天回来看到它时，要么看到新的有效版本，要么明确看到“这个结果因为新证据已经需要重新评估”。

旧结果还应该保存，因为要能解释昨天为什么会得出那个结论，但它已经不是当前最新可信结论。

这就是当前 Target 的 Version + Dependency + Staleness 设计要解决的问题。

Q17

回答：

这三个故障我不会一刀切。

Graph 检索挂了，如果当前问题用 BM25 + Vector 仍然能够找到足够证据，就降级到 Hybrid Retrieval。

Memory 挂了，我更倾向于直接没有 Memory 继续，因为 Memory 本来就不能拥有正式法律事实；最多损失个性化和历史上下文。

强模型超时，可以在预算和任务要求允许时重试或者切换 Provider；如果弱模型只能做抽取、改写这类任务，可以继续。但如果现在正处于一个关键法律结论的最终质量 Gate，我不会为了“任务必须成功”随便换一个能力明显不足的模型然后假装结果等价。

真正必须停止的情况是：关键证据不足、权限无法确认、高风险副作用状态不清楚、或者降级以后已经无法满足这个任务要求。

而且降级必须成为结果的一部分。

比如明确告诉用户：Graph 能力不可用，本次结果只基于基础检索；或者某项高级验证没有完成，结果需要人工复核。

否则“还能返回答案”反而会制造最危险的假成功。

Q18

回答：

这种情况绝对不能直接把 Step 再执行一次，因为真实世界里的邮件可能已经发出去了。

恢复以后我第一件事不是看 Agent 觉得自己执行到哪，而是对账。

先检查 Zuno 有没有保存这次外部操作的唯一标识、调用记录和 Effect Receipt；如果外部系统支持根据 Operation ID 或幂等 Key 查询，就向外部系统确认。

如果确认已经成功，就补齐本地状态，不能再发。

如果确认没有执行，再在重新校验权限以后重试。

如果外部系统本身无法告诉我到底有没有执行，我会把它标成 unknown outcome，进入人工确认，而不是赌博式重试。

恢复时应该优先相信已经提交的 Domain State、外部系统已经发生的 Effect、以及持久化 Receipt，再和 Runtime Checkpoint 对账。

LangGraph 自己的 Interrupt 文档也特别提醒，恢复时节点可能从头重新执行，因此 Interrupt 之前发生的副作用必须做到幂等；这也是为什么 Workflow Checkpoint 本身不能证明外部副作用有没有发生。

Q19

回答：

任务 A 可以继续做纯计算，但它不能拿着启动时的旧权限和旧案件版本，最后无条件提交结果。

我会在两个重要位置重新确认世界有没有变化。

第一是发生副作用之前重新鉴权。

第二是正式业务结果提交之前检查当前案件版本和权限版本。

如果 A 是基于 Version 10 开始的，提交时案件已经到 Version 11，它就不能假装自己的判断仍然基于最新世界。根据变化范围，可以重新读取、Replan，或者进入人工复核。

同样，管理员已经撤销权限以后，即使 A 启动时有权限，也不能因为任务跑了十分钟就继续使用旧授权提交高风险结果。

如果 A 和 B 得出冲突结论，两边首先都只是 Proposal。

谁先执行完不是决定正式事实的依据。

最终由拥有业务状态提交权的 Domain Owner 根据当前版本、证据、权限和 Review 决定哪个结果可以进入正式状态，必要时让人处理冲突。当前 Target 的 Owner 边界就是为了避免 Runtime 自己变成“谁最后写数据库谁就赢”。

Q20

回答：

如果规模突然上来，我预计最先有压力的不是普通 CRUD，而是三类重任务：

文档解析、OCR、Embedding、索引和 Graph 构建；

大量长时间模型 / Agent 任务；

以及需要隔离的 Tool / Sandbox 或离线 Eval。

这些很适合先拆成独立 Worker，因为它们有不同的 CPU、GPU、I/O 和任务时长。

但这并不等于我要立刻拆十几个 Microservice。

平台 CRUD、领域状态、很多同步 API 完全可以先放在一个边界清楚的模块化 Python Backend 里。只有某一块真的需要独立扩缩容、故障隔离、安全隔离或者独立部署生命周期，才把它变成物理服务。

所以我理解 Part A 的 “Microservice Direction” 是保留拆分能力，而不是现在冻结服务数量。当前文档甚至明确要求每次拆服务都回答：为什么不是 Library？为什么不是 Worker？

如果今天重新做一遍，我最先砍的就是过早的物理服务拆分。

因为它不会增加法律业务价值，却会立刻引入网络故障、重试、Schema 兼容、分布式 Trace 和本地开发成本。

我会从模块化后端 + 必要 Worker 开始，再让真实负载和安全边界决定是否拆服务。

GraphRAG、长期 Memory、Native Runtime 这类复杂度也都继续接受各自的 Kill Test，但在整体工程结构上，我首先不会把系统做成“为了微服务而微服务”。

无法确认的项目事实

1. 历史项目第一版需求由谁提出、原人工 SOP 和最初最痛的业务步骤，目前无法确认。

2. 尚未恢复一条可以公开讲述的真实业务任务，以及“简单 RAG 在哪一步失败”的历史 Bad Case。

3. “回答质量还需要提高”的具体根因、修复方式和 Cause → Fix → Metric 没有恢复。

4. 用户个人历史贡献目前只能确认到 Agent、Memory、OpenViking Memory / Context 接入和 Tool Calling Strategy，具体文件、Commit、Bug 和测试尚未恢复。

5. Pilot 的具体用户数量、任务量、部署位置、运行时间、SLA、真实测试题和完整历史技术栈无法确认。

我认为 Red 最可能继续追问

1. Q1 / Q2 / Q6 的真实性缺口：既然没有恢复真实业务任务和 Bad Case，现在的 Target Complexity 到底有多少是业务驱动，有多少仍只是合理假设。

2. Q4 的个人 Ownership：如果代码级任务、Commit 和 Bug 还没恢复，简历上的平台设计、检索、评测等较宽表述应该如何收窄。

3. Q7～Q10 的 Build / Buy 边界：如果 Generic Host、LangGraph、OpenViking 已经覆盖大量通用能力，Legal Backend 是否才是 Zuno 真正应该保留的最小产品边界。


---

STAGE C — RED REVIEW / COUNTER

Q1

Blue 回答判断：

事实不足，但没有回避核心。

理由：

Blue 没有用 Target 反写历史，这一点是对的，而且明确承认“第一版需求是谁提出、原来人工怎么做、最痛步骤是什么”都没有恢复出来。

但从真实面试角度，这仍然是当前项目故事最大的空洞。

一个高级面试官问“为什么有这个项目”，最终想听到的是：

谁在工作； 原来怎么工作； 哪里痛； 为什么值得做系统。

现在 Blue 只能证明“这是智慧司法背景下的项目，而且做到了 Pilot”，还不能证明今天 Part A 描述的那类复杂法律工作就是项目最初真正被要求解决的问题。

继续追问：

1. 所以如果我现在追问“法院人员不用 Zuno 的时候具体怎么完成这项工作”，你的答案就是目前不知道，对吗？

2. 在缺少这个事实的情况下，你凭什么判断现在 Target 选择的“跨版本、证据依赖、长期法律状态”是在解决真实痛点，而不是一个技术上合理但尚未验证的假设？

Q2

Blue 回答判断：

部分回答，真实性证据不足。

理由：

作为 Target 设计，Blue 给出的边界是合理的：

简单单文档问题默认走简单 RAG；

只有跨材料、跨版本、需要持续更新的任务才值得增加复杂度；

并且接受 Benchmark 失败后删除这些复杂能力。

问题在于，这个回答目前证明的是：

“这种系统为什么在理论上可能值得做。”

还没有证明：

“Zuno 历史项目为什么确实需要这么做。”

尤其没有一条真实任务能把：

Simple RAG → 失败点 → 增加某项能力 → 实际改善

连起来。

继续追问：

1. 如果现在没有历史 Bad Case，那你准备拿什么类型的真实任务作为第一批验证样本，才能证明这不是自己给自己设计需求？

2. 如果 Simple RAG 在这些复杂任务上只比 Zuno 差一点点，但成本低很多，你会怎么判断这些额外复杂度还值不值得存在？

Q3

Blue 回答判断：

回答充分。

理由：

Blue 清楚地区分了两件事：

法律 / 智慧司法背景是历史事实；

高风险法律任务、版本化业务状态、证据依赖、结果过期和人工复核，是后来收窄形成的 Target。

也明确承认：

如果去掉法律领域，大量能力就只是普通 Agent + RAG 的通用能力。

这避免了把“Agent、Memory、Tool、Workflow 都有”包装成产品差异。

这里唯一需要 Main 后续关注的是：

“可推广到其他高风险领域”目前只能作为架构抽象，不能反过来扩大 Zuno 的产品故事。

继续追问：

关闭。

Q4

Blue 回答判断：

事实不足，而且是面试真实性的高风险缺口。

理由：

Blue 对 Ownership 的边界非常克制：

Agent、Memory、OpenViking、Tool Calling Strategy 可以确认；

完整 Runtime、完整 GraphRAG、完整后端、部署、整体架构不能归到个人。

这个边界本身是可信的。

但问题没有真正解决：

“你实际接到什么任务、改了什么逻辑、遇到什么 Bug、怎么验证。”

这些正是高级面试官判断项目是否真正做过的关键证据。

现在回答到“我愿意打开哪几块当前代码”还不够，因为当前代码不能证明历史贡献。

继续追问：

1. 如果面试官现在不接受“我参与过 Memory”，而是继续问“你当时具体改了什么，输入输出是什么，出过什么 Bug”，你目前是不是只能承认这部分历史还没恢复？

2. 在代码级 Ownership 恢复之前，你如何避免简历里的“设计平台、检索、评测、安全恢复”等宽表述让面试官误以为这些都是你历史上亲自主责？

Q5

Blue 回答判断：

回答充分。

理由：

交付阶段分得很清楚：

Internal Demo → Customer Demo → Court-side Testing → Pilot Validation → Production = NO。

同时主动拒绝使用用户数、SLA、法院数量、生产环境等未经证实的信息。

这已经足够回答本轮的“Demo / Pilot / Production 是否混淆”问题。

继续追问：

关闭。

Q6

Blue 回答判断：

事实不足，但回答方式正确。

理由：

Blue 没有把“客户认为质量需要提升”擅自解释成 Recall、Graph、多跳、Citation 或模型推理问题，也没有把今天的架构方案反写成当年的 Cause → Fix。

这符合真实性要求。

但它同时意味着：

目前没有一条历史质量问题能够直接支撑 GraphRAG、证据依赖、冲突检测或其他复杂能力的引入。

这是事实缺口，不应该通过继续架构推理补出来。

继续追问：

关闭事实追问。

该缺口保留到本轮 Findings，等待未来真实材料，而不是让 Blue 猜。

Q7

Blue 回答判断：

部分回答，核心产品边界开始成形，但仍缺验证。

理由：

Blue 没有选 GraphRAG、Memory、Multi-Agent 这些技术名词，而是选了：

证据与结论可追溯；

长期版本化业务结果；

高风险动作与正式结果的控制边界。

这比“我们有 11 个模块”强很多，也已经开始形成真正的产品 Kernel。

但第三项仍然包含两个不同场景：

一类是正式法律结论如何提交；

另一类是发邮件、调用外部系统这类副作用。

如果 Zuno 只做法律研究和知识问答，没有任何外部副作用，这个产品是否仍然成立，需要继续讲清楚。

另外，这三个核心价值现在仍主要来自 Target 推理，还没有完成用户或 Benchmark 验证。

继续追问：

1. 如果把所有外部 Tool 和副作用全部删掉，只做法律知识研究和审查，Zuno 的最小核心还剩什么？

2. 这三个里面哪一个如果 Benchmark 证明没有收益，会真正改变你对 Zuno 产品边界的判断，而不只是删一个 Provider？

Q8

Blue 回答判断：

部分回答，Build / Buy 原则成立，但证据还不够。

理由：

Blue 已经明确：

通用 Host 能做的就复用；

Zuno 只保留和法律业务正确性绑定的能力。

这个方向是清楚的。

但“某个平台功能列表里有 Workflow、Knowledge、MCP”只能证明它提供了这些表面能力，不能证明它在 Zuno 需要的版本、权限、恢复、数据边界和部署方式下真的可以替代 Native Host。

换句话说：

Build / Buy 不能只做 Feature Checklist。

真正需要的是：

把一条 Zuno 任务放进去，看 Host 的扩展点是否足够。

继续追问：

1. 现在有没有一条具体能力，是你已经能证明 Generic Host 很难通过插件或外部 Backend 实现，所以必须由 Zuno 自己控制的？

2. 如果还没有，那是不是应该承认“Legal Backend 可能已经足够”目前比“完整 Zuno Platform 必须存在”更有证据？

Q9

Blue 回答判断：

回答充分，但 Native Runtime 的必要性仍未建立。

理由：

Blue 没有把 LangGraph 已有的持久执行能力包装成 Zuno 自研。

它把可能的 Zuno Runtime 价值限定在：

业务版本；

预算与权限；

正式状态提交；

副作用对账；

领域约束。

同时明确接受：

如果 Host + Legal Backend 足够，就删除 Native Runtime。

这是一个可反转的架构回答。

现在的问题已经不再是“设计有没有讲清楚”，而是：

这个 Runtime 是否真的比外部 Host 提供额外价值。

这是 Measurement 问题。

继续追问：

关闭设计追问。

保留 Measurement Concern。

Q10

Blue 回答判断：

回答充分。

理由：

Blue 正确地区分了：

“Zuno 需要 Memory 这个概念边界”

和

“Zuno 要自己造一套 Memory 存储系统”。

同时把 Memory 限制为上下文来源，而不是正式法律事实，并接受 OpenViking 或其他 Provider 替换以及长期 Memory 整层删除。

这已经回答了本轮整体 Architecture 层面的 Build / Buy 问题。

继续追问：

关闭。

Q11

Blue 回答判断：

部分回答。

理由：

Blue 已经主动把：

GraphRAG；

Agentic Retrieval；

长期 Memory；

复杂动态 Planning；

Persistent Multi-Agent；

过早 Microservice

降为可删除复杂度。

同时坚持：

权限、审批、不可逆副作用、正式业务状态提交和恢复对账不能直接交给模型。

这个取舍基本成立。

但这里还有一个概念需要继续压：

“一次任务最小可恢复的执行控制”到底是不是 Zuno 的产品能力。

如果 Generic Host 已经提供足够的恢复，这一项也可能只是被复用的基础设施，而不是 Zuno Kernel。

继续追问：

1. 你这里说“最小可恢复执行控制”是基础，那它是 Zuno 自己必须实现的能力，还是只要底层 Host 能提供这个保证就够了？

2. 除了权限和正式业务提交之外，还有没有哪项所谓“基础能力”其实也应该继续接受 Build / Buy，而不是默认归 Zuno？

Q12

Blue 回答判断：

部分回答，主链路已经讲通，但入口处还有关键缺口。

理由：

这是本轮比较重要的正向结果。

Blue 已经能用普通工程语言把：

上传材料 → 确认版本和权限 → 理解任务 → 简单任务直接检索 / 复杂任务有限规划 → 检索证据 → 可选 Memory → 模型提出候选 → Tool 受控执行 → 人审 → 正式结果提交

连成一条线。

这说明 Part A 的核心责任边界已经基本可以映射到真实执行流程。

但有一个非常现实的问题没有回答：

文档上传成功，不等于解析、Embedding、索引、Graph Projection 都已经准备好。

如果用户在知识索引只完成一半时立即点“开始”，当前回答没有说明系统到底等、拒绝、部分检索还是带风险继续。

继续追问：

1. 用户刚上传 100 份材料，40 份已经索引，60 份还在处理，这时候他立刻点击“开始审查”，你是让任务跑、让它等，还是明确拒绝？为什么？

2. 如果你允许部分数据运行，最后结果怎么知道自己不是在一个“不完整知识视图”上得到的？

Q13

Blue 回答判断：

回答充分。

理由：

Blue 清楚地区分了：

长期业务状态；

Agent 临时执行状态。

并且用一个非常好的故障例子说明为什么二者不能混：

业务结果已经提交，但最后 Checkpoint 还没写成功。

这已经足以说明：

Checkpoint 不能等价于业务事实；

恢复不能只重放 Runtime。

继续追问：

关闭。

Q14

Blue 回答判断：

部分回答，来源边界清楚，但法律业务冲突仍被简化了。

理由：

Blue 成功说明了：

当前材料、旧版本材料、Memory 是不同类型的信息；

Memory 不能覆盖正式材料；

旧版本可以保留用于历史解释；

模型不能直接修改正式状态。

但是：

“最新版本就是当前事实”在真实法律场景里仍然可能过于简单。

补充协议、附件、不同生效时间、不同主体材料可能同时有效。

真正的困难并不总是：

A 新、B 旧，所以 A 赢。

也可能是：

A、B 同时有效，但适用范围不同。

这说明版本治理和法律适用判断之间还需要保持清晰边界。

继续追问：

1. 如果 A 和 B 不是简单的新旧替代，而是两份都有效、但适用于不同时间或不同事项，系统靠什么避免“版本新就覆盖版本旧”的错误？

2. 这种冲突到底属于 Knowledge 找材料的问题，还是属于法律业务判断的问题？

Q15

Blue 回答判断：

部分回答，安全责任边界清楚，但版本变化链路还没完整回答。

理由：

Blue 已经明确：

模型只能提出 Tool Call；

业务权限、审批、参数限制、副作用控制和审计不能交给 MCP；

换 MCP Server 也不应该改变这些规则。

这一层职责边界是清楚的。

但题目里的“明天 MCP Server 换了”还有一个工程问题：

如果 Server 本身升级，Tool 名称、参数或者语义发生变化，Zuno 在什么时候发现？

尤其是一个长任务已经运行一半，Plan 还是按旧工具能力生成的，这时不能只说“Adapter 变化”。

继续追问：

1. 一个任务已经运行十分钟，MCP Server 在中途升级，原来的 Tool 参数已经不兼容，你希望系统什么时候发现这件事？

2. 这种情况下你认为应该重试当前调用，重新规划剩余任务，还是直接停止？你用什么信息区分？

Q16

Blue 回答判断：

回答充分。

理由：

Blue 已经把新证据后的处理讲成：

依赖定位 → 标记受影响结果 → 有把握则局部重评 → 依赖不完整则扩大范围 → 旧版本保留但不能继续冒充 Current。

这既避免了“全部重跑”的粗暴方案，也没有假设系统永远能精确增量更新。

整体 Architecture 层已经足够。

继续追问：

关闭。

Q17

Blue 回答判断：

部分回答，降级方向正确，但“降级后还能不能算正式结果”仍不清楚。

理由：

Blue 能够分别处理：

Graph → Hybrid；

Memory → 无 Memory；

强模型 → Retry / Provider fallback。

也明确指出：

关键证据不足、权限不清、副作用状态不明时必须停止。

问题在于：

“告诉用户这次 Graph 不可用”还不等于解决质量语义。

对高风险任务来说，系统还需要回答：

这次降级结果究竟仍然满足任务要求；

还是只能作为草稿；

还是必须人工 Review 后才能交付。

否则 UI 上写一句“能力降级”仍可能让用户把结果当正式结论。

继续追问：

1. 谁决定一次降级后的结果仍然满足这个任务的最低质量要求？

2. 如果正常模式允许直接形成正式结果，但降级模式只能返回草稿或强制人审，这个差异应该在哪个环节被控制？

Q18

Blue 回答判断：

回答充分。

理由：

这是本轮最完整的一条故障回答之一。

Blue 没有把 Timeout 当失败，也没有盲目 Retry，而是先确认真实世界是否已经发生副作用：

能查成功 → 补本地状态；

确认未执行 → 重新鉴权后重试；

无法确认 → unknown outcome + 人工处理。

同时明确：

Runtime Checkpoint 不能覆盖外部事实。

整体恢复思想已经成立。

继续追问：

关闭。

Q19

Blue 回答判断：

部分回答，并发提交边界清楚，但权限撤销的传播还不够。

理由：

Blue 已经说明：

启动时权限不是永久授权；

副作用前和正式提交前必须重新检查；

旧案件版本不能无条件提交；

两个 Agent 谁先跑完不能决定正式事实。

这些都是正确的总体边界。

但这里还有一个更细、同时仍然属于总体架构的问题：

任务 A 被撤销权限以后，它不只是“不能提交”。

如果它后面还要继续读取受保护材料、再次检索、调用模型处理敏感内容，是否还能继续？

回答里“可以继续做纯计算”需要一个更严格的前提：

这些计算不能继续获得已经被撤销的受保护输入。

继续追问：

1. 权限被撤销以后，如果任务 A 下一步还需要重新读取案件材料，它还能继续吗？

2. 你只在副作用和最终提交前重新鉴权够不够，还是长任务运行过程中所有新的受保护访问都必须以当前权限为准？

Q20

Blue 回答判断：

部分回答，并暴露了一个明显的 Architecture Concern。

理由：

Blue 对扩展顺序的判断很清楚：

先识别 OCR、Embedding、索引、长 Agent Run、Sandbox、Eval 等真正的重任务；

优先独立 Worker；

普通 CRUD 和领域事务先保持模块化 Backend；

只有出现扩缩容、故障、安全或部署生命周期证据后才拆服务。

这个回答本身非常合理。

但它和当前 Part A 中：

Microservice Direction = ACCEPTED_TARGET

之间存在值得 Main 关注的张力。

因为 Blue 自己的答案实际上是：

“目前并没有证据支持必须走 Microservice，只应该保留未来按证据拆分的能力。”

如果这是事实，那么“Microservice Direction”到底是在表达：

一个已经接受的技术方向；

还是一个未来满足条件才启用的部署选项？

目前语言可能比证据更强。

这里存在 Architecture Concern，但 Red 不决定正式架构如何修改。

继续追问：

1. 如果今天没有真实负载、HA、安全隔离或独立部署生命周期证据，为什么 Microservice 还应该被称为已经接受的 Direction，而不是一个保留的部署选项？

2. 什么具体证据出现以后，你才会第一次把某个 Worker / Library 真正拆成独立 Service？

RED ROUND FINDINGS

[STORY] [FACT]

Zuno 的历史产品起点仍未真正恢复。

目前能证明智慧司法背景、Demo、法院侧测试和 Pilot，但仍不能回答“谁最早遇到什么问题、原人工 SOP 怎么做、第一版需求是什么”。因此，当前 Part A 的 Target Product Thesis 不能被反写成历史立项原因。

[STORY] [FACT]

个人 Ownership 仍停留在能力级，而不是工程任务级。

Agent、Memory、OpenViking Memory / Context、Tool Calling Strategy 的参与可以确认，但“接到什么任务 → 改什么逻辑 → 遇到什么 Bug → 如何验证”仍缺事实。对真实面试而言，这比架构术语掌握更容易成为真实性风险。

[ARCHITECTURE] [MEASUREMENT]

Legal Backend 目前比 Native Agent Platform 更接近已讲清楚的最小产品边界。

Blue 已多次接受 UI、通用 Workflow、MCP、Memory Provider、Graph Provider、LangGraph Runtime 等能力外部化，并接受 Native Runtime Kill Test。当前仍没有测量证明完整 Native Runtime 比 Generic Host + Legal Backend 有额外价值。

[ARCHITECTURE] [MEASUREMENT]

GraphRAG、长期 Memory、复杂 Planning、Persistent Multi-Agent 和部分 Runtime 能力已经被正确降为可删除复杂度，但核心差异化本身同样尚未被真实业务 Benchmark 证明。

本轮已经能讲出“证据可追溯 + 长期版本化业务结果 + 正式结果/副作用受控”这一产品 Kernel，但它目前主要是 Target Hypothesis，不是已证实的业务收益。

[CHAIN]

端到端主链路已经基本讲通，但 Knowledge Readiness / Index Freshness 仍是明显缺口。

当前回答默认“上传后完成解析和索引再开始”，没有说明大批材料部分解析、部分索引、Projection 延迟时，一个 Run 是否允许开始，以及如何避免在不完整知识视图上形成正式结果。

[CHAIN]

降级策略有方向，但缺少“降级结果是否仍有资格成为正式结果”的统一语义。

Graph、Memory、Model 都可以有不同程度降级，但仅向用户展示 Warning 不足以证明高风险任务仍满足最低要求。Draft、Review Required、正式结果之间的边界仍需进一步讲清楚。

[CHAIN]

长任务中的动态权限变化还没有完全闭合。

Blue 已覆盖副作用前和正式提交前重新鉴权，但撤权以后任务是否还能继续读取受保护材料、重新检索和向模型暴露内容仍需明确。权限不能只控制“最后能不能写”，还关系到运行过程能不能继续访问。

[ARCHITECTURE]

“Microservice Direction 已接受”与 Blue 的 Worker-first / Evidence-driven 拆分回答存在张力。

Blue 明确认为当前首先应该是模块化 Backend + 必要 Worker，并由真实扩缩容、故障、安全和部署生命周期证据决定是否拆 Service。这里存在 Architecture Concern：当前 Target 语言是否比实际证据更强，需要 Blue Reflection 和 Main Coordinator 判断。


---

STAGE D — BLUE ARCHITECTURE REFLECTION

开始 Reflection 前重新检查了 main。当前 HEAD 仍然是本轮 BASE_SHA：b00f5bb3fb0bad9168a1dce96d9e4817a60d9773，没有发生基线漂移。

本轮 Reflection 另外复核了当前 Canonical Architecture 和相关 ADR。一个重要发现是：当前总体 Architecture 一方面明确写着默认可以从“模块化 Python 服务 + 独立 Worker”开始、物理拆分需要 Scaling / Failure / Security / Lifecycle 等理由；另一方面 Target Status 又把 Microservice Direction 标成 ACCEPTED_TARGET。

更重要的是，两份当前有效 ADR 的语义也存在明显张力：ADR-0008 明确写着默认最小形态是 Generic Host + Legal Backend，并写明 Deployment 应“模块化单体 + 独立 worker 优先”；ADR-0010 则把 Microservice Architecture 固定为 accepted-target，并提出五个 network-facing service 候选。

这使 Q20 不只是 Blue 表达问题，而是真正值得 Main Coordinator 处理的架构治理问题。

BLUE COUNTER ANSWERS

Q1 Counter Answer

1. 对。如果现在继续问“法院人员不用 Zuno 时具体怎么完成这项工作”，目前最准确的答案就是：不知道，历史事实尚未恢复。

我能说智慧司法背景、法院侧测试、Pilot 和质量反馈，但不能补出原来的人工 SOP。

2. 因此我现在也不应该说“已经判断跨版本、证据依赖、长期业务状态就是历史真实痛点”。

更准确的是：这些是现在的 Target Hypothesis。

当前 Architecture 本身已经把 Product Thesis 写成一个可证伪的问题，并且明确如果 Benchmark 证明不了收益，对应自研复杂度就应该删除。

所以这里不是“凭什么相信它一定正确”，而是：

先根据法律场景提出一个候选问题模型；

再用真实任务、真实用户反馈和 Benchmark 证明；

证明不了就收缩。

不能用架构设计替代尚未恢复的历史事实。

Q2 Counter Answer

1. 第一批验证样本不能主要由我们自己凭想象生成。

优先级应该是：

首先恢复法院侧测试题、客户 Demo 材料、历史 Bad Case 或真实任务记录；

如果历史材料无法恢复，再找真实法律使用者提供或确认任务；

只有在这些都不足时，才使用人工构造的 Target Scenario，而且必须明确标成 Benchmark Scenario，而不能说是历史客户任务。

验证集还应该同时包含简单任务和复杂任务。

因为如果只选“特别适合 Zuno”的跨文档、多版本任务，就会自己给自己制造优势。

2. 如果 Simple RAG 只差一点，但成本低很多，我不会只看 Accuracy 谁高。

要一起比较：

质量差多少；

Reviewer Acceptance 差多少；

Unsupported Claim 是否下降；

Latency、Token、模型调用和运维成本增加多少；

结果复用和新证据后的维护成本是否改善。

最好在实验前就定义“多大收益才值得增加复杂度”。

如果复杂架构只换来很小的质量改善，却显著增加成本和恢复复杂度，我会选 Simple RAG。

当前 A/B/C Kill Test 已经有这个方向，但后续 Benchmark 需要把“实际值得的阈值”提前定义，而不是看完结果以后再解释。

Q4 Counter Answer

1. 对。

如果面试官继续问：

“你当时具体改了什么？”

“输入输出是什么？”

“出了什么 Bug？”

“怎么验证？”

我目前只能承认这部分历史没有恢复。

不能因为现在能看懂当前代码，就把当前代码反写成当年的个人贡献。

2. 在恢复之前，最安全的做法是把三类内容分开表达：

历史个人工作，只写目前能确认的 Agent、Memory、OpenViking Memory / Context 接入和 Tool Calling Strategy；

团队能力，不自动归到个人；

现在重新做的 Architecture Reconstruction，可以说“后来重新设计 / 参与架构梳理”，但不能写成“历史项目中本人已经实现”。

因此这个问题首先属于 Facts / Resume Ownership，不是靠修改 Target Architecture 能解决的。

如果简历中的“设计平台、检索、评测、安全恢复”等句子让人自然理解成全部历史个人实现，那应该由 Main 后续单独审查事实与简历口径，而不是让 Architecture 替这些表述背书。

Q7 Counter Answer

1. 如果所有外部 Tool 和副作用全部删除，只保留法律知识研究和审查，我认为 Zuno 的最小核心仍然可以成立。

这时我会把第三项重新说得更准确：

不是“高风险副作用控制”本身，而是正式业务结果的受控提交。

最小核心变成：

证据和结论可追溯；

长期、版本化、会随新证据失效的法律业务结果；

模型 Proposal 与正式业务状态之间有明确 Admission / Human Authority 边界。

发邮件、写外部系统属于任务存在副作用时才需要增加的一层 Trust 能力，不应该成为 Zuno 产品成立的前提。

2. 真正最能改变产品边界的是：

如果复杂法律任务中，Evidence-linked / Versioned Domain State 相比普通 Host + RAG 没有可测收益。

如果 B 与 A 接近，不只是删 Graph Provider 或 Memory Provider，而是说明 Legal Backend 本身很可能没有足够产品价值，Zuno 应进一步退回 Generic Host + Legal Skills / Retrieval。

这实际上已经符合 ADR-0008 的 Reversal Criteria。

Q8 Counter Answer

1. 目前没有。

我还不能指出一条已经有运行证据证明：

“Generic Host 通过插件、API 或外部 Backend 无论如何都实现不了，所以必须由完整 Zuno Platform 自己控制。”

能证明的是：

有一部分业务事实、证据依赖、Human Decision 和版本状态不能仅仅靠聊天上下文来表达；

但这些完全可能由一个外部 Legal Backend 提供。

2. 所以是的。

“Generic Host + Legal Backend 可能已经足够”目前比“完整 Zuno Native Platform 必须存在”更有证据。

而且这不是本轮新发明的结论。

当前 ADR-0008 已经明确把默认最小形态定义成：

Generic Host

Legal Skills / Knowledge Scope

MCP / API Legal Capability Provider

必要时的最小 Legal Domain Backend；

Native Domain-aware Runtime 则是 DEFERRED / HYPOTHESIS。

因此这里我不建议再增加 Architecture。

真正缺的是 Integration Spike 和 A/B/C Measurement。

Q11 Counter Answer

1. “最小可恢复执行控制”是系统需要的保证，不代表 Zuno 必须自己实现一套 Runtime。

如果 Generic Host 或 LangGraph 已经能够满足：

长任务持久化；

Interrupt / Resume；

任务恢复；

必要的幂等接口；

并且 Zuno 能在外部保存自己的 Domain State 和 Effect 状态，

那就应该复用。

Zuno 自己真正要拥有的是：

恢复以后业务状态怎么解释；

正式事实和 Runtime State 如何对账；

哪些操作可以 Retry；

哪些必须 Replan 或人工确认。

2. 还有很多“基础能力”都应该继续 Build / Buy：

基础 BM25 / Vector Retrieval；

Model SDK / Model Gateway；

Workflow Engine；

Checkpoint；

Queue；

Object Storage；

Vector / Graph Store；

普通认证机制；

Sandbox Provider；

UI。

Zuno 应拥有的是和自己业务正确性相关的 Contract、Policy 和 Domain State，而不是这些底层能力的每一个实现。

Q12 Counter Answer

1. 如果用户声明本次审查范围是这 100 份材料，而现在只有 40 份完成可检索处理，我默认不允许它直接形成正式审查结果。

最简单、安全的默认方案其实不是设计复杂机制，而是：

等所需材料 Ready，再开始正式审查。

如果产品需要让用户提前看到进度，可以允许基于 40 份材料做“部分分析”，但必须明确缩小 Scope，而且这个结果只能是草稿或临时分析，不能悄悄当成完整材料上的正式 Finding。

2. 因此每次 Run 必须知道：

它本来应该覆盖哪些文档和版本；

其中哪些已经完成必要的解析 / 索引；

当前检索看到的是哪一代 Knowledge View；

有没有缺少本应属于 Scope 的材料。

正式结果提交前需要再次确认：

这个结果依赖的 Knowledge View 是否满足该任务的最低完整性要求。

这里不一定需要一个新服务，也不需要把所有 Projection 状态塞进 Part A。

但 Part A 应该让读者知道一个原则：

Document Uploaded ≠ Knowledge Ready；正式结果必须知道自己基于什么完整度和版本的知识视图。

当前 Part B 已经提到 索引 stale 是 Evidence Retrieval 的失败条件，但还没有把“部分索引是否允许形成正式结果”讲成完整语义。

Q14 Counter Answer

1. 我第一次回答里的“最新合同 A 是当前业务材料，所以以 A 为准”确实说得太简单。

真实法律场景不能用：

版本号大 → 自动覆盖版本号小。

如果 A、B 分别适用于不同时间、主体、事项或者约定范围，它们都可能仍然有效。

系统首先应该保留：

它们各自是什么文件；

什么时候生效；

适用什么范围；

来源和版本是什么。

之后再判断哪份材料对当前争议点适用。

2. 这里是两个不同责任。

Knowledge 负责把 A、B 都正确找到，并保留来源、版本、时间和 Scope，不要因为新版本存在就把旧版本从证据空间抹掉。

“当前争议到底适用 A、B 还是二者组合”属于 Legal Intelligence / Domain Judgment。

模型可以提出 Applicability Proposal，但最终正式判断仍然需要受 Domain 规则和必要的人审约束。

所以这一项主要是我的第一次回答过度简化。

当前 Architecture 已经明确把 Legal Applicability 放在法律能力和业务判断边界里，因此我不认为必须因此新建一层架构。

Q15 Counter Answer

1. 我希望至少在两个时点发现 Tool 能力变化：

Plan / Step 准备使用 Tool 时先解析当前能力；

真正调用前再次确认当前 Tool 的参数和语义仍然与计划时兼容。

长任务不能只在十分钟前发现一次 Tool，然后一直假设能力不变。

运行中的任务应该知道自己原先基于哪一版 Tool Capability 做出的计划。

如果真正调用时发现 Server 已升级、参数不兼容，就不能让模型自己猜新参数然后继续。

2. 如何处理取决于“计划是否仍然成立”。

如果只是同一能力的瞬时网络故障，参数和语义没变，可以 Retry。

如果 Tool 能力发生了变化，但仍存在安全、兼容的替代调用方式，说明执行方式变了，剩余任务需要重新解析能力，必要时 Replan。

如果需要的能力已经消失、权限或审批条件改变，或者当前已经存在副作用 outcome uncertainty，就应该停止自动执行并进入人工处理。

所以：

Retry 解决执行失败；Replan 解决原计划所依赖的能力假设已经变化。

当前 Part B 已经把 Provider 版本不兼容 列为 Legal Capability 的失败类型，但 Part A 对“运行中 Provider / Tool Capability Drift”还不够直观。

Q17 Counter Answer

1. 不能由模型自己决定。

应该由这次任务的质量要求和 Answer / Domain Admission Policy 判断。

例如这类任务要求：

关键材料必须 Ready；

Citation Coverage 达到要求；

关键证据不能缺失；

某些高风险判断必须经过指定质量检查或 Human Review。

降级以后仍满足这些最低条件，就可以继续。

不满足，就不能因为“模型还是生成了一个答案”而算正式结果。

2. 这个差异应该在最终结果进入正式业务状态之前被控制。

正常模式满足所有要求：

可以进入正常 Admission。

发生降级以后：

如果仍满足最低要求，可以正常提交；

如果质量保证降低，则只能进入 review_required；

如果关键条件缺失，就应该 rejected / abstain，而不是形成正式 Finding。

当前 Part B 的 Domain Admission 本来就已经有 Canonical Version / review_required / rejected 三类输出。

因此这里不是要发明新的复杂状态机。

真正需要补的是 Part A 的普通工程语言：

降级不仅影响提示语，还会影响结果有没有资格成为正式业务状态。

Q19 Counter Answer

1. 如果权限已经被撤销，而任务 A 下一步还需要重新读取受保护案件材料，那它不能继续使用旧授权。

它需要重新鉴权。

鉴权失败以后，就不能继续读取。

同样，如果下一步需要重新检索受保护语料，或者把新的敏感内容发送给 Model Provider，也必须使用当前权限判断。

2. 所以只在副作用和最终提交前重新鉴权不够。

对长任务更准确的原则是：

每一次新的受保护访问都依据当前权限。

包括：

重新读取文档；

Knowledge Retrieval；

读取 Secret；

Tool Call；

向外部 Provider 暴露受保护内容；

正式提交。

任务启动时拿到的权限不能变成一个十分钟、一小时都永久有效的通行证。

至于“已经读进内存的旧内容，在撤权以后纯 CPU 计算还能不能继续”，这是更细的 Security Policy 问题。

高风险场景下我倾向于撤权后中断或隔离后续处理，但这个具体策略应该在 Security Module / Part B 冻结，而不是现在假装所有租户都只能有同一种规则。

当前 Part B 已经要求跨边界操作绑定 Policy Epoch，也把 Revoked Permission 列入验证要求，但 Part A 没有把“持续授权作用于所有新受保护访问”讲清楚。

Q20 Counter Answer

1. 重新看完当前 Architecture 和两份 ADR 后，我认为这个质疑成立。

如果今天没有真实负载、HA、安全隔离、独立 Availability 或独立 Deployment Lifecycle 证据，那么从证据驱动原则看，Microservice 不应该仅因为未来可能需要就天然比模块化 Backend + Worker 更高一级。

当前 Architecture 自己其实已经写着：

只有出现独立 Scaling、Failure、Security、Availability、Lifecycle 等理由才拆物理服务，而且默认可以从模块化 Python 服务加独立 Worker 开始。

ADR-0008 也明确写的是：

模块化单体 + 独立 worker 优先；用户数不是微服务证据。

但是 ADR-0010 又把 Microservice Architecture 固定为 accepted-target，并列出五个 network-facing Service Candidate。

所以这里已经不是一句话解释能解决的问题。

Main 需要判断：

这是 Owner 已经明确接受、即使尚无测量也必须保持的 Target Constraint；

还是前面架构重构留下的一项过强约束，现在应该降级成 evidence-gated deployment option。

Blue 不替 Main 做最终决定，但我倾向于后者，因为它更符合本轮已经形成的“复杂度举证责任”。

2. 我第一次把 Worker / Library 拆成独立 Service，至少需要看到一个明确而且可重复的独立边界，例如：

该工作负载需要单独扩缩容，而且与主事务后端资源曲线明显不同；

它的故障不能合理地和主进程共享 blast radius；

它需要独立网络 / Secret / Sandbox 安全边界；

它需要不同 Availability 或部署生命周期；

它需要形成稳定的跨 Host API，并有独立 Ownership。

如果只是：

“这个任务比较慢”

或者：

“以后用户可能很多”

那独立 Worker 就够，不需要马上增加网络服务。

1. ROUND QA RECAP

Q1

Red 在问什么：历史项目到底因为什么真实问题产生。

Blue 核心回答：历史智慧司法背景、Demo / Court Testing / Pilot 可以确认，但最初需求和人工 SOP 不知道。

Red 最终判断：事实缺口成立；Target Product Thesis 不能反写成历史起点。

Q2

Red 在问什么：为什么简单 RAG 不够，是否有真实失败链。

Blue 核心回答：Simple RAG 应作为默认基线，复杂度只服务跨材料、版本和长期更新任务。

Red 最终判断：Target 推理成立，但历史 Bad Case 和真实价值证据缺失。

Q3

Red 在问什么：法律定位是历史事实还是后期 Target 包装。

Blue 核心回答：法律 / 智慧司法是历史方向，高风险 Domain State 等是后期 Target 收窄。

Red 最终判断：回答充分，关闭。

Q4

Red 在问什么：个人到底做过什么。

Blue 核心回答：可确认 Agent、Memory、OpenViking、Tool Calling Strategy；其他不能扩大。

Red 最终判断：Ownership 边界正确，但工程任务级事实严重不足。

Q5

Red 在问什么：到底交付到 Demo、Pilot 还是 Production。

Blue 核心回答：做到 Pilot Validation，没有 Production 证据。

Red 最终判断：回答充分，关闭。

Q6

Red 在问什么：客户说“质量不好”具体是什么问题。

Blue 核心回答：只能确认存在反馈，不能确认具体 Cause / Fix / Metric。

Red 最终判断：事实不足，但回答方式正确；不允许用架构猜测补历史。

Q7

Red 在问什么：如果只留三个能力，Zuno Kernel 是什么。

Blue 核心回答：Evidence Traceability、Versioned Domain Result、Controlled Formal Result / Effect。

Red 最终判断：核心开始成形，但外部副作用不应与正式结果提交混成同一个必要条件。

Q8

Red 在问什么：为什么不用 Generic Host。

Blue 核心回答：Generic Host 能做的尽量复用，Zuno 只保留法律业务正确性相关状态和规则。

Red 最终判断：Build / Buy 原则正确，但尚无证据证明完整 Native Platform 必要。

Q9

Red 在问什么：Zuno Runtime 相比 LangGraph 真正增加什么。

Blue 核心回答：不是重造 Checkpoint，而是业务版本、权限、预算、Admission、Effect Reconciliation。

Red 最终判断：设计回答充分；Native Runtime 必要性属于 Measurement。

Q10

Red 在问什么：为什么还需要自己的 Memory 概念。

Blue 核心回答：Memory Provider 可以外部化，Zuno 只控制上下文使用政策；长期 Memory 可整层删除。

Red 最终判断：回答充分，关闭。

Q11

Red 在问什么：哪些高级能力其实可删，哪些基础能力真属于 Zuno。

Blue 核心回答：Graph、Long-term Memory、Persistent Multi-Agent、复杂 Planning、过早服务拆分都可删。

Red 最终判断：还需澄清“可恢复 Runtime”是所需保证，不等于 Zuno 自己实现。

Q12

Red 在问什么：完整用户请求如何跑。

Blue 核心回答：主执行链已经能从上传、检索、规划、候选、Tool、人审跑到正式提交。

Red 最终判断：主链成立，但缺少 Knowledge Readiness / Partial Index 语义。

Q13

Red 在问什么：Domain State 和 Runtime State 为什么分开。

Blue 核心回答：生命周期不同，Checkpoint 不能覆盖已经发生的正式业务事实。

Red 最终判断：回答充分，关闭。

Q14

Red 在问什么：新旧材料与 Memory 冲突怎么办。

Blue 核心回答：Memory 不可覆盖正式材料，旧版本仍保留。

Red 最终判断：来源边界正确，但“新版本优先”表达过度简化，需区分法律适用性。

Q15

Red 在问什么：MCP 只是接入还是安全边界，以及 Server 变化怎么办。

Blue 核心回答：业务权限、审批、幂等、审计属于 Zuno；MCP 只是 Provider / Protocol。

Red 最终判断：安全责任边界成立，但运行中 Tool Capability Drift 没讲完。

Q16

Red 在问什么：新证据如何使旧结论过期。

Blue 核心回答：按 Dependency 定位、局部重评、必要时扩大范围，旧版本保留但不能继续冒充 Current。

Red 最终判断：回答充分，关闭。

Q17

Red 在问什么：Graph / Memory / Model 同时故障时如何降级。

Blue 核心回答：可逐层降级，关键证据 / 权限 / Effect 不清时停止，并向用户显示降级。

Red 最终判断：还缺“降级结果是否有资格成为正式结果”的统一语义。

Q18

Red 在问什么：Tool 已成功但本地未知怎么恢复。

Blue 核心回答：先 Reconciliation，不盲目 Retry；unknown outcome 进人工处理。

Red 最终判断：回答充分，关闭。

Q19

Red 在问什么：并发、旧版本和动态撤权如何处理。

Blue 核心回答：提交和副作用前重检权限 / Domain Version，Domain Owner 决定正式状态。

Red 最终判断：还需覆盖运行过程中所有新的受保护访问，而不仅是写入边界。

Q20

Red 在问什么：规模增长时为什么要 Microservice。

Blue 核心回答：Worker-first、模块化 Backend 优先，实际证据决定 Service Split。

Red 最终判断：这与 Microservice Direction = ACCEPTED_TARGET 存在明显张力。

2. WHAT ACTUALLY FAILED

[FACT]

历史项目起点和真实业务 SOP 没有恢复。

这是 Q1 / Q2 / Q6 的共同问题。

不能通过修改 Architecture 解决。

当前 Target 只能继续保持 Target / Hypothesis，不能变成历史立项事实。

[FACT]

个人 Ownership 缺少任务级证据。

Q4 暴露的是：

参与过什么方向可以确认；

具体任务、代码、Bug、验证还无法确认。

这属于历史事实恢复和简历口径问题，不属于 Target Architecture 缺陷。

[MEASUREMENT]

Legal Backend、Native Runtime、Graph、长期 Memory 等复杂度的价值仍未被实际业务证明。

这里不是 Part A 完全没说清楚。

当前 Architecture 和 ADR-0008 已经有明确 Kill Test、Host Boundary 和 Native Runtime Deferred。

真正缺的是实验。

因此不能因为 Red 追问 Build / Buy 就增加更多平台能力。

[ANSWER]

Q14 第一次回答把“最新版本”说得过于像“最新版本必然覆盖旧版本”。

这是 Blue 的回答错误。

当前 Target 已经存在 Legal Applicability / Domain Judgment 边界，因此不需要因此新增“冲突解析服务”。

需要确保 Narrative 不让读者误解 Document Version 和 Legal Applicability 是同一件事。

[PART_A] + [PART_B]

Knowledge Readiness / Partial Index 缺少完整运行语义。

当前 Part B 已经知道 index stale 是 Retrieval Failure，但没有清楚回答：

Run 是否可以基于不完整 Knowledge View 开始；

如果开始，结果是否还能正式提交。

这是本轮真正发现的跨 Knowledge → Runtime → Domain Admission 缺口。

[PART_A] + [PART_B]

降级能力与正式结果资格之间的关系没讲清楚。

现有 Domain Admission 已经支持 review_required / rejected，所以不需要新增平行状态体系。

但需要把：

“Provider 降级”

和

“Result Eligibility”

明确连起来。

[PART_A] + [PART_B]

动态撤权目前强调了 Effect / Commit，但运行中的所有新受保护访问没有在 Narrative 中闭合。

Part B 已经有 Policy Epoch 和 Revoked Permission 验证要求。

因此这更像跨层安全原则没有讲透，而不是 Security 架构从零缺失。

[ARCHITECTURE]

运行中的 Tool / Provider Capability Drift 需要更明确。

Part B 已经把 版本不兼容 当作 Provider Failure。

缺的是：

什么时候检测；

Retry 与 Replan 怎么区分；

长任务不能按旧能力继续猜参数。

[ARCHITECTURE]

Microservice Target 存在真正的治理冲突。

ADR-0008 明确主张模块化单体 + Worker 优先，Native Platform / Runtime 保持可删除。

ADR-0010 则把 Microservice Architecture 固定为 accepted-target，并提出五个 Service Candidate。

总体 Architecture 又同时写：

Microservice Direction = ACCEPTED_TARGET

和

默认从模块化 Python + Worker 开始，Service Split 由证据决定。

这是本轮最明确的 Target Architecture / ADR Alignment Concern。

[NO_CHANGE]

以下 Red 追问重要，但当前设计已经足够：

Q3 的 History / Target 分离；

Q5 的 Pilot / Production 分离；

Q9 的 Runtime Provider / Domain Owner 分离；

Q10 的 Memory Provider 可替换性；

Q13 的 Domain State / Runtime State 分离；

Q16 的 Staleness / Dependency；

Q18 的 Effect Reconciliation。

不应为了显得“修了很多架构”而继续扩展这些部分。

3. ARCHITECTURE OPTIMIZATION PROPOSALS

PROPOSAL-01 — Knowledge Readiness 决定正式任务是否可运行

来源：

Q12 / Red Review：Partial Parsing、Partial Index、Projection Delay。

问题：

Document Uploaded 和 Knowledge Ready 当前没有在 Part A 的主链路中明确区分。

为什么它是架构问题：

高风险结果是否可信，不只取决于检索算法，还取决于 Agent 实际看到的是不是任务声明范围内完整、可识别版本的材料。

如果一个 Run 在 100 份材料只 Ready 40 份时产生正式结果，Domain Admission 就可能建立在错误的 Knowledge Scope 上。

建议的概念性调整：

Part A 增加一个简单原则：

正式任务必须知道自己绑定的文档范围、版本和 Knowledge Readiness；声明 Scope 尚未满足时，默认等待或阻止正式执行。允许 Partial Run 时必须显式缩小 Scope，结果不能自动获得正式结果资格。

Part B 再定义：

如何表达 Ready / Partial / Stale；

Run 如何绑定 Knowledge Generation；

Domain Admission 如何验证检索视图完整性。

建议落点：

Part A

Part B

Knowledge / Domain Module Design

复杂度影响：

NEUTRAL

为什么不是更简单的方案：

最简单方案就是所有必要索引完成前直接等待，这应当作为默认。

Proposal 不是要求新增 Readiness Service，而是防止正式结果在不完整知识视图上静默产生。

替代方案：

首版完全禁止 Partial Run，只允许所有声明材料 Ready 后执行。

反转条件：

如果产品永远只处理同步上传、极小文档集，而且索引完成具有强事务保证，则 Part B 可以显著简化。

当前状态：

建议接受

PROPOSAL-02 — 降级必须改变 Result Eligibility，而不仅是显示 Warning

来源：

Q17 / Red Review：Graph、Memory、Model 降级后的正式结果资格。

问题：

当前 Narrative 已经知道怎么降级 Provider，但没有清楚说明降级后结果还能否作为正式 Finding / WorkProduct。

为什么它是架构问题：

在高风险任务里，“系统还能生成文字”与“结果满足正式交付条件”是两个完全不同的问题。

如果 Provider Degradation 不影响 Domain Admission，就会产生假成功。

建议的概念性调整：

Part A 增加：

降级可以保证任务继续运行，但不能自动保证结果仍具有相同业务资格。每次降级都必须重新检查该任务的最低证据、质量和安全要求；不满足时结果降为 Draft / Review Required，或直接 Abstain。

Part B 使用现有 Domain Admission 的：

Canonical / review_required / rejected

表达具体控制，不新增平行状态体系。

建议落点：

Part A

Part B

Domain / Eval Module Design

复杂度影响：

NEUTRAL

为什么不是更简单的方案：

只在 UI 显示“Graph unavailable”不能控制业务状态。

但也无需建设新的 Degradation Engine，可以复用已有 Admission / Answer Policy。

替代方案：

所有关键 Provider 一旦降级都强制 Human Review。

反转条件：

对于低风险纯聊天或明确不形成正式业务状态的任务，只做 Warning 即可。

当前状态：

建议接受

PROPOSAL-03 — 长任务采用持续授权，而不是启动时授权

来源：

Q19 / Red Review：运行过程中权限撤销。

问题：

现有回答重点检查 Effect 和最终 Commit，但遗漏后续 Retrieval、Document Read、Model Egress 等新的受保护访问。

为什么它是架构问题：

权限控制的不只是“能不能最后写数据库”。

权限撤销以后继续读取材料或继续向外部模型传输内容，本身就可能造成越权和信息泄露。

建议的概念性调整：

Part A 增加一个安全原则：

长任务启动时的授权不是永久租约。每次新的受保护访问、外部暴露、Tool Effect 和正式提交都必须依据当前 Policy；权限撤销至少阻止后续新访问，并按任务风险决定 Pause / Cancel / Review。

Part B 再定义 Policy Epoch、Snapshot 使用、已经加载内容在撤权后的处理规则和恢复语义。

建议落点：

Part A

Part B

Security Module Design

复杂度影响：

NEUTRAL

为什么不是更简单的方案：

只在开始和最后检查两次权限不能覆盖长任务中间的敏感数据访问。

不需要引入分布式 Policy Engine；首先可以在现有 Security Gate 边界执行当前授权判断。

替代方案：

短任务使用极短授权租期，但高风险读取仍需服务端重新校验。

反转条件：

完全不访问受保护资源、没有外部 Egress 且任务只处理用户已经公开提供的数据时，可以简化。

当前状态：

建议接受

PROPOSAL-04 — 运行中的 Tool Capability 变化不能由 Agent 猜参数继续执行

来源：

Q15 / Red Review：MCP Server 在长任务中途升级。

问题：

当前 Architecture 有 Provider Version Incompatibility，但没有在 Part A 讲清“计划建立以后 Capability 发生变化”怎么办。

为什么它是架构问题：

计划对 Tool 能力存在假设。

如果 Tool Schema、名称或语义改变，继续按旧 Plan 自动调用可能产生错误甚至副作用。

建议的概念性调整：

Part A 补一个 Provider Drift 原则：

长任务使用 Tool / Capability 前需要确认当前能力仍与计划时兼容；不兼容时不能猜参数继续。瞬时执行失败使用 Retry，能力假设失效则重新解析能力并 Replan；无法建立安全兼容路径则停止或 Human Review。

具体版本绑定、Schema Compatibility、Provider Resolution 放 Part B / Tool Module。

建议落点：

Part A

Part B

Tool / Capability Module Design

复杂度影响：

NEUTRAL

为什么不是更简单的方案：

“调用失败就重试”无法处理语义已经改变的 Tool。

也不需要设计复杂的全球版本协商协议；首版只要绑定运行时观察到的能力版本并在调用前验证兼容性。

替代方案：

任务启动后禁止 Tool Server 热升级，只在任务结束后切换版本。

反转条件：

若部署环境能够强制整个 Run 生命周期内 Tool Capability 不变化，则运行时兼容检测可以显著简化。

当前状态：

建议考虑

PROPOSAL-05 — 重新审查 Microservice Direction = ACCEPTED_TARGET

来源：

Q20 / Red Review，以及 ADR-0008 与 ADR-0010 的当前冲突。

问题：

当前治理同时表达了：

模块化单体 + Worker 优先；

Service Split 由 Scaling / Failure / Security / Lifecycle 证据决定；

以及 Microservice Architecture 是 accepted-target。

这三个陈述放在一起，容易使“证据驱动拆分”退化成“最终反正一定微服务，只是暂时没拆”。

为什么它是架构问题：

这是物理架构方向是否已经冻结的问题，不是 Blue 回答方式问题。

而且它已经跨越总体 Architecture 和两个 Accepted ADR。

建议的概念性调整：

Main 应重新判断 Microservice 的治理状态。

Blue 倾向的目标表达是：

模块化 Backend + 独立 Worker 是默认物理起点；Microservice 是 evidence-gated deployment refinement，而不是在缺少独立扩缩容、故障、安全、Availability 或 Lifecycle 证据时预先承诺的终局。

如果 Main 决定仍保留 ACCEPTED_TARGET，则必须明确：

它是 Owner Constraint，而不是由当前负载证据推导出的架构结论；

并说明为什么这个约束值得承担当前 ADR 已承认的分布式系统成本。

建议落点：

Part A

ADR

Deployment / Infrastructure Module Design

复杂度影响：

SIMPLIFY

为什么不是更简单的方案：

更简单的方案正是模块化 Backend + Worker，应作为默认比较对象。

替代方案：

保留 ADR-0010 不变，但把五 Service 仅作为 Future Deployment Profile，并要求每个 Service 单独过 evidence gate。

反转条件：

出现可重复证据证明某边界确实需要独立 Scaling、Failure Isolation、Security Boundary、Availability 或 Deployment Lifecycle 时，再正式拆分对应 Service。

当前状态：

建议接受 Main Review；是否修改需 Main 决定

4. KEEP / DO NOT CHANGE

1. 不要因为 Q1 / Q2 / Q6 的历史事实不足，就把 Target Architecture 删除或反写成历史。

正确动作是继续把 Product Thesis 标成可验证 Target，并补 Facts / Measurement。

2. 不要因为 Red 讨论 Generic Host，就重新强化 Native Zuno Platform。

当前 ADR-0008 已经把 Generic Host + Legal Backend 作为默认最小形态，把 Native Runtime 放在 Deferred / Hypothesis。

这应该保持。

3. 不要因为 Runtime 被质疑，就删除 Domain State / Runtime State 分离。

即使最终完全使用 LangGraph、Dify 或其他 Host，业务事实仍不能等价于 Workflow Checkpoint。

Q13 / Q18 已经证明这个边界有独立价值。

4. 不要因为 Q14 出现复杂法律冲突，就增加新的 Conflict Resolver Service。

当前问题主要是 Blue 把“版本”和“适用性”说得太简单。

Knowledge / Legal Intelligence / Domain Judgment 的现有责任划分已经足够。

5. 不要因为 Q15 出现 MCP Version Drift，就绑定某个特定 MCP Server。

Architecture 应保护 Tool / Capability 的业务 Contract，不应锁定 Provider。

6. 不要因为 Graph、Memory、Multi-Agent 被反复讨论，就把它们重新升级成核心。

Graph 继续 Conditional；

Long-term Memory 继续可删除；

Persistent Multi-Agent 不作为默认目标。

7. 不要因为并发和撤权问题就引入分布式数据库、2PC、Event Sourcing 或复杂分布式锁。

当前 PostgreSQL Version / Admission + Runtime Checkpoint + Security Gate 的基本边界仍可保持简单。

8. 不要把“可恢复执行”写成 Zuno 必须自研 Runtime。

这是必须满足的能力要求，不是实现 Ownership。

5. FACTS TO VERIFY

1. 历史第一版需求、谁提出、原人工 SOP、最耗时 / 最容易出错的步骤。

2. 至少一条真实法律任务 / Court QA / Customer Demo Bad Case，可以还原：

Simple RAG 或旧系统表现
→ 具体失败
→ 团队修改
→ 结果是否改善。

3. 个人代码级 Ownership：

任务是什么；

改了什么逻辑；

输入输出；

遇到什么 Bug；

怎么调试；

怎么验证。

4. “回答质量需要提高”的真实 Cause / Fix / Metric，以及本人是否参与其中。

5. Pilot 的真实范围：

参与人员；

任务类型；

数据规模；

运行时间；

部署环境；

评价方法；

是否存在可恢复 Artifact。

这些都不能通过修改 Target Architecture 来补齐。

6. EXPERIMENTS / MEASUREMENTS NEEDED

Experiment 1 — Simple RAG vs Legal Backend

使用真实或由真实法律用户确认的任务，至少区分：

简单单文档；

跨文档；

跨版本；

新证据导致旧结论变化。

比较 Generic Host / Simple RAG 与 Legal Backend。

同时测质量、Reviewer Acceptance、Unsupported Claim、Latency、Token 和成本。

如果 B 与 A 近似，缩减 Domain Backend。

Experiment 2 — Generic Host Integration Spike

不是比较 Feature List，而是真正把一条完整 Zuno Target Task 放进 Generic Host：

Document Scope；

External Legal Backend；

Domain Version；

Human Review；

Tool Gate；

Resume / Recovery。

检查 Host 扩展点是否够。

如果够，则继续外部化 Native Runtime。

Experiment 3 — Native Runtime A/B/C Kill Test

继续执行当前 Architecture 的 A / B / C：

A：Generic Host + Legal Prompt / Skills

B：Generic Host + Zuno Legal Backend

C：Zuno Native Runtime + First-class Domain State

并提前注册“多大的 C > B 才值得增加 Runtime 成本”。

Experiment 4 — Graph / Memory Ablation

对相同数据与相同模型分别关闭：

Graph；

Long-term Memory；

Agentic Retrieval。

只有在特定 Query Class 上产生稳定质量 / 成本收益才保留。

Experiment 5 — Knowledge Readiness Fault Test

人为制造：

100 份文档只完成 40 份；

Vector 已完成但 Graph Projection 未完成；

Index stale；

某文档新版本已上传但旧 Index 仍在。

验证系统不会静默形成完整 Scope 的正式结果。

Experiment 6 — Dynamic Permission Test

长任务执行中途撤销：

Document Read；

Retrieval Scope；

Model Egress；

Tool Permission；

Approval。

验证后续新访问是否立即被阻止，以及 Resume 后是否重新使用当前权限。

Experiment 7 — Service Split Evidence

在决定某组件变成独立 Service 前分别测：

CPU / GPU / I/O Scaling；

Failure Blast Radius；

Security / Secret Boundary；

Availability；

Deployment Lifecycle；

Operational Cost。

如果 Worker 已经能解决问题，就不拆 Network Service。

================================================== MAIN COORDINATOR HANDOFF

ROUND: 01

BASE_SHA: b00f5bb3fb0bad9168a1dce96d9e4817a60d9773

A. 本轮核心结论

本轮没有证明 Zuno 历史项目最初就是为了当前 Target Product Thesis 而建立；历史 SOP、真实 Bad Case 和代码级个人 Ownership 仍是 Facts 缺口，不能由 Architecture 补写。

Target Architecture 的主体边界反而基本经受住了本轮攻击：Generic Host + Legal Backend 是更可信的最小默认形态，Native Runtime、Graph、Long-term Memory 和 Persistent Multi-Agent 都可以继续保持可删除。

端到端链路真正新增暴露了四个需要补清楚的运行原则：Knowledge Readiness、降级结果资格、持续授权、运行中 Tool Capability Drift。

本轮最强的 Architecture Concern 是 Microservice 治理：ADR-0008 的“模块化单体 + Worker 优先”与 ADR-0010 的“Microservice accepted-target”以及 Part A 当前状态表达之间存在需要 Main 明确裁决的张力。

B. 建议修改 Architecture

PROPOSAL-01
补充 Knowledge Readiness 原则：正式 Run 必须知道自己基于哪些材料、版本和完整度，Partial Knowledge View 不得静默生成完整 Scope 的正式结果。

PROPOSAL-02
补充 Degradation → Result Eligibility 原则：Provider 降级以后必须重新判断是否仍可形成正式结果，而不仅是显示 Warning。

PROPOSAL-03
补充 Continuous Authorization 原则：长任务所有新的受保护访问均按当前权限重新判定。

PROPOSAL-04
补充 Tool Capability Drift 原则：运行中能力版本变化时不得猜参数继续，区分 Retry、Replan 和 Stop / Review。

PROPOSAL-05
Main 重新审查 Microservice Direction = ACCEPTED_TARGET，并统一 ADR-0008、ADR-0010 与 Part A 的物理部署叙事。

C. 建议不修改

1. 不修改 History / Current / Target 严格分离原则。

2. 不因为 Generic Host 质疑而强化 Native Runtime；继续保留 Host + Legal Backend 默认边界。

3. 不修改 Domain State 与 Runtime State 分离。

4. 不新增所谓“Memory Conflict Service”或“Legal Conflict Resolver Service”。

5. 不绑定 OpenViking、Dify、WorkBuddy 或某个 MCP Server。

6. 不把 GraphRAG、Long-term Memory、Persistent Multi-Agent 升级为默认能力。

7. 不因为并发问题引入 Event Sourcing、2PC、分布式数据库或复杂锁。

D. 建议补 Facts

1. 历史人工 SOP 和第一版真实需求。

2. 真实法律任务与 Simple RAG / 旧系统 Bad Case。

3. 客户“回答质量需要提高”的 Cause → Fix → Metric。

4. 用户个人代码级 Task → Change → Bug → Debug → Test Ownership。

5. Pilot 的用户、任务、数据、部署和验证范围。

这些都不能通过修改 Target Architecture 来补齐。

E. 建议进入 Part B / Module

1. Knowledge Readiness 的具体状态、Generation、Partial / Stale 处理。

2. Degradation 对 Admission / Answer Policy 的具体映射。

3. Dynamic Permission / Policy Epoch 对 Read、Retrieval、Model Egress、Tool、Commit 的具体语义。

4. Tool Capability Version / Compatibility / Re-resolution。

5. Service Split 的实际证据条件与运行验证方式。

不要把这些字段级和状态级细节全部塞进 Part A。

F. 需要验证

1. Simple RAG vs Legal Backend。

2. Generic Host Integration Spike。

3. A / B / C Runtime Kill Test。

4. Graph / Long-term Memory Ablation。

5. Partial Index / Stale Knowledge Fault Test。

6. Revoked Permission Fault Test。

7. Microservice / Worker Scaling、Failure 和 Security Evidence。

G. 建议归档内容

ARCHIVE_FULL_ROUND_PACKET: YES

归档范围：

STAGE A Red Questions

STAGE B Blue Initial Answers

STAGE C Red Review / Counter

Blue Counter Answers

STAGE D Blue Reflection

Main Coordinator Judgment（之后由 Main 添加）

H. 给 Main 的一句话建议

本轮建议只补 Knowledge Readiness、降级结果资格、持续授权与 Tool 能力漂移，并优先裁决 Microservice accepted-target 与 Worker-first 证据原则的冲突，其余 Host / Runtime / Graph / Memory 继续按现有 Kill Test 验证，不扩大历史事实。


---

STAGE E — MAIN COORDINATOR JUDGMENT

STATUS: MAIN_JUDGMENT_COMPLETED

ROUND_OUTCOME:
CONDITIONALLY_ACCEPTED_WITH_TARGETED_REVISIONS

ARCHITECTURE_GATE:
OVERALL_ARCHITECTURE_BASELINE_SURVIVED_ROUND_01

MODULE_DECOMPOSITION_GATE:
NOT_OPEN


### 1. Overall Judgment

Round 01 已经达到预期目的：

Zuno 的 Overall Architecture Narrative 已经能够用普通工程语言解释：

- 为什么简单 RAG 可能不足；
- Generic Host 与 Zuno 自有能力的边界；
- Domain State 与 Runtime State 的区别；
- Knowledge、Memory、Model、Tool 和正式业务状态的大致责任；
- 新证据、恢复、降级和副作用的基本处理思路；
- Graph、Long-term Memory、Native Runtime、Persistent Multi-Agent
  等复杂能力为什么必须保持可删除。

因此：

总体 Architecture 不需要推倒重来。

但是：

Part A 还没有达到最终稳定状态。

Round 01 暴露出的少数跨层缺口需要先修正，
然后再进行至少一轮 Overall Architecture 复试。

在此之前：

不得因为旧 11 模块或当前目录已经存在，
直接冻结最终 Module Count / Module Boundary。


### 2. Story / Reality Judgment

ACCEPT RED FINDING。

历史事实目前只能支持：

智慧司法背景；
内部 Demo；
客户 Demo；
法院侧人员测试；
Pilot Validation；
存在“回答质量还需要提高”的客户反馈。

目前不能支持：

原始人工 SOP；
第一版真实需求；
一条完整历史 Bad Case；
Simple RAG → Failure → Fix → Metric 的真实闭环；
具体 Pilot 用户规模 / SLA；
完整历史运行技术栈；
大量代码级个人 Ownership。

这些都是：

FACT GAP

而不是：

ARCHITECTURE GAP。

正式决定：

不得修改 Target Architecture 去填补这些未知历史事实；
不得把 Target Scenario 反写成历史真实客户流程；
不得因为当前代码存在某能力就声明历史项目已经运行过该能力。


### 3. Minimal Product Boundary Judgment

ACCEPT WITH CLARIFICATION。

当前更可信的最小产品边界是：

Generic Host
+
Zuno Legal Backend / Legal Capability

而不是：

必须拥有一个完整 Native Agent Platform。

Zuno 目前最值得继续验证的 Kernel 是：

1. 结论与材料 / 证据之间可追溯；
2. 长期、版本化、可因新证据失效的业务结果；
3. 模型 Proposal 与正式业务状态提交之间存在受控边界。

外部 Tool / Side Effect：

属于存在副作用任务时的重要 Trust 能力，

但不是：

“Zuno 产品能够成立”

的绝对前提。


### 4. Native Runtime Judgment

KEEP CURRENT REVERSIBLE POSITION。

Native Runtime：

不升级。

仍保持：

DEFERRED / HYPOTHESIS。

LangGraph、Generic Host 或其他 Runtime
如果已经满足：

durable execution；
checkpoint；
interrupt / resume；
必要的任务恢复；

则应优先复用。

Zuno 自己真正需要拥有的是：

恢复后业务状态如何解释；
Domain 与 Runtime 如何对账；
Retry / Replan / Human Review 的领域控制；
正式状态什么时候允许提交。

是否值得维护 Native Runtime：

继续由 A / B / C Kill Test 决定。


### 5. Graph / Memory / Multi-Agent Judgment

NO PROMOTION。

以下能力继续保持可删除：

GraphRAG；
Agentic Retrieval；
Long-term Memory；
复杂 Dynamic Planning；
Persistent Multi-Agent；
大规模 Specialist Runtime。

不得因为本轮讨论次数多，
就把这些能力提升为 Zuno Kernel。

OpenViking、Dify、WorkBuddy、LangGraph、MCP
继续保持可替换 / 可复用候选，
不得锁定 Provider。


### 6. PROPOSAL-01 — Knowledge Readiness

DECISION:
ACCEPT

Architecture 必须补清：

Document Uploaded
不等于
Knowledge Ready。

正式 Run 必须知道：

本次任务声明覆盖哪些材料；
材料处于哪些版本；
当前 Knowledge View 是否完整到足以满足本次任务。

默认最简单策略：

必要材料未 Ready 时等待或拒绝正式执行。

如果允许 Partial Run：

必须显式缩小 Scope，
且 Partial Knowledge View 不得静默形成完整 Scope 的正式结果。

Part A：

只写概念原则和用户可理解的系统行为。

Part B：

再定义具体 Readiness、Generation、Partial / Stale 和 Admission 规格。

不要因此新增 Readiness Microservice。


### 7. PROPOSAL-02 — Degradation and Result Eligibility

DECISION:
ACCEPT

Architecture 必须区分：

系统还能继续生成结果

和

结果仍满足正式业务资格。

Graph、Memory、Model 或其他 Provider 降级以后：

必须重新判断本任务最低证据、质量和安全要求是否仍满足。

可能结果：

仍可正式提交；
必须 Human Review；
只能作为 Draft；
Abstain / Reject。

不得只依赖 UI Warning 表达质量下降。

优先复用现有：

Answer Policy
+
Domain Admission

不要创建第二套平行状态机。


### 8. PROPOSAL-03 — Continuous Authorization

DECISION:
ACCEPT

长任务启动时获得的权限：

不是整个 Run 生命周期的永久授权。

所有新的受保护访问都必须依据当前权限：

Document Read；
Retrieval；
Secret Access；
Model Egress；
Tool Call；
External Effect；
Formal Commit。

权限撤销后：

至少阻止新的越权访问。

已经载入内存的数据是否允许继续纯计算、
何时 Pause / Cancel / Review，

进入 Part B / Security Module 后再冻结具体策略。

不得因此默认引入复杂分布式 Policy Engine。


### 9. PROPOSAL-04 — Tool Capability Drift

DECISION:
ACCEPT_WITH_SCOPE_REDUCTION

Part A 应补充简单原则：

长任务不能假设 Tool / MCP Capability
在整个 Run 生命周期永久不变化。

实际调用前：

必须确认当前能力仍与原计划兼容。

如果只是瞬时执行失败：

Retry。

如果 Tool Schema、语义、能力或权限发生变化，
导致原计划假设失效：

重新解析能力，
必要时 Replan。

如果无法建立安全兼容路径：

Stop / Human Review。

Part A 不进入：

版本协商协议；
具体 Schema Registry；
具体数据库表；
内部 Version Contract。

这些只允许以后进入 Part B / Tool Module，
并且只有确有必要时实施。


### 10. PROPOSAL-05 — Microservice Governance

DECISION:
ACCEPT_AND_REVISE_TARGET

Main Coordinator 判定：

当前：

ADR-0008
“模块化单体 / Backend + Worker 优先”

与：

ADR-0010
“Microservice Architecture = accepted-target”

存在实质性治理张力。

Round 01 的 Architecture Decision 是：

不再把 Microservice 作为缺少运行证据时预先承诺的终局 Target。

新的总体原则应是：

模块化 Python Backend
+
必要的独立 Worker

作为默认物理起点。

Microservice / Independent Network Service
是：

EVIDENCE-GATED DEPLOYMENT REFINEMENT。

只有当某个边界出现可重复证据证明需要：

Independent Scaling；
Failure Isolation；
Security / Secret Isolation；
Distinct Availability；
Independent Deployment Lifecycle；
Stable Cross-host API；
Distinct Data / Operational Ownership；

才允许真正拆为独立 Network Service。

“任务比较慢”
“以后用户会很多”
“微服务更先进”

均不足以成为拆分证据。

ADR-0010 的正式治理修订：

留给下一独立 Architecture Revision Task 执行。

本 Archive Task 不修改 ADR。


### 11. Keep / Do Not Change

本轮明确不改变：

History / Current / Target 分离；

Domain State 与 Runtime State 分离；

Generic Host + Legal Backend 的默认最小边界；

Native Runtime Deferred；

Graph Conditional；

Long-term Memory 可删除；

Persistent Multi-Agent 非默认；

模型只产生 Proposal、不能直接提交正式业务事实；

副作用 unknown outcome 必须先对账而不是盲目 Retry；

PostgreSQL 与 Runtime Checkpoint 的事实边界。


### 12. Facts and Measurement

以下内容保持：

OPEN FACT GAP

不得由 Architecture 自动补齐：

历史人工 SOP；
历史 Bad Case；
个人代码级 Ownership；
质量 Cause → Fix → Metric；
Pilot 规模和运行细节。

以下内容保持：

MEASUREMENT REQUIRED

Simple RAG vs Legal Backend；
Generic Host Integration Spike；
A / B / C Runtime Kill Test；
Graph Ablation；
Long-term Memory Ablation；
Partial Knowledge Fault Test；
Dynamic Permission Fault Test；
Service Split Evidence。


### 13. Module Gate

MODULE_DECOMPOSITION_GATE:
NOT_OPEN

原因：

Round 01 的目标是建立 Overall Architecture，
不是冻结模块。

下一步顺序：

先根据本轮 Main Judgment
对 Part A 做一次 Targeted Revision；

再执行 Round 02 Overall Architecture Interview。

只有当 Round 02 的主要问题已经从：

“Zuno 到底是什么、为什么这样设计”

转变为：

“某个稳定责任内部如何设计”

时，

Main Coordinator 才打开：

MODULE_DECOMPOSITION_GATE。


### 14. Round 01 Final Conclusion

Round 01 没有要求推翻 Zuno 总体架构。

它确认了：

Generic Host + Legal Backend
是当前最有解释力的最小默认形态；

并发现四个值得补清的跨层运行原则：

Knowledge Readiness；
Degradation → Result Eligibility；
Continuous Authorization；
Tool Capability Drift。

同时正式要求重新收敛 Microservice Target：

默认从模块化 Backend + Worker 开始，
物理 Service Split 必须由真实证据触发。

ROUND 01:
COMPLETED

NEXT ARCHITECTURE ACTION:
TARGETED PART_A REVISION

NEXT RED_BLUE ACTION:
ROUND 02 — OVERALL ARCHITECTURE RE-INTERVIEW

================================================== END CURRENT PACKET
