# Findings — rb-2026-09-09-tool-calling-task-004

Round result: `CLOSED_WITH_INTERVIEWABLE_TOOL_CALLING_TASK_AND_EVIDENCE_LIMIT`  
Resume claim verdict: `PASS_FOR_BOUNDED_V4_UPGRADE`  
Highest severity: `S2`

本轮测试 v3 中仍然泛化的 `Agent 与 Tool Calling` 表述。PF-032 与 2026-04-15 / 04-28 历史代码已经足以支撑一个有边界的 Tool Calling 主故事；只保留一个会限制结果强度、但不要求继续削弱 Resume 的 Finding。

## F1 — Tool Calling Strategy 已恢复到具体任务，现实业务结果仍未恢复

Severity: `S2`  
Type: `EVIDENCE_GAP`

### What is now proven

可以稳定证明并展开：

- `773467580ee428a0536c7f594c0847c1510879ac` 由用户 GitHub 账号 authored / committed；父代码包含独立 tool-invocation / available-tools selector scaffolding、MCPAgent-as-Tool 和 SkillAgent-as-Tool 路径；该提交把具体 MCP tools 和 Skill guidance tools 直接绑定到一个 `GeneralAgent`，并把 MCP user config 放到 tool-call middleware 中按调用注入；
- 父代码虽然实例化过 `LLMToolSelectorMiddleware`，实际 middleware 列表没有返回它，因此只能说移除了 selector scaffolding，不能说替换了已证明在线运行的第二 selector model；
- Workspace Agent 保留 deterministic direct route 与 ReAct fallback：目标 / 参数明确的一步 Tool 可以走短路径，开放式、多步或参数不完整的任务继续进入 ReAct；
- `0b5fb35039711ab0b63dad6528df5e4705fbc93d` 中可从前后代码直接复现并确认两个历史 defect/fix：custom MCP name 归一化自递归，以及高德天气自然句的 naive city extraction；
- 同一 04-28 commit 新增 regression test artifact，固定 `maps_weather(city="南京")` 与 custom MCP name 不递归等行为；
- MCP / Provider 继续负责协议连接、Tool discovery 和具体执行，Zuno 当时负责 Agent-side schema exposure、routing、user-config injection 和 result handling；
- 两个 commit 都由用户账号提交，但 04-28 是 broad platform commit，因此个人 Claim 只落到有明确 before/after 和 test artifact 的 Tool Calling 局部改动。

这些证据已经解决“只会说参与 Tool Calling、无法解释具体 Strategy / bug / alternative”的主要任务级缺口。

### What remains unknown

当前没有恢复：

- 最初触发 04-15 Strategy 重构的产品 / 业务需求、Issue 或 Review；
- 两个 4 月 SHA 对应的历史 test execution / CI pass；
- custom MCP recursion 或 weather parameter defect 是否来自真实用户 / Pilot Bad Case；
- Tool Trace、调用成功率、latency、token 或成本前后数据；
- 客户 / 法院 / Pilot 对这条 Tool Calling 工作的可验证结果。

因此不能把故事包装成“客户发现 Tool Calling 失败 -> 我修复 -> 成功率提高 X%”。当前最强事实是 Strategy refactor + code-reproducible defects + regression test artifacts。

### Resume decision

**允许新增 v4 候选，并增强 Tool Calling bullet。** 不覆盖 v3，不直接覆盖当前投递 PDF。

建议 Resume 只表达四层事实：

```text
single-Agent Tool/MCP strategy
-> concrete MCP tools directly exposed to GeneralAgent
-> per-user config injected at tool-call time
-> direct-route / ReAct fallback + two route hardening fixes
```

避免写入：

- “设计 / 实现完整 Tool Runtime”；
- “Tool Control Plane / PreparedAction / Approval / Idempotency / Reconcile 已在 4 月完成”；
- “历史 CI 全绿”；
- “显著降低 latency / token”；
- “调用成功率提升”；
- “修复生产事故”。

### Evidence still worth recovering

后续只有以下材料能实质抬高这条故事的结果层：

```text
原始需求 / Issue / Review
-> 历史 test run / CI artifact
-> 真实 Tool Trace / Bad Case
-> Pilot / 客户调用结果
-> latency / token / success-rate 对照（如果当时真实存在）
```

如果这些材料长期找不到，不需要继续弱化当前 bounded Claim。

## Resolved by this round

- `OWNERSHIP_GAP`：从方向级“参与 Tool Calling Strategy”收敛到 04-15 Strategy diff 与 04-28 局部 hardening diff；
- `TRADEOFF_GAP`：可以解释 direct MCP tools 的简化收益与 Tool Schema / Context scale 代价；
- `BUILD_BUY_GAP`：MCP Provider 与 Zuno Agent-side routing/config responsibility 已分开；
- `EVIDENCE_GAP`（任务实现部分）：可以解释两个真实代码 defect 与 regression test artifact；
- `RESUME_CLAIM_RISK`：允许增强为有边界的具体任务，但不允许跨时间层借后续 Tool Control Plane 抬高 4 月经历。