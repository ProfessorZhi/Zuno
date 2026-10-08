# Blue Wave 1 — Candidate Answers A1–A100

```text
round: rb-2026-10-08-formal-021
role: Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师
answers_to: 02_red_questions.md @ <HEAD_AT_COMMIT>
register: 第一层 20–60 秒口语，其后可展开
provenance: >
  A1–A50 与 A51–A100 由两次同规格的 Blue 执行分别生成（同一 Skill、同一 register、同一 Ownership 规则），
  A51–A100 的生成方可读取 A1–A50 成品以保持口径一致。本文件为顺序拼接，未统一措辞。
```

## A1

这次重构里我亲手改的是 4 月 15 日那个提交，核心动作是把「MCP Server 被整体包成一个 Tool」这层拆掉——删掉了独立的 `mcp_agent.py` 和 `skill_agent.py`，把真实的 MCP tools 直接绑到同一个 `GeneralAgent` 上，同时把用户级配置注入从子 Agent 挪回主 Agent 的 tool-call middleware，按 tool 名映射回 server id 再取配置。重构之前那块长什么样，我能从父提交看到：`GeneralAgent` 自己带 `tool_invocation_model`、`available_tools` 状态和 `LLMToolSelectorMiddleware`，每个 MCP server 走 `MCPAgent` 再包一层 tool，skill 走 `SkillAgent`。「之前是谁写的」我没法回答——这个仓库的 commit 作者字段区分不出我和团队，我只能说这段 before 代码是父提交里已经存在的，属于我当时接手的现状。

第二层：

- before：`StreamAgentState` 带 `available_tools`，模块常量 `MAX_TOOLS_SIZE = 10`；`__init__` 持 `self.tool_invocation_model`、`self.mcp_agent_as_tools`、`self.skill_agent_as_tools`；`setup_agent_middleware()` 构造 `LLMToolSelectorMiddleware(model=self.tool_invocation_model, max_tools=3)`；`setup_search_tool()` 定义 `search_available_tools` 返回 `Command(update={"available_tools": ...})`（延后选工具脚手架）。
- after：单个 `create_agent(tools=self.tools + self.mcp_tools + self.skill_tools)`；`setup_mcp_tools()` 用 `MCPManager(...).get_mcp_tools()` 直接绑定并维护 `self.mcp_tool_server_map[tool_name] = mcp_server_id`；skill 退化为 `load_skill_context(query)` 的 guidance-only tool；`tool_invocation_model` / `available_tools` / `LLMToolSelectorMiddleware` / `search_available_tools` 全部移除。
- 该提交删除 `core/agents/mcp_agent.py`（−120）与 `core/agents/skill_agent.py`（−263），`general_agent.py` 大幅改写。

- `事实层`: Historical / Personal Ownership（受作者字段限制，见下）
- `证据`: commit `773467580ee428a0536c7f594c0847c1510879ac`；`docs/governance/project-fact-provenance.md` PF-012 / PF-032 与「Tool Calling Strategy 取证边界」段
- `边界`: 该 SHA 由我的账号 authored，但仓库口径明确「作者字段区分不出个人与团队」，所以我只说「这是我能自证的一笔」，不说「整块是我独立拥有」；「重构前是谁写的」保持 Unknown。

## A2

重构前是两层 Agent 加一层 tool 边界：主 Agent 里看到的是「某个 MCP server」这一个 tool，选中之后进入 `MCPAgent`，`MCPAgent` 内部自己再跑一次 ReAct 去选这个 server 里具体哪个 tool，然后通过它的 tool-call wrapper 注入用户配置，最后才真正发 MCP 调用。也就是说一次用户请求可能穿过两个模型循环：外层选 server，内层选 tool。

第二层：

- `MCPAgent`（已删除）持有 `MCPConfig(BaseModel)`：`server_name / mcp_server_id / url / type / tools / …`；`setup_agent_middlewares()` 用 `@wrap_tool_call add_tool_call_args`，内部 `mcp_config = await MCPUserConfigService.get_mcp_user_config(self.user_id, self.mcp_config.mcp_server_id)` 后 `request.tool_call["args"].update(mcp_config)`；内层是独立的 `create_agent(system_prompt=CALL_END_PROMPT)`。
- `SkillAgent`（已删除）同样自带一个 agent，暴露 `get_file_content` / `list_skill_files`。
- 所以「配置跨层传递」和「身份跨层传递」都在第二层发生，第一层只传一个 server 级 tool。

- `事实层`: Historical
- `证据`: `77346758` 的父版本 `mcp_agent.py` / `skill_agent.py`
- `边界`: 这是对已删除代码的复述，不是我今天在跑的路径；当前 `EmitEventAgentMiddleware` 已退役，路径换成了 `WorkSpaceSimpleAgent._execute_binding_tool` → 模块级 `execute_binding_tool` → `ToolInvocationGateway`。

## A3

老实说，我没有一个可复核的现场 bad case 记录来说明当时的表现形态——是报错、静默丢配置还是把 A 的配置给了 B，我拿不出证据。我能证明的只有结构问题本身：配置注入点被放在嵌套的子 Agent 里，所以 `user_id` 和 server id 必须跨层带下去，注入点离真正的 dispatch 隔了一层模型循环。重构把注入点移回主 Agent 的 tool-call middleware 之后，这个跨层依赖就消失了。所以这条我只能给到「有结构证据、无现场记录」。

第二层：

- 原来的注入点：`MCPAgent` 内部的 `add_tool_call_args`（子 Agent 层）。
- 现在（4 月那版）：`EmitEventAgentMiddleware.awrap_tool_call`，`if self.mcp_checker(tool_name): mcp_server_id = self.mcp_id_resolver(tool_name)` 后取配置并 `request.tool_call["args"].update(mcp_config)`。
- 现在（当日 main）：`execute_binding_tool` 在调用点算 `mcp_config = await mcp_user_config_resolver(user_id, mcp_tool_id_resolver(binding.name))` 再 `call_args.update(mcp_config)`。

- `事实层`: Historical / Current（机制）
- `证据`: 上述两处注入代码；`docs/governance/project-fact-provenance.md` PF-032 明确「已恢复客户 / 法院事故」这一项**没有**证据
- `边界`: 具体 bad case 表现 = Unknown；不能为了答案好看编一个「串用户」的故事。

## A4

注入发生在**真正发起调用之前的那一刻**，不是构造 tool schema 的时候。schema 是静态的，用户配置是每次调用现取的：按 tool 名映射回它属于哪个 MCP server，再拿这个 `user_id` 去取该 server 的配置，合并进「这一次调用」的参数里，然后才 dispatch。

第二层：

- 4 月那版：`EmitEventAgentMiddleware.awrap_tool_call` 里 `request.tool_call["args"].update(mcp_config)`，紧贴 tool 执行。
- 当日 main：模块级 `execute_binding_tool`（`src/backend/zuno/platform/services/workspace/simple_agent.py:160`）在 189–201 行做注入，之后如果 adapter registry 没绑就 `raise MCPToolAdapterNotBound(...)`（:206）fail closed，早于任何 `binding.ainvoke`。
- 只有 `mcp_requires_user_config(binding.name)` 为真的 tool 才取配置；platform-ready 的 MCP（server 没有 config）不取。

- `事实层`: Historical / Current
- `证据`: `simple_agent.py:189-201`、`:206`、`:2928`（`mcp_requires_user_config`）；测试 `tests/agent/test_workspace_simple_agent.py:165` `test_mcp_without_user_config_is_treated_as_platform_ready`
- `边界`: 注入的是「该用户在该 server 上的配置」，不是工具定义本身；schema 层不因用户而变。

## A5

不会串。原因是配置不是挂在 server 对象或某个进程级变量上的，而是每次调用按 `user_id` 现取、合并进**这一次调用自己的参数字典**里。两个并发请求各自持有自己的 call args，没有共享可变状态，所以不需要「全局 dict 加锁」这种方案，也不需要靠锁去保证隔离。

第二层：

- 隔离单位是单次调用，不是 server：同一 server 同一 tool 的两个用户，各自解析到各自的配置副本。
- 注入点在 `execute_binding_tool` 内部，`call_args` 是本次调用的局部对象。
- 没有把 user config 写进任何模块级 / 类级缓存字段。

- `事实层`: Current
- `证据`: `simple_agent.py:189-201`；对比父版本 `MCPAgent` 也是同样的「每次现取再 update 到本次 args」，只是位置在子 Agent
- `边界`: 我说的是「配置不串」；这不等于「并发的远端调用本身是安全的」——那是 06 的 effect/idempotency 问题，另算。

## A6

如果配置真的放在进程共享变量里，Python 里正确的绑定方式是 `ContextVar`：它按协程/任务上下文传播，`asyncio` 里每个请求一条链路各自看到自己的值，不用全局锁，也不会因为 `await` 切走而串。不过要说清楚——**这条路径今天没有用 ContextVar**。MCP 用户配置是靠显式把 `user_id` 作为参数传到调用点、再当场去取的，这比 ContextVar 更直接，也没有上下文泄漏风险。

第二层：

- Platform 里确实有 ContextVar（`src/backend/zuno/platform/common/contexts.py:5-8`：`trace_id`、`unique_id`、`user_id`、`agent_name`），但那是 tracing 用的，MCP 配置不走它。
- 选显式参数而不是 ContextVar 的理由：注入点就在一个明确知道 `user_id` 的函数里，隐式上下文反而增加「哪来的值」的调试成本。
- 如果未来改成在中间件层统一注入，而没有显式参数可带，`ContextVar` 会是首选而不是全局 dict。

- `事实层`: Fundamental / Current
- `证据`: `platform/common/contexts.py`；`execute_binding_tool` 的显式 `user_id` 传参
- `边界`: 这是「今天的实现选择 + 如果重做我会怎么选」，不是「我当时做了 ContextVar 改造」。

## A7

因为包装本身才是问题，不是透传没修好。把一整个 MCP server 包成一个 tool 之后，主 Agent 看不到 server 内部具体的工具 schema，它只能选到一个不透明的「某 server」，然后进第二个模型的 ReAct 循环去选真正要调的工具。这带来三个代价：工具选择质量下降（模型在看不见 schema 的情况下选）、一次请求变成两次模型往返、身份和配置必须跨层维护。删掉这层比修它的透传更简单，也更少状态——所以选择是减法而不是补一条更长的透传链。

第二层：

- 最简方案：主 Agent 直接绑定具体 MCP tools，注入点跟着 tool 走。
- 为什么之前的方案不够：嵌套 Agent 让「工具选择」这件事分散在两个模型循环里，且 wrapper tool 的 schema 粒度丢失。
- 我改的机制：删除 `MCPAgent` / `SkillAgent` 包装，绑定真实 tools，配置注入落在主 Agent 的 tool-call middleware。
- 验证：`tool_invocation_model` / `available_tools` / selector 脚手架在同一提交里消失，且新增的 direct-route 测试锁住了「不显式点名 MCP 的 query 也能直接路由」。

- `事实层`: Historical / Personal Ownership
- `证据`: commit `77346758`；`tests/agent/test_workspace_simple_agent.py:16`
- `边界`: 这是 4 月那次重构的判断；今天 Runtime 又演进成 Single Controller + governed binding，不能说「当时的抽象今天还是唯一正确形态」。

## A8

今天的判据是**规则**，不是模型。规则层做两件事：一是 `_detect_route_hint` 用正则（slash command）加关键词表（飞书/高德/必应/知识库/skill/终端）判断意图；二是 `_plan_kind_for` 用 token match 决定 `simple` 还是 `complex`。如果 `complex`，Runtime 需要一个注入的 DAG planner，而产品组合里这个是 `None`，所以复杂请求今天会 fail closed，而不是真的进模型规划。这点我如实说，因为「复杂请求进 ReAct」更像历史/设计描述，不是今天产品路径的现状。

第二层：

