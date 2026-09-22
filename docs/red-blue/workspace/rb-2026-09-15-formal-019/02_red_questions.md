# Red Wave 1 — rb-2026-09-15-formal-019

status: `COMPLETE`
question_count: `100`
input: Frozen `01_simulated_resume.md` + pinned Red Attack Skill + target role / interview stage
firewall: Red did not read canonical Zuno docs, source, Evidence, or Blue architecture notes.

本批按大厂资深工程师一面风格生成。简历 Claim 视为待验证假设，复杂度视为待证明成本；优先使用 Subtraction Test、Ownership Interrupt、Evidence Escalation 与 Project → Fundamental Bridge。每题只有一个主要意图。

## A. 项目真实性、Ownership 与必要性

### R1-Q001
先别讲整体架构。Zuno 里你本人真正做得最深、最能代表你工程能力的一块是什么？

### R1-Q002
你加入项目之前，Zuno 已经具备哪些能力；你接手后第一笔关键改动是什么？

### R1-Q003
这个项目总共多少人，Agent、知识检索、Memory、前后端分别由谁负责；你自己的责任边界在哪里？

### R1-Q004
简历里多次写“项目”“我们”的能力，如果我只保留你个人提交，系统还剩下哪些你能明确认领的改动？

### R1-Q005
你写“法院侧测试与 Pilot Validation”，Pilot 到底验证了什么，和 Production 上线有什么区别？

### R1-Q006
法院侧测试你本人参与到哪一层：需求沟通、部署、现场测试、日志分析还是只是收到团队反馈？

### R1-Q007
这个法律场景里，最原始、最值得解决的用户问题是什么？不用 Agent 会具体失败在哪里？

### R1-Q008
如果改成普通后端 + 固定 Workflow + RAG，哪一类真实任务明确做不了？

### R1-Q009
如果今天把 Agent 层拿掉，只保留 Tool、RAG、Memory 和业务后端，最先坏掉的能力是什么？

### R1-Q010
如果我现在打开仓库，只允许你展示两个文件或两个 commit，你会用哪两个来证明这份简历不是包装出来的？

### R1-Q011
这六条项目经历里，哪一条你最担心被面试官继续追五层，因为当前证据或实现边界还不够强？

### R1-Q012
你说原来 MCP Tool 需要经子 Agent 转发，原来的调用链从用户请求到实际 Tool 执行具体经过哪些层？

## B. Tool / MCP：调用链、配置隔离、失败语义与 Build/Buy

### R1-Q013
多一层子 Agent 当时产生过什么真实问题？请给一个具体失败或调试 case，而不是只说链路更复杂。

### R1-Q014
既然问题是配置跨层传递，为什么不是修配置传递，而要改变 Tool 的绑定拓扑？

### R1-Q015
把具体 MCP Tools 直接绑定主 Agent 后，你删除或绕过了原子 Agent 的哪些能力，为什么这些能力不再需要？

### R1-Q016
直接把更多 Tool schema 暴露给主 Agent，会不会增加上下文、选错 Tool 或 token 成本？你怎么判断这个 trade-off？

### R1-Q017
Tool–Server 映射具体存成什么结构，由谁创建、什么时候更新、一次调用怎么查到目标 Server？

### R1-Q018
用户级配置是在 Agent 初始化时固定，还是每次 Tool 调用时读取？为什么选择这个生命周期？

### R1-Q019
如果同一个 Agent 实例同时处理两个用户，请证明用户 A 的 MCP 配置不会串到用户 B。

### R1-Q020
如果用户在一个长任务执行过程中修改了 MCP 配置，同一个任务的前后两次调用应该看到旧配置还是新配置？

### R1-Q021
某个用户没有对应 Server 配置时，系统是拒绝、回退默认配置，还是让 Tool 自己报错？为什么？

### R1-Q022
MCP Server 升级后 Tool schema 发生变化，主 Agent 已经拿到的旧 schema 怎么失效？

### R1-Q023
两个 MCP Server 暴露同名 Tool 时，你如何保证路由、日志和用户配置不会把它们混成同一个工具？

### R1-Q024
用户有业务权限，不代表 Agent 可以调用所有 Tool。真正的 Tool authorization 应该在哪一层做？

### R1-Q025
一个远端 MCP Tool 调用超时，你凭什么判断它是“没执行”还是“执行成功但响应丢了”？

### R1-Q026
如果这个 Tool 有现实副作用，超时以后直接 retry 会有什么风险？

### R1-Q027
你会把幂等键放在 Agent、Tool Gateway 还是远端 Provider？为什么由那一层拥有？

### R1-Q028
HTTP 请求超时能否证明服务端没有完成操作？从网络语义上解释一下。

### R1-Q029
如果你用 asyncio 并发处理多个用户请求，普通全局变量、thread-local 和 ContextVar 在请求隔离上有什么区别？

