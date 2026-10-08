# Blue Wave 2 — Candidate Answers A101–A200

```text
round: rb-2026-10-08-formal-021
role: Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师
answers_to: 04_red_wave2_review_and_questions.md @ <HEAD_AT_COMMIT>
register: 第一层 20–60 秒口语，其后可展开
coaching_boundary: 读了 Red 2 的公开盲评（Part A）；未读 03_blue_architecture_notes.md
provenance: >
  A101–A150 与 A151–A200 由两次同规格的 Blue 执行分别生成（同一 Skill、同一 register、同一 Ownership 规则），
  A151–A200 的生成方可读取前半批成品以保持口径一致。本文件为顺序拼接，未统一措辞。
```

## A101

两句都对，但说的是两个时间点。简历那句「复杂请求进入 ReAct 路径」写的是 4 月那版重构的**设计意图**——分流规则把复杂请求往 ReAct 侧路由；A8 说的是**今天**：那条复杂分支只有在注入 dynamic DAG planner 时才成立，而产品装配里 `main.py:113` 是 `dynamic_dag_planner=None`，所以带「报告」这类 complex 词的请求会在准入处命中 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND`，**在准入就被挡掉，走不到 ReAct**。所以「进入 ReAct 路径」作为今天的现状**不准确**。

第二层：

- 机制：分流在 `simple_agent.py:2150` `_plan_kind_for` 判 complex；准入链在 `single_controller_runtime.py:787-827`（reason 依次含 `stale_security_epoch` / `unknown_tool_for_workspace` / `UNRESOLVED_TOOL_POLICY` / `PRODUCT_APPROVAL_FLOW_NOT_BOUND` / `DYNAMIC_PLAN_RUNTIME_NOT_BOUND`），`complex_unbound` 在 `:737-739`，常量 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND` 在 `:103`。
- 顺手修正 Wave 1 两处硬错：(a) A8/A56 把 `single_controller_runtime.py` 写成 `agent/runtime/execution/` 下——错，真实路径是 `src/backend/zuno/platform/services/workspace/single_controller_runtime.py`；(b) 我说 `:497-501` 是抛异常——错，那是 `return None`。

- `事实层`: Current（准入行为）+ 我的历史表述错误
- `证据`: `main.py:113`；`platform/services/workspace/single_controller_runtime.py:103,737-739,818,787-827`；`simple_agent.py:2150`
- `边界`: 简历该句按今天 live path 应写成「复杂请求在准入层按 planner 绑定与否决定是否进 ReAct，今天产品装配下 fail closed」。另：Red 2 批评本套三段式像模板而非真实自限——我把 Q101/Q102/Q113/Q116/Q117/Q118/Q127/Q138/Q146/Q148 归为**真做现场判断**（我要在两条互斥陈述里选一条收口、并明确收回），其余题的三段式更接近固定格式。

## A102

两句不矛盾，但 A10 把测试的**对象**选错了。产品装配下这条复杂分支不可达（Q101），所以我本来该测的是「准入把 complex 挡掉」——那是确定性的、不需要模型；A10 讲的「要假模型 harness 才能冻结」说的是**准入之后 ReAct 行为**怎么断言，那才是 fixture 问题。我用后者去解释整条分支的测试成本，等于把最容易测的那段（准入 block）说成了难测。

第二层：

- direct route 一侧有回归断言（准入 + 工具参数抽取，含自定义 MCP 名称递归）；ReAct 一侧暂无断言。
- 今天若要补：优先补「complex + planner=None ⇒ 命中 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND`」这条准入断言，而不是 ReAct 行为断言。
- `事实层`: Current + 我的表述失焦
- `证据`: `single_controller_runtime.py:818`；简历第 1 条「ReAct 一侧暂无回归断言」
- `边界`: 我没把「准入 block」写成断言，这是当时缺口；ReAct 行为断言今天仍空。

## A103

覆盖不均。有回归断言的是 direct route 侧的准入与参数抽取（含自定义 MCP 名称递归）；`_detect_route_hint` 出来的 route-hint 出口、`/skill`、终端、图片重生成这些出口，我**没有**给每个都配专门断言。

第二层：

- `_resolve_governed_tool` 在 `simple_agent.py:2159`；`_canonical_mcp_target` 在 `:2702`；`_detect_route_hint` 在 `:2743`。
- 已知被测试触达的是 `_canonical_mcp_target` 的「已规范名不变」分支（Q108 那条）。
- `事实层`: Current + 覆盖缺口
- `证据`: `simple_agent.py:2159,2702,2743`；无逐出口断言清单
- `边界`: 我没逐出口审计断言覆盖，所以「哪些没有」我只按已知报 direct/ReAct 两侧，其余标未核实。

## A104

固定清单，不是从 server 注册表生成。`_detect_route_hint` 里是写死的 `command_map` 字典和写死的 `["飞书",…]` / `["高德",…]` / `["必应",…]` / 知识库 / skill / 终端 关键词元组。新接一个 server，只要不在 bing/gaode/feishu 之内，这张表**不会**自动认识它——会静默落到 `RouteHint()`（空），需要人改代码。

第二层：

- 兜底：单 server 情形有 `if not target and len(self.mcp_configs) == 1` 的回填；多 server 就没有。
- 维护成本：新增 server = 改关键词表，纯手工。
- `事实层`: Current
- `证据`: `simple_agent.py:2743-2800`（字面 dict + 字面元组）
- `边界`: 我没把它做成注册表驱动；这是可改进项（今天建议：从 server 注册表派生 + 显式命令兜底），不是当时已实现。

## A105

这张表在 `simple_agent.py:2150` `_plan_kind_for`，是（中英混写的）关键词命中表，命中任一就判 complex。归属我**不能**证明是我单独定的——它就在我做 workspace 路由那段代码里，但我拿不出「作者是我」的独立证据。误判成 complex 的后果：因为 planner 是 None，请求会命中 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND` 被挡——用户看到的是被拒/block 的准入结果，不是降级回答。

第二层：

- 表：`("compare","across","conflict","multi-hop","multihop","analyze","synthesize","报告")`——只有「报告」是中文，其余英文。
- 误判代价是 fail closed（拒），比 fail open 安全；可用性代价是「多问一句也做不了」。
- `事实层`: Current（表存在）+ Unknown（作者）
- `证据`: `simple_agent.py:2150`
- `边界`: 具体用户可见文案（block 在 UI 上长什么样）我没核实——`admission_reason` 是机器 reason，UI 呈现未证明；作者归属标 Unknown。

## A106

确定性的，不是随机。`idempotency_key` 形如 `idem:{tenant}:{workspace}:{run_id}:{step_run_id}:{tool_name}:{salt}`，而 `salt` 由调用方按动作身份传：`simple_agent.py:215-218` 传的是 `salt=str(getattr(binding,"name","") or resolved_tool_id)`，默认 `""`。所以 key 由动作身份（binding 名 / tool id）确定，不掺随机量。

第二层：

- 定义在 `mcp_tool_executor_adapter.py` 的 `idempotency_key(self, *, tool_name: str, salt: str = "")`；调用点 `:135-137`。
- A12/A93 把「随机 salt 破坏幂等」当风险讲——该风险不成立，收回。
- `事实层`: Current
- `证据`: `mcp_tool_executor_adapter.py`（`salt` 默认 `""`）；`simple_agent.py:215-218`
- `边界`: 真风险不在 salt，而在 key 的其他分量（见 Q107）。

## A107

前提不成立——salt 是确定的（Q106）。但**真正**的幂等边界在 key 的其他分量上：key 里含 `run_id` 和 `step_run_id`。这意味着：(1) 同一 step run 内，两次同工具、同 salt 的调用会**撞同一个 key**（过度收敛），即使逻辑上是两次不同调用；(2) 整个 run 重跑时 `run_id` 变了 → key 变了 → **不会**命中上一轮的 receipt——这才是「retry 漏掉既有 receipt」的真实来源，不是 salt。

第二层：

- 今天兜「重发」的机制是「同一 step run 内 key 稳定」；跨 run 重发靠的是别的（上层不去重发 / 显式 reconcile），不是这张 key 自己认旧 receipt。
- `事实层`: Current（结构判断）
- `证据`: `mcp_tool_executor_adapter.py` key 模板含 `run_id`/`step_run_id`
- `边界`: 我没审计跨 run 重发路径上「谁去查旧 receipt」，那半段标未证明；同 step 撞 key 的触发场景我也没造过测试。

## A108

那是**测试夹具名**，不是线上命名形态。`qa-` 前缀加数字后缀是合成的。它测的是 `_canonical_mcp_target("qa-mcp-461126") == "qa-mcp-461126"`——即「已经规范的输入不再被二次改写」（无双重归一）这条分支。

第二层：

- `_canonical_mcp_target` 在 `simple_agent.py:2702`。
- 与线上命名规则的关系：我只能说它模仿了「注册型 id 形态」，线上 MCP server 名的确切生成规则我**没核实**。
- `事实层`: Personal Ownership（我加的断言）+ Unknown（线上命名规则）
- `证据`: `simple_agent.py:2702`；测试断言字面
- `边界`: 该断言证明「已规范名不变」，不代表线上命名被验证；命名规则标 Unknown。

## A109

那两个能力（`get_file_content` / `list_skill_files`）随 `skill_agent.py` 一起退场了，**没有**被我重新挂到别处。skill 变成 guidance-only 工具——返回指引文本，不再有一个能读 skill 文件的子 Agent。

第二层：

- 删的是 `mcp_agent.py`(−120) 与 `skill_agent.py`(−263)。
- 所以「读 skill 文件」这条能力今天在 live path 上是一个**缺口**，不是被等价承接。
- `事实层`: Personal Ownership（删除）+ 缺口
- `证据`: 删除记录；无等价承接的直接证据
- `边界`: 我没把等价读文件能力作为 governed binding 重新暴露。今天建议：若还需要「读 skill 文件」，作为受管 tool 重新引入，而不是恢复子 Agent。

## A110

简历那句指的是 **4 月那版**形态，不是今天的。今天 Runtime 是 Single Controller + governed binding：单个 controller 在做，不再是「自由 ReAct 遍历所有工具」。所以「单 Agent」在「没有多 Agent 扇出」意义上今天仍成立；「Tool Calling」作为 4 月那种自由机制，已经不是 live 形态。

第二层：

- 今天的调用是受管 binding（`execute_binding_tool`）而不是 ReAct 循环。
- 简历措辞今天更准确的说法是「单 Controller + 受管工具绑定」。
- `事实层`: Historical（4 月）+ Current（今天形态）
- `证据`: `simple_agent.py:160-229`；A7/A75 的三件 delta
- `边界`: 「单 Agent」我保留（今天仍不指多 Agent）；但把「Tool Calling」当今天的机制会误导。

## A111

拆开算：**暴露 + 注参**这一件今天是 live 且被测的（`execute_binding_tool` 按 Tool–Server 映射注入用户配置）；**准入**这一件，规则本身在跑（route hint + plan kind + governed tool 解析都执行），但复杂分支因为 planner 未绑定而**终止于 block**，不是「放行进 ReAct」。所以 4 月那段的存活率是：注参/暴露 ≈ 存活；「复杂 → ReAct」只作为「会拒」的闸门存活。净：三件里约一件半在跑。

第二层：

- 我给不出百分比，只能给机制级判断。
- `事实层`: Current + 我的历史表述
- `证据`: `execute_binding_tool`（`simple_agent.py:160-229`）live；`DYNAMIC_PLAN_RUNTIME_NOT_BOUND`（`single_controller_runtime.py:818`）block
- `边界`: 「存活率」是机制级估计，不是量化指标，别当数字读。

## A112

用 **deepseek-v4-flash**。`a25c95a2`（2026-06-20 15:12，`Align multihop eval profile with DeepSeek default`）把受版本管理的 profile 里 `conversation_model` 从 `qwen-plus` 改成 `deepseek-v4-flash`，而这个提交是 audit `7928df50`（17:04）和 rerun `3da5d742`（17:23）**共同**的祖先；audit 比较的两个输入 `hotpotqa_baseline_rag_limit5_calibrated.json` / `hotpotqa_local_graphrag_limit5_calibrated.json` 来自对齐之后跑出的 `c3d06da3`（16:26），rerun 里也记着 `conversation model: deepseek-v4-flash`。所以 audit 和 rerun 都是 deepseek。

第二层：

- 那条 commit message 里「previous HotpotQA limit=5 real runtime smoke 早于这次 profile 对齐，summary 仍反映 qwen-plus」说的是**更早的一次 smoke**，不是这次 audit。
- `事实层`: Historical
- `证据`: `a25c95a2`（profile `qwen-plus`→`deepseek-v4-flash`）；audit `7928df50`；rerun `3da5d742`（记录 deepseek）；输入来自 `c3d06da3`
- `边界`: 这是从 commit 元数据 + 受管 profile/产物重建的结构判断；audit 本身是「对两份 json 做比较的报告提交」。若有更早、未进版本管理的运行，我核不到。

## A113

按 Q112，audit 和 rerun **同为 deepseek-v4-flash**，所以「换模型」这个解释在 audit→rerun 这一对上**不成立**——这一条我能排除。但剩下那部分我**不能**干净地归给 fusion 修复：两轮之间 baseline 自己的数字也在飘（MRR@10 0.90→1.00、Recall@2 0.70→0.90、avg latency 12148.21→16064.76 ms），baseline 代码没改却变了，说明是样本/环境波动或进程内非持久化索引带来的噪声；而且没有 leave-one-out，只有一次 rerun。所以：能排除「换模型」；不能证明「就是 fusion 修复」。

第二层：

- 归因结论：local 0.80→1.00 里有多少来自 fusion、多少来自运行噪声，**今天不可分离**。
- `事实层`: Historical + Unknown（归因）
- `证据`: 同上三个 sha + 两轮 baseline 数字
- `边界`: 这是本轮最高价值题：我给的是「排除哪一条 + 不能证明哪一条」，不是「我修好了 0.80→1.00」。若要我给单因归因，我做不到——需要 H1 逐臂 ablation。

