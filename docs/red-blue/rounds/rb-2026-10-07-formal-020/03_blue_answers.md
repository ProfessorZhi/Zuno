# Blue Wave 1 — Candidate Answers A1–A100

```text
round: rb-2026-10-07-formal-020
role: Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师
answers_to: 02_red_questions.md @ 4d9bf767
register: 第一层 20–60 秒口语，其后可展开
```

## A1

我接手的不是一张白纸。在我那笔改动之前，MCP Tool 不是直接挂到主 Agent 上的——它要先经过一层专门的 Tool 选择/转发脚手架：`tool_invocation_model`、`available_tools`、`LLMToolSelectorMiddleware`，再加一层把 MCPAgent、SkillAgent 当成 Tool 嵌进去的嵌套结构。所以调用链大概是：主 Agent → 一个 tool-selector 中间件 → MCPAgent/SkillAgent → 真正 `ainvoke`。我改的是这个"转发层被删掉"这一段：把具体 MCP Tools 直接拼进主 Agent 的 tool list，另外把用户级 MCP 配置改成在真正调用那一刻按 Tool→Server 映射注入。

第二层：

- 删除嵌套脚手架、把 tools 直接绑到单一 agent 的那笔是 `773467580ee428a0536c7f594c0847c1510879ac`（2026-04-15）。
- 现在的落点：`WorkSpaceSimpleAgent.init_simple_agent` 里 `self.tools = plugin_tools + mcp_tools + knowledge_tools + skill_tools`；`setup_mcp_tools()` 里 `self.mcp_tools = await self.mcp_manager.get_mcp_tools()`，没有 MCPAgent 这一层了。
- 我必须说清楚：这是"删一层、直连并注入配置"，不是"我从零写了 Tool Calling 框架"。

- `事实层`: Historical · Personal Ownership · Current
- `证据`: `src/backend/zuno/platform/services/workspace/simple_agent.py:1160`、`:1430-1449`；`docs/governance/project-fact-provenance.md` PF-032
- `边界`: 那套被删的转发脚手架是谁写的、当时为什么这么设计，我没能从历史里切出来；`77346758` 是一笔范围很宽的 commit，我不能把整笔都算成 Tool Calling 的贡献。

## A2

不是启动时静态注册一次，是每个会话、每个 Agent 实例起来的时候动态装的。这张"主 Agent 能用哪些 Tool"的表不在一个全局常量里，它是这个 agent 实例自己的一个 list 属性——`plugin_tools + mcp_tools + knowledge_tools + skill_tools` 拼出来的。

第二层：

- 装载时机在 `WorkSpaceSimpleAgent` 初始化里，`setup_mcp_tools()` 去 MCP manager 拉一遍 tool 列表。
- 持有者是 agent 实例本身，等于"一个产品会话一个实例"。
- 另外还有一张不同的表：server→tools 的映射 `self.server_dict`，那是给配置注入用的，不是给"能不能用"用的。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/workspace/simple_agent.py:1160`、`:1430-1449`、`:327`
- `边界`: 我没有统计过一进程里最多并发起多少这类实例，也没有压测数据。

## A3

最直接的动因是配置隔离：MCP server 需要用户级配置（每个人自己的 key、自己的 server id），如果让配置沿着调用链一层层往下传，就要每一层都开一个参数槽位、每一层都记得透传。用子 Agent 中转，本质上是把"这个世界只认一套配置"变成"每个子 Agent 带自己的配置"。

第二层——如果反过来，把配置一层层往下传会在哪坏掉：

- 不是"传不过去"，是"漏传就静默降级"。中间任何一层用默认值兜底，调用会带着错误的配置继续跑下去，而不是报错。
- 现在改成显式注入：`execute_binding_tool` 里判 `is_mcp_tool(binding.name) and mcp_requires_user_config(binding.name)` 才去 `mcp_user_config_resolver(user_id, mcp_tool_id_resolver(binding.name))`，把 config 合进 `call_args`。

- `事实层`: Historical · Personal Ownership · Target
- `证据`: `src/backend/zuno/platform/services/workspace/simple_agent.py:189-201`、`:1389`；`src/backend/zuno/api/services/mcp_user_config.py:128-136`
- `边界`: "漏传会静默降级"是我今天从代码结构推出的解释，我没有当时那版代码的失败记录来证明这就是当年真实的坏法。

## A4

承 A2 那张表。映射有两张，key/value 类型不一样：

- `server_dict`: `dict[str, list[str]]`，key 是 server name，value 是这个 server 下的 tool 名字列表。
- `get_mcp_id_by_tool`: `str -> str`，tool 名字 → `mcp_server_id`，再去 `self.mcp_configs` 里按 `server_name` 匹配到配置。

它不是代码里的常量，也不是配置文件，是运行时注册表——上面的实现就是初始化时用 `mcp_servers_info` 现算出来的一个 dict。至于谁有权改它：只有 agent 初始化那一段能写它，业务代码改不了。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/workspace/simple_agent.py:1438-1441`、`:2920-2926`、`:103-116`（`MCPConfig` 里带 `server_name` / `mcp_server_id` / `config_enabled`）
- `边界`: 我没找到任何一处运行时修改 `server_dict` 的代码路径，所以我说它"不可变"是"没有找到写入口"，不是"设计上禁止写"。

## A5

不会串，但让配置跟着请求走的不是 ContextVar——是显式参数加"一个会话一个实例"。`execute_binding_tool` 把 `user_id`、`tenant_id`、`workspace_id`、`run_id`、`step_run_id`、`trace_id` 全部当实参往下传，配置在每个请求里现查现注。

第二层，这里有个我必须澄清的点：

- 项目里**确实**有一个 `user_id` 的 ContextVar，但它只服务可观测性（LangSmith metadata、用量统计），**不用**来传 MCP 配置。
- 也就是说：如果有人问我"你们是不是靠 ContextVar 隔离用户配置"，诚实的回答是"不是"。
- 下游还有一道：`AgentRuntimeService._assert_scope` 在 tenant/workspace 不匹配时直接 `PermissionError`。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/workspace/simple_agent.py:160-176`、`:301-324`、`:348`；`src/backend/zuno/platform/common/contexts.py:7`、`:21-28`；`src/backend/zuno/agent/runtime/service.py:395-416`
- `边界`: 我没有写过并发注入的对抗性测试，所以"不会串"是基于调用形态的判断，不是被测试固定住的事实。

## A6

超时不在 Agent 循环那一层。真正生效的是 MCP client 的连接层，分三个数：HTTP 连接默认 5 秒、SSE read 默认 300 秒、streamable HTTP 默认 30 秒 / read 300 秒。另外 tool discovery 那一步有一个显式的 `asyncio.wait_for`；但 tool **执行**那一步没有 `wait_for`，只有连接的 timeout 在兜。

第二层，超时那一刻主 Agent 拿到什么：

- MCP content 层对 `isError` 抛 `ToolException`，往上变成 `ToolRuntimeExecutionResult(status="failed")`。
- Agent 侧把它映射成一个 **BLOCKED observation**，`failure_reason` 填的是 result.status，然后按这个 observation 继续往下走。
- 换句话说：它不是一个异常炸穿循环，是一次"步骤被标记为阻塞"。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/mcp/sessions.py:27-31`；`src/backend/zuno/platform/services/mcp/manager.py:17-32`；`src/backend/zuno/platform/services/mcp/load_mcp/tools.py:71-83`、`:37-38`；`src/backend/zuno/agent/runtime/execution/tool_step.py:95-106`
- `边界`: `RuntimeLimits.timeout_ms` 这个字段存在，但我没有找到真正围着一次 tool 调用生效的定时器；所以"Agent 循环层超时"我答不出来——它今天是声明式的 budget，不是 timer。

## A7

不会无条件重试。带副作用的调用，重试的前提是"上一把确定没发生"——判据不是时间，是 effect certainty：只有当对账结论是 `CONFIRMED_NOT_EXECUTED` 时，才允许对同一个 effect 重发。

第二层：

- 执行前先抢幂等位：`claim_idempotency_receipt(scope="tool-side-effect", key=call_id, ...)`，key 里面带 `prepared_action_hash` 和 `target_resource_set_ref`。
- 抢到了才允许 dispatch；已经 completed 的就走 replay，返回既有 receipt，不再打网络。
- 结果未知时不重试，转成 `reconcile_required`。
- 另外代码里 `hidden_retry_count` 记的是 0：没有对上层隐藏的自动重试。

- `事实层`: Current
- `证据`: `src/backend/zuno/capability/tool_runtime/invocation_gateway.py:1290-1317`、`:1339-1366`；`src/backend/zuno/capability/tool_runtime/runtime_batch.py:460`；`src/backend/zuno/capability/runtime.py:1001`
- `边界`: 幂等位有 TTL（60 秒）。TTL 到期之后、远端 effect 仍未确认的那段窗口怎么收敛，我只能说它靠对账走，我本人没有测过这个边界。

## A8

路由判定是规则做的，不是一个模型调用，而且它在产品侧、不在 canonical runtime 里。三个函数配合：`_detect_route_hint` 做关键词匹配，`_classify_mcp_route_tool` 做正则抽参，`_resolve_governed_tool` 决定"能不能给一个确定的直接 tool step"，给不出来就 `None`、回落。

第二层，这里是这条 bullet 上我必须主动纠正的地方：

- 在 canonical runtime 里，**没有**一个独立的 "direct" strategy mode。`plan_kind == "tool"` 被显式映射成 `StrategyMode.REACT`——那个被确认为"目标明确"的 tool step，最终还是跑在 ReAct 的 step 图里。
- 所以"direct route vs ReAct 回落"更准确的表述是：**产品侧先决定要不要把参数钉死**，钉死了就是一个单步的 governed tool step；钉不死才交给 ReAct 自己选工具。它不是一个二级运行时。
- "自定义 MCP 名称递归"那类 case 判错的点是 `_canonical_mcp_target` 自己递归回自己：规范化之后 query 和 server name 相等，就死循环。修法是把自定义名字在进入递归前就返回规范化结果，不再回递归。

- `事实层`: Current · Personal Ownership
- `证据`: `src/backend/zuno/platform/services/workspace/simple_agent.py:2159-2188`、`:2743-2800`、`:2848-2890`、`:2702-2724`；`src/backend/zuno/platform/services/workspace/single_controller_runtime.py:1147-1152`；`tests/agent/test_workspace_simple_agent.py:16`、`:54`、`:129`
- `边界`: `src` 里**不存在** `direct_route` / `falls back to ReAct` 这样的字面量；我也没有找到一条断言"多步 query 应该回落到 ReAct"的回归测试。所以这句简历措辞在今天代码里的对应物比它读起来要弱。

## A9

"到底发生没发生"这件事，裁决权不在 Agent，也不在我这一层——它在 Tool Runtime 的 effect/reconciliation 域里。系统不自己给自己发一张"我认定它成功了"的证明；它把状态标成 `UNKNOWN_EFFECT`，交给对账去收敛。

第二层：

- Gateway 在这三种情况下都会返回 `reconcile_required`：抛 `ToolEffectUnknownError`、dispatch 之后抛了别的异常、dispatch 之后的持久化失败。返回码是 `UNKNOWN_EFFECT_RECONCILIATION_REQUIRED`。
- 关键设计点：**`UNKNOWN` 不许降级成 `FAILED`**。理由很直白——降级成 Failed 会导致有人再发一次，而那次可能真的重复执行了。
- 接下来系统做的动作：开一条 OPEN reconciliation，带上对账查询描述；超过 `age_escalation_after_seconds=900` 之后被 sweep 成 `ESCALATED` / `MANUAL_ASSESSMENT`，转人工判定。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/capability/tool_runtime/invocation_gateway.py:536-587`、`:564`、`:1958`；`src/backend/zuno/platform/database/tool_runtime/domain.py:1188-1199`
- `边界`: 超时 900 秒这个数是代码里的常量，但我没有证据说它是被调过参的；我倾向于它是拍的。

## A10

自研这一层真正补的 delta，不是"注册、注入、超时"这三件事——这三件成熟 MCP Host 都能做。补的是**副作用语义**：把一次 MCP 调用变成一条有 business key 的 prepared action，绑上 authorization decision、security epoch、mandatory audit proof，然后产出 effect receipt，未知时产出 reconciliation。这些不是 MCP 协议层的东西，是"我们改外部现实"这件事需要的记账。

第二层：

- 唯一真正瘦的那层是 `MCPLangChainToolAdapter.execute`——它确实就是个 `binding.ainvoke` 的包壳，delta 只是 tenant/run/step 上下文和 idempotency key。
- 删掉条件写清楚：如果哪天 MCP host 原生提供"按调用上下文注入 per-user 配置 + 幂等 key + 副作用回执 + 未知结果对账"，并且我们能接受把 effect authority 交给它，那这层就该删。
- 我自己判断这条件今天远没到，尤其最后一条——effect authority 交出去，等于把授权和审计的边界交出去。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/capability/mcp/mcp_tool_executor_adapter.py:70-74`、`:77-156`；`docs/decisions/0007-reuse-first-build-requires-evidence.md`
- `边界`: 这是"如果重做我会怎么删"的推理题，我给的是判断，不是已执行的删除，也没有删除的收益测量。

## A11

具体点：HotpotQA development smoke 上，graph candidates 把 baseline 本来已经命中的两篇挤出了 Top-K——`Ed Wood` 和 `Shirley Temple`。回归测试里固化下来的那条更小：`Sinister (film)` 不能出现在 top5 里。

第二层，发现归属我必须切开讲：

- 那次 audit 的记录是有的：baseline `Recall@5=1.00 / MRR@10=0.90`，本地跑出来 `Recall@5=0.80 / MRR@10=0.80`。
- 我的 commit 是修复侧：`5d9b719e`(2026-06-20) baseline-preserving fusion。
- "是谁第一个发现的"我没法从历史里切出来——我不愿意把它 claim 成我个人的。

- `事实层`: Historical · Current · Evidence
- `证据`: `docs/governance/project-fact-provenance.md` PF-031；`tests/graphrag/test_graphrag_baseline_preserving_fusion.py`
- `边界`: 这几条 query 的原始报告是 gitignore 掉的，我手上没有可复现的原始产物。

## A12

