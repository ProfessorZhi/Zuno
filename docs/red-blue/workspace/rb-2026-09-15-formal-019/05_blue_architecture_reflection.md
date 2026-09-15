# Blue Final Architecture Reflection — rb-2026-09-15-formal-019

status: `COMPLETE`

本反思在 Red Final 提交以后，读取两轮公开 Q/A、两份 sealed Blue architecture notes，以及固定 `zuno_base_sha` 的 Architecture / Modules / ADR / Evidence。它判断真实系统缺口，不替候选人重算 Red verdict。

## Executive conclusion

本轮没有证明 Zuno 应升级成 Multi-Agent、更多服务或更复杂 GraphRAG。相反，现有 **Generic Host / Single Agent + Zuno Legal Backend + measurement-gated Native Runtime** 的总体方向经受住了 subtraction test。

真正暴露出的重点是：

1. **1 个有条件成立的 Architecture Gap**：Long-term Memory / Context 的状态 Owner 与 Authority 没有在九模块架构中完全落位。
2. **3 个高优先级 Doc / Narrative Gap**：Tool/Capability 版本依赖链、Effect Current 恢复事实、Context trace 的非权威边界。
3. **2 个已经有负向 Evidence 的 Implementation Blocker**：Effect Reconciliation 最终收敛缺失；`MANDATORY_BEFORE_EFFECT` durable audit gate 未接入现实发送边界。
4. **GraphRAG / direct route / Multi-Agent 主要是 Evidence 与删除条件问题**，不应靠新增架构对象解决。

---

## F1 — Long-term Memory / Context 缺少一个完整的 Target Authority 归属

classification: `ARCHITECTURE_GAP`（仅当 Zuno 继续保留 structured long-term Memory 作为 Target 能力时）
priority: `P0`

### 暴露方式

Red2 从 `MemoryScope` 一直追到：谁有权扩大 scope、谁能把 candidate 变成 APPROVED、reviewer 是否有 scope 权限、权限撤销发生在 ContextPack build 以后怎么办、冲突/过期/删除由谁决定。

### Canonical 文档现状

总体九模块 Authority Matrix 没有一行拥有 long-term Memory record / promotion / current-version truth。04 Runtime 明确写着 **does not own long-term Memory truth**；08 Security 拥有 Authorization、SecurityEpoch 和 Effective Lifecycle Policy；跨模块 reference 又把 `Memory / Context` 定义为 **Optional Provider Boundary**，不覆盖 Domain / Security truth。

这几个判断单独都合理，但合起来仍缺一个问题的直接答案：

> 一条非 Domain 的 structured memory record 谁保存、谁决定“当前可召回”、谁记录 review/provenance、谁负责 supersede/conflict/delete 的耐久事实？

历史 V2 的 `APPROVED` contract 恰好把这个缺口暴露出来：如果 `APPROVED` 被理解成“事实是真的”，它越权；如果只是“允许召回”，它又应受 08 的 recall/lifecycle policy 控制。

### 最简单修法

**不增加第十个业务模块。** 默认保持 Memory 为 Optional Provider Boundary：

- Memory Provider / Store 只拥有自己的 record、source refs、provider-local version/index facts；
- 08 拥有当前 recall eligibility、scope authorization、retention / no-recall / purge / legal-hold policy；
- 01/04 只消费经过当前授权的 Context/Memory snapshot，不拥有 long-term memory truth；
- 02 继续拥有真正的法律业务事实；Memory 内容无论是否 reviewed，都不能直接升级为 Domain truth；
- “reviewed / approved memory”在 Target 文档里必须明确是**召回资格 / 人工治理事实**，不是专业事实认证。

如果这套边界仍然显得比业务收益更复杂，删除 structured long-term Memory Target，只保留 Raw Event + Task Summary + Context assembly，等 A/B 证明跨会话收益以后再恢复。

### 成本与退出条件

成本主要是补 contract、lifecycle 和 freshness guard，而不是新服务。若跨会话任务 A/B 无稳定收益，关闭 long-term Memory extraction/promotion/retrieval，Architecture Gap 随之消失。

---

## F2 — Tool / Capability / Config / Credential 的版本依赖链分散，缺少一条容易执行的跨模块故事

classification: `DOC_GAP`
priority: `P0`

05 已有 `CapabilityVersion / ProviderBinding / config_version_ref`；06 有 `ToolVersion / PreparedAction`；08 有 `CredentialVersion / SecurityEpoch`；04 有 `StepRun.resolved input-version set`。Owner 本身并不冲突。

