# Round #013 Findings

Round: `rb-2026-09-13-zuno-interview-batch-013`  
Status: `CLOSED_AFTER_BATCH_002`  
Highest severity: `S2`  
Architecture verdict: `PASS_NO_NEW_ARCHITECTURE_GAP`  
Resume/project verdict: `PASS_WITH_PERSONAL_EVIDENCE_CEILING`

Batch results:

```text
Batch 001: 100 questions / 85 PASS / 13 PARTIAL / 0 FAIL / 2 UNSUPPORTED_CLAIM
Batch 002: 100 questions / 55 PASS / 45 PARTIAL / 0 FAIL / 0 UNSUPPORTED_CLAIM
Total:     200 questions / 140 PASS / 58 PARTIAL / 0 FAIL / 2 UNSUPPORTED_CLAIM
```

The second batch intentionally moved from broad architecture to function/data-path/project-reality depth, so the higher PARTIAL count is expected. Findings are deduplicated from the full transcript and do not own Project, Architecture, Evidence or Resume truth.

## F1 — Tool / MCP 是当前最强的个人实现故事，但“核心 diff 可证明”和“完整运行语义可证明”必须分开

- **severity:** S2
- **gap_type:** `EVIDENCE_GAP / RESUME_CLAIM_RISK`
- **trigger_questions:** Batch 001 Q016/Q018–Q022/Q024; Batch 002 B2-Q003/B2-Q006–Q009/B2-Q013/B2-Q015/B2-Q017/B2-Q019–Q022/B2-Q024/B2-Q032

Batch 002 证明 PF-032 比 Batch 001 最初判断更强。Canonical provenance 已经足以支持一条函数级主故事：

```text
parent GeneralAgent
  tool_invocation_model / available_tools / selector scaffolding
  MCPAgent-as-Tool / SkillAgent-as-Tool
→ 77346758...
  actual MCP tools + Skill guidance tools bound directly to GeneralAgent
  EmitEventAgentMiddleware injects user MCP config by tool→server mapping
→ 0b5fb350...
  WorkSpaceSimpleAgent route hardening
  _canonical_mcp_target() custom-name self-recursion fix
  _extract_gaode_weather_city()
  deterministic regression artifacts
```

Custom MCP recursion 的触发条件、修复函数、天气自然句到 `maps_weather(city="南京")` 的 regression 都可以从 canonical PF-032 讲清。面试白板层面已经足够支撑“我确实做过这段代码”，而不只是方向级参与。

真正的 evidence ceiling 在外围运行语义与项目因果：

- per-user MCP config 的 request-local / async concurrency 隔离方式未恢复；
- discovery / schema refresh / namespace collision 未恢复；
- direct route 失败后是否进入 ReAct、是否可能导致 side-effect duplicate 未恢复；
- MCP timeout / disconnect / schema-error propagation 未恢复；
- route observability / trace 字段未恢复；
- 原始 Issue、Review、任务分配和客户/业务需求未恢复；
- regression artifact 能证明源码锁定了失败条件，但不能写成历史 CI / E2E / Pilot 已验证；
- 没有 token、latency、success-rate 或客户收益测量。

### Decision impact

不改 Zuno Architecture，也不削弱当前 v5 简历的 bounded Tool Calling bullet。后续最有价值的工作是从 `77346758...`、`0b5fb350...` 及 test file 恢复一份**个人任务证据卡**：before/after call path、exact code location、repro input、test assertion、已知未覆盖运行语义。原始 requirement / Review 若找不到就保持 Unknown。

不要把 later PreparedAction / Approval / Idempotency / EffectReceipt / Reconcile 反写成 4 月个人实现。

### Retest scenario

大厂二/三面代码级白板：要求候选人从 MCPAgent-as-Tool 画到 GeneralAgent direct tools，再追 config concurrency、route failure、test boundary 和 alternative。通过标准是能明确区分“代码 diff 已证明”和“运行语义未恢复”。

---

## F2 — Context / Memory 有最完整的 PR/commit/test 演进链，但实现细节与真实运行闭环仍明显薄于 Tool/MCP

- **severity:** S2
- **gap_type:** `EVIDENCE_GAP / IMPLEMENTATION_GAP`
- **trigger_questions:** Batch 001 Q030/Q032/Q033/Q035; Batch 002 B2-Q036–Q045/B2-Q047–Q050/B2-Q052/B2-Q053/B2-Q055/B2-Q057/B2-Q059–Q063/B2-Q069