- `_detect_route_hint` — `simple_agent.py:2743`（正则 + 关键词）。
- `_resolve_governed_tool` — `:2159`（解析具名 tool / MCP route tool / `/skill` / 图片重生成 → 单个 `(tool_id, args)`）。
- `_plan_kind_for` — `:2150`：命中 `("compare","across","conflict","multi-hop","multihop","analyze","synthesize","报告")` 返回 `complex`，否则 `simple`。
- `plan_kind == "complex"` 要求 `dynamic_dag_planner`，缺失时 `single_controller_runtime.py:497-501` 抛 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND`；产品组合 `src/backend/zuno/main.py:113` 装的是 `None`。
- Runtime 里的「ReAct step」（`agent/runtime/execution/react_runner.py:20-67`）是**一个 step 内**的一次模型调用，它不直接给模型绑工具。

- `事实层`: Current / Historical
- `证据`: `simple_agent.py:2150/2159/2743`；`single_controller_runtime.py:497-501`；`main.py:113`
- `边界`: 「用规则还是模型」的答案是「规则，模型侧未接线」；我不把它包装成「规则+模型混合」。

## A9

那条断言固定的是 `_canonical_mcp_target` 的**收敛性**。父版本的逻辑是：如果规范化后的 query 落在 server 名里、或者 server 名落在 query 里，就再去递归调一次 `self._canonical_mcp_target(server_name)`。当规范化后的 query 恰好**等于**规范化后的 server 名时，这个递归永远不收敛，直接 `RecursionError`。断言写的是 `agent._canonical_mcp_target("qa-mcp-461126") == "qa-mcp-461126"`，也就是「自定义 MCP 名要原地返回规范化名，不许再递归」。不写它最容易漏的回归就是：任何自定义命名的 MCP server，只要它的名字和用户的规范化输入撞上，就会炸栈。

第二层：

- 修复：命中分支直接 `return server_norm`，并留注释解释为什么不能再递归。
- 同批新增的相关断言：`_extract_gaode_weather_city()` 的城市抽取、platform-ready MCP 无需用户配置、direct structured result 的最终呈现。

- `事实层`: Historical / Current
- `证据`: `0b5fb35039711ab0b63dad6528df5e4705fbc93d`；`tests/agent/test_workspace_simple_agent.py:54`
- `边界`: 这是**代码前后差异可复现**的实现缺陷，仓库口径明确：没有证据说明它曾在法院/Pilot/Production 形成真实事故。

## A10

ReAct 一侧暂时没有回归断言，是因为它不好写：direct route 是确定性映射（规则进、tool+args 出），可以直接冻结；ReAct 走模型，要把它固定住，需要一个可复现的假模型 + 冻结的调用轨迹 fixture，而这套 harness 我没有建。补它的代价就是维护一个确定性模型替身，外加防止 fixture 随 prompt 漂移。至于什么时候补——我没有承诺过日期，诚实的说法是：先有可复现的假模型 harness，才谈得上补断言。

第二层：

- direct route 侧已有的断言（可锁定准入与参数抽取边界）：`test_astream_direct_routes_non_explicit_mcp_query`、`test_classify_mcp_route_tool_extracts_clean_weather_city`、`test_canonical_mcp_target_handles_custom_server_name_without_recursion`、`test_mcp_without_user_config_is_treated_as_platform_ready`。
- ReAct 侧：没有对应文件，也没有 CI 断言。
- 简历里我写的是「ReAct 一侧暂无回归断言」，这句话我维持。

- `事实层`: Current / 证据缺口
- `证据`: 简历原文；`tests/agent/test_workspace_simple_agent.py` 文件范围
- `边界`: 这是一个我知道并承认的缺口，不给排期承诺，也不说「已在计划中」。

## A11

只看客户端，我判断不出来。timeout 只说明本地没拿到确定响应，远端可能没执行，也可能已经成功。工程上的做法是先把「到底有没有发出去」变成一个耐久事实：调用前先落明确的动作身份和一次 Attempt，Attempt 记录 dispatch 阶段——是 `KNOWN_NOT_SENT`，还是 `REQUEST_SENT` 之后才 `TIMED_OUT` / `CONNECTION_LOST`。只要越过了 send boundary，结果就是 UNKNOWN，绝不映射成普通 Failed，也绝不盲重试。

第二层：

- Attempt 状态族：`CREATED → DISPATCHING → REQUEST_SENT / KNOWN_NOT_SENT`，`REQUEST_SENT → RESPONSE_RECEIVED / TIMED_OUT / CONNECTION_LOST`（`docs/modules/effects/reference.md` B7）。
- 只有 `KNOWN_NOT_SENT`（可证明没发出去）才允许有界重试；`REQUEST_SENT` 之后一律走 Reconcile。
- 参考实现次序：TX1 先持久化 PreparedAction / idempotency + durable Attempt intent，COMMIT 后才真正发外部调用。

- `事实层`: Target / Fundamental（timeout 语义）
- `证据`: `docs/modules/effects/reference.md` B7 / B11 / B14.5–B14.6
- `边界`: 这是 06 的 Target 语义；「消除网络栈与持久化之间所有不可观测纳秒窗口」是不承诺的，恢复依赖远端幂等 / correlation / 对账。

## A12

收敛幂等靠的是**动作身份**，不是靠「重试次数」：`idempotency key` 的作用域是 tenant + tool operation（当前实现里是 `tool-side-effect` 命名空间），再配上由规范化后的非敏感参数算出的 canonical action hash。规则只有两条：same key + same action hash → 返回既有 action/effect，或继续它原来的对账；same key + **不同** action hash → 直接 conflict fail closed，不允许偷偷新建第二个逻辑动作。这样重试同一个逻辑意图只会命中同一条记录。

第二层：

- 当前 MCP 路径的 key：`idem:{tenant_id}:{workspace_id}:{run_id}:{step_run_id}:{tool_name}:{salt}`，作为 `call_id` 传进 Gateway（`mcp_tool_executor_adapter.py:70-74`, `:135`）。
- Gateway 侧：`claim_idempotency_receipt(...)`；completed claim 直接返回 `result_ref`；`in_progress` 且同 owner 就先 reconcile 再返回既有 `result_ref`；否则 `idempotency claim is already held or completed`。
- action hash 由 `redact_sensitive_payload(args)` 后规范化计算；Secret 值不进 hash payload。

- `事实层`: Current（本地幂等）/ Target（远端幂等）
- `证据`: `invocation_gateway.py:1290-1332`、`:304-323`；`docs/modules/effects/reference.md` B14.4
- `边界`: 我只能保证本地不会为同一 key+hash 造第二个逻辑动作；**远端**去重要看 Provider 是否真幂等，那需要按 ToolVersion 资格化，今天没有真实 Provider 证据。仓库口径也明确「不宣称 exactly-once」。

## A13

远端现实是真值。本地状态只是「我们目前能证明什么」，证明不了就得承认不知道。所以本地超时但远端其实成功时，正确状态是 `UNKNOWN_EFFECT` + 一条 `OPEN` 对账记录，收敛责任在 06，不在 Runtime，也不在调用方自己猜。有可信的远端查询/业务键就走查询；没有就转人工一次性结论。今天 provider remote-query 是被 Defer 的，所以实际兜底路径是人工。

第二层：

- 矛盾点：Attempt 是终态（TIMED_OUT），Effect 不是——Attempt terminal state 与 Effect terminal state 不能合并。
- 收敛链（当日）：`UNKNOWN Effect → durable OPEN Reconciliation → replay 仍是 reconciliation_required → 需要时升级 → 授权的一次性人工判断 → 结论性 EffectReceipt`。
- Runtime 只进 `WAITING_RECONCILIATION`（Target 命名），它不从 transport 状态反推答案。

- `事实层`: Target / Current（人工兜底已实现）
- `证据`: `docs/governance/effect-remote-query-reconciliation-status.md` §Decision / §Current；`docs/evidence/README.md`「UNKNOWN EFFECT RESTART REPLAY: FIX VERIFIED / UNKNOWN PRESERVED」
- `边界`: 自动 remote query 目前 `DEFERRED_BY_PROVIDER_CAPABILITY`；说「谁收敛」时我指 06，不说「已经能自动收敛」。

## A14

我的判断是 MCP 传输层本来就该 Buy，不该自研。Zuno 在这段里真正自己写的 delta 不是协议，而是三件框架不会替你决定的事：一是 MCP tools 怎么被**单个受治理 Agent** 暴露（去掉包装层、绑定真实 tools）；二是**按用户、按 tool→server 映射**注入用户级配置，并且这个注入点紧贴 dispatch；三是 **direct route 与计划路径的准入**（什么请求走确定性的单工具直连）。至于今天文档里那套 PreparedAction / Authorization / Approval / Idempotency / EffectReceipt，是后来更强的 Tool Control Plane，不归这段 4 月的工作。

第二层：

- ADR 0007（reuse-first）分得很清楚：MCP 只提供工具暴露 / 协议，**不拥有**授权或现实效果事实；这两类语义必须由 Zuno 的 06/08 拥有。
- MCP 传输、工具发现、协议连接交给成熟 provider（`MCPManager` 等）；自研只到「暴露、注参、准入」。
- 当时那段代码没有 effect control——`PreparedAction` / `Approval` / `Reconcile` 是后续层。

- `事实层`: Historical（4 月）/ Target（今天的 Build-Buy 口径）
- `证据`: ADR `docs/decisions/0007-reuse-first-provider-boundary.md`；`project-fact-provenance.md` PF-032 末尾的边界说明
- `边界`: 我不把后来的 Tool Control Plane 反写成 4 月成果，也不说「Zuno 自研了 MCP 协议」。

## A15

我能复核到的是结果，不是三路各自的精确 rank。那轮 audit 记的是 baseline `Recall@5=1.00`、local GraphRAG `Recall@5=0.80`，并逐题指出了两次 top5 回退：一条把 baseline 已命中的 gold `Ed Wood` 挤出去，注入了 `Sinister (film)` 和 `Adam Collis`；另一条把 `Shirley Temple` 挤出去，注入了 `Charles Craft`。所以我能给到「谁被挤出、谁被注入、根因是排名位移」。三路 vector / BM25 / graph 各自在那个 query 上的 rank，我没有单独存档——我开始记录 per-source rank 是后来改 fusion 的时候才加进去的。

第二层：

- 根因定性：ranking **displacement**，不是「graph route 完全没激活」，也不是候选池里真的缺那个文档。
- 实现里从 `5d9b719e` 起在 `merge()` 记录 `vector_rank` / `bm25_rank` / `graph_rank`，`_baseline_rank()` 取 `min(vector_rank, bm25_rank)`。
- 事后 audit 无法补出历史三路 rank，因为当时没落这个 metadata。

- `事实层`: Historical
- `证据`: `7928df50e9b5f3035e576fa4ed47eaf31c93cc78`（audit 文档，含两条 regression question id `5a8b57f2…` / `5a8c7595…`）；`docs/governance/project-fact-provenance.md` PF-031
- `边界`: 「三路精确 rank」= 无直接证据，保留 Unknown，不用今天的代码反推。

## A16

是我自己跑出来的。我先在一轮 retrieval-only `real_runtime` smoke 里看到 local 掉到 0.80，把它写成一个 audit 文档（先立证据、再动手），然后才连续改。要说 ownership 的边界：提交在我的 GitHub 账号下，但仓库口径是「作者字段区分不出个人与团队」，所以我只说「这是我能自证的一笔」，不说「整个 GraphRAG 是我独立实现的」。

第二层：

- 顺序：`7928df50`（audit，只改文档）→ `5d9b719e`（fusion）→ `c7814793`（seed）→ `c17f737f`（alias）→ `762ffdc7`（path）→ `8a11c193`（eval 基建限制）→ `3da5d742`（rerun）。
- 先写 audit 再改，是为了让「原来哪里会错」有独立、可复核的落点。

- `事实层`: Historical / Personal Ownership（受限）
- `证据`: 上述 commit 链；PF-031
- `边界`: 不能扩成「GraphRAG 整体是我的」；也不能说这条和 PF-017 客户质量反馈是同一个 Cause→Fix。

## A17

不是加权融合，是把 baseline 的原始 rank 当成**不可被挤出的下限**，再加一层分层硬分区。实现上 `_candidate_group()` 把候选分到离散的组（0：vector∩graph 且 graph 信号 ≥6；1：任一 baseline 命中，或 graph-only 且信号 ≥9；2：graph-only 且信号 ≥6；3：其余），排序 key 是 `(candidate_group, baseline_rank, -chain_score, -graph_tier, -graph_signal, -(local+base))` 升序。`baseline_rank` 就是下限，等于 `min(vector_rank, bm25_rank)`。所以 baseline 候选天然排在 graph-only 噪声前面，噪声再也挤不掉它。那个加权和（`fusion_score`）只写进 metadata，**不参与排序**。

第二层：

- `_candidate_group` — `src/backend/zuno/platform/services/retrieval/fusion.py:166-187`；`_baseline_rank` — `:190-202`；`_graph_rank_adjustment` — `:204-224`；`_rank_key` — `:951-977`；`merge()` — `:979-1073`，`fusion_metadata["strategy"] = "baseline_preserving"` 在 `:1065`。
- 排序之后还有三条按 query class 的 guardrail 做「硬替换」重排 top：comparison / bridge / genealogy。
- `_graph_signal()`（`:156-163`）是四个计数器的整数和：`graph_support_count + graph_seed_hit_count + graph_file_focus + graph_path_count`。

- `事实层`: Current / Historical
- `证据`: 上述 file:line；测试 `tests/graphrag/test_graphrag_baseline_preserving_fusion.py`（含 `test_noisy_graph_candidates_do_not_evict_baseline_top_gold_like_candidate`）
- `边界`: 这套是「护栏」不是「更好的排序算法」；它保证不劣于 baseline，不保证优于 baseline。

## A18

门槛是分档的：`GRAPH_PROMOTION_THRESHOLD = 6`，另外 graph-only 候选想进 baseline 组需要 ≥9。为什么是离散档位而不是连续加权？因为这一层要回答的问题不是「哪个更相关」，而是「这个 graph 候选有没有资格越过 baseline」——不同 route 的原始 score 本来就不可比，硬拼一个连续分会把不可比的东西假装成可比。所以用离散 guard 更诚实。但要坦白：6 和 9 是我手定的，没有 calibration 证据，它正是那种「应该被 ablation 决定该不该删」的常数。

第二层：

- `GRAPH_PROMOTION_THRESHOLD = 6` — `fusion.py:9`。
- 组划分见 A17；graph-only 进组 1 的门是信号 ≥9，进组 2 是 ≥6。
- 与 RRF 的关系：这里没有用 RRF；RRF 是排名融合，这一层是「保留 baseline rank 的硬下限 + 分层晋升」。

- `事实层`: Current
- `证据`: `fusion.py:9`、`:166-224`；ablation 协议把它列为 H1（`docs/governance/rb019-graphrag-ablation-protocol.md` §3）
- `边界`: 档位来源 = 手定，无调参记录；不声称「经过优化」。

## A19

记录下来的那次 rerun 是同条件的一套：2026-06-20，同一数据集 `hotpotqa`，`limit=5`，`top_k=10`，auto route policy，三个模式（baseline / local / deep）在同一次记录里。但有两点必须说清楚，否则会误导：第一，更早那轮 limit=5 的 smoke 用的是 `qwen-plus`，是 profile 对齐之后才换成 `deepseek-v4-flash` 的；第二，「同一索引」严格说不成立——runner 是在进程内用 corpus 临时重建一个本地 graph retriever、注入 runtime registry，跑完就清掉，索引并不持久化。

第二层：

- 5 条 query 是 HotpotQA（distractor）里的多跳题，是 `--limit 5` 截出来的前 5 条，不是按 query class 挑的。
- runner：`tools/evals/zuno/multihop_eval/run_real_runtime_eval.py`；`--limit` 默认 10，5 是命令行传的；`selected_questions = all_questions[:max(limit,0)]`（:391）。
- 原始报告落在 gitignored 的 `reports/evals/multihop/real_runtime/`。
- 图索引不持久化是 `8a11c193` 那笔专门记录的 eval 基建限制（`ingest_to_knowledge.py` 仍是 `not_implemented`）。

- `事实层`: Historical / Current（基建边界）
- `证据`: `3da5d742`（rerun 记录）；`8a11c1930b6e7e3cf34e7708e5c967fdcc564292`；PF-031
- `边界`: 所以这条只能写「在该 5-query 样本上不再低于 baseline」，不能写「正式 benchmark」或「已证明收益」。

## A20

「不再低于 baseline」用的是 retrieval-only 口径的 `Recall@5`（audit 同时记了 `MRR@10`）；协议里把首要指标固定为 `FullChainHit@5` 与 `Recall@5`。这个数不是我手算的，是 eval runner 按 gold 命中算的。但有一个我必须主动说的原始数字：这次 rerun 里 **baseline 自己的 `MRR@10` 也从 0.90 变成了 1.00**，所以不能把任何精确变化单独归因给某个机制——baseline 动了，说明这份 5 题样本本身波动就大。

第二层：

- 报出的对齐数字：local 恢复到 `Recall@5=1.00`、`MRR@10=1.00`、`ChainRecall@5=1.00`、`FullChainHit@5=1.00`，`fallback_count=1`。
- 5 条样本下，一条题的命中变化就是 0.20 的指标移动——这个粒度本身就说明为什么它只能是 smoke。
- 指标定义与口径来源：`tools/evals/zuno/multihop_eval` 的 README 与 `rb019-graphrag-ablation-protocol.md` §4。

- `事实层`: Historical
- `证据`: `3da5d742`；PF-031（原文就写了 baseline MRR 也在 rerun 中变化）；`docs/evidence/current-eval-baseline.md`（`MEASUREMENT_BLOCKED`）
- `边界`: 先给工程结论「这是 smoke、不是 benchmark」，再给原始数字；不制造单机制收益百分比。

## A21

因为独立 holdout 现在**跑不了**，不是我没想跑。按冻结协议，一次 holdout 需要三个条件同时成立：可访问的数据集、可运行的知识索引、模型凭证；并且要先冻结 split id，每个数据集建议 ≥300 题。今天的真实状态是：本机连 HotpotQA 官方源 TCP 超时、`data/evals/multihop/` 不存在、没有模型 API 凭证与运行时索引。所以协议状态就是 `BLOCKED_PENDING_DATA`。

第二层：

- 代价构成：数据集接入（HotpotQA / 2WikiMultiHopQA / MuSiQue 经 adapter 归一化）+ 冻结 split + 可运行的 Knowledge 索引 + 模型凭证 + 逐题报告落 gitignored 目录。
- 明确禁止：拿调参样本上的旧 `limit=10/20/50` 结果冒充 holdout。
- 解锁条件写在协议 §8：数据 + 索引 + 冻结切分齐了才执行。

- `事实层`: Current（测量状态）
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md` §5/§6/§8；`docs/evidence/current-eval-baseline.md`
- `边界`: 这是环境阻塞，不是结论保留；不给「下周就能跑」这种话。

## A22

我没做过这个 ablation，所以下面**是预测，不是结论**。如果做 leave-one-out，我预期 H1（baseline-preserving fusion / promotion threshold）掉得最多，因为它直接防的就是已经观察到的那个失败——graph 噪声把 baseline 已命中的 gold 挤出 top5；去掉它，那两条 regression 应该立刻回来。别名归一化我预期在 HotpotQA 上影响最小（它主要救 `(novel)` 这类后缀差异，英文样本里这种形态不密集），但它在中文法律主体上有多重要，我反而更没把握（见 A24）。seed expansion 和 path ranking 应该居中，但我给不出方向一致的预期。

第二层：

- 三个机制各自的针对性测试是存在的（`tests/graphrag/test_graphrag_seed_expansion.py`、`test_graphrag_entity_alias.py`、`test_graphrag_path_ranking.py`），测试只证明对应 behavior，不证明对指标的边际贡献。
- 协议 §2 的判据是：full 相对 full-minus-H 方向一致且跨切分稳定才保留；不稳定或不显著就删。

- `事实层`: Open Design / 预测
- `证据`: 机制实现 `fusion.py` / `retriever.py` / `entity_alias.py`；协议 §2/§3
- `边界`: 明确标成预测；如果 Red 追问「你凭什么这么排」，我的依据是失败形态的因果强度，不是数据。

## A23

seed 现在是「候选感知」的：除了 query 词，还会把 baseline top5 候选的 title / file_name 也变成 seed，每个 seed 带 `source` 标签（`query` / `baseline_title` / `baseline_file` / `baseline_entity` / `alias`）。别名归一化是**规则**，不是字典也不是模型：先做字符串规范化（去括号后缀、去冠词、连字符→空格、小写、压空白），再做精确匹配 → 规范化精确匹配，可选模糊匹配；有一份 `GENERIC_ENTITIES` 名单永不展开。

第二层：

- `_build_seed_entities_with_source()` — `src/backend/zuno/platform/services/graphrag/retriever.py:289-376`（candidate-context 段 :349-371）；`_extract_query_seeds()` — `:279-287`（保留向后兼容）。
- 上游 `orchestrator.py:655-674` 从 `rag_result["documents"][:5]` 构造 `candidate_context`，经 `graph_options["candidate_context"]` 传下去。
- `normalize_entity_name` — `graphrag/entity_alias.py:25-32`；`resolve_alias` — `:35-61`；`GENERIC_ENTITIES` — `:10-22`。

- `事实层`: Current / Historical
- `证据`: 上述 file:line；测试 `test_graphrag_seed_expansion.py`、`test_graphrag_entity_alias.py`
- `边界`: 是规则/字符串级，不是实体消解；没有中文法律实体词典参与。

## A24

会，而且现在这层没有防护。当前 alias 模块只做字符串规范化加精确/规范化精确匹配，它不是实体消解：`normalize_entity_name` 里「去掉括号后缀」这一步就可能把两个本来不同的实体规范到同一个串上；它也没有「母公司/子公司/分公司」这种层级或从属关系判断，没有中文法律主体词典。所以「会不会把子公司和母公司误合并」——在规则恰好能碰到的那些串上会，而且我没有在中文法律语料上测过它，所以这是「未评估的风险」，不是「已经验证安全」。

第二层：

- 危险点一：括号内容被剥离后可能撞串（例如同一集团下的不同主体用括号区分）。
- 危险点二：没有从属/层级语义，别名解析不做「同一个法人」判断。
- 危险点三：`GENERIC_ENTITIES` 只挡一批通用词，不挡法律主体。
- 当前这条机制在 HotpotQA 英文样本上的收益也没有 ablation 支持。

- `事实层`: Current / Fundamental（在真实域上的失效）
- `证据`: `graphrag/entity_alias.py:25-61`；没有中文法律实体测试用例
- `边界`: 我承认这是已知薄弱点；如果今天重做，我会先问「别名归一化在中文法律主体上到底该不该用规则」，而不是先扩规则。