问题在于这些事实分散在四篇 reference 中。面对下面的真实故障，读者需要自己拼完整答案：

```text
模型按 Tool schema/config v1 规划
→ Server schema 或 Credential/config 变成 v2
→ 旧 Step 还没 dispatch
→ 到底继续、拒绝、Retry 还是 Replan？
```

### 建议

不新增 `ToolSnapshotService` 或新的版本对象。直接把 04 的 `resolved input-version set` 写清楚，至少可引用：

- CapabilityVersion / ProviderBinding / semantic config version；
- ToolVersion / operation contract；
- KnowledgeGeneration / relevant DocumentVersion；
- SecurityEpoch；
- CredentialVersion / Secret Lease 只按安全要求绑定使用资格。

然后在 Overall Architecture 增加一个 failure window：**plan-time capability snapshot 与 dispatch-time dependency mismatch → fail closed / Replan，不静默参数迁移。**

这会把当前已经存在的设计拼成一条完整故事，不增加新模块。

---

## F3 — Effect Target 设计正确，但 Current 文档没有把已确认的恢复缺陷放到足够显眼的位置

classification: `DOC_GAP + IMPLEMENTATION_GAP`
priority: `P0`

Target 的设计是本轮最稳定的部分之一：`PreparedAction → ToolAttempt → EffectReceipt / OutcomeUnknown → Reconcile`，并明确 Checkpoint 不能证明 Effect。

但固定 base 的 Current Evidence 已经给出比“Gap / 尚未证明”更强的负向结论：

1. UNKNOWN external effect 第一次会正确写成 `reconcile_required`；
2. 重启后同 action/idempotency replay 不会重复 dispatch，这是正向行为；
3. 但上层 Runtime 会把尚未完成 Reconciliation 的 replay 错误升级成 `completed`；
4. Current 有 OPEN reconciliation、escalation 和人工 assessment 记录，但没有发现真正写入 `RESOLVED` 的收敛 writer、remote-query consumer 或 conclusive `ReconciliationReceipt` 路径。

因此 Current 不能只写“unknown external effect → RECONCILE / no blind retry”就结束。它必须同时明确：

> **unknown 能被耐久保存，但 restart replay certainty 仍有错误升级，最终 reconciliation convergence 尚未实现。**

这不是 Target 架构错误；它是一个已经被证据证明的 Current Implementation Blocker，同时也是 Current/Gap 文档表达不够锋利。

---

## F4 — `MANDATORY_BEFORE_EFFECT` Target 已经定义，但 Current send path 有已确认的审计门禁缺口

classification: `DOC_GAP + IMPLEMENTATION_GAP`
priority: `P0`

08 Target 正确区分 `AuditRequirement` 与 committed `AuditPersistenceReceipt`；06 Target 也要求高风险 send 前消费 matching durable audit proof。

Current Evidence 已经证明一个具体反例：Security requirement 存在、durable audit receipt 不存在时，provider executor 仍被调用，Gateway 最终返回 completed 并写出 EffectReceipt。

这说明：

```text
Audit requirement exists
!=
Audit durability gate consumed before effect
```

建议 06 / 08 的 `Current / Gap / Evidence` 段直接引用这条负向事实，而不是仅把 Mandatory Audit 留在未来测试列表里。实现上必须把 matching audit receipt check 接入 send boundary；不能靠 Telemetry 或事后 Trace 补票。

---

## F5 — Context trace / provenance 需要更明确地写成“可解释性证据”，不能被读成正确性证明

classification: `NARRATIVE_GAP + DOC_GAP`
priority: `P1`

历史 Context/Memory V2 对 source ids / policy trace 的改动是合理的，但 Red2 指出了一个重要边界：

> trace 能证明“压缩过什么、来自哪里”，不能证明摘要没有删掉法律限定条件，也不能证明来源内容是真的。

建议在 Overall Architecture / Context 相关叙事里增加一个跨模块不变量：

```text
Provenance / source trace proves origin and transformation history;
it does not prove factual truth, authorization, or semantic preservation.
```

对不可丢失的 legal evidence / policy / current user constraint，优先 stable refs / extractive representation / validation，而不是把自由摘要当 Authority。

---

## F6 — GraphRAG 是 Evidence Gap，不是 Architecture Gap

classification: `EVIDENCE_GAP`
priority: `P1`