口径是 retrieval-only 的 IR 指标，不是端到端答案正确率：`Recall@2/5/10`、`Precision@5/10`、`MRR@10`、`ChainRecall@5/10`、`FullChainHit@5/10`。出问题那阵子，主看的是 `Recall@5` 和 `MRR@10`。

第二层：

- 这个口径是 multihop eval harness 定的，不是业务侧定的。后来冻结的 ablation 协议里，primary metric 收成两个：`FullChainHit@5` 和 `Recall@5`。
- 我要明确界：这些指标衡量的是"该捞的 doc 有没有进 top-K"，不衡量"回答对不对"。

- `事实层`: Current · Evidence
- `证据`: `tools/evals/zuno/multihop_eval/metrics.py:34`、`:69`、`:118`；`docs/governance/rb019-graphrag-ablation-protocol.md`
- `边界`: 我参与制定过口径的哪一部分，我记不清了；只能说这个 harness 是项目既有的评测面。

## A13

会答错的不是"文档里没这句话"那种，是**答案需要把两篇文档连起来**的那种：comparison（比较两个实体）、bridge（A 提到 X、X 决定 B）、genealogy 这几类。用户场景比如说——问"这两份材料里对同一个事实的说法是否一致"，vector 能把两段各自捞上来，但它不知道这两段之间有边；BM25 更不知道。

第二层：

- 图侧的信号就是在补这个：`graph_support_count`、`graph_seed_hit_count`、`graph_file_focus`、`graph_path_count`。
- 但这里有个我必须认的边界：我说"vector + BM25 会答错"是从机制上推的，我没有一份"只开 vector+BM25 的对照测量"来把它变成证据。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/platform/services/retrieval/fusion.py:157`
- `边界`: 图检索的**必要性**没有被测量过。这是 ablation 协议存在的理由，不是它的结论。

## A14

承 A12 的口径。"保留原始 rank"不是把分数加权相加——原 rank 被存成每个候选 metadata 上的独立字段：`vector_rank`、`bm25_rank`、`graph_rank`、`requery_rank`。融合时先按 `chunk_id` 去重，同一个 chunk 被几路命中就把几路的 rank 都挂在它身上。

最终顺序是一个**字典序 tuple**，不是分数和：

```text
(candidate_group, baseline_rank, -chain_score, -graph_tier, -graph_signal, -(local_score + base_score))
```

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/retrieval/fusion.py:979`、`:992-1021`、`:952-977`
- `边界`: 这里有个容易讲错的地方我要点出来：代码里**确实算了一个 `fusion_score` 写进 metadata**，但它**不是排序键**。谁只看那个字段就会得出"两路分数相加"的错误结论。

## A15

是一个可比的整数标量，算法就是四项相加：`graph_support_count + graph_seed_hit_count + graph_file_focus + graph_path_count`。分层是四层 candidate group，加上一个 0–4 的 graph tier。

第二层，晋升方式是最关键的一点：

- 不是"直接提到最前"。graph-only 的候选要进到比较靠前的组，signal 得够（阈值 6/9 那档）；进了组之后，它仍然带一个 `baseline_rank` 的位置。
- 有 chain 支持的，`baseline_rank = max(graph_rank - 1, 1)`；signal 够大的，`= graph_rank + 1`。也就是说它是**可被反超的位次**，不是插到队首。
- 这是有意为之：这条路的目的是"别把 baseline 挤出去"，那它自己就不能是个挤人的角色。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/retrieval/fusion.py:157`、`:166`、`:190`、`:205`
- `边界`: 我讲不出这四条信号为什么是等权相加的；没有权重依据可追。

## A16

一共 9 个常量，集中在一个类头部：`GRAPH_PROMOTION_THRESHOLD=6`、`COMPARISON_SELECTION_SIZE=3`、`COMPARISON_MIN_SEEDS=2`、`BRIDGE_SELECTION_SIZE=3`、`BRIDGE_PROTECTED_TOP=2`、`BRIDGE_MIN_SEEDS=2`、`GENEALOGY_PROTECTED_TOP=5`、`GENEALOGY_PROMOTION_SIGNAL_THRESHOLD=2`、`GENEALOGY_FULL_CHAIN_THRESHOLD=3`；分层里还硬编了 6 和 9 两个档。

第二层，怎么定下来的，我直接给实话：

- 没有扫参记录，没有从数据里统计出来的分布，代码里也没有一行注释写理由。
- 定法就是经验值 + 让 bad case 不再复现。谁定的：我在修那三个 heuristic 的时候定的。
- 这就是为什么后来要写 ablation 协议：**这些数现在没有 holdout 支撑**。

- `事实层`: Current · Personal Ownership
- `证据`: `src/backend/zuno/platform/services/retrieval/fusion.py:9-17`、`:179`、`:183`、`:200`
- `边界`: 我不能给你"为什么是 6 不是 5"的依据——没有。协议里 `measurement_status: BLOCKED_PENDING_DATA`。

## A17

承 A11。那 5 条 query 怎么挑的，我答不出来——挑法没有被记录，我不愿意事后编一个"代表性"的说法。

它**能**证明的：在这 5 条上，修复之后回到了 baseline 水平，`Sinister (film)` 那条回归不再复现。
它**不能**证明的：任何分布上的普遍改善、任何"GraphRAG 更好"的结论。

第二层：

- 5-query smoke 是一条回归安全带，不是 benchmark。协议里明确写了 limit=10/20/50 都**不是** holdout。
- 顺带说清一个容易被我讲飘的地方：eval README 里有更晚的 limit=50 rerun（`enhanced Recall@5 = 0.98`）。那个数我不把它当"优于 baseline"的证据——它既不是 holdout，也不是我用来做决定的依据。

- `事实层`: Current · Evidence · Unknown
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md`；`tools/evals/zuno/multihop_eval/README.md`
- `边界`: 5 条 query 的选取口径：Unknown。原始报告 gitignore。

## A18

没有 holdout。ablation 也没有跑成正式结果——协议已经冻结、heuristic 一条条编了号（H1–H9，每条都带代码位置），但 `measurement_status: BLOCKED_PENDING_DATA`。阻塞原因是硬的：没有 HotpotQA 的稳定访问、没有对应凭据和索引环境。

第二层：

- 协议明确写了 limit=10/20/50 这些不等于 holdout，所以"换一类 query 分布收益还在吗"这题我今天的答案是：**不知道，且现在是 measurement blocked**。
- 能替代的只有单组件级的回归测试：seed expansion、entity alias、path ranking、comparison/bridge/genealogy guardrail、chain-aware fusion 各自有自己的 test 文件。这些固定的是"没退化"，不是"有收益"。

- `事实层`: Current · Evidence · Unknown
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md`；`tests/graphrag/` 下对应 6 个测试文件
- `边界`: holdout 收益：Unknown，且是 blocked 的 Unknown，不是"没来得及看"。

## A19

这个账我没法算给我你——没有压测、没有线上日志、没有估算模型，`MEASUREMENT_BLOCKED`。我不给数字。

第二层，能说的只有结构性事实（注意，这不是延迟数据）：

- 检索侧是**顺序 await** 的：vector → requery → bm25 → graph 依次走，`retrieval/` 里没有 `asyncio.gather`，也没有超时取消。
- 图那一侧还有自己的 hop 上限和 path 上限（`graph_hop_limit=2`、`max_paths_per_entity=10`），所以它的成本随图规模走。
- 由此能得到的唯一结论是定性方向：**图这一路是串行增量成本**，不是并行摊掉。具体多少，我不知道。

- `事实层`: Current · Unknown
- `证据`: `src/backend/zuno/platform/services/retrieval/orchestrator.py:614-689`；`src/backend/zuno/platform/services/graphrag/retriever.py:797-798`；`docs/evidence/current-eval-baseline.md`
- `边界`: 延迟、成本、QPS：**一个数都没有**。没有生产环境，就没有 per-request 成本可测。

## A20

两个触发信号是现成的，而且都在代码里：图不可用或项目没准备好时，图路由**根本不会被开**——只有在 `internal_route == "local_graphrag"` 且 `graph_available` 时才开；健康度下降时 planner 会给出 `graph_not_ready` / `community_not_ready` 这类原因码，走降级。

第二层：

- 但"什么时候该整体关掉"这件事，我不应该用"自动降级"来回答，因为那是可用性开关，不是价值判断。
- 真正的退出条件是测量性的：如果 holdout 上关掉 seed expansion / alias / path ranking 之后指标不掉，那这些组件就该删。协议已经把这个 test 设计写好了，只是现在 blocked。
- 也就是说：**今天的答案是"暂时保持 optional"，理由是测量缺席，不是因为我判断它有效。**

- `事实层`: Current · Target · Evidence
- `证据`: `src/backend/zuno/platform/services/retrieval/planner.py:199-200`、`:91-98`、`:172-176`；`docs/governance/rb019-graphrag-ablation-protocol.md`
- `边界`: GraphRAG 的净收益：Unknown / blocked。我不会说"删掉会掉指标"，因为我没有那个对照。

## A21

V2 之前跨回合靠的是会话内的历史 + 一个上下文拼装过程；没有一个"按作用域统一读取"的入口，读取和过滤散在调用点。需求来源我不能 claim 成我提的——能追到的只是"early important Memory work / OpenViking Memory-Context 集成"这个方向层面的参与记录。

第二层：

- 我能自证的个人落点：`GeneralAgent.prepare_context` 是 `d4e2fe2e`(2026-06-26) 建起来的，`f3c74338`(PR #8, 2026-06-30) 做了 readback 收紧。
- 这两笔之后，`general_agent.py` 在 `ab1222da`(2026-08-04, Phase 22 单一产品运行时重构) 被整个删掉了。

- `事实层`: Historical · Personal Ownership · Unknown
- `证据`: `docs/project/reference.md`（"early important Memory work"、"OpenViking Memory / Context integration"）；commit `d4e2fe2e`、`f3c74338`、`ab1222da`
- `边界`: "统一入口"这个需求是谁提的：Unknown。另外 OpenViking 那份产物在 git 里没有恢复回来，我不能拿它当天可查的证据。

## A22

粒度是四元组合，不是一个单一维度：`MemoryScope(user_id, agent_id, project_id, thread_id)`。四个一起构成 scope，谁都不是"作用域"本身。

第二层，谁定义的、写在哪：

- 定义在代码里：`MemoryScope` 是个 dataclass，不是文档里的概念。
- 运行时实际填的值是 `_memory_scope()` 给的：`user_id` 取 state、`agent_id` 固定成 `"agent_run"`、`project_id` 取 `workspace_id`、`thread_id` 取 state。
- 所以"project"这个业务概念在存储层是用 `workspace_id` 表达的。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/memory/layers.py:42`；`src/backend/zuno/agent/runtime/nodes/core.py:485`
- `边界`: `agent_id` 被写死成 `"agent_run"` 之后，这一维实际不区分任何东西——它今天更像占位。我没有找到把它用起来的消费方。

## A23

写三种，不是一种：原始记忆事件、任务摘要、结构化记忆候选/版本。触发者是**回合结束**这个运行时节点，不是用户操作、也不是某个人手动触发。

第二层：

- 入口是 `post_turn_commit()`，往下落到 `commit_turn_outcome`，一次写进 `memory_candidates_v2`、`memory_versions`、`memory_snapshots`、`context_pack_versions`、`memory_use_traces` 五张表。
- 注意"写入 ≠ 生效"：写进去的是 candidate；结构化记忆要过了 review 状态（pending/approved/rejected）才可能被回读。`TaskMemorySummary` 还强制带 `source_event_ids`。

- `事实层`: Current
- `证据`: `src/backend/zuno/agent/runtime/nodes/core.py:391`；`src/backend/zuno/memory/governed_runtime.py:30`；`src/backend/zuno/platform/services/memory/layers.py`；`src/backend/zuno/platform/database/memory/domain.py:15`、`:30`、`:54`
- `边界`: 我没有测量过 post-turn 写入对回合延迟的贡献。

## A24

承 A23。今天的读入口是运行时图里那个 `prepare_context` 节点，节点体是 `build_context()`；它调 `MemoryEngine.build_context_pack()`，再由 `render_context_pack()` 渲染。

过滤**两层都有**，而且分工是明确的：

- **scope 过滤在 SQL WHERE 里**：`user_id / agent_id / project_id / thread_id` 直接进 WHERE 子句。
- **review / 状态过滤在应用层**：`_memory_exclusion_reason` 把非 APPROVED 的、以及 `stale / conflict / revoked` 状态的候选剔掉。

第二层，这里必须纠正一句话，因为它牵到我简历的措辞：

- `prepare_context()` **今天不是函数**。全 `src/` grep 不到 `def prepare_context`。它今天只是运行时图里的一个**节点名**，节点体叫 `build_context()`。
- 历史上那个同名方法是我在 `GeneralAgent` 上写的（2026-06-26 → 2026-06-30），`ab1222da`(2026-08-04) 把整个文件删了。
- 所以简历那句"注入 `prepare_context()`"按今天的代码读会失准；准确说法是"注入到回合前的上下文构建节点"。

- `事实层`: Historical · Current · Personal Ownership
- `证据`: `src/backend/zuno/agent/harness.py:9`、`:269`；`src/backend/zuno/agent/runtime/nodes/core.py:62`；`src/backend/zuno/memory/engine.py:645`、`:753`、`:1054`；`src/backend/zuno/memory/store.py:520`
- `边界`: 我不能说今天的节点实现就是我当年那版搬过去的——中间文件被删过，我没有做过逐行比对。

## A25

承 A22。**scope 不足以当授权边界**，这一点在项目自己的措辞里就写着：`Provenance != Truth != Authorization`，以及 memory 是"optional non-authoritative provider boundary"。scope 是一个**过滤维度**，不是一次权限裁决。

第二层，你的具体场景：

- 两个案件共用同一个 `user_id` 时，靠 `project_id`（运行时是 `workspace_id`）和 `thread_id` 分开——只要调用方把这两个值传对了，SQL WHERE 就会挡住串读。
- 但这个保护的前提是"调用方传对"。scope 本身不做权限判定，也没有一个"这个人有没有权读这个 matter"的裁决点。
- 真正的授权归属在 Security/Governance：`Memory Recall Eligibility` 是它拥有的概念，`privacy_delete_scope` 也是在这一侧。