## A25

延迟有记录，token 没有。那轮 rerun 里 `local_graphrag` 的平均时延从大约 15806ms 涨到 18503ms——但这是本地重建图路径的数字，不是生产路径。token 成本我没有实测过，没有可信数字可以给。所以这条的诚实答案是：额外时延有量级观察、额外 token 成本 = Unknown。

第二层：

- 时延数字来自 `3da5d742` 的 rerun 记录（local_graphrag 均值 15806→18503 ms）。
- 协议 §4 要求按 query 记录 token / 调用次数和 p50 / p95 时延，但那是「要测什么」，不是「已经测了」。
- 多跳图检索天然多出一轮图遍历 + 更多候选，成本方向是明确的，量级未知。

- `事实层`: Historical（时延）/ Unknown（token）
- `证据`: `3da5d742`；协议 §4
- `边界`: 我不把「方向上升」包装成「代价可接受」，也不编一个 token 数字。

## A26

判据写在冻结协议里，而且很硬：在冻结的独立 holdout 上，如果某条启发式 `H` 的 full 相对 full-minus-H 没有方向一致、跨切分稳定的提升，就删掉它，删完重跑剩余项；如果一条都留不下来，那是可接受结论。对整层来说，如果 GraphRAG 在它声称擅长的 query class 上打不过更简单的 baseline，那它就该退回普通 hybrid / vector 检索，而不是因为「更复杂」保留。

第二层：

- 协议 §2：不许用调参样本上的提升当保留理由（这些启发式当初就是在那些样本上调出来的）。
- 首要指标：`FullChainHit@5` 与 `Recall@5`；其余（Recall@2/10、Precision、MRR、ChainRecall、CitationLineage 命中、token/时延、fallback/失败计数）作为约束。
- 执行模式必须标 `real_runtime`；mocked / stackless 结果不得混入。