## A114

因为把这两件事连起来讲**本来就是错的**——audit 和 rerun 同模型（Q112），根本没有「跨轮换模型」发生在这一对上。A19 说的「换过模型」指的是**更早的历史**（更早那次 qwen-plus smoke vs 后来 deepseek 的运行），不是 audit→rerun。所以我在 Wave 1 的错误是**没给「换过模型」加范围限定**，让 A19 读起来像在解释 audit→rerun。baseline 0.90→1.00 的真实解释是：同一 baseline、同一模型、数字却变了 ⇒ 样本/环境波动。

第二层：

- 修正 A19/A84：模型变更的陈述限定在「更早 smoke vs 后续运行」；audit→rerun 同模型。
- `事实层`: Historical + 我的表述错误
- `证据`: Q112 的三个 sha
- `边界`: baseline 波动我只能说「同代码同模型数字不同」；具体机制（latency 抖约 30% 说明环境也变了）我没进一步查。

## A115

那个 1.00 是**全配置**结果，不是单机制结果——rerun `3da5d742` 排在 fusion → seed → alias → path 之后，所有机制都在里面。所以「同日 rerun 不再低于 baseline」证明的是**这个组合**在那 5 条 query 上 ≥ baseline，**没有**证明是哪个机制做的。「同日」成立：audit 17:04 与 rerun 17:23 同一天、隔 35 分钟。

第二层：

- 归属：无 ablation，结论范围就是「组合」，拆不到单机制。
- `事实层`: Historical
- `证据`: `3da5d742`；audit `7928df50`
- `边界`: 7 个机制提交是否全在同一天，我没逐条核实日期，不硬说；结论能证明的是「bundle ≥ baseline」。

## A116

是「**没做**」，不是「做不了」——A21 那次是口径移动，我收回。真相：ablation / holdout 在 6 月是我**未执行**（我的缺口）。`BLOCKED_PENDING_DATA` 来自一个**更晚的治理产物**（`docs/governance/rb019-graphrag-ablation-protocol.md`，来源 round `rb-2026-09-15-formal-019 / IMP-019-05`，frozen 2026-10-07，owner 03+09）——那不是我写的，也不描述我 6 月的状态。`data/evals/multihop/` 不存在、本机连 HotpotQA 源 TCP 超时是**今天**让它 blocked 的事实，但不是 6 月未执行的原因。

第二层：

- 区分：`没做`（6 月，我的）vs `今天阻塞`（协议层，后来的、非我的）。
- `事实层`: Historical（我的缺口）+ 后来治理产物（非我）
- `证据`: 协议文档的 round 来源/frozen_at/owner；`data/evals` 与 `reports/evals/multihop/real_runtime/` 实测不存在
- `边界`: 用后来的冻结协议把我自己的缺口包装成外部阻塞，是这道题我 Wave 1 最该收回的地方。

## A117

会，而且这是我和 A17 的**真矛盾**。`_apply_genealogy_guardrail`（`fusion.py:877`）字面上做 `selected[weakest_index] = candidate`（`:922`），并返回 `final_top5_floor_preserved = (promoted_candidate is None)`——**恰好**在它晋升候选时 `floor_preserved=False`。也就是说这个 guardrail **故意**在 comparison/bridge/genealogy 三类 query 上覆盖 baseline rank 下限。

第二层：

- 两个机制在代码上不互斥（一个在排序阶段，一个在排序之后），但作为「全局不变量」的表述互斥。
- `事实层`: Current
- `证据`: `fusion.py:756/815/877`；`:922` 的 `selected[weakest_index]=candidate`；返回 `final_top5_floor_preserved`
- `边界`: A97「硬替换 top」和 A17「baseline-preserving 不变量」不能同时当全局真理讲——要收回的是 A17 的「全局」二字。

## A118

只在**排序阶段**成立，在最终输出上不成立。baseline-preserving 的下限体现在排序键里的 `_baseline_rank = min(vector_rank, bm25_rank)`（`fusion.py:190`）；而三个 guardrail 是排序**之后**的覆盖，能把候选抬到下限之上。所以在 guardrail 命中的 query 类上，最终输出可以是「比 baseline 差」的——这是有意的赌注（赌那几类上 graph 证据更好）。

第二层：

- 结论：不是全局不变量。
- `事实层`: Current
- `证据`: `fusion.py:190`（排序键）；`:877`+`:922`（guardrail 覆盖）
- `边界`: 修正 A17：应说「排序阶段不劣于 baseline，guardrail 类上按设计可以牺牲这条」。

## A119

手定，无 calibration，我指不到每个阈值对应的具体失败形态。`GRAPH_PROMOTION_THRESHOLD = 6` 在 `fusion.py:9`；`_candidate_group` 里的 `signal>=6` / graph-only `signal>=9` 在 `:166`。这些是调融合时定的调参常数，唯一反馈是那 5 条 query 的 smoke。诚实说：更接近「拍的 + smoke 试出来的」，不是从具体失败反推、也不是校准出来的。

第二层：

- `事实层`: Current（常数）+ 无来源证据
- `证据`: `fusion.py:9,166`
- `边界`: 「从哪条失败反推」——我给不出，标无直接证据。

## A120

这是弱点，说得对。`_graph_signal`（`fusion.py:157`）= `graph_support_count + graph_seed_hit_count + graph_file_focus + graph_path_count`——把四个语义不同、量纲不同的计数器**等权整数相加**再比 6/9。它假设这些计数可通约、等权，实际不是（一个 path 信号 ≠ 一个 support 信号）。后果：阈值不可解释，多个弱信号叠加也能凑到晋升阈值。

第二层：

- 当时理由：要一个标量来 gate，最简单。
- 今天建议（非当年实现）：分信号各自设阈，或先归一化再合。
- `事实层`: Current + Open Design
- `证据`: `fusion.py:157,166`
- `边界`: 这条是「今天会改」的建议，不是当时已实现；我也没有 ablation 证明分开设阈一定更好。

## A121

没有。`_score_path`（`retriever.py:426`）返回 6 元整数元组，权重手定，验证只到单测——在跑 HotpotQA 之前**没有**做过任何一次人工排序对齐。所以这 6 个权重是「推出来的」，不是「对出来的」。

第二层：

- 分量进入 `-chain_score`/`-graph_tier`/`-graph_signal` 这些排序键。
- `事实层`: Current + 无对齐证据
- `证据`: `retriever.py:426`；`fusion.py:952-977` 排序键
- `边界`: 我给不出对齐记录，因为没有。

## A122

是。**唯一有记录**的收益就是「全配置 ≥ baseline」那条 5-query smoke。我举不出任何一个「删掉图路由会变差」的 query，也没有「图路由救回了 baseline 漏掉的文档」的记录。所以这层唯一的已记录收益是**非劣**——而非劣用「图权重 0」这个平凡配置也能拿到。这正是我 A68 说要先测融合/guardrail 复杂度是否值钱的原因。

第二层：

- `事实层`: Current + 证据缺口
- `证据`: 只有 5-query smoke；无正向增益记录
- `边界`: 「收益为零」我限定为「**已记录**收益为零」——不是断言绝对无收益，是断言没有证据说有。

## A123

因为整套机制是对着 **HotpotQA（英文多跳 QA 数据集）** 建的，那是当时唯一可用的评测面。于是英文评测的关系词汇**渗进了领域词汇**：`GENERIC_ENTITIES = {Introduction, Overview, Objectives, Objective, History, Roadmap, Examples, Example, High, Low, Medium}`（`graphrag/entity_alias.py`），以及 `founded by` / `maternal grandfather` / `director of` 这类 cue 全是英文（`retriever.py:59,68` 的 `BRIDGE_RELATION_CUE_PATTERN` / `GENEALOGY_RELATION_CUE_PATTERN`）。对一个天津法院中文卷宗平台，这是**域不匹配**：seed/guardrail 逻辑按中文卷宗里不会出现的英文关系词来 gate。

第二层：

- 根因：评测来源（HotpotQA）被直接泛化成了域词汇。
- `事实层`: Current（词汇）+ 我的机制选择
- `证据`: `entity_alias.py:10-40`；`retriever.py:59,68`
- `边界`: 我没为中文域重建这套关系词表；这是根本性的域适配缺口。

## A124

没有。一次都没有——系统的目标域（中文法律语料）上从没跑过，连人工看结果都没有。唯一的运行是那 5 条英文 HotpotQA smoke。所以「已知中文法律主体上有误合并风险」这件事本身都只是**推断**（因为 `GENERIC_ENTITIES` 和别名归一化按英文建的），不是实测到的。

第二层：

- `事实层`: 目标域零验证
- `证据`: 无（连一次运行记录都没有）
- `边界`: 我明确说：这套检索在目标域上的验证是**零**。

## A125

共同点**很少**，不足以支撑复用。`Ed Wood`（电影）/`Shirley Temple`（人）是开放域多跳 QA 里的命名实体；法院卷宗主体是公司、法人、案号——结构化、有的还是数字型标识（案号）。案号是精确匹配标识，别名归一化不但不必要还有风险；公司名才是别名误合并（Q124）真正咬人的地方。所以「同一套 seed/路径机制复用」是**假设**，不是被证成的事实。

第二层：

- 机制为开放域命名实体多跳设计；迁移到法律命名实体没有证据支撑。
- `事实层`: Open Design + 假设
- `证据`: `5a8b57f2…`/`5a8c7595…`；`entity_alias.py`
- `边界`: 我举不出法律域上的同类失败，因为没测过。

## A126

我给不出可信的生产量级。15806→18503 ms 是**进程内、非持久化、单机、5 条 query** 的数字，还包含图重建；它不外推到「有持久化图存储、并发负载、不同 top_k」的生产路径。要给估计，至少要知道生产图存储的 p50/p99 查询时延和路径展开次数——这两个我没有。所以：没有可靠的生产估计；smoke 只能界定**形状**（图工作主导时延），不能界定**量级**。

第二层：

- `事实层`: Unknown（生产量级）
- `证据`: 只有 `local_graphrag` 15806→18503 ms 的 smoke
- `边界`: 不给数——制造量级估计就是这个项目最严重的失败模式之一。

## A127

真实路径是 `core.py`。live path 是 `agent/runtime/nodes/core.py:62-120` 的 `build_context` → `:79` 调 `build_context_pack(scope=...)`。`prepare_context` **只作为一个节点名存在**：`harness.py:269` 的节点契约列了这个名字，`runtime_batch.py:499-516` 的 `_validate_controller_harness` 要求正是那 10 个节点名，`durable_runtime.py:416-424` 对 `"prepare_context"` 节点的 `_execute_node` 只是合并 `context_pack`。所以 A28 说的 `GeneralAgent.prepare_context()`——那个**对象**错了；和 ContextOrchestrator 一样，名字在、不是 live 调用点。

第二层：

- 修正 A28：机制（调用前读 + 回合后写）是真的，但它的家在节点/core 层，不是一个 `GeneralAgent` 类的方法。
- `事实层`: Current + 我的表述错误
- `证据`: `core.py:62-120,79`；`harness.py:269`；`runtime_batch.py:499-516`；`durable_runtime.py:416-424`
- `边界`: 我 Wave 1 用 `d4e2fe2` 这个 sha 去指 `GeneralAgent.prepare_context()`——对象命名错，收回。

## A128

简历第 4 条描述的是**真实那条节点链**：`build_context` 节点（读，经 `build_context_pack`）+ `post_turn_commit` 节点（`core.py:391`，写）。这两个**节点名**确实在 live controller harness 契约里。所以第 4 条讲的行为（调用前读、回合后写）方向是对的，是我在 A28 把集成点点名点错了。

第二层：

- `事实层`: Current
- `证据`: `core.py:79,391`；`harness.py:269,333`
- `边界`: 我应把第 4 条的归属明确写成 core.py 的 build_context + post_turn_commit，而不是 `GeneralAgent.prepare_context`。

## A129

归属上我只能说：它是**更早的遗留抽象**（带 typed contracts + scope），今天在 `src/` 里**没有 production call site**——它是不是本轮产物，我没证据说是本轮做的。如果重做：**删掉它**，把 scope 语义留在 live path 上（`build_context_pack(scope=…)` 本来就带 scope）。把它挂到真实入口只会给同一套语义再开一个入口，不值得。

第二层：

- `事实层`: Current（无 consumer）+ Unknown（归属/时间）
- `证据`: `src/` 无 consumer；`core.py:79` 的 scope 已存在
- `边界`: 我拿不出「它当初为什么被建、谁需要它」（同 Q175），那部分标 Unknown。

## A130

runtime 侧 `core.py:485-491` 把 `agent_id` 硬编码成 `"agent_run"`——所以 `MemoryScope` 的 **agent 维今天是常数**，不区分任何东西。其余维度（user/workspace/tenant 等）仍然带真值、仍有区分力。所以简历说的「作用域」剩下来的是那些真被穿透的维；agent 这一维是个 stub。

第二层：

- 我不报「四维里剩三维」这种精确数——我报机制：agent 轴被塌成常量。
- `事实层`: Current
- `证据`: `core.py:485-491`
- `边界`: 具体几个维度在具体调用点带真值，我没逐点审计。

## A131

stale 状态是**方法调用写的**，不是后台写的。没有 reaper，状态迁移（激活、review 等）靠调用方显式发起——所以「新鲜度」依赖调用方**自觉**去调那次迁移；调用方不调，就没有任何东西把它标 stale。它不是同步自动刷新。

第二层：

- 激活路径是显式的 `SELECT ... FOR UPDATE` + CAS（`domain.py:301/315`）。
- 刷新归属 = 调用方，不是调度器。
- `事实层`: Current
- `证据`: `domain.py:301/315/353/363-364`；无后台 reaper
- `边界`: 我没审计「哪些调用方漏了这次迁移」——那会是一条真 bug 清单，我没做。

## A132

