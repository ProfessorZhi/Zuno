# Blue Wave 1 Architecture Notes — rb-2026-09-15-formal-019

status: `COMPLETE`
visibility: `SEALED_FROM_RED`

本文件是 Wave 1 的架构初诊。它不用于 coaching Blue Wave 2 Candidate，也不向 Red 暴露。

## 1. Tool/MCP：历史实现可信，但企业级调用语义不能从 4 月提交外推

**signal**：Red 连续追到 per-user config、shared-instance isolation、schema drift、timeout、idempotency、authorization。

**source_check**：PF-032 与 4 月 15 日提交能证明 concrete MCP Tool 直接绑定 GeneralAgent、`mcp_tool_server_map`、call-time `get_mcp_user_config(user_id, server_id)` 和 Workspace route hardening；不能证明 shared-instance cross-user isolation、ConfigVersion、ToolVersion、Approval、Idempotency 或 Reconciliation 已在当时完成。

**judgment**：主要是 `SIMULATED_RESUME_GAP / EVIDENCE_GAP`，不是把今天架构判错。历史 bullet 应继续限定为 binding/config/routing；高风险 Effect 语义属于后来更强的 Tool Runtime。

**simpler baseline**：MCP Host/Provider 负责 discovery/schema/execution，Zuno 只保留业务授权、资源范围、effect truth 和审计。

**measurement / retest**：下一轮继续追 two-user concurrency、config drift、同名 Tool collision 和 timeout outcome；若当前实现已补齐，应由 Current Evidence 证明，不得反写历史。

## 2. Direct route：当前最明显的是“价值未证明”，不是“必须继续扩架构”

**signal**：Red 追问 direct route 的 formal matcher、context pronoun、高风险 Tool bypass、与模型 Tool Calling 的收益差。

**source_check**：PF-032 能证明 deterministic direct route / ReAct fallback、custom MCP recursion 和天气参数 bug 的 regression artifact，但没有 latency/token/cost/reliability benchmark。

**judgment**：`EVIDENCE_GAP`。只有当 direct route 绕过统一 authorization/effect boundary 时才升级为 `ARCHITECTURE_GAP`；当前先不要新增独立 Router Service 或状态机。

**exit condition**：若 direct route 相对统一 Tool Calling 没有稳定收益，删除该优化路径。

## 3. GraphRAG：真正问题是 heuristic + evaluation coverage，不是再加更多图机制

**signal**：Red 已经把 5-query smoke、threshold=6、四项连续改动、alias collision、latency 和 delete gate 全部拉出来。

**source_check**：PF-031 能证明 ranking displacement、baseline-preserving fusion、candidate-aware seed、alias normalization、path-aware ranking，以及同一 tiny smoke 修复后恢复到 baseline；没有 holdout、正式 ablation 或普遍收益证据。

**judgment**：主分类 `EVIDENCE_GAP`。当前 Target 已经把 GraphRAG 定义为 query/evidence-gated、measurement-gated，因此不需要因为 Red 压力把它升级成默认主干。

**candidate change**：先建正式 eval，再决定 always-off / gated / retained；不要先增加 Graph Planner、更多路径状态或独立 Graph Agent。

**measurement needed**：分 query class、冻结 corpus/config、Hybrid+rERanker baseline、增量和 leave-one-out ablation、answer/citation quality、latency/token/cost、错误 seed amplification。

## 4. Entity alias：轻量字符串归一化不够承载身份敏感 Authority

**signal**：Red 直接问同名异人如何避免误合并。

**source_check**：历史 alias normalization 是 retrieval heuristic，不是 stable entity resolution。

**judgment**：如果它只用于候选检索，是 `IMPLEMENTATION_GAP / EVIDENCE_GAP`；如果未来用 alias 结果直接提交 Canonical Domain State，则会成为 `ARCHITECTURE_GAP`。

**simpler alternative**：检索层允许多个 candidate + provenance；只有真正需要稳定身份时再引入 canonical entity id/disambiguation，不为 GraphRAG 好看先建完整 Entity Service。

## 5. Memory V2：Wave 1 暴露的是 foundation 与 enterprise semantics 的清晰断层

**signal**：Red 追 scope authority、reviewer authority、concurrent write、READ COMMITTED、revocation after ContextPack、freshness 和 conflict versioning。

