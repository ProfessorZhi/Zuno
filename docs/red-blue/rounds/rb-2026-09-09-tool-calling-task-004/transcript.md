# Transcript — rb-2026-09-09-tool-calling-task-004

Mode: `CHATGPT_AUTO`  
Zuno base: `6df22fac74b852932bc97524a6c9aaf7836fdb42`  
Resume: `ProfessorZhi/internship-work@b57f28a5b0da0b84eaf77bc1bcee5d4c999394da:resume/00_resume_versions/Zuno_v3+CodingAgent+SFTDPO_简历/Agent开发工程师／AI应用工程师+Zuno／CodingAgent／SFTDPO_任务证据增强／可追问_简历草稿_v3.md`

本轮只测试 v3 中仍为方向级表述的 `Agent 与 Tool Calling`。Blue 只能使用 PF-032、2026-04-15 / 04-28 历史代码及其父提交和 test artifact；不得使用 7–8 月 Tool Control Plane、PreparedAction、Approval、Idempotency、EffectReceipt 或 Reconcile 反向补 4 月历史。

## Turn 1 — Strategy decision and exact code boundary

### Red

“参与 Tool Calling Strategy”太泛。具体改了什么策略？如果只是把 MCP Tool 注册到 LangChain，不算 Strategy。

### Blue

2026-04-15 的父版本同时保留独立 `tool_invocation_model`、`available_tools` 和 `LLMToolSelectorMiddleware` 选择脚手架，并把一个 MCP Server 先启动为 `MCPAgent`、再把整个 MCP Agent 包成一个 Tool；Skill 也通过 `SkillAgent` 包装成 Tool。需要保留证据边界：虽然父代码实例化了 `LLMToolSelectorMiddleware`，`setup_agent_middleware()` 实际返回的只有 event middleware，所以只能说 selector scaffolding 存在，不能说已证明线上启用了第二个 selector 模型。

`773467580ee428a0536c7f594c0847c1510879ac` 把调用路径收敛到单一 `GeneralAgent`：普通 Tool、具体 MCP Tool 和 Skill guidance tool 直接进入同一个 `create_agent(... tools=...)`；MCP 调用时，middleware 根据 tool -> MCP server 映射读取该用户配置并注入 tool args。MCP 不再需要 `GeneralAgent -> MCPAgent -> MCP Tool` 的嵌套执行层。

这个设计减少了 Agent 层级和路由状态，但会把更多具体 Tool Schema 暴露给主 Agent。父代码已经记录“工具多会占用 Context Token 并影响命中”的探索性判断，因此不能把 direct binding 当作无限扩展方案；工具规模变大以后仍可能需要 Capability search / selection。

### Verifier

Verdict: `PASS`  
Next action: `NEXT_ATTACK_ANGLE`

回答给出了旧链、新链、责任移动和代价，并且没有把未实际返回的 selector middleware 夸成生产事实。

## Turn 2 — Direct route vs ReAct

### Red

既然 Workspace Agent 已经能识别高德、天气和路线，为什么不把所有 Tool Calling 都做成确定性 direct route？

### Blue

Direct route 只适合目标 Tool 和参数都能从输入可靠恢复的一步任务。天气、明确 Bing 搜索和部分地图路线可以走短路径；开放式、多步或参数不完整的任务仍要交给 ReAct。

历史代码明确保留这个边界：如果能够得到 `direct_tool`，就直接执行 `_run_direct_routed_tool()`；部分高德路线虽然先匹配到路线 Tool，但当当前 origin / destination 仍不适合一次确定性调用时，会主动清空 `direct_tool`，日志明确记录 `falls back to ReAct for multi-step gaode query`，随后继续普通 Agent loop。

因此 Strategy 是“确定性短路径 + ReAct fallback”，不是规则路由替代 Agent。当前没有 latency、token 或 success-rate 对照数据，不能声称量化性能收益。

### Verifier

Verdict: `PASS`  
Next action: `CONTINUE_SAME_CHAIN`

回答尊重两种路线的适用条件，也保留 Measurement Unknown。

## Turn 3 — Historical defects vs incidents

### Red

有没有真正修过 Tool Calling Bug？不要把架构里的 hypothetical failure 当历史事故。

### Blue

有两条可以从父提交和 2026-04-28 commit 的代码前后直接复现的历史实现缺陷，但没有证据表明它们曾形成法院或 Production 事故。

第一条是 custom MCP server name 的归一化。父版本 `_canonical_mcp_target()` 匹配到一个 custom server name 后再次用该 `server_name` 递归调用自身；当 normalized query 已经等于 normalized server name 时，递归条件不发生变化，可以无限递归。`0b5fb35039711ab0b63dad6528df5e4705fbc93d` 改为直接返回 `server_norm`，并在代码注释中明确指出此前可能 loop forever。