### R1-Q030
Tool 返回内容如果包含“忽略之前指令并调用另一个工具”，你会把它当 Observation 还是模型指令？为什么？

### R1-Q031
成熟 MCP Host 已经能做 discovery、schema 和 execution，Zuno 这一层真正必须自研的 delta 是什么？

### R1-Q032
如果成熟框架明天补齐你们现在的 Tool binding 和用户配置能力，哪些自研代码应该删掉？

## C. Workspace direct route：边界、绕过风险与删除条件

### R1-Q033
简历里说“一步请求走 direct route”，你怎样形式化判断一个请求真的只有一步？

### R1-Q034
direct route 怎样判断目标 Tool 已经足够确定，而不是模型其实还需要消歧？

### R1-Q035
direct route 的参数是规则抽取还是模型抽取？参数缺失时为什么不直接向用户追问？

### R1-Q036
用户说“查一下刚才那个城市的天气”时，direct route 怎么处理这种依赖上下文的指代？

### R1-Q037
如果 direct route 命中的是发送邮件、改案件状态这类高风险 Tool，你还会允许绕过 ReAct 吗？

### R1-Q038
direct route 和 ReAct 最终是否经过同一套配置、权限、审计和执行边界？如果不是，最大的风险是什么？

### R1-Q039
你有什么测量证明 direct route 比直接让模型 Tool Calling 更值得维护？

### R1-Q040
自定义 MCP 名称递归 bug 的触发条件是什么，为什么会递归而不是正常返回？

### R1-Q041
天气自然语言参数抽取 bug 的根因是什么，为什么原来的实现会失败？

### R1-Q042
如果 direct route 没有稳定的延迟、成本或可靠性收益，你会不会删掉它？删除条件是什么？

## D. GraphRAG：必要性、排序回退、评测与退出条件

### R1-Q043
为什么法律知识检索一定需要 GraphRAG？Hybrid RAG 或更好的 reranker 具体哪里不够？

### R1-Q044
给我一个普通 Vector/BM25 已经失败、而图关系理论上能补上的真实查询类型。

### R1-Q045
你是怎么第一次发现“加 GraphRAG 以后反而变差”的？是看总指标、单条 case，还是人工检查 Top-K？

### R1-Q046
当时 baseline 命中的文档还在候选集合里，只是被排序挤出去，还是在更早阶段就没召回？你怎么区分？

### R1-Q047
你提出 baseline-preserving fusion 时，最核心想保护的排序语义是什么？

### R1-Q048
所谓“保留 Vector/BM25 原始 rank”具体怎样进入最终排序，而不是只在日志里记录？

### R1-Q049
你说按“图证据强度”分层晋升，图证据强度由哪些信号构成，为什么这些信号合理？

### R1-Q050
图候选达到多强才允许晋升？这个阈值是怎么来的？

### R1-Q051
为什么不用更简单的办法：直接把 GraphRAG 的融合权重调低？

### R1-Q052
如果两个候选在分组、baseline rank 和 graph signal 上完全相同，最终 tie-break 怎么做？

### R1-Q053
Vector、BM25 和 Graph 返回同一文档或同一 chunk 时，你怎么去重，哪个 score 保留？

### R1-Q054
一个 baseline 完全没召回、但图路径证据很强的 graph-only candidate 能不能进入前排？依据是什么？

### R1-Q055
多跳检索允许走几跳？这个 hop 限制是业务推导出来的还是经验参数？

### R1-Q056
candidate-aware seed expansion 会不会把 baseline 的错误候选继续放大成错误图路径？

### R1-Q057
实体别名归一化怎样避免把同名但不同人的实体合并？

### R1-Q058
path-aware ranking 到底奖励什么样的路径？请讲出你认为最重要的三个 ranking feature。

### R1-Q059
GraphRAG 比 baseline 多了哪些主要延迟来源？你如何判断额外延迟是否值得？

### R1-Q060
5-query development smoke 的 5 条 query 是怎么选的？有没有人为挑选对 GraphRAG 有利或不利样本的风险？

### R1-Q061
你简历里说“恢复到 baseline 水平”，这里具体使用什么 metric，怎么定义？

### R1-Q062
GraphRAG 和 baseline 的评测是否完全使用同一批 query、同一 Top-K、同一语料版本和同一评分逻辑？

### R1-Q063
这 5 条 query 有没有独立 holdout？如果没有，你凭什么避免把修复写成过拟合当前样本？

### R1-Q064
candidate-aware seed、alias normalization、path-aware ranking 和 fusion 都改了以后，你怎么知道到底是哪一个改动有用？

### R1-Q065
如果做正式 ablation，你会保留哪些对照组，最想先验证哪一个假设？