PF-030 → PF-029 已经形成可信的历史工程链：

```text
Target plan
→ typed Context contracts
→ scoped Memory contracts
→ minimal GeneralAgent pre/post-turn integration
→ callable ContextOrchestrator
→ PR #8 readback hardening
   same-scope task summary
   APPROVED structured memory only
   Context Pack policy
   source trace
   review / provenance contract
   focused tests: 32 passed
   repo tests: 66 passed
   legacy tests: 11 passed
   contract eval profiles: status ok
```

这足以支撑“我完成了一条 Context Builder / Memory foundation slice”，也能明确证明该工作不是 3 月从零引入整个 Memory——4 月公开根提交已经存在 Memory subsystem。

但 closed-book 深挖仍无法回答：

- `same-scope` 的 exact key / filtering predicate；
- structured memory 完整 schema；
- APPROVED filter 在 store 还是 Python 层；
- task summary 的生成器 / failure semantics / freshness；
- source-id trace 的实际 storage / cardinality；
- Context Pack prompt ordering / dedupe / conflict handling；
- memory-store failure 的 fail-open / fail-closed / degradation policy；
- token overflow / relevance ranking；
- write paths 是否都不能绕过 review；
- exact cross-scope negative fixture；
- prompt-injection / instruction-vs-data isolation；
- DocumentVersion 更新后的 stale-memory invalidation；
- Reviewer 在真实产品里由谁操作、没有 reviewer 时怎样运行；
- 真实客户/法院需求、Bad Case 和质量收益。

### Decision impact

不把这些缺口升级成新的 Domain/Memory 状态机。优先从 PR #8、PF-030 commits 和 focused test files 恢复字段级 contract 与代表性正反测试；恢复不到的继续写 Unknown。尤其不要借 Coding Agent 项目的 token compression / truncation / Subagent Memory 经验补 Zuno 历史。

若未来真实产品主要从 Matter / Knowledge / Domain 重建案件上下文，应继续让 Long-term Memory 缩回用户/工作偏好、开放问题和阶段性工作上下文，而不是重新争夺案件事实 Authority。

### Retest scenario

只给面试官一个 `prepare_context()` 白板：两个 Matter、同一用户、冲突 APPROVED memory、超长 context、恶意 memory、Memory store timeout。要求逐项说明“历史代码证明 / 需要回源码 / 今天 Target”。

---

## F3 — OpenViking 仍属于 participation-only Claim

- **severity:** S1
- **gap_type:** `EVIDENCE_GAP`
- **trigger_questions:** Batch 001 Q038; Batch 002 B2-Q064/B2-Q065

PF-011 只能支持用户确认参与 OpenViking 在 Memory / Context 区域的接入；公开 Git 没有恢复对应 SDK / Adapter / 数据结构、Build/Buy 决策和运行方式。PF-029/PF-030 不能替代 OpenViking artifact。

### Decision impact

当前 v5 简历没有把 OpenViking 单独作为主 bullet，因此不需要立即修改。面试中若主动提及，只说参与接入；除非恢复 artifact，不升级成“主导 OpenViking 集成”“设计整体 Memory 架构”或“生产使用”。

---

## F4 — Batch 001 的 Red source-policy 违规已在 Batch 002 修正

- **severity:** S2 at Batch 001; `RESOLVED_FOR_ROUND_PROCESS`
- **gap_type:** `EVIDENCE_GAP`
- **scope:** `ROUND_PROCESS`, not Zuno Architecture
- **trigger_questions:** Batch 001 Q061/Q062

Batch 001 Red 使用了不在固定 Zuno base / manifest source set 内的 #212 diagnostic premise。Blue 正确拒绝，Verifier 判 `UNSUPPORTED_CLAIM`。Controller 随后将 Red project source policy 写回 manifest：Red 可以查看固定 Zuno base 作为“目前建立的项目”，但 Current-specific premise 必须能回到 fixed base 或显式 admitted source，不能使用聊天记忆、旧 summary 或 closed diagnostic branch。

Batch 002 没有再次出现 unsupported Current premise，说明本轮 process correction 生效。

### Decision impact

这是 Harness 修正，不产生 Knowledge Architecture Finding。未来若要测试 #212，必须先把证据显式加入 Round source 或 canonical Evidence。

---

## F5 — 两个最强个人实现都缺“进入哪次真实法院/Pilot版本”的版本映射，个人工程结果无法升级成用户结果