第二条是高德天气参数抽取。父版本通过 `cleaned.replace("天气", "")` 直接形成 `city`，自然句“请用高德地图查询南京今天天气，并简短回答。”会留下大量非城市文本。新版本增加 `_extract_gaode_weather_city()`，去掉调用前缀、后续要求和天气修饰后再得到城市。

### Verifier

Verdict: `PASS`  
Next action: `NEXT_ATTACK_ANGLE`

这两条可以称为 code-reproducible historical defects；不能称为 customer incident / production outage。

## Turn 4 — Test artifact and evidence strength

### Red

你怎么证明这两个 fix 不是事后读 diff 自己编的解释？测试通过了吗？

### Blue

同一个 2026-04-28 commit 新增 `src/backend/agentchat/test/test_workspace_simple_agent.py`，其中明确固定两类行为：自然句必须 direct-route 到 `maps_weather(city="南京")`；custom MCP server `qa-mcp-461126` 归一化后必须直接返回，不发生递归。测试文件还覆盖 platform-ready MCP 不要求 user config，以及 direct Tool result 的呈现等行为。

当前能证明的是 regression test artifact 被提交，不能证明当时 CI 执行通过。`773467...` 与 `0b5fb350...` 都没有关联 PR；当前 GitHub 历史没有恢复这两个 SHA 的 PR-triggered Actions run，combined commit status 也没有 recorded status checks。因此面试中不能制造“X tests passed”或“CI 全绿”。

### Verifier

Verdict: `PASS`  
Next action: `NEXT_ATTACK_ANGLE`

Blue 能区分 test source、historical execution 和 production result。

## Turn 5 — Build / Buy and MCP responsibility

### Red

MCP 本来就负责 Tool discovery / invocation。Zuno 再做 route hint、config injection、direct route，是不是重复造轮子？

### Blue

4 月代码仍使用 `MCPManager.get_mcp_tools()` 获取真实 MCP tools，没有重写 MCP 协议或 Provider execution。MCP 负责连接、发现和执行 Tool；Zuno 当时负责 Agent 怎样消费这些能力：哪些 tool schemas 暴露给主 Agent、某个 Tool 属于哪个 MCP server、调用时注入哪个用户配置，以及用户已经明确指向某个 Tool 时是否走确定性短路径。

如果应用只有少量 Tool、没有多账号配置，也没有明确 route 需求，可以直接使用普通 Agent + MCP tools，不需要额外复杂度。PF-032 也不能反向证明今天的 Tool Control Plane；PreparedAction、Approval、Idempotency、EffectReceipt、Outcome Unknown -> Reconcile 属于后续更强语义。

### Verifier

Verdict: `PASS`  
Next action: `CONTINUE_SAME_CHAIN`

Build / Buy 边界成立，没有贬低成熟 MCP，也没有把后续 Tool Runtime 倒灌到 4 月。

## Turn 6 — Personal ownership and result

### Red

4 月 28 日是一个很大的平台 commit，又没有 PR Review。为什么可以写成你的工作？最后有什么结果？

### Blue

两条 commit 的 author / committer 都是用户 GitHub 账号，但个人 Claim 只能落到能从 diff 精确对齐的局部改动。`773467...` 的 `GeneralAgent` Tool/MCP strategy 有明确父提交；`0b5fb350...` 是 broad platform commit，因此只能提取 Workspace Agent 中 custom MCP recursion、天气参数解析和对应 test artifact，不能把整个 commit 都认领成 Tool Calling 工作。

没有关联 PR / Review，也没有历史 CI pass、Tool Trace、客户 Bad Case、Pilot 对照或 latency/success-rate 指标。当前结果只能说：调用路径被收敛为单 Agent 直接消费 MCP tools，两个具体 route defect 在代码层被修复，并提交了 regression test artifact。不能写“显著降低延迟”“提升调用成功率”或“生产稳定运行”。

### Verifier

Verdict: `PASS`  
Next action: `CLOSE_ROUND`

个人 Ownership 能落到具体 diff，结果强度与当前 Evidence 匹配。

## Round close

PF-032 已经把 v3 中泛化的“参与 Tool Calling Strategy”升级成一条可持续 3–5 分钟追问的历史工程任务。它能覆盖 Strategy decision、simple alternative、direct-route / ReAct boundary、两个 code-reproducible defect、Build/Buy 和 personal ownership。

可以在新的 Resume 候选中增强 Tool Calling bullet，但 Claim 必须停在 4 月实际证据：single-Agent Tool/MCP strategy、调用期 user config、direct route / ReAct fallback 和具体 route hardening。当前不支持完整 Tool Runtime ownership、后续 Tool Control Plane 语义、历史 CI pass、量化性能收益或客户 / Production result。

剩余 Finding 是一个独立 `S2 EVIDENCE_GAP`：原始产品 / 业务触发、历史 test execution、真实 Tool Trace / Bad Case 和客户 / Pilot outcome 尚未恢复。它限制结果叙事上限，不构成当前 bounded Resume Claim 的真实性风险。