会——点名的那个反模式**是可能的**。写入在 `post_turn_commit` 一个 UoW 里做；失败时只置 `memory_persistence_unavailable`，**run 本身不因此被判失败**。所以「run 看起来成功、记忆静默丢了」在这个设计下是成立的风险。这个 flag 有没有被冒泡到用户面/告警面，我没有证据说它被冒泡了。

第二层：

- 今天建议（非当年实现）：要么让 flag gate run 的成功态，要么把它冒泡成可观测事件。
- `事实层`: Current + Open Design
- `证据`: `core.py:391` post_turn_commit；`memory_persistence_unavailable`（无冒泡证据）
- `边界`: 我没读遍所有失败分支，只确认这条语义缺口存在。

## A133

是**各自独立走到 APPROVED**。review 状态是**逐行**的（`memory_runtime.py:69` `review_status` 默认 `"pending"`），代码里没有一步「把两条冲突候选并排摆给 reviewer」的仲裁。所以两条内容冲突的 memory 可以各自独立通过 review，reviewer 不会自动看到它们「并列」——我没有那样的界面/逻辑。

第二层：

- `事实层`: Current
- `证据`: `memory_runtime.py:69`；无冲突仲裁/并排呈现
- `边界`: 「reviewer 是否凑巧一起看到」取决于 UI，我没核实 UI。

## A134

就我能核的：它**没有被记成一条待办**——今天实际生效的就是 scope + APPROVED。recall eligibility 属 08 但没接上，这个缺口在我能看到的范围里是**放着**的 Gap，不是排了期的事。

第二层：

- `事实层`: Current + Unknown（是否有 issue 条目）
- `证据`: 无待办/issue 的直接证据
- `边界`: 我没法穷举 issue tracker，所以「没被记」是「我没找到」的强度。

## A135

不是我起草的。ADR 0007 是项目的决策记录，里面的 memory kill-test 阶梯是**那个决策记录的内容**，不是我写的草案，也不是从框架文档搬的——归项目/团队。我是把它当**判据**引用。

第二层：

- `事实层`: Unknown/非我（Ownership）
- `证据`: ADR 0007 存在；作者归属无我证据
- `边界`: 我不认领这条判据的作者身份。

## A136

那些数是 **PR #8 描述里记的**，不是我在答题时重跑出来的。它们锁的行为类别是 memory readback：scope 过滤、仅 APPROVED、source trace / provenance 约束（即读回资格规则）。我能确认的是**类别**，不是「32 条逐条覆盖了什么」——后者我不重跑就报不了。

第二层：

- `事实层`: Historical（PR 记录）
- `证据`: PR #8 描述（32 focused / 66 repo / 11 legacy / 三 profile contract eval ok）
- `边界`: 我不把这些数说成「我现场跑出来的」；逐条覆盖范围我未核。

## A137

没有。我找不到任何一次**人工使用** structured memory 的记录——没有使用痕迹，只有测试和 PR 记录。所以按 A36/A76 那条「没有稳定边际收益就关」的判据，它今天的状态是：**连使用证据都没有**，这本身既是「倾向删」的信号，也是「删之前先上 telemetry」的理由。

第二层：

- `事实层`: 无使用痕迹
- `证据`: 无（无 telemetry / 使用记录）
- `边界`: 「没有记录」≠「没人用过」——但按可核标准，我只能报「无记录」。

## A138

收回「ACTIVATED」。真实情况是**两个**代码枚举 + 一个文档词，而且两个代码枚举**互相不一致**：`agent/domain/task_contracts.py:38-42` 是 `PlanVersionStatus = DRAFT/ACTIVE/REJECTED/SUPERSEDED`；`agent/runtime_batch.py:104` 是 `PlanVersionRecord.status: Literal["DRAFT","VALIDATING","ACTIVE","SUPERSEDED"]`；`ACTIVATED` 只出现在文档里，**不在**任何一个代码枚举里。所以 A38 的 `ACTIVATED` 是我把文档词当代码枚举背了。`VALIDATING` 是谁加的，我没有证据。

第二层：

- 两个枚举的差异：一个用 `REJECTED`，一个用 `VALIDATING`。
- `事实层`: Current（两个枚举）+ 我的表述错误
- `证据`: `task_contracts.py:38-42`；`runtime_batch.py:104`
- `边界`: 我拿不出 `VALIDATING` 的作者；「哪个是真的」——两个都是真的，只是属于两套类型。

## A139

设计意图是**各 Owner 比**：PlanVersion 只冻结「运行因果」，tool/prompt/model 版本各自归它们的 Owner，Runtime 不替它们比。但「这个比对今天**被实现并被谁调用**」——我没有一条 live 比较器指向它，所以实现度标未证明。

第二层：

- `事实层`: Target（设计）+ Unknown（实现）
- `证据`: `task_contracts.py:345` PlanVersion frozen；无 live comparator 证据
- `边界`: 我不把「Owner 比」说成今天已在跑。

## A140

代码里那一支是 **REJECT**。`planning/recovery.py:137-149`：当 `incoming_execution_epoch < active_execution_epoch`（epoch 旧了）返回 `REJECT_LATE_RESULT`；`:132` 另一支是 `RECONCILE_CHECKPOINT`（domain generation 领先 checkpoint 时）。所以「纯计算但基于旧材料」的晚到结果，按实现的这一支是**拒绝**，不是重算——重算属于重新准入的决策，不归这个比较器。

第二层：

- 注意：这些分支**没有非测试调用方**——所以它是「代码里的分支」，不是「已被接线的行为」。
- `事实层`: Current（代码分支）+ 未接线
- `证据`: `recovery.py:132,137-149`
- `边界`: 我说的是「代码怎么分支」，不是「生产今天这么跑」。

## A141

不共存为「两套活 checkpoint」。canonical 是 `agent/runtime/graph.py:14-75`：`build_agent_graph(dependencies, checkpointer)`，docstring 明说这个 `checkpointer` 是「Zuno 的 domain checkpoint bridge，不是 LangGraph `BaseCheckpointSaver`」，它调 `checkpointer.persist_node/persist_interrupt/complete`（`:82-95`），`graph.compile()` **不**带 checkpointer。官方 `PostgresSaver` 只在 `agent/runtime/phase08.py`（`phase08_postgres_checkpointer`、`build_phase08_test_checkpointer`→`InMemorySaver`），**没有 production caller**（只在 `agent/runtime/__init__.py` 被 re-export）。所以 runtime 恢复实际读的是 Zuno domain bridge；官方 PostgresSaver 是未接线的。

第二层：

- `事实层`: Current
- `证据`: `graph.py:14-75,82-95`；`phase08.py`；`agent/runtime/__init__.py`
- `边界`: 「两套同时存在」是代码面存在，不是运行时并存。

## A142

我拿不出「某个节点真为这条约束拆过」的证据——它是**约束陈述**，不是已落地的事实。而且这条约束的实际咬合面被 Q141 限住了：`interrupt()` 是官方 saver 路径的语义，而官方 saver 未接线。

第二层：

- `事实层`: Target/约束 + 未落地
- `证据`: 无节点拆分证据；`phase08.py` 未接线
- `边界`: 不把约束说成实现。

## A143

是**文档里的顺序**。我没有一个单一恢复例程函数能指给你看它按这个次序执行。组件都在（02 receipt、06 effect、08 授权重校各自存在），但「合成一条按此顺序跑」这件事，实现度标未证明。

第二层：

- `事实层`: Target + 实现未证
- `证据`: 各组件存在；无单一编排器
- `边界`: 我不把文档顺序说成代码执行顺序。

## A144

停在设计。**没有**真的拿一个通用 Agent Host 跑过哪怕一次对照。所以「为什么自研」这个论证靠的是设计推理，不是一次运行。

第二层：

- `事实层`: Target/设计 + 未执行
- `证据`: 无对照运行记录
- `边界`: A/B/C 的 A 臂从未被实测。

## A145

是**为必要性论证构造的例子**，不是真实发生过的那次 case（真发生过我会说「我把当时的 case 拿来」）。所以我该把它标成「举例说明」，不该让它听起来像 incident。

第二层：

- `事实层`: 构造示例
- `证据`: 无
- `边界`: 收回把它讲得像真实 case 的口气。

## A146

第一次调用在 `capability/tool_runtime/invocation_gateway.py:388`，第二次在 `:462`（两处都是 `_reauthorize_execute_epoch` 调用点，定义在 `:1260`）。A46 只列了 `:462`——那是 A46 的**遗漏**，不是第一次调用在别处。

第二层：

- `事实层`: Current + 我的遗漏
- `证据`: `invocation_gateway.py:388,462,1260`
- `边界`: 修正 A46：调用序列漏了 `:388`。

## A147

**今天没人触发**。`escalate_due_reconciliations`（`invocation_gateway.py:1607`）在生产里**没有调用方**——只有测试调它。所以那个 900 秒阈值：不是请求驱动、不是 cron、不是运维手工——它是「实现了但没驱动」。这就是缺口。

第二层：

- `事实层`: Current（无驱动）
- `证据`: `invocation_gateway.py:1607`；仅测试调用
- `边界`: 这个「无人驱动的时间阈值」今天等于不生效。

## A148

收回「今天跑起来的」这个暗示——`record_manual_effect_assessment`（`:1787`）在生产里也**没有调用方**，所以它今天没在跑，身份问题在「没有 caller」面前是悬空的。它的签名**要求** `assessor_principal_id`、`evidence_payload` 等——但「真实的、受策略约束的 reviewer 身份由谁供给」未证明，因为**没有谁供给**。

第二层：

- `事实层`: Current（未接线）
- `证据`: `invocation_gateway.py:1787`；仅测试调用
- `边界`: 我把「未证明的身份绑定」修正为「未接线的功能」。

## A149

今天是在**工具执行层停**，不是一个 Run 状态机停。`capability/runtime.py:700-745`：当 `reconcile_required`/`async_waiting` 时，置 `gateway_effect_certainty="UNKNOWN_EFFECT"` 并返回 `ToolRuntimeExecutionResult(..., status=gateway_status, security_decision=SecurityDecision.BLOCK.value)`。所以**工具执行被 BLOCK 并返回 blocked 结果**；`WAITING_RECONCILIATION` 这个 Run 级状态机在 src 里**不存在**（那个字面只出现在 `docs/modules/runtime/reference.md`）。

第二层：

- 「设计上停」是 Target；「今天停」= 工具层 BLOCK，不是 Run 停。
- `事实层`: Current
- `证据`: `capability/runtime.py:700-745`；`docs/modules/runtime/reference.md`
- `边界`: 我修正 A48 的含糊处：停发生在工具层且是 BLOCK 语义。

## A150

最坏状态是**「远端真的执行了、但系统只报 blocked/unknown」**这个背离。AUD-L1 已验的是「强制审计先于效果」这条在**正常路径**成立；AUD-L2（crash/restart 生命周期）未证明意味着：在崩溃窗口里，系统**不能**证明「审计必先于效果」这个不变量穿过了重启。用户看到的是工具执行返回 `UNKNOWN_EFFECT` + `BLOCK`（Q149）——即「被拒/不确定」，不是静默的「done」。但如果远端 Provider 实际已执行，就会出现「效果已发生 vs 报告说 blocked」的背离，而**消解**这个背离要靠那个没驱动的 reconciler（Q147）。

第二层：

- 用户可见：blocked/unknown，不是假成功。
- 真正的坏：效果已发生但报告 indeterminate，且无人驱动对账。
- `事实层`: Current（BLOCK 行为）+ Unknown（AUD-L2 崩溃窗口）
- `证据`: `capability/runtime.py:700-745`；`invocation_gateway.py:1607`（无驱动）
- `边界`: 「AUD-L2 在真实 Provider 上触发会怎样」我按机制推，不是实测到的。

## A151

revoke 是**打在 gateway 内部的一个 fault seam 上，但它改的是持久化的 SecurityEpoch 行**——所以机制上它模拟的是「外部撤销」，注入点却是测试对 gateway 的 subclass。测试里的 `_RevokingAfterAuditGateway` 覆写了 `_persist_mandatory_audit_before_effect`：调完父类把审计写 durable 之后，直接用一条 `UPDATE security_effective_epochs SET status='revoked'` 把当前 epoch 置成 revoked。gateway 自己随后在 `_reauthorize_execute_epoch` → `validate_pre_effect_authorization` 里重读持久化 epoch，发现 stale 就 block，executor 调用 0 次。所以：**防线在产品里，触发是一个写库的测试 seam**。

第二层：

- 撤销动作不是走产品 API，而是测试进程直接 `UPDATE ... WHERE epoch_ref=... AND status='active'`，并 `assert updated == 1`——它刻意只影响一条 epoch，避免「撤销了别的东西」的假证据。
- 真正的校验点：`invocation_gateway.py:1264-1276` `_reauthorize_execute_epoch` → `platform/security/persistence.py:1045` `validate_pre_effect_authorization`；两次调用点在 `:388`（approval 之后）与 `:469`（durable audit 之后、dispatch 之前）。
- 这个 probe 与 `PRE-EFFECT SECURITY EPOCH REVOCATION: PASS` 这条 evidence 对应。

- `事实层`: Current（防线已验证）；测试 seam 是测试构造
- `证据`: `tests/security/test_mandatory_audit_postgres_boundary.py:825-844`（`_RevokingAfterAuditGateway`）、`:848` 起的 `test_security_epoch_revoked_after_audit_still_blocks_provider_send`、断言 `executor_calls == []`；`invocation_gateway.py:388,469,1264-1276`
- `边界`: 我没有证据证明**产品里存在一个真实的「撤销 epoch」入口**被端到端跑过。这个 probe 证明的是「epoch 变化时 send 前会拦住」，不证明「谁能撤销 epoch、走什么审批」。

## A152

不是我设计的。九模块的 authorization 划分是**团队后来系统化的 ADR**——`docs/decisions/0007-reuse-first-provider-boundary.md`，status `accepted-target`，decision_date `2026-08-12`，在里面九个逻辑责任域各有 owner。我做 effect 那段时，落到代码里的是「executor 只执行、security 判定」这条**局部**实现约束，不是那套 owner 表。

