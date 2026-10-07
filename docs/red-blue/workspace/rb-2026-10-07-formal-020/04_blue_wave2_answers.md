# Blue Wave 2 — Candidate Answers A101–A200

```text
round: rb-2026-10-07-formal-020
answers_to: 04_red_wave2_review_and_questions.md（Q101–Q200）
register: 第一层 20–60 秒口语，其后可展开
```

---

## T01 Tool / MCP

## A101

基本是。我核过 `77346758` 的 diff：它删掉了 `src/backend/agentchat/core/agents/mcp_agent.py`（-120 行）和 `skill_agent.py`（-263 行），同时重写了 `general_agent.py`。而仓库第一个 commit `eafeb1c2` 就是我到岗同一天的白天。所以在 git 里，那套转发层唯一的痕迹就是**这一笔 diff 的 before 一侧**——没有任何一笔更早的 commit 展示它被"引入"过。如果它同一周被引入又被删，"重构"这个词不成立，我会把它降级成"拆除一个在初始快照里就存在的转发层"。

更要紧的是作者字段：`eafeb1c2` 和 `77346758` 是同一条身份谱系。所以我不但证明不了那套层"早于我"，我甚至证明不了 `eafeb1c2` 不是我这条谱系的。这就是我为什么只敢说"重构"这个动词。

- `事实层`: Historical · Personal Ownership · Unknown
- `证据`: `77346758`（`mcp_agent.py` -120、`skill_agent.py` -263、`general_agent.py` 重写）；`eafeb1c2` 2026-04-15 "Initial commit"
- `边界`: 那套层有没有独立历史、有没有真跑过：Unknown。

## A102

我能指认一处，而且只有一处。`77346758` 在 `simple_agent.py` 里只有一个很小的 hunk，落点是 `create_skill_tool` 的内层函数：原来叫 `call_skill_agent`，改名成 `load_skill_context`。改之前它构造 `SkillAgent`、`init_skill_agent()`、`ainvoke([HumanMessage(...)])`，把子 Agent 的回答当工具返回值；改之后它调 `AgentSkillService.build_skill_runtime_context(skill, query=...)`，把 skill 包当文本返回。行为差异可指认：选 Skill 以前会拉起一个子 Agent，之后变成把 skill 包注入同一段对话。

这就是"删转发层"能给出的粒度——它不在 `general_agent.py` 那一大坨重写里，而在这个小 hunk 里。

- `事实层`: Personal Ownership · Historical
- `证据`: `77346758` 的 `services/workspace/simple_agent.py` hunk；当前对应文件 `src/backend/zuno/platform/services/workspace/simple_agent.py`
- `边界`: `general_agent.py` 那部分逐处归属：切不出。

## A103

真实依据我拿不出来。"漏传会静默降级"是我今天从代码结构推出的解释，不是当年的失败记录。我能替代给出的只是一个更强的 after-state：现在这条路径是 fail-closed 的——`execute_binding_tool` 在没有注册 adapter 时抛 `MCPToolAdapterNotBound`，早于任何 `binding.ainvoke`；配置注入变成调用点显式的一步。

但"当年某个坑逼我们删掉转发层"这个说法，我没有证据，我不编。

- `事实层`: Unknown（动机）· Current（after-state）
- `证据`: `platform/services/workspace/simple_agent.py:181-211`（docstring：无 adapter 时 fail closed）
- `边界`: 当年的失败记录：无。

## A104

我不知道同一个会话内并发两条请求是同一实例还是两个实例。我没有构造过这个测试，也没有找到代码依据说会话内的实例生命周期。我能说清的是：即使共享实例，注入的配置也不会来自实例自身的可变状态——`execute_binding_tool` 是模块级函数，`user_id` 是显式实参，配置每次现查；而 `server_dict` 只被读、不被写。

但这里有一个我必须点出的弱点：`_execute_binding_tool` 传的 `user_id=self.user_id` 是**会话实例的属性**。所以"现查现注"里的 `user_id` 不是从本次请求里取的，是从构造时冻结在实例上的。同一用户同一会话没问题；同一实例被不同用户复用才会串——而那取决于实例怎么来。

- `事实层`: Unknown · Current
- `证据`: `simple_agent.py:160-176`（显式 kwargs）、`:1379-1396`（`user_id=self.user_id`）、`:327`（`server_dict` 只读）
- `边界`: 会话内并发实例数：没测过。

## A105

`mcp_servers_info` 是 `self.mcp_manager.show_mcp_tools()` 的返回，也就是 MCP manager 从当前进程注册的 server 列表算出来的。所以 `server_dict` 的第一次进入路径是：MCP manager 初始化时装载 server → `show_mcp_tools()` → `server_dict`。能改它的只有 agent 初始化那一段；但上游 `mcp_servers_info` 的权威属于 MCP manager 的注册表。

我没有追到"谁有权改 MCP manager 的 server 注册表"那一层的所有权。

- `事实层`: Current · Unknown（上游所有权）
- `证据`: `simple_agent.py:1430-1441`；`platform/services/mcp/`
- `边界`: 上游注册表的写权：没有读到底。

## A106

捕获点不在 Agent 循环里。模型驱动的调用最终走到 `_execute_binding_tool`，它传 `user_id=self.user_id` —— 是**会话实例**的属性，在实例构造时定下，不是模型给的，也不是每次从请求里取的。所以"这一层怎么拿到 user_id"的答案是：它不拿，它是被实例持有的。

这既是我要认的优点（配置不靠隐式上下文传递），也是我要认的边界：如果实例生命周期和请求生命周期不是 1:1，这个 `user_id` 就有可能是过期的。

- `事实层`: Current
- `证据`: `simple_agent.py:1379-1396`；`:160-176`
- `边界`: 实例与请求的对应关系：没测过。

## A107

一个既不返回也不断开的 MCP server，会把 tool step 挂到连接层 timeout 为止——SSE read 300 秒、streamable read 300 秒。tool 执行那一步没有 `wait_for`，`RuntimeLimits.timeout_ms` 是声明式 budget，不是围着一次调用生效的 timer。所以"谁解开它"：正常路径上没有 step 级 timer；最坏是挂到 300 秒被连接层打断，或者进程被外部重启。

有没有 worker 级的 reaper 兜这一手，我没有找到。

- `事实层`: Current · Unknown
- `证据`: `platform/services/mcp/sessions.py:27-31`；`agent/runtime/execution/tool_step.py:95-106`
- `边界`: 上层 reaper：无证据。

## A108

60 秒之后，同一个 `call_id` 的第二次调用会**重新拿到 claim 并再打一次网络**。我读了 `claim_idempotency_receipt`：行不会被删；TTL 到期后（`expires_at <= now()`）那条 UPDATE 分支会把 generation+1、status 重置成 `in_progress`、`result_ref` 清空，也就是重新 claim 成功。claim 一旦 acquired，代码直接往下走去 dispatch，不再看 replay 分支。

所以那个洞是实的：TTL 之内的重试走 replay（返回既有 receipt、不打网络）；TTL 之外走重新 dispatch。真正能在 60 秒后拦住它的只有 effect certainty / 对账那条路，而那条路的远端查询没实现。所以"确定没执行才重发"这个守卫在 60 秒之后没有实现支撑。

- `事实层`: Current · Evidence
- `证据`: `platform/database/foundation.py:1184-1258`；`capability/tool_runtime/invocation_gateway.py:1283-1317`
- `边界`: 我没有跑过跨 TTL 的端到端测试。

## A109

是后者——**记录还在，只是不再算数**。到期不做物理删除；`expires_at` 过了之后同一 `(tenant, scope, key)` 可以被重新 claim。同一个 `call_id` + `prepared_action_hash`：TTL 内走 `not acquired` 分支，若 `status=='completed'` 且 `result_ref` 在 → replay；TTL 后走 UPDATE 分支 → 重新 acquired → 直接 dispatch（打第二次网络）。

还有一条硬约束：key 相同但 `request_hash` 不同，直接 `InfrastructureConflictError`——所以"同 key 不同输入"是被拒的，不是被重放的。

- `事实层`: Current
- `证据`: `foundation.py:1184-1258`、`:1245-1248`
- `边界`: TTL 到期瞬间的并发：没测过。

## A110

今天**没有任何东西触发它**。我 grep 过：`escalate_due_reconciliations` / `timeout_due_async_jobs` 的调用方只有测试，`src/` 里没有 cron、没有 worker 调它。所以那条 900 秒升级规则今天是一条**有入口、没有执行者**的规则。"转人工"作为默认动作，在今天的运行里更接近纸面默认。

我要把 A46 的措辞收一下：A46 说"默认动作是转对账"，那是**设计上的默认**；今天实际能发生的是——开一条 OPEN reconciliation 就停住，没有东西把它推向 ESCALATED。

- `事实层`: Current · Evidence
- `证据`: `invocation_gateway.py:1607-1618`；`grep -rn "escalate_due_reconciliations" src/ tests/` 只命中 def 与测试
- `边界`: 仓库外的调度（运维脚本）：没有证据，不 claim。

## A111

保留这一层是因为**它承载的不是上下文构造，是 fail-closed 的准入**。`execute_binding_tool` 的 docstring 写明：每次 `binding.ainvoke` 必须经 `MCPToolExecutorAdapter` 注册表；没有注册 adapter 就抛 `MCPToolAdapterNotBound`，早于任何 `binding.ainvoke`。如果把上下文构造挪到调用点直接 `ainvoke`，就等于把"没有 adapter 就不许发"这道闸门挪掉。

所以它不是纯壳——壳的部分（上下文 + 幂等 salt）可以挪，但"注册表 + 缺失即拒"这条语义不行。A10 说它"就是个 `binding.ainvoke` 的包壳"是对的，但我漏讲它同时是准入闸门，这里补上。

- `事实层`: Current · Target
- `证据`: `simple_agent.py:181-211`；`capability/mcp/mcp_tool_executor_adapter.py`
- `边界`: "去掉 adapter 会不会更简单"我没验证。

## A112

我承认口径不均匀。原因不是我在回避 gateway，是**审计的起点不同**：`planning/`、`recovery/` 那批是我在读 canonical runtime 布局时顺路做的 import 图扫描；而 gateway 这一层，我是从我自己的产品侧路径**逆着调用链往回读**的——`execute_binding_tool` → adapter → gateway——所以是"从入口读进去"，不是"从定义找 consumer"。

你直接问的答案我补上：gateway 的调用方是 `mcp_tool_executor_adapter.py`（adapter 持有 gateway 并调它），而 adapter 的注册表由 `simple_agent.py:1287-1330` 这个 composition 根装出来。所以它**在活路径上**，和 `BranchResultFencer`/`DynamicStepWorker` 不一样。

- `事实层`: Current · Personal Ownership（口径）
- `证据`: `simple_agent.py:1287-1330`；`capability/mcp/mcp_tool_executor_adapter.py:45,84,203`
- `边界`: 我没把 gateway 每个入口都做成 import 图证据。

---

## T02 GraphRAG

## A113

回到记录上查清了：两个数都来自公开历史，但它们属于**两次不同的 run**，而**错的是 A60 那个提法**。审计那次（`7928df50`，2026-06-20，HotpotQA limit=5）：baseline `MRR@10=0.90`、local `MRR@10=0.80`——这是 A11 的那对数，A11 没说错。同日 rerun（`3da5d742`）：local `MRR@10=1.00`，而且**baseline 的 MRR@10 也变成了 1.00**——provenance 原文就写着"baseline 的 `MRR@10` 在 rerun 中也从 `0.90` 变为 `1.00`，因此不应制造精确的单机制收益百分比"。所以 A60 那句"修复前后 MRR@10 0.80→1.00"把 local 的 run-to-run 增量讲成了"vs 一个不动的 baseline"，这是错的。正确说法是：修复链走完之后 local 与 baseline **打平在 1.00**，不是"超过 baseline"。

我更深的教训：baseline 本身在两次 run 之间漂了（0.90→1.00），说明这个 5-query smoke **两边都不稳**，单点数字根本不该当"修复前后"用。所以"self-claimed baseline_preserving 却超过 baseline"这个悖论不成立——它没超过，是打平；矛盾来自我把两次 run 的数拼进了一句话。