- **severity:** S2
- **gap_type:** `PROJECT_REALITY_GAP / MEASUREMENT_GAP`
- **trigger_questions:** Batch 002 B2-Q032/B2-Q069/B2-Q071–B2-Q073

PF-032 和 PF-029/030 都已经能证明真实 main-history 工程行为，但目前没有证据回答：

```text
这项改动由哪个真实需求 / Issue 驱动？
→ 谁 Review / 验收？
→ 进入了哪个 Demo / Court-side Testing / Pilot build？
→ 对真实用户的哪项任务产生了什么结果？
```

因此“真实项目代码”是可证明的，“真实法院用户因此获得某个收益”仍不可证明。这个缺口比继续增加 Target 架构细节更影响面试项目可信度。

### Decision impact

后续项目取证优先级应从 Architecture 继续下钻到**版本—任务—用户结果**：寻找 release/build、Demo材料、任务/Issue、Review、真实 Bad Case、Pilot环境或运行记录。恢复不到时，简历继续把结果写成 code/test boundary，不写用户收益。

---

## F6 — 简历项目名“法律智能 Agent 平台”仍可能把面试官预期抬到完整平台 Ownership

- **severity:** S1
- **gap_type:** `RESUME_CLAIM_RISK`
- **trigger_questions:** Batch 001 Q007; Batch 002 B2-Q082

最新 Project/Architecture 已把长期产品中心从 Agent Chat 转为可验证 Case Workspace / Legal Backend，并把 Generic Agent Harness 降为可替换基础设施。v5 简历标题仍是“Zuno：法律智能 Agent 平台”。正文已经用“在已有系统基础上参与 Agent、Memory / Context、Tool Calling 与数据调试”限制个人 Claim，因此当前没有事实错误，但标题可能让大厂面试官先验地按“完整 Agent 平台 Owner”追问。

### Decision impact

不在本 Red Round 直接改简历。后续 Resume task 可比较两种策略：保留历史项目名但开场立刻限定个人范围；或将副标题改为“智慧司法 AI / 法律智能工作系统”以降低错误先验。任何修改必须保持项目真实名称/历史定位。

---

## F7 — 数据库调试 bullet 证据强度显著低于前两条，适合作为辅助而不是独立亮点

- **severity:** S1
- **gap_type:** `EVIDENCE_GAP / RESUME_CLAIM_RISK`
- **trigger_questions:** Batch 002 B2-Q078

PF-013 只支持“进入 PostgreSQL 查看或调试过实际数据”，未恢复具体表、SQL、故障、修复和结果。因此该 bullet 能说明候选人接触真实项目数据和状态排障，但无法经受与 PF-029/PF-032 同等深度的技术追问。

### Decision impact

后续若能恢复一个具体 DB debugging incident，再升级；否则保持辅助描述，不分配与 Tool/Context 相同的面试时间。

---

## Stable non-findings after 200 questions

两批共 200 问后，没有发现新的总体 Architecture contradiction。以下主题在高压追问下能够由允许文档给出来源支持、同时保持事实层级：

- History / Current / Target / Unknown；
- Pilot != Production；
- LIPLAB research != personal implementation ownership；
- Research Artifact → Capability → Provider → Qualification → Candidate → Formal Business Fact；
- Case Workspace is projection, not a new Authority；
- Conversation / Memory != case database；
- retrieval miss != absence；
- GraphRAG baseline / ablation / kill condition；
- Checkpoint != Domain completion proof；
- Retry / Replan / Reconcile；
- irreversible Domain / external Effect history；
- Effects/Security Slice C positive evidence and confirmed violations；
- HumanDecision != automatic ground truth；
- Release Eval != Production qualification；
- Generic Agent Harness / LangGraph primitives should be reused；
- Native Runtime / persistent Multi-Agent / GraphRAG remain measurement-gated；
- logical responsibility != microservice deployment；
- project-derived Python/PostgreSQL/RabbitMQ/idempotency/network/cache/version/fencing/backpressure fundamentals。

A PASS here means “Blue can answer from allowed sources”, not “the Target is fully implemented”.

## Why the Round stops after two batches

The stop condition is met. Batch 001 established broad architecture and evidence boundaries. Batch 002 concentrated 100 additional questions on the remaining personal implementation risks and produced stable, repeated evidence ceilings. A third 100-question batch would mostly restate the same unrecovered fields / historical project facts rather than change a design or evidence decision.

The next productive actions are independent Blue repair / evidence-recovery tasks, followed by a Red retest with different questions. The active Red Round must not repair its own findings.