第二层：

- 时间上不可能是我定的：我做 Tool/MCP 是 4 月（PF-032），ADR 0007 是 8 月，且是 team-authored。
- 我做 effect 时的实现事实：模型/Runtime/Tool 都不能自己放宽授权——`invocation_gateway.py` 里授权判定一律回到 `SecurityUnitOfWork` 读持久化 decision 与 epoch，调用方传进来的 `approval`/`security_decision` 只是**引用**，不是权限本身（`validate_pre_effect_authorization` 要 `decision_id` + `prepared_action_hash` + `require_approved_request`）。
- 这些是对 ADR 语义的**局部服从**，不是它们的**设计者**。

- `事实层`: 团队/架构（ADR 0007，2026-08-12）；个人（局部实现约束）
- `证据`: `docs/decisions/0007-reuse-first-provider-boundary.md`；`invocation_gateway.py:1264-1276`；`platform/security/persistence.py:1045`
- `边界`: 我不认领那套九模块 authority 划分的设计。而且 ADR 0007 自己是 `accepted-target`，不是「历史当时就这么实现的」。

## A153

3 月到 4 月 15 日之间，我**在公开历史里拿不出任何东西**——因为根提交 `eafeb1c2`（2026-04-15）就是公开历史的起点，在那之前没有我可以复核的 artifact。我在那段做的事只能落到「参与过」这一级：PF-010 明确说我参与过 Memory 相关第一批重要工作，PF-011 说我参与了 OpenViking 在 Memory/Context 区域的接入——但 PF-011 的 artifact 到今天**没有恢复**。所以公开历史看不到，不是「做了但没提交」，而是**我无法证明那时做了什么**。

第二层：

- 加入时间是 PF-007（USER_CONFIRMED，约 2026-03）；根提交是 2026-04-15——中间这段是「用户回忆」而不是「材料可核对」。
- 公开历史到 2026-04-29 快照，`memory/client.py` 仍是同一 blob，也没有 `viking`/`openviking` 路径——所以 OpenViking 那段不在公开快照里。
- 另一种可能是存在未推送/本地/私有分支（这是 PF-011 明说的升级路径），但那是**假设**，不是证据。

- `事实层`: Unknown（公开历史空白）
- `证据`: `docs/governance/project-fact-provenance.md` PF-007 / PF-010 / PF-011；根提交 `eafeb1c2`（2026-04-15）
- `边界`: 我不能把 3 月到 4 月 15 日写成「我写了 X」。「参与了 OpenViking 接入」是本人回忆，不是可复核实现。

## A154

**没有。** 4 月 15 日之前，我指不出任何一次能今天复核的代码、设计或文档。最早可自证的是 `77346758`（2026-04-15），和根提交同一天——所以「我第一笔改动」这种话我从来不用；A51/A52 的写法「这是我能自证的一笔」就是为了这条。

第二层：

- PF-011 的 OpenViking artifact 今天 `NOT_RECOVERED`；当前连接设备上也没有历史索引记的 `F:\internship-work\resume project\Zuno` 路径，未推送 refs 也查不到。
- 6 月那条 Context/Memory V2 链（PF-029/PF-030）**不是** 4 月之前的东西，不能拿来填这段空白——那是它自己的时间窗（2026-06-25/26 与 PR #8）。
- 唯一还能算「4 月 15 日之前状态」的东西，只能从 `77346758` 的**父提交**反读——那是「在我动手之前仓库长什么样」，不是我写的东西。

- `事实层`: Unknown
- `证据`: `77346758`（2026-04-15）为最早可自证；PF-011 `PUBLIC_GIT_NOT_RECOVERED`
- `边界`: 不升级、不脑补。「3 月我在做 Memory/OpenViking」保留在回忆层。

## A155

**我不知道当时的流程，而历史本身没有留下流程痕迹。** PF-032 写得很直白：`77346758` 没有关联 PR、没有 Review、没有历史 status check。一个删两个文件、重写主 Agent 绑定的改动直接进了 main——这是我今天能核对的**事实**；至于当时是否存在某种（没被记录下来的）评审约定，我**没有证据**。

第二层：

- `77346758`（2026-04-15）由我的 GitHub 账号 authored，但 author 字段区分不出个人与团队——所以这只能证明「这个提交在我的账号下」，不能证明「这个改动没人 review」。
- combined commit status 对这两个 SHA 都没有 recorded status check；也没有 PR-triggered Actions run 恢复出来。
- 所以能写的只有「tests were added / test artifact exists」，**不能**写「历史 CI 已通过」——这是 PF-032 明确划的界。

- `事实层`: Historical（无 PR/Review/status check）+ Unknown（当时流程）
- `证据`: `docs/governance/project-fact-provenance.md` PF-032 与「Tool Calling Strategy 取证边界」
- `边界`: 「为什么没走 PR」我不知道。我不编一个「当时团队约定直推 main」的解释。

## A156

简历只写了三条切片（Tool/MCP、GraphRAG、Context/Memory），切片之外我还能确认参与的有四条，都在台账里：**Memory 第一批重要工作**（PF-010）、**OpenViking 在 Memory/Context 的接入**（PF-011）、**数据库查看/调试**（PF-013）、**Agent 部分开发**（PF-009）；另外**开发期间学习/接触 LangGraph、GraphRAG**（PF-014）——这一条要小心措辞，它是**学习背景**，不等于我实现了现在的 GraphRAG。

第二层：

- 为什么没写进简历：PF-011 的 artifact 今天不可复核（写成简历条目会越过证据）；PF-013 是「看过/调试过数据」，不构成模块 owner；PF-014 更只是学习接触。
- 与我主动划的切片不同：切片是我**能证明**的三条；上面这几条是**参与过但材料不足**的。
- 所以「这三条之外我做过什么」的诚实答案是：做过但大多不可复核，且其中至少两条（OpenViking、DB）在当时就是**参与**级别而非 owner。

- `事实层`: Historical（USER_CONFIRMED 级参与）
- `证据`: `docs/governance/project-fact-provenance.md` PF-009/PF-010/PF-011/PF-013/PF-014
- `边界`: 这几条只能停在「参与过」，不能升格成「我负责」。

## A157

**几成是我的，我说不出来——只能给提取标准，不能给比例。** `0b5fb350`（2026-04-28）是跨工具/Knowledge/模型/Docker/脚本的大提交，PF-032 明确说**不能把整个 commit 归为 Tool Calling 个人任务**。我的提取标准只有一条：**有明确前后差异 + 有 regression test artifact 的路径**才算我这段。按这个标准能安全提取的就是 `WorkSpaceSimpleAgent` 里那几条。

第二层：

- 具体是：`_canonical_mcp_target()` 对自定义 MCP server name 的无限自递归修复（并加 `test_canonical_mcp_target_handles_custom_server_name_without_recursion`）；高德天气 direct route 从 `cleaned.replace("天气","")` 改成 `_extract_gaode_weather_city()`（并固定 direct route 到 `maps_weather(city="南京")`）。
- 「剩下的谁写的」——**我不知道**，author 字段区分不出个人与团队，我也没有当年的分工记录。
- 我给不出百分比。给百分比就是编数字。

- `事实层`: Historical（子集可证）+ Unknown（所有权比例）
- `证据`: PF-032 与「Tool Calling Strategy 取证边界」；`0b5fb350`
- `边界`: 只有「可安全提取的子集」这一级结论，没有「我写了 X%」。

## A158

**如果没人追问，我大概不会主动说这两条。** 说概率就是给自己留面子——真实情况是：30 分钟口语面试里，我大概率会先讲「我做了什么」，`ContextOrchestrator` 没有生产调用点、`KnowledgeGeneration` 在 src 里搜不到，这种**自曝空环**的话，我未必会自己开口。这正是这套材料存在的理由：它要防的就是「讲得漂亮但不真」。所以我把这两条**主动放在 A55/A78**，就是为了不依赖我临场自觉。

第二层：

- `ContextOrchestrator` 定义在 `platform/services/application/context/orchestrator.py:115`，`prepare()` 在 `:124`；grep 全 `src/` 只有 re-export（`agent/context.py`、两个 `__init__.py`），**没有生产调用点**（A55 已记）。
- 真实调用前读取路径是 `agent/runtime/nodes/core.py:64/79` → `memory_engine.build_context_pack(...)`（`memory/engine.py:645`）。
- `KnowledgeGeneration` 在 `src/` 里 literal **0 命中**（A78 已记），它只活在 `docs/modules/knowledge/README.md` 的 Target 段。

- `事实层`: Current
- `证据`: `orchestrator.py:115`；`core.py:64/79`；`memory/engine.py:645`；`docs/modules/knowledge/README.md`
- `边界`: 这一答是**自我风险评估**，不是事实陈述；我没有证据说「我一定会说」。

## A159

**我不知道为什么没有 ADR**，只能确认结果：`docs/decisions/` 里没有一条覆盖 direct-route 准入的决策记录，而 A56 记的 decision owner 到现在还是 Unknown。用一个会影响**所有请求分流**的规则、却没有决策记录——这是我今天回看时**最想改的一件事**：它应该是 ADR 而不是散在代码里的关键词表。

第二层：

- 现状：准入规则在 `simple_agent.py:2150` `_plan_kind_for`（`("compare","across","conflict","multi-hop","multihop","analyze","synthesize","报告")` 命中就 complex）和 `:2743` `_detect_route_hint`（关键词表）里——都是**代码即规则**。
- 对照：`docs/decisions/` 里的 ADR（如 0007）都是 team-authored、日期在 8 月，status `accepted-target`——它们**不覆盖** 4 月这条分流规则。
- 所以「为什么没有」我只能说 Unknown；「该不该有」是**今天的设计建议**：该有，而且要写清 owner。

- `事实层`: Unknown（缺失原因）+ 今天的设计建议
- `证据`: `simple_agent.py:2150,2743`；`docs/decisions/`（无对应 ADR）
- `边界`: 这条「应该补 ADR」是我今天的判断，不是「当时有人决定不写 ADR」的历史事实。

## A160

**它是流水线上最近的一次 main run，不是为面试专门跑的。** `docs/evidence/README.md` 里把它写成「最新 main run `35516807526`」，和它前面的 PSC-A（`35071244101`）、PSC-B（`35121830478`）、PSC-D（`35202465804`）是一串**逐次推进**的 selected run——走势就是「上一次的基础上再加一条 regression」，不是一次性为某个场合准备的。

第二层：

- 它是 **SELECTED CODE VERIFICATION**（`AVAILABLE @ 5eaeaf563d6c…`），不是 full CI——同一份 evidence 里 `FULL CI: NOT RUN / NOT ESTABLISHED`。
- 它覆盖的是**当前**被选中的 Domain / Citation / Application / Runtime / Knowledge / Capability / Tool / Model Gateway / Security / Observability / Retrieval / Eval 行为；本次新增的是 PRD-A2 的 stable `runtime_request_ref ↔ canonical task/run` binding 等。
- 它**不certify 4 月那条 Tool Calling 路径**：4 月的 regression test artifact 存在（PF-032），但没有证据说它们被纳进了这个 selected 集合。

- `事实层`: Current
- `证据`: `docs/evidence/README.md`（`SELECTED GITHUB RUN: 35516807526 / 224 passed, 32 warnings`、`FULL CI: NOT RUN`）
- `边界`: 我不能说这个 run「覆盖了 4 月的路径」。能说的是：它是当前 main 上最近一次的 selected 验证。

## A161

那句是**仓库的书面口径**，不是我为了保边界现编的。`docs/project/README.md` 里明确写「Commit 历史不能单独证明个人 Ownership」（2161 commits、author 字段区分不出个人与团队），并直接要求「任何『这是我的第一笔改动』式表述都应改写为『这是我能自证的一笔』」。我**采纳**它是因为它对我成立，但话不是我先说的。

第二层：

- 这条口径之所以可信度高：它是在**合同/项目材料层**写的，且有具体数字支撑（2161 commits），不是我一个人的免责声明。
- 它对我的具体含义：`77346758`/`0b5fb350` 是「我账号下的提交」，不是「我独占的改动」；所以我在 A51/A52/A157 里都只用「可自证」。
- **两者可以同时成立**：它是仓库口径，也是我真实遵守的边界——我不需要在诚实和一致之间二选一。

- `事实层`: 仓库口径（书面）+ 个人采纳
- `证据`: `docs/project/README.md`（「加入项目时，系统已经存在」「Commit 历史不能单独证明个人 Ownership」）
- `边界`: 我不是这句的**作者**。若问「谁写的」，我不知道。

## A162

对读简历的人，它提供的是**环境/阶段信息，不是结果信息**：它说明这套东西进过一个**真实评测环境**（客户侧 Demo、法院侧测试、Pilot），不是只在本地跑过。可验证的部分只有「到过这个阶段」这一级——PF-015/016/018/019 都是 `USER_CONFIRMED` 的阶段事实。

第二层：

- 反过来它**不能**提供：规模、题集、参考答案、reviewer 协议（PF-018 明确「未恢复测试规模、题集、参考答案和 Reviewer 协议」）、pass/fail 判据、任何效果数字。
- 我仍把它写进简介的理由：**阶段本身就是信息**——「在真实环境被使用过」和「没被使用过」是两个不同的项目质量信号；但我绝不把它写成「验收获通过」。
- 这条界线是 PF-020（Production `NO EVIDENCE / NOT ESTABLISHED`）的直接后果。

- `事实层`: Historical（阶段）+ Unknown（规模/判据/结果）
- `证据`: `docs/governance/project-fact-provenance.md` PF-015/016/018/019/PF-020
- `边界`: 简历里这一句的可验证信息量就是「到过 Pilot 这个阶段」，很薄。

## A163