- `事实层`: Evidence · Current
- `证据`: `docs/governance/project-fact-provenance.md:92`（审计 baseline MRR@10=0.90）与 `:96`（rerun local 1.00，且 baseline 也从 0.90→1.00）；commit `7928df50`、`3da5d742`
- `边界`: 我明确：**A60 的表述是错的，A11 的 0.90 在审计那次是对的。**

## A114

不是同一批，我要把这几个东西切开。A11 说的 `Ed Wood`/`Shirley Temple` 被挤出，是审计那次（`7928df50`）在 HotpotQA limit=5 上逐题点出的两个 top5 regression；这个 limit=5 就是那 5 条 query。而"有回归测试"是另一件事：`tests/graphrag/test_graphrag_baseline_preserving_fusion.py` 里固化的 bad case 用的是 `Scott Derrickson`/`Ed Wood`/`Sinister (film)` 这组，断言是 `"Ed Wood" in top5` 且 `"Sinister (film)" not in top5`。

三个东西的来源：bad case 与指标来自同一个 limit=5 审计；回归测试把同一类形状固化成确定性 fixture。它们同源，但"我修复前跑的数"和"测试里的 fixture"不是一份产物。

- `事实层`: Evidence
- `证据`: `project-fact-provenance.md:92`；`tests/graphrag/test_graphrag_baseline_preserving_fusion.py`
- `边界`: 5 条 query 的具体清单：Unknown（raw report gitignored）。

## A115

今天可打开的文件里，这几个数写在两处：`docs/governance/project-fact-provenance.md`（PF-031 表格行 + 正文 92/96 行）和 `tools/evals/zuno/multihop_eval/README.md`。raw report 是 gitignore 的。所以你问的核心我认：**我只能给"转抄"，给不出 raw run**。

这不是"凭什么说它不是转抄"——它就是转抄，转抄自那份公开历史恢复。诚实结论：这几个数字**可复现性为零**；provenance 自己把 gitignored raw runtime reports 列在"不能支持"的原因里。我唯一能说的是：provenance 文档本身是这条记录的权威，我不是从别处二次转述来的。

- `事实层`: Evidence · Unknown
- `证据`: `project-fact-provenance.md:63,92,96`；`tools/evals/zuno/multihop_eval/README.md:338-341`（raw reports gitignored）
- `边界`: 独立于 README 的原始产物：不存在。

## A116

定阈值和定口径是两件事。口径（`Recall@5`/`MRR@10` 这一套）是既有 multihop eval harness 定的，我只是用它；阈值（那 9 个常量）是我在修三个 heuristic 时拍的。我在指标体系上模糊、在阈值上精确，原因不神秘：**阈值是我改过的行，口径不是我改过的行**。记忆颗粒度跟着"我有没有动过它"走。

我不否认这里有认知偏差风险：我能精确回忆的恰好是我 claim 的部分。但这不是"结果反向选择了记忆"，是"我对自己写过的代码比读过的规范记得细"。

- `事实层`: Personal Ownership · Unknown
- `证据`: `tools/evals/zuno/multihop_eval/`（既有 harness）；`platform/services/retrieval/fusion.py:9-17`（我定的常量）
- `边界`: 口径是谁定的、我参与了哪一块：Unknown。

## A117

靠机制上"应该有用"。我测出来的是**没退化**，不是**有用**。所以你那个对比是对的：在今天的证据下，"GraphRAG 这层"和"我加了一个可能没用的层"之间，**我拿不出证据把它们分开**。这正是那份 ablation 协议要回答的问题，而它现在是 BLOCKED。

但我要指出一个不对称：vector+BM25 在 comparison/bridge 上答错是从机制推的（我诚实标了），而图候选把 baseline 挤出 top5 是**被测量到的**。所以这条 bullet 的合法 claim 是"修了一个被测量到的回归"，不是"图检索有净收益"。前者留着，后者我不 claim。

- `事实层`: Current · Target · Unknown
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md`（`measurement_status: BLOCKED_PENDING_DATA`）
- `边界`: 净收益：Unknown，且 blocked。

## A118

六个字段全相等时，**没有显式的第七个 tie-break 键**。`sorted(..., key=...)` 用那六个字段组成的 tuple；Python 的 `sorted` 是稳定排序，所以最终顺序退化成输入顺序——即候选进入融合时的既有顺序（先 vector、再 bm25、再 graph）。所以它**是确定的，但不是"完全由分数决定"**：全同时会退化成输入序。

我没找到代码在对输入先做一次稳定排序来固定这一点，所以严格说"同样输入 → 同样输出"成立，"不同输入序 → 结果可不同"也成立。

- `事实层`: Current
- `证据`: `platform/services/retrieval/fusion.py:992-1021`
- `边界`: 我没构造过六字段全等的 fixture。

## A119

是的，基本是这样。`baseline_rank` 排在 `chain_score`/`graph_tier`/`graph_signal` 之前，所以图那三个信号只在 `candidate_group` 相同且 `baseline_rank` 也相同时才参与决断。而 graph-only 候选的 `baseline_rank` 是被构造出来的（`max(graph_rank-1,1)` 或 `graph_rank+1`）——它得到的不是"按图信号排"，而是"给一个可被反超的位次"。

这是设计意图的必然结果：既然 fusion 的目标是"别把 baseline 挤出去"，它就不能让图信号主导顺序。准确说法是：**图信号决定"谁进哪个 group / 拿到什么 baseline_rank"，不决定组内相对次序**。

- `事实层`: Current
- `证据`: `fusion.py:190-205`；`:992-1021`
- `边界`: 我没做"关掉图信号看排序变不变"的对照。

## A120

我实际有权决定的是**阈值**（那 9 个常量是我在修 heuristic 时定的），**方向不是我提的**——图路由、planner 图开关在我之前就在。所以"这套 heuristic 的设计者"要拆：**框架/方向的设计者不是我，具体判据和门限是我的**。要给一个"设计者"，那是"既有方向 + 我的实现"，而既有方向的具体提出者我没有记录。

我不愿意把它说成"我设计了这套 heuristic"——那会把方向权和阈值权混成一个。

- `事实层`: Personal Ownership（阈值）· Unknown（方向提出者）
- `证据`: `fusion.py:9-17`；`project-fact-provenance.md:63`
- `边界`: 方向提出者：Unknown。

## A121

这两个说法**不互斥**，但要用具体一组来分。就拿 comparison 三件套（`COMPARISON_SELECTION_SIZE=3`、`COMPARISON_MIN_SEEDS=2`）：它的**触发条件是 bad case 逼出来的**——comparison 类 query 上图候选会挤 baseline；但**具体取 3 和 2 这两个数**是为了让那类 query 的 guardrail"看起来完整"，没有 bad case 支持"为什么是 3 不是 2"。所以我 A16 说的"为让 bad case 不复现"针对的是**机制存在**，A74 说的"为架构完整性加的"针对的是**具体数值**。

我要认的错是：我两次都没把"机制 vs 数值"这个区分讲出来，所以读起来像互斥。

- `事实层`: Current · Personal Ownership
- `证据`: `fusion.py:9-17`、`:179`
- `边界`: "3/2 有没有 bad case 支撑"：没有。

## A122

**我没有任何一条不在那 5 条里的 query 能证明修复后它也没坏。** 手上没有外围证据。所以我不能排除"这个修复是对着这 5 条过拟合的"。

我能给的替代品只有单组件级回归测试（seed expansion / alias / path ranking / guardrail / chain-aware fusion 各自的 test 文件），它们固定的是"在这组 fixture 上没退化"，仍然不是"泛化"。这题的诚实答案是：**过拟合无法排除**，而排除它正是那份 ablation 协议要做的事。

- `事实层`: Unknown · Evidence
- `证据`: `rb019-graphrag-ablation-protocol.md`（holdout 未跑）；`tests/graphrag/`
- `边界`: 外围 query：一条都没有。

## A123

它是**面试流程的产物**。文件头写着：`source: red-blue rb-2026-09-15-formal-019 / IMP-019-05`、`frozen_at: 2026-10-07`、`owner: 03 Knowledge & Evidence + 09 Observability & Evaluation`。它的出处字段自己写着这是上一轮 Red/Blue 的 IMP-019-05，今天冻结的。所以 A18/A20 那套"退出条件是测量性的"论证，挂在一份**评测流程产物**上，尽管 owner 字段挂了两个产品模块名。

`measurement_status: BLOCKED_PENDING_DATA` 是谁维护的：从文件看是"冻结协议"的一部分，没有独立维护者证据；产品侧有没有人读它，我不知道。这正是我在 A80 里被 Red 抓到的同一类问题（拿评测标准当技术依据），我要在这一轮把它摆在台面上认。

- `事实层`: Evidence · Unknown
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md:1-10`
- `边界`: 产品侧读者：无证据。

## A124

和那 9 个阈值是同一根线——**都是拍的**。`graph_hop_limit=2`、`max_paths_per_entity=10` 在 planner 里从请求透传下来（`planner.py:263-264`），代码里没有依据、没有扫参；它们和 `GRAPH_PROMOTION_THRESHOLD=6` 是同一种经验值。

对那个"总延迟 = 四路之和"的推论，我确认前提：检索是顺序 await，没有 `gather`、没有超时取消。所以图这一路是纯串行增量成本，而它的两个上限也是拍的——"成本被这两个数限制住"这句话，限制的方式是我定的，不是测出来的。

- `事实层`: Current · Unknown
- `证据`: `platform/services/retrieval/planner.py:263-264`；`platform/services/retrieval/orchestrator.py:614-689`
- `边界`: 延迟/成本数字：一个都没有。

## A125

`graph_available` 是**当时算的**，不是持久化的健康位。它出现在 planner 判断里（`internal_route == "local_graphrag"` 且 `graph_available` 才开图路由），来源是这一轮的运行时判断。所以"停 true"的场景在**这一层**不成立——它不是缓存字段，是每轮重算的。但我立刻加边界：它是不是"每轮重算"，取决于调用 planner 的上游有没有传陈旧值；我没把上游读到底。

如果上游给的是缓存的 readiness（比如 `ProjectReadiness` 或 `graph_not_ready` 原因码），那"图坏了但开关还开"就可能发生。我不能排除。

- `事实层`: Current · Unknown
- `证据`: `platform/services/retrieval/planner.py:91-98,172-176,199-200`
- `边界`: `graph_available` 的新鲜度与上游所有权：没读到底。

---

## T03 Memory / Context

## A126

这个环**没有闭合**，我认。五条 bullet 里有两条（第 4、5 条）描述的是已经不存在的代码：`general_agent.py` 在 `ab1222da`（2026-08-04）被删了。所以今天"我做过"能靠的只有 commit 存在与否；而 commit 的作者字段又切不出归属。两件事叠加的结果：**这两条 bullet 今天既不可从代码验证、也不可从 blame 验证，只能靠 commit 的存在 + 我自己认领**。

我不打算用"所以我做过"收口。准确说法是：第 4/5 条的 claim 今天是 `Historical · Personal Ownership`，证据强度是"有 commit、归属靠自述"。

- `事实层`: Historical · Unknown
- `证据`: `ab1222da` 删除 `general_agent.py`；`d4e2fe2e`、`f3c74338`
- `边界`: 归属验证路径：确实闭合不了（作者不可区分）。

## A127

是，我倾向它是"typed contract 是后补的"的证据。`MemoryScope(user_id, agent_id=None, project_id=None, thread_id=None)` 是一个**冻结的 dataclass**，而运行时把 `agent_id` 永远填成 `"agent_run"`。一个 typed contract 里带着一个恒定的维度，说明这个 contract 是从"要有个 scope 抽象"长出来的，不是从"有谁真的按 agent 隔离"长出来的。

但我要收一句：单凭一个恒定维度，不能证明整个 contract 是后补的——也可能是 `agent_id` 为将来多 Agent 预留的位。区别在于**有没有对应的产品需求**，而这个我没有记录。