- `事实层`: Current · Target
- `证据`: `docs/project/reference.md`；`src/backend/zuno/memory/store.py:520`；`src/backend/zuno/memory/engine.py:540`
- `边界`: 我没法证明"跨案件串读不可能"——我能证明的是"scope 过滤存在"，不能证明"scope 就是授权"。这两件事我没有混起来讲。

## A26

已经进过上下文的那条 memory，**不会被追溯改写**——已经发生的对话里它就在那儿。系统能做的是两件事：一是让**后续**回合不再召回它，二是留下"哪次上下文用了哪个 memory 版本"的痕迹，让下游结论可以被重新判定。

第二层：

- 版本侧：memory 版本状态有 DRAFT / ACTIVE / REVOKED / SUPERSEDED，激活走 CAS；被撤销之后不再 eligible。
- 痕迹侧：`memory_use_traces` 就是记"这一份 context pack 用了哪些 memory"的。
- 知识侧有个可类比的成熟做法：源被删时不是删记录，而是把 evidence 标成 `citation_eligibility='REJECTED'`、把 lineage 标 `deleted_or_tainted=true`。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/platform/database/memory/domain.py:301`；`src/backend/zuno/memory/governed_runtime.py:30`；`src/backend/zuno/platform/database/knowledge/domain.py:669`、`:685`
- `边界`: **下游结论要不要回滚**——今天没有一个自动的失效传播机制，我能点出来的只有"痕迹存在"。我不会说"会级联回滚"。

## A27

判"谁更新"主要靠状态位和版本，不是靠比时间戳。回读时 `_memory_exclusion_reason` 会把 `stale`、`conflict`、`revoked` 三种状态直接剔掉；写入侧靠版本 CAS 和 aggregate version 防止旧写覆盖新写。

第二层，我要老实说清我能指和不能指的：

- 能指：状态排除（应用层）、版本状态机、CAS 激活。
- 不能指：一个"按时间戳比较新旧"的比较器。我没有找到这样一段逻辑，所以我不宣称它是靠时间戳判的。
- 我的定位是：这是状态机 + 版本在兜，不是 timestamp 在兜。

- `事实层`: Current
- `证据`: `src/backend/zuno/memory/engine.py:1054`；`src/backend/zuno/platform/database/memory/domain.py:301`；`src/backend/zuno/agent/domain/task_contracts.py:345`
- `边界`: "stale 是谁标的、按什么规则标的"——这条标定逻辑我没有追到底，答不出来。

## A28

信 Domain。这不是我的偏好，是项目写明的边界：Memory 是可选、非权威的 provider；provider 记录不替代 Domain truth。Agent 下一步必须以 Domain 当前状态为准，memory 只能作为提示。

第二层：

- 谁拥有裁决权：正式业务事实在 Domain 侧（Domain 提交才是事实来源）；Runtime 不能代表业务成功。
- 上层还有一道收敛：如果最终答案里有 unsupported 的 claim，合成/终结阶段会走 ABSTAIN，而不是拿 memory 硬凑。

- `事实层`: Current · Target
- `证据`: `docs/project/reference.md`（Memory/Context 是 optional non-authoritative provider boundary；Provider records do not replace Domain truth）；`src/backend/zuno/agent/runtime/synthesis/grounded_answer.py:87-88`；`src/backend/zuno/agent/application/finalization/service.py:100-101`
- `边界`: 如果一条 memory 与 Domain 冲突但没人触发 abstain，这条冲突会不会静默漏过去——我没有见过对应的失败测试，不敢断言它一定被拦住。

## A29

没有 A/B。承 A21：这一整套 typed contract + scope 约束**没有做过对照实验**。配对的评测在这个项目里只存在于检索侧（RAG），memory 侧没有。

第二层，没有对照我拿什么说服人：

- 我能拿出来的不是"收益"，是**它防住了哪一类 failure**：跨 scope 泄漏、stale memory 覆盖 Domain、无 provenance 的注入。这三类的共同点是——它们不是"质量差一点"，是"错得没法解释"。
- 代价我也认：多了一层 contract、一层 review 状态、一层 orchestrator，复杂度是真的。
- 所以更诚实的说法是：**这层复杂度今天是"举证不足但失败类真实"**，不是"已被证明值得"。

- `事实层`: Current · Evidence · Unknown
- `证据`: `docs/evidence/current-eval-baseline.md`；`tests/memory/`、`tests/agent/test_context_orchestrator.py`
- `边界`: 收益对照：不存在。我也没有"退回拼 prompt"的对照结果。

## A30

删的条件我可以说得比"没有"更具体一点：

- 如果任务形态退化成**单回合、无跨回合状态**，那 task summary 就没有承载物；
- 如果 scope 收缩到只剩一个维度（见 A78），那 scope 约束这套抽象就退化了；
- 如果 review / provenance 这两类失败被证明不会发生（比如内容根本不进正式结论），那审阅状态机就是多余的。

第二层：

- 三条都成立时，这层应该被收回成"一次请求内拼 prompt"。
- 今天哪条成立？一条都不成立——这是**为什么留着**，不是**为什么值得**。我要把这两个说清楚。

- `事实层`: Target · Unknown
- `证据`: `src/backend/zuno/platform/services/application/context/orchestrator.py:115`
- `边界`: 这三条是我能给的最接近 delete condition 的东西，但它不是被批准的架构决定，是我的判断，也没有触发点被观测到过。

## A31

我不能给你一次"某年某月这个 case 逼我们上 Runtime"的真实事件——那个具体 case 我没有恢复出来，我不编。我能给的是**这个问题本身被文档化过的四种失效窗口**：材料实质变化、Domain 已提交但 Checkpoint 没写、外部动作过了 send boundary 之后响应丢了、权限/资格漂移。

第二层：

- 这四种里第二种和第三种是最直接的"固定 workflow 不够"的理由：workflow 假设每一步都能重入且可重放，但这个系统里有不可重放的副作用。
- 第三种尤其致命：workflow 的重试是幂等的，而一次"已经发出去的通知"不是。

- `事实层`: Target · Unknown
- `证据`: `docs/architecture/architecture.md`（四类 failure window）
- `边界`: 具体是哪一次事故/哪一天触发的：Unknown。我不会把"文档里有这个失效窗口"讲成"我们被它打过"。

## A32

这条链上的状态对象，从入口数下来是：产品侧请求 → `RuntimeStartRequest` → 图内的 `AgentRuntimeState`/`AgentRuntimeSnapshot` → 每个 node 的 `NodeOutcome` → 终结 `finalize()` → `FinalizationService.commit` → Domain repository 落 `agent_run` / `plan_version` / 最终 gate 与 outcome。

第二层，谁写谁读：

- 入口写：`AgentRunApplicationService.create_task` 组 `RuntimeStartRequest`，`AgentRuntimeService.start` 校验 owner refs 之后建 state。
- 图的每一步：`graph.invoke(state.to_snapshot().model_dump(mode="json"))`，每个 node 从 dict 重新 parse。
- 终结写：`finalize()` → `FinalizationService.commit(state)`；随后 `post_turn_commit` 走记忆侧。
- 只有 Domain repository 拥有正式业务事实的写权。

- `事实层`: Current
- `证据`: `src/backend/zuno/api/v1/product.py:168`；`src/backend/zuno/agent/application/run_service.py:60`、`:147`；`src/backend/zuno/agent/runtime/service.py:43`、`:109`、`:183`；`src/backend/zuno/agent/runtime/nodes/core.py:345`、`:391`；`src/backend/zuno/platform/database/agent/domain.py:179`
- `边界`: 我列的是主干，不是穷举；`RuntimeStartRequest` 到 Domain 之间还有 outbox/dispatch 的消费路径（`consume_runtime_request_dispatch`）我这次没有逐行读完。

## A33

有两种对象，分层，而且**今天只有一种真的在跑**：

- **运行时 `PlanState`**：只在进程内，挂在 run state 上，**不是一个表**。它只作为 run JSON snapshot 的一个嵌套字段被 checkpoint 带走。
- **领域 `PlanVersion`**：不可变聚合（DRAFT/ACTIVE/REJECTED/SUPERSEDED，带 `aggregate_version`），有真版本号、有 CAS；但**运行时没有一个表在持久化它**。

第二层，这里我必须纠正我自己的一个讲法：

- `agent_runtime_plan_versions` 这张表和它的写入函数 `append_plan_version` **都存在，但没有 caller**。
- 所以"计划存在 durable store 里"这句话按今天的代码是**不成立的**——它只是被写好了。
- 谁能激活：canonical 路径上是 `service.py` 造的 `plan_version=1, activation_status="activated", activated_by="agent_core"`；被拦的请求是 `plan_version=0`。

- `事实层`: Current
- `证据`: `src/backend/zuno/agent/contracts.py:380-394`；`src/backend/zuno/agent/runtime/state.py:52`、`:111`；`src/backend/zuno/agent/runtime/service.py:301-334`；`src/backend/zuno/agent/runtime/checkpointer.py:34-37`；`src/backend/zuno/agent/runtime/sqlite_store.py:318-325`（无 caller）；`src/backend/zuno/agent/domain/task_contracts.py:38`、`:344-508`
- `边界`: `append_plan_version` 是"写了但没接线"。我无法说这条持久化路径什么时候会被接上，也不 claim 它今天是活的。

## A34

承 A33。前半段我给不了：**引入 PlanVersion 之前你们靠什么判断"这是旧计划留下的动作"，我没有恢复出当时的实现**。我不愿意从今天的机制倒推一个当年的兜底。

第二层，还有一个更要紧的纠正：

- 我 A33 里说"单调 `plan_version` 是核心信号"——这句在**活着的路径上也不成立**。canonical 路径上 `plan_version` 只在构建时被赋成 0 或 1，**没有任何递增路径**；replan 引擎改的是 `status="replanned"` 并追加一步，**不动版本号**。
- 真正带版本语义的是领域聚合的 `aggregate_version`（activate/supersede 里递增）和 `domain_generation`；这些是真的。
- 兜底会漏的那种情况我可以推：如果只剩"同一个 step 身份"这一重信号，那"计划换了、但 step 身份碰巧没变"就会漏。

- `事实层`: Current · Unknown
- `证据`: `src/backend/zuno/agent/runtime/service.py:315`、`:323`、`:331`；`src/backend/zuno/agent/runtime/planning/replan.py:39-45`；`src/backend/zuno/agent/domain/task_contracts.py:488`、`:502`
- `边界`: 当时的兜底具体是什么、在哪类情况漏过：Unknown。这是历史题，我不回填。

## A35

设计是**在结果回来的那一刻**判，而且是硬拒——`BranchResultFencer.accept()` 按 plan version 不是 active、epoch 过期、step hash 不匹配、step run 已作废这几种理由拒收。

第二层，但这里我必须给一个比"有"更准的答案：

- **这套 fencing 今天没有接在 canonical runtime 上。** 唯一调用 `BranchResultFencer` 的是 `DynamicStepWorker`，而 `DynamicStepWorker` **自己也没有 caller**。reducer、replan barrier、join control decision、recovery planner 同样都只有定义、没有 caller。
- 活的图（`graph.py` + `nodes/core.py`）是通过 `PlanExecutor` **顺序执行** step 的，**完全没有分支/晚到结果的 fencing**。
- 所以准确表述是：**这层语义被设计成在结果回来那一刻判，代码也写好了，但它是一条未接线的路径。**
- 提交侧还有 Domain 的 stale 守卫，那道是活的，但它管的是"写冲突"，不是"晚到结果"。

- `事实层`: Current
- `证据`: `src/backend/zuno/agent/runtime/planning/branch_result.py:96-120`；`src/backend/zuno/agent/runtime/planning/dynamic_worker.py:91`；`src/backend/zuno/platform/database/agent/domain.py:437`
- `边界`: 我没有构造过"跨 epoch 晚到"的端到端测试；而且按今天的接线状态，构造了也走不到那段代码。

## A36

**不是同一个事务。** Domain 提交和 checkpoint 写入是两笔独立的写，中间崩了确实会出现"domain 改了、checkpoint 没改"。

第二层，而且这不是被我忽略的角落，是**被显式建模**的：

- canonical graph 用的不是 LangGraph saver——`graph.py` 的注释直接写"checkpointer 是 Zuno 的 domain checkpoint 桥，不是 LangGraph BaseCheckpointSaver"，`graph.compile()` 是裸编的。
- 每跑完一个 node 由 `RuntimeGraphCheckpointer.persist_node()` 单独写一次。
- 那两笔之间的一致性靠 `reconcile_generations(domain_generation, checkpoint_generation)` 事后比对，返回值里有 `fact_owner`、`auto_repair`、`replay_allowed`、`terminate_run`。
- 崩溃点还被命名了：`DOMAIN_COMMIT_BEFORE_CHECKPOINT`。
- 恢复侧规则是 `RecoveryWatermark.recovery_rule ∈ {DOMAIN_WINS, CHECKPOINT_REPLAY, ESCALATE}`，并且校验 domain_generation != checkpoint_generation 就必须有决策。
- 为什么不做成一个事务：运行时存储每次方法调用自己开一个连接/事务，Domain 侧是另一个 `UnitOfWork`——**两个引擎，没有跨 store 2PC**，这条在项目的工程约定里是写明的默认（跨 Store 默认无 2PC）。Domain 侧自己的补偿是**同库 outbox**（domain 事实 + outbox 事件在同一个事务里写）。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/agent/runtime/graph.py:17`、`:75`、`:78`；`src/backend/zuno/agent/runtime/checkpointer.py:13`、`:27`；`src/backend/zuno/agent/runtime/phase08.py:342`、`:796`；`src/backend/zuno/agent/runtime/planning/recovery.py:22`；`src/backend/zuno/agent/runtime_batch.py:220`、`:747`
- `边界`: 这些 reconciliation 逻辑**没有对应的 test 导入**——`phase08.py` 和 `planning/recovery.py` 在 `tests/` 里找不到 importer。所以"它被建模了"可以自证，"它能修对"我不能自证。

## A37

以 **Domain 为准**。domain 在整套 reconciliation 里被显式声明为 fact owner；checkpoint 落后时，checkpoint 是待修复的那一侧。

第二层，这件事谁决定：