- `事实层`: Target / Open Design（这是我自己认的判据）
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md` §2/§4/§6
- `边界`: 这是「什么结果出现就该删」的规则，不是「现在已经该删」的结论。

## A27

会在两类场景上失败。第一类是长任务/多轮：上下文不断追加历史，一条被 reviewer 拒掉的候选还躺在对话历史里继续影响后面的推理；新材料进来了，旧 summary 还留在前文，模型看到的是一份不断变长、来源和有效性混杂的临时记忆。第二类是恢复：run 崩了以后，如果没有按 scope 组织过的、带 provenance 的记录，你只能拿一个旧的 context blob 当「被冻结的世界」，既不能按当前 domain / knowledge / security 重新组装，也说不清某句话是从哪来的。单轮问答不需要这一层，这个我不硬撑。

第二层：

- 目标是让 Context 变成「一次执行需要的临时工作集」，材料/正式判断留在各自 Owner（03/02），需要跨 step 保存的写到有明确 Owner 的外部状态。
- 关键不变量：`Provenance != Truth != Authorization != Semantic Preservation`——source id 只能说明来源，不能证明真实性、权限或压缩没丢关键法律限定。

- `事实层`: Target / Open Design
- `证据`: `docs/architecture/architecture.md`（Context 与 Memory 段）；`docs/modules/reference.md`「Memory record != Domain truth」
- `边界`: 这是必要性论证，不是「我们已经解决了」；简单场景我明确说不用上这层。

## A28

V1 是项目原有的 memory 子系统：公开根提交里就已经有 `services/memory/`、Memory History DAO 和 Chroma / Milvus vector store，`MemoryClient` 默认用 Chroma。V2 这条链——6/25 的 Target 计划、6/26 的 typed Context contract → scoped Memory foundation → 最小 `GeneralAgent.prepare_context` / post-turn 集成 → 最小 `ContextOrchestrator`，再到 6/29 PR #8 的 readback hardening——提交都在我的账号下。我改的部分：引入 typed Context / Memory contract 与带 review 状态的 scope 模型，把「同 scope 的 task summary + 仅 APPROVED 的 structured memory」接回调用前读取，并补 source trace、policy / provenance 约束和 focused tests。我没有从零建整套 Memory，也不是 OpenViking 那批最早工作的证据承担者。

第二层：

- `13dd929`：`ContextSource` / `ContextItem` / `TokenBudgetPolicy` / `ContextTrace` / `ModelContextPacket` / `ContextPreparationInput`。
- `b1836dc`：`MemoryLayer` / `MemoryScope` / `RetentionPolicy` / `RawMemoryEvent` / `TaskMemorySummary` / `MemoryCandidate` / `InMemoryLayerStore`。
- `d4e2fe2`：`GeneralAgent.prepare_context()` + 回合后写入。
- `3d865e1`：`ContextOrchestrator` + `RecentWindowSelector`。
- `f3c7433`（PR #8，单实现提交，merge `b8502ef5`）：`ContextPackPolicy`、`ContextSource.TASK_SUMMARY/MEMORY`、`source_event_ids_by_item`、`MemoryReviewStatus`，以及 pre-call readback。

- `事实层`: Historical / Personal Ownership（受限）
- `证据`: 上述 SHA；`docs/governance/project-fact-provenance.md` PF-029 / PF-030 与「Memory / OpenViking 取证边界」
- `边界`: PF-010 明确「公开根提交已经存在 Memory 子系统」，所以不能说用户从零引入 Memory；OpenViking 的接入细节仍未恢复，不能用 V2 / PR #8 反证。

## A29

因为这一层多出来的不是更花哨的 SQL 谓词，而是三条语义。第一，scope 是读写、合并、回溯统一用的四维身份（user / agent / project / thread），不是「检索时随手加个过滤」。第二，也是最容易混的一条：**scope 相等 ≠ 授权**——一条记录 scope 命中不代表当前请求有权召回它，能不能 recall 是 08 的 lifecycle / recall 判断，不能拿 scope equality 当 permission。第三，每个 item 必须带 source trace，provenance 只是来源，不等于真值，也不等于压缩没丢语义。数据库层确实就是四列 WHERE，所以剩下的价值全在这三条约束和它们带来的边界上。

第二层：

- `MemoryScope`：`user_id`、`agent_id`、`project_id`、`thread_id`（`platform/services/memory/layers.py:43-55`）；DB 层 `_scope_select()` 生成 `WHERE user_id=:user_id AND agent_id=:agent_id AND project_id=:project_id AND thread_id=:thread_id`（`memory/store.py:520-526`）。
- runtime 侧 `_memory_scope(state)` 里 `agent_id` 是硬编码字面量 `"agent_run"`（`agent/runtime/nodes/core.py:485-491`）。
- 关键区分（模块 reference）：`MemoryScope equality != Authorization`；`Provenance != Truth != Authorization != Semantic Preservation`。
- recall eligibility 由 08 拥有，01/04 只消费当前允许的 snapshot（Target）。

- `事实层`: Target（语义）/ Current（实现）
- `证据`: `layers.py:43-55`；`memory/store.py:520-526`；`docs/modules/reference.md`「绝对不能再次混淆的边界」
- `边界`: 「scope equality ≠ authorization」这层**今天在代码里没有独立 08 门**，实际生效的是 scope + APPROVED 过滤；这是 Current/Target 差距，我不夸大。

## A30

不是 Agent 直接写。模型只能产生 `MemoryCandidate`，写入要经过 review（`MemoryReviewDecision`）。入口是回合后的 `post_turn_commit` 节点，它调 governed runtime 的 `commit_turn_outcome`，在一个 `MemoryUnitOfWork` 里一次性写 raw event、task summary、memory version / context pack / usage trace。这个入口的 owner 是 Memory 引擎加它背后的 repository，不是 Agent，也不是模型的自觉。

第二层：

- `post_turn_commit` — `src/backend/zuno/agent/runtime/nodes/core.py:391-482`；写 raw event（:396-409）、task summary（:410-417）、`governed_runtime.commit_turn_outcome(...)`（:419-442）、reflexion lesson candidate（:445-452）。
- `GovernedMemoryContextRuntime.commit_turn_outcome` — `memory/governed_runtime.py:30-142`：`commit_governed_memory(memory_kind="EPISODIC", trigger_type="RUN_OUTCOME")` → `activate_memory_version` → `build_context_pack` → `record_memory_use`。
- 审批：`MemoryReviewDecision.approve`（`layers.py:224-239`）；engine 侧 `review_memory_candidate`（`memory/engine.py:317-374`）在 APPROVED 时 `replace(candidate, review_status=APPROVED, requires_review=False)` 并落 `memory_candidate_approved` 治理条目。
- 异常安全：写入失败时置 `task_state["memory_persistence_unavailable"]=True` 并跳过，读回节点也尊重这个 flag。

- `事实层`: Current / Target（Candidate→review 语义）
- `证据`: `core.py:391-482`；`governed_runtime.py:30-142`；`engine.py:317-374`
- `边界`: 这是「写入入口在哪」，不是「写入质量已被证明」；review 是否足够（谁有资格审）我没有证据。

## A31

Target 口径下，最终判断权在 08：它拥有 recall eligibility / lifecycle policy，01/04 只消费当前被允许的 snapshot。**但今天真正生效的门不是 08**——是 engine 读回时的两个条件：同 scope，加上 `review_status == APPROVED`；非 APPROVED 的会被 `_memory_exclusion_reason` 排除。所以严格的回答是：Target 上这个 authority 属于 08，Current 上它落在 Memory engine 的过滤逻辑里，独立的 08 recall decision 尚未接上。这是差距，我如实说，不把 Target 说成已完成。

第二层：

- 过滤点：`MemoryEngine._memory_exclusion_reason` — `memory/engine.py:1054-1064`（非 APPROVED 返回 `..._review`）；`render_context_pack` — `:753`，走 `store.task_summaries(scope)` 与 `search_semantic_memory(scope=...)`，空时 fallback 到 `_approved_memory_candidates(scope)`。
- Target：08 owns Recall Eligibility / lifecycle；`docs/modules/security/README.md` 明确「in-flight recall 由 08 决定能否使用」，02 仍拥有业务 truth。
- 现有 capture intent 上带 `security_epoch_ref`，但这不是完整的 recall decision。

- `事实层`: Current（实现）/ Target（authority）
- `证据`: `engine.py:753`、`:945-950`、`:1054-1064`；`docs/decisions/0007-reuse-first-provider-boundary.md` §Optional Context / Memory（Recall 是 ContextCandidate）
- `边界`: 我不把「APPROVED 过滤」包装成「08 recall authority 已实现」。

## A32

撤回影响的是**未来读取**，不改历史。机制上，一条 memory 被改回 REJECTED 之后，下一次 `render_context_pack` 会因为非 APPROVED 直接把它排除，所以后续回合不再读回它。已经写下的历史 context pack 是当时的快照，不会被改写——这符合系统的一条总原则：撤权控制新的受保护使用，不重写已经合法发生的历史。

第二层：

- 排除点：`_memory_exclusion_reason`（`engine.py:1054-1064`）；测试 `tests/memory/test_context_pack_engine.py:131` `test_context_pack_excludes_stale_conflict_revoked_and_sensitive_memories_with_reasons`。
- review decision 有独立落库：`DurableMemoryStore.save_review_decision`（`memory/store.py:93`）+ DB `memory_review_decision` 表；candidate 表有 `review_status` 列（`platform/database/models/memory_runtime.py:69`）。
- 历史回合里已经注入的内容不回收。

- `事实层`: Current（未来读取）/ Target（撤权只约束未来）
- `证据`: 上述 file:line；`docs/modules/reference.md` C3「撤权只约束新的受保护访问和尚未执行动作」
- `边界`: 「已经写进模型上下文的历史轮次怎么被当作脏数据清除」没有机制；我只能说它不再进入**新的** context pack。

## A33

读回是在 build 时按 scope 现取，而且有明确的排除逻辑：stale / conflict / revoked / sensitive 的条目会被排除并记原因。所以「状态已经正确刷新成 stale」的情况是被挡住的。但你问的恰恰是「过期了但状态还没刷新」——这种情况今天**挡不住**：没有后台 reaper 去主动刷新状态，staleness 完全靠已记录的状态判断；状态本身没更新，它仍可能被注入。这是一个真实的缺口。

第二层：

- 排除逻辑：`_memory_exclusion_reason`（`engine.py:1054-1064`）。
- 测试把「stale / conflict / revoked / sensitive」四种排除都锁住了：`tests/memory/test_context_pack_engine.py:131`。
- 没有发现任何后台任务负责刷新 summary / candidate 的时效状态。
- 上下文里的 `task_state` 只有 caller 传进来的字段加上 thread/task id，没有 freshness 时间戳校验。

- `事实层`: Current（能力）/ 缺口（未刷新状态）
- `证据`: 上述 file:line 与测试
- `边界`: 我明确说「状态没刷新 = 挡不住」；不把它含混成「我们有 staleness 防护」。

## A34

诚实说：今天**没有语义仲裁**。candidate 级别只有 `dedupe_key` 和一条 consolidation 路径（产出一个 consolidated candidate）；memory version 的激活有 `SELECT ... FOR UPDATE` 加 generation CAS，能保证**同一条 version** 不被两次激活，所以你不会退化成「并发写覆盖一条记录」。但「同一 Domain 里两条内容互相冲突的 memory 同时存在」这件事，系统不会自动判谁对——你会得到两条并存的候选，冲突处理不在这层。要哪条赢，得靠上层（review 人判或后续 consolidation）。

第二层：

- 悲观锁 + 乐观 CAS：`MemoryRepository.activate_memory_version` — `platform/database/memory/domain.py:301`；`SELECT status FROM memory_versions ... FOR UPDATE`（:315），状态必须 ∈ {`APPROVED`,`ACTIVE`}（:320-321），`UPDATE ... WHERE ... AND generation=:expected_generation`，`rowcount != 1` 抛 `MemoryGovernanceConflict("memory activation CAS failed")`（:363-364）。
- `MemoryUnitOfWork` 用 `connection.begin()`，**没有显式设置隔离级别**（DB 默认），全仓库 `domain.py` / `store.py` / `engine.py` 里唯一一处 `FOR UPDATE` 就是 `domain.py:315`。
- 幂等：`memory_commit_receipts.idempotency_key` + `ON CONFLICT DO NOTHING`；`content_hash = canonical_sha256(...)`。

- `事实层`: Current / Fundamental（并发与冲突）
- `证据`: `domain.py:301-364`、`:268-299`、`:83-99`
- `边界`: 我能说「同一 version 不会被双激活」；不能说「冲突 memory 会被正确仲裁」——后者不存在。

## A35

不能，因为我没有做过。没有 A/B，也没有一个可复现的对照 case。ADR 0007 明确要求 long-term memory 走 kill test（No long-term memory → Working context only → Typed episodic → +semantic/procedural → External Context Provider），指标包括 task completion、unsupported claim、stale-memory error、context relevance、human correction、token、latency、cost 和 scope violation；这个还没做。所以今天我能说的只有「设计上多解决了什么」，不能说「加了就更好」。

第二层：

- 现有证据只到「focused tests 通过 + contract-level 行为正确」：PR #8 描述记 focused tests 32 passed、repo tests 66 passed、legacy compatibility 11 passed、三 profile contract eval `status: ok`。测试证明 behavior，不证明质量收益。
- `docs/evidence/current-eval-baseline.md` 是 `MEASUREMENT_BLOCKED`。

- `事实层`: Current（测试）/ Open（收益）
- `证据`: PF-029 记录的 PR #8 描述；ADR 0007 §8；`current-eval-baseline.md`
- `边界`: 明确说「没有 A/B」，不拿单测通过冒充质量证据。

## A36

按已接受的口径：如果跨会话 A/B 显示 structured long-term memory 没有稳定边际收益，就关掉它，退回 `Raw Event + task summary + 按需读取 Owner facts`。注意删的是 **structured long-term memory 这一层**，Context 组装保留——Context 组装是执行优化，本来就不承担业务 Authority。所以删除条件不是「出故障」，而是「测量上没有可重复收益」。

第二层：

- 架构口径：`structured long-term memory 是否保留由 09 的 A/B / kill test 决定`；「没有稳定收益时退回 Raw Event + task summary + 按需读取 Owner facts」。
- 同一条规则也适用于 GraphRAG / Reflection / Specialist / Native Runtime：measurement-gated。

- `事实层`: Target（删除判据）
- `证据`: ADR 0007 §8；`docs/modules/reference.md`「Memory / Context 是 Optional Provider Boundary」；`docs/architecture/reference.md` B12 Delete conditions
- `边界`: 这是「什么条件下删」，不是「今天该删」；今天没有测量数据支撑任一方向的结论。

## A37

会在一类请求上失效：任务跑到一半、前提变了、而且有旧结果正在返回的请求。具体 case：一次合同争议分析并行三个分支——合同义务、付款事实、抗辩理由——前两个已经返回，用户这时补进一份补充协议，改了付款日期；几分钟后旧的抗辩分支带着一份写得很好的结果回来。固定 workflow 只会问「这一步成功了吗」，它没有能力判断这份结果基于哪一版材料、现在还成不成立；它也没有能力区分「Domain 已经提交但 checkpoint 还没写」。这类时间差才是 Runtime 存在的理由。

第二层：

- 需要的判断：结果依赖哪版 DocumentVersion / KnowledgeGeneration、哪版 Plan；接受、重新验收还是重做。
- 另一类同源问题：Domain 已提交、Checkpoint 未写时，恢复若只信旧 Checkpoint 会重复提交正式事实。
- 短任务、无副作用、失败重跑无代价时，ReAct 循环或固定 workflow 就够——这点我不否认。

- `事实层`: Target / Fundamental
- `证据`: `docs/modules/runtime/README.md`（四个故障窗口）；`docs/architecture/reference.md` B7 failure windows
- `边界`: 这是「哪类请求需要 Runtime」的论证，不是「我们已经完全实现」；完整三层运行图与 Replan Barrier 今天仍是 Target/Gap。

## A38

一个 PlanVersion 冻结的是**运行因果**，不是具体的工具/prompt/模型版本。它绑定 `plan_id / plan_version`、`run_id`、`status`、`planner_role / planner_attempt_ref`、`plan_hash`、`created_from_plan_version`、`replan_reason`、`activated_at`、`superseded_at`；一旦 ACTIVATED，Step、edge、requirement 的集合就不可再改。真正解析出来的 Capability / ProviderBinding / ToolVersion / Model / config 是记在**每个 StepRun 的 resolved input-version set** 上的，dispatch、晚到、resume 时由各自的 Owner 判断还兼不兼容。这点很容易被说错，我特意分开讲。

第二层：

- PlanVersion 字段：`docs/modules/runtime/reference.md` B14.1；状态机 `DRAFT → ACTIVATED → SUPERSEDED`，ACTIVATED 不可变（`docs/architecture/reference.md` B5）。
- StepRun resolved dependency set：`PlanVersion + input refs + KnowledgeGeneration + CapabilityVersion / ProviderBinding + Model/Tool/config refs + applicable security refs`（`docs/architecture/reference.md` B9）。
- Runtime 记录版本，但**不自己判断兼容性**：05 判 Capability、06 判 Tool semantics、07 判模型路由、08 判安全/credential、03 判 KnowledgeGeneration。
- 代码：`src/backend/zuno/agent/domain/task_contracts.py:345` `PlanVersion`（frozen dataclass，:367-371 校验 hash）；`agent/runtime_batch.py:103` `PlanVersionRecord`（status `DRAFT/VALIDATING/ACTIVE/SUPERSEDED`，:138 `immutable_hash`）；`platform/model_gateway.py:3171` 明确禁止 Model Gateway 激活 PlanVersion。

- `事实层`: Target（定义）/ Current（部分实现）
- `证据`: 上述 doc 与 code file:line
- `边界`: 不可变 PlanVersion 的完整语义今天仍是 Target/Gap（`docs/modules/runtime/README.md` Current 段）；代码里已有 hash/immutable 表达，但不能说完整冻结语义已实现。

## A39

不自动丢弃，也不自动合并。晚到结果要重新验收：先比 PlanVersion、resolved input-version set、DocumentVersion / KnowledgeGeneration、Capability / Tool / Model 版本和 Security 新鲜度，纯计算的假设过期就 reject / 重新评估 / Replan。但也有一条不能违反的原则：如果这份「晚到结果」其实对应一个**已经发生的现实 Effect**，那 Runtime 不能因为它来自 stale branch 就否认现实。今天代码里有 late-result 的处理分支（reject / reconcile checkpoint），但完整的 Replan Barrier 语义仍是 Target。

第二层：

- 状态表达：`Branch: IN_FLIGHT → ARRIVED → ACCEPTED / REJECTED_STALE / REEVALUATION_REQUIRED`（`docs/modules/runtime/reference.md` B7）。
- 代码侧：`agent/runtime/planning/recovery.py:11` `RecoveryAction`（含 `REJECT_LATE_RESULT`、`RESUME_IN_FLIGHT`、`RECONCILE_CHECKPOINT`）。
- Join 侧要求：接受晚到结果时重新校验 PlanVersion / input set / security freshness / Capability/Tool/Knowledge 版本；reducer 必须幂等、按 branch identity 去重，不允许「最后写入 wins」。

- `事实层`: Target / 部分 Current
- `证据`: 上述 doc 与 `recovery.py:11`；`docs/modules/runtime/reference.md` B14.3 / B14.6
- `边界`: Replan Barrier 今天在 Gap 列表里；`docs/modules/runtime/README.md` 明确「不可变 PlanVersion、Replan Barrier」仍是 Target/Gap。

## A40

检测方式是去问真正拥有结果的 Owner，而不是相信 checkpoint 比谁新。当前实现里的做法是：Domain 侧用 canonical mutation / version 的 expected-version CAS 和 idempotency 来回答「这一步有没有已经提交」；如果 Domain 的 generation 已经领先于 checkpoint，就先修 Runtime 的控制进度（`recovery.py` 里有这个分支），不再提交一次。Target 上这个锚点是 matching `AdmissionReceipt`——但要说清楚，`AdmissionReceipt` 今天 `NOT IMPLEMENTATION-PROVEN`，所以现在能依赖的是 domain mutation/version 那一套。

第二层：

- 代码：`src/backend/zuno/agent/runtime/planning/recovery.py:11` `RecoveryAction`，`:125` 有「domain generation 领先 checkpoint」的分支；`src/backend/zuno/agent/runtime/service.py:202` `resume()`，`:221` `latest_checkpoint(...)`，`:224` 重建 state，`:261` `graph.invoke(...)`；`:402` `_assert_scope`。
- Domain 侧：`InMemoryCanonicalDomainStore` / `SqlAlchemyCanonicalDomainStore` 用 expected DomainVersion CAS，过期返回 `VERSION_CONFLICT`；同 idempotency 输入返回 `ALREADY_APPLIED`，同 key 不同输入 `REJECTED`（Wave-001 证据）。
- 恢复顺序（C4）：load checkpoint → 查 02 Receipt → 查 06 Effect → 刷新 08 授权 → 重验 03/05/07 → 修 Runtime。

- `事实层`: Current（Domain CAS / checkpoint 分支）/ Target（AdmissionReceipt）
- `证据`: `recovery.py:125`；`tests/domain/test_domain_mutation.py`；`docs/evidence/implementation-wave-001.md`；`docs/evidence/README.md`「TARGET ADMISSION RECEIPT: NOT IMPLEMENTATION-PROVEN」
- `边界`: 「owner-first E2E recovery」和「checkpoint complete 但 Receipt 缺失时拒绝 formal-complete」在 `current-test-baseline.md` 里明确列在**未证明**清单里。

## A41

操作上 Runtime 拥有 checkpoint / resume 的控制事实，所以「从哪一步继续」这个动作是它做的；但它的恢复顺序被一条规则约束住：先去看有没有更强的 Owner 事实，再修自己。也就是说——正式业务提交先问 Domain，现实副作用先问 06，授权先问 08，只有纯计算没有留下更强外部事实时才重新算。所以答案是：Runtime 决定操作上的继续点，但判断依据必须来自拥有结果的那个 Owner；它不允许用一份更旧的控制快照去覆盖业务世界。

第二层：

- C4 恢复顺序：`load checkpoint / pending writes → validate active PlanVersion / controller lease → query 02 AdmissionReceipt when required → query 06 Effect / Reconciliation when required → refresh 08 Authorization before new protected action → revalidate 03 / 05 / 07 → repair Runtime Control State`。
- Checkpoint 只证明「Runtime 上次记录到哪」，可能比 Domain / Effect / Security 的事实更旧。
- Lease / fencing 保护 Runtime 自己的并发边界，但不证明远端 POST 没发生。

- `事实层`: Target（authority 划分）/ Current（顺序部分实现）
- `证据`: `docs/modules/runtime/reference.md` C4 / B9；`docs/modules/reference.md`「恢复时先找 Owner Fact，再修复 Projection」
- `边界`: 完整跨 Owner recovery 是 Gap；今天代码只证明了 checkpoint、interrupt、cancel/restart、duplicate claim 这些有限行为。

## A42

纯 LangGraph 不够，不是因为它缺 checkpointer——它恰恰给了图执行、checkpoint、interrupt、pending writes。它不知道的是业务上发生了什么：Formal Admission 有没有成立、外部 POST 有没有发出去、权限还有没有效。所以我们做了一件有点反直觉的事：canonical graph 故意**不**把 LangGraph 的 `BaseCheckpointSaver` 当权威，Agent Run store 才是真值，LangGraph 只管 transition control——`graph.py` 里那句注释写的就是这个。还有一个纯框架解决不了的细节：`interrupt()` 恢复会从节点起点重跑，所以 interrupt 之前的可见副作用必须幂等，或者被拆到单独的 node / 06 的 effect boundary 上。

第二层：

- 代码：`agent/runtime/graph.py:5` 用 `langgraph.graph` 的 `StateGraph`；`:17-19` 注释明确「checkpointer is Zuno's domain checkpoint bridge, not a LangGraph BaseCheckpointSaver … the Agent Run store remains the source of truth while LangGraph owns transition control」。
- 官方 PostgresSaver 已引入：`agent/runtime/phase08.py:8-11`（`InMemorySaver` / `PostgresSaver` / `Command, interrupt`），`:40` `PostgresSaver.from_conn_string(...)`；依赖 `langgraph-checkpoint-postgres = 3.1.0`（ADR 0005），且 ADR 明确 checkpoint 表**不得**被解释为领域成功。
- Zuno 在框架之上加的是：dynamic Plan DAG + `Send`、Replan Barrier、幂等 reducer（按 branch identity 去重）、恢复矩阵、06/08 门。

- `事实层`: Current / Build-vs-Buy
- `证据`: `graph.py:17-19`；`docs/decisions/0005-official-langgraph-postgres-checkpointer.md`；`docs/modules/runtime/reference.md` B11 / B14.5
- `边界`: 我不说「我们自己实现了 checkpointer」——恰恰相反，官方 saver 用来做 primitive，自研的是它不拥有的业务恢复语义。

## A43

删除判据是：如果 Generic Agent Host 加我们的 Legal Backend 已经能在三件事上给出同样正确的行为——Domain 已提交/Checkpoint 落后时的恢复、Effect unknown 时的停车与对账、resume 后重新授权——而且自研 Runtime 的额外收益超不过它的维护成本，那这一层就该缩薄，甚至退出主路径。怎么测：A/B/C 对照——Generic Host + Legal Skills、Generic Host + Zuno Legal Backend、Zuno Native Runtime + 一等领域状态，测 Evidence Sufficiency、Citation Correctness、Unsupported Claim、Reviewer Acceptance、Recovery Correctness、duplicate-effect、Latency、Token、Cost。这套今天没有跑，所以没有结论。

第二层：

- 判据来源：ADR 0012（Evidence-gated physical service split）+ 总体架构 B12 Delete conditions。
- 前提条件：只有真实任务证明通用 Host 在这些约束上不足，且额外 Runtime 的收益超过维护成本，才值得继续扩大。
- 今天的 Current 只证明主运行链、checkpoint、interrupt、cancel/restart、duplicate claim、unknown Effect reconcile；Native Runtime necessity 是 `not established`。

- `事实层`: Target / Open Design
- `证据`: ADR `0012-evidence-gated-physical-service-split.md`；`docs/architecture/reference.md` B12；`docs/modules/runtime/reference.md` B13
- `边界`: 这是删除判据与测量方案，不是「已经测出该删」。

## A44

在 send 前重新校验，而且是**两次**：一次在 prepare / approval 之后；另一次在 mandatory audit 提交之后、紧贴 dispatch 之前。具体是 `_reauthorize_execute_epoch()` 去调 `validate_pre_effect_authorization()`，它会 fail closed 地抛「security epoch 已过期」「action hash 在 effect 前变了」「approval 在 effect 前过期」这几类。这不是「计划时校验过就算了」，也不是「根本不校验」。有正向 fault 证据：epoch 在 send 前被 revoked 时，provider executor 调用次数是 0。

第二层：

- `_reauthorize_execute_epoch(...)` — `src/backend/zuno/capability/tool_runtime/invocation_gateway.py:1260` → `repo.validate_pre_effect_authorization(...)`（`platform/security/persistence.py:1045-1090`），抛点分别在 :1070（decision missing）/ :1072（prepared action hash changed before effect）/ :1074（stale security epoch before effect）/ :1076 / :1079 / :1084。
- 第二处调用带明确注释：`invocation_gateway.py:459-467`「Audit persistence is not a permanent authorization ticket. Re-check current security after the durable proof and immediately before any sandbox/provider dispatch.」
- 证据：PR #203 / run `34560042535`（pre-send SecurityEpoch revocation，executor 0 次调用）；`docs/evidence/README.md`「PRE-EFFECT SECURITY EPOCH REVOCATION: PASS」。

- `事实层`: Current（已验证的窄窗口）/ Target（完整持续授权）
- `证据`: 上述 file:line + run id；`docs/evidence/current-test-baseline.md` 「Slice C 正向证据」
- `边界`: 这关闭的是 `revocation-before-send` 这一个窗口；其他 Authorization / Approval / Policy drift、Policy Engine outage、no-egress 仍未证明，完整治理闭环未建立。

## A45

这个「现在仍然被授权」的最终判断权在 08，而且是在执行点上**被强制**的：06 在越过 send boundary 前消费 08 的当前决定，而不是由下游 Tool 自己说了算。AuthorizationDecision 只是政策判断，它不证明材料已读、模型已调、工具已执行；反过来，Tool 也不可能替 08 宣布自己被允许。

第二层：

- Owner 划分：08 owns AuthorizationDecision / ApprovalDecision / ModelEgressDecision / AuditRequirement；06 只消费，不拥有（`docs/modules/security/reference.md` B2，`docs/modules/effects/reference.md` B2）。
- 边界原则：「08 拥有 policy decision；目标 Store / Module 拥有 execution fact」；「安全决定不能被 Model、Runtime、Application、Tool 或 Provider 本地默认值放宽」。
- 分工模式：Decision 与 Enforcement 分离——08 产生可解释决定，03/07/06/02 在真实执行点强制，条件不全时停止。

- `事实层`: Target（authority）/ Current（enforcement 点）
- `证据`: `docs/modules/security/reference.md` B1/B2/B10；`docs/architecture/reference.md` B10
- `边界`: 下游 Tool 只能执行，不能判决；这条是设计上的硬边界，但我不能说它今天已经覆盖所有 effect 路径。

## A46

审计写在 effect **之前**，而且它是必要条件，不是事后补票。顺序是：prepare → security epoch → approval → secret lease → **mandatory audit commit** → 再查一次 epoch → 才 dispatch。崩溃时次序不被搞乱的依据是两点：audit proof 在一个独立的耐久边界里提交；send gate 会 `assert_audit_durable_for_effect(...)` 去消费那份**已经 committed 的** proof，proof 缺失时 executor 为 0。另外，proof 绑定的是那条持久化的 Security AuditRequirement 的 id/hash，requirement 漂移会在 send 前 fail closed。

第二层：

- 顺序：`_issue_secret_lease`（:409）→ `_persist_mandatory_audit_before_effect`（:429-436）→ `_reauthorize_execute_epoch`（:462）→ sandbox（:499）→ `result = await executor()`（:535）。
- fail-closed 实现：`invocation_gateway.py:1426-1527`；requirement 缺失、`requirement_hash / audit_channel_id / decision_id / status` 变化、committed proof hash 变化、commit 后 requirement 变化，都会抛 `SecurityPersistenceError`。
- 测试：`tests/security/test_mandatory_audit_postgres_boundary.py:418` `test_external_effect_requires_durable_mandatory_audit_before_dispatch`、`:848`、`:933`、`:982`。
- 证据：`docs/evidence/README.md`「MANDATORY AUDIT BEFORE EFFECT: FIX VERIFIED / MISSING PROOF FAILS CLOSED」。

- `事实层`: Current（已验证）/ Target（完整 audit class）
- `证据`: 上述 file:line + 测试；#205 / run `34560692093` 是修复前的负向 History
- `边界`: AuditRequirement 的 `BEST_EFFORT / DURABLE / MANDATORY_BEFORE_EFFECT` class 是否由 08 耐久表达、以及 AUD-L2（send 后 crash/restart 的 audit lifecycle 修复）都**未证明**。

## A47

这个窗口分两个方向。方向一：audit proof 已经提交，但 Security 或 Sandbox 在 send 前明确阻断——这时 Tool 先留下 `NOT_DISPATCHED / NO_EFFECT`，audit row 再进 `dispatch_aborted` 释放 capacity，**不会**伪装成 `effect_observed`。这是 AUD-L1，已经 verified。方向二：effect 已经发出但 audit 缺失——这个方向由 fail-closed 关闭（缺 proof 就不发）。收敛责任在 06 的 gateway 生命周期状态；但要注意，**crash / restart 场景属于 AUD-L2，尚未实现证明**。

第二层：

- AUD-L1：`_mark_mandatory_audit_dispatch_aborted` — `invocation_gateway.py:1551`（调用点 :487、:529）；对应 `_mark_mandatory_audit_effect_observed`（:1529）。
- 测试 `test_post_audit_security_abort_releases_capacity_without_observed_effect`（`tests/security/test_mandatory_audit_postgres_boundary.py:1083`）、`mandatory_audit_observed_cannot_abort`。
- 证据：`docs/evidence/README.md`「MANDATORY AUDIT PRE-SEND ABORT: AUD-L1 SELECTED VERIFIED / REVISION 20260920_60」；「AUD-L2 NOT IMPLEMENTATION-PROVEN」。
- 06 的 drain 语义：只有能证明没发出去或已经完成，Attempt/Effect 语义才够用；未知时保持 unknown。

- `事实层`: Current（AUD-L1）/ Gap（AUD-L2）
- `证据`: 上述 file:line 与 evidence 行
- `边界`: 我把「pre-send abort 已闭环」和「crash/restart lifecycle 未闭环」分开说，不合并成「audit lifecycle 已解决」。

## A48

对外呈现的是 `UNKNOWN_EFFECT`：一条耐久的 `ToolExecutionReceipt`（`status=UNKNOWN`、`effect_certainty=UNKNOWN_EFFECT`）加一条 `OPEN` 的对账记录，gateway 返回 `reconcile_required`。能不能继续走下一步——**不能对同类副作用继续**。设计上 Run 应该停在等待对账；但要如实说，Target 里那个状态叫 `WAITING_RECONCILIATION`，今天的 `src/` 里没有这个字面状态，代码是返回一张 `reconcile_required` 的 receipt。

第二层：

- 落地表示：`invocation_gateway.py:539-549`（receipt UNKNOWN/DISPATCHED/UNKNOWN_EFFECT），`:550-574`（对账行 OPEN/RECONCILE + `provider_effect_id` + `reconciliation_query`），`:581-587`（返回 `ToolGatewayReceipt("reconcile_required", ..., "UNKNOWN_EFFECT_RECONCILIATION_REQUIRED")`）。
- 不变量：`Outcome Unknown 不得映射为普通 Failed，也不得 Blind Retry`；`known-not-executed 与 outcome-unknown 必须分开`。
- 重启行为：`tests/capability/test_tool_effect_postgres_boundary.py:222` `test_unknown_external_effect_stays_reconcile_required_after_runtime_restart`。

- `事实层`: Current（表示与重启保留）/ Target（运行状态名）
- `证据`: 上述 file:line；`docs/evidence/README.md`「UNKNOWN EFFECT RESTART REPLAY: FIX VERIFIED / UNKNOWN PRESERVED」
- `边界`: 「Run 停在 WAITING_RECONCILIATION」是 Target 状态机表述；src-wide grep 找不到该字面量，我不说它已经在代码里存在。

## A49

对账由 06 拥有。多久做一次：当前**没有后台 reconciler**，也不会按时间阈值去猜远端真值；一条 `OPEN` reconciliation 到 age 阈值（gateway 里是 900 秒）后 escalate 成 `MANUAL_ASSESSMENT`，再由授权 reviewer 记一条**一次性**结论，最后 `resolve_effect_reconciliation` 收敛成 EffectReceipt / `RESOLVED`。所以自动 vs 人工的答案是：自动的远端查询目前 `DEFERRED_BY_PROVIDER_CAPABILITY`，**当前是人工结论兜底**。

第二层：

- escalate：`platform/database/tool_runtime/domain.py:1188` `escalate_due_reconciliations`（置 `ESCALATED / MANUAL_ASSESSMENT`，`manual_assessment_required=true`）；阈值 `age_escalation_after_seconds=900`（`invocation_gateway.py:564`）。
- 人工判断规则：`record_manual_effect_assessment` — `domain.py:1577`，要求授权 reviewer principal、要求已存在 reconciliation、provider-effect identity 必须匹配、要求已 escalate；exact replay 幂等，第二条不同结论 fail closed。
- 收敛：`resolve_effect_reconciliation` — `domain.py:1028`，只接受 conclusiveness，写结论性 EffectReceipt 并置 `RESOLVED`；不同第二结论抛 `ToolRuntimeConflict`。
- 决策记录：`docs/governance/effect-remote-query-reconciliation-status.md`（`DEFERRED_BY_PROVIDER_CAPABILITY / MANUAL_CONCLUSIVE_FALLBACK_CURRENT`）。

- `事实层`: Current（人工兜底）/ Target（自动 query）/ Deferred
- `证据`: 上述 file:line；`docs/governance/effect-remote-query-reconciliation-status.md`；`docs/governance/aud-l1-implementation-status.md:43`「当前没有 background reconciler」
- `边界`: reviewer 的 role / tenant / approval-policy authoritative binding 还没证明；「一次判断是否够」也未被真实人工工作流证明。

## A50

谁是真值：**远端现实**。本地记录只是「我们目前能证明什么」。系统避免骗自己的方式是拒绝一切替代品——HTTP 2xx、transport success、ToolAttempt 终态、Checkpoint，全都不算 Effect truth，只有 `EffectReceipt` 或结论性的 `ReconciliationReceipt` 才算；transport timeout 一律映射成 UNKNOWN，而不是 Failed。所以「怎么发现自己在骗自己」的答案是：它不允许自己用最容易得到的那个 success 去替代相邻 Owner 的完成证明；如果连可信的远端查询能力都没有，它就停住并把结论升级到人工，而不是猜——这正是 remote-query reconciliation 今天被 Defer 的原因。

第二层：

- 完成证明 / 非证明：`docs/architecture/reference.md` B6——「外部动作是否发生 = EffectReceipt or conclusive ReconciliationReceipt；非证明 = HTTP timeout、transport success、ToolAttempt terminal state alone」。
- 不变量：「Transport Success 不等于 Effect Success」；「跨远端系统默认不使用 2PC」；「ToolAttempt 完成不能证明 Effect」。
- 现实已经改变、本地还是旧的情况下，收编未知事实是被禁止的：`docs/modules/effects/README.md`「即使 06 已经证明发送成功，外围 Host 是否最终采纳、展示或进入它自己的业务流程，仍属于外部系统能够证明的范围，Zuno 不把未知事实收编成本地状态」。

- `事实层`: Target（authority）/ Current（fail-closed 与人工兜底已实现的部分）
- `证据`: `docs/architecture/reference.md` B6；`docs/modules/effects/reference.md` B1；`docs/governance/effect-remote-query-reconciliation-status.md` §Non-goals
- `边界`: 这是「设计上不允许自我欺骗」；不等于「我们已经能自动发现远端漂移」——自动查询是 Deferred，多数现实漂移今天要靠人工对账或外围系统回执发现。

## A51

加入的时候系统已经存在，不是空仓库起步。我能确认的是：已经有一版代码，还有一个比较简单的自研前端，所以是 Brownfield。但这条有个很硬的取证边界——本仓库公开根提交 `eafeb1c2` 是 2026-04-15，而这个日期和我能自证的第一笔改动 `77346758` 是同一天。也就是说，公开 Git 历史里根本没有「我加入时就已经有一个能跑通 Tool Calling 的版本」这句话的证据。我唯一能间接看到的 before 状态，是 `77346758` 的父提交：那时 `GeneralAgent` 已经带着一套能工作的嵌套 Tool Calling（MCP 走 `MCPAgent`、skill 走 `SkillAgent`），那套不是我写的。所以「已经有东西在跑」这件事，我靠的是父提交的代码，不是作者字段。

第二层：

- 项目口径：`greenfield: false`；加入时已有代码 + 简单自研前端（`docs/project/reference.md`「Historical baseline」）。
- 取证限制：公开根提交与个人第一笔改动同日；2161 个 commit 里作者字段区分不出「我」与「团队」。
- 我能看到的最早 before 状态就是 `77346758` 的父提交。

- `事实层`: Historical
- `证据`: `docs/project/README.md`「加入项目时，系统已经存在」；`docs/project/reference.md`「Historical baseline」；PF-007 / PF-008；根提交 `eafeb1c2dfe9fbb70e4e2fc1f89b687e37f3dc8d`
- `边界`: 「四月那版当时是不是 Production、历史技术栈完整是什么」都是 Unknown；我只能说它已经存在、且有一版前端。

## A52

我能自证的第一笔是 `77346758`（2026-04-15）：删掉 `core/agents/mcp_agent.py` 和 `core/agents/skill_agent.py` 两个包装 Agent，把真实 MCP tools 和 skill guidance 直接绑到同一个 `GeneralAgent`，配置注入从子 Agent 挪回主 Agent 的 tool-call middleware。为什么说它「能自证」——它是一个单主题、自洽的提交：删两个文件、改写 `general_agent.py`、移掉 `tool_invocation_model` / `available_tools` / `LLMToolSelectorMiddleware` 这一整套延后选工具的脚手架。至于「第一」这个字我得改：它和公开根提交同日，所以它是「我账号下能自证的最早一笔」，不是「仓库历史上的第一笔改动」。

第二层：

- 可自证靠的是提交内容与范围，不是作者字段（作者字段不可信，见 `docs/project/README.md`「Commit 历史不能单独证明个人 Ownership」）。
- 这个提交没有关联 PR、Review 或历史 status check。
- 所以措辞一律是「这是我能自证的一笔」。

- `事实层`: Historical / Personal Ownership（受限）
- `证据`: `773467580ee428a0536c7f594c0847c1510879ac`；PF-032
- `边界`: 同日于根提交，不能声称「项目历史第一笔」；也不能证明它是独立 PR。

## A53

「重构之前是谁写的」我答不了——作者字段区分不出人和团队，这一段我只能说它是我接手时的现状。为什么需要动它，我能从技术侧讲清楚：父版本把一整个 MCP Server 包成一个不透明 tool，主 Agent 只能选到「某个 server」，再进第二层模型的 ReAct 去选真正要调的工具，配置和身份都必须跨层带下去。这不是「谁写错了」，是这个抽象的代价。但要注意，**组织上为什么让我来重构、原来那位是不是还在做，我没有证据**，不能替团队补一段动机。

第二层：

- 原实现的三个代价：工具选择质量下降（模型看不见 server 内 schema）、一次请求两次模型往返、身份/配置跨层维护。
- 最简方案：删掉包装层，主 Agent 直接绑具体 tools，注入点跟着 tool 走。
- 「动因」我能给的只是技术动因；产品/组织动因 = Unknown。

- `事实层`: Historical（技术机制）/ Unknown（组织动因）
- `证据`: `77346758` 及其父提交 `mcp_agent.py` / `skill_agent.py`；PF-032
- `边界`: 不按常识猜「原作者离职/调岗」这类团队叙事。

## A54

这条我必须分开说，否则就是造假。**能算我个人 slice 的**：Tool/MCP 那段（`77346758` 的单 Agent 重构、`0b5fb350` 上 Workspace direct-route / custom MCP 递归 / 高德天气抽取那几条）、GraphRAG retrieval quality 那条 fix chain（`7928df50` → `3da5d742`）、Context/Memory V2 那条链（`13dd929`…`3d865e1`，到 PR #8 的 `f3c7433`）。**不能算我的**：今天 `docs/modules/` 里那套 LangGraph 图结构、九模块 Runtime、以及平台级的 PostgreSQL schema 与迁移——那些是后来团队系统化整理的总体目标架构，不是 2026 年 3 月我加入时的历史成果。数据库我只是进库查过、调过实际数据，不拥有 schema 设计。

第二层：

- 个人可自证切片：Tool/MCP（PF-032）、GraphRAG（PF-031）、Context/Memory V2（PF-029 / PF-030）。
- 非个人：总体 Target Architecture、九模块、ADR、平台 DB schema / Migration（PF-013 只到「查过库」）。
- 我不用作者字段证明「哪些模块是我写的」。

- `事实层`: Historical / Personal Ownership（受限）
- `证据`: PF-013 / PF-029 / PF-030 / PF-031 / PF-032；`docs/project/README.md`「团队与个人参与的边界」
- `边界`: 任何「整块是我写的」都不成立；我只能给 bounded slice。

## A55

`ContextOrchestrator` 是代码里真实存在的组件，不是我为了描述工作编的名字——它在 `src/backend/zuno/platform/services/application/context/orchestrator.py:115`，旁边还有 `RecentWindowSelector`。但它今天有一个我必须主动说的地位问题：**它在 `src/` 里没有生产调用点**。真实的调用前读取路径不是走它，而是走 `agent/runtime/nodes/core.py` 的 build_context 节点，去调 `deps.memory_engine.build_context_pack(scope=…)`。所以诚实说法是：它是真实的 typed contract 入口与已落地的最小实现，但它今天不是 live path。

第二层：

- 定义处：`platform/services/application/context/orchestrator.py:115`（`__all__` 在 :190）。
- 其他出现都只是 re-export shim（`agent/context.py`、`agent/__init__.py`、包 `__init__`），没有业务调用。
- 真实路径：`agent/runtime/nodes/core.py:64` `hasattr(memory_engine, "build_context_pack")` → `:79` `build_context_pack(...)`；实现在 `memory/engine.py:645`。

- `事实层`: Current（组件存在）/ 边界（无生产调用点）
- `证据`: `orchestrator.py:115`；`core.py:64/79`；`engine.py:645`
- `边界`: 我不把它包装成「上下文统一的运行时入口」；今天的真值入口是 `build_context_pack`。

## A56

我拿不出证据说这条边界是产品、Leader 还是我自己定的——仓库里没有对应决策记录。当前能说清的是**它今天长什么样**：判据是规则，不是模型。`_detect_route_hint` 用正则加关键词表判意图，`_plan_kind_for` 用 token match 决定 `simple` / `complex`；`complex` 需要一个注入的 DAG planner，而产品组合里装的是 `None`，所以复杂请求今天 fail closed。至于「谁拥有最终解释权」——严格讲今天解释权落在代码里的这几张表和这个注入点，落在一个还没有 owner 文档的规则集合上。

第二层：

- 判据实现：`simple_agent.py:2743`（`_detect_route_hint`）、`:2150`（`_plan_kind_for`）、`:2159`（`_resolve_governed_tool`）。
- `complex` 缺 planner → `DYNAMIC_PLAN_RUNTIME_NOT_BOUND`（`single_controller_runtime.py:497-501`）；产品装配见 `main.py:113`。
- 决策 owner = Unknown（`docs/decisions/` 里没有 direct-route 准入的 ADR）。

- `事实层`: Current（实现）/ Unknown（决策归属）
- `证据`: 上述 file:line；`docs/decisions/` 目录
- `边界`: 不替我或团队补一段「这是产品定的」的话。

## A57

不是「之前就有 CI 在跑」。那批 direct-route 断言是**随 `0b5fb350`（2026-04-28）这轮改动一起新增的**，而且当前 GitHub 历史没有恢复这两个 SHA 的 PR-triggered Actions run，combined commit status 里也没有 recorded status check。所以严格说法是「测试 artifact 存在、作者当时锁定了哪些失败条件」，**不能写「历史 CI 已通过」**。今天确实有一个选定的 main run（`35516807526`，224 passed），但那是当前快照的验证，不是 2026 年 4 月那批测试当时的执行记录。

第二层：

- 新增的断言示例：`test_canonical_mcp_target_handles_custom_server_name_without_recursion`、`test_mcp_without_user_config_is_treated_as_platform_ready`、天气参数抽取。
- 没有恢复的：那批 SHA 的 CI run / status check。
- 当前：`SELECTED GITHUB RUN: 35516807526 / 224 passed`。

- `事实层`: Historical（新增）/ Current（今天的 run）
- `证据`: PF-032 的「不能写历史 CI 已通过」边界；`docs/evidence/README.md` 当前 run 行
- `边界`: 我用「test artifact exists」而不是「测试当时在 CI 跑过」。

## A58

如果一定要挑一个最代表这段工作的 diff，我会挑 `77346758`：它是单主题、边界干净、前后差异能在父提交里直接读出来的那一笔。`0b5fb350` 虽然含 direct-route 和 custom MCP 递归这些我认的内容，但它是个跨工具、Knowledge、模型、Docker、脚本的大提交，**整个 commit 不能算成我的**，只能从里面安全提取几条有明确前后差异和测试的路径。Context/Memory 那段最干净的是 PR #8（`f3c7433`）——单实现提交。所以要回答「独立 PR 还是混在一起」：有独立 PR 的只有 Memory 那段；Tool/MCP 的两笔都不是我能自证的独立 PR。

第二层：

- 最干净：`77346758`（单主题重构）。
- 混合大提交：`0b5fb350`（可安全提取子集，不能整包认领）。
- 独立 PR：`f3c7433`（PR #8，单实现提交）。
- `3da5d742` 等是一串连续 fix commits，不是单个 PR。

- `事实层`: Historical / Personal Ownership（受限）
- `证据`: 上述 SHA；PF-031 / PF-032
- `边界`: 我不把 `0b5fb35` 整笔算成 Tool Calling 个人任务。

## A59

这条我只能说不知道。我能确认的是项目进入过法院侧人员测试和 Pilot Validation（PF-018 / PF-019），但**测试题数量、参与法院、人员角色、参考答案、Reviewer protocol、环境与性能数据都还没恢复**，我本人在其中到底是写代码、配环境还是现场看别人跑，我没有可复核的记录能证明。所以我不说「我在法院现场做了 X」——那会是把「项目经历过」扩写成「我做过」。

第二层：

- 已确认：court-side testing / Pilot Validation 作为项目阶段存在。
- 未恢复：我个人的参与层级（编码 / 环境 / 现场）。
- 当前证据里 `COURT QA: UNKNOWN / NOT AVAILABLE`。

- `事实层`: Historical（项目阶段）/ Unknown（个人参与深度）
- `证据`: PF-018 / PF-019；`docs/project/reference.md`「historical milestones」；`docs/evidence/README.md`
- `边界`: 个人参与深度 = Unknown，不用项目阶段反推。

## A60

我给不出「是法院的人拿真实案子在用，还是我们演示他们在旁边看」这个判定。能确认的只是项目经历过 court-side testing 和 Pilot Validation 两个阶段，以及 Pilot Validation **不等于 Production**。到底是「真实使用」还是「演示 + 旁观」，需要 Pilot 环境、参与人、运行记录，这些今天都没有恢复；所以我不会为了答案好看把它说成「法院在用真实案件」。

第二层：

- 已确认：court-side testing 比内部 Demo 更接近真实工作环境。
- 未恢复：使用方式（自用 / 演示 / 旁观）、Task Class、角色。
- 明确禁写：Production、稳定用户规模、部署 Endpoint。

- `事实层`: Historical（阶段）/ Unknown（使用方式）
- `证据`: PF-018 / PF-019；`docs/project/README.md`「项目真实走过的阶段」
- `边界`: Pilot 的定义边界到此为止，不升级成「真实生产使用」。

## A61

没有。跑多少条 case、持续多少天、有没有日志表格邮件——这些我一个都拿不出来。历史性能指标（QPS / Latency / Token / Cost / HA / DR）在台账里就是 UNKNOWN，Pilot 的用户量、时长、验收材料也都未恢复。所以这条的诚实答案只有一个：Unknown，而且我不拿今天的 benchmark 或本机运行去反推当时。

第二层：

- PF-022（历史性能指标）= UNKNOWN。
- Pilot 最值得恢复的是任务类型、使用方式、失败、人工兜底、验收条件——这些尚未恢复。
- 恢复路径写在 PF 台账「未来可升级证据」列。

- `事实层`: Unknown
- `证据`: PF-019 / PF-022；`docs/governance/project-fact-provenance.md` §7
- `边界`: 不编样本数、天数、记录载体。

## A62

这个边界不是某个人拍的，它是**取证边界**：简历写「内部 Demo、法院侧测试与 Pilot Validation」而不写 Production，是因为 PF-020 明确写着 Production 是 `NO EVIDENCE / NOT ESTABLISHED`——没有生产 Endpoint、部署证明、SLA、运维监控、正式验收。所以与其说是「谁定了边界」，不如说是「证据只支持到 Pilot 为止」。我不会替它安一个「合规考虑」或「领导决定」的动机，那两个都没有材料。

第二层：

- PF-020：不能把历史项目描述成正式生产系统。
- PF-015 / 016 / 018 / 019 分别只支持 Internal Demo / 客户侧 Demo / Court-side Testing / Pilot Validation。
- 边界表述统一由 `docs/governance/project-fact-provenance.md` 维护。

- `事实层`: Historical（边界结论）/ Unknown（若有人为决策，其内容不可考）
- `证据`: PF-015 / PF-016 / PF-018 / PF-019 / PF-020
- `边界`: 不给这个边界补一个不存在的人为动机。

## A63

没有可复核的现场 case。我没有恢复出「我以为对、当场跑错」的那次具体记录——PF-017 只确认客户反馈过「回答质量还需要提高」，但没有恢复完整的 Bad Case、根因或前后指标。这里我要特别防一个串味：今天 `docs/evidence/` 里确实有真实负向故障（比如 PR #201 的 restart replay 误升级、PR #205 的缺 audit proof 仍 dispatch），但**那些是当前 CI 里的 fault probe，不是法院现场**，不能拿它们当「法院那次错在哪」。

第二层：

- PF-017：根因未被证明一定是 RAG / Prompt / Memory / Model 中某一项。
- 当前负向证据（#201 / #205）属于 Current fault probe，与法院现场无证据关联。
- 现场 bad case 表现 = Unknown。

- `事实层`: Historical（反馈存在）/ Unknown（具体 bad case）
- `证据`: PF-017；`docs/evidence/README.md`（#201 / #205 描述）
- `边界`: 不用当前 fault probe 冒充历史现场事故。

## A64

不知道有没有明确判据。我能说的是：**没有任何已恢复的材料写过一个 pass/fail 判据，也没有写它是由谁定的**。所以我会直接说「跑了就算完成、还是有一个门槛」，我没证据，不能替你选一个。项目层现在能保留的说法只有「项目进入过 Pilot Validation」，不能扩成「Pilot 通过了某个验收门槛」。

第二层：

- 已确认：Pilot Validation 是一个真实阶段。
- 未恢复：验收条件、判据、判定人。
- 禁止：把 Pilot 写成「已通过验收」。

- `事实层`: Unknown
- `证据`: PF-019；`docs/project/README.md`「Pilot Validation 仍属于试点」
- `边界`: 判据与判定人 = Unknown，不编门槛。

## A65

卡点在哪我没有证据，只能说不确定——模型质量、合规、法院内部流程、还是没人接手，这四个我一个都不能选。台账在这条上给的升级证据是「Pilot 环境、用户、时长、验收材料」，这些都没恢复。我能说清的只有一层逻辑：Pilot Validation 本身不等于 Production，至于为什么没进 Production，当前材料不足以归因。

第二层：

- PF-019 / PF-020：Pilot ≠ Production。
- 未恢复：未落地的真实原因。
- 禁止：把「没进 Production」归因到某一个技术或组织原因。

- `事实层`: Unknown
- `证据`: PF-019 / PF-020；`docs/governance/project-fact-provenance.md` §7
- `边界`: 不给未落地原因做任何单因归因。

## A66

不知道它今天还在不在法院环境里跑。当前证据的收口就是一行：`COURT QA: UNKNOWN / NOT AVAILABLE`——既没有「还在跑」的证据，也没有「已停机 / 已回滚」的证据。所以我不说它已经停机，也不说它还在运行，就停在 Unknown。

第二层：

- `docs/evidence/README.md` 边界块：`COURT QA: UNKNOWN / NOT AVAILABLE`。
- 没有可复核的法院环境运行记录、Endpoint 或运维证据。
- Pilot 是历史阶段，不自动成为今天 main 的 Current runtime evidence。

- `事实层`: Unknown
- `证据`: `docs/evidence/README.md`；PF-020
- `边界`: 不猜「已停机」或「在运行」。

## A67

没测过。今天这条 GraphRAG 检索链的形态是明显往英文问答数据集调的：`entity_alias.py` 的通用实体名单是 `Introduction / Overview / High / Low` 这类英文词，fusion 和 retriever 里那一堆关系线索表（`founded by`、`maternal grandfather`、`director of`）也是英文；评测是 HotpotQA distractor。换成一类真实卷宗——中文、多主体、带括号简称的法律材料——我没有跑过，也不会声称它还能用。而且按我在别名归一化那条的结论（去掉括号后缀、无实体词典、无层级），它在中文法律主体上不只是「没测」，是有已知的误合并风险。

第二层：

- 面向英文问答的证据：`entity_alias.py` 的 `GENERIC_ENTITIES`、`fusion.py` 的 `BRIDGE_RELATION_CUES` / `GENEALOGY_RELATION_CUES`、HotpotQA 评测。
- 中文法律语料：无测试用例、无 holdout。
- 与 A24 一致：误合并风险是推理判断，不是已测结论。

- `事实层`: Current（面向英文）/ Unknown（中文法律泛化）
- `证据`: `graphrag/entity_alias.py:10-22`；`retrieval/fusion.py:36-55`；`tools/evals/zuno/multihop_eval`
- `边界`: 泛化能力 = 未测，不声称可用。

## A68

我不会第一步把整层 GraphRAG 删掉，但我也不会说它「已经证明了价值」。原因是：观测到的失败是**融合层的排名位移**——graph 候选把 baseline 已命中的 gold 挤出了 top5——不是「graph 路由没用」。所以第一步该动的是那条 baseline-preserving 融合，而不是整个图路由。至于「删掉之后哪个 query 会明确变差」——这正是我要如实说的地方：**我举不出一个会因为删掉图路由而变差的 query**。audit 只记录了被挤出的（`Ed Wood`、`Shirley Temple`），没有记录任何「baseline 漏、graph 补上」的 case；seed expansion 和 path ranking 是后来加的，没有 ablation。所以「找不出受益 query」这件事本身，就是这层该被 ablation 优先审的论据。

第二层：

- 观测失败的根因：ranking displacement，不是 graph route 未激活。
- 被挤出的两条 regression question id：`5a8b57f2…` / `5a8c7595…`。
- 没有任何已落盘的「graph 补回 gold」case。
- 判定这层的规则在冻结协议里：holdout 上无稳定增量就删。

- `事实层`: Historical（失败形态）/ Open Design（删除判断）
- `证据`: `7928df50e9b5f3035e576fa4ed47eaf31c93cc78`；`docs/governance/rb019-graphrag-ablation-protocol.md` §2/§3
- `边界`: 我给的是「该优先被审」而不是「今天已经该删」；也没有一个「删了就变差」的 query 可指。

## A69

因为把图权重调到 0 就是「把 graph route 整个关掉」，那正是 ablation 里 `full-minus-H1` 的一个臂；我写融合是为了修一个更窄的问题——不是「graph 太弱」，而是「graph 候选跳到了 baseline gold 上面」。要让权重低到永远不挤掉 baseline gold，本质上就等于把「baseline rank 是下限」写死，而这层融合做的就是把这个下限显式、可检查地表达出来，还顺手保留 graph 的分层晋升。但我要把话反过来讲清楚：如果 holdout 测下来 graph 路由在它声称擅长的 query class 上打不过更简单的 baseline，那「权重 0 / 删掉」就是更简单也更正确的答案，这层融合就没有存在理由。它存在是因为我当时在修一个已观测的回归，不是因为我已经证明 graph 加了价值。

第二层：

- 更简单方案：`GRAPH_PROMOTION_THRESHOLD` 失效 / 短路 `_graph_rank_adjustment`（协议里 H1 的关闭方式）。
- 融合层实际做的事：`_rank_key` 把 `baseline_rank = min(vector_rank, bm25_rank)` 当下限，`candidate_group` 做分层，`fusion_score` 只进 metadata 不参与排序。
- 两者在测量上等价于同一个 ablation 的两臂。

- `事实层`: Open Design / Fundamental（更简单方案为何不够，以及何时够）
- `证据`: `fusion.py:9,166-224,951-977`；协议 §3 H1
- `边界`: 我不说「融合一定比权重更优」；这是可被 holdout 推翻的设计判断。

## A70

按 `where user_id=? and project_id=?` 查一张表，会在一类场景上不够：**同一 user + 同一 project 下，不同 thread / 不同 agent 的内存会互相读回**。scope 是四维的 `user_id / agent_id / project_id / thread_id`，两个 thread 的 task summary 用二维过滤是分不开的，会串。但这条我要跟 A29 保持一致、不夸大：数据库层确实就是四列 `WHERE`，多出来的并不是更花哨的谓词，而是三条语义——(1) scope 是读写/合并/回溯统一用的身份；(2) `scope 相等 ≠ 授权`，能不能召回是 08 的事；(3) 每个 item 必须带 source trace，provenance 不等于真值。另外要主动说：runtime 侧 `agent_id` 今天硬编码成 `"agent_run"`，所以 agent 这一维其实没被真正用起来。

第二层：

- `MemoryScope`：`platform/services/memory/layers.py:43-55`；DB `_scope_select()`：`memory/store.py:520-526`（四列 AND）。
- 硬编码：`agent/runtime/nodes/core.py:485-491` `agent_id` = `"agent_run"`。
- 语义边界：模块 reference「MemoryScope equality != Authorization」。
- 结论：够不够取决于你要不要再要 thread 隔离 + eligibility + provenance，不是取决于 SQL 复杂度。

- `事实层`: Target（语义）/ Current（实现）
- `证据`: `layers.py:43-55`；`store.py:520-526`；`core.py:485-491`；`docs/modules/reference.md`
- `边界`: 「scope equality ≠ authorization」这层今天在代码里没有独立 08 门；生效的是 scope + APPROVED 过滤，不粉饰成已实现。

## A71

今天删掉它，生产路径上不损失任何东西——因为它今天就不在 live path 上，真实调用前读取走的是 `build_context` 节点 → `build_context_pack(scope=…)`。所以「多出来的这层抽象带来什么」的诚实回答是：今天带来的是一个 typed contract 入口（`ContextSource` / `ContextItem` / `ContextPackPolicy`，加一个 `RecentWindowSelector`），而不是一个被消费的运行时入口。如果今天重做，我会先测一件事：`build_context_pack` 是不是已经覆盖了它声称要做的事；如果是，就删掉 `ContextOrchestrator`、把 contract 直接挂到真实入口上，而不是留一个没有 consumer 的统一入口。

第二层：

- 定义：`orchestrator.py:115`，contract 在 `context/contracts.py:10/33/49`。
- 无生产调用点：`src/` 内除自身与 re-export shim 外无业务引用。
- 真实入口：`core.py:64/79`。

- `事实层`: Current（存在）/ Open Design（该不该留）
- `证据`: `orchestrator.py:115`；`context/contracts.py`；`core.py:64/79`
- `边界`: 我不硬撑「统一入口」的必要性；它今天是一个待验证、可能该删的抽象。

## A72

如果只问「数据形状」，一个普通 Pydantic model 就够了，不需要自研 contract 体系；LangGraph 的 state/channel 更不够——它是运行期内部状态，明确是非权威的（checkpoint 不等于 Domain fact）。所以这层 typed contract 的价值不在容器，而在它编码的不变量：哪些字段只是 provenance、哪些是候选、哪些才是正式事实，以及 scope 语义。一个 Pydantic model 能表达字段，但不会替你守住「source id 不等于 truth、不等于 authorization、也不等于压缩没丢语义」这几条。我的判断是：容器可以退化成 Pydantic，但那些不变量必须留在某个 typed 边界上，否则它们会散回注释里。

第二层：

- 相关 contract：`context/contracts.py`（`ContextSource` / `ContextItem` / `ContextPackPolicy`）、`memory/layers.py`（`MemoryScope` / `ReviewStatus`）。
- 框架边界：`agent/runtime/graph.py:17-19` 注释明确「checkpointer … the Agent Run store remains the source of truth」。
- 不变量：`Provenance != Truth != Authorization != Semantic Preservation`。

- `事实层`: Open Design / Build-vs-Extend
- `证据`: `context/contracts.py`；`graph.py:17-19`；`docs/modules/reference.md`
- `边界`: 我不说「自研 contract 比 Pydantic 强」；形状层面它们等价。

## A73

三个里我挑**实体别名归一化**最该删，收益也最不确定。理由有两条：一是它在 HotpotQA 上救的主要是 `(novel)` 这类括号/大小写差异，而英文样本里这种形态本来就稀疏；二是它在中文法律主体上不是「收益不确定」，是带着已知的误合并风险（去括号后缀、无实体词典、无层级，见 A24）。而且它和其它两个不一样——它和任何一个**已观测到的失败**都没有直接因果。但我要标明这是判断，不是测量：真值要等 ablation 里 H8 那一臂。

第二层：

- H8：`graphrag/entity_alias.py:resolve_alias`，关闭方式 = 严格字面匹配。
- 观测收益：无；观测失败：无（英文样本上没记录到它引发的错）。
- 风险：中文法律主体误合并 = 推理判断，未测。

- `事实层`: Open Design / 预测
- `证据`: `entity_alias.py:25-61`；协议 §3 H8；A24
- `边界`: 明确是预测排序，不是数据结论。

## A74

只能留一个的话，我留 **candidate-aware seed expansion**。因为在这三个里，它最直接服务多跳本身——它把 baseline top5 候选的 title / file_name 也变成 seed，把「第一跳找到的东西」喂给图去走第二跳；另外两个（别名归一化、path-aware ranking）更像是给图路径打分时的精度修饰。删别名归一化的代价：英文上我预期接近零，中文上反而降低误合并风险，所以「代价」主要是失去它对括号变体的覆盖。删 path-aware ranking 的代价：可能丢掉 comparison / bridge 类的路径优势，但那恰恰是没被证明的一截。两个代价今天都**没有测量支撑**——这就是我唯一能诚实说的。

第二层：

- 保留：H7 seed expansion（`retriever.py:_build_seed_entities_with_source`）。
- 删除：H8 别名归一化 + H9 path-aware ranking。
- 代价 = 未测量；协议 §3 里对应可关闭开关。

- `事实层`: Open Design / 预测
- `证据`: 协议 §3 H7/H8/H9；`retriever.py:290-376`
- `边界`: 明确这是减法优先级建议，不是消融结果。

## A75

传输层、工具发现、协议连接本来就该 Buy——成熟 MCP Host / SDK 负责把工具暴露出来、把调用发出去。Zuno 真正非自己做不可的 delta 有三件：一是**按用户、按 tool→server 映射注入用户级配置**，并且注入点紧贴 dispatch；二是**单个受治理 Agent 的准入**——什么请求走确定性的单工具直连、什么请求进计划路径；三是后来才有的 Tool Control Plane（PreparedAction / Approval / Idempotency / EffectReceipt），但那不是 4 月这段的工作。要把边界说清：前两件是我这段能自证的，第三件是后续团队更强的语义，不能算进这段。

第二层：

- ADR 0007（reuse-first）：MCP 只提供工具暴露/协议，不拥有授权或现实效果事实。
- 我这段的自研：去包装 + 注参 + 准入（`77346758` / `0b5fb350`）。
- 非我这段：PreparedAction / Approval / Idempotency / EffectReceipt。

- `事实层`: Historical（4 月）/ Target（Build-Buy 口径）
- `证据`: `docs/decisions/0007-reuse-first-provider-boundary.md`；PF-032 末尾边界
- `边界`: 不把后来的 Tool Control Plane 反写成 4 月成果，也不说「Zuno 自研了 MCP 协议」。

## A76

删除条件是**测量条件**，不是故障条件。按已接受口径：如果跨会话 A/B 显示 structured long-term memory 没有稳定边际收益，就关掉它，退回 `Raw Event + task summary + 按需读取 Owner facts`。注意删的是「readback 上这层 review/provenance 约束」所在的 structured long-term memory 这一层，Context 组装保留——它本来就不承担业务 Authority。另外一个次要条件是 review 的实际成本：如果每次读回都要跑人审、吞吐撑不住，那这层也不该硬留。今天这两个条件都没有数据，所以我能说的只是判据。

第二层：

- 判据来源：ADR 0007 §8（memory kill test 阶梯：No long-term memory → Working context only → Typed episodic → +semantic/procedural → External Provider）。
- 指标含 task completion、unsupported claim、stale-memory error、context relevance、human correction、token、latency、cost、scope violation。
- 同规则适用于 GraphRAG / Reflection / Specialist / Native Runtime。

- `事实层`: Target（删除判据）
- `证据`: `docs/decisions/0007-reuse-first-provider-boundary.md` §8；`docs/modules/reference.md`
- `边界`: 这是「什么条件删」，不是「今天该删」；今天没有任何一侧的测量数据。

## A77

设计上的答案是靠 **serving pointer**：一份文档更新会构造新一代 `KnowledgeGeneration`，跑 generation-level 校验（manifest、覆盖、必要 projection 都齐），然后**原子切换 ServingPointer**；查询入口只消费已经验证过的 serving generation，不跟后台写入进度。所以「检索侧切没切到新版」在目标设计里是一条可判定的事实。但我必须说清楚今天的地位：这套 generation lifecycle / 原子 serving switch 属于 03 的 **Target**，当前是 Gap——我没恢复出持久化的 generation + serving activation 的端到端证据，评测本身甚至是进程内临时重建图检索器、跑完就清掉。今天真正在代码里能查的是另一件事：`CitationProvenanceGuard` 会校验 `document_version_id`，版本对不上的引用会被直接拒，所以「用了旧版」至少不会静默地指错。

第二层：

- Target：DocumentVersion refs → processing spec → KnowledgeGeneration → validation → 原子 ServingPointer。
- Gap：`docs/modules/knowledge/README.md` 的 Gap 段明确列了 generation activation、原子 serving switch、跨 Store purge。
- Current 存在的：`knowledge/provenance.py:71` `CitationProvenanceGuard`（doc version / span 校验）；`ingestion/delete_restore.py` 的可见性生命周期。

- `事实层`: Target（切换机制）/ Current（版本校验）/ Gap（端到端）
- `证据`: `docs/modules/knowledge/README.md`；`knowledge/reference.md`「KnowledgeGeneration / Serving Activation」；`knowledge/provenance.py:89-96`
- `边界`: 我不说「已经能可靠判断检索切到新版」；serving 语义未落地。

## A78

今天的诚实答案是：**`KnowledgeGeneration` 在 src 里我没找到对应实现**——它是 03 模块文档里的 Target 概念，不是一个已经在跑的类、表或状态机。我在 `src/` 里搜这个名字是空的。真实存在的是它的邻居：`knowledge/ingestion/contracts.py` 里的 `SourceSpan` / `DocumentProvenance` / `CanonicalDocumentIR` / `TransformLedgerEntry`，以及一条 ingestion runtime；这些是「做派生处理」的 IR 与账本，不是「一代知识」这个版本对象。还有一个容易误认的东西：`knowledge/runtime_batch.py:195` 的 `KnowledgeReadinessEvidence`——它要求凑齐 30 个 requirement id，那是一个**批量取证包装**，不是 `ReadinessDecision`。

第二层：

- 搜索结论：`src/` 内 literal `KnowledgeGeneration` 无命中（空即「搜索范围内未找到」，不等于「永远不存在」）。
- 存在：`ingestion/contracts.py` 的 `SourceSpan`(:53) / `DocumentProvenance`(:144) / `CanonicalDocumentIR`(:152)。
- `knowledge/runtime_batch.py:195/259` `KnowledgeReadinessEvidence`（evidence gate，非运行时概念）。

- `事实层`: Current（IR / 账本）/ Target（KnowledgeGeneration 概念）/ Gap
- `证据`: `knowledge/ingestion/contracts.py`；`knowledge/runtime_batch.py:195`；`docs/modules/knowledge/reference.md`
- `边界`: 不把 ingestion IR 说成 KnowledgeGeneration；也不把「没搜到」泛化成「仓库永远没有」。

## A79

设计上，指向被删文档的 Citation 不应该「悬空」，而应该**不再可服务**：删除走的是可见性生命周期——`visibility_revoked → cleanup_requested → physically_deleted → verified`（还带 restore point 和 legal hold），也就是说先撤可见性、再清物理。读回侧有一道护栏：`CitationProvenanceGuard` 在 `evidence_missing` 时拒（UNSUPPORTED），在 `document_version_mismatch` / `evidence_span_mismatch` 时拒（INVALID_PROVENANCE），在 `visible_scope_refs` 里找不到有效 scope 时拒（SCOPE_DENIED）。所以「有没有一条路径会读到悬空引用」——代码里那条路径是**会读、但会被拒**，不是静默返回。但要如实说：这只是组件级的护栏，端到端的「删除 → 所有 projection 清理 → 读回一致拒绝」没有被证明，knowledge 的 Gap 段明确列了**跨 Store purge** 和**权限撤销后的召回收敛**。

第二层：

- 删除生命周期：`ingestion/delete_restore.py` 的 `DeleteState`（:16-23）与 `DeleteLifecycleReceipt`（:26 起）。
- 引用护栏：`knowledge/provenance.py:83-119`。
- Gap：跨 Store purge、revocation 后召回收敛。

- `事实层`: Current（护栏与删除生命周期）/ Gap（端到端一致性）
- `证据`: `delete_restore.py`；`provenance.py:83-119`；`docs/modules/knowledge/README.md` Gap 段
- `边界`: 我不说「悬空引用已被端到端消除」；只说组件会拒。

## A80

Target 语义是**分层的**，不是单一的阻塞或最终一致：一次 `ReadinessDecision` 是按 task scope + requirements + security 算出来的 `READY / PARTIAL / BLOCKED`，`PARTIAL` 必须带「覆盖了什么、缺了什么」，调用方再决定等待、缩小 scope 还是停。而底层 generation 的切换是**all-or-nothing 的原子切换**：先写 staged manifest，generation-level validation 过了才切 serving pointer，查询入口只读已验证的 generation、不跟后台写入。所以答案是：**对「某一代知识能不能被服务」这个问题，门是阻塞的（校验+原子切换）；对「这个任务现在能不能开始」这个问题，门是任务级、可 PARTIAL 的**。今天这两个都没有落地——现有的是那个 30-requirement 的 evidence 包装，不是运行时 readiness。

第二层：

- Target：`ReadinessDecision`（`knowledge/reference.md` §B14.2 / 生产段），input fingerprint 绑定 DocumentVersion set / generation / scope / requirements / security。
- 原子切换：`knowledge/README.md:69`（staged manifest → validated generation → 原子切 ServingPointer）。
- Gap：真实多版本 readiness、generation activation 未验证。

- `事实层`: Target（语义）/ Gap（实现）
- `证据`: `docs/modules/knowledge/README.md:25/69`；`knowledge/reference.md` §B14.2
- `边界`: 不说「今天已经有 readiness 门」；现有 `KnowledgeReadinessEvidence` 只是取证包装。

## A81

代码里 Citation 存的是 **`document_version_id` + `source_span_id`** 两个稳定身份，不是任意字符区间。`_source_span_id` 的取值顺序是 `source_span_id` → `span_id` → `chunk_id` → `block_id`；如果这些都没有，就退化成对 `source_span` 映射做一次规范 JSON 的 sha256（取前 24 位）当 span id。所以粒度是「chunk / block 级的稳定 span」，字符偏移不是主要表达方式。原文被改之后还指不指得准——护栏的答案是**宁可拒绝也不指错**：候选和 lineage 的 `document_version_id` 不一致、或 `source_span_id` 对不上，都会 REJECT（`document_version_mismatch` / `evidence_span_mismatch`），而不是让引用悄悄漂到新位置。

第二层：

- `CitationCandidate`（`provenance.py:24-32`）：`claim_id / evidence_id / document_version_id / source_span_id / citation_id`。
- span id 解析：`provenance.py:238-254`。
- 版本/span 校验：`provenance.py:89-96`。

- `事实层`: Current
- `证据`: `knowledge/provenance.py:24-32,89-96,238-254`
- `边界`: 这是「拒得掉」；不等于「能跨版本把引用定位回同一处」——跨版本重定位今天没有机制。

## A82

我的回答是：**用 Top-K 证不了「全案没有」**，这一点架构文档讲得很硬——Retriever 找到若干片段，只能证明这次查询看到了这些内容，不能证明关键材料没有遗漏。要证「没有」，设计上需要的是 `ReadinessDecision` 的覆盖语义（这个任务要求的材料范围有没有被覆盖齐）+ negative evidence（把「检索不到」表达成一个有覆盖前提的结论）。而这两件里，**negative evidence 条件在 knowledge 的 Gap 清单里**，还没落地。今天能做的只有一半：检索链会记 `zero-evidence`，agentic 循环里也有一个 `no_evidence` 停止原因进 evidence ledger——它能说「这条查询零命中」，但那是「我没检索到」，不是「全案没有」。所以面对用户，我只能说「当前范围内未检索到」，不能说「确实没有」。

第二层：

- 观测项：`knowledge/reference.md:235` 检索链至少观测 `zero-evidence`。
- 代码：`knowledge/agentic/evidence_ledger.py:66` `stop_reasons.append("no_evidence")`；`agentic/corrective.py:28`。
- Gap：`knowledge/README.md:99` 明确「negative evidence 条件」仍待验证。

- `事实层`: Target（覆盖语义）/ Current（zero-evidence）/ Gap
- `证据`: `docs/modules/knowledge/README.md:99`；`knowledge/reference.md:235`；`evidence_ledger.py:66`
- `边界`: 我不把 zero-evidence 说成「证明了全案没有」。

## A83

`5` 在我这条链里有两个来源，都不是「调出来的最优 K」。第一，HotpotQA smoke 的 `5` 是命令行 `--limit 5` 的**样本条数**，是 `all_questions[:5]` 截出来的前 5 条，不是按 query class 挑的；评测 runner 的 `top_k` 默认其实是 10，`rerank_top_k` 默认 `min(top_k, 5)`。第二，`rerank_top_k = 5` 是 profile 里的一个默认值。所以「为什么偏偏是 5」——我没有任何调参加据能回答，`limit=5` 是 smoke 的规模，`rerank 5` 是默认值，两者都不是被优化选出来的。

第二层：

- runner：`tools/evals/zuno/multihop_eval/run_real_runtime_eval.py`，`--limit` 默认 10（:562），`top_k` 默认 10（:372）。
- `selected_questions = all_questions[:max(limit,0)]`（:391）。
- `rerank_top_k` = `min(top_k, 5)`（:214）。

- `事实层`: Current（配置来源）/ Unknown（K 的取值理由）
- `证据`: `run_real_runtime_eval.py:214/372/391/562`
- `边界`: 不给 `5` 编一个「经过排序实验得到」的理由。

## A84

记录下来的那次 rerun 是同条件的：同一天（2026-06-20）、同一数据集 `hotpotqa`、`limit=5`、`top_k=10`、auto route policy，baseline / local / deep 三个模式在同一次记录里跑。但有两点必须主动讲，否则会误导：第一，更早那轮 limit=5 的 smoke 用的是 `qwen-plus`，是 profile 对齐之后才换成 `deepseek-v4-flash` 的，所以**跨那两轮不是同模型**；第二，「同一索引」严格说不成立——runner 是在进程内用 corpus 临时重建一个本地 graph retriever、注入 runtime registry，跑完就清掉，索引不持久化。这两点跟 A19 是同一个口径。

第二层：

- 同条件项：date / dataset / limit / top_k / route policy，「同日 rerun」。
- 不同条件项：早期轮次模型是 `qwen-plus`，后改 `deepseek-v4-flash`。
- 索引：`8a11c193` 记录的 eval 基建限制——临时重建、run 后清理、persisted ingestion `not_implemented`。

- `事实层`: Historical / Current（基建边界）
- `证据`: `3da5d742`；`8a11c1930b6e7e3cf34e7708e5c967fdcc564292`；PF-031
- `边界`: 只说「在同一次记录里同条件」，不说「同一持久化索引上可复现」。

## A85

是**持平**，不是反超。rerun 里 local 恢复到 `Recall@5=1.00`，而 baseline 是 `1.00`——也就是「不再低于」，对齐到同一条线上。所以能不能区分是 fusion 在起作用还是噪声？我的诚实答案是：**在这 5 条样本上区分不了**。最有说服力的一条反证是：这次 rerun 里 **baseline 自己的 `MRR@10` 也从 0.90 变成了 1.00**——baseline 动了，说明这份样本本身波动就大；5 条题里一条翻转就是 0.20 的指标跳动。所以在小样本上，我只会下「该 smoke 的 sampled regression 消失」这个结论，不会说「fusion 带来了提升」。

第二层：

- local 恢复值：`Recall@5=1.00`、`MRR@10=1.00`、`FullChainHit@5=1.00`，`fallback_count=1`。
- 反证：baseline `MRR@10` 0.90→1.00（PF-031 原文就写了）。
- 一条题 = 0.20 指标移动。

- `事实层`: Historical
- `证据`: `3da5d742`；PF-031；`docs/evidence/current-eval-baseline.md`（`MEASUREMENT_BLOCKED`）
- `边界`: 不制造「fusion 有效」的因果或百分比。

## A86

我不为它们做测量辩护——**我拿不出「保留它们是对的」的测量证据**。我能给的理由只有两条，且都弱：一是每个机制都对着一个具名失败形态、并有一条对应单测（但单测只证明 behavior，不证明对指标的边际贡献）；二是「现在就删」同样是没有测量的猜测。所以我的立场是**暂留 + 明确 gate 住**：这层的去留权不在我手里，在冻结的 ablation 协议手里，而协议今天是 `BLOCKED_PENDING_DATA`（本机连不上 HotpotQA 官方源、没有运行时索引和模型凭证）。如果 Red 反过来主张「没 ablation 就该先 Defer 掉」，我不反驳——那是同等可辩护的位置。

第二层：

- 判据（协议 §2）：holdout 上 `full` 相对 `full minus H` 方向一致且跨切分稳定才保留；否则删。
- 当前状态（协议 §8）：`BLOCKED_PENDING_DATA`。
- 已记录的 `normal vs enhanced` 只证明「不劣于基线」，不是逐项 leave-one-out。

- `事实层`: Open Design（保留理由）/ Current（协议阻塞状态）
- `证据`: `docs/governance/rb019-graphrag-ablation-protocol.md` §2/§8
- `边界`: 不用「复杂所以保留」当理由；承认这些机制目前是没有收益证明的复杂度。

## A87

别名归一化要救的是「跨文档里同一个实体的写法不一致」：大小写、标点、冠词、以及像 `(novel)` 这种括号后缀，导致 seed 命中不到图节点，于是第二跳走不过去。但「你真见过还是推演出来的」——我必须说实话：**推演的成分大**。我是从代码和 HotpotQA 实体提及的形态推出「这类差异会造成漏配」，我没有一条落盘记录显示「某条题就是因为别名没归一化而失败、归一化后命中」；也没有 ablation 把 H8 单独关掉看谁掉。中文法律那侧更干脆：误合并是纯推理判断，未测。所以这条机制的「必要性 bad case」目前是有的（形态清楚），但**没有可复核的实例**。

第二层：

- 目标失败形态：跨文档实体提及方差 → seed 漏配 → 多跳断链。
- 归一化实现：`entity_alias.py:25-32`（去括号、去冠词、连字符/标点→空格、小写、压空白）。
- 证据缺口：无单机制 bad case 记录、无 H8 ablation。

- `事实层`: Open Design / 推理判断
- `证据`: `graphrag/entity_alias.py:25-61`；协议 §3 H8
- `边界`: 明确「形态成立但实例未记录」，不用推演冒充观测。

## A88

path-aware ranking 里的「path 证据强度」是一个**确定性的规则分数**，不是模型打的。`_score_path` 返回一个 6 元整数元组，构成为：seed 覆盖（字符串包含）、关系线索命中（对着固定的英文关键词表和 relation-type 集合判 comparison / bridge / genealogy）、标题匹配加成、以及对泛化实体的惩罚；`_path_metadata` 另外算出 path_length、seed/bridge 覆盖、support count 等。这些权重是**手定的**，验证只到单测一层——没有 calibration，也没有「这个打分本身对不对」的评测。所以我要说清楚：它的「强度」既不是学出来的，也没有被证明过是好的排序。

第二层：

- `_score_path` — `graphrag/retriever.py:426-479`；`_path_metadata` — `:531-558`。
- 关系线索来源：`fusion.py` 的 `BRIDGE_RELATION_CUES` / `GENEALOGY_RELATION_CUES` 与 retriever 的 relation-type 集合。
- 验证：`tests/graphrag/test_graphrag_path_ranking.py`（behavior only）。

- `事实层`: Current / Fundamental（打分可落地性）
- `证据`: `retriever.py:426-479,531-558`；`fusion.py:36-55`
- `边界`: 不声称这个打分被验证过或经过调参。

## A89

不会串。原因跟前面那条一样：配置不是挂在 server 对象或任何进程级变量上，而是**每次调用按 `user_id` 现取、合并进这一次调用自己的参数字典**。`execute_binding_tool` 一开始就 `call_args = dict(args)`，然后 `call_args.update(mcp_config)`——`call_args` 是本次调用的局部对象，两个并发请求各持一份，没有任何共享可变状态，所以不需要「全局 dict 加锁」这种方案。隔离单位是单次调用，不是 server：同一 server 同一 tool 的两个用户各自解析到各自的配置副本。

第二层：

- 注入点：`platform/services/workspace/simple_agent.py:189-201`（`call_args.update(mcp_config)`）。
- 局部对象：`call_args` 为函数局部，未写入模块级 / 类级缓存字段。
- 对比父版本 `MCPAgent` 也是「每次现取再 update 到本次 args」，只是位置在子 Agent。

- `事实层`: Current
- `证据`: `simple_agent.py:189-201`
- `边界`: 这只说「配置不串」；不等于「并发的远端调用本身安全」——那是 06 的 effect/idempotency 问题，另算。

## A90

用的是**显式函数参数**，不是 ContextVar，也不是线程/协程本地。调用点本来就明确知道 `user_id`，所以直接把 `user_id` 带进 `execute_binding_tool`，在注入点当场去取该用户在该 server 上的配置。为什么不用 ContextVar：注入点在一个已知 `user_id` 的函数里，隐式上下文反而增加「这个值到底哪来的」的调试成本。平台里确实有 ContextVar（`platform/common/contexts.py`：`trace_id` / `unique_id` / `user_id` / `agent_name`），但那是 tracing 用的，MCP 配置不走它。如果哪天改成在中间件层统一注入、没有显式参数可带，那 ContextVar 才是首选——而不是全局 dict。

第二层：

- 显式传参：`execute_binding_tool(..., user_id=..., mcp_user_config_resolver=...)`。
- ContextVar 存在但用途不同：`platform/common/contexts.py:5-8`。
- 选显式的理由：可追溯、无上下文泄漏风险。

- `事实层`: Fundamental / Current
- `证据`: `simple_agent.py:158-201`；`platform/common/contexts.py`
- `边界`: 这是「今天的实现选择 + 如果重做我会怎么选」，不是「当时做了 ContextVar 改造」。

## A91

cancel 本地 coroutine 不等于远端停了。协程被 cancel 只说明本地不再等它，已经发出去的请求对端可能还在跑、甚至已经跑完——这跟「HTTP 超时」是同一类语义模糊。系统对这条有明确规则：**cancel 在 send 前才算「阻止 Attempt」；Cancel 在 send 后，远端 cancel 只是可选尝试，仍要走 Reconcile**；`C3` 也写了「取消只阻止未来可停止的 dispatch，已发出但未知的调用继续 Reconcile」。所以答案是不能拿 cancel 当「远端没执行」的证明。另外如实补一句：在工具调用这条路径上我没找到 `asyncio.gather`——它出现在 memory client、mcp `multi_client`、queue runner 这些地方；但无论本地是顺序还是并发发起，cancel 的语义都不延伸到远端。

第二层：

- 规则：`docs/modules/effects/reference.md` B14.6「Cancel 在 send 前 → 阻止 Attempt；Cancel 在 send 后 → 尝试 cancel 可选，仍 Reconcile」；C3。
- 不变量：不把 cancel 当 confirmed-not-executed。
- 代码位置：`asyncio.gather` 命中于 `memory/client.py`、`platform/services/mcp/multi_client.py`、`queue/runner.py` 等，不在 tool invocation 路径。

- `事实层`: Target（语义）/ Fundamental（协程取消）
- `证据`: `docs/modules/effects/reference.md` B14.6 / C3；src grep 结果
- `边界`: 我不说「cancel 会终止远端」；也不声称已审计所有调用点的并发方式。

## A92

只靠客户端分不清——timeout 只说明本地没拿到确定响应，远端可能没执行，也可能执行了但结果没回来。要分，得在发送前先把「到底有没有发出去」变成一个耐久事实：调用前落一条 Attempt，记录 dispatch 阶段是 `KNOWN_NOT_SENT`，还是越过 send boundary 之后的 `REQUEST_SENT`，再是 `TIMED_OUT` / `CONNECTION_LOST`。只有 `KNOWN_NOT_SENT`（可证明没发出去）才允许有界重试；一旦越过 send boundary，结果就是 UNKNOWN，绝不映射成普通 Failed。

第二层：

- 状态族：`CREATED → DISPATCHING → REQUEST_SENT / KNOWN_NOT_SENT`，`REQUEST_SENT → RESPONSE_RECEIVED / TIMED_OUT / CONNECTION_LOST`（`docs/modules/effects/reference.md` B7）。
- 参考次序：TX1 先持久化 PreparedAction / idempotency + durable Attempt intent，COMMIT 后才发外部调用。

- `事实层`: Target / Fundamental（timeout 语义）
- `证据`: `docs/modules/effects/reference.md` B7 / B11
- `边界`: 这是 06 的 Target 语义；「消除网络栈与持久化之间所有不可观测窗口」不承诺，恢复依赖远端幂等 / correlation / 对账。

## A93

有做幂等，而且做法是**动作身份**而不是「重试次数」。当前 MCP 路径的 key 是 `idem:{tenant_id}:{workspace_id}:{run_id}:{step_run_id}:{tool_name}:{salt}`，作为 `call_id` 传进 Gateway；Gateway 侧 `claim_idempotency_receipt(...)`：completed claim 直接返回既有 `result_ref`，`in_progress` 且同 owner 就先 reconcile 再返回既有结果，否则拒绝。另外还有一条由规范化后的非敏感参数算出的 action hash：same key + same hash 走既有记录；same key + **不同** hash 直接 conflict fail closed，不允许悄悄造第二个逻辑动作。

第二层：

- key 生成：`capability/mcp/mcp_tool_executor_adapter.py:70-74`（`idempotency_key`），代入 `:135-137` `call_id`。
- Gateway：`invocation_gateway.py` `claim_idempotency_receipt`（A12 给的行号 `:1290-1332` / `:304-323`）。
- action hash：`redact_sensitive_payload(args)` 后规范化；Secret 值不进 hash payload。

- `事实层`: Current（本地幂等）/ Target（远端幂等）
- `证据`: `mcp_tool_executor_adapter.py:70-74,135-137`；`invocation_gateway.py`
- `边界`: 能保证本地不造第二个逻辑动作；**远端**去重看 Provider 是否真幂等，今天没有真实 Provider 证据，也不宣称 exactly-once。

## A94

用的不是单一手段：**激活路径是悲观行锁 + 乐观 CAS**。`MemoryRepository.activate_memory_version` 先 `SELECT status FROM memory_versions ... FOR UPDATE`（`platform/database/memory/domain.py:315`），状态必须在 `{APPROVED, ACTIVE}`，再 `UPDATE ... WHERE ... AND generation=:expected_generation`，`rowcount != 1` 就抛 `MemoryGovernanceConflict("memory activation CAS failed")`。所以同一条 version 不会被双激活，也不会 lost update。但要说清楚两点：`MemoryUnitOfWork` 用的是 `connection.begin()`，**没有显式设置隔离级别**（DB 默认）；`FOR UPDATE` 在 memory 模块里就这一处。仓库别处还有锁，比如 `agent/runtime/postgres_store.py:127/276` 的 `FOR UPDATE`、`platform/database/foundation.py:465` 的 `FOR UPDATE SKIP LOCKED`（队列领取）。

第二层：

- 悲观锁 + CAS：`domain.py:301`（方法）/ `:315`（FOR UPDATE）/ `:320-321`（状态约束）/ `:353`（CAS 条件）/ `:363-364`（冲突抛错）。
- UoW：`domain.py:83` `MemoryUnitOfWork`，`:89` `self._connection.begin()`，无 isolation 参数。
- 其它锁点：`postgres_store.py:127/276`；`foundation.py:465/626/909/1486`。

- `事实层`: Current / Fundamental（并发写）
- `证据`: `platform/database/memory/domain.py:83,301-364`；`postgres_store.py`；`foundation.py`
- `边界`: 我能说「同一 version 不会双激活」；不说「隔离级别经过调优」——它是 DB 默认。

## A95

设计上是不能的——**不要拿着数据库行锁去等模型返回**。原因很直接：模型调用是秒级甚至更长的外部等待，而 `SELECT ... FOR UPDATE` 持有的是行锁，锁一跨过 `await`，就会把连接和锁一起摁住，直接放大到连接池耗尽、并发出错。在我看过的那条 memory 路径里也没有这个问题：回合后的 `post_turn_commit` 是在模型已经返回之后才开的写事务，`activate_memory_version` 的 `FOR UPDATE` 是一段很短的激活事务，里面不含模型调用。但我要给一个诚实的边界：我没有逐个调用点审计「是否存在某处把模型调用包在写事务里」，所以这是「规则 + 我抽查的这条路径」，不是全仓库证明。

第二层：

- 反模式定义：长事务里 `await` 外部调用 = 锁/连接被长期占用。
- 检查点：`post_turn_commit`（`agent/runtime/nodes/core.py:391-482`）→ `commit_turn_outcome`（`memory/governed_runtime.py:30-142`）→ `activate_memory_version`（短事务）。
- 锁点：`platform/database/memory/domain.py:315`。

- `事实层`: Fundamental / Current
- `证据`: `core.py:391-482`；`governed_runtime.py:30-142`；`domain.py:315`
- `边界`: 不说「全仓库保证无长事务」；只保证设计规则与抽查路径。

## A96

审核状态是**数据库里的一列**，不是纯应用层判断：candidate 表 `platform/database/models/memory_runtime.py:69` 有 `review_status: str = Field(default="pending", index=True)`，另有独立的 `memory_review_decision` durable 表（`store.save_review_decision`）。读回过滤发生在应用层，但依据是这一列：`MemoryEngine._memory_exclusion_reason` 里 `if candidate.review_status is not MemoryReviewStatus.APPROVED: return f"{...}_review"`。至于 TOCTOU——「review 刚通过、读回却读到旧状态」：读回是每次 build 现查一次，读到的是**查询时已提交的状态**；它没有把「审核决定」和「读回」放进同一个快照或同一事务里冻结，所以严格说没有一个专门的 TOCTOU 护栏，只有一个「按当前提交状态过滤」的规则。而且按我在前面那条的结论，没有后台 reaper 主动刷状态，状态的新鲜度依赖写入真的落库。

第二层：

- 列：`memory_runtime.py:69`（`review_status`，indexed）；独立表：`store.save_review_decision`（`memory/store.py:93`）。
- 应用层过滤：`memory/engine.py:1054-1064`。
- 并发面：无显式 snapshot / 事务冻结；无后台刷新任务。

- `事实层`: Current（列 + 过滤）/ Gap（TOCTOU 护栏）
- `证据`: `memory_runtime.py:69`；`engine.py:1054-1064`；`store.py:93`
- `边界`: 我不说「TOCTOU 已防住」；存在的只是按当前提交状态的过滤。

## A97

都不是 RRF，也不是单纯加权和。它是一套**硬分层 + baseline rank 下限**：`_candidate_group` 把候选分到离散组（0/1/2/3），`_rank_key` 的排序键是 `(candidate_group, baseline_rank, -chain_score, -graph_tier, -graph_signal, -(local+base))`，其中 `baseline_rank = min(vector_rank, bm25_rank)` 当不可被挤出的下限；另外针对 comparison / bridge / genealogy 三类 query 还有硬替换 top 的 guardrail。代码里**确实算了一个加权 `fusion_score`，但它只写进 metadata、不参与排序**。为什么不用 RRF：RRF 是把多路排名做成一个全局融合分再重排，那会把「baseline 是下限」这条保证抹掉，而我们的目标恰恰是「不劣于 baseline」；而且不同 route 的原始分本来就不可比，硬拼一个连续分会把不可比的东西假装成可比。

第二层：

- `_rank_key` — `retrieval/fusion.py:951-977`；`_candidate_group` — `:166-187`；`_baseline_rank` — `:190-202`。
- guardrail：`_apply_comparison_guardrail` / `_apply_bridge_guardrail` / `_apply_genealogy_guardrail`（`merge()` `:1039-1053` 调用）。
- 全仓库 grep `RRF` / `reciprocal`：无命中。

- `事实层`: Current / Fundamental（IR 融合）
- `证据`: `fusion.py:166-224,951-977,1039-1055`；grep 结果
- `边界`: 这是「护栏式融合」，不是「更好的融合算法」；不保证优于 baseline。

## A98

是**硬分区**，不是 tie-break。`candidate_group` 是排序键的第一位，排在 `baseline_rank` 之前——也就是说「属于哪个组」先决定谁在前，组内才看 rank；再加上三类 query 的 guardrail 会直接替换 top 里的成员。所以 graph 证据够强的候选是「跨组晋升」，不是「同分时排前面」。它跟 RRF 的冲突在根上：RRF 的整个前提是「把不同来源的 rank 融成一个全局分」，而这里的设计**拒绝把不可比的 route 分做融合**——graph 能不能越过 baseline 是一个「够不够格的 gate」，不是一个分数贡献。一个 gate 和一个连续融合分在数学上不相容：你想让 gate 生效，就得放弃 RRF 那种「所有来源平等贡献」的假设。

第二层：

- 组即主键：`_rank_key` 返回元组首位 = `candidate_group`（`fusion.py:965,977`）。
- 硬替换：`selected[weakest_index] = candidate`（genealogy 等 guardrail）。
- 与 RRF 不相容点：gate（离散资格）vs 连续融合分。

- `事实层`: Current / Fundamental（排序语义）
- `证据`: `fusion.py:166-189,900-949,951-977`
- `边界`: 不说这比 RRF 好；只说它和 RRF 在前提上冲突，不能混用。

## A99

是 **ANN，不是精确 KNN**。当前向量侧用的是 Chroma，建 collection 时带了 `metadata={"hnsw:space": "cosine"}`，也就是 HNSW 近似索引；Milvus 侧走的是 `MilvusLiteClient`。所以在 `limit=5` 这种小 K 下，返回的是「近似最近邻」，理论上存在 recall 损失。要坦白的是：**我没有测过这个 recall 损失**——没有「ANN vs 精确」的对照，也没有在不同 K 下的召回曲线。所以我能说的只是「它实现上是近似的、并且这个代价未被测量」，不能说「近似损失可忽略」。

第二层：

- Chroma：`platform/services/rag/vector_db/chroma_client.py`，`create_collection` 里 `metadata={"hnsw:space": "cosine"}`；查询 `n_results=min(top_k, 100)`。
- Milvus：`MilvusClient(MilvusLiteClient)`。
- 未测：ANN recall@K、不同 K 的召回变化。

- `事实层`: Current（实现）/ Fundamental（ANN 代价）/ Unknown（recall 损失）
- `证据`: `chroma_client.py`（create_collection / _search_collection）；`milvus_client.py`
- `边界`: 不给「小 K 下 recall 损失可忽略」这种没测过的结论。

## A100

我的答案是：**三者都不能单独当最终判断**，它们各自只拥有自己那一层。模型只产生候选（`MemoryCandidate` / `EvidenceCandidate`），它不拥有真值也不拥有授权；review 流程负责把候选推进成被采用的记录；数据库约束负责的是**身份与并发**——比如 memory version 的激活 CAS、幂等 receipt 的唯一约束，它们的作用是让并发写 fail closed、而不是让谁知道真相。真正的「可信」拆成两层归 Owner：真实性/正式事实归 02 Domain，能不能在这次调用里被使用归 08 Security（recall eligibility / authorization）。三者冲突时，遵循的不变量是 `Provenance != Truth != Authorization != Semantic Preservation`——source id 只说明来源，不能拿来当真相、权限或压缩无损的证明。所以冲突的仲裁顺序不是「模型听 review、review 听数据库」，而是**各自回到自己那个 Owner**：模型永远不赢；authorization 由 08 判；并发写的一致性由 DB 约束兜底。

第二层：

- 候选 vs 正式：候选由模型 / 检索产生，正式事实由 02 HumanDecision / WorkProduct 承担。
- 授权：`docs/modules/security/reference.md`（08 owns AuthorizationDecision / Recall Eligibility）。
- DB 约束：`domain.py:353-364`（activation CAS）、`memory_commit_receipts.idempotency_key`。
- 不变量：`docs/modules/reference.md`「绝对不能再次混淆的边界」。

- `事实层`: Target（authority）/ Current（CAS 与幂等已实现的部分）
- `证据`: `docs/modules/security/reference.md`；`docs/modules/reference.md`；`domain.py:353-364`
- `边界`: 独立的 08 recall decision 今天还没接上（这条跟 A31 一个口径）；我不把「数据库约束 + APPROVED 过滤」说成完整的信任仲裁。