- `事实层`: Current · Target · Unknown
- `证据`: `platform/services/memory/layers.py:41-57`；`agent/runtime/nodes/core.py:485-492`
- `边界`: 它是不是"预留位"：无需求记录。

## A128

按我自己的口径审，五张表里**两张没有 reader**：`memory_use_traces` 和 `context_pack_versions` 在 `src/` 里只有 INSERT，没有 SELECT/UPDATE。另外三张（`memory_candidates_v2`、`memory_versions`、`memory_snapshots`）有读者。

所以 `memory_use_traces` 是纯写入侧——它记"这轮用了哪些 memory 版本"，但今天没有任何地方拿它来做事。这和 A26 里我说"痕迹存在"是一个意思，只是我当时没说它**是一个没人读的痕迹**。

- `事实层`: Current · Evidence
- `证据`: `platform/database/memory/domain.py:110`（versions INSERT）、`:171`（candidates INSERT）、`:326`（snapshots INSERT）、`:383`（context_pack_versions INSERT）、`:486`（memory_use_traces INSERT）；无 SELECT 命中
- `边界`: 我没扫 `tools/` 里的离线分析脚本。

## A129

因为简历的措辞是**在基线我之前那个代码版本**写的，而我今天意识到它按当前代码读会失准。这是一个真实的"知道却未修"。原因不是掩饰，是**简历是冻结产物**——`01_simulated_resume.md` 头部写着 `status: FROZEN`、`frozen_against_main: 7d3081f2...`。这一轮我被允许**修正说法**，但不被允许**改简历文本**，所以它留着。

这就是我在 A24 里花力气把"`prepare_context()` 今天不是函数"讲清楚的原因——我能在回答里纠正失准，不能回去改那份冻结文件。如果面试里要我负责，我会说：这句该改成"注入到回合前的上下文构建节点"。

- `事实层`: Historical · Current
- `证据`: `01_simulated_resume.md:3-8`；`agent/runtime/nodes/core.py:62`（`build_context`）
- `边界`: 谁冻结的、能不能解冻：不在我这一层。

## A130

调用方就是 canonical runtime 的 state 装配——`_memory_scope(state)` 从 `AgentRuntimeState` 取 `state.user_id` / `state.workspace_id` / `state.thread_id`，所以传值的是**运行时 state**，不是某个人手填的。所以"保护的前提是调用方传对"里的"调用方"是 runtime 内部，不是产品侧某个入口。

有没有一条测试故意传错 `workspace_id` 看会不会串读：**我没有找到**。我找到的是 scope 过滤在 SQL WHERE 里（`_scope_select` 四列等值），但我没有一条 negative test 是"错误 workspace_id → 断言读不到"。

- `事实层`: Current · Unknown
- `证据`: `agent/runtime/nodes/core.py:485-492`；`memory/store.py:520-527`（`_scope_select`）
- `边界`: 故意传错的负向测试：不存在。

## A131

它改的是**未来召回**，不是当前上下文。`REVOKED` 让这条版本在后续回读时进不了 eligible 集合（`_memory_exclusion_reason` 会把 `revoked` 剔掉）；已经进过上下文的不会被追溯改写。

所以"它和删掉这条记录有什么区别"——**在效果上，对"未来召回"这一件事，没区别**；区别只在审计：删掉会丢"这条曾存在/曾被用过"的痕迹，REVOKED 保留 lineage。这也解释了为什么要有 `memory_use_traces`——它为"已用过但后来被撤"留痕（虽然今天没人读）。

- `事实层`: Current · Target
- `证据`: `memory/engine.py:1054-1059`；`platform/database/memory/domain.py:301`；ADR-0007 §5
- `边界`: 下游结论回滚：没有自动传播。

## A132

是同一处境，而且我要说成同一句话：**`stale` 这个状态我没有找到生产者**。`_memory_exclusion_reason` 会把 `stale` 剔掉，但谁把一条 memory 标成 `stale`，我 grep 不到写入侧——`memory_state` 的唯一写入值是 `"decayed"`，`stale` 只出现在读侧的排除集合里。所以 A27 里"状态机在兜底"这句要收窄：**门在、读侧挂了、但我在生产侧指不出开门的人**——和 A43 的 epoch 是同一个形状。

这一条我要主动记账：我 Wave 1 把 `stale` 当"活的"排除依据讲了，实际我只能证明"读侧会排除它"，不能证明"它会被写出来"。这是我对 A27 的自我修正。

- `事实层`: Current · Unknown
- `证据`: `memory/engine.py:1054-1059`（读侧排除）、`:440`（唯一写入值是 `"decayed"`）；生产侧写入 `stale`：grep 无命中
- `边界`: `stale` 的生产者：缺失。

## A133

不算。ADR-0007 明确把这类东西排在 Domain truth 之外：Memory 是 optional non-authoritative provider boundary，召回项只是 `ContextCandidate`；"用户偏好用中文回复"是一条**偏好/上下文**，不是 `Matter / DocumentVersion / Claim / Evidence / Finding` 任何一类。所以 A28 那条原则（信 Domain）对**没有 Domain 字段的纯 memory 事实**不适用——因为没有对应事实可冲突。

那谁判：没有裁决点。系统对这类东西的处理是"当提示用，不让它进正式结论"——它要么被 abstain 挡在结论之外，要么只能影响风格。准确说法：**A28 只在"两边都有"时成立；只有一边时，它不构成"冲突"**。

- `事实层`: Current · Target
- `证据`: `docs/decisions/0007-reuse-first-provider-boundary.md`（optional provider boundary）
- `边界`: 判"偏好 vs 事实"的门：代码里没有独立裁决点。

## A134

我选前者是**不诚实的**，我选后者才是我能举证的位置。三个删除条件一条都不成立 ≠ 它必要；它只说明**我没举出收益，也没举出"不必要"**。所以我应该说：留着的理由是"**我没能证明它不必要**"，不是"它必要"。A30 那句"一条都不成立——这是为什么留着"读起来像第一种，我现在改成第二种。

这正是 ADR-0007 的 kill test 要回答的：没有稳定边际收益时必须允许关闭。所以留着的正当性只能挂在一份**还没跑的对照**上。

- `事实层`: Target · Unknown
- `证据`: `docs/decisions/0007-reuse-first-provider-boundary.md`（long-term memory kill test）
- `边界`: 收益对照：不存在。

## A135

我算不出"多少工作量花在那个三维上"，因为我没有工时记录——**这个数不存在**。我能给的定性是：`agent_id` 这一维在运行时恒定，`thread_id` 是会话态，`user_id` 是授权态；如果按 A78 压缩成只留 `project_id`，消掉的不是"工作量"，是**一个 contract 的一半维度**。

我要认的落差：V2 那句"typed contracts + scope 约束"读起来像"我建了四维隔离"，但其中两维（`agent_id`、`thread_id`）今天要么恒定、要么属于别的层。所以这条 bullet 的合法上限是"建了 scope 抽象与回读过滤"，不是"建了四维隔离"。

- `事实层`: Personal Ownership · Unknown
- `证据`: `layers.py:41-57`；`core.py:485-492`
- `边界`: 工时占比：不存在这个数。

---

## T04 Runtime

## A136

我读了文件头：`docs/architecture/architecture.md` 是 **Target Architecture** 文档，`status: normative-target`、`architecture_state: ACCEPTED_TARGET`，owner 写的是 `Cross-cutting Architecture Owner`；git 里最近三次改动是 2026-09-16 / 09-20 / 09-24。也就是说，它是**在 Runtime 已经建好之后**写的目标说明，不是立项依据。所以"四种失效窗口"是**事后归纳**，不是当年那次事故的立项书。

这对 A31 的影响：我说"这四种窗口是最直接的固定 workflow 不够的理由"仍成立，但我不能说"这份文档是当初上 Runtime 的原因"——时序上它是后来的。

- `事实层`: Target · Evidence
- `证据`: `docs/architecture/architecture.md:9-24`（front-matter）
- `边界`: 立项依据落在哪份文件：没有找到。

## A137

按今天的接线，它**不是约束**，是一组"被领域聚合实现了、但没有运行时执行者"的领域规则。`BranchResultFencer` 只在 `branch_result.py` 定义、`dynamic_worker.py` 使用；`DynamicStepWorker` 自己没有被 `src/` 里任何 non-def 位置引用；活的图是 `PlanExecutor` 顺序执行的。所以"晚到结果按 epoch 拒收"这句今天描述的是**能力**，不是**在跑的约束**。

唯一活着的相关守卫是 Domain 的 stale 写冲突检查（提交侧），但它管"写冲突"，不管"晚到结果"。

- `事实层`: Current · Target
- `证据`: `planning/branch_result.py`；`planning/dynamic_worker.py`；`platform/database/agent/domain.py`
- `边界`: 它什么时候接线：无法说。

## A138

是**准备这一轮回答时**发现的。我在准备 Wave 2 时重读了 `service.py:301-334`，看到 `plan_version` 只被赋 0 或 1、`replan.py` 只改 status 不动版本号。所以在 A34 自我纠正。

对你那个连带质疑——A33 那段别的内容还能不能信——我的回答是：**该降级信任，不该整段作废**。A33 里"`agent_runtime_plan_versions` 表和 `append_plan_version` 存在但无 caller"这一条我复核过（`sqlite_store.py:318` 定义、grep 无 caller），它站得住；出事的是"单调版本号是核心信号"那句，我已经在 A34 撤了。同一段里两类陈述混着讲了，这是我该修的表述习惯。

- `事实层`: Current · Personal Ownership
- `证据`: `agent/runtime/service.py:315,323,331`；`platform/services/.../replan.py`；`sqlite_store.py:318`
- `边界`: 我放弃"A33 整段可信"的辩护，改成逐条。

## A139

**今天不可能出现**——不是因为有人拦住了它，是因为执行的形态让它不发生：活的图是 `PlanExecutor` 顺序执行 step，一步走完才走下一步，所以没有"同一个 step 的旧版本结果和当前结果并存"的时刻。**晚到结果这个问题被"顺序执行"这个事实消解掉了**，不是被 fencing 解决的。

这也解释了为什么 fencing 没接线却没出事：它保护的是一个顺序执行下不存在的场景。反过来说，一旦图真的并行化，这层没接线的 fencing 就是空的——这是一个真实的前置风险。

- `事实层`: Current
- `证据`: `agent/runtime/planning/` 下 fencer 无 caller；`agent/runtime/graph.py` + `nodes/core.py`（顺序执行）
- `边界`: 将来并行化会不会暴露：推断，不是实测。

## A140

对，outbox 对我说的那个窗口一点帮助都没有。outbox 保证的是 domain 事实 + outbox 事件这一对的原子性（同库同事务）；我说的窗口是 domain 已提交、checkpoint（另一个存储）没写。outbox 覆盖"domain → 事件"，覆盖不到"domain → checkpoint"。这是两对不同端点的原子性，我把它们并列讲在同一条里，容易让人以为 outbox 是那个窗口的补偿。

正确说法：domain→事件 有同库原子性；domain→checkpoint 没有，只靠事后 `reconcile_generations` 比对。这两个补偿的适用面不同，我 A36 里没把这层分清。

- `事实层`: Current · Target
- `证据`: `agent/runtime/graph.py:17-20`；`agent/runtime/checkpointer.py`；`runtime_batch.py:220-225`
- `边界`: outbox 事件消费路径我这次没逐行读完。

## A141

按今天的代码，`reconcile_generations` **不在活路径上被调**——它在 `phase08.py:342` 定义、被 `agent/runtime/__init__.py:40` 再导出，但 `src/` 里没有一处调用它。`planning/recovery.py` 虽然被 `platform/database/agent/domain.py:34` import，但 import 的是 `PersistedStepRunSnapshot`，不是 recovery 规划器。所以 A37 那句"以 Domain 为准"今天**没有执行者**——它是被建模的规则。

这里我要把 A36 的边界补一个精度：我说"`phase08.py` 和 `planning/recovery.py` 在 `tests/` 里找不到 importer"是对的（那些 test 里的 `phase08` 是字符串，不是 import），但我该加一句：`recovery.py` 在**生产侧**是被 import 的（为 `PersistedStepRunSnapshot`），只是那些规划类没有 caller。

- `事实层`: Current
- `证据`: `agent/runtime/phase08.py:342`；`agent/runtime/__init__.py:40`；`platform/database/agent/domain.py:34`；grep `reconcile_generations` 调用点：无
- `边界`: 谁该执行它：没有证据。

## A142

在一个没有生产环境、没有 SLA、没有值班的试点里，**今天没有人点**——因为没有可点的现场。所以"人点恢复"在这个部署状态下**等价于不恢复**。这是 A38 那个答案的直接推论，我 Wave 1 没把它推到底。

我要区分"设计上的恢复路径存在"和"这条路径今天可达"：设计上它要求 pending interrupt + 最新 checkpoint + approval decision，三者齐了就能 resume；今天缺的是**人**——没人扮演 approval 的审批方。

- `事实层`: Current · Unknown
- `证据`: `agent/runtime/service.py:202,227-238`；`docs/evidence/current-runtime-baseline.md`（approval 语义保留）
- `边界`: 谁在实际环境审批：Unknown。

## A143

ADR-0005 我读了：`status: accepted`、`date: 2026-07-18`，文件里只有 status/date，没有 approver 字段。所以"谁批准的"我答不出来。**它知不知道主线跟它不一致**：我没有证据。但"不一致持续到今天没被纠正"这件事，我能从代码里确认。

那 ADR 的实际效力是什么：我的判断是**它约束了 PHASE04 的一个决策（引官方依赖），但没有约束主线图的实现**。它自己还写着"不批准永久 dual checkpointer runtime"——而今天主线恰恰是 dual（自研桥为实跑、官方 saver 只挂在 `phase08.py`）。所以这条 ADR 在实现层是**未被执行**的。

- `事实层`: Current · Target · Unknown
- `证据`: `docs/decisions/0005-official-langgraph-postgres-checkpointer.md:3-4`（无 approver）；`agent/runtime/graph.py:14-20`
- `边界`: 批准人、有没有人发现不一致：Unknown。

## A144

那条测试（`tests/repo/test_agent_system.py`）的意图是**防有人把旧架构复活**，不是防 cutover 到官方 saver。它所属的测试函数名是 `test_agent_system_has_no_archived_runtime_facades_or_phase_verifiers`，断言的是 `phase08_cutover.py` 不存在、以及 `tools/scripts` / `tests` 下不允许出现名字里带 `phase`/`legacy`/`cutover` 的文件。所以它"禁止一个 cutover 文件"的意思是：**不许再出现以 phase/cutover 命名的过渡产物**，是"清场"，不是"锁死方向"。

所以你把我 A39 里那句读成"这条测试在守护 ADR 与实现的分裂"是过度解读——它守护的是"不要有过渡期残骸"。我 A39 的表述太省，这里修正：那条测试和 ADR-0005 不是一件事。

- `事实层`: Current
- `证据`: `tests/repo/test_agent_system.py`（含对 `.agent/programs/.../PROGRAM01_real-unified-runtime-cutover.md` 的 exists 断言）
- `边界`: 它想防哪个 cutover：从函数名与断言语义看是"过渡残骸"。

## A145

在 PostgreSQL 单实例里，**技术上是可行的**——domain 表和 checkpoint 表放同一个库，就可以放同一个事务里一次提交。所以"两个引擎"在这台单实例 PG 上**不是技术限制，是架构选择**：运行时存储和 Domain 侧是两套连接/事务边界，这个分裂是设计决定的，不是 PG 挡住的。

所以我 A40 里把"能不能原子"当硬前置是对的，但我该说得更直接：**在今天的部署形态下，这个前置是可以做到的，所以收回的瓶颈不在技术，在架构选择**。我把 A40 的"我没有验证过能不能"升级为"在单实例 PG 上可行，是一个选择问题"。留一句：一旦 domain 和 runtime 分成两个库/两个服务，这个可行性就没了——那正是服务拆分证据门要管的。

- `事实层`: Target · Current
- `证据`: `agent/runtime/checkpointer.py`（独立存储）；`docs/decisions/0012-*`
- `边界`: 我没有真把两笔写进一个事务验证过。

---

## T05 Security / Effect

## A146

我是**读了这个层**，不是有人给我讲过。而且我和它有真实的代码接触点：我工作所在的那个文件（`simple_agent.py`）就是构造 `ToolInvocationGateway` 的地方（`:1287-1330`），`execute_binding_tool` 的 docstring 明确要求每次 `binding.ainvoke` 必须经 adapter 进 gateway。所以每次有 tool 调用，我的代码就是 gateway 的上游一行。

所以"不是我的 Ownership"和"细节熟"不矛盾：**我是这一层的调用方，不是它的作者**。调用方为了理解"我发出去的 tool call 到底被怎么处置"，必须读到 `_reauthorize_execute_epoch` / `assert_audit_durable_for_effect` 这一层。但我不能因为这些细节熟，就说我拥有它。

- `事实层`: Personal Ownership（调用方）· Unknown（作者）
- `证据`: `simple_agent.py:1287-1330`、`:181-211`；`capability/mcp/mcp_tool_executor_adapter.py:45,84`
- `边界`: 它是谁设计的：不知道。

## A147

窗口的上界**由中间夹了两次真实 I/O 决定**，不是代码路径长度：两次检查之间夹着 `_persist_mandatory_audit_before_effect` 的**落库 + 重读校验**，再往下才是 dispatch，而 dispatch 本身是网络/sandbox 调用。所以窗口至少包含一次数据库写 + 一次数据库读；如果中间有远端调用，还会更长。

"一定会抓住吗"——**不会"一定"**。第二次检查读的是当前 epoch 状态，所以如果撤销在第二次检查**之前**已提交，就会被抓住（这正是那条测试：在网关提交后、re-authorization 前把 epoch 改成 revoked，executor 0 次）；如果撤销发生在第二次检查**之后**、dispatch 之前，这次检查就抓不住——那段只剩 dispatch 自身的语义兜。所以我说"从代码结构读出来的"就是这个意思。

- `事实层`: Current
- `证据`: `invocation_gateway.py:432-462`（审计落库→重读→reauthorize→dispatch 的顺序）
- `边界`: 我没构造过"第二次检查之后才撤销"的竞态测试。

## A148

它是在描述**一片可执行代码**，不是"真实运行中可观察的能力"。理由是 A43 那个：`security_effective_epochs` 在 `src/` 里只有 INSERT/JOIN/SELECT，没有一处把 status 改成 `revoked`——唯一的 revoked 是测试里的裸 SQL。所以"fail-closed 已实现"的准确含义是：**消费侧（执行前的 epoch 检查）已经实现且被测试验证；生产侧（撤销的写入）不存在**。

一个状态只能由测试制造，意味着这条 fail-closed 在真实运行里**观察不到**——因为真实运行里没有那个前置条件。

- `事实层`: Current · Evidence · Unknown
- `证据`: `platform/security/persistence.py:329,382,399,593,1062`；`tests/security/test_mandatory_audit_postgres_boundary.py:835`
- `边界`: 撤销路径缺失原因：Unknown。

## A149

我今天的倾向是**补生产者**，但带条件。理由：这个状态机的消费侧是真的、fail-closed 是被测试固定住的、而且它挂在 send boundary 上——这是一个"安全属性已经有人守着、只是没人能触发撤销"的形状。撤销权应该由 08 Security 的 lifecycle policy 拥有（ADR-0007 把 Secret / lifecycle policy 划给了 08），所以补的是"08 里一个把 epoch 置 revoked 的合法入口"，不是给我这一层补。

如果补不上，那就退到"承认它不该有独立对象"——但我不倾向这个，因为 fail-closed 这条属性有价值，不该因入口缺失而被删。**会明年还在吗**：按今天没有 owner 去补的状态，它很可能就停在"门在、没人转锁"。

- `事实层`: Target · Unknown
- `证据`: `docs/decisions/0007-*`（08 拥有 lifecycle policy）；`platform/security/persistence.py`
- `边界`: 谁该补：没有排期，是我的判断。

## A150

**在活路径上被调**。`assert_audit_durable_for_effect` 定义在 `foundation.py:1747`，调用点在 `invocation_gateway.py:1499`，而它的上游 `_persist_mandatory_audit_before_effect` 在主 execute 路径的 `:432` 被调——就在每次真实 dispatch 之前。所以这一条和 `BranchResultFencer` 不一样：**它是接线的**。

这很重要，因为它把 A35/A47 那些"写了没接"的清单**切出一个反例**：这个系统的安全性层不是全都没接线——gateway 的审计前置校验是活的，缺的是它下游的"远端对账"和它上游的"epoch 撤销"。

- `事实层`: Current · Evidence
- `证据`: `invocation_gateway.py:432,1499`；`platform/database/foundation.py:1747`
- `边界`: 我没跑过它的 end-to-end。

## A151

判据是**进程内标志**。`DispatchCertainty` 是在 `ToolRuntimeBatch.cancellation(...)` 里从 `provider_stop_confirmed` 这个布尔入参算出来的：`NOT_DISPATCHED if provider_stop_confirmed else MAYBE_DISPATCHED`。所以 `NOT_DISPATCHED` 的成立条件就是上游给了 `provider_stop_confirmed=True`。

那**进程崩了之后它还成立吗**——如果那个 `True` 只来自进程内判断、没有对应耐久事实，那**不成立**；它必须在恢复时重新由耐久证据推出。我没有逐行读 `provider_stop_confirmed` 的赋值来源，所以我只能说到这里：判据在这个函数里是进程内布尔，是否被耐久化取决于调用方。

- `事实层`: Current · Unknown
- `证据`: `capability/tool_runtime/runtime_batch.py:52-55,241,465-467`
- `边界`: `provider_stop_confirmed` 的赋值来源：没读到底。

## A152

一次真实的 UNKNOWN effect 今天会**停在 OPEN reconciliation**：系统开一条 OPEN，落对账查询描述（被 hash），然后……没有东西推它。`escalate_due_reconciliations` 只在测试里被调（A110），所以它不会自动变成 ESCALATED。要往下走，只能靠人工 `record_manual_effect_assessment`——而这在一个没有现场的制度里也没人做。

所以终态是：**OPEN，停住**。`record_manual_effect_assessment` 是唯一能给出确定性结论的入口（只在结论是 `CONFIRMED_EXECUTED`/`CONFIRMED_NOT_EXECUTED` 且残留不确定性为空时才 resolve，否则拒）。

- `事实层`: Current · Evidence · Unknown
- `证据`: `invocation_gateway.py:1607-1618,1787`；`platform/database/tool_runtime/domain.py`
- `边界`: 有没有人工真的做过：无证据。

## A153

**是缺口的性质，不是设计意图。** 设计意图是"确定没执行才重发"；而"确定没执行"的**技术路径**（远端查询）没实现，只留了人工评估作为出口。所以安全守卫在实现上依赖一个人工动作——如果没人做，一个 UNKNOWN effect 永远不能被安全重发（只能停在 OPEN）。这在设计上是 fail-safe 的保守，在实现上是"一条没接通的安全链"。

我要把它和 A7/A96 合成一句话：**重发安全性的三个环节里，有一个（对账执行）是空的**。所以"安全"今天是"发不出去也收不了口"。

- `事实层`: Current · Target · Unknown
- `证据`: `runtime_batch.py:460`（`retry_same_effect_allowed = conclusion == CONFIRMED_NOT_EXECUTED`）；`invocation_gateway.py:1787`
- `边界`: 这是设计缺口还是暂缓：没有决策记录。

## A154

代码支撑的是一个**通用法律/文档 RAG + Agent 平台**，法院侧的场景标签没有代码支撑。我 grep 过 `src/backend/zuno` 里 `court|法院|judicial|审判|立案`——**零命中**。真实对外的动作是 SMTP 邮件、物流 HTTP 查询、Lark 消息。所以简历里"面向天津法院智慧平台相关场景"这句，**代码支撑的是一个通用法律 RAG 被贴了法院场景的标签**。