- 常规路径由 recovery 决策决定（`DOMAIN_WINS`）；
- 但"这次恢复是否可接受"的最终裁决权不在代码里——`recovery_rule` 有 `ESCALATE` 这一档，也就是说分歧到一定程度是**转人工**的。
- 顺带一句可以说清的：domain 领先、checkpoint 落后时，重放是被限制的（`replay_policy="RECONCILE_BEFORE_RETRY"`），不是"从 checkpoint 重新跑一遍"。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/agent/runtime/phase08.py:342`、`:796`；`src/backend/zuno/agent/runtime_batch.py:220`
- `边界`: 转人工之后是谁接手、SLA 多久——没有证据，答不出来。

## A38

**主要靠人点。** 恢复入口是显式的 resume 调用（要带 approval decision），要求"存在一个 pending interrupt"且"存在最新 checkpoint"；durable runtime 那侧的 `resume_task` 也要求 approval 是 approved/rejected 二者之一。

第二层，自动的那一半能做什么、不能做什么：

- 自动的只有**规划**，而且它**没有接线**：`ParallelRecoveryPlanner` / `Phase21CrashRecoveryMatrix` 是纯函数、没有 caller；`RecoveryAction.RESEND_OUTBOX` 这个"重发"动作**没有任何地方会执行它**。
- 活的路径上，真正防重复的是 store 的 claim（`claim_tool_execution`、effect claim），不是 recovery planner。
- 重放端口 `ReplayPort` 今天只有 in-memory 实现，注释写的是 contract-test 用的；并且有 `replay_generation` 守卫拒绝 stale replay。
- 结论：**自动重放带副作用动作这件事，今天既没有权限也没有实现**——这是双重保险，不是我给它设的边界。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/agent/runtime/service.py:202`、`:227-238`；`src/backend/zuno/agent/durable_runtime.py:272`；`src/backend/zuno/agent/runtime/planning/recovery.py:12`、`:176`、`:218-225`（无 caller）；`src/backend/zuno/platform/recovery/replay.py:58`、`:70`、`:84`
- `边界`: `ParallelRecoveryPlanner` 那套是"写了没接"。我不把它讲成"我们的恢复策略"，因为按今天的接线它不参与运行。

## A39

承 A37。LangGraph 原生确实覆盖了两块：图执行和 Postgres checkpointer（ADR-0005 采纳了官方的 `langgraph-checkpoint-postgres`，`3.1.0`，2026-07-18）。

第二层，自研补的 delta，以及一个我必须摆到台面上的**矛盾**：

- delta 是**领域侧的**：domain 才是 fact owner、plan version 的激活只能一次、replan 需要一个正式的 new plan version、分支结果要按 epoch/plan/step 拒收、budget 要按 step 准入、effect 要绑 receipt。
- **矛盾**：ADR-0005 明确要求官方 saver 是唯一的 checkpointer 基座，并且**不允许**用自研桥/SQLite store 替代它——而 canonical 那条路**正好就是**自研桥。官方 saver 只在 `phase08.py` 里被接上，而 `phase08.py` **没有生产 caller、也没有测试**；还有一条测试反过来禁止存在一个 cutover 文件。
- 所以今天真实状况是：**ADR 要求的和主线跑的是两条路**，不是"我们按 ADR 做了"。
- 为什么不能直接换成原生恢复：原生恢复的语义是"从 checkpoint 重跑"，而这里有 Domain 已提交、checkpoint 未写的窗口，重跑会重复副作用。

- `事实层`: Current · Target
- `证据`: `docs/decisions/0005-official-langgraph-postgres-checkpointer.md:14-16`；`src/backend/zuno/agent/runtime/phase08.py:8-11`、`:36-42`、`:93`、`:136-153`；`src/backend/zuno/agent/runtime/graph.py:14-20`、`:75`；`tests/repo/test_agent_system.py:36`
- `边界`: "为什么主线图没接官方 saver"——我没有找到当时的决策记录，不编。我也不能判断这是"过渡态"还是"永远不会接"。

## A40

收回条件我给三条，必须同时成立：一是 Domain 提交与 checkpoint 写入能做成一次原子写（或 single-writer），那条 split-write 窗口消失；二是"计划只能激活一次"、"晚到结果按 epoch 拒收"这类语义能用框架原生的 interrupt + state guard 表达出来；三是 effect/授权绑定不需要运行时的 plan 版本参与。

第二层：

- 三条齐了，`RuntimeGraphCheckpointer` 这层桥就该被删掉，直接用 saver。
- 今天哪条成立？一条都不成立——第一条就不成立，两笔写是两个存储。
- 我要说清一点：这是 Target 推理，不是排期。

- `事实层`: Target · Unknown
- `证据`: `src/backend/zuno/agent/runtime/checkpointer.py:13`；`docs/decisions/0005-official-langgraph-postgres-checkpointer.md`
- `边界`: 我把第一条当成硬前置，但我没有验证过"能不能做到原子"。这是判断，不是已评估的方案。

## A41

先说一句定位：`src/backend/zuno/security/` 这个目录**不存在**，安全模块在 `src/backend/zuno/platform/security/`。

"谁被允许调用哪个 Tool、对哪个对象"是在**平台安全层**定义的，而且不是一条规则，是三样东西：一张 tool 的副作用画像表（`side_effect_level` 决定要不要审批、要不要沙箱、凭据策略、网络策略、要不要审计）、一个 `AuthorizationDecision`/`ActionAuthorizationDecision`，以及落到 `security_authorization_decisions` 表的持久化决定。

第二层，我必须先划自己的边界：

- 这一层**不是我的 Ownership**。我的 Tool/MCP 工作的落点是在产品侧的配置注入，不是这个授权面。
- "对哪个对象"这个问题的答案落到 `target_resource_set`：从参数里的 `url/path/endpoint/resource/target/query/to` 这些键抽出 resource_refs 和 conflict keys。

- `事实层`: Current · Unknown（Ownership 侧）
- `证据`: `src/backend/zuno/platform/security/governance.py:300`、`:320-347`；`src/backend/zuno/platform/security/runtime_batch.py:17`、`:136`、`:215`；`src/backend/zuno/platform/security/persistence.py:474`；`src/backend/zuno/capability/tool_runtime/effect_policy.py:90`
- `边界`: 这套是谁设计的、什么时候进来的：我不知道，不 claim。副作用矩阵里"write_external → 审批+沙箱+brokered 凭据+allowlist+审计、destructive → 默认拒"这些策略是谁拍的：Unknown。

## A42

**两个时刻都查，而且是刻意重复的。** 一次在工具选择/准入时，一次在真正 dispatch 之前。

第二层，具体落点：

- 选择/准入选拔：`capability/runtime.py` 里 `ToolSecurityGate().evaluate(profile=...)`。
- prepare 阶段落库校验：`validate_pre_effect_authorization(...)`。
- dispatch 前的再检查有两道：一道 `_reauthorize_execute_epoch(...)`，一道就在 `executor()` 调用前——代码注释写得很明白：**"审计持久化不是一张永久授权票"**，所以落完 durable proof 之后、任何 sandbox/provider dispatch 之前，要再按当前安全状态检查一次。

- `事实层`: Current
- `证据`: `src/backend/zuno/capability/runtime.py:490`、`:375`；`src/backend/zuno/capability/tool_runtime/invocation_gateway.py:388`、`:1060`、`:459-462`、`:535`
- `边界`: 这两次检查之间有多大窗口、窗口里权限真的变了会不会被这次检查抓住——我是从代码结构读出来的，没有构造过竞态测试。

## A43

会被挡住，而且是 **fail-closed**：执行前发现 epoch 不是 active，直接抛 `"stale security epoch before effect"`，不执行。

第二层，系统靠什么知道权限变了，以及一个我必须主动说的缺口：

- 靠的是 `EffectiveSecurityEpoch.revocation_generation`：每次调用生成一个 `security-epoch:tool-effect:{scope_hash}` 的引用；effect 前按它重读当前 epoch 状态。
- 有一条测试专门固定了这个行为：先落审计、再用裸 SQL 把 epoch 改成 `revoked`，断言 executor 从未被调用、审计 1 条、effect 0 条。这是 negative history #203 那条。
- **缺口**：我 grep 了整个 `src/backend/zuno`，对 `security_effective_epochs` 只有 `INSERT`/`JOIN`/`SELECT`——**没有一条生产代码路径会 revoke 一个 epoch**，唯一把 status 置成 revoked 的是测试里的那个裸 SQL 接缝。也就是说：fail-closed 的**门是有的、锁是真上了**，但"谁来转这把锁"这件事，我今天指不出来。

- `事实层`: Current · Evidence · Unknown
- `证据`: `src/backend/zuno/platform/security/persistence.py:356`、`:1073-1074`；`src/backend/zuno/capability/tool_runtime/invocation_gateway.py:198`；`tests/security/test_mandatory_audit_postgres_boundary.py:835`、`:848`
- `边界`: 生产侧的 epoch 撤销路径：**缺失**。这是我今天最想主动交代的一个洞。

## A44

有，而且是**强制在 effect 之前**写。记录里写的是：谁（`owner_id`，形如 `tool-runtime:{call_id}`）、什么操作（`action="tool.execute"`）、基于哪一份授权（`authorization_decision_id`），外加 `security_epoch_ref`、`prepared_tool_action_id`、`prepared_action_hash`、租户 id、审计需求 id/hash。

第二层，这套的关键在于"写着不算，要能读回来才算"：

- 落库进 `infra_mandatory_audit_events`，状态写 `durable`。
- 落完之后立刻**重读校验**（`assert_audit_durable_for_effect`），读不回来就 `FencingRejectedError`——原话是"effect cannot run before tenant-scoped durable mandatory audit"。
- 审计需求本身也会在 proof commit 之后再校验一次，变了就报 `mandatory audit requirement changed after proof commit`。

- `事实层`: Current · Evidence
- `证据`: `src/backend/zuno/capability/tool_runtime/invocation_gateway.py:430`、`:1426`、`:1478-1490`、`:1506-1520`；`src/backend/zuno/platform/database/foundation.py:1618`、`:1747`；`infra/db/alembic/versions/20260718_12_mandatory_audit.py:47`
- `边界`: 审计类别分级、以及审计表自身的 crash/restart 生命周期修复，证据文档里写的是 **not proven**，我认同这个判断。

## A45

靠**关闭状态**判断，不靠"读日志猜"。每条审计行有两种合法结局：`mark_audited_effect_observed`（确实发出去了）和 `mark_audited_effect_dispatch_aborted`（确定没发出去，容量释放）。

第二层，判定精度还有一个专门的类型：