**source_check**：PF-029/030 能证明 typed contracts、`MemoryScope(user_id, agent_id?, project_id?, thread_id?)`、同 scope readback、APPROVED structured memory、source trace、minimal orchestrator 和 focused tests；不能证明 durable concurrency、CAS、完整 reviewer RBAC、MemoryEpoch、成熟 conflict resolution 或质量收益。

**judgment**：历史层面是 `IMPLEMENTATION_GAP / EVIDENCE_GAP`，不应通过简历话术掩盖。当前系统若已演进出 durable store/governance，应单独由 Current Evidence 证明。

**simpler baseline**：Raw Event + Session/Task Summary 先成立；Structured Long-term Memory 只有跨会话任务的 A/B 证明收益后开启。

**exit condition**：长期 Memory 无稳定收益时，删除 extraction/promotion/retrieval，只保留必要 summary/context assembly。

## 6. Memory scope 与 Security Authority 需要保持分层

**signal**：`MemoryScope` 等值过滤不能证明 caller 有权构造任意 scope。

**judgment**：这是一个高价值边界。Memory Store 可以负责 scope equality，Security/Workspace owner 必须负责“当前请求允许使用哪个 scope”。不要把 `where user_id/project_id` 当 authorization。

**classification**：若 canonical docs 已明确该 Owner，属于 `NARRATIVE_GAP / IMPLEMENTATION_GAP`；只有 Owner 本身冲突才是 `ARCHITECTURE_GAP`。

## 7. Multi-Agent：Red 没有发现必须升级的证据

**signal**：Red 从 Single Agent 继续追 Tool → Subgraph → Worker → Specialist → Persistent Multi-Agent。

**source_check**：当前 ADR 允许 Generic Host + Zuno Legal Backend 作为 baseline；Persistent Multi-Agent 和 Native Runtime 都是 measurement-gated。

**judgment**：`NO_ZUNO_CHANGE`。Wave 1 没有出现“Single Agent / Subgraph 已经被真实 workload 证明失败”的证据，因此不能因为面试题多就引入 Supervisor/Specialist 拓扑。

**retest**：只有 context isolation、独立 policy/tool set、长任务 recovery 或 parallel throughput 出现可测瓶颈后，再评估 Specialist。

## 8. Generic Host / Build-Buy：Red 的 subtraction test 与当前 ADR 方向一致

**signal**：Red 多次要求说明 MCP Host、Mem0/OpenViking、Generic Host 已经覆盖什么。

**source_check**：ADR-0008 明确允许 `Generic Host + Legal Skills/Knowledge + MCP/API + minimal Legal Backend`，Native Runtime、GraphRAG、Long-term Memory、Persistent Multi-Agent 都需要测量证明。

**judgment**：`NO_ZUNO_CHANGE`。这一轮反而验证了当前 reuse-first / complexity burden 框架是合理 baseline。

**risk**：Blue Candidate 如果回答成“Zuno 所有层都必须自研”，那是 Blue Skill/Narrative 问题，不是架构真相。

## 9. Resume / Ownership：法院侧测试与团队规模仍然是可信度高风险区

**signal**：Red 问用户本人是否现场参与法院测试、项目谁主导、六条 bullet 哪些真正个人提交。

**source_check**：可以确认约 7–8 人核心规模、项目经历法院侧测试/Pilot、用户约 3 月加入且非 founder；但完整组织图、法院测试个人参与层级未恢复。

**judgment**：`OWNERSHIP_GAP / EVIDENCE_GAP`。简历当前没有夸大 Production，但口头回答必须继续避免把 Team Fact 说成 Personal Ownership。

## 10. Blue Candidate Framework：需要保留“历史没有做到，但今天我知道怎么设计”的回答能力

Wave 1 最容易失败的题不是纯技术题，而是历史/开放设计混合题。例如 idempotency、Memory concurrency、stale Specialist result。Blue 必须先说历史是否存在，再给今天设计；如果只回答 Unknown 会显得没有能力，如果拿 Target 回填 History 会损害真实性。

**workflow note**：下一轮 Retrospective 应检查 Blue 是否稳定执行 `HISTORICAL_OWNERSHIP / CURRENT_SYSTEM / TARGET_DESIGN / OPEN_DESIGN / FUNDAMENTAL` 分类，而不是只看答案听起来是否高级。