我要给这个判断加个边界：`docs/project/reference.md` 写着 Zuno 与天津法院相关场景有关系、且不是整个智慧法院项目。所以"相关场景"这个措辞本身是准的；失准的是"面向天津法院智慧平台"读起来像深度集成。我该改成"面向法律文档场景、与智慧法院相关场景有关联"。

- `事实层`: Current · Evidence
- `证据`: `grep -rniE "court|法院|judicial|审判|立案" src/backend/zuno/` → 无命中；`docs/project/reference.md`
- `边界`: 法院侧代码在不在仓库外：不知道。

## A155

我没有证据说这些真对外的动作**真的发出去过**——我只能说**代码真的会发**：`smtplib.SMTP_SSL/SMTP` 真连、`urllib.request.urlopen` 真打、MCP server 里是真 `lark_oapi` 客户端。至于发给谁、在哪个环境，我答不出来——**没有生产环境，也没有发送日志给我看**。

所以准确说法：**"代码路径是真的"和"动作真的发生过"是两件事**，我 Wave 1 里把它们讲得有点近。前者我能举证（源码），后者我不能（没有 trace / 没有收件人记录）。这是一个我要收的边界。

- `事实层`: Current · Evidence · Unknown
- `证据`: `capability/tools/send_email/action.py`；`capability/tools/delivery/action.py`；`capability/layer.py`
- `边界`: 实际作用对象：Unknown。

## A156

我核对了证据引用，**我 Wave 1 引错了文件**。那些负向历史 #201/#203/#205/#207 **不在** `docs/evidence/implementation-wave-001.md` 里——那份文件讲的是 TASK-001（Domain mutation）和 TASK-003（Citation provenance）。#201/#203/#205/#207 实际在 `docs/evidence/current-test-baseline.md`，以及 `docs/evidence/README.md`、`docs/governance/effect-security-slice-c-review.md`。

这份文档是谁写的、什么时候写的：`current-test-baseline.md` 是一份 Current Test Baseline，绑在快照 `5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660` / run `35516807526` 上。那些编号是**未合并的 test-only 诊断分支产生的 PostgreSQL fault probe 负向证据**，文件里明说它们不进入 main、都使用 test-only Alembic compatibility alias。所以它们是**在 fault probe 里真的跑出来的**，不是纯命名条目；也确实是被复盘整理进 Evidence 的条目。两者都真。

- `事实层`: Historical · Evidence
- `证据`: **修正**：`docs/evidence/current-test-baseline.md:134,162,166,183,213,244,269,271,306`；`docs/evidence/README.md`；`docs/governance/effect-security-slice-c-review.md`
- `边界`: A48/A49 里引用的 `implementation-wave-001.md` 是错的，我在此更正。

## A157

我给出那个重构方案，依据是**"我是它的调用方"**——我读过它（A146），但我不是它的 owner，所以我给的是**观察 + 判断**，不是"我会怎么改我自己的东西"。这一点我在 A50 开头就划了，但你问得对：观察者给的方案不等于有权给的方案。

具体后果：如果把 execution receipt 折进 effect certainty，会失去的是**"发出去"和"改了现实"之间的那层区分依据**——`DispatchCertainty` 有三档（NOT_DISPATCHED / DISPATCHED / MAYBE_DISPATCHED），`EffectCertainty` 是 CONFIRMED_EFFECT / NO_EFFECT / UNKNOWN_EFFECT。两轴不同构：一个"发出去了但结果未知"的调用，合并后会只剩"UNKNOWN_EFFECT"，而**"要不要重发"需要的是 dispatch 那一轴的 certainty**。所以合并会丢掉 `MAYBE_DISPATCHED` 这个分辨力——而它正是"已发出、未知，重启后是否被错误升级成 completed"那条负向证据依赖的那一档。

- `事实层`: Current · Target
- `证据`: `capability/tool_runtime/runtime_batch.py:52-55`、`:450-455`；`docs/evidence/current-test-baseline.md:134,162`
- `边界`: 我没做合并的影响测量。

---

## T06 Project History

## A158

是，**唯一的非文档物证我也找不到独立的那一个**。git 从 `eafeb1c2`（2026-04-15）开始，而"3 月已存在"的唯一依据是 `docs/project/reference.md` 里"user joined around 2026-03""project and code already existed; a simple custom frontend already existed"。这份 reference 的 owner 字段是 `Project Documentation Owner`，`provenance_source: docs/governance/project-fact-provenance.md`。

有没有非文档物证：我找不到。所以"3 月已经有系统"这句话的支撑是**文档自述**。我要说清它和"我编的"不一样——它是 canonical 文档里的一个已接受事实；但它的**独立可核性**是零。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md:8,16-21`；`git log --reverse`（首个 commit `eafeb1c2` 2026-04-15）
- `边界`: 非文档物证：没有。

## A159

规则我给出：**commit 只在"存在性"上算数，不在"归属"上算数**。当我说"这件事发生了（一段代码被加/被删了）"，commit 是充分的；当我说"这是**我**做的"，commit 永远不充分，因为作者字段把人压成一条谱系（同一邮箱 + 自动化账号混在一起）。

所以 Red 说"有利时够、不利时不够"——我接受这个观察，但我想指出它不是双标，是**两个不同的断言用同一份证据**：一笔 commit 能证"发生了什么"，不能证"谁做的"。我 A53 里主张归属时其实偷用了 commit，我该把 A53 的措辞统一成"存在性 + 我的自述"。这条规则我认，并接受它削弱 A53。

- `事实层`: Historical · Unknown
- `证据`: `git shortlog -sne`（作者谱系）；`docs/project/reference.md:16-27`
- `边界`: "谁做的"：结构上不可切。

## A160

我没有证据说那一个月我在提交——因为**提交归到同一条谱系下就切不出来**。所以"没提交"和"提交了但归到统一身份下"这两种，我分不开。你由此推出"你'第一笔'的判断建立在不可靠的作者字段上"，**这个推论我接受**：我说"我最早能自证的改动是 `77346758`"，严格讲是"我能自证的**一笔**"，不是"我的**第一笔**"。

所以 A52 里"真正的第一笔：Unknown"这句是诚实的，但 A55 里"2026-03 到 04-15 历史里没有我的可辨识痕迹"这句要收：它不是"我没提交"，是"我辨识不出来"。

- `事实层`: Historical · Unknown
- `证据`: `git log --reverse`；作者谱系不可分
- `边界`: 那一个月的提交：不可辨识。

## A161

**按我自己的判据，它不满足。** 这个追问是对的：我说留第 2 条是因为"claim 和证据匹配"，但这个 0.90/1.00 的矛盾、A17 的不可复现、A16 的无依据阈值，全挂在它上。所以按"claim 和证据匹配"这个词，它挂的不是匹配，是**"五条里相对最好"**。

我要把 A60 的判据改准确：留第 2 条不是因为它匹配，是因为它**唯一有一条"被测量到的 bad case → 修复 → 回归测试"三段链**；但它的**指标**不可复现、**阈值**无依据。所以更诚实的措辞是"五条里唯一有回归测试固定住的"——我在 A60 的"边界"里其实写了（"bounded regression fix"），但正文里用了更强的"claim 和证据匹配"。这一条我改。

- `事实层`: Personal Ownership · Evidence
- `证据`: A113/A17/A16 的证据；`tests/graphrag/test_graphrag_baseline_preserving_fusion.py`
- `边界`: 我把"匹配"改成"五条里唯一有回归测试"。

## A162

除了 `77346758` 的 diff，我找得到**残骸**，找不到"它在跑"的证据。残骸：`MCPAgentTable` + `api/v1/mcp_agent.py` 的 CRUD 面今天还在（`platform/database/dao/mcp_agent.py`、`models/mcp_agent.py`）；`multi_agent_enabled` 字段还在（而且有 reader，见下一题）。

但"曾经在跑"的独立证据（它的测试、它的 API 调用记录）我没有。准确说法：**它存在过**（diff 与残骸都证明），**它是否在跑过**——没有证据。

- `事实层`: Historical · Evidence · Unknown
- `证据`: `77346758`；`platform/database/dao/mcp_agent.py`、`models/mcp_agent.py`；`api/v1/mcp_agent.py`
- `边界`: 运行证据：无。

## A163

这里我要**修正 A54 的一个错**。我说 `multi_agent_enabled` "没有任何 reader"——**错了**。它至少有一个 reader：`src/backend/zuno/product/runtime_batch.py:428`，在一个校验里——`if fixture.task_request.multi_agent_enabled: errors.append("Product Surface must not become a second controller")`。也就是说，这个字段被读的地方，是**一个"产品面不许变成第二个 controller"的断言**。另外 `api/services/workspace.py:188` 也把它从 task 透传下去，DTO 在 `api/dto/completion.py:10`、`api/dto/workspace.py:134`。

所以多 Agent 的残骸比我说得更明确：不只是"字段没人读"，而是**有一条校验明确禁止它在产品面开启**。这强化了"单 Agent 是撤退/收口"的判断，不是"从未有过多 Agent 设计"。谁做的、为什么撤回：我没有记录。所以简历说的"单 Agent"是**这个撤退的结论**，不是当初的选择。

- `事实层`: Current · Evidence · Unknown
- `证据`: `product/runtime_batch.py:428`、`:243`；`api/services/workspace.py:188`；`api/dto/workspace.py:134`；`simple_agent.py:252,288`
- `边界`: 撤回的历史原因：Unknown。**修正 A54。**

## A164

我指一个最窄的：`5d9b719e`（2026-06-20）"Add baseline-preserving GraphRAG fusion"，紧随其后同分钟的 `c7814793`（seed expansion）、`c17f737f`（alias）、`762ffdc7`（path-aware）。这四笔是我能指认的 heuristic 落点——它们各自有对应测试。所以"三个 heuristic 是我实现的"，我能指到 **commit 粒度 + 测试粒度**。

但你那个类推我接受：这和我批评别人的"归属不可切"**是同一处境**——我能指 commit，指不出 hunk 级（不像那个小 hunk）。差别只有程度：这里 commit 与 heuristic 是 1:1 命名的，所以指认力比宽 commit 强。

- `事实层`: Personal Ownership · Historical
- `证据`: commit `5d9b719e`、`c7814793`、`c17f737f`、`762ffdc7`（均 2026-06-20）
- `边界`: hunk 级归属：切不出。

## A165

typed contract / 版本 / receipt 这套**在我加入第一个月不存在**。它们出现的时间我能圈一个区间：`PlanVersion` 相关的领域聚合在 `agent/domain/task_contracts.py`，`SecurityEpoch` / `PreparedAction` / `EffectReceipt` 在 `capability/tool_runtime/` 与 `platform/security/`。**出现的时候我在不在**：我在项目里，但**我没有参与这一套的建设**——我的落点是产品侧的 tool 配置注入和检索 heuristic，不是这些领域对象的建模。

所以"scoped Context/Memory V2"这条 bullet 描述的是**Memory 那一版的 typed contract**（`MemoryScope` / `MemoryCandidate` / review 状态），不是 PlanVersion/SecurityEpoch 那一套。这两套我不混。至于是不是我建的那一版：Memory 那一版有我的 commit（`d4e2fe2e`/`f3c74338`），PlanVersion/SecurityEpoch 那套没有。

- `事实层`: Historical · Personal Ownership · Unknown
- `证据`: `platform/services/memory/layers.py`（MemoryScope）；`agent/domain/task_contracts.py`（PlanVersion）；`capability/tool_runtime/`
- `边界`: 它们被引入的日期：我没逐笔定位。

## A166

接口的话，我得诚实：**没有哪个跨模块接口是我定的**（哪怕一小块）。我能指的最靠近"接口"的是 `execute_binding_tool` 的签名——它是一个模块级 helper，参数是我扩的（显式 user_id/tenant/workspace/run/step/trace），但它不是一个跨模块 contract。所以我接受"局部改动的实现者"这个定位。

我不想把它说得比它小：我在检索 heuristic 那一层是**判据的定者**，那是比"实现者"多一点、比"接口设计者"少一点的位置。但按你问的"接口"这个词，答案是没有。

- `事实层`: Personal Ownership · Unknown
- `证据`: `simple_agent.py:160-176`（我扩的参数面）
- `边界`: "接口"的严格定义下：零。

## A167

"约 7–8 人"来自 `docs/project/reference.md`：`core R&D team: approximately 7–8 people based on currently recoverable evidence`。所以这是**文档**给的，owner 是 Project Documentation Owner。它怎么定义"核心"、是全员还是快照——**reference 没写**。而且措辞本身是 `based on currently recoverable evidence`，就是"按当前可恢复证据估计"，这已经承认它是一个**估计**，不是名册。

所以我不能把它当日名单用。它是个量级。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md:21`
- `边界`: "核心"的定义 / 是否快照：文档没写。