- `DispatchCertainty`：`NOT_DISPATCHED / DISPATCHED / MAYBE_DISPATCHED`——系统自己承认存在"可能发出去了"这一档。
- 重启后不去重放，而是**类型化重述**：`describe_side_effect_result_ref` 返回 kind（EFFECT_RECEIPT / RECONCILIATION / ASYNC_JOB / UNKNOWN）和 certainty，gateway 再映射成 `replayed` / `confirmed_not_executed` / `reconcile_required` / `async_waiting`。
- 一条硬约束：已经 `dispatch_aborted` 的行不能反过来再被授权。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/database/foundation.py:1793`、`:1828`、`:1662-1665`；`src/backend/zuno/capability/tool_runtime/runtime_batch.py:52`、`:58`；`src/backend/zuno/platform/database/tool_runtime/domain.py:943`；`src/backend/zuno/capability/tool_runtime/invocation_gateway.py:1339`、`:1365-1408`
- `边界`: "确定没发出去"的判定究竟基于什么证据（进程内标志？还是远端确认？）——我没有逐行读 `dispatch_aborted` 的判定条件，不敢展开。

## A46

默认动作是**既不重试也不放弃，转对账**，到时间转人工。开一条 OPEN reconciliation，状态机是 `UNKNOWN → RECONCILING → {SUCCEEDED, FAILED}`，其中只有对账结论 `CONFIRMED_NOT_EXECUTED` 才允许重发同一个 effect。

第二层，谁定的：

- 这条默认值不在我手里——它属于 tool runtime / security 这一层的平台设计，不是我那笔 Tool/MCP 配置注入改动的产物。
- 时效上有一个常量：开 reconciliation 时 `age_escalation_after_seconds=900`，超过就 sweep 成 `ESCALATED` / `MANUAL_ASSESSMENT`。

- `事实层`: Current · Target · Unknown（Ownership 侧）
- `证据`: `src/backend/zuno/capability/tool_runtime/runtime_batch.py:360-361`、`:460`；`src/backend/zuno/platform/database/tool_runtime/domain.py:1188-1199`
- `边界`: 900 秒怎么来的：没有依据可追，我不 claim 它是调过的。

## A47

对账机制**有骨架，但没有跑起来的那一半**。诚实版本是这样：系统会落一个对账查询描述、把幂等键和业务键（`prepared_action_hash` + `target_resource_set_ref`、`provider_effect_id`）一起存下来；但**没有任何代码真的拿这个描述去远端查**——它只被写入和被 hash，没有 reader、没有执行器。

第二层，所以你的三个子问题分别是什么状态：

- "怎么确认系统认为的和现实一致"：靠人工判定路径收口——`record_manual_effect_assessment`，只有结论是 `CONFIRMED_EXECUTED` / `CONFIRMED_NOT_EXECUTED`（且残留不确定性为空）时才去 resolve，非结论性的会被拒：`reconciliation conclusion must be conclusive`。
- "多久跑一次"：我能指出的只有 sweep 入口（`escalate_due_reconciliations` / `timeout_due_async_jobs`）和 gateway 包装；**调度这些 sweep 的 cron/worker**，我没有证据说它存在。
- "对不上怎么处理"：转人工评估。

- `事实层`: Current · Evidence · Unknown
- `证据`: `src/backend/zuno/capability/tool_runtime/invocation_gateway.py:1958`、`:1787`、`:1823-1825`、`:1607`、`:1614`；`src/backend/zuno/platform/database/tool_runtime/domain.py:146-165`、`:1028-1185`；`docs/project/reference.md`（"Provider remote-query integration … remain unproven"）
- `边界`: 远端对账查询执行 + 调度频率：**缺失**。这是 evidence 文档自己写明的未证明项，我完全同意。

## A48

真的改过外部现实，但不是法院侧。`src/backend/zuno` 里 grep `court|法院|judicial|审判|立案` **没有任何命中**——法院侧系统集成不存在。真实对外发出去的有：SMTP 发邮件（`smtplib` 真连）、物流查询 HTTP（urllib 真打阿里云）、Lark/飞书消息（MCP server 里是真 `lark_oapi` 客户端）。

第二层，重复/漏执行：

- 我没有可讲的**生产事故**——没有生产环境，就没有生产事故。
- 能被证据支持的是：重复投递抑制和对账在**测试层面**被固定过（未知 effect 跨进程重启后仍保持 reconcile-required、结论性"未执行"永不变成 completed 也不重发）。
- 另一类证据是负向历史条目：#201（UNKNOWN effect 被错误升级成 completed）、#205（缺 durable proof 仍然 dispatch）、#207（租约前凭据撤销）。

- `事实层`: Current · Evidence · Unknown
- `证据`: `src/backend/zuno/capability/tools/send_email/action.py:171-177`；`src/backend/zuno/capability/tools/delivery/action.py:50`；`src/backend/zuno/capability/layer.py:481`、`:585`；`tests/capability/test_tool_effect_postgres_boundary.py:222`、`:359`；`docs/evidence/implementation-wave-001.md`
- `边界`: "当时是怎么发现的"——我答不出来，我不把测试里的断言讲成一次真实发现。

## A49

承 A43。这一段我给不出完整答案，我给能给的：

- **更严格的 effect/授权之前靠什么兜底**：我不知道当时的实现，不回填。能推的最保守版本是"人工复核 + 只读限制"，但那是我从"后来为什么加 fail-closed"倒推的，不是证据。
- **能追到的演进动因**是负向证据条目：#203 讲的是"发送前 SecurityEpoch 撤销必须 fail-closed"，#207 讲的是"租约前凭据撤销必须 fail-closed"，#205 讲的是"强制审计要求没有持久化证明却已经 dispatch"。
- 这三条读起来指向同一个方向：**审计/授权这一层最初是"先做出来"，后来被补成"没有 durable proof 就不许出网"**。

- `事实层`: Historical · Evidence · Unknown
- `证据`: `docs/evidence/implementation-wave-001.md`（negative history #203/#205/#207）
- `边界`: 当时的决策会议、谁推动的、有没有真实事故驱动：全部 Unknown。我不会把"负向历史条目存在"讲成"我参与了那次决策"。

## A50

这一层不是我的 Ownership，所以我给的是**判断**，不是"我会怎么改我自己写的东西"，这一点我要先说清。

第二层，我认为最该被合并/砍掉的三处：

1. **回执三件套可以收**：execution receipt / effect receipt / reconciliation 三种输入类型里，execution 与 effect 的区分主要服务"发没发出去"和"改没改现实"两个问题，但它们的字段高度重叠；我倾向于留 effect + reconciliation，把 execution 折进 effect 的 certainty 里。
2. **手工评估那条路可能是临时物**：`ToolManualEffectAssessmentInput` 是为了"没有远端查询也要收口"而存在的；一旦 A47 里缺的那半（远端对账执行）补上，它应该被降级成 escalation 的一个分支，而不是一个独立对象。
3. **最该被质疑的是只有测试接缝才走得通的路径**：epoch revocation 今天没有生产者（A43）。一个只有测试能触发的状态机分支，要么补上生产者，要么承认它不该有独立对象。

- `事实层`: Current · Target · Unknown（Ownership 侧）
- `证据`: `src/backend/zuno/platform/database/tool_runtime/domain.py:29`、`:49`、`:75`、`:125`、`:146`、`:249`
- `边界`: 我不是这一层的 owner，也没有删除的收益/风险测量。上面是"如果重做我会怎么合"的推理，不是已决定的方案。

## A51

我不能凭记忆给你指一个"我当时亲眼看到它跑通的入口"——这件事我今天没法诚实做到。能确认的存量基线是：我大约 2026-03 加入时，项目和代码已经存在，**已经有一个简单的自研前端**，不是绿地。

第二层，还有一个我今天必须一起交代的坑：

- git 历史里第一个 commit 是 `eafeb1c2`（2026-04-15，"Initial commit"）。也就是说，**我能看到的 git 历史是从我加入之后才开始的**——它既不能证实"系统早于 4 月存在"，也不能否证。
- 所以关于"入职第一天的存量"，我有文档依据（pre-existing code + simple custom frontend + 约 7–8 人核心研发），但**没有一个我可以指给你看的、当年跑通的入口**。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md`（joined around 2026-03；project and code already existed；greenfield: false；约 7–8 人）
- `边界`: 具体入口：Unknown。我不把"文档说它已经存在"讲成"我看过它跑"。

## A52

这笔我答不实。我能自证的最早个人改动是 Tool/MCP 那一笔（`773467580ee428a0536c7f594c0847c1510879ac`，2026-04-15），但"**第一笔**改动"——也就是在那之前我有没有更早的 commit——我没法从历史里单独切出来。

第二层，为什么切不出来，是个结构性问题：

- 仓库 2161 个 commit 里，人只有极少数身份：`ProfessorZhi`、`WenHi Huang`/`vince`（同一邮箱）、以及自动化（Claude Code + MiniMax、minimax1、github-actions）。也就是说，**历史里的"人"几乎只有一个**——我无法用作者字段区分"我"和"别人"。
- 在这种情况下，任何"这是我的第一笔"都会是叙事，不是证据。

- `事实层`: Historical · Personal Ownership · Unknown
- `证据`: commit `77346758`；`git shortlog -sne` 作者分布；`docs/governance/project-fact-provenance.md` PF-032
- `边界`: 真正的"第一笔"：Unknown。我宁愿说不知道，也不编一个日期。

## A53

逐条切：

- **第 1 条 Tool Calling 重构**：我做的（`77346758` 2026-04-15 / `0b5fb350` 2026-04-28）。但要说清：那两笔范围很宽，我不是整笔的唯一贡献者，也不 claim 它是"从零写"。
- **第 2 条 GraphRAG 排序回退**：方向是既有的（图路由本来就在），定位 + 方案 + 实现是我在这一段里做的（`5d9b719e` 等）。
- **第 3 条 多跳图检索优化**：同一条线上的延续，三个 heuristic（seed expansion / alias / path ranking）是我实现的。
- **第 4 条 scoped Context/Memory V2**：我做的，但它所在的文件**后来被删了**（`ab1222da`）。
- **第 5 条 Memory readback 收紧**：我做的（`f3c74338`，PR #8）。
- **一条都不是"从零写"**——五条全部是在一个已经存在的系统上改。这个前提我不接受被省略。

- `事实层`: Historical · Personal Ownership · Current
- `证据`: `docs/governance/project-fact-provenance.md` PF-029/PF-030/PF-031/PF-032；commit `77346758`、`0b5fb350`、`5d9b719e`、`c7814793`、`c17f737f`、`762ffdc7`、`d4e2fe2e`、`f3c74338`、`ab1222da`
- `边界`: 第 1 条我给的边界最重：`0b5fb350` 是一笔宽 commit，其中的 Tool Calling 部分不能整笔算我的；而且那一笔**没有恢复出历史 CI run**。

## A54

承 A53。那套转发是**别人写的**——我修的是它，不是它。

第二层，我能给出的是它的形状和我的推断，两者我要分开：

- **形状（可查）**：被删掉的那套包括 `tool_invocation_model`、`available_tools`、`LLMToolSelectorMiddleware`，以及把 MCPAgent / SkillAgent 当成 Tool 嵌套进去的结构；另外 `MCPAgentTable` 和 `api/v1/mcp_agent.py` 的 CRUD 面到今天还在，但已经不被 workspace adapter 引用了；`multi_agent_enabled` 这个字段还存着，但**没有任何 reader**。
- **推断（不可查）**：让子 Agent 中转的动因，最合理的解释是"每个 MCP server 需要自己的用户级配置/凭据上下文"。但这是我的推断，不是记录。
- 我要强调最后一点：**我不能说"原始动机我知道"**。

- `事实层`: Historical · Unknown
- `证据`: `docs/governance/project-fact-provenance.md` PF-032；`src/backend/zuno/platform/services/workspace/simple_agent.py:288`；`src/backend/zuno/api/v1/mcp_agent.py:18-142`
- `边界`: 作者是谁、原始动机是什么：Unknown。历史里作者身份不可区分（见 A52）。

## A55

承 A52。这题我得小心，因为它隐含一个"中间隔了很久"的期待，而事实可能正好相反：我能自证的 Tool/MCP 第一笔和"直接绑定主 Agent 落地"是**同一天**（2026-04-15），收紧递归那笔在 2026-04-28。

第二层：

- 所以如果我硬给你一个"隔了几个月"的故事，那是编的。
- 我唯一能诚实说的：在这条线上，**那笔重构本身就是我很早的改动之一**，我没有一段"先做别的事、后来才动它"的可自证历史。
- 至于 2026-03 到 2026-04-15 之间我在做什么——历史里没有我的可辨识痕迹，我答不出来。

- `事实层`: Historical · Personal Ownership · Unknown
- `证据`: commit `77346758`(2026-04-15)、`0b5fb350`(2026-04-28)
- `边界`: 2026-03 到 04-15 期间我的工作密度：Unknown。

## A56

承 A54。**方向不是我提的**——GraphRAG 图路由、planner 的图开关在我在这个项目之前就已经存在。我做的层级是：定位 + 定方案 + 写实现，三段都在一个**很窄的范围内**。

第二层，我要把"我到底定了什么"具体化，因为这才是 Ownership 的真边界：

- 我定的是 heuristic：seed expansion、别名归一化、path-aware ranking，以及 fusion 里那 9 个阈值和分层。
- 我没有定的是：图该不该存在、图候选该不该进融合、指标体系该是什么——这些是既有的。
- 我承认最弱的一环：那几个阈值**是我拍的**（A16），拿不出依据。

- `事实层`: Historical · Personal Ownership
- `证据`: commit `5d9b719e`、`c7814793`、`c17f737f`、`762ffdc7`、`3da5d742`；`docs/governance/project-fact-provenance.md` PF-031
- `边界`: "方向已经定了交给我执行"这句话里的**决定者是谁**，我没有记录；我不 claim 是我提的方向，也不 claim 别人明确指派给我。

## A57

承 A51。**不存在**。typed contract、版本、receipt 这一整套，在我加入的第一个月是不存在的——`PlanVersion`、`SecurityEpoch`、`PreparedAction`/`EffectReceipt` 这些对象都是后来的。

第二层，至于"当时靠什么保证同一件事"，这是我的一个明确的缺口：

- 我不知道当时的兜底。原因是结构性的：那段代码在我能看到的 git 历史之前或之后被换掉了，我没法指认"当时的哪一段实现了今天的哪个机制"。
- 我唯一能确定的是**今天这些机制有明确落点**（见 A32–A48），以及**它们不是我在第一个月建的**。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md`（current target architecture != historical architecture ownership）
- `边界`: 当时的兜底实现：Unknown。这题我不回填今天的机制。

## A58

承 A53。我给不出一个"从头到尾没改过"的模块——因为我只在一个很窄的切片里工作过，**"我没碰过"和"它没被改过"是两件事**，我不会把它们混起来讲。

第二层，能确定的是我的覆盖面边界：

- 我碰过的：产品侧的 workspace/tool 装配与路由、检索融合的 heuristic 层、context/memory 的读取与写回。
- 从我的 commit 记录看**可以被认为没碰过**的是：07 Model Gateway、09 Observability & Evaluation。
- 但我只能给出"我没有碰过的证据"，不能给出"接口从头到尾没变过"的证据——后者需要逐模块看历史，我没做。

- `事实层`: Unknown · Personal Ownership
- `证据`: 无
- `边界`: "接口从未变过"：我没有做过这个核对，所以答不出来；答不出来不等于没问题。

## A59

承 A53、A56。这题我给你一个可能不在预期内的答案：**逐行 blame 切不出三方**。

第二层，理由是硬事实：

- 仓库里的"人"几乎只有一个身份谱系（`ProfessorZhi` / `WenHi Huang` / `vince`，同一邮箱），其余是自动化账号。所以 blame 只能告诉我"某一笔是自动化的还是这个身份谱系的"，**不能告诉我"这是我、这是学长、这是团队另一个人"**。
- 因此我做不到你要的拆分。我能做的拆分只有另一种粒度：**"这笔 commit 的存在/不存在"**——`5d9b719e`/`c7814793`/`c17f737f`/`762ffdc7` 是修复，`ab1222da` 是删除。
- "约 7–8 人核心研发"这个数是**文档**给的，不是 blame 给的。这两件事我不合并。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md`（约 7–8 人）；`git shortlog -sne`
- `边界`: 逐行归属：**不可恢复**。这是这轮我最想说清楚的一条——不是我不愿意说，是证据不存在。

## A60

我留**第 2 条：GraphRAG 排序回退**。删掉另外四条。

第二层，为什么是它，以及我为什么认可"删四条"：

- 它是五条里证据链最完整的：有具体 bad case（`Ed Wood` / `Shirley Temple` 被挤出去）、有回归测试、有修复前后的指标（`Recall@5` 0.80→1.00，`MRR@10` 0.80→1.00）、有冻结的 ablation 协议来标注它的边界。
- 另外四条各自的弱点我直接说：第 1 条 commit 太宽、归属不可切；第 3 条是同一条线上的延续，但证据只有 5-query smoke；第 4 条所在的文件**已被删除**，今天是历史而非 Current；第 5 条与第 4 条同源，且 `prepare_context()` 这个名字在今天的代码里已不是函数（A24）。
- 注意我留它**不是**因为它"效果最好"——它的指标也是 tiny smoke 级。我留它是因为它的 **claim 和证据匹配**。

- `事实层`: Personal Ownership · Evidence
- `证据`: `docs/governance/project-fact-provenance.md` PF-031；`tests/graphrag/test_graphrag_baseline_preserving_fusion.py`
- `边界`: 即便留这一条，它的正确上限也是"bounded regression fix"，不是"GraphRAG 更好"。

## A61

发起主体和在场角色，我给不出——`docs/governance/project-fact-provenance.md` 里对法院侧测试/Pilot 明确写了：规模、题目集、评审协议**均未恢复**。我不会靠记忆补一个座位表出来。

第二层，能确定的是这件事在里程碑序列里的位置：既有的产品/代码 → 内部 demo → 客户/智慧法院侧 demo → 质量反馈 → 迭代 → 法院侧测试 → Pilot Validation。