当前 Target 已正确把 GraphRAG 定义成 query/evidence/measurement-gated，因此架构不用升级。

真正的问题是 Current implementation 累积了多层 heuristic：

- baseline-preserving fusion；
- threshold 6 / 9；
- candidate-aware seed cap；
- alias normalization；
- path-aware ranking / generic penalty。

只有 fusion 与已观察 ranking displacement 有直接因果关系。其余机制缺 holdout / ablation。

### 下一步

先跑：

```text
Hybrid baseline
→ + fusion
→ + seed
→ + alias
→ + path ranking
→ leave-one-out
```

使用独立 multi-hop holdout，并同时报告 retrieval、answer/citation、fallback reason、latency/token/cost。如果 fusion-only 已经足够，其余 heuristic 应删除，而不是继续复杂化图系统。

---

## F7 — Direct route 不需要进入 Target Architecture

classification: `NO_ZUNO_CHANGE / EVIDENCE_GAP`
priority: `P2`

历史 direct route 是有效的个人工程故事，但没有长期价值 benchmark；固定 base 的 Current runtime evidence 甚至已经说明旧 direct tool execution 路径被移除。

因此架构上不要为它建立 Router Service、独立状态机或新的 Authority。若未来重新使用，最多作为确定性 fast path，最终仍走统一 Tool/Security/Effect boundary，并有明确删除条件。

---

## F8 — Generic Host + Legal Backend baseline 应保留

classification: `NO_ZUNO_CHANGE`

ADR-0008 与本轮 subtraction test 一致：

- 简单 QA → controlled RAG / Generic Host；
- Generic Host 可承担 session、普通 workflow、普通 Tool Calling；
- Zuno 只保留真正需要长期 Authority 的 legal Domain/Evidence/Effect/Security contract；
- Native Runtime 只有 A/B/C 证明增益后才升级。

本轮没有证据支持把 Native Runtime 变成所有任务必经路径。

---

## F9 — Multi-Agent / Specialist 继续 measurement-gated

classification: `NO_ZUNO_CHANGE`

没有出现 Tool、Subgraph、parallel worker 已经在真实 workload 中失败的证据。Single Controller + parallel execution 仍是更简单的默认控制模型。

未来只有在以下问题被测量后才值得升级：独立 Context / Tool / Security policy、长生命周期 recovery、parallel throughput 或明显 context contamination。即使升级，Specialist 仍输出 proposal，正式 Domain/Effect/Security Authority 不迁移给 Agent。

---

## F10 — Current / Target 分离总体表现良好，不建议为了面试压力重写整个架构

classification: `NO_ZUNO_CHANGE`

Architecture Part A 开头明确说明是 Target，Current 只看 Evidence；九模块 reference 也多次写“detail design candidate / implementation not established”。这套事实保护应保留。

需要修的是少数 Current 段落没有同步最新负向 Evidence，以及 Memory Optional Boundary 没有把 Owner 讲到底，而不是重新设计九模块。

---

# Final priority

## P0 — 应进入用户改进审批

1. **Memory / Context Target Authority 收口**：保留 optional provider 时明确 record / recall eligibility / review / lifecycle / Security owner；或在无收益证据前删除 structured long-term Memory Target。
2. **Tool dependency version story**：把 CapabilityVersion / ProviderBinding config / ToolVersion / SecurityEpoch / CredentialVersion 串进 04 resolved input-version set 和一个 schema/config drift failure scenario。
3. **Current Effect recovery 文档纠偏 + implementation plan**：明确 restart replay certainty bug 与 reconciliation convergence 缺失。
4. **Mandatory Audit Current 文档纠偏 + implementation plan**：明确 missing durable audit proof 仍能 dispatch 的已确认 blocker。

## P1 — 先测量再决定

5. GraphRAG 正式 ablation / independent holdout；根据结果删除不增益 heuristic。
6. Context provenance 非 truth / 非 semantic-preservation 的文档边界。

## P2 — 不改架构

7. direct route 仅作为历史 / 可删除优化。
8. Multi-Agent 不升级。
9. Generic Host + Legal Backend baseline 保留。

## 这轮最重要的架构结论

面试压力没有证明 Zuno “不够复杂”。它证明了相反的事情：**现在真正需要修的是少数 Authority / Current-recovery 闭环，以及把已经存在的版本与安全事实连成一条可执行故事；GraphRAG、Memory、Multi-Agent 等复杂机制继续必须为自己的存在负责。**