**两者都成立，但要拆开：**「只写到 Pilot 为止」这个**写法**是我准备简历时定的选择；而它之所以必须这么写，是因为底下有一条**真实取证边界**（PF-020：Production 是 `NO EVIDENCE / NOT ESTABLISHED`、PF-019：Pilot 不等于 Production）。也就是说：边界是事实层的，措辞是我的。

第二层：

- 如果写成「已生产上线」会越过 PF-020；写成「Pilot 验证完成度 X%」会越过 PF-018/PF-019——两条都缺材料。
- 所以我选的不是「更保守的措辞」，而是**唯一没有越界的措辞**。这一点上我的自由度很小。
- 但「我选了停在 Pilot」这个动作是我的——不是谁要求我这么写的。

- `事实层`: 事实边界（PF-019/PF-020）+ 个人措辞选择
- `证据`: `docs/governance/project-fact-provenance.md` PF-019/PF-020
- `边界`: 我**没有**把它扩写成任何完成度或验收结论；也没有证据说明团队里有谁要求我这么写。

## A164

**我没在台账里提交过我能指认的条目**，而且维护方是谁我也说不上来。`project-fact-provenance.md` 是一份**治理层**文档（在 `docs/governance/` 下，和 ADR、freeze 材料同级），它的 PF 表是 round/owner 流程产出的，不是我个人的工作记录。PF-022（历史性能指标 `UNKNOWN`）就是没人能补上样本的条目之一。

第二层：

- PF-022 现行表述：QPS / Latency / Token / Cost / HA / DR **未恢复**；且**不能**用今天的测试或本机运行反推历史 Pilot 指标。
- 我个人的位置：我在 4 月做的是 Tool/MCP 与后续检索/上下文代码；我不记得、也没有证据显示我提交过一条 PF 条目。
- 所以「谁维护」——`docs/governance/` 归属上属于 round 流程，但**具体人/角色我指不出来**，只能说 Unknown。

- `事实层`: Unknown（维护方、我的提交记录）
- `证据`: `docs/governance/project-fact-provenance.md` PF-022
- `边界`: 我不认领这份台账的编写；也没有证据说我提交过条目。

## A165

**我没看过原文。** 对 PF-017 我能说的只有它已经写下的那一条：「客户曾反馈回答质量还需要提高」。**反馈渠道、原文、时间**都不在可复核范围里——而且台账特别点名**不能**把它跟 PF-031（HotpotQA GraphRAG 那次修复）接成一个 Cause→Fix 故事。

第二层：

- PF-017 的「不能扩大成」列了三项：不能说根因一定是 RAG/Prompt/Memory/Model 某一项；不能用 PF-031 的研发 Eval 反证客户反馈根因；升级证据是「客户 Bad Case / Issue / 调试记录 / 前后指标」——这些都没有。
- 我为什么不能凭印象补：一旦我说「我见过原话」，就从 `USER_CONFIRMED` 变成了**二手转述**，而转述在面试里最像事实、最经不起追问。
- 所以我把它停在「存在这条反馈」。

- `事实层`: Unknown（渠道/原文）
- `证据`: `docs/governance/project-fact-provenance.md` PF-017
- `边界`: 「我本人看到过原文吗」——没有证据支持我说看过。

## A166

**我在项目里的位置离 Pilot 有多远，我也说不出来。** 能确认的是：我做的是**代码级**工作（Tool/MCP、GraphRAG 检索、Context/Memory），而这些模块是 Pilot 部署的**上游**；但我没有任何材料能把我的工作与 Pilot 的某次运行、某个环境、某个判据连起来。所以「距离」是一个我**无法定位**的量，答案是 Unknown，不是谦辞。

第二层：

- 为什么连「离得远/近」都不能给：Pilot 的时长、参与人、环境、验收材料都没有（PF-019），没有坐标，就没有距离。
- 我能确定方向的一件事：我的工作**不等于** Pilot 运营——不是我在跑法院侧环境。
- 「如果连这两条都不知道说明什么」——它说明我确实不在 Pilot 的组织核心；但这句仍是**推断**，我把它标成推断。

- `事实层`: Unknown（位置/距离）
- `证据`: PF-019（Pilot 材料未恢复）；本人的可确认工作为代码级
- `边界`: 「我不在 Pilot 核心」是推断，不是证到的事实。

## A167

**没有可靠印象，我连时间都不给。** 台账写的是 `COURT QA: UNKNOWN / NOT AVAILABLE`（`docs/evidence/README.md`），即法院侧的质量结论今天**不可用**；「最后一次被法院侧的人碰到是什么时候」也没有记录。我给不出日期，也不打算给一个「大概是在某个月」的印象——「哪怕不可复核的印象」这句邀请，正是最容易让我编出一个听起来合理的日期的陷阱。

第二层：

- 证据状态：`COURT QA: UNKNOWN / NOT AVAILABLE`——这既是「没结论」，也是「没时间戳」。
- PF-018（法院侧测试）本身也只到「进入过法院侧人员测试」，不含时间/规模/题集。
- 所以我把它整条留在 Unknown；升级它需要的是「测试题 / 记录 / 评价表」。

- `事实层`: Unknown
- `证据`: `docs/evidence/README.md`（`COURT QA: UNKNOWN / NOT AVAILABLE`）；PF-018
- `边界`: 我不给日期、不给印象，因为我没有可依据的记忆锚点。

## A168

三天加一份真实中文卷宗，我会**先测「这套检索在中文法律文本上到底能不能命中」**，而不是先测图。理由：我改的那套机制有一大块是**英文线索**驱动的——`fusion.py` 的 comparison/bridge 关系线索表是英文（`founded by`、`maternal grandfather`、`director of` 之类，`fusion.py:36-84`），`entity_alias.py` 的 `GENERIC_ENTITIES` 也是英文词（`:10-22`）。它在 HotpotQA（英文）上跑通，**不构成**在中文卷宗上有效。所以第一件事是把「迁移性」测掉。

第二层：

- 具体三步：
  1. 从卷宗里手标 15–30 个 `query → gold 段落`，先量 **baseline（vector/BM25）单独**的 Recall@k——如果 baseline 在中文法律文本上就命中不了，图这一层的讨论没有意义。
  2. 单独查**英文线索是否触发**：中文表达（如「其父」「创办」「系……之子」）能不能命中那两张英文表；`resolve_alias` 的 fuzzy 分支现在是**退化成 no-op**（`entity_alias.py:35-61` 里 `allow_fuzzy` 分支重新比的是已经比过的 `normalized_candidate == normalized_known`），所以别名归一化在中文上基本只剩「精确/归一化精确」。
  3. 再看 **CitationProvenanceGuard 在真实 span 上的拒绝率**——`validate` 里有 `evidence_span_mismatch`/`document_version_mismatch` 分支（`provenance.py:74-133`），如果真实卷宗的 span 抽取本身就对不齐，引用会被大量拒掉（见 A182）。
- 判据：第一步过不了，就说明这套 GraphRAG 修复对法院域**暂时不适用**；这是可以三天内得到的结论。

- `事实层`: 今天的设计判断（不是历史实现）
- `证据`: `fusion.py:36-84`（英文关系线索表）；`entity_alias.py:10-22,35-61`；`provenance.py:74-133`
- `边界`: 这是「我会怎么测」的建议，不是「我们测过」；我从未在中文卷宗上测过这套检索（A67）。

## A169

删融合和删图路由**是一件事的两半，不是二选一**。「baseline-preserving fusion」是**给图层擦地板的护栏**——它的存在意义就是「图候选别把 baseline 已经命中的文档挤出去」。如果图路由被 Defer 掉，就没有东西需要护栏了，融合自然跟它一起走；这不是因为它无效，而是因为它**只对图层生效**。

第二层：

- 所以「唯一有『不劣于 baseline』证据的部分」这个观察是对的：它确实是唯一有证据的部分。但那个证据是**防止变差**，不是**带来收益**——护栏拿到 1.00 的 Recall@5，等于回到 baseline，净收益是 0（在 5 样本上）。
- 而且「baseline-preserving」**不是全局不变量**（修正 A17）：`_rank_key` 的排序确实以 `baseline_rank` 为主（`fusion.py:951-977`），但 `_apply_genealogy_guardrail` 会**故意**用图候选顶掉一个 baseline 项（`fusion.py:922` `selected[weakest_index] = candidate`），`floor_preserved = promoted_candidate is None`（`:943`）就是这个意思——地板在被晋升时是**被允许**不保留的。
- 顺带：真正在**驱逐** baseline 的是 genealogy guardrail；comparison/bridge guardrail 大多是**换入 baseline 候选**（保护链路）。所以「融合」这个词下面其实是三件不同的事。

- `事实层`: Current（代码机制）+ 我的口径修正
- `证据`: `fusion.py:922,943,951-977,756,815,877`
- `边界`: 删它的依据不是「它没用」，是「它与图层同生同死」。这里我**维持** A117/A118 的修正，不回到「全局不变量」的说法。

## A170

**没有跑过一次权重 0。** 我只见过它作为**可执行的实验设想**被写下来——`docs/governance/rb019-graphrag-ablation-protocol.md` 把 H1 的 switch-off 方式定义成「把图权重调到 0」，但同一份文件的 `measurement_status` 是 `BLOCKED_PENDING_DATA`，冻结于 2026-10-07，阻塞原因是数据源 TCP timeout、`data/evals/multihop/` 缺失、无模型凭据/索引。所以它到今天**还是设计，不是结果**。

第二层：

- 这份协议本身是 `FROZEN_PROTOCOL`，`owner 03+09`，来源 `rb-2026-09-15-formal-019 / IMP-019-05`——是一份**先冻协议、再等数据**的产物，不是跑过的记录。
- 所以 A69 那句「把图权重调到 0 就是 full-minus-H1 的一个臂」的准确含金量是：**臂定义存在，臂没跑**。
- 我在这里要防的失败模式：把「一个干净可执行的消融臂」讲得像「一次消融结果」。

- `事实层`: Target/Gap（协议已冻、未执行）
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md`（`measurement_status: BLOCKED_PENDING_DATA`、H1–H9、§8 阻塞原因）
- `边界`: 我没有跑过权重 0，也没有跑过该协议里任何一条臂。

## A171

**是我的判断，不是让步——但我承认它有让步的成分，所以我要把理由讲清楚，而不是停在「我不反驳」。** 理由：在测量被 `BLOCKED_PENDING_DATA` 卡住时，**「删」和「留」同样都没有依据**。没有测量，你证明不了「有稳定收益」，也证明不了「没有收益」。所以正确的动作既不是删、也不是宣布永久保留，而是 **Defer：明确挂在一个 gate 后面**——这正是仓库自己的治理口径（`documentation-architecture.md:286`：`Single Controller, independent services, GraphRAG, Reflection, persistent Multi-Agent or Native Runtime remain examples of measurement-gated choices. Existing implementation does not grant permanence.`）。

第二层：

- 换成我自己的项目，我会做同样的事，但**多一步**：给这个 gate 定一个**到期/触发条件**（谁在什么时间拿到数据、拿不到就默认 Defer 到关闭）。没有触发条件的 Defer 会变相变成永久保留——这是我对 A86 那句要补的地方。
- 我不同意的部分：如果 Red 主张的是「没测量 ⇒ 现在就删」，那我不接受这个推论——测量缺失是**双向**的。

- `事实层`: 个人工程判断 + 今天的设计补充
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md`（测量被阻塞）；`docs/governance/documentation-architecture.md:286`
- `边界`: 「Defer 而不是删」是今天的判断；我当时并没有为它写过一份带触发条件的 gate。

## A172

**A73 和 A74 按现在这么说是互相打架的**——因为别名归一化和 seed expansion **是同一个机制的两半**：别名归一化的输出就是喂给 seed expansion 的输入（这正是 Q173 指出的耦合）。所以「删别名归一化、留 seed expansion」这个组合，会让 seed expansion 只剩**精确名字**能命中图节点，而 A74 想覆盖的失败形态（「seed 命中不到图节点」）恰恰**又回来了**。

第二层：

- 机制：`resolve_alias`（`entity_alias.py:35-61`）把查询里的实体名映射到图里已知的名字；`normalize_entity_name`（`:25-32`）做归一化精确匹配；seed expansion 用的是**归一化后**的名字去站节点。所以别名这一层是 seed 命中率的**前置条件**。
- 而且 `resolve_alias` 的 fuzzy 分支实际是 no-op（见 A168），意味着这套别名机制本身的能力比名字听起来更窄。
- 结论：正确的做法是**把它们当一个单元**评估——要么一起留，要么一起 Defer。分开预算收益，会系统性高估每一半的边际收益。

- `事实层`: Current（代码耦合）+ 我对 A73/A74 的修正
- `证据`: `entity_alias.py:25-32,35-61`；seed 使用归一化名字（`c7814793` 那批引入的 seed source 记录）
- `边界`: 我不再沿用「别名/seed 各自独立可删」的框架；但我也没测过「只删一半」的实际影响，那是测量层的事。

## A173

**同意——它们确实是一个机制**，按两个预算收益会重复计算。我在这条上**收回 A73/A74 那种「两个独立机制」的预算方式**：别名归一是 seed expansion 的输入预处理，`alias` 标签就是这条链的证据（seed 带着 alias 来源被记下来）。

第二层：

- 机制链：查询 → 实体抽取 → `resolve_alias`（别名→已知节点名）→ seed expansion（用已知节点名在图里扩种子）→ path-aware ranking。这条链上任何一环的名字都**不是独立收益源**，是一根链上的环节。
- 所以消融设计应该把它们**串成一个臂**（例如「full-minus-alias-and-seed」），而不是两个臂；否则 H 系列会把同一次收益算两遍。
- 这条也修正了我 A73/A74 的框架，跟上一条（A172）是一致的：**一个机制，一个臂**。

- `事实层`: 我的口径修正（对 A73/A74）
- `证据`: `entity_alias.py:35-61`；A23 记录的 `alias` 标签
- `边界`: 我没有重跑消融来验证「合并成一个臂」后的数字，这是**协议该怎么改**的建议。