- `事实层`: Historical · Unknown
- `证据`: `docs/governance/project-fact-provenance.md` PF-018/PF-019；`docs/project/reference.md`
- `边界`: 发起方、在场角色、是不是"正式测试"：Unknown。我要点明一个诚实的方向：既然协议都没恢复，我**不能**把它讲成一次有第三方验收的测试。

## A62

我不能声称我本人当面跑过现场 demo。这是我必须给的答案——我记不清有没有、也不愿意把一个模糊记忆讲成一次现场经历。

第二层：

- 能确认的是**项目层面发生过 demo**（客户 / 智慧法院侧 demo 在里程碑序列里）。
- 但"这场 demo 是谁跑的、是不是预置输入、有没有走全路径"——没有恢复到证据。而且你这个问题问的恰恰是这个：如果是预置输入的演出，它就**不等于系统真的能跑**。
- 所以我的答案是：我没有一个可自证的现场经历可以给你。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md`（milestone 序列）
- `边界`: 我本人现场跑过没有：Unknown。这个"不知道"我不打算用"应该跑过"来抹平。

## A63

承 A51/A61。使用时长和频次，我不知道——这是未恢复项，不是我不愿意说。

第二层，能说的边界：

- "Pilot Validation"在文档里是一个里程碑定性，但它**没有**附上"每天用/隔几天用一次/只测了一轮"这类使用强度信息。
- 所以任何"持续用了几个月"的说法我都不会讲。**没有这个数**。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/reference.md`；`docs/governance/project-fact-provenance.md` PF-019
- `边界`: 时长、频次：Unknown。

## A64

承 A63。这个词的出处我能追：它是**项目/架构文档里的定性**，被写进里程碑和简历的语境里；它不是法院/甲方出具的一份验收结论——至少我找不到任何一份法院侧的验收文书来支撑它。

第二层：

- 这一点很重要，因为它决定了这个词的"重量"：如果它是我们自己的定性，它描述的是"做了试点验证这个动作"，不是"第三方判定通过"。
- 而且文档自己就补了一句：Pilot Validation 仍然属于试点，不构成 Production。

- `事实层`: Historical · Unknown
- `证据`: `docs/project/README.md`；`docs/governance/project-fact-provenance.md` PF-018/PF-019
- `边界`: 有没有一份法院侧书面结论：**没有**（我不 claim 存在，也不 claim 明确不存在——我 claim 我没有证据）。

## A65

只有一条，而且它是一句汇总，不是一条 case：客户反馈是"**回答质量还需要提高**"。至于这条反馈对应哪个具体 bad case、root cause 是什么——**当没有被恢复出来**。

第二层，我要主动加一句边界，因为它是个陷阱：

- 这条反馈和 GraphRAG 那条线**必须保持独立**，不能合并成"因为回答质量差所以我们做了 GraphRAG"。
- 而且"回答质量还需要提高"是用户侧的感受，不是我们定位到的一个技术故障；把它讲成一次"收到 bad case 然后修好"的闭环，是升级证据。

- `事实层`: Historical · Evidence · Unknown
- `证据`: `docs/governance/project-fact-provenance.md` PF-017
- `边界`: 具体 bad case 与 root cause：Unknown，且 provenance 文档明确要求它与检索线保持独立。

## A66

来源我分三类说，不给你数值：

- **检索指标**（`Recall@5`、`MRR@10` 那些）：来自 `tools/evals/zuno/multihop_eval/` 的 run，记录在 provenance 的 PF-031 和 eval README 里。是我跑的 retrieval-only 评测。
- **测试数**（`224 passed`）：来自一次**固定快照**的 CI run（run `35516807526`，快照 `5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660`）。这是"某次跑过"，不是 Full CI——证据文档自己写着 `FULL CI: NOT RUN`。
- **性能/规模类**：**没有来源，因为不存在**。没有 QPS、没有 latency、没有成本、没有法院数量、没有用户量。

- `事实层`: Evidence · Unknown
- `证据`: `docs/evidence/current-test-baseline.md`；`docs/evidence/current-eval-baseline.md`；`docs/governance/project-fact-provenance.md` PF-020/PF-022/PF-031
- `边界`: 任何我没列出的数，就是没有。

## A67

承 A63。**我不知道会不会有人来问。** 我不把"Pilot ≠ Production"顺手讲成"所以一定没人依赖"——那是两个不同的断言，后者我没有证据。

第二层：

- 我能提供的间接事实是：没有生产部署、没有 SLA/值班/事故记录，也没有任何"依赖它"的运维证据。
- 但"有没有人在用、关掉会不会被发现"这件事，取决于我不知道的现场安排。
- 所以这题的正确答案是：**Unknown**，并且我不用它来加强"这不是生产"的论点——那个论点有别的、更硬的证据（A69）。

- `事实层`: Unknown
- `证据`: 无
- `边界`: 真实依赖是否存在：Unknown。

## A68

用例和验收标准是谁写的，我没有证据——`PF-018/PF-019` 明确说规模、题目集、评审协议未恢复。所以"法院有没有出自己的题"我也答不了。

第二层，但我要主动把风险自己说出来，因为这是这题真正想问的：

- 如果题目集和验收标准都是我们自己出的，那它就是**自证**——自出题自验收，不能支撑任何"被验证过"的强 claim。
- 既然我拿不出"法院出题"的证据，那我在这一题上的立场就是：**在没有独立标准之前，我不会把法院侧测试讲成验证。**
- 我不会用"应该有法院参与"来补这个洞。

- `事实层`: Unknown
- `证据`: `docs/governance/project-fact-provenance.md` PF-018/PF-019
- `边界`: 出题方与验收方：Unknown；且我承认"自证"是当前无法排除的可能。

## A69

承 A64。第一位原因不是"效果还不够好"，而是：**它从来没有成为法院侧的生产依赖。** 没有部署、没有值班、没有 SLA、没有事故记录，也没有任何运维/故障数据。

第二层，我把它落成可查的状态标签，不靠形容词：

- `PRODUCTION_READINESS: NOT_ESTABLISHED`
- `FULL CI: NOT RUN`；QUALITY: `not_yet_proven`
- COURT QA: `UNKNOWN`
- 没有 QPS / latency / 成本 / 高可用 / 容灾数据

- `事实层`: Current · Evidence
- `证据`: `docs/evidence/current-runtime-baseline.md`；`docs/evidence/current-eval-baseline.md`；`docs/evidence/current-test-baseline.md`
- `边界`: 我特意不说"效果不够"当第一位原因——那会把一个部署/运维事实换成一个质量判断，我手上没有质量对照数据来支持它。

## A70

最诚实的一句话：**"没有，Zuno 没有在法院生产环境跑过；法院侧只到试点验证，没有任何生产依赖。"**

第二层，为什么我仍然保留 Pilot Validation：

- 因为那个词是**准确的**。Pilot Validation 在这份材料里的定义就是试点，而且项目文档明确写了"Pilot Validation 仍属于试点"，也明确禁止把它升级成 Production。
- 把它删掉反而是一种不准确：那会让读者以为连试点都没做过。
- 所以我保留它不是为了好看，是因为它是我能举证的上限；我要做的只是**不让它往上漂**。

承 A64、A67：这句话和我前面两答的口径是一致的——A64 说这个定性来自项目侧，A67 我说关掉会不会被发现是 Unknown。这两点都不加强"这是生产"，也不削弱"这是试点"。

- `事实层`: Historical · Current
- `证据`: `docs/project/README.md`；`docs/governance/project-fact-provenance.md` PF-018/PF-019
- `边界`: Pilot 期间的实际使用规模：Unknown（A63）。这句话我不加任何规模形容词。

## A71

老实说：**我没有统计过调用方数量**，所以"哪些模块只有一到两个调用方"我答不准。我如果给你一个清单，那是我凭印象编的清单。

第二层，我能给的是"看起来窄"的候选，并且标明这是印象不是测量：

- 07 Model Gateway：消费方基本收敛在需要真实模型调用的那几处。
- 09 Observability & Evaluation：更像横向能力被各模块引用，而不是有自己的调用图。
- 05 Capability & Skill：我从它身上讲不出一个独立的 authority，它的内容我倾向于认为可以并进 06。

- `事实层`: Current · Unknown
- `证据`: `docs/architecture/architecture-views.md`（B2 authority matrix）
- `边界`: 调用方计数：**没做过**。这三个是我的怀疑对象，不是结论。

## A72

如果必须点一个，我会先动 **05 Capability & Skill**——不是删掉它的内容，是把它的独立身份并进 06 Tool Runtime & Effects。

第二层，为什么是它而不是别的：

- 我对它的测试是"删掉它，主流程还能不能跑完"，而这条路径上的实际执行语义（工具怎么跑、effect 怎么记、失败怎么对账）都在 06。05 更像一份分类法。
- 但我也要说清另一件事：**九个模块不是九个微服务**，所以"删模块"在我的理解里是"合并责任域"，不是"下线一个进程"。如果你问的是后者，我的答案会不一样。

- `事实层`: Current · Target
- `证据`: `docs/modules/README.md`；`docs/architecture/architecture-views.md`
- `边界`: 我没有实际做过这个合并的可行性核对；这是我今天的直觉，A75/A79 会对它做压力测试。

## A73

能论证的只有 **05**：把它的内容并进 06 之后，Tool 调用的主流程我讲不出会缺哪一步。

第二层，我要对"删掉无损"这个说法加个限定：

- "跑得完"不等于"没损失"。05 如果承载着"能力/技能的定义权"，那它消失之后这份定义权会临时没有主人。
- 06 能接住它，是因为 06 本来就在管工具的 effect 语义——这是**接管**，不是**无损**。
- 所以更准确的回答是：**05 是唯一一个我能论证"可以在不改变主流程结果的前提下被合并"的**，而 09 我论证不了（删掉它 evidence 就断了）。

- `事实层`: Current · Target
- `证据`: `docs/modules/README.md`
- `边界`: 我没验证过合并后的实际影响；这是论证不是实验。

## A74

我为架构完整性加过、而不是被 bad case 逼出来的，最明显的是 **fusion 里那套 guardrail 阈值层**：comparison / bridge / genealogy 三组，9 个常量。我能给 GraphRAG 回退那个 bad case 配一条证据，但我给不出"为什么 comparison 要 3、bridge protected top 要 2"这类问题的 bad case。

第二层，第二个我认的是 **手工 effect 评估那类对象**：它在"没有远端对账也要收口"这个理由下是合理的，但它今天更像"因为这个状态机需要一个出口"而存在。

- `事实层`: Current · Personal Ownership
- `证据`: `src/backend/zuno/platform/services/retrieval/fusion.py:9-17`；`src/backend/zuno/platform/database/tool_runtime/domain.py:249`
- `边界`: 我这句自认可能会伤到我自己的第 2、3 条 bullet——我先认，而不是等你抓。注意 `domain.py:249` 那个对象不是我的 Ownership，我引用它是作为"我观察到同样气味"的例子。

## A75

承 A72。对 05 这个判断，正确答案是"**那个问题今天还在，只是被换了个容器**"。

第二层，所以 A72 那句"该删"要收窄：

- 05 当初要解决的问题是"能力/技能的定义权归谁"。这个问题今天没有消失——只是 06 在事实上承担了它。
- 所以这不是"问题不存在了所以可以删"，而是"**两份 authority 重叠了，该并成一个**"。这是两种完全不同的删除理由，我不混。
- 我前面如果让你听成"问题消失了"，我在这里纠正。

- `事实层`: Current · Target
- `证据`: `docs/architecture/architecture-views.md`（B2 authority matrix）
- `边界`: "当年为什么要单独设 05"我没找到记录；所以我也不 claim 它当年是多余的。

## A76

压成五个我会这么并：01+02 → 产品与法律事实；03 不动；04+05+06 → 运行时与工具；07 不动；08+09 → 治理与证据。

第二层，合并之后会回来的 failure，我具体说两个：

- **04+05+06 合并最大的风险**：把 06 的"effect 属于工具运行时、未知不许降级成失败"这条边界泡软。今天的 `UNKNOWN_EFFECT` 之所以不降级成 `FAILED`，是被 06 拥有的；如果它变成"runtime 的一个状态"，很可能被 runtime 的 retry 语义吸收——那就直接退化成重复副作用。
- **08+09 合并的风险**：审计/授权是 fail-closed 的**拒付**逻辑，而 observability 是**记录**逻辑。合并后很容易出现"先记录再拒"——那正好是负向历史 #205 那个形状（没有 durable proof 也已经 dispatch）。

- `事实层`: Target
- `证据`: `docs/architecture/architecture-views.md`；`src/backend/zuno/capability/tool_runtime/runtime_batch.py:58`；`docs/evidence/implementation-wave-001.md` #205
- `边界`: 这是思想实验，我没有做合并，也没有测量合并后的影响。

## A77

承 A71。我最想点的那一层是 **MCP tool executor adapter**：`MCPLangChainToolAdapter.execute` 就是在 LangChain 的 `binding.ainvoke` 外面包了一层，delta 只有上下文（tenant / workspace / run / step / trace）和幂等 key 加 salt。

第二层，第二个候选是 **checkpoint 桥**：

- Zuno 自己有 `RuntimeGraphCheckpointer`，而 LangGraph 原生 saver 已被 ADR-0005 采纳、并且在 `phase08.py` 里真的接了。所以"checkpoint 这块是自研"这句话有相当一部分是包壳。
- 但我要立刻加上限定：桥里真正自研的部分不是"写 checkpoint"，是"和 Domain 对账"——那部分框架没有。
- 所以这两层的答案都是"包壳 + 一点真 delta"，不是"纯壳"。

- `事实层`: Current
- `证据`: `src/backend/zuno/capability/mcp/mcp_tool_executor_adapter.py:77-156`；`src/backend/zuno/agent/runtime/checkpointer.py:13`；`docs/decisions/0005-official-langgraph-postgres-checkpointer.md`
- `边界`: 我没有做"去掉适配器直接调"的可行性验证。

## A78

只留一个维度，我留 **`project_id`**（运行时是 `workspace_id`，也就是"案件/工作区"）。

第二层，其余三维怎么替代：

- `user_id`：由调用方的授权身份承载——它本来就应该来自 authorization 上下文，而不是 memory 自己的一个字段。
- `thread_id`：会话状态交给运行时/上下文窗口，它管的是"这轮看到什么"，不是"这条记忆属于谁"。
- `agent_id`：今天它被写死成 `"agent_run"`（A22），实际不区分任何东西，所以它是最容易去掉的一维。