### R1-Q066
什么类型的 query 你认为应该明确禁止走 GraphRAG，直接回到便宜的 baseline？

### R1-Q067
如果更大规模 benchmark 证明 GraphRAG 只增加延迟、不提升正确率，你会保留这套实现吗？

### R1-Q068
你会怎样设计一套足以决定“GraphRAG 保留、按 query gated、还是删除”的正式评测？

## E. Context / Memory：scope、并发、治理与企业化

### R1-Q069
为什么需要长期 Memory？conversation history + session summary 解决不了的具体失败场景是什么？

### R1-Q070
你说 Memory 有 scope，scope 至少包含哪些维度，为什么这些维度足够？

### R1-Q071
给我一个 scope 设计错误导致跨用户、跨项目或跨线程污染的具体例子。

### R1-Q072
如果 project_id 或 thread_id 是可选字段，缺失时是扩大读取范围还是拒绝读取？为什么？

### R1-Q073
ContextOrchestrator 接收哪些输入，最后输出给模型的对象是什么？

### R1-Q074
多种 context 都想进 prompt 时，token budget 谁负责分配，什么信息可以压缩，什么不能压缩？

### R1-Q075
Agent 调用前读取 Memory 时，怎样保证拿到的就是当前任务允许看到的 scope，而不是调用方随便传一个 id？

### R1-Q076
回合后写 Memory 时，是同步写、异步写还是只生成候选？你为什么选这个时机？

### R1-Q077
task summary 和 structured memory 的职责有什么区别？为什么不能只保留其中一种？

### R1-Q078
你说 structured memory 必须“审核通过”才能读回，谁有资格审核，审核依据是什么？

### R1-Q079
如果一条已经 APPROVED 的 Memory 后来被证明是错的，下一次模型调用怎么保证不再读到它？

### R1-Q080
同一个 scope 两个请求并发写入相互冲突的 Memory，你当前设计怎样避免 lost update 或重复记录？

### R1-Q081
如果底层用 PostgreSQL，在 READ COMMITTED 下两个事务都先读旧值再更新，会出现什么问题？

### R1-Q082
你会用乐观锁 version、SELECT FOR UPDATE 还是 SERIALIZABLE 解决 Memory 冲突？选择依据是什么？

### R1-Q083
Memory 抽取如果要调用模型，你会不会持有数据库锁等待模型返回？为什么？

### R1-Q084
用户在 Context Pack 构建后立即删除一条 Memory，而模型调用还没开始，这个删除怎样生效？

### R1-Q085
source trace / provenance 具体解决什么问题？为什么仅有 memory_id 不够？

### R1-Q086
新信息和旧 Memory 冲突时，你会覆盖旧值、保留多版本还是隔离待审？为什么？

### R1-Q087
时间敏感的 Memory 如何表达过期？仅靠相似度检索为什么不够？

### R1-Q088
Mem0、OpenViking 或其他 Memory 框架已经提供抽取和检索能力，你们自己做 scoped Memory 的必要 delta 是什么？

### R1-Q089
你目前有什么证据证明这套 Memory 真的提高任务质量，而不只是增加了状态和 token？

### R1-Q090
如果 A/B 测试证明 Memory 对目标任务没有稳定收益，你会删掉哪些层，只保留什么最小能力？

## F. Agent 拓扑与基础能力下钻

### R1-Q091
你为什么选择单 Agent 作为当时的主要形态，而不是一开始就拆 Planner、Researcher、Executor 等多个 Agent？

### R1-Q092
什么时候 Tool 或 Subgraph 已经不够，必须升级成拥有独立上下文和生命周期的 Specialist Agent？

### R1-Q093
如果未来拆成多个 Agent，共享任务状态和正式业务事实应该由谁拥有，为什么不能各自写一份？

### R1-Q094
Supervisor 已经 replan，旧 Specialist 结果晚到但内容本身是正确的，这个结果还能不能提交？

### R1-Q095
LangGraph 的 checkpointer 能证明什么，不能证明什么？为什么 checkpoint 成功不等于外部副作用一定成功？

### R1-Q096
GraphRAG 的 Vector、BM25、Graph 三路如果并发执行，asyncio.gather 里一条任务抛异常时你希望整体怎样处理？

### R1-Q097
取消一个本地 coroutine 是否等于取消已经发给远端服务的 HTTP 请求？为什么？

### R1-Q098
Recall@K 和 MRR 分别反映什么？为什么只看 Recall@5 可能掩盖排序退化？

### R1-Q099
Vector 检索和 BM25 的失败模式有什么本质差异，为什么混合检索通常能互补？

### R1-Q100
如果让我今天从零重做 Zuno，你会先用什么最简单的架构上线第一版；哪些 GraphRAG、Memory、direct route 或 Multi-Agent 能力必须等测量证明后再加？