## A174

按 PF-032 自己的措辞，成熟 Provider / MCP SDK **已经**负责协议连接和具体工具执行；Zuno 当时决定的只是「这些能力怎样被 Agent **暴露、选择、注参、呈现**」。如果 MCP Host 已经自带 per-user config，那**「注参」这一件基本塌成 commodity**，剩下的 delta 主要是另外两件 + 注参里**非通用**的那一小段。

第二层：

- 塌掉的部分：把用户配置塞进调用参数本身（`call_args.update(mcp_config)`）——如果 Host 原生支持 per-user config，这就是 Host 的活。
- 还剩的、非通用的一小段：
  - tool→server 映射：用 `binding.name` 反查 server id（`simple_agent.py:197-200` `mcp_tool_id_resolver(binding.name)`）——这是 Zuno 自己的绑定语义。
  - **确定性 salt**：`salt=str(getattr(binding,"name","") or resolved_tool_id)`（`simple_agent.py:217`）——幂等 key 的身份来自绑定，不是随机（这也与 A106 的收回一致）。
  - **fail-closed**：没有注册 adapter 就在 `binding.ainvoke` 之前 `MCPToolAdapterNotBound`（`simple_agent.py:206` 一带）。
  - 准入：`mcp_requires_user_config` 这类门是「准入」那一件，不是「注参」。
- 所以「暴露、注参、准入」三件的准确说法应该是：**「注参」大部分塌了，delta 实际收敛到「暴露 + 准入」两件加上注参里的一小段绑定语义**。

- `事实层`: Current（代码）+ 我对 A75 三分法的修正
- `证据`: `simple_agent.py:188,197-201,206,217`；PF-032「Zuno 当时的代码主要决定这些能力怎样被 Agent 暴露、选择、注参和呈现」
- `边界`: 这条修正只调整「三件」的内部分布，不改结论「Zuno 的 delta 很窄」。

## A175

**它是被一份 Target 设计需要出来的，不是被某个具体使用者需要出来的。** PF-030 把这条链写得很清楚：6 月 25 日先落「明确标注为 Target」的 Context/Memory 设计，6 月 26 日连续落 typed Context contract、scoped Memory foundation、`GeneralAgent` 最小 context/post-turn 集成，以及**「callable pre-call `ContextOrchestrator`」**。所以它诞生时的身份是「设计里那个统一的按作用域装配入口」，**不是**「某条产品链路来要一个组件」。后来没有任何生产调用点接上它，它就停在了那里。

第二层：

- 定义：`platform/services/application/context/orchestrator.py:115`，`prepare()` 在 `:124`；`RecentWindowSelector` 在 `:113` 附近——它把 candidates（system prompt / recent window / memory items / knowledge evidence / capability items）按 token budget 过一遍。
- 真实在跑的读取路径是**另一条**：`agent/runtime/nodes/core.py:64/79` → `memory/engine.py:645 build_context_pack`。两条路都在，但**没有交叉**。
- 所以「谁需要它」的诚实答案：**设计需要它**；没有具体 caller。这也是 A55/A71「今天删掉不损失任何东西」的依据。

- `事实层`: Historical（6 月 V2 链，PF-030）+ Current（无调用点）
- `证据`: PF-030；`orchestrator.py:115,124`；`core.py:64/79`；`memory/engine.py:645`
- `边界`: 我不能说它是「某个团队要的功能」；它的需求来源是 Target 设计本身。

## A176

**都不对——按这个判据，可选层今天既不该删、也不该被永久保留，应该全部显式 Defer 到一个 gate 后面。** 「测量没有稳定收益就删」这条判据在 `MEASUREMENT_BLOCKED` 下**根本触发不了**：它要求一个测量结果作为输入，而输入不存在。同理，「没测量就删」等于把「未知」当成「无收益」——这是把缺失证据当反证。

第二层：

- 判据的正确形态应该是三段：① 能测 → 按测得的收益决定留/删；② **测不了 → 显式 Defer（挂在 gate 上，并带触发/到期条件）**；③ 只有在 Defer 了但触发条件长期无法满足时，才回到「按成本删」。
- 现在缺的是②里的**触发条件**——没有它，Defer 会事实上变成永久保留，这跟「按判据该删」是同一枚硬币的两面。
- `docs/evidence/README.md` 里 `QUALITY: not_yet_proven` + 测量 blocked 的组合，正好落在这个空缺上。