第二层补充一句我自己的判断依据：法律场景里最有现实意义的隔离边界是**案件**——"这条记忆会不会串到另一个案子"是真实后果，而"是不是同一个用户"在单用户试点里区分度很低。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/platform/services/memory/layers.py:42`；`src/backend/zuno/agent/runtime/nodes/core.py:485`
- `边界`: 这是压缩抽象的思想实验；`agent_id` 只被写死这一点我是从代码读出来的，但我没有确认过将来它会不会被用起来。

## A79

承 A75。两个结论必须分开挂，它们不对应同一件事：

- **fusion 的阈值层**：**当时该做但做错了。** "graph 把 baseline 挤出去"这个回归是真的、必须止血，所以那一层该有；错的是阈值和分层**没有依据**（A16）。这是实现层错误。
- **05 的独立身份**：更接近"**当时就不该单独存在**"。我讲不出它独有的 authority，而 06 事实上已经在做同一件事。

第二层：

- 这两者对应的架构责任完全不同：前者该修的是"给它补依据"（也就是那份 ablation 协议要做的事）；后者该做的是**合并**，而不是继续给 05 补对象。
- 如果我把这两件事都说成"当时不该做"，我就会把一个真实的 regression 说成自嗨；反过来都说是"做错了"，我就会放过一个重叠的 authority。

- `事实层`: Target · Personal Ownership
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md`；`docs/architecture/architecture-views.md`
- `边界`: 05 那半是判断，不是有记录的结论；A80 会点出我写不出来的那个。

## A80

我逐条给，然后告诉你哪条我写不出来——但先说清：这九个模块不是九个微服务，所以"删除/合并条件"我按**责任域**给。

第二层：

- 01 应用层：合并条件是"产品入口只剩一个"——今天已经不是，所以留。
- 02 法律领域与工作产出：删条件 = 正式业务事实不再需要唯一属主。不成立。
- 03 知识与证据：删条件 = 引用不再需要可追溯。不成立。
- 04 Agent 运行时与控制：删条件 = 计划不再需要版本、晚到结果不再需要拒收（A40 的三条）。
- 05 能力与技能：**合并条件成立**（A72/A79）——并入 06。
- 06 工具运行时与效果：删条件 = 不再有外部副作用。不成立。
- 07 Model Gateway：删条件 = 不再需要 provider 抽象与费用/配额归属（A50 里"provider binding"这部分）。
- 08 安全与治理：删条件 = 不再需要 fail-closed。不成立。
- 09 可观测与评测：**这一条我写不出来。**

第二层，为什么 09 我写不出来：删掉它没有"某个 failure 会回来"，但它也**没有一个独立的运行时行为**——它更像"证据的存放地"。这是我这轮最不舒服的一条：我几乎要给出"因为我们需要证据所以它存在"，而这正好是标准里点名的"Receipt 太多但说不清哪个 failure 需要它"那种气味。所以我把它标成"写不出条件"，而不是硬编一个。

- `事实层`: Target · Unknown
- `证据`: `docs/modules/README.md`；`docs/architecture/architecture-views.md`；`docs/governance/interview-acceptance-standard.md`（§9 简化信号）
- `边界`: 09 的删除条件：**写不出来**。我把它当成一条未举证的复杂度留在桌上，而不是给它编一个退出条件。

## A81

从文档进来到用户能点引用，主干是一个状态链：文件解析状态（`uploaded → queued → parsing → review_pending → parsed → indexing → indexed`）、`ParseJobStatus` 的作业状态、KnowledgeVersion 的版本状态（`BUILDING → READY → ACTIVE → SUPERSEDED`）、以及 `DocumentVersion` 记录，最后是引用血缘。

第二层，谁改谁：

- 解析/索引状态：由 ingestion 的异步运行时推进，`indexing → indexed` 之后 enqueue 索引请求。
- `BUILDING → READY`：由知识服务在"可见的 BM25 与 VECTOR 两个索引都在"之后写。
- `READY → ACTIVE`：由一次 cutover 写，之前的 ACTIVE 变 SUPERSEDED。
- 引用血缘：`commit_citation_lineage` 一次落一行，带 evidence / document_version / source_span_ref / span_text_hash / authorization_ref。

第二层补充，这一点我要主动讲，因为它是这个子系统最不该被隐藏的结构事实：**这里有两条互不连通的"真相"链**。一条是产品侧的 pipeline 表（file status + task status + stage），另一条是严格知识域的版本/snapshot/evidence 链。而"ready"这个词在两条链上**各有一个来源**：一条是我上面讲的 `mark_ready`，另一条是 `knowledge_config` 里**硬编的字符串** `"ready"`。这两者不是一个东西。

- `事实层`: Current
- `证据`: `src/backend/zuno/knowledge/ingestion/async_runtime.py:301`、`:353`、`:458`、`:481`；`src/backend/zuno/agent/contracts.py:47`；`src/backend/zuno/platform/database/knowledge/domain.py:141`、`:314`、`:439`、`:422`、`:602`；`src/backend/zuno/platform/services/pipeline/models.py:1-30`；`src/backend/zuno/api/services/knowledge.py:42-77`
- `边界`: 两条链各自的消费方我没有全部核对；另外从上传到解析之间还有 storage/lease 那一层（ingestion lease 恢复），我这轮没有逐行读。产品侧那条链是不是还在被使用，我也没有确认。

## A82

"Ready"是给**消费方**看的——具体就是 cutover 和检索两处门禁。写权限不在用户手里，在知识服务手里。

第二层：

- 谁能改：只有 `mark_ready`。而它有一条硬前置：可见索引数少于 2 就直接拒（`KnowledgeVersion needs visible BM25 and VECTOR indexes before READY`）。所以"准备好了"不是一个人点一下的状态，是"两个索引都在"这个条件成立。
- 谁消费：cutover 只接受 `READY`/`ACTIVE`；`active_snapshot_id` 只认 ACTIVE；检索侧拿不到 ACTIVE snapshot 会明说 `Knowledge search requires an ACTIVE Knowledge Snapshot`。
- 另有一条同名的、但完全不同的东西：`ProjectReadiness`（图项目侧的 `ready`/`not_ready`）——它在配置层，跟这里的索引 Ready 不是一回事。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/database/knowledge/domain.py:296`、`:308-314`、`:385-389`、`:55`；`src/backend/zuno/api/services/knowledge.py:754`、`:895-902`；`src/backend/zuno/platform/services/graphrag/project/loader.py:22`、`:166`
- `边界`: review_pending 这一档的审阅是谁在什么界面点的，我没有追。

## A83

引用里存的不只是 doc id——它带了可以定位到**字符区间**的东西：`label`、`evidence_id`、`document_id`、`chunk_id`、`block_id`、`source_span`、`trust_label`、`source_uri`、`provenance`。其中 `source_span` 里有 `char_start`/`char_end`、`page`、`bbox`、`section_path` 这些。

第二层，但"点进去"这件事我必须讲清楚，因为它正是这题真正想问的，而且答案不好听：

- **服务端没有"resolve 一个 citation 到原文区间"的接口**——我 grep 过 `api/v1/`，没有 span/citation 解析端点。
- 前端那边也**没有实现**：citation 渲染成一个纯文本 chip，没有 click handler、没有跳转；`apps/web/src` 里 grep 不到任何用 char range 做高亮或滚动的代码。
- 所以准确的说法是：**定位信息在数据模型里有，点击可达性没有实现。** 我不说"客户端高亮"——那是我一开始想当然，是错的。
- 另外定位用的 id 本身也不一定是区间：绑定层存的 `source_span_id` 是一个**身份**，可以是 span id、chunk id、block id，也可以是整个 span dict 的 SHA-256。

- `事实层`: Current
- `证据`: `src/backend/zuno/knowledge/agentic_graphrag.py:434`、`:446`；`src/backend/zuno/knowledge/ingestion/contracts.py:53`、`:295`、`:320-321`；`src/backend/zuno/agent/runtime/synthesis/citation_binding.py:16-28`；`src/backend/zuno/knowledge/provenance.py:238-254`；`apps/web/src/pages/workspace/defaultPage/defaultPage.vue:2701-2709`
- `边界`: 我只确认了 Web 前端这一处渲染是纯 chip；有没有别的客户端（比如法院侧那个简单自研前端）实现了跳转，我没有证据，不 claim。

## A84

**不失效、也不重定向**——这两条路今天都没有实现。旧引用变成"可被检测出过期"，不是"自动跳到新版本"。

第二层，机制是这样：

- 新解析会生成新的 `document_version_id`，文件记录上的 `latest_document_version_id` 指过去。`parent_document_version_id` 这个字段存在，是可选、且没有用于重定向。
- 陈旧是在**校验时**被发现的：校验发现 evidence stale 会给 `evidence_stale`；发现 `candidate.document_version_id != evidence.document_version_id` 会给 `document_version_mismatch`。
- 源被删的那条路更硬：`mark_source_deleted` 会把 evidence 标成 `citation_eligibility='REJECTED'`，并把 lineage 标成 `deleted_or_tainted=true`。
- 版本级的 supersede 是有的，但那是**整个知识空间 cutover** 级别（旧 ACTIVE → SUPERSEDED），不是单个文档级别。

- `事实层`: Current
- `证据`: `src/backend/zuno/knowledge/ingestion/async_runtime.py:483`；`src/backend/zuno/knowledge/provenance.py:16-20`、`:87-92`；`src/backend/zuno/platform/database/knowledge/domain.py:422`、`:669`、`:685`
- `边界`: 文档版本级重定向：**不存在**。我不把它讲成"设计上做了别的选择"，它就是没做。

## A85

**不能**。"检索不到"和"这个信息不存在"是两件事，系统没有把前者当后者。它能给的是覆盖度判断，不是全集证明。

第二层，实际有的东西：

- 覆盖度：`EvidenceCoverageSummary` / `EvidenceFrontier`，带 `uncovered_claim_refs`、`stop_reasons`（`coverage_incomplete` / `strict_citation_missing` / `conflict_unresolved` / `no_evidence`）、`coverage_ratio`。
- 出口是**弃答**：grounded answer 会走 `Abstain: unsupported claims remain` / `Insufficient cited evidence to answer`；corrective 在 `coverage_incomplete` / `no_evidence` 时给 ABSTAIN；终结 gate 也能落 ABSTAIN。
- 检索侧还有 `citation_coverage = cited_document_count / len(chunk_ids)` 这类比。

- `事实层`: Current
- `证据`: `src/backend/zuno/knowledge/agentic/contracts.py:116`、`:127`；`src/backend/zuno/knowledge/agentic/evidence_ledger.py:45`、`:59-74`；`src/backend/zuno/agent/runtime/synthesis/grounded_answer.py:87-88`；`src/backend/zuno/knowledge/agentic/corrective.py:26-31`；`src/backend/zuno/agent/application/finalization/service.py:100-101`
- `边界`: "全案没有这个信息"作为**肯定性结论**：系统不产出这个结论。这是设计上的克制，不是能力的缺失——但我也不能证明它永远不会被讲成否定结论。

## A86

**没有权重。** 三路融合不是加权求和——Vector 和 BM25 只贡献名次（`vector_rank` / `bm25_rank`），图贡献 tier 和 signal，最终顺序是一个**字典序 tuple**。

第二层，所以"固定常量还是随 query 变"这个二选一的答案都不是：

- 固定的部分是**优先级顺序**：先 candidate_group，再 baseline_rank，再 chain_score、graph_tier、graph_signal，最后才是本地分。
- "随 query 变"的部分是策略名 `query_aware`，以及一组按 query 类型触发的 guardrail（comparison / bridge / genealogy）。
- 我要主动纠两个可能的误读：一是 metadata 里那个 `fusion_score` 是算术和、看起来"像权重融合"，但**它不是排序键**；二是**这个项目里有第二套融合实现**——agentic 那条路上是一个真正的 RRF，`rrf_score += 1.0/(60.0 + rank)`，k=60 是**硬编**的。所以"三路融合"这件事在仓库里有两份答案，别把它们当成一套。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/retrieval/fusion.py:952-977`、`:992-1021`、`:1065`；`src/backend/zuno/platform/services/retrieval/planner.py:268`；`src/backend/zuno/knowledge/agentic_graphrag.py:876`、`:1409-1419`
- `边界`: `alpha` / `bm25_weight` / 可调 `weight` 我确实没找到；但 `rrf_k=60` 是存在的（硬编，没有依据可追）。A94 会纠正我这题里可能说过头的地方。

## A87

承 A86。被挤出的那条图候选，它的证据强度**不会转移，也不会回流**——它就是随着候选一起出局。分数去哪了：哪也不去，它只存在于那条候选自己的 metadata 里，换不来别的候选的位置。

第二层，真正在设计上被保护的不是"图候选的分数"，而是**baseline 的槽位**：