## A168

没越过。"定位并修复 GraphRAG 排序回退"——定位（有 bad case）、修复（有实现）、回退（ranking displacement）——三个词都在上限内。它有"更好"吗？没有。所以措辞和上限一致。

那为什么 A60 还要专门加一个上限：因为**读简历的人会自己加**——一份写着 GraphRAG 的简历，读者容易默认"GraphRAG 有收益"。我加上限不是因为我越界，是为了**堵住读者的默认闸门**。这是对"措辞没越界但容易被误读"的处理。

- `事实层`: Personal Ownership
- `证据`: `01_simulated_resume.md:23`；A60 边界
- `边界`: 无。

---

## T07 Pilot / Court

## A169

我不知道那句话是谁写的——它是简历文本，和 `docs/project/README.md` / `reference.md` 的里程碑序列一致（existing product/code → internal demo → customer/smart-court demo → quality feedback → iteration → court-side testing → Pilot Validation）。所以写它的人依据的是**项目侧里程碑文档**，不是法院侧的文书。

细节（发起方、在场、规模、题集）全不可恢复，是因为项目事实表明确写"测试规模、题集、参考答案、Reviewer 协议未恢复""Pilot 环境、用户、时长、验收材料"未恢复。所以写这句话的人依据的**不是证据，是里程碑定性**。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md:22-25`；`docs/governance/project-fact-provenance.md`（PF-018/PF-019）
- `边界`: 作者：Unknown。

## A170

**一件都没有**——不是"我没找过"，我找过：项目事实表把"客户 Bad Case、Issue、调试记录、前后指标""测试题、记录、评价表""Pilot 环境、用户、时长、验收材料"全部列在**未恢复**那一栏。唯一一条用户侧文字是那句汇总反馈"回答质量还需要提高"。

所以物证清单是：一条汇总反馈。一条聊天记录、一张截图、一个日志时间戳——我没有。我要区分"我没找过"和"没有"：这两种在 provenance 里的形态不一样，这里是后者（文档自己写了未恢复）。

- `事实层`: Historical · Unknown
- `证据`: `docs/governance/project-fact-provenance.md`（PF-017/018/019）
- `边界`: 物证：一条汇总反馈，其余无。

## A171

它是**我们内部给自己定的里程碑名**。"Pilot Validation"出现在 `docs/project/README.md` 和 `reference.md` 的里程碑序列里，没有一份法院/甲方文书用过这个词（我没有找到）。所以它和"我们做完了一轮试点"在语义上是同一个东西——**它的重量就是"我们做了这个动作"，不是"第三方判定通过"**。

而且文档自己补了 "Pilot Validation does not establish Production"，等于承认这个词的上限。

- `事实层`: Historical · Evidence
- `证据`: `docs/project/reference.md:24-25`；`docs/project/README.md`
- `边界`: 有没有法院侧用过这个词：无证据。

## A172

如果结论只有"还要提高"，那它验证的是**"流程能跑通"**，不是"质量达标"。这是合法的一种 validation——**一个试点可以验证"系统能被用起来"而不验证"用得好"**。所以我不该把"Validation"这个词的空洞感当作它在撒谎；它验的是可运行性。

但我要收一句：既然只有一条汇总反馈、没有题目集和验收协议，"流程能跑通"这件事**也没有独立证据**——它仍然是里程碑文档自述。准确说法：**Pilot 验证的是"项目侧认为流程跑过一轮"**。

- `事实层`: Historical · Unknown
- `证据`: `docs/governance/project-fact-provenance.md`（PF-017）
- `边界`: 验了什么：无独立证据。

## A173

`224 passed` 是**被截取的一个 CI run**：`current-test-baseline.md` 头部写着 `verified_code_snapshot: 5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660`、`workflow_run: 35516807526`、`selected_suite: 224 passed`，而 `implementation-wave-001.md` 写 `Full CI: FULL CI NOT RUN`。所以"某次跑过"是准确的，"从没跑全过"也是准确的——**它们不矛盾，因为 224 是 selected suite、不是 full CI**。

为什么材料上呈现的是前者而不是后者：因为"selected suite 224 passed"是绑定 SHA 的 Current 证据，而"full CI not run"是一条限制。呈现的选择在于**把限制和证据并列**，而不是"只报喜"。这两个数**同时**在那两份文档里，不是藏了一个。

- `事实层`: Evidence
- `证据`: `docs/evidence/current-test-baseline.md`（snapshot / run / 224 passed）；`docs/evidence/implementation-wave-001.md`（FULL CI NOT RUN）
- `边界`: 谁挑的、为什么挑这个 suite：文档没有署名那一节，我不知道。

## A174

我举不出来。**一条都举不出来**——法院侧某个人给过某条要求、提过某个问题形状，我没有这样的记录。所以"题目集和验收标准是不是我们自己出的"这个问题，我不能反过来举证说"不是自证"。

我能给的只是逻辑上界：项目事实表把"已恢复测试规模、题集、参考答案和 Reviewer 协议"放进"不能支持"栏。这意味着**连"法院出过题"这句话都不能说**。所以我选：不做反向举证，接受"自证无法排除"。

- `事实层`: Unknown
- `证据`: `docs/governance/project-fact-provenance.md`（PF-018）
- `边界`: 第三方标准：零条。

## A175

那些标签写在 `docs/evidence/` 三份文件里：`current-runtime-baseline.md`（`CURRENT / QUALITY_NOT_ESTABLISHED`）、`current-eval-baseline.md`（`MEASUREMENT_BLOCKED`）、`current-test-baseline.md`（一长串 status token + `QUALITY_NOT_ESTABLISHED`）。owner 是 09 那一侧。`PRODUCTION_READINESS: NOT_ESTABLISHED` 出自 `implementation-wave-001.md`。

你问"是不是从头到尾自证"——**是**。这些标签是**项目侧自己贴的证据边界**，不是第三方审计。所以"这不是生产"这个结论的证据链，确实是自证。但我要指出一个不对称：这些自证标签的**方向是往下的**（自己承认没生产），"回答质量还需要提高"是往下的，"NO EVIDENCE / NOT ESTABLISHED"也是往下的。骗人往上自证和往下自证的难度不同——但这不改变你的结论：**它是自证**。

- `事实层`: Evidence · Unknown
- `证据`: `docs/evidence/current-runtime-baseline.md`；`current-eval-baseline.md`；`current-test-baseline.md`；`implementation-wave-001.md`
- `边界`: 第三方审计：不存在。

---

## T08 Simplication / Delete

## A176

你抓得对——**我能做 import 图扫描，A71 说"没统计过"是不一致的**。我在 A33/A35 里做的正是"grep 调用方"，那套方法对 05/07/09 同样适用。所以 A71 的"没统计过"不是能力问题，是**我没做**。

我顺手补一个现在就能给的印象：07 Model Gateway 的调用点收敛在需要真实模型调用处；09 是横向被引用；05 的语义落在 `capability/` 而执行语义在 `tool_runtime/`。但这些话说出来仍然是印象——**要坐实就得跑一次 `grep -rn`**，那正是 A71 该做而没做的。

- `事实层`: Current · Personal Ownership（方法）
- `证据`: 无（我承认没做）
- `边界`: 调用方计数：**没做过**（不是"做不了"）。

## A177

合并第一天会没人负责的是**"能力/技能的资格判定权"**。05 的 authority 是 `CapabilityVersion / ProviderBinding / Conformance / Eligibility`；如果第一天就把它并进 06，那"一个能力算不算 eligible"就没有 owner 了——06 管的是 effect 语义，不是能力的资格。

所以 A73 说的"接管不是无损"具体落在这里：06 能接住"工具怎么跑"，接不住"能力够不够格用"。迁移必须先把 Eligibility 的判定搬过去、并明确它的新 owner，否则第一天就是真空。

- `事实层`: Target
- `证据`: `docs/decisions/0007-*`（05/06 Owner 定义）；`docs/modules/README.md`
- `边界`: 我没做合并的可行性核对。

## A178

两点我分开答。**第 2 条 bullet 的核心工作是止血**——`Ed Wood`/`Shirley Temple` 被挤出 top5 是一个被测量到的回归，修它是止血。而 A74 里我认的"为架构完整性加的"是**fusion 里那套 guardrail 阈值层**（comparison/bridge/genealogy 三组 9 个常量），那是**服务于第 3 条 bullet**（多跳图检索优化），不是第 2 条。所以"止血"和"架构自嗨"不在同一条 bullet 上。

我要认的是：我 A74 里把这两件事都挂在"我的 GraphRAG 工作"下讲，边界没划清，读起来像我在给第 2 条埋雷。实际是：第 2 条 = 止血（有 bad case）；第 3 条的一部分 = 无 bad case 的 guardrail（A16 的 9 个阈值）。

- `事实层`: Personal Ownership · Current
- `证据`: `fusion.py:9-17`；`tests/graphrag/test_graphrag_baseline_preserving_fusion.py`
- `边界`: —

## A179

我依据的是**行为像，不是名字像**。我说 05 与 06 重叠，理由是：05 的语义对象（Capability semantic contract / ProviderBinding / Eligibility）在今天的代码里**没有独立的运行时行为**——工具怎么跑、effect 怎么记、失败怎么对账全在 06（`capability/tool_runtime/`）。所以"两个 authority 重叠"的依据是"谁在实际执行"。

但我要承认这个依据的弱点：**"找不到记录"意味着我也不能排除"05 当年确实有独立 authority，只是今天退化了"**。所以我给的是"今天重叠"，不是"当年就冗余"。这正好和我 A75 里说的"当年为什么单独设 05 我没找到记录"一致。

- `事实层`: Current · Unknown
- `证据`: `docs/modules/README.md`；`capability/tool_runtime/`
- `边界`: 当年动机：Unknown。

## A180

**纯推演，没有历史支撑。** 我举不出一次真实的合并/重构出现过那两个形状中的任何一个。我说 04+05+06 合并会让 `UNKNOWN_EFFECT` 不降级这条边界泡软，是**从"拥有者变了、语义会被宿主吸收"这个一般规律推的**；说 08+09 会变"先记录再拒"，是从"fail-closed 逻辑 + 记录逻辑混一起"推的。

唯一沾边的是那条"缺 durable proof 也 dispatch"的负向证据——但那不是合并造成的，是 wiring 缺失。所以我不能拿它当"合并会复现"的证据。我把 A76 的措辞降级为"推演"。

- `事实层`: Target · Unknown
- `证据`: `docs/evidence/current-test-baseline.md`（那条负向证据，但不是合并场景）
- `边界`: 历史支撑：没有。

## A181

按同样的口径我答：checkpoint 桥里"和 Domain 对账"那部分**今天不在跑**。`reconcile_generations` 定义在 `phase08.py:342`、被 `agent/runtime/__init__.py:40` 再导出，但 `src/` 里零调用（A141）。所以它和 `BranchResultFencer` 是同一份"写了没接"清单上的成员。

这直接修正 A77：我在 A77 里说 checkpoint 桥"有相当一部分是包壳，但里面对账那部分是真 delta"——"真 delta"指它是**框架没有、Zuno 自己写的**，这一点成立；但我漏了它**没接线**。所以准确说法是：**真 delta，但没跑**。

- `事实层`: Current
- `证据`: `agent/runtime/phase08.py:342`；`agent/runtime/__init__.py:40`；grep 调用点：无
- `边界`: —

## A182

我答不出"还有多少个"——**我没有逐字段核过 typed contract 的每个维度有没有消费方**。`agent_id` 是我唯一核过的（写死 + 无消费方）。所以 A78 里"scope 是四元组合"这个描述，**结构上是照定义念的，语义上是照运行值讲的**——四元在 dataclass 里是真的，但"四维各自承担隔离"这个语义我只对 `project_id`（=workspace_id）和 `user_id` 有把握。

我给你的诚实答案是：**"四元组合"这句话里，照结构念的成分多于照语义讲的成分**。这是你问的那个比例，我认。

- `事实层`: Current · Unknown
- `证据`: `platform/services/memory/layers.py:41-57`
- `边界`: 其他死字段：没有核过。

## A183

我给一个直接的答案：**技术判断在前，标准在后**。我判断 09 写不出删除条件，是因为我读了 `docs/modules/README.md` 和 `architecture-views.md` 之后，发现 09 的语义对象（telemetry/eval projection、DatasetVersion、EvalRun、ReleaseEvidence）**没有独立的运行时行为**——它是一个证据存放地。这个判断不需要看那份面试标准。

但你问的第二问我要认真答：**我的"边界"字段有多少是按那份标准写的**——**是有的**。`interview-acceptance-standard.md` 里"「太像设计出来的项目」信号"一节列了"Receipt 太多但说不清哪个 failure 需要它""所有设计都未来可扩展却没有 delete condition"这几条。我在写 A80 和 A29/A50 的"边界"时，确实在用这套语言组织自我削减。也就是说：**技术判断是真的，但"边界"字段的形态被评测标准塑造过**。这一点我不否认——它正是 Red 在 A80 上抓到的 handle，我在这里认。

- `事实层`: Current · Personal Ownership（自我审查）
- `证据`: `docs/governance/interview-acceptance-standard.md`（"太像设计出来的项目"信号）；`docs/modules/README.md`
- `边界`: 哪些边界是我独立得出的、哪些被标准塑形：我不能逐条分开，但比例上"减少自身 claim"这个方向是被标准强化的。

## A184

在我今天的判断里，09 **更像一个证据存放目录，不是一个模块**。它没有独立运行时行为——它的产物是 projection / dataset / eval run / release evidence，都是"对别的模块的记录的整理"。所以"模块"这个身份是谁给的：是 `architecture.md` 的九模块责任域划分给的。**它作为"模块"的身份来自架构文档的编号，不来自独立的运行时边界**。

我要克制一点：这不是说它该删。ADR-0007 把 09 排成 Owner（拥有 complexity kill test）——**如果它承担"复杂度 kill test"这个职责，那它就不是纯存放地**，而是一个治理判断的持有者。所以更准确的说法是：09 的"模块"身份今天一半是证据目录、一半是 kill test 的持有者；前一半可以并，后一半得留。

- `事实层`: Target · Current
- `证据`: `docs/architecture/architecture.md`（九模块）；`docs/decisions/0007-*`（09 拥有 complexity kill test）
- `边界`: 它有没有独立运行时行为：从代码看没有。

---

## T09 Knowledge / Retrieval

## A185

按 A33/A35 的口径我答：**产品侧那条链（pipeline 表：file status + task status + stage）今天有读者**——它由 ingestion 异步运行时推进，`platform/services/pipeline/models.py` 定义、`knowledge/ingestion/async_runtime.py` 写入。所以它不像 `BranchResultFencer` 那样是死的。

但我要收一句：A81 里我说"产品侧那条链是不是还在被使用，我也没有确认"——这句我这次**部分确认了**：有写入侧、有 state 定义；但我没有确认**它是否还是检索侧的权威**（那更像严格知识域的 snapshot/version 链）。所以两条链都在动，只是权威不同。

- `事实层`: Current
- `证据`: `knowledge/ingestion/async_runtime.py`；`platform/services/pipeline/models.py`
- `边界`: 谁是检索的权威：严格知识域链（ACTIVE snapshot）。

## A186

**cutover 和检索读的是严格知识域那条**——`KnowledgeVersion` 的 `READY`/`ACTIVE`：cutover 只接受 `READY`/`ACTIVE`，检索拿不到 ACTIVE snapshot 会明说。而硬编的 `"ready"` 是**产品侧 RAG handler 的健康位**（`platform/services/rag/handler.py:486,489`：`health_status or "ready"`），不是知识域的状态。

所以"谁在防它们的漂移"——**没有人**。这是两个同名不同源的状态，一个来自 `mark_ready`（有硬前置），一个来自 handler 的默认值 `"ready"`。它们没有同步机制。

- `事实层`: Current
- `证据`: `platform/database/knowledge/domain.py:296,309`（`mark_ready` 及前置）；`platform/services/rag/handler.py:486,489`
- `边界`: 我没找到任何把它们对齐的代码。**顺带修正 A81**：A81 把硬编 `"ready"` 归到 `agent/contracts.py:47`，真实位置是 `platform/services/rag/handler.py:486,489`。

## A187

**是的，从来没有成立过**——"用户点得到引用"这件事在这个产品里没有实现：服务端 `api/v1/` 里只有一个把 citation 投影成 id 列表的端点（没有 span 解析端点），前端把 citation 渲染成纯文本 chip，没有 click handler。

那个"从文档进来到用户点得到引用"的前提，**是我在回答里接受并复述的**——它是那道题的题干给的状态链终点，我顺着讲下来了，没有当场指出"这个终点其实没实现"。这是我在 Wave 1 该纠而未纠的一处。答案是：前提是题面给的框架，我接受得不对。

- `事实层`: Current
- `证据`: `src/backend/zuno/api/v1/product.py:474-496`（只投影 citation id）；前端 citation chip 无 click handler
- `边界`: 有没有别的客户端实现：无证据。

## A188

是**一个没人收敛的洞**，不是设计。`source_span_id` 这个身份字段能承载多种语义（span id / chunk id / block id / span dict 的哈希），意味着"身份相等"对不同写入方不是同一件事。所以如果将来要做点击定位，**这些语义必须先统一**，否则 `id ==` 蕴含不了"同一段位置"。

我 A90 里已经点过"id 相等不蕴含位置相等"——这里补"为什么"：因为 id 的生成方不唯一。收一句边界：我没有逐个写入方核对它们各自用哪种语义，所以我给的是"它承载多种语义"这个观察，不是"每种各占多少"。

- `事实层`: Current · Unknown
- `证据`: `knowledge/agentic_graphrag.py`；`agent/runtime/synthesis/citation_binding.py`；`knowledge/provenance.py`
- `边界`: 各写入方的语义分布：没有核对。

## A189

按我的口径答：`evidence_stale` 这个标记**今天没有消费方**。它是在 `CitationProvenanceGuard.validate` 里作为一个校验结果返回的，而下游我找不到"读到 STALE 之后做什么"的代码——所以它和"这条引用已经废了但没人知道"在**效果上**没区别，区别只在"有人去查时能查出来"。

对比一下：源被删那条路更硬——`mark_source_deleted` 会把 `citation_eligibility` 改成 `'REJECTED'`，而 `'REJECTED'` 是**会被 SQL 过滤掉的**，所以它是**有消费方的**。同一个系统的两种失效标记，一个接线、一个不接线。这个对比我 Wave 1 没讲出来。

- `事实层`: Current · Unknown
- `证据`: `knowledge/provenance.py`（validate 返回 STALE）；`platform/database/knowledge/domain.py:669`
- `边界`: 有没有服务端消费 STALE：没有找到。

## A190

按我的口径：**abstain 这条路径是接线的**。`grounded_answer.py` 产出 `Abstain: unsupported claims remain` / `Insufficient cited evidence to answer`，corrective 逻辑在 `coverage_incomplete`/`no_evidence` 时给 ABSTAIN，终结 gate 也能落 ABSTAIN。这些都有真实定义、被真实函数调用——和 `BranchResultFencer` 不同。

但"memory 与 Domain 冲突但没人触发 abstain"这半问今天还是不能答：abstain 的触发条件是 **unsupported claim / coverage 不足**，不是"memory 与 Domain 冲突"。所以"冲突静默漏过"这条路径**本身就不在 abstain 的判定范围内**——不是 abstain 没接线，是它管不到那件事。这个区分我 Wave 1 没讲清。

- `事实层`: Current
- `证据`: `agent/runtime/synthesis/grounded_answer.py:87-88`；`knowledge/agentic/corrective.py`
- `边界`: memory↔Domain 冲突的检测器：不存在。

## A191

我要诚实：**我没有把这两套都追到调用点，所以我不知道哪一套跑在真实检索里**。我能给的：产品侧那套（字典序 tuple 的 merge）在 `platform/services/retrieval/fusion.py`，是 orchestrator 走的；agentic 那套（真 RRF，`rrf_score += 1.0/(60.0 + rank)`，k=60 硬编）在 `knowledge/agentic_graphrag.py:876`。

我的**倾向**是两套都在各自路径上活着（产品检索 vs agentic RAG），不是一套死代码——但我没做"追到调用点"的核对，所以我把它标成 Unknown，不 claim。这也顺带回答"谁在维护口径一致"：**如果两套都活，那没人**——它们是两个子系统各自的选择。

- `事实层`: Current · Unknown
- `证据`: `platform/services/retrieval/fusion.py`；`knowledge/agentic_graphrag.py:876`
- `边界`: 哪套是死代码：没有核对到调用点。

## A192

我读到的证据里，淘汰逻辑是"替换最弱的 baseline 槽位"这个动作，而 **penalty 函数的具体形状我上次是照印象讲的**——我这次在 `fusion.py` 里 grep 不到任何 `penalty` 标识符。所以我要收：A87 里"有一个 penalty 逻辑在算该拿掉哪一条"这句，**我指不出它的函数**。

如果它存在，和那 9 个阈值同性质（无依据魔数）的可能性很高——但"可能性高"不是证据。所以这题我答：**形状我没读到，不能确认它存在**。

- `事实层`: Unknown
- `证据`: `grep -n "penalty" platform/services/retrieval/fusion.py` → 无命中
- `边界`: penalty 的形状与魔数：Unknown。**这是对 A87 的收缩。**

## A193

两种都可能，取决于切在哪：**正常句子边界上的引用**给的是完整句；**被字符窗口硬切的超长句**给的是残句。补全那一步**不在服务端做检索时的邻接扩展**（没有），而是靠**引用块自身带的 `parent_context`**——它是 `block.text[:1200]`，是切分时**预先写进 chunk metadata** 的，所以"补全"是**数据自带**，不是"服务端在展示时补"。所以是前端/展示层决定要不要用这 1200 字符。

而前端今天只是把 citation 渲染成 chip，**没有用 parent_context 去补全显示**。所以用户今天看到的是残句（如果只显示 chunk 文本）。

- `事实层`: Current
- `证据`: `knowledge/ingestion/router.py:541`（`parent_context`）、`:15-16`、`:583`
- `边界`: 别的客户端有没有用 parent_context：无证据。

## A194

是**我的推断**，不是从代码读出的因果。我指不出把"引用失效"和"coverage 不足"连起来的那一处代码——我能指出的是两条各自存在的链：`mark_source_deleted` 把 evidence 标成 `citation_eligibility='REJECTED'`；abstain 由 `unsupported claims`/`coverage_incomplete` 触发。但**"REJECTED 会导致 coverage 不足"这一步的传递**我没有读到具体实现。

所以我要把 A89 的措辞降级：A89 说"引用失效 → coverage 不足"是连接点，那是**我推的连接**，不是代码里的一处。这一条我认错。

- `事实层`: Unknown
- `证据`: 无（我指不出那处代码）
- `边界`: 因果链的实现依据：**没有**。**修正 A89。**

---

## T10 工程基础

## A195

我指出一条**本项目真实存在的 finally 清理路径**：`capability/tool_runtime/sandbox.py` —— WASM Python sandbox 跑子进程之后，`finally:` 里 `os.unlink(script_path)` 删临时脚本，包在一个 `try/except OSError` 里。这是真的、活的清理路径。

但它**不是我写的**，所以它回答不了"我亲自排查过取消/超时吗"。我要诚实：本项目里我没有一次"我亲自排查过的取消/超时 bug"可以讲——`simple_agent.py` 里我工作过的那段（`execute_binding_tool` 及 router helper）**一个 `finally` 都没有**（grep = 0）。所以 A95 那题我答的是通用语义，落不到本项目经验上。这个缝我认。

- `事实层`: Current · Personal Ownership（gap）
- `证据`: `capability/tool_runtime/sandbox.py`（唯一的 try/finally）；`grep -n "finally:" platform/services/workspace/simple_agent.py` → 0
- `边界`: 我亲自写的 finally：没有。

## A196

memory 侧是 **CAS，不是普通覆盖写**——但要说清 CAS 在哪一层。三步：读（`memory_versions` 带 `status`/`aggregate_version`）→ 判断（`activate_memory_version`）→ 写（带 `expected_version` 的激活）。如果 `expected_version != aggregate_version` 就冲突。所以是真的 CAS，不是覆盖写。

我要把 A99 里的一句收一下：A99 我引 `task_contracts.py:345` 当"domain 侧 stale 冲突"的证据，**那个行号指的是 `PlanVersion` 类定义**，不是 CAS 点；真正的 CAS 是 `PlanVersion.activate` 在 `task_contracts.py:476-489`（`expected_version != aggregate_version` 就拒）。行号我给偏了，点没错。

- `事实层`: Current
- `证据`: `platform/database/memory/domain.py:301`；`agent/domain/task_contracts.py:476-489`
- `边界`: memory 侧我没有做过多回合压力测试。

## A197

最短路径**今天走不通**。产生：dispatch 后异常/超时 → 落一个 UNKNOWN effect + 开一条 OPEN reconciliation。安全处置需要一个结论：`CONFIRMED_NOT_EXECUTED`（才允许重发）或 `CONFIRMED_EXECUTED`（收口）。而给结论的唯一入口是 `record_manual_effect_assessment`（远端查询没实现，A47）——所以最短路径是"**等一个人来做人工评估**"。

如果没有人，它就停在 OPEN，且 `escalate_due_reconciliations` 只在测试里被调（A110），所以连"过期升级"都不会发生。端到端：**产生得通，处置不通**——卡在缺失的对账执行器或缺失的人。

- `事实层`: Current · Target · Unknown
- `证据`: `invocation_gateway.py:536-587,1607-1618,1787`；`runtime_batch.py:460`
- `边界`: 有没有真实的 UNKNOWN effect 发生过：无记录。

## A198

**我没有一处**。我写过的那几段（`execute_binding_tool`、router 的 `_canonical_mcp_target`/`_detect_route_hint`/`_classify_mcp_route_tool`）里 grep 不到 `finally`；它们基本是直线 async 加早返回，没有需要 `finally` 的资源清理。

我在别的 commit 里能指到 `finally`（有一笔宽 commit 在 `minio.py` 和一个 test 里加了若干处），但那笔**范围极宽**（同时动了 launchers/scripts/docker/plans），我 A53 自己说过不能把整笔算我的。所以那些 finally 我**不能干净地 claim 成我写的**。这就是缝：**我答的 `CancelledError` 是通用语义，落不到"我写过带 finally 的并发清理"这个画像上**。

- `事实层`: Personal Ownership（gap）· Unknown
- `证据`: `grep -n "finally:" platform/services/workspace/simple_agent.py` → 0；宽 commit 的 finally 落在非我模块
- `边界`: 我亲自写的 finally：没有一处可干净 claim。

## A199

**真实的 WHERE 是四个等值列**：`user_id + agent_id + project_id + thread_id`（`MemoryScope` 的四维直接进 WHERE，见 `memory/store.py` 的 `_scope_select`）。所以我 A98 给的 `(user_id, project_id, created_at DESC)` **要改**——漏了 `agent_id` 和 `thread_id`（虽然 `agent_id` 恒定、`thread_id` 是会话态）。

正确的建议是 `(user_id, project_id, thread_id, agent_id, created_at DESC)`——等值列全在前、排序列在后。但如果如 A78 所说 `agent_id` 恒定、`thread_id` 可压缩，那可以把它们在索引里降权。所以 A98 那条建议**按今天的查询形状是不完整的**，我改。

- `事实层`: Current
- `证据`: `platform/services/memory/layers.py:41-57`；`memory/store.py:520-527`（`_scope_select` 四列等值）
- `边界`: 有没有 EXPLAIN 佐证：没有。

## A200

**今天不算数**，我当场改。原文："用回归测试固定路由边界（含自定义 MCP 名称递归与自然语言参数抽取）"。逐段核：`自定义 MCP 名称递归` 有测试（`_canonical_mcp_target` 自递归的修法）；`自然语言参数抽取` 有测试（城市抽成"南京"）；但 `路由边界` —— 只有 **direct route 的断言**，没有任何一条断言"多步 query 应回落到 ReAct"，`src` 里也没有 `direct_route`/`falls back to ReAct` 字面量。所以"固定路由边界"只固定了一半。

我改成："**用回归测试固定 direct route 的准入与工具参数抽取边界（含自定义 MCP 名称递归），ReAct 回落侧暂无回归断言。**" 这个版本每一段我都能指到 test 或明确标"无"。

- `事实层`: Personal Ownership（修正）· Current
- `证据`: `tests/agent/test_workspace_simple_agent.py`（direct route 断言）；`grep -rn "direct_route\|falls back to ReAct" src/` → 无
- `边界`: 我改的措辞就是上面这句。

---

## 附录：本次实际打开的文件

以下是我本轮（Wave 2）实际用 Read / Grep / Bash 打开或检索过的路径，按用途分组。

**冻结输入与评审**
- `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\01_simulated_resume.md`
- `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\03_blue_answers.md`
- `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\04_red_wave2_review_and_questions.md`
- `D:\projects\zuno\.agent\red-blue\defense-model.md`

**canonical truth / 治理文档**
- `D:\projects\zuno\docs\README.md`
- `D:\projects\zuno\docs\project\README.md`
- `D:\projects\zuno\docs\project\reference.md`
- `D:\projects\zuno\docs\governance\project-fact-provenance.md`
- `D:\projects\zuno\docs\governance\rb019-graphrag-ablation-protocol.md`
- `D:\projects\zuno\docs\governance\interview-acceptance-standard.md`
- `D:\projects\zuno\docs\governance\effect-security-slice-c-review.md`
- `D:\projects\zuno\docs\architecture\architecture.md`
- `D:\projects\zuno\docs\architecture\architecture-views.md`
- `D:\projects\zuno\docs\modules\README.md`
- `D:\projects\zuno\docs\decisions\0005-official-langgraph-postgres-checkpointer.md`
- `D:\projects\zuno\docs\decisions\0007-reuse-first-provider-boundary.md`
- `D:\projects\zuno\docs\decisions\0012-evidence-gated-physical-service-split.md`
- `D:\projects\zuno\docs\evidence\README.md`
- `D:\projects\zuno\docs\evidence\implementation-wave-001.md`
- `D:\projects\zuno\docs\evidence\current-test-baseline.md`
- `D:\projects\zuno\docs\evidence\current-eval-baseline.md`
- `D:\projects\zuno\docs\evidence\current-runtime-baseline.md`

**eval / 工具**
- `D:\projects\zuno\tools\evals\zuno\multihop_eval\README.md`
- `D:\projects\zuno\tools\evals\zuno\multihop_eval\metrics.py`

**真实源码 —— retrieval / knowledge**
- `D:\projects\zuno\src\backend\zuno\platform\services\retrieval\fusion.py`
- `D:\projects\zuno\src\backend\zuno\platform\services\retrieval\planner.py`
- `D:\projects\zuno\src\backend\zuno\platform\services\retrieval\orchestrator.py`
- `D:\projects\zuno\src\backend\zuno\knowledge\agentic_graphrag.py`
- `D:\projects\zuno\src\backend\zuno\knowledge\provenance.py`
- `D:\projects\zuno\src\backend\zuno\knowledge\ingestion\router.py`
- `D:\projects\zuno\src\backend\zuno\knowledge\ingestion\async_runtime.py`
- `D:\projects\zuno\src\backend\zuno\platform\database\knowledge\domain.py`
- `D:\projects\zuno\src\backend\zuno\platform\services\rag\handler.py`
- `D:\projects\zuno\src\backend\zuno\platform\services\pipeline\models.py`

**真实源码 —— tool / MCP / workspace**
- `D:\projects\zuno\src\backend\zuno\platform\services\workspace\simple_agent.py`
- `D:\projects\zuno\src\backend\zuno\capability\tool_runtime\invocation_gateway.py`
- `D:\projects\zuno\src\backend\zuno\capability\tool_runtime\runtime_batch.py`
- `D:\projects\zuno\src\backend\zuno\capability\tool_runtime\sandbox.py`
- `D:\projects\zuno\src\backend\zuno\capability\mcp\mcp_tool_executor_adapter.py`
- `D:\projects\zuno\src\backend\zuno\platform\services\mcp\sessions.py`
- `D:\projects\zuno\src\backend\zuno\platform\database\foundation.py`
- `D:\projects\zuno\src\backend\zuno\platform\security\persistence.py`
- `D:\projects\zuno\src\backend\zuno\product\runtime_batch.py`
- `D:\projects\zuno\src\backend\zuno\api\services\workspace.py`
- `D:\projects\zuno\src\backend\zuno\api\services\knowledge.py`
- `D:\projects\zuno\src\backend\zuno\api\dto\completion.py`
- `D:\projects\zuno\src\backend\zuno\api\dto\workspace.py`
- `D:\projects\zuno\src\backend\zuno\api\v1\product.py`
- `D:\projects\zuno\src\backend\zuno\api\v1\mcp_agent.py`
- `D:\projects\zuno\src\backend\zuno\platform\database\dao\mcp_agent.py`
- `D:\projects\zuno\src\backend\zuno\platform\database\models\mcp_agent.py`

**真实源码 —— runtime / memory / agent**
- `D:\projects\zuno\src\backend\zuno\agent\runtime\service.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\graph.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\checkpointer.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\phase08.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\__init__.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\sqlite_store.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\planning\recovery.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\planning\branch_result.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\planning\dynamic_worker.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\nodes\core.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\execution\tool_step.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\synthesis\grounded_answer.py`
- `D:\projects\zuno\src\backend\zuno\agent\runtime\synthesis\citation_binding.py`
- `D:\projects\zuno\src\backend\zuno\agent\domain\task_contracts.py`
- `D:\projects\zuno\src\backend\zuno\agent\contracts.py`
- `D:\projects\zuno\src\backend\zuno\platform\database\agent\domain.py`
- `D:\projects\zuno\src\backend\zuno\platform\services\memory\layers.py`
- `D:\projects\zuno\src\backend\zuno\platform\database\memory\domain.py`
- `D:\projects\zuno\src\backend\zuno\memory\engine.py`
- `D:\projects\zuno\src\backend\zuno\memory\store.py`

**测试**
- `D:\projects\zuno\tests\graphrag\test_graphrag_baseline_preserving_fusion.py`
- `D:\projects\zuno\tests\repo\test_agent_system.py`
- `D:\projects\zuno\tests\security\test_mandatory_audit_postgres_boundary.py`
- `D:\projects\zuno\tests\agent\test_workspace_simple_agent.py`
- `D:\projects\zuno\tests\capability\test_tool_effect_postgres_boundary.py`

**前端**
- `D:\projects\zuno\apps\web\src\pages\workspace\defaultPage\defaultPage.vue`

**未打开（明示）**：`03_blue_architecture_notes.md`、任何 `*architecture_notes*` 文件、`docs/red-blue/` 下的任何历史 round 目录，均未读取。