- `事实层`: 今天的设计判断
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md`（测量 blocked）；`docs/governance/documentation-architecture.md:286`（measurement-gated）
- `边界`: 「全部 Defer」是我的判断，不是当时的处置；当时没有为任何可选层写下带触发条件的 gate。

## A177

维持 A42/A43：**必要性 `not established`**，而且这正是台账里的官方状态——PF-025「Native Runtime 必要性」是 `TARGET / MEASUREMENT_GATED`，说的是「复杂任务**可以**用 Zuno 原生 Runtime；简单问答可留在通用宿主」，明确**不能**扩写成「自研 Runtime 已证明对所有任务更好」。所以今天维护它的理由**不是「它更好」**，而是「它承载了一组**法律域特有的状态语义**（领域状态/证据版本/正式准入/失效/Effect recovery）的假说，且这些语义在通用宿主上还没有被证明不可替代」。

第二层：

- 支撑继续维护的**合法**理由：① 这些语义（DocumentVersion、ReadinessDecision、PreparedAction/EffectReceipt、CitationProvenance）确实在通用平台里不原生存在（PF-024 的产品假说）；② 它们不是「Runtime 的表演」，而是**产品必须回答的问题**。
- 支撑**缩小**的理由：`module-detail-freeze-readiness-review.md` 把 `Native Runtime necessity measurement` 列进 **04 模块未做的事**，而 `documentation-architecture.md:286` 明确「现有实现不授予永久性」。
- 所以准确说法：**继续维护的正当性是「gate 没被关掉 + 假说还成立」，不是「已证明更好」**。如果那个对照测量永远做不出来，诚实的处置就是把它收进 Defer（同 A176），而不是默认永久保留。

- `事实层`: Target / MEASUREMENT_GATED
- `证据`: `docs/governance/project-fact-provenance.md` PF-025；`docs/governance/documentation-architecture.md:286`；`docs/governance/module-detail-freeze-readiness-review.md`（Native Runtime necessity measurement 未做）
- `边界`: 我不主张自研 Runtime 更好的证据；也没有那个对照数据。

## A178

**30 不是又一个独立的手定常数，但它是「一份手写清单的长度」。** 代码里 `KnowledgeRuntimeBatch.requirement_ids = tuple(f"ARCH-KNOW-{index:03d}" for index in range(1, 31))`（`runtime_batch.py:205`），`readiness_evidence(...)` 要求 `len(self.requirement_ids) == 30`（`:259-260`）。所以「30」= 那条 `ARCH-KNOW-001..030` 枚举的长度，是**从清单推出来的**，不是另写死一个 30。

第二层：

- 但要把话说全：**清单本身是手写的**——`range(1, 31)` 里的 31 是人为定的，改清单长度，30 就跟着变，而 `== 30` 这个断言会**跟着一起失效或一起过**（它和清单同源，所以不会互相制约）。
- 也就是说：`== 30` 这个检查**防不住「清单被改短」**——因为检查条件和被检查对象是同一个常量。这是它作为「就绪证据」的结构弱点。
- 所以准确的回答是：30 不是魔法数，但它是**未受保护的手写枚举长度**；这正是要指出的地方（与 Q178 的怀疑方向一致，只是机制不同）。

- `事实层`: Current（代码）
- `证据`: `runtime_batch.py:205,259-260`；`KnowledgeReadinessEvidence` 定义在 `:195`
- `边界`: 我**不**把它说成「又一个手定常数」（那是第一眼印象），也不说它「有保护」——它是 self-referential 的检查。

## A179

**这条我该先纠正前提，我没纠正，是我的问题。** 冻结简历里没有 `KnowledgeGeneration` 这个词；它是**知识模块 Target 文档**里的词，在 `src/` 里 literal **0 命中**（A78 已记）。我当时按「它存在」直接答了机制，等于默认了一个简历里不存在的名词是简历内容——正确做法是先说「这个词不在冻结简历里，它是 Target 文档词，代码里搜不到」。

第二层：

- 这正是我这批答案反复在打的**文档先行 / 代码未跟**问题：知识模块 `README.md` 的 Target 段用 KnowledgeGeneration / generation activation / 原子 serving switch 描述机制，而 Current 段自己写「不能证明完整 generation lifecycle、task readiness、原子 serving switch 已经落地」。
- 所以 A77/A80 用这些词描述机制时，**必须带 Target 标签**——我曾经没有每次都带，这是口径漏洞。
- 修复方式：不是把 A77/A80 撤掉，而是把「用词来源」显式写出来（Target 文档词 → 代码里叫什么，或没有）。

- `事实层`: 我的遗漏（未纠正前提）
- `证据`: 冻结简历 `01_simulated_resume.md`（无 KnowledgeGeneration）；`docs/modules/knowledge/README.md`（Target 段）；A78（src 零命中）
- `边界`: 我认这是漏纠；但我不认为「它不存在」——它作为 Target 概念存在，只是不在简历、不在 src。

## A180

**今天没有原子切换。** `ServingPointer` 在整个 `src/` 里 **0 命中**（我按名字搜过），所以「原子切换 ServingPointer 保护 serving 完整性」是 Target，不是今天在跑的机制。今天**避免读到旧 embedding** 的护栏不在读取侧，而在**引用侧**：`CitationProvenanceGuard.validate` 会拿 `document_version_id` 与当前比对，不一致就拒（`provenance.py:92` `document_version_mismatch`）。

第二层：

- 关键区别：**「拒引用」≠「不读旧 embedding」**。读取侧（向量/BM25/图）今天没有版本门控；它读的是索引里当下的内容（Chroma `n_results=min(top_k,100)`，`chroma_client.py:52`）。
- 所以今天的真实风险是：文档更新后，**索引里可能还留着旧版本**，检索**可能**命中它——这时能兜住的只有引用校验（把对不上的引用拒掉），拿不回「本来该命中的新版本」。
- 知识 README 的 Gap 段把这条明说了：「generation activation、跨 Store purge、权限撤销后的召回收敛」都还需要验证。

- `事实层`: Target（原子切换）+ Current（引用校验是唯一在跑的护栏）
- `证据`: `ServingPointer` 在 `src/` 0 命中；`provenance.py:92`；`docs/modules/knowledge/README.md`（Gap 段）；`chroma_client.py:52`
- `边界`: 我修正 A77 的暗示：原子切换**没有**落地；今天只有引用侧校验，无读取侧版本门控。

## A181

**是文档先行，代码在别处换了名字——不是「代码未跟」那么简单。** 没有 `KnowledgeGeneration` 这个字面（0 命中），但同一个语义在代码里以**别的名字**存在：`KnowledgeVersionRecord`/`KnowledgeVersionState`（`runtime_batch.py`）、`document_version_id`、`DocumentVersion`、索引 manifest 等。所以不是「设计说了一个东西、代码完全没有」，而是**同一概念两套命名**。

第二层：

- 这类命名漂移让「找证据」这件事变得危险：按 Target 词搜，会得到「0 命中 → 没实现」的**假阴性**；按代码词搜，才看到版本/就绪/引用这些机制**部分存在**。
- 连带一处：PF-029 的表述用的是 `GeneralAgent.prepare_context()`，而代码里这条路径叫 `build_context_pack`（`agent/runtime/nodes/core.py:64/79` → `memory/engine.py:645`）——**台账本身也在用文档词**。这解释了 A28 当初为什么会写成 `GeneralAgent.prepare_context()`：它是**照着台账/文档词写的**，不是照着代码。
- 所以我修正的落点：不是「代码没跟上」，是**词表没统一**——需要一张 Target 词 ↔ 代码符号 的对照。

- `事实层`: Current（命名漂移）+ 我对 A28 成因的补充
- `证据`: `KnowledgeGeneration` 在 `src/` 0 命中；`runtime_batch.py:195,205`（KnowledgeVersion*/requirement_ids）；`core.py:64/79`；`memory/engine.py:645`；PF-029 用词
- `边界`: 我不改 A28 的实质修正（真路径是 `core.py`/`build_context_pack`），只是把「为什么会写错」补成命名漂移。

## A182

用户在「引用被拒」时看到的**不是报错、也不是空答案，而是「这条 claim 降级成 unsupported」**——粒度是**逐条 claim**，不是整轮失败。机制在 `RuntimeCitationBinder.bind`：当候选引用不唯一、或引用对应的 evidence 找不到时，它产出一条 `CitationBinding(citation_id=None, support_verdict="insufficient", failure_class="UNSUPPORTED", reason_code=...)`，`reason_code` 可能是 `citation_provenance_unavailable` / `evidence_missing` / `citation_ambiguous_without_claim_relation` / `document_version_mismatch`。**它宁可让这条 claim 没有引用，也不指错。**

第二层：

- 所以产品表现准确说是：**该 claim 以「证据不足」呈现**（`support_verdict="insufficient"`），并带一个可追溯的 `reason_code`——这是一条**可解释的降级**，不是静默失败。
- 我**不能**声称的那部分：这条 `insufficient` 最终在 UI 上被渲染成什么（是灰掉、是带提示、还是被过滤掉）取决于 synthesis 的呈现层，我**没有证据**说用户看到的具体形态。
- 一个真实风险：如果真实卷宗的 span 抽取本身对不齐，`evidence_span_mismatch`（`provenance.py:96`）会**大面积**触发，结果就是「答案在，但引用几乎全被拒」——那时用户看到的就是一个没有引用支撑的答案。

- `事实层`: Current（claim 级降级机制）
- `证据`: `agent/runtime/synthesis/citation_binding.py:32-70`；`knowledge/provenance.py:74-133`（`document_version_mismatch:92`、`evidence_span_mismatch:96`）
- `边界`: UI 呈现形态我不知道；「拒绝率在真实卷宗上多高」也没测过。

## A183

**今天一步都不会被生产走到。** 生命周期状态是定义好的（`DeleteState = Literal["visibility_revoked","cleanup_requested","physically_deleted","verified","legal_hold","restored"]`，`delete_restore.py:17-24`），`DeleteRestoreRuntime` / `PersistentDeleteRestoreCoordinator` 也在，但**生产里没有调用方**——grep 全仓只有 `tests/knowledge/test_ingestion_delete_restore.py` 在调它。所以「今天有几步真的会被走到」的答案是：**零步**（除测试外）。

第二层：

- 机制是完整的：`request_delete`（默认 state 落 `visibility_revoked`，`:341`）→ `request_cleanup` → `mark_physical_delete`（`:493`）→ `verify_delete`，每一步产 `DeleteLifecycleReceipt`。它是**一条实现好的链**，只是没有入口。
- 所以即使「只有第一步被触发」这个较弱的说法也**不成立**——连第一步都没有产品入口（除了测试构造 `DeleteLifecycleCommand`）。
- 这与仓库的模式一致：协议/状态机常先落地（Target 词），workflow 接线在后；README 的 Gap 段也把「跨 Store purge、权限撤销后的召回收敛」列为待验证。

- `事实层`: Current（实现存在、无生产驱动）
- `证据`: `delete_restore.py:17-24,341,493,534`；调用方仅 `tests/knowledge/test_ingestion_delete_restore.py`
- `边界`: 我修正「只有第一步会被走到」的暗示——今天是 0 步，不是 1 步。

## A184

**我不敢说用户实际看到什么——因为我没有证据说存在一条面向用户的「全案无相关内容」渲染。** 能确认的只有零命中在**检索层**的表达：`zero-evidence` 是检索可观测性里的一个信号（`docs/modules/knowledge/reference.md:235` 一带），也就是「这次检索没拿到证据」这件事**被记录**；但「记录了一个 zero-evidence 信号」和「产品给了用户一句结论」是两件事。

第二层：

- 我**能**说的：zero-evidence 只证明「我没检索到」，**不能**证明「全案没有」——因为索引就绪度、路由失败、后端失败都可能造成零命中，而这些与「案卷里真的没有」是不同原因（A82 已记）。
- 我**不能**说的：系统今天会回什么字符串/什么 UI。产品层的空答案措辞、或者是否降级到「覆盖不全」的提示，我没有依据。
- 所以我把它停在：**信号存在，产品表现 Unknown**——并给出今天的建议（见 A189）：零证据必须带「覆盖范围 + 就绪度」一起呈现，不能单独呈现成结论。

- `事实层`: Current（检索层信号）+ Unknown（产品表现）
- `证据`: `docs/modules/knowledge/reference.md`（retrieval observability / `zero-evidence`）；A82
- `边界`: 我不编用户可见文案；「全案无相关内容」这个结论我今天不会让系统单独下。

## A185

**那份范围定义今天存在，但它是硬编码在代码里的一份清单，不是由某个 owner 维护的文档。** 「这个任务该覆盖什么」在代码里就是 `KnowledgeReadinessEvidence.requirement_ids`——`ARCH-KNOW-001..030` 那 30 条（`runtime_batch.py:205`）。覆盖/缺失的计算就是拿**命中到的 requirement** 去比这份清单。

第二层：

- 所以 `PARTIAL` 带「覆盖了什么、缺了什么」在结构上是成立的：`KnowledgeReadinessEvidence` 有 `requirement_ids` + `code_refs`/`test_refs`/`verifier_ref`/`evidence_ref`，`implementation_available` 由 `len(...) == 30` 这类条件决定（`:259-260`）。
- 问题在于：这份「该覆盖什么」是**通用工程清单**（ARCH-KNOW-NNN 这种编号），不是**按案件类型/法律任务**定义的范围。也就是说，它回答不了「这个**具体法律任务**该覆盖哪些材料」——那需要的是按任务类别的覆盖定义，而它不存在。
- 谁维护：**没有明确的 owner**；它随代码改，改它不受任何治理流程约束（同 A178 的结构弱点）。

- `事实层`: Current（清单在代码里）+ Gap（按任务类型的范围定义缺失）
- `证据`: `runtime_batch.py:195,205,259-260`
- `边界`: 我不说这份清单是「任务范围定义」的完整答案；它只是一个通用 requirement 枚举。

## A186

指**rerank 之后的 5**。`run_real_runtime_eval.py` 里 `rerank_top_k = int((profile.get("retrieval") or {}).get("rerank_top_k") or min(top_k, 5))`、`top_k` 是 CLI 的 `--top-k`（默认 10）；所以样本 `limit=5` 时量的是 `Recall@5`/`MRR@10` 里的 top-5，也就是**rerank 之后**的最终 5 条。

第二层：

- 三个量要分清：`limit` = 样本题数（5）；`top_k` = 候选召回数（默认 10）；`rerank_top_k = min(top_k, 5)` = 最终保留数（5）。
- 「被挤出 top-K」在 audit（`7928df50`）里指的就是**最终 top5**——`Ed Wood`、`Shirley Temple` 原本在 baseline 的 top5 里，被 graph-added 文档挤出去。所以「Top-K」在简历那句话里 = rerank 后的 5。
- 我会避免的一个含糊：说「Top-K」时如果**不说清是候选 10 还是最终 5**，读者会以为是召回侧被挤——那是另一件事。

- `事实层`: Current（runner 参数语义）
- `证据`: `tools/evals/zuno/multihop_eval/run_real_runtime_eval.py:216`（`rerank_top_k ... or min(top_k, 5)`）、`:567-568`（`--limit`/`--top-k` 默认 10）；PF-031 的 top5 表述
- `边界`: 我更准确地写「最终 top5」，不再单说「Top-K」。

## A187

**方向可以归因，量级不能。** 能站住的部分是**机制级**的：audit（`7928df50`）逐题指出了两次 top5 位移、点名了被挤出的 `Ed Wood` 和 `Shirley Temple`，并把根因定位成 **ranking displacement（图侧噪声占了 top5 位）**，而不是「图路由没激活」。这是**看得到机制**的归因，不是统计推断。站不住的部分是**幅度**：样本只有 5 题、没有重复、没有 ANN 抖动控制。

第二层：

- 一个直接的警告信号：同日 rerun 里 **baseline 的 `MRR@10` 也从 0.90 变成 1.00**（PF-031）。baseline 自己动了，说明这批 run 有**运行间方差**，因此「local 从 0.80 回到 1.00 里有多少是 fusion、多少是方差」**不可分离**。
- ANN 侧：Chroma HNSW `hnsw:space="cosine"`（`chroma_client.py:43`），小 K（top_k 默认 10）下的召回损失**没测过**（A99 已记），所以「抖动只来自图」这个前提**没被验证**。
- 所以准确表述是：**「graph-added 文档在 5 题里挤掉过 baseline 已命中的 2 篇」是可追溯的事实；「GraphRAG 修复带来 X 收益」不成立**——后者需要 holdout + 消融，而那还是 `BLOCKED_PENDING_DATA`。

- `事实层`: Current（机制归因可追溯）+ Gap（幅度不可分离）
- `证据`: PF-031（两次 top5 regression 逐题记录、baseline `MRR@10` 0.90→1.00）；`chroma_client.py:43,52`；`rb019-graphrag-ablation-protocol.md`
- `边界`: 我**不**说 graph 是唯一变量；相反，我指出 baseline 自己也变了。

## A188

**我不能说这是有意分开的**——没有证据（没有 ADR、没有决策记录）。代码上的事实是：知识检索的**配置**里 `vector_backend = "chroma"`，但检索结果转文档时标的是 `source_backend="milvus"`（`orchestrator.py:616`）；Milvus 侧是 `MilvusClient(MilvusLiteClient)`（`milvus_client.py:6`）。至于 Memory 默认 Chroma，是 PF-010 记的**历史事实**（根提交已含 Chroma/Milvus，当时 `MemoryClient` 默认 Chroma）。

第二层：

- 所以「哪套服务知识检索、哪套服务记忆」的准确回答是：**记忆侧默认 Chroma 是历史形成的**（根提交就有，我没参与那个选择）；**知识检索侧今天配置是 chroma**，但来源标签写着 milvus——这是一处**标签不一致**，不是一套清晰的分工。
- 「有意分开的吗」：**Unknown**。有可能是历史分层（记忆子系统先有 Chroma，检索适配层后做），也可能是别的；我没有材料证明是**决策**。
- 我不把它讲成「双向量库架构」——那是把一个不一致讲成设计。

- `事实层`: Historical（Memory 默认 Chroma）+ Current（配置/标签不一致）+ Unknown（意图）
- `证据`: PF-010；`docs/modules/knowledge/reference.md`（`chroma_client.py:43,52`、`milvus_client.py:6`、`orchestrator.py:616`）
- `边界`: 我不为这个划分认领设计意图；也不声称它是一致的设计。

## A189

**今天没有一个这样的条件。** 它被列在 Gap 里而不是实现里——`docs/modules/knowledge/README.md` 的 Gap 段明确写「negative evidence 条件」仍需验证。所以「有明确条件说『这条缺了以后就永远不宣称全案没有』」的答案是：**没有**。

第二层：

- 现在的失败形态：zero-evidence 一旦被当成结论，就会把「索引没就绪 / 路由失败 / 后端失败」这三种**过程性原因**误读成「案卷里没有」——这是 A82/A184 那条边界的直接后果。
- 今天我会怎么定这个条件（**今天的建议，不是当时的实现**）：出现 zero-evidence 时，**必须同时满足**才允许下「无相关内容」这类结论——① 就绪度是 `READY`（不是 `PARTIAL`/`BLOCKED`）；② 计划中每一条 retriever（vector/bm25/graph）都有成功返回；③ 没有 `fallback` / 没有 `candidate_blocked_reason`。三条缺任何一条，输出只能是「覆盖不全/未知」，**不能**是「全案没有」。
- 这条条件应该跟 readback（A185）一样落到**数据里**（一条判据字段），而不是靠会话语义约定。

- `事实层`: Gap（条件不存在）+ 今天的设计建议
- `证据`: `docs/modules/knowledge/README.md`（Gap: negative evidence 条件）；A82/A184
- `边界`: 这是我今天建议的条件，不是已实现的门；阈值/字段名未定。

## A190

**没有缓存——所以隔离不是靠「缓存失效策略」，而是靠「根本不存在一个可能串的缓存」。** `MCPUserConfigService.get_mcp_user_config`（`api/services/mcp_user_config.py:141`）每次调用都直接走 DAO；DAO 的 `get_mcp_user_configs`（`database/dao/mcp_user_config.py:63`）是一次 `select ... where user_id = :user_id and mcp_server_id = :mcp_server_id` 的**当场查询**。我在 service 和 DAO 两层都没找到 `lru_cache` / 进程内 dict 缓存 / TTL 包装。

第二层：

- 所以 Q190 的假设（「如果有缓存且没有失效策略，隔离还在吗」）在这条路径上**不成立**：没有缓存，就不存在「按 `(user_id, server_id)` 命中到别人的配置」这个失效面。
- 代价要说清楚：**每个 tool 调用一次 DB 读**（`execute_binding_tool` 在 `:197` 调 resolver）。这是拿**延迟/DB 压力**换隔离的确定性——不是没有成本。
- 另一个隔离来源是 A89 那条：`call_args = dict(args)`（`simple_agent.py:188`）是**本次调用的局部对象**，`call_args.update(mcp_config)`（`:201`）只改本地副本，不写回绑定。

- `事实层`: Current（无缓存）
- `证据`: `api/services/mcp_user_config.py:141`；`database/dao/mcp_user_config.py:63`；`simple_agent.py:188,197,201`
- `边界`: 修正 A5/A89 的落点——不是「缓存策略正确」，是「没有缓存」；代价是每调用一次 DB 读。

## A191

**冲突时显式参数赢，ContextVar 根本不参与注入判定。** 工具路径上的 user 身份是**显式参数**：`execute_binding_tool(*, ..., user_id: Any, ..., mcp_user_config_resolver=...)`（`simple_agent.py:160-164`），注入时用这个 `user_id` 调 resolver（`:197-200`）。`platform/common/contexts.py:5-8` 里的 `user_id` ContextVar 是给 **tracing** 用的（`get_user_id_context` 在 `:21`），不是给授权/注参用的。

第二层：

- 所以「谁赢」的结构是：**注入这种有后果的动作只认显式参数**；ContextVar 只影响日志/追踪字段。两者不一致时，日志里的 `user_id` 可能与实际注参的 `user_id` 不同——那是**可观测性**问题，不是**隔离**问题。
- 反过来说：如果未来有人**改用 ContextVar 去做注参**，那才会把 tracing 通道变成权限通道——这是我会明确禁止的改动（与 A6/A90「ContextVar 只用于 tracing」一致）。
- 我想补的一条：**全局没有一处断言「ContextVar.user_id == 显式 user_id」**。所以万一两者分叉，今天没人会报错。

- `事实层`: Current（显式参数优先）
- `证据`: `simple_agent.py:160-164,197-200`；`platform/common/contexts.py:5-8,21`
- `边界`: 「两者会不会真的分叉」我今天没有断言、也没有检查；我只能说分叉了也不会影响注参正确性。

## A192

**顺序的，一条接一条，没有 `gather`。** 多路检索在 `RetrievalOrchestrator._run_single_pass`（`retrieval/orchestrator.py:545`）里是**依次 `if` 块 + 依次 `await`**：`:614` vector → `:615 await rag_retriever.retrieve`；`:649` bm25；`:655` graph → `:674 await graph_retriever.retrieve`。我在整个 `retrieval/` 目录搜 `gather`，**0 命中**。

第二层：

- 所以「怎么并发」的答案是**不并发**——它是**顺序流水线**：vector 跑完才跑 bm25，再跑 graph；proactive requery 循环（`:625-628`）也是顺序。每一路单独 `await`，并发度 1。
- 与 A91 的一致性：A91 说 tool 路径上没有 `asyncio.gather`——这里是**同一条规则的延续**：两个关键路径都走顺序，框架内部也不做并发（`RagRetrieverAdapter`/`GraphRetrieverAdapter` 只是把调用转给底层 client）。
- 诚实的代价：**顺序 ⇒ 多路检索的延迟是相加的**，不是取 max。这是我在简历里没写、也没有测量的一条事实（延迟数字属 PF-022，`UNKNOWN`）。

- `事实层`: Current（顺序执行）
- `证据`: `retrieval/orchestrator.py:545,614-615,625-628,649,655,674`；`retrieval/` 下 `gather` 0 命中
- `边界`: 我不声称「并发已实现」；也没测过并发的收益。

## A193

**今天没有一个远端 Tool 支持真正的 cancel，所以那条规则在产品路径上基本没被触发过。** 证据是明写的：`CXL-A` 只证明了「**本地 cancel 意图**不会吞掉之后到达的**真实 provider completion**」（`docs/evidence/README.md`：`CXL-A LATE CALLBACK TRUTH: SELECTED VERIFIED`），而 `CXL-B NOT IMPLEMENTED`——也就是**cancel 编排本身没有实现**。同一份 evidence 里也把 provider cancel capability 写成「后续可选能力」。

第二层：

- 所以「cancel 在 send 之后只是可选尝试」的准确含义是：**它是「能力缺席时的兜底语义」，不是「一个在跑的功能」**。真正被验证的是**对 late callback 的诚实**（不假装取消成功），不是取消成功。
- 下一步在不猜 task id 的前提下，可以把现有 Product cancel token 交给同一个 canonical AgentRun（`docs/evidence/README.md` 的说法）——但那是**下一步**，不是今天。
- 因此「这条规则有没有被真实触发过」：**没有产品路径上的证据**。

- `事实层`: Current（CXL-A verified / CXL-B not implemented）
- `证据`: `docs/evidence/README.md`（`CXL-A LATE CALLBACK TRUTH: SELECTED VERIFIED / CXL-B NOT IMPLEMENTED`；provider cancel capability 为后续可选）；`docs/governance/cxl-b-cancel-orchestration-freeze-candidate.md`
- `边界`: 我不把「cancel 是可选尝试」讲成「支持软取消」；今天没有远端 cancel 能力。

## A194

**我保证不了「写 Attempt」和「这次 send」是同一个原子动作——它们注定不是同一动作，所以保证的落点是「动作身份」而不是「原子性」。** 机制上：Attempt 以 `dispatch_certainty=NOT_DISPATCHED` 先落库，`call_id` / 幂等 key 把这条 Attempt 与**这次动作的身份**绑在一起，重试只允许在 `KNOWN_NOT_SENT` 时发生。但「落 Attempt」到「socket send」之间**必然有一个窗口**——这正是 AUD-L2 的窗口，而 `AUD-L2` 现在是 `NOT IMPLEMENTATION-PROVEN`。

第二层：

- 所以准确的回答是：**同一是「身份同一」（同一个 `call_id` + 同一个幂等 key + 同一个 `prepared_action_hash`），不是「写入与发送同一」（那是分布式事务，做不到）。**
- 这个窗口里崩溃的最坏结果，就是系统**不能证明**自己站在边界哪一侧——它只能诚实地报不确定（`UNKNOWN_EFFECT`），不能猜「一定没发」或「一定发了」。
- 这也解释了为什么仓库同一个 evidence 会把两条并列写：`UNKNOWN EFFECT RESTART REPLAY: FIX VERIFIED / UNKNOWN PRESERVED`——重放**不吞** UNKNOWN，不把它升级成确定。

- `事实层`: Current（身份同一 + 幂等 gate）+ Gap（AUD-L2 原子性未证明）
- `证据`: `docs/evidence/README.md`（`MANDATORY AUDIT CRASH-RESTART REPAIR: AUD-L2 NOT IMPLEMENTATION-PROVEN`、`UNKNOWN EFFECT RESTART REPLAY: FIX VERIFIED / UNKNOWN PRESERVED`）；`invocation_gateway.py` 幂等 `complete_idempotency`
- `边界`: 我不声称「写入与发送已原子化」；那个窗口今天靠「保留 UNKNOWN」而不是靠原子性来诚实。

## A195

**CAS 防不住这条，而且「读到未提交的另一条 memory」这个前提在 READ COMMITTED 下不成立。** READ COMMITTED **禁止脏读**——你读不到别的事务**未提交**的行。所以「读到未提交的另一条 memory 再基于它写」不会发生。真正的风险不是脏读，是**不可重复读/幻读**：同一事务里**两次**读，第二次可能看到别的事务**新提交**的行。

第二层：

- `activate_memory_version` 的保护（`domain.py:301-364`）是**针对写入目标的**：`SELECT status ... FOR UPDATE`（`:315`）锁住那一行，再校验 `status in {APPROVED, ACTIVE}`，最后用 generation 做 CAS（`rowcount != 1` 时 `raise MemoryGovernanceConflict("memory activation CAS failed")`，`:363` 一带）。它保证「这个 version 的激活不丢更新」。
- 它**不**保证：「我在这个事务里基于**别处读到的若干行**做的决定，在提交时仍然成立」。那需要 `REPEATABLE READ`/`SERIALIZABLE`，或把那些行也显式锁住——而 `MemoryUnitOfWork`（`domain.py:83-96`）用的是 `connection.begin()`，**没有显式隔离级别**，即 PostgreSQL 默认 READ COMMITTED（A94 已记）。
- 所以准确的回答：**CAS 防 lost update（对同一行），不防「基于别处读到的快照做决定」的并发漂移。**

- `事实层`: Current（FOR UPDATE + CAS，READ COMMITTED）
- `证据`: `domain.py:83-96,301-364`（`FOR UPDATE:315`、CAS:363 一带）
- `边界`: 我不声称这是可串行化的存储；也没做过并发压测来量这个漂移的影响。

## A196

**没有静态检查，也没有 CI 规则——今天只能靠人搜。** A95 说的「没逐点审计」就是这个意思：没有一条 lint/AST 规则会拦「模型调用被包在写事务里」。今天的做法只能是**结构性搜索**：找 `with <uow>` / `engine.connect()` / `connection.begin()` 块里是否出现 `await`（模型网关是 async）——因为 `MemoryUnitOfWork.__exit__` 的 commit 是**同步**的，一个 `await` 出现在这类块里，本身就是这个反模式的**形状**。

第二层：

- 为什么这条可行：模型调用走 async gateway（`ModelGateway`），DB UoW 是 sync 的（`domain.py:83-96`）。所以「在事务里等模型」= 「sync 事务块里出现 await」——在语法层面可见。
- 今天我会怎么落地（**今天的建议**）：写一条 AST 检查，禁止 `with engine.connect()/begin()/UnitOfWork` 的 body 里出现 `Await` 节点；或者退一步，用一条 grep-based CI 规则对 `Begin/connect` 附近 N 行内的 `await` 报 warn。
- 现状诚实说：**这条规则不存在**，所以这类反模式今天**可以静默通过 review**。

- `事实层`: Gap（无静态检查）+ 今天的设计建议
- `证据`: `domain.py:83-96`（同步 commit）；无对应 lint/CI 规则被找到
- `边界`: 我没做过完整审计，所以「当前是否存在这类反模式」我答不了；我能答的是「没有拦住它的机制」。

## A197

**会大幅收窄，但「自然消失」只在一个更强的条件下成立——谓词必须落在「决定点」上。** 如果过滤只是从应用层挪成 SQL 里一句 `WHERE review_status='approved'`，然后**读出来再基于它做事**，那 TOCTOU **没消失**——只是窗口从「应用层判断」挪到「SQL 读」和「后续动作」之间。要真消失，得让**判断和效果在同一条语句/同一个事务里**：例如写入本身带 `WHERE review_status='approved'`（条件写），或者对那行 `SELECT ... FOR UPDATE` 后再决定。

第二层：

- TOCTOU 的本质是「**检查**和**使用**之间有间隙」。换查询位置不改变间隙的存在，只改变间隙的宽度和位置。
- `activate_memory_version` 就是「正确形态」的一个模板：它把检查（`status in {APPROVED,ACTIVE}`）放在**同一事务、同一把锁下**，再用 CAS 兜住提交时的一致性（`domain.py:315,363`）——也就是说，仓库里已经有「把谓词钉在决定点上」的做法，只是没推广到 memory 的**读取过滤**上。
- 所以答案：**下沉到 SQL 是必要但不充分**；真正的消除靠「条件写 / 同行锁定 / 同事务判定」。

- `事实层`: 今天的分析（不是当时已实现）
- `证据`: `domain.py:315,363`（同事务判定 + CAS 模板）
- `边界`: A96 说的「过滤在应用层、无 TOCTOU 护栏」我维持；这里补的是「下沉成 SQL 谓词**够不够**」——答案是不够。

## A198

**它是「只写进 metadata、不参与决策」的计算——所以它的意义是 trace/观测，不是排序。** `_rank_key`（`fusion.py:951`）先算 `item.metadata["fusion_score"] = (100 - group*20) + (20 - min(baseline_rank,20)) + graph_tier*3 + graph_signal + local_score + base_score + chain_score*2`（`:968-976`），然后 `return` 的元组（`:977`）是 `(candidate_group, baseline_rank, -chain_score, -graph_tier, -graph_signal, -(local_score+base_score))`——**`fusion_score` 不在里面**。

第二层：

- 也就是说：这个分数是**给人看的诊断值**（把分组/基线 rank/图层级/信号/本地分合成一个标量，便于看 trace），**不改变任何排序结果**。排序完全由那个元组决定。
- 这里面有一个**同源信息重复**的有趣点：`fusion_score` 的成分几乎都能在那个元组里找到（group、baseline_rank、graph_tier、graph_signal、local+base），所以它不是引入了新信息，而是**把已有分量打包成可读的一个数**。
- 诚实处置：要么把它**明确标注为 trace-only**（避免后人误以为它影响排序），要么删掉（它是一个**看起来像权重融合、实际不决策**的字段——这正是 Q169/A169 说的「融合这个词下面有好几件事」的一个实例）。

- `事实层`: Current（代码）
- `证据`: `fusion.py:951,968-977`
- `边界`: 我**不**说它「在跑所以有用」；它今天不参与任何决策。删或标注为 trace-only 是我今天的建议。

## A199

**查过——这个模式在 IR 里是成熟做法，而且这套仓库里就有一份更标准的实现没用在这条路上。** 「先过滤/候选生成，再重排」是标准的两段式检索（hard filter / candidate generation → 昂贵 ranker）；「硬约束 + 连续分数」的组合也是标准做法（constrained ranking / LTR），不是数学上不相容。真正的问题是**这个仓库没走那条成熟路**，而是自己拼了一套「分组 + 层级 + 基线 rank」的自制方案。

第二层：

- 更大的发现：**同一个仓库里已经有一份 RRF 实现**——`knowledge/agentic_graphrag.py:876` `entry["rrf_score"] += 1.0 / (60.0 + rank)`，strategy 名为 `local_rrf_then_score_rerank`（`:1411`），sort key 在 `:883`；`knowledge/runtime_batch.py:230` 也引用了 `rrf_version_ref="rrf:v1"`。
- 也就是说：**知识检索路径**用的是 `retrieval/fusion.py` 那套自制 group/tier 方案，而**另一条路径**用的是 RRF（k=60，业界最常见的成熟融合法）。这是我的第一批答案里搞错的一处（A97 说「全仓没有 RRF」）——**收回**：RRF 在仓里存在，只是没用在知识检索这条路上。
- 所以「重新发明」的准确说法是：不是「不知道 RRF」，而是**在知识检索这条路上选了自制方案、没试过那条已有的 RRF**——而 RRF 恰恰是最该先试的 baseline。

- `事实层`: Current（仓内两套融合路径并存）+ 我对 A97 的收回
- `证据`: `fusion.py:951-977,1065`；`knowledge/agentic_graphrag.py:876,883,1411`；`knowledge/runtime_batch.py:230`
- `边界`: 我维持 A97 的收回（RRF 存在）；但不主张 RRF 在这条路上**一定更好**——那需要 A/B，而那是没跑的。

## A200

**它一直是设计上的不变量，我没有「实际遇到三个 Owner 直接冲突」的案例。** 我能给的最接近真实证据的是**负向 probe**：PR #201 / run `34559517466` 曾证明「unresolved Reconciliation 在 restart replay 时被错误升级成 completed」、PR #205 / run `34560692093` 曾证明「缺少 durable mandatory-audit proof 时 send path 仍会 dispatch」——这些后来都被修成正向 regression。但这两个是**缺口（该拦没拦）**，不是**Owner 之间判断打架**。

第二层：

- 概念上要分清两种东西：
  - **Owner 冲突**：Security 说不行、Approval 说行、Budget 说无所谓——谁赢。这需要三方**同时给出相反裁决**才会暴露。
  - **顺序缺口**：某个 owner 的判定**没被查到**（例如审计证明缺失仍然放行）。这是**接线/顺序**问题，不是权威冲突。
- 上面两个 probe 属于后者：它们证明的是「owner-first ordering 还不是处处成立」，修完之后证明「顺序被强制」。所以它们是**顺序的证据**，不是**冲突的证据**。
- 所以我诚实的回答是：**不变量、未观测到冲突实例**；我**不会**用「我们遇到过，最后 X 赢了」这种句子去把它讲成 incident（这与 A145 我对「构造示例」的处理一致）。

- `事实层`: 设计不变量 + 未观测到冲突实例（Unknown）
- `证据`: `docs/evidence/README.md`（PR #201 / `34559517466`、PR #205 / `34560692093` 的负向证据及其后续修复）
- `边界`: 我不编一个「三方冲突」的案例；我能证明的只有「顺序曾被违反过，然后被修好」。