- guardrail 生效时做的动作是"替换位置"，而且挑的是**最弱的 baseline 槽位**，也就是把晋升放进一个还能被反超的位置，而不是插队首。
- 淘汰某个候选时还有一个 penalty 逻辑在算"该拿掉哪一条"。
- 所以这套融合的本质是"分层 + 保位"，不是"加权拼接"。这也是它为什么被命名为 `baseline_preserving`，而不是 `score_fusion`。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/services/retrieval/fusion.py:743-744`、`:912-923`、`:952-977`、`:1065`
- `边界`: 我给不出"被挤出候选的信号有多强"这种量化——那需要对每个 case 跑一遍看 metadata，我没做。

## A88

分两种：**能对齐的**和**会被硬切的**。

第二层，具体怎么切：

- 切分用的是句子正则（按 `. ! ?` 断句），所以正常情况下引用单元的边界是句子。
- 但超长句会被一个字符窗口硬切（`_split_long_unit`），citation chunk 上限 240 字符。**也就是说，切在句子中间是真会发生的。**
- 兜底有两个：一是引用块本身携带最多 1200 字符的 `parent_context`；二是相邻关系靠 `neighbor_chunk_ids` / `parent_chunk_id` 记录。
- 没有的是：文本重叠窗口（没有 overlap），以及检索时的自动邻接扩展。

- `事实层`: Current
- `证据`: `src/backend/zuno/knowledge/ingestion/router.py:15`、`:16`、`:566-570`、`:583`、`:512-516`、`:541`
- `边界`: 声明里还有一份"boundary_priority"列表（section/paragraph/sentence/table_cell/code_block/character），但实际实现的只有 sentence + character 两种——声明比实现宽，这一点我要说明。

## A89

承 A84、A85。我在这里要做一个明确的自我纠正：**如果我在 A84 里让你听成"旧引用仍然可用"，那是错的**。A84 的准确表述是"旧引用不重定向、但会被**检测为 stale 或 document_version_mismatch**"；源被删时更硬，会被标成 `citation_eligibility='REJECTED'`、`deleted_or_tainted=true`。

第二层，所以你这个问题我今天只能这样回答：

- 引用指向的那段被删掉之后，**"旧引用仍可用"不成立**——它会被标成不可用。
- 而 A85 那套"覆盖度不足就弃答"，在这条路径上恰好是同向的：先是引用被标掉，再是缺引用导致 coverage 不完整、走 abstain。
- 两条线不冲突，但它们的**连接点**是"引用失效 → coverage 不足"，不是"引用失效 → 结论自动回滚"。下游结论要不要回滚，A26 已经答过：没有自动失效传播。

- `事实层`: Current · Evidence
- `证据`: `src/backend/zuno/knowledge/provenance.py:87-92`；`src/backend/zuno/platform/database/knowledge/domain.py:669`、`:685`；`src/backend/zuno/knowledge/agentic/evidence_ledger.py:59-66`
- `边界`: "引用失效之后已有结论是否被重新判定"——我只能指出 coverage 这条链会缺证据，不能指出有一个回滚机制。

## A90

承 A81。我觉得可以删的是**引用结构的重复定义**：同一个引用在今天有三套形状——服务端的 `Citation`、DTO 层的 `WorkspaceCitationRef`、以及契约层的 `CitationContract`。

第二层，删掉会变得不可判定的是什么，我说具体：

- 删掉 DTO/契约那两套、只留一套，本来应该是好事；但**删的顺序**错了就会丢 `source_span` 的传递。
- 而 A83 已经说清了：点击可达性今天**根本没实现**。所以"删掉会变得不可判定"这个说法要收窄——它今天不是"会不会坏"，而是"**会让一件还没做的事再也做不成**"：span 一旦不出现在对外 payload 里，前端就永远拿不到字符区间。
- 另一层更微妙：绑定层存的是 `source_span_id` 这个**身份**，可能是 hash；如果把它当成偏移量来用，那"点进去落到哪一段"其实是**不可判定**的——id 相等不蕴含位置相等。

- `事实层`: Current · Target
- `证据`: `src/backend/zuno/knowledge/agentic_graphrag.py:434`；`src/backend/zuno/api/dto/workspace.py:256`、`:299`；`src/backend/zuno/agent/runtime/synthesis/citation_binding.py:16-28`；`src/backend/zuno/knowledge/provenance.py:238-254`
- `边界`: 我没有验证这三套结构是否真的有语义差异（也可能只有命名差异）；如果只是命名差异，那"删哪一套"就退化成一次重构偏好，而不是一个状态对象的存废。

## A91

因为 `requests` 这类网络调用在等 socket 的时候会**释放 GIL**，所以多个线程能真正重叠在 I/O 等待上；线程在这段时间不是"占着解释器"的。而 CPU 密集型任务从头到尾都要持有 GIL，线程只能轮流跑，还要额外付上下文切换的成本，所以基本不加速，甚至更慢。

第二层：

- 严格说，GIL 的释放是按字节码间隔和阻塞调用发生的；`requests` 的 socket 读写属于后者。
- 所以"用线程做 I/O 并行"成立的前提是**等待占主导**；一旦其中掺了 CPU 重的解析或序列化，收益就被吃掉。

- `事实层`: Current
- `证据`: 无
- `边界`: 我没有做过这个项目上的线程 vs 协程实测；上面是机制层面的回答。

## A92

**不会丢更新**——对这个具体的语句而言不会。`UPDATE t SET c = c + 1 WHERE id = 1` 里的 `c + 1` 是在**数据库内部**读的，PostgreSQL 在 READ COMMITTED 下遇到并发写会用更新后的行版本重新求值，所以两个事务串起来算，`c` 会加 2。

第二层，真正会丢更新的形状是另外两种：

- **读在客户端**：先 `SELECT c` 出来、应用里加 1、再 `UPDATE t SET c = ?`。这个丢更新 READ COMMITTED 挡不住，因为决定值的那次读和执行不在同一个语句里。
- **把隔离级别提到 REPEATABLE READ**：那时不是丢更新，而是第二个事务拿到序列化失败（first-updater-wins），要么重试要么报错——这是另一个失败模式。
- 所以这题的要点是：**丢更新不是"READ COMMITTED 的默认结果"，它是"读-改-写被拆到语句之外"的结果。**

- `事实层`: Current
- `证据`: 无
- `边界`: 我讲的是 PostgreSQL 的行为；我没有在本项目里构造过这个并发测试。

## A93

**不能断定。** 超时只说明"我没收到响应"，不说明"远端没做"。一个很常见的情况：请求已经到达并被处理完了，响应在回程丢了——连接被中间设备切断、或者服务端处理完之后进程/网络出了问题。

第二层：

- 这类"已执行、响应丢失"正是项目里 `UNKNOWN_EFFECT` 存在的原因；系统对它的处理是不降级、不重试，转对账（A9）。
- 另一种不能断定的情况更直白：超时发生在**连上之前 vs 请求发出之后**，语义完全不同；如果超时在连接建立阶段，那倒更接近"没发出去"，但仅凭超时这个事件本身，你分不清是哪一种。

- `事实层`: Current
- `证据`: `src/backend/zuno/capability/tool_runtime/runtime_batch.py:58`；`src/backend/zuno/capability/tool_runtime/invocation_gateway.py:536-587`
- `边界`: 我没有在真机上抓过"已处理但响应丢失"的实例。

## A94

承 A86。先纠正我自己的前提：**我在 A86 里说"三路并行、超时就返回"是错的。** 代码里检索是**顺序 await** 的（vector → requery → bm25 → graph），`retrieval/` 里既没有 `asyncio.gather` 也没有超时取消。所以这题的场景在本项目里不存在。

第二层，但语义问题本身要答清楚，因为它是个真陷阱：

- 即使真的用了 `gather` + 超时，被取消的也只是**本地 coroutine**——取消在下一个 await 点抛 `CancelledError`。
- 远端那次 HTTP 请求**不会因此停下**：连接断开与否取决于协议层，服务端可能已经把请求读进去、甚至处理完了。这和 A93 是同一件事的两种表现。
- 所以"取消 = 终止"是不成立的；取消只保证"我不再等结果"，不保证"对方不再做"。

- `事实层`: Current · Personal Ownership（纠正）
- `证据`: `src/backend/zuno/platform/services/retrieval/orchestrator.py:614-689`
- `边界`: 我没有验证过别的子系统（比如知识 ingestion）有没有用 `gather`；我只确认了检索这一条路没有。

## A95

`asyncio.create_task`：**读得到**。任务创建时会**拷贝当前 context**，所以在创建之前 set 的值会带进任务里；反过来，任务里改的 ContextVar 不会影响创建者的 context。

`run_in_executor`（以及 `to_thread`）：**读不到**。它在线程池里跑，普通函数不会继承调用方的 context；要靠 `contextvars.copy_context()` 显式传，或者干脆当参数传进去。

第二层，承 A54 必须加一句：

- 在这个项目里，per-user MCP 配置**根本不在 ContextVar 里**——它是显式实参加"一会话一实例"（A5）。项目里那个 `user_id` ContextVar 只服务可观测性。
- 所以这题对本项目而言的正确回答是：**如果当初用 ContextVar 存它，在 `create_task` 里是安全的、在 `run_in_executor` 里会丢**；而我们当时选的是显式传递，正好绕开了这个坑——这是设计选择的结果，不是我们提前想到了这个语义。

- `事实层`: Current
- `证据`: `src/backend/zuno/platform/common/contexts.py:7`、`:21-28`；`src/backend/zuno/platform/services/workspace/simple_agent.py:160-176`
- `边界`: 我没有写过一个"故意在 executor 里读 ContextVar 看它丢"的验证测试。

## A96

承 A93。最坏的事态是**重复写**：远端执行了两次，而我们只记了一次——账是平的，现实是重复的。这在法律场景里可能是重复发送通知、重复提交这类有外部后果的事。

第二层，靠什么让它安全：

- **幂等键**：调用前抢 `claim_idempotency_receipt`，scope 是 `tool-side-effect`，key 里带 `prepared_action_hash` 和 `target_resource_set_ref`；已经完成过就返回既有 receipt，不再打网络。
- **只有确定没执行才允许重发**：`retry_same_effect_allowed` 只在结论是 `CONFIRMED_NOT_EXECUTED` 时为真。
- **未知不重试**：转 reconciliation。
- 我要主动说这条链的弱点：幂等位有 **60 秒 TTL**（A7），TTL 之外的重试靠的是对账结论，而对账的远端查询今天**没有实现**（A47）。所以"安全"是有条件的。

- `事实层`: Current · Evidence
- `证据`: `src/backend/zuno/capability/tool_runtime/invocation_gateway.py:1290-1317`；`src/backend/zuno/capability/tool_runtime/runtime_batch.py:460`；`tests/agent/runtime/test_runtime_tool_idempotency.py:20`
- `边界`: 幂等键的 TTL 之外、远端对账缺失这两点叠加的那个窗口，我只有"它被设计成靠对账收口"这句话，没有测试覆盖它。

## A97

意味着**取消不会进入你的 `except Exception` 分支**。`CancelledError` 在 3.8+ 继承自 `BaseException`，`except Exception` 抓不到它，所以你放在那里的清理逻辑在协程被取消时**不会执行**。

第二层，正确的写法：

- 清理放 `try/finally`，它两条路都走。
- 如果确实要拦 `CancelledError`，必须**再抛出去**——吞掉它会破坏取消语义，让对方以为任务正常结束了。
- 反过来，`except Exception` 的语义也因此更干净：它抓的是"真错误"，不抓控制流。

- `事实层`: Current
- `证据`: 无
- `边界`: 我没有在本项目里专门审查过取消安全的清理路径；这是通用语义的回答。

## A98

我按 `(user_id, project_id, created_at DESC)` 定——**等值列在前，排序列在后**，而且 DESC 要写进索引，才能让 `ORDER BY created_at DESC LIMIT 20` 直接吃索引顺序。

第二层，反过来会变差的原因是最左前缀：

- 如果索引是 `(created_at, user_id, project_id)`，那按 `created_at` 的范围/排序变成第一列，后面两个等值列**用不上前缀定位**——索引要么退化成"先扫时间再过滤"，要么直接被放弃。
- 更准确一点：等值列放前面是为了把搜索空间先切到"这个用户的这个项目"，再在这个小集合里按时间取前 20；反过来就是先给全表排序，再逐行过滤。
- 还要注意，如果查询里出现范围条件，范围列之后的列就失去定位能力——所以我不会把范围列放中间。

- `事实层`: Current
- `证据`: 无
- `边界`: 我没有在本项目里对这个具体查询做过 `EXPLAIN` 对比；上面是索引设计的一般原理应用。

## A99

承 A92、A95。能产生丢失更新的时序：A、B 两个回合几乎同时开始，都在**同一份记忆基线**上工作——A 读到版本 N，B 也读到版本 N；A 先写成 N+1 提交，B 再写成"基于 N 的结果"提交。如果写入是"覆盖式写"，B 就静默覆盖了 A 的更新，而且没有任何一方报错。

第二层，为什么 READ COMMITTED 挡不住：

- READ COMMITTED 保证的是"每条语句看到的是语句开始前已提交的数据"。它**不**保证"你读的那个版本到写的时候没变过"——A 和 B 的读发生在各自语句里，都合法。
- 真正挡它的是**乐观并发控制**：写入时带版本 CAS。项目里 memory 侧确实有这一层——版本状态机带 `aggregate_version`、激活是 CAS；domain 侧也有 stale 冲突。
- 所以准确说法是：**READ COMMITTED 不够，是版本 CAS 在兜底**。这句话我必须说，因为它同时界定了我个人的贡献边界——`prepare_context` 读取和 readback 收紧是我做的，CAS 在 domain/memory 版本层，不是我这笔。

- `事实层`: Current · Personal Ownership
- `证据`: `src/backend/zuno/platform/database/memory/domain.py:301`；`src/backend/zuno/agent/domain/task_contracts.py:345`；`src/backend/zuno/memory/governed_runtime.py:30`
- `边界`: 我没有构造过多回合并发写入的对抗测试；"CAS 能兜住"是从代码结构判断的，我没有见过它被压住的实测。

## A100

会被算成**两个不同的错误**，而且它们**代价完全不对称**。

第二层，哪个方向对我更致命：

- "该 direct 却走了 ReAct"：多花几步、多花 token、可能慢，但**还是靠工具选择在选工具**——结果大概对，代价是效率。
- "该 ReAct 却走了 direct"：**参数是正则钉死的**（A8），直接跳过了工具再选择这一步。它可能拿错参数、调错工具，而且如果这个工具带副作用，后果不是"答得慢"，是"做错事"。所以**这个方向致命**。
- 因此如果只能优化一个方向，我会把 direct route 的**准入条件收紧**，宁可多回落到 ReAct。

第二层，承 A53 我必须承认的一件事：**今天的回归集并没有真正固定住这条边界。** 有 direct route 的断言（非显式 MCP query 走 `tool.maps_weather`、city 抽成"南京"），但**没有任何一条断言"这类 query 应该回落到 ReAct"**——`src` 里也找不到 `falls back to ReAct` / `direct_route` 这样的字面量。所以我在 Q53 说的"用回归测试固定路由边界"，严格讲只固定了一半。

- `事实层`: Current · Personal Ownership · Unknown
- `证据`: `tests/agent/test_workspace_simple_agent.py:16`、`:129`、`:54`；`src/backend/zuno/platform/services/workspace/simple_agent.py:2159-2188`
- `边界`: ReAct 回落侧的回归断言：**不存在**。这是我这条 bullet 上最需要被修的缺口——它不只是"答得不全"，它是"简历的措辞强于测试"。
