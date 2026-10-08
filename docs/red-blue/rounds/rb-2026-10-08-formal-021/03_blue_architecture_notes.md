# Blue Wave 1 — 架构初诊（Architecture Notes）

```text
round: rb-2026-10-08-formal-021
artifact: 03_blue_architecture_notes
role: Blue Team — Architecture Reviewer
sealed: true
readable_by: Blue Architecture Reflection only
base_sha: cdd2063b341e6919fafaa1395d1f3bdc837329f6
head_observed: 97bdd0dbc5f9bce5929291ab173aac2df41731d1

inputs:
  - 01_simulated_resume.md
  - 02_red_questions.md
  - 03_blue_answers.md
  - 00_manifest.yaml
  - .agent/red-blue/defense-model.md
  - AGENTS.md
  - docs/README.md / docs/project/ / docs/architecture/ / docs/modules/ / docs/decisions/ / docs/evidence/ / docs/governance/
  - src/backend/zuno/** , tests/** , tools/**
```

```text
审计声明（诚实边界）：
1. 本诊断只把 03_blue_answers.md 当作"候选人口径"，所有结论都回到 canonical source
   （docs/architecture/reference.md、docs/modules/reference.md、docs/modules/*/README.md、
   docs/governance/*、docs/evidence/*、src/**）重取。
2. 本轮对 docs/ 做过一次跨目录 grep（用于定位 ContextOrchestrator / direct-route / ReAct
   在 canonical 文档里的出现位置）。该 grep 的输出顺带带回了 docs/red-blue/rounds/** 与
   本轮 workspace 内其他文件的若干片段。这些片段 **没有** 被用作任何 finding 的证据，
   本诊断也未引用任何历史轮次的结论；凡涉及"上一轮已判过什么"的推断，本文件一律
   从 A 系列回答 + canonical source 重新推导。
3. 本文件的 finding 只分四类：ARCHITECTURE_GAP / IMPLEMENTATION_GAP / EVIDENCE_GAP /
   ANSWER_QUALITY（含 DOCS_GAP）。升级到 ARCHITECTURE_GAP 的门槛见 §0。
```

---

## §0 判定门槛与分类口径（先立规则，再下判断）

**只有下列问题本身不成立，才倾向判 `ARCHITECTURE_GAP`**：Owner、Authority、State semantics、
Contract、Recovery、Security Authority、Build / Buy 因果、复杂度缺乏可删除 / measurement gate。

本文件额外加两条自约束，防止把"没做到"误升成"设计站不住"：

```text
A. 设计已给出 Owner 与 Contract，只是 Current 没实现  → IMPLEMENTATION_GAP
B. 缺少一份文档 / 没做一次 benchmark / 候选人一时答不上 → DOCS_GAP / EVIDENCE_GAP / ANSWER_QUALITY
C. 只有当"两条被接受的来源对同一事实给出互斥答案"，或"某条被声明的不变量在
   Current 里连落点都不存在"时，才升到 ARCHITECTURE_GAP
```

本轮同时尊重以下已核事实约束，不把它们当作"仍存在的缺陷"：
`IMP-020-01/02/03` 已在 base 落地；`docs/evidence/current-eval-baseline.md` 的
`MEASUREMENT_BLOCKED` 是**整个 eval 层**的状态，不是 GraphRAG 专属；GraphRAG 的
holdout 与 leave-one-out 未执行，`docs/governance/rb019-graphrag-ablation-protocol.md`
= `BLOCKED_PENDING_DATA`；`ContextOrchestrator` 在 `src/` 内无生产调用点；commit 作者字段
区分不出个人与团队。

### 结论摘要

| 编号 | 主题 | 分类 | 一句话 |
| --- | --- | --- | --- |
| F-01 | Workspace 准入边界（direct route / complex） | **ARCHITECTURE_GAP** | 一条改变执行语义的准入门没有 Authority，且 shipped composition 下 complex 臂不可达，违反 B1 不变量 #3 |
| F-02 | 远端 Effect 收敛 | IMPLEMENTATION_GAP（已登记） | 无 background reconciler，自动 remote query `DEFERRED_BY_PROVIDER_CAPABILITY`，当前人工兜底 |
| F-03 | AUD-L2（send 后 crash/restart 的 audit lifecycle） | IMPLEMENTATION_GAP（已登记） | AUD-L1 已 verified，L2 明确 `NOT IMPLEMENTATION-PROVEN` |
| F-04 | 幂等键的 `salt` 契约 / provider 侧 uuid 幂等键 | CONTRACT 问题（需复测） | `salt` 无契约文档；另有一处 provider 侧幂等键用 `uuid4().hex` |
| F-05 | 9 条检索启发式无已执行的 measurement | **EVIDENCE_GAP**（明确不升级） | gate 已存在且冻结，缺的是数据，不是 gate |
| F-06 | 逐条 heuristic 的可消融性 | **conditional ARCHITECTURE_GAP** | H1 依赖 `_graph_signal`，而该信号由 H7/H8/H9 的产出构成 → 共享状态可能使"逐条关闭"物理上不可归属 |
| F-07 | "GraphRAG 只面向英文 / 中文法律语料无测试用例" | ANSWER_QUALITY + EVIDENCE_GAP | 平台存在中文合同结构抽取器与中文合同图测试；真实缺口只在 alias/fusion/path 三个启发式 |
| F-08 | Recall eligibility 的 08 门 | IMPLEMENTATION_GAP（安全相关） | 架构要求"消费 current eligibility"，Current 无该 decision surface，替代品是 stored `review_status` + scope 相等 |
| F-09 | `ContextOrchestrator` 与真实装配入口 | DOCS/ANSWER + CLEANUP | 无 consumer、canonical docs 从未命名它；简历仍读作"统一入口" |
| F-10 | MemoryScope 第四维 `agent_id` | SEMANTICS_GAP（小） | runtime 固定为字面量 `"agent_run"`，四维身份在 Current 实际是三维 |
| F-11 | 冲突 memory 无语义仲裁 | **NOT A GAP**（by design） | memory 非权威，02 拥有 truth，冲突不在这层解决是设计 |
| F-12 | staleness 无刷新 owner | OWNER_QUESTION（小） | 排除逻辑依赖已写入的状态位，无 reaper，无 freshness 校验 |
| F-13 | Runtime 恢复权威 / late result / Build-Buy | **NOT A GAP** | Owner-first recovery、ADR 0007/0012 自洽；Current 部分实现 |
| F-14 | Pilot / 法院 / GraphRAG 中文泛化 | **NOT A GAP**（无可用证据） | 全部 Unknown，边界表述正确 |
| F-15 | `KnowledgeGeneration` / `ReadinessDecision` | **NOT A GAP**（已登记 Gap） | Target 概念，`src/` 无实现，knowledge README Gap 段已登记 |

**ARCHITECTURE_GAP 计数：1 条确认（F-01）+ 1 条条件性（F-06，取决于下一轮复测）。**

---

## §1 F-01 — Workspace 准入边界没有 Authority，且 complex 臂在产品组合下不可达

**Red signal 是什么？**
Q7（Subtraction Test）、Q8（分流判据由谁判）、Q14 / Q75（Build/Buy 的真实 delta）、
Q56（这条边界由谁拥有最终解释权）。A8 与 A56 给出了同一个答案：判据是**规则**；`complex`
需要一个注入的 DAG planner，而产品组合里是 `None`，所以复杂请求**fail closed**；
"这条边界由谁拥有最终解释权"= **Unknown**（`docs/decisions/` 里没有相应 ADR）。
简历第 1 条把这条边界写成了核心交付物："目标与参数明确的一步请求走 direct route，
复杂请求进入 ReAct 路径"。

**canonical source 怎么说？**
- 准入实现（已实测）：`platform/services/workspace/simple_agent.py:2032/2080`
  `plan_kind = "tool" if resolved_tool_id else self._plan_kind_for(original_query)`；
  `_plan_kind_for` 在 `:2149-2157`，命中 token 表
  `("compare","across","conflict","multi-hop","multihop","analyze","synthesize","报告")`
  即返回 `"complex"`，否则 `"simple"`。全部是子串匹配，无模型参与。
- 准入拦截（已实测）：`platform/services/workspace/single_controller_runtime.py:737-738`
  `complex_unbound = plan_kind == "complex" and self._dynamic_dag_planner is None`；
  `:814-818` 置 `admission_reason = DYNAMIC_PLAN_RUNTIME_NOT_BOUND`（常量定义在 `:103`）
  并 `return self._blocked_request(...)`。该处注释写明这是一次刻意的 PHASE22 修复：
  "an unbound composition must never fake a fixed three-step DAG or fall back to a direct answer"。
- 产品组合（已实测）：`src/backend/zuno/main.py:113` `dynamic_dag_planner=None`。
- canonical 架构：`docs/architecture/reference.md` B1 不变量 #3 =
  "Native Runtime entrant 一定有 Plan：简单单步，复杂 Dynamic DAG"；B4 Profile B = 复杂法律分析
  走 `04 AgentRun + immutable PlanVersion → … → 02 Formal Admission`。
  **canonical 的 9 模块 / ADR / reference 里没有 "direct route vs ReAct 准入门" 这个概念**；
  `docs/governance/project-fact-provenance.md` PF-012 只把它记为 2026-04-28 的**历史**事实
  （"Workspace MCP direct-route hardening"）。

**这是回答问题就能解决，还是系统本身的问题？**
系统本身。三条被接受的描述对同一事实给出互斥答案：
```text
简历第 1 条：复杂请求 → ReAct 路径
架构 B1 #3 / B4 Profile B：复杂请求 → Dynamic DAG（immutable PlanVersion）
今天代码：复杂请求 → admission block（DYNAMIC_PLAN_RUNTIME_NOT_BOUND，无回落）
```
同时这条边界的判据**没有 owner**：没有 ADR、没有模块 reference 条目、没有 decision record，
"解释权"落在一张 `_plan_kind_for` 的字符串表上（A56 自己承认）。

**Current / Target / Evidence / Unknown**
- CURRENT：`tool` / `simple` / `complex` 三值准入；complex 在 shipped composition 下被
  `_blocked_request` 拦下，注释明确不允许回落；`报告` 这个中文词会把一次普通 workspace 请求
  翻成 complex。全部有 file:line。
- TARGET：B1 #3 + B4 Profile B —— complex 必须落到 immutable PlanVersion 的 Dynamic DAG。
- EVIDENCE：无。没有任何 Eval / fault probe 覆盖"哪些请求被判 complex / 被拦多少"。
- UNKNOWN：拦下后产品面呈现什么（是否被上层包装成用户可见失败）；`report/direct-route`
  准入边界在设计上应由 01 还是 04 拥有；computed 的 `complex` 是否在任何已知产品场景下
  真的产生过一条合法 Dynamic DAG。

**最简单方案是什么？**
1. 承认这条边界是 01/04 之间的一个**准入契约**，给它一个 owner 与一份最小 decision record
   （不必是完整 ADR，可以是模块 reference 的一个 B14 Guard 条目）；
2. 在 ownership 未定之前，把 `_plan_kind_for` 的 token 表降级为"路由提示"，并按 B1 #3
   明确：产品组合未绑定 planner 时，complex 请求的对外语义是**受控拒绝**，不是"进 ReAct"；
3. 修简历措辞，使其与 B1 #3 一致。

**当前设计在哪里失败？**
不是"规则不如模型"——规则准入是可辩护的简化。失败点在：**一条改变执行语义与授权路径的
准入决定没有 Authority，而且它的 complex 臂在 shipped composition 里不可能成立**。
B1 #3 说"Native Runtime entrant 一定有 Plan"，但当前组合既产不出 Dynamic DAG，
也不允许回落，于是这条不变量在产品面无法被满足。这是 Owner + Contract 层面的站不住。

**是否真的需要 Architecture Revision？**
需要，但只需要**最小**的一次：把准入边界写成 01/04 的契约并指定 owner，然后要么绑定 planner，
要么把"complex 未绑定 = 受控拒绝"正式写进 Target。不需要新增模块或状态机。

**有没有更简单替代？**
有：把 `_plan_kind_for` 的 complex 判据删掉，让所有 workspace 请求都走 `simple` 单步路径，
只保留 `tool` 直连；等到真正有 Dynamic DAG 需求时再引入准入分层。这比"维持一个不可达的
三值准入"更少状态，也与 B12 的 Delete 判据一致（复杂机制无测量支撑则不做）。

**增加什么成本？**
最小方案成本 = 一份 decision record + 一处措辞修正，接近 0 代码。替代方案成本 = 放弃
"复杂任务"这个产品叙事，需要产品侧同意。

**退出条件是什么？**
当且仅当以下之一成立时应关闭该 gap：(a) 产品组合绑定了 Dynamic DAG planner 且
B4 Profile B 端到端可跑；或 (b) 接受一次 Architecture Revision，把 complex 的对外语义
正式定义为受控拒绝并记录。

**下一轮如何复测？**
① `grep -rn "dynamic_dag_planner" src/backend/zuno/main.py` 确认仍为 `None`；
② 对 `_plan_kind_for` 的 8 个 token 各造一条真实 workspace 请求，记录是否得到
`DYNAMIC_PLAN_RUNTIME_NOT_BOUND`（可执行的确定性验证）；
③ 在 `docs/modules/` 或 `docs/decisions/` 里确认是否出现了准入 owner 记录。

---

## §2 F-02 — 远端 Effect 收敛是人工兜底（已登记，不上调）

**Red signal**：Q11–Q13（timeout 语义 / 幂等 / remote effect 归属）、Q48–Q50（unknown effect /
对账 / external reality）。A11–A13、A48–A50。

**canonical source**：`docs/governance/effect-remote-query-reconciliation-status.md`
（`DEFERRED_BY_PROVIDER_CAPABILITY / MANUAL_CONCLUSIVE_FALLBACK_CURRENT`）；
`docs/evidence/README.md`「UNKNOWN EFFECT RESTART REPLAY: FIX VERIFIED / UNKNOWN PRESERVED」；
`docs/modules/reference.md`「Recovery 时先找 Owner Fact」表；`docs/architecture/reference.md` B6
"外部动作是否发生 = EffectReceipt or conclusive ReconciliationReceipt"。
A49 的 `age_escalation_after_seconds=900` 与
`platform/database/tool_runtime/domain.py:1577 record_manual_effect_assessment` 与之相符。

**判定**：Owner 明确（06 拥有）、Contract 明确（unknown 不得映射成 Failed、不得盲重试）、
缺口有独立 governance 文档登记。→ **IMPLEMENTATION_GAP，不是 ARCHITECTURE_GAP**。
这正是 §0 规则 A 的样本：设计已回答"谁拥有、怎样算完成"，只是 Current 还没有自动收敛能力。
900 秒阈值是手定常数，属 EVIDENCE（无 calibration），并入 F-05 的同一类问题。

**下一轮复测**：确认 `docs/governance/effect-remote-query-reconciliation-status.md`
的状态是否从 DEFERRED 变化；确认 reviewer role / tenant / approval-policy 的 authoritative
binding 是否仍未被证明（A49 自述的边界）。

---

## §3 F-03 — AUD-L2 仍未证明（已登记，不上调）

**Red signal**：Q46（audit-before-effect）、Q47（crash window 谁收敛）。A46、A47。

**canonical source**：`docs/evidence/README.md`
「MANDATORY AUDIT PRE-SEND ABORT: AUD-L1 SELECTED VERIFIED」「AUD-L2 NOT IMPLEMENTATION-PROVEN」；
`docs/modules/reference.md:314` 明确"manual judgment Authority、audit class、AUD-L2 crash/restart
lifecycle 与 Target composed SecurityEpoch 继续保持 Gap"。A46/A47 的 file:line
（`invocation_gateway.py:1426-1527`、`:1529`、`:1551`）与 canonical 一致。

**判定**：**IMPLEMENTATION_GAP**。Owner（06/08）与 Contract（缺 proof 就 fail closed；
`dispatch_aborted` 不伪装成 `effect_observed`）都成立；RED 的窄窗口已转正。
不上调的理由：这是"没做到"，不是"设计不成立"。

---

## §4 F-04 — 幂等键的 `salt` 没有契约；另有一处 provider 侧幂等键用 `uuid4().hex`

**Red signal**：Q12（有副作用 Tool 重试如何收敛成幂等）、Q93（idempotency key / 去重）。
A12、A93 都以
`idem:{tenant_id}:{workspace_id}:{run_id}:{step_run_id}:{tool_name}:{salt}`
作为"动作身份"，并宣称 same key + same action hash → 复用；same key + different hash → conflict。

**canonical source（已实测）**：
- `capability/mcp/mcp_tool_executor_adapter.py:70-74`：
  `def idempotency_key(self, *, tool_name: str, salt: str = "") -> str` —— `salt` 是一个
  **调用方可选参数，默认空串**，没有任何 docstring / 类型约束 / 测试说明它的允许取值范围。
- 唯一的生产调用点 `platform/services/workspace/simple_agent.py:217`：
  `salt=str(getattr(binding, "name", "") or resolved_tool_id)` —— 今天传的是 binding 名，
  对同一步骤的重试是稳定的，**所以当前不会破坏去重**。
- 但同一 capability 树下另有一处：
  `capability/mcp/servers/lark_mcp/mcp_tool/calendar_event/create_calendar_event.py:57`
  `.idempotency_key(uuid.uuid4().hex)` —— 用**每次新建的随机 uuid** 作幂等键。

**这是回答问题就能解决，还是系统本身的问题？**
偏系统。`docs/modules/reference.md` 的不变量写的是
"Same correlation id != same idempotency namespace"，并要求
"same key + different action hash 必须冲突失败"。而这里"什么可以进 key"没有契约：
一个以 `salt` 命名的自由分量挂了在同一条 key 上，既无 owner、也无测试锁定它的稳定性。
`uuid4().hex` 那一处更直接：如果它确实是 provider 侧的幂等键，随机值等于放弃 provider 去重。

**Current / Target / Evidence / Unknown**
- CURRENT：key 形如上述模板；`salt` 默认 ""，当前生产传 binding 名（稳定）；`uuid4` 幂等键
  存在于 lark calendar create 工具路径。
- TARGET：幂等 namespace 按边界分离，key 必须稳定到能识别 duplicate logical work
  （B8 / B9 / 跨模块 reference）。
- EVIDENCE：`docs/evidence/README.md` 的 restart replay / unknown-effect 正向证据覆盖了
  本地幂等；**没有**任何证据覆盖"`salt` 变化时 key 是否应当变化"。
- UNKNOWN：`create_calendar_event.py` 的 `.idempotency_key(uuid4().hex)` 是 provider 请求
  的真实幂等键，还是一个普通 request-id（若是前者则为实缺陷）；`salt` 的合法取值范围；
  是否存在第三个传 `salt` 的调用点。

**最简单方案是什么？**
两条：① 把 `salt` 改名为语义明确的名字（如 `binding_identity`）或直接从 key 模板里删掉
（`tool_name` 已足够区分），并加一条测试锁定"同一步骤重试产生同一 key"；
② 对 `create_calendar_event.py:57` 判定该 uuid 的角色，若它是 provider 幂等键则改为
由 06 的 action identity 派生。

**当前设计在哪里失败？**
失败在"幂等身份"这个 Contract 的关键分量是可选的、未命名的、未被测试的。它今天恰好稳定，
但没有任何机制阻止未来某个调用点传入变化的 `salt`——那时去重会**静默失效**，
而不是 fail closed。

**是否真的需要 Architecture Revision？**
不需要。这是一次 contract 收紧 + 一条测试。

**增加什么成本？**
极低。若要改 `salt` 的形态，需回看它的唯一生产调用点（已知只有一处）。

**退出条件是什么？**
`idempotency_key` 的参数集被限定为稳定身份（或 `salt` 被移除），且存在一条
"同一 step 重试 → 同一 key" 的测试；`uuid4` 幂等键的角色被判定并记录。

**下一轮如何复测？**
① `grep -rn "salt=" src/backend/zuno --include=*.py`（本轮结果：2 处，见上）；
② 打开 `create_calendar_event.py` 上下文，确认 `.idempotency_key(...)` 的去向；
③ 在 `tests/` 内搜是否存在锁定 key 稳定性的用例（本轮未发现）。
**注意**：这是"需要复测的契约问题"，**不是**已确认缺陷；在拿到 ② 的结论前不要写成缺陷。

---

## §5 F-05 — 9 条检索启发式没有已执行的 measurement（EVIDENCE_GAP，明确不升级）

**Red signal**：Q18（门槛怎么定的）、Q21（holdout 为什么没跑）、Q22 / Q73 / Q74（逐个删谁）、
Q26 / Q68（kill condition）、Q86（无 ablation 凭什么保留）、Q25（latency / token 成本）。

**canonical source**：
- `docs/governance/rb019-graphrag-ablation-protocol.md`：`status: FROZEN_PROTOCOL`、
  `measurement_status: BLOCKED_PENDING_DATA`；§2 给出保留 / 删除判据；§3 逐条列出 H1–H9 及
  关闭方式；§5 要求冻结 split、≥300 题；§8 列出三个阻塞条件。
- `docs/evidence/current-eval-baseline.md`：整层 `MEASUREMENT_BLOCKED`
  （"固定 benchmark 目前没有可用的外部实际数据"——**不是 GraphRAG 专属**）。
- `docs/modules/reference.md:244` B1 #10 / `docs/architecture/reference.md` B12：
  "Extend only when measured constraints appear"，GraphRAG 等均 measurement-gated。
- 实现（已实测）：`platform/services/retrieval/fusion.py:9` `GRAPH_PROMOTION_THRESHOLD = 6`，
  `+3`（即 9）内联出现在 `:183/:200`；`_candidate_group` `:166-187`、`_baseline_rank`
  `:189-202`、`_rank_key` `:951-977`、`merge` `:979-1073`、`_graph_signal` `:156-163`、
  三个 guardrail `:755-812 / :814-874 / :876-949`。仓库内**不存在**任何 calibration / ablation
  结果文件或配置来支撑 6/9。
- `docs/modules/knowledge/README.md:99` Gap 段已登记："GraphRAG 按 query class 的
  holdout / ablation … 仍需要验证"。

**这是回答问题就能解决，还是系统本身的问题？**
回答问题解决不了，但**也不是架构站不住**。关键在于 §0 规则 B：**gate 已经存在**——
它被写成了冻结协议、有 owner（03 + 09）、有明确的删除判据与解锁条件。缺的是数据。
把"没跑 benchmark"升级成 Architecture Gap，会与本届规则正面冲突。

**Current / Target / Evidence / Unknown**
- CURRENT：H1–H9 随默认 `merge()` 生效；阈值手定；`fusion_score` 被算出来但只写进 metadata、
  不参与排序（A17/A97 自述，与 `_rank_key` 的键序一致）。A68 承认"举不出一个
  删掉图路由会变差的 query"。
- TARGET：B12 + 冻结协议 §2 —— 无稳定增量即删；删除是合法终点。
- EVIDENCE：`normal vs enhanced` 只证明"不劣于基线"；5 条 smoke 的 rerun 里
  **baseline 自己的 `MRR@10` 也从 0.90 变成 1.00**（`PF-031` 原文已写），所以"不再低于
  baseline"在小样本上区分不出机制与噪声。
- UNKNOWN：每条 H 的真实边际贡献；token 成本（A25 明确 Unknown）；中文法律语料上的方向。

**最简单方案是什么？**
不动架构，只做两件工程事（都已在协议里）：
① 按 §3 确保每条 H 都有可关闭开关（协议已列出关闭方式）；
② 数据可用时按 §6 跑 leave-one-out，按 §2 判保留 / 删除——**包含"一条都不留"这个合法终点**。

**当前设计在哪里失败？**
在一个更精确的点上：**这 9 条不是"先设计后测量"，而是"先修 bug 后补协议"**。
`merge()` 是一层叠一层的启发式（分组 → 下限 → guardrail 硬替换 top），
复杂度已经在默认路径上生效，而它的保留判据被一个当前不可执行的协议 gate 住。
这不是设计矛盾（协议就是为它写的），而是**已知未收敛的复杂度债**。

**是否真的需要 Architecture Revision？**
不需要。需要的是执行协议。但若 F-06 成立（见 §6），则需要设计层面的一个小小的可删除性改造。

**有没有更简单替代？**
有，且协议已经承认：删除全部 9 条、回到普通 hybrid / vector 检索，是"可接受结论"
（协议 §2 末句）。A69 也自己说："如果 holdout 测下来打不过更简单的 baseline，
那『权重 0 / 删掉』就是更简单也更正确的答案"。

**增加什么成本？**
执行成本 = 数据集接入 + 冻结 split + 可运行索引 + 模型凭证（协议 §8 的三个阻塞项）。
**不执行**的成本 = 继续携带一层无收益证明的复杂度，并让每一次 Red 追问都落在
"你凭什么保留"这个没有答案的位置上。

**退出条件是什么？**
协议 §2 逐条判决完成，或整层被判退回 hybrid。任一方向成立后，F-05 关闭。

**下一轮复测？**
① `docs/evidence/current-eval-baseline.md` 与协议 §8 的状态是否改变；
② `docs/modules/knowledge/README.md:99` 的 Gap 列表是否仍在；
③ `fusion.py:9` 的 `GRAPH_PROMOTION_THRESHOLD` 是否仍为无 calibration 的裸常数；
④ 是否出现了任何 `full-minus-H` 的落盘结果。

---

## §6 F-06 — 逐条 heuristic 的可消融性未证明（conditional ARCHITECTURE_GAP）

**Red signal**：Q22（leave-one-out 预期谁掉最多）、Q74（只能留一个留谁）、Q86（无 ablation
凭什么保留）。A22 / A73 / A74 / A86 都给了**预测**并明确标成预测。

**canonical source**：
- 协议 §3 的前提是"每条启发式需要一个可关闭开关"，即**假设 H1–H9 可独立关闭**。
- 实现（已实测）：`_graph_signal()`（`fusion.py:156-163`）= 四个计数器的整数和
  （`graph_support_count + graph_seed_hit_count + graph_file_focus + graph_path_count`），
  而 `_candidate_group()`（`:166-187`）用这个和与 `GRAPH_PROMOTION_THRESHOLD` 决定候选分组。
  于是 **H1（promotion threshold）的输入由 H7（seed expansion，产生 seed_hit）、
  H9（path-aware ranking，产生 path_count）的产出构成**。

**这是回答问题就能解决，还是系统本身的问题？**
这是**可能**的系统问题，也是本轮唯一一条可能需要第二次 Architecture Revision 的地方。
如果 H7 / H8 / H9 的关闭会改变 H1 的输入分布，那么"只关 H1、其余不变"这个实验臂
在物理上不是"其余不变"——判决结果不可归属，协议 §2 的判据无法被真正执行。
按 §0 的"复杂度缺乏可删除 / measurement gate"触发条件，这会从"没有数据"变成
"gate 本身不可执行"，从而越过 ARCHITECTURE_GAP 门槛。

**Current / Target / Evidence / Unknown**
- CURRENT：`_graph_signal` 是多源计数器之和，`_candidate_group` 依赖它；H1 与 H7/H9 共享状态。
- TARGET：协议 §6 要求"只关闭 H，其余不变"。
- EVIDENCE：无。没有任何实验证明 H 之间相互独立。
- UNKNOWN（**这是本轮最需要被验证的未知**）：关掉 H7/H9 后 `_graph_signal` 的分布变化多大；
  是否所有 9 条都有真实独立开关；`fusion_score`（算而不用）是否说明这层 fusion 的
  "融合分"契约本身就处在两套语义之间。

**最简单方案是什么？**
在跑 leave-one-out 之前，先做一次**可消融性检查**（比 ablation 便宜得多）：
对 pipeline 逐条关闭 H，记录 `_graph_signal` / `candidate_group` 的分布变化；
若发现强耦合，改成"关掉整组"或引入一个显式的 `heuristic_mask` 让每条 H 的贡献
在排序键上可单独观测。若耦合确实不可拆，则应**整组一起测**（全有 / 全无），
而不是假装能逐条归因。

**当前设计在哪里失败？**
"逐条启发式"这个保留单位可能是设计上的错觉。如果机制是共享信号上的层层叠加，
那么"9 条"这个计数本身就不代表 9 个可分别删除的复杂度。

**是否真的需要 Architecture Revision？**
只在可消融性检查确认强耦合时。若耦合弱，这只是一条 EVIDENCE_GAP，并入 F-05。

**有没有更简单替代？**
有：不做逐条 ablation，直接做**整层 ablation**（GraphRAG on/off）。这可以直接回答
B12 的 Delete 判据（是否值得保留这一层），只是回答不了"哪条该删"。对当前阶段
（连"这一层值不值得留"都未证）来说，整层 ablation 的信息量/成本比更高。

**增加什么成本？**
可消融性检查成本 ≈ 一次静态阅读 + 若干分布记录，不需要数据集与凭证，
**因此它可以在 `BLOCKED_PENDING_DATA` 期间先做**。这是本轮最具性价比的动作。

**退出条件是什么？**
可消融性被证实（或证伪）：要么给出每条 H 独立可关的证据，要么把保留单位改成"整组"。

**下一轮复测？**
① 读 `_graph_signal` 与三个 guardrail 的输入面，画一张 H→signal→group 的依赖图；
② 写一个 stackless 单测：固定 corpus，逐条关闭 H7/H8/H9，断言 `_graph_signal` 与
`_candidate_group` 的分布是否变化；
③ 结论写回协议 §3，把"可关闭"升级为"可独立关闭（已验证）"或改成整组判决。

---

## §7 F-07 — "GraphRAG 只面向英文 / 中文法律语料无测试用例"过强

**Red signal**：Q24（中文法律实体别名归一化最容易出什么错）、Q67（换真实卷宗还能用吗）、
Q87（不做别名归一化哪类多跳会失败）。A24 说"没有中文法律实体词典"、
"没有在中文法律语料上测过它"；A67 说"中文法律语料：无测试用例、无 holdout"；
A23 说实体别名归一化是规则、`GENERIC_ENTITIES` 是英文词。

**canonical source（已实测）**：
- A23 / A24 关于 `entity_alias.py` 的部分**成立**：`GENERIC_ENTITIES`（`:10-22`）只有
  `Introduction / Overview / Objectives / History / Roadmap / Examples / High / Low / Medium`
  等英文词；`normalize_entity_name`（`:25-32`）会剥离括号后缀（`PARENTHETICAL_PATTERN = re.compile(r"\s*\([^)]*\)")`，`:6/:27`）；
  没有中文法律主体词典。
- 但"中文法律语料无测试用例"**不成立**：
  `platform/services/graphrag/extractors/structured_extractor.py` 是一整套**中文合同**
  结构抽取器（`FILE_NAME_TITLE_HINTS` 主服务合同 / 借款合同、`CLAUSE_HEADING_PATTERN` 第…条、
  `PARTY_PATTERN` 甲方/乙方/丙方、`REGULATION_PATTERN` 《…》、`RISK_CUE_MAP` 等）；
  `tests/graphrag/test_contract_review_project_payload.py:64-108` 用一份完整中文合同
  断言实体对（`("星河科技有限公司","Party")`、`〈《中华人民共和国个人信息保护法》",…〉`、
  `("数据泄露风险","Risk")`），另有 `tests/graphrag/test_structured_graph_extractor_contract.py`。

**判定**：`ANSWER_QUALITY`（口径过强）+ `EVIDENCE_GAP`（真实缺口存在，但位置不同）。
真实可辩护的说法是：**"GraphRAG 的融合 / 别名 / 路径三个启发式只面向英文形态，
且没有中文法律主体上的 alias 覆盖；但平台另有一条中文合同结构抽取链，它有自己的中文测试。"**
A67 把整条 GraphRAG 说成英文调优，抹掉了这条中文路径——这对候选人**不利**
（它让回答看起来比实际更弱）。

**Current / Target / Evidence / Unknown**
- CURRENT：英文导向的 fusion/alias/path + 中文合同结构抽取器（两条并存）。
- TARGET：B12 measurement-gated；中文法律主体上的实体消解语义未在 canonical 定义。
- EVIDENCE：中文合同图测试存在（组件级）；中文法律主体上的 alias / 多跳**无**测试。
- UNKNOWN：中文合同抽取链与英文导向 fusion 是否为同一条检索路径；中文卷宗上的端到端表现。

**最简单方案 / 复测**：
① 确认中文合同抽取链是否汇入同一个 `merge()`——若是，则"英文调优"的结论必须限定到
融合层而非整层；
② 在下一轮回答里把 A67 改成上述限定版；
③ 若要证伪误合并风险，最小实验是用 `test_contract_review_project_payload.py` 的两家
同集团主体（括号区分）验证 `normalize_entity_name` 是否合并。

**是否 ARCHITECTURE_GAP？** 不是。它是回答口径 + 覆盖缺口。

---

## §8 F-08 — Recall eligibility 的 08 门在 Current 没有落点（IMPLEMENTATION_GAP，安全相关）

**Red signal**：Q30（写入 owner）、Q31（recall authority 谁拥有）、Q32（撤回）、
Q96（TOCTOU）、Q100（三者冲突听谁）。

**canonical source**：
- `docs/architecture/reference.md` B2 / B10 / B18：08 拥有 Recall Eligibility /
  lifecycle policy；"context / long-term memory recall -> current 08 recall/lifecycle/security
  eligibility before consumption"；B6 "当前 Memory / Context 是否可消费 = current matching
  recall/lifecycle/security eligibility + snapshot provenance …… **非证明 = similarity hit、
  same scope equality、old Context blob、source id alone**"。
- `docs/modules/reference.md`：「MemoryScope equality != Authorization」；
  08 拥有 "Recall Eligibility"。
- 实现（已实测）：`src/` 内 `recall_eligibility` / `RecallEligibility` / `recall_decision`
  **零命中**；真实门是 `memory/engine.py:1054-1064 _memory_exclusion_reason`
  （`review_status != APPROVED` → 排除；`memory_state in {"stale","conflict","revoked"}` → 排除；
  sensitive tags 命中 → 排除），在 `:835/:870/:949` 施用于召回。
- A29 / A31 / A70 / A100 自己承认这个差距："Target 上这个 authority 属于 08，
  Current 上它落在 Memory engine 的过滤逻辑里，独立的 08 recall decision 尚未接上。"

**判定**：**IMPLEMENTATION_GAP**（安全相关），不是 ARCHITECTURE_GAP。
Owner 明确（08）、Contract 明确（消费 current decision）、差距被候选人主动标注。
——但它值得单独列，因为它是本轮唯一一条**安全语义**上的 Current/Target 落差，
且 §0 规则 C 的第二半在这里擦边：被声明的不变量「scope equality != authorization」
在 Current 里没有独立落点，今天真正生效的**就是** scope 相等 + 一个存储的状态位。
这意味着今天"scope 相等"**事实上就是**授权，与声明相反。

**Current / Target / Evidence / Unknown**
- CURRENT：scope 四列 WHERE（`memory/store.py:520-526`）+ stored `review_status` /
  `memory_state` / sensitive tags 过滤。
- TARGET：08 产出 recall / lifecycle decision，01/04 消费。
- EVIDENCE：`tests/memory/test_context_pack_engine.py:131` 锁定四种排除；
  **没有**任何证据涉及独立 08 decision。
- UNKNOWN：08 侧将来以什么对象承载 recall decision；`security_epoch_ref`（A31 提到）
  与 recall 的关系。

**最简单方案**：不新建对象——把 `_memory_exclusion_reason` 的判定输入从"存储状态位"
改为"当前 08 资格查询"，并把 scope 相等从"授权条件"降级为"范围条件"。

**复测**：① `grep -rn "recall_eligibility\|RecallEligibility" src/` 是否出现；
② `docs/modules/security/README.md` 的 Recall Eligibility 段是否从 Target 移出；
③ 确认 `_memory_exclusion_reason` 是否新增了 08 输入。

---

## §9 F-09 — `ContextOrchestrator`：一个没有 consumer 的"统一入口"

**Red signal**：Q55（ContextOrchestrator 是真组件还是归纳的名字）、Q71（多出来的抽象带来了什么、
删掉损失什么）。A28、A55、A71。

**canonical source（已实测）**：
- 组件真实存在：`platform/services/application/context/orchestrator.py:115`（`__all__` `:190`）。
- **无生产调用点**：`src/` 内除自身与 re-export shim
  （`platform/services/application/context/__init__.py:14`、`agent/context.py:24`、
  `agent/__init__.py:41`）外没有任何实例化或 `.prepare(...)` 调用。
- 真实装配路径：`agent/runtime/nodes/core.py:62` `build_context` 节点
  → `:79` `deps.memory_engine.build_context_pack(...)`（`hasattr` 守卫在 `:64`）
  → `memory/engine.py:645` → `render_context_pack` `:753` → store `:334`。
  生产接线：`agent/runtime/factory.py:87` `MemoryEngine(store=DatabaseMemoryStore())`，
  经 `main.py:92` 注入。
- **canonical docs 从未命名 `ContextOrchestrator`**：`docs/architecture/`、
  `docs/modules/`、`docs/decisions/` 里都没有它。架构对 context 装配的 Owner 表述是
  `docs/architecture/reference.md` B2 尾段与 B18："01 / 04 为当前请求或 Step 组装可消费 snapshot"。
- 简历第 4 条仍写着："统一 typed contracts 与 scope 约束（ContextOrchestrator），
  接入 Agent 调用前读取与回合后写入，**使上下文组装按作用域在统一入口完成**"。

**判定**：`DOCS_GAP` + `ANSWER_QUALITY` + 一次 cleanup，**不是 ARCHITECTURE_GAP**。
理由：架构已经把装配责任分给了 01/04 与 provider，不存在两个 Owner 争同一事实；
`ContextOrchestrator` 只是一个被后来 live path 取代、未清理的早期抽象。
按 §0 规则 B，"一个孤儿组件 + 一句过强的简历措辞"不该升级。

**CURRENT / TARGET / UNKNOWN**
- CURRENT：typed contract 模块存在且有测试；无 runtime consumer；live 入口是
  `build_context_pack`。
- TARGET：01/04 组装 snapshot；provider 提供 record（B2/B3/B18）。
- UNKNOWN：这层 typed contract（`ContextSource` / `ContextItem` / `ContextPackPolicy`）
  是否与 `build_context_pack` 的输出契约等价——**这一条决定该删还是该接线**。

**最简单方案**：先测"`build_context_pack` 的返回是否已覆盖 `ContextOrchestrator` 的契约"
（A71 自己也提了这个测法）。覆盖 → 删除孤儿组件，把契约挂到真实入口；
不覆盖 → 把契约接到 `build_context` 节点，而不是保留一个平行入口。

**下一轮复测**：① `grep -rn "ContextOrchestrator" src/` 结果是否仍只有 shim；
② 对比 `platform/services/application/context/contracts.py` 与 `memory/engine.py:645-753`
的输出形状；③ 检查简历第 4 条措辞是否已与 live path 对齐。

---

## §10 F-10 — MemoryScope 的四维身份在 Current 实际是三维

**Red signal**：Q29（scope 语义多出来什么）、Q70（只用 user_id + project_id 会失败在哪）。

**canonical source**：`platform/services/memory/layers.py:43-55` `MemoryScope` 四个字段
（`user_id` / `agent_id` / `project_id` / `thread_id`）；DB 侧 `memory/store.py:520-526`
四列 AND。已实测：`agent/runtime/nodes/core.py:485-491 _memory_scope()` 里
`:488` 是 `agent_id="agent_run"` 硬编码字面量，而 `_memory_scope` 在 `:77`（读）与
`:394`（写）都被调用。

**判定**：`SEMANTICS_GAP`（小）。A29 / A70 都主动承认了这一点（"agent 这一维其实没被真正
用起来"），所以口径是诚实的；但它意味着"scope 是四维身份、读写/合并/回溯统一使用"
这个论证在 Current 只能算三维成立。不上调到 ARCHITECTURE_GAP：第 4 维语义不是被设计否掉，
只是当前没有被赋值。

**下一轮复测**：`grep -rn "agent_id=" src/backend/zuno/agent/runtime/nodes/core.py`；
确认是否出现了按真实 agent 身份赋值的路径。

---

## §11 F-11 — 冲突 memory 无语义仲裁：这是设计，不是缺陷

**Red signal**：Q34（同 Domain 两条冲突 memory 谁赢、会不会退化成并发写覆盖）、
Q94（并发写隔离级别）、Q95（行锁等模型）。

**canonical source / 实测**：
- 并发侧**不退化**：`platform/database/memory/domain.py:301 activate_memory_version`，
  `:315 SELECT ... FOR UPDATE`，`:320-321` 状态约束，`:353 AND generation = :expected_generation`，
  `:363-364 rowcount != 1 → MemoryGovernanceConflict("memory activation CAS failed")`。
  `MemoryUnitOfWork`（`:83-99`）无显式隔离级别（DB 默认）——A34/A94 自述一致。
- **语义侧不需要仲裁**：`docs/modules/reference.md`「Memory record != Domain truth」、
  「绝对不能再混淆的边界」；B2 尾段："02 的 Canonical Domain State 在冲突时优先"。

**判定**：**NOT A GAP**。两条冲突的 structured memory 同时存在、系统不判谁对，
与"memory 是非权威 record"这一已接受设计**一致**：谁赢由 02 的正式事实决定，
不由 memory 层仲裁。A34 的自我判断（"要在上层 review 人判或后续 consolidation"）
是对的方向。

**下一轮复测**：确认 `docs/modules/reference.md` 的「Memory record != Domain truth」
仍在；确认是否有新的 consolidation 语义被引入（那才需要重新评估）。
**不上调**是本节的重点：这是一条**看起来像架构缺口、实际是设计边界**的信号。

---

## §12 F-12 — staleness 没有刷新 owner（OWNER_QUESTION，小）

**Red signal**：Q33（过期但状态未刷新）。A33 明确："今天**挡不住**——没有后台 reaper 去主动
刷新状态，staleness 完全靠已记录的状态判断"。

**canonical source**：`memory/engine.py:1054-1064` 的排除**依赖已写入的 `memory_state`**；
`tests/memory/test_context_pack_engine.py:131` 锁定四种排除。
`docs/architecture/reference.md` B7 要求"old Context / Memory snapshot after policy or Domain
change → rebuild from current Owner facts + current 08 recall/lifecycle eligibility"。

**判定**：`OWNER_QUESTION`（小）——"谁负责让状态变 fresh"在 canonical 里没有明确 owner
（B10/B7 只说消费者要 revalidate）。它**擦边** Owner 触发条件，但**不升级**为
ARCHITECTURE_GAP 的理由是：B9 已经写明 recall/lifecycle eligibility 的 freshness owner
是 08 且消费者必须 revalidate；缺的是那条链的落地，与 F-08 是同一根因。
把它并到 F-08 处理，不单独立 gap。

**下一轮复测**：与 F-08 同一组复测；另加 `grep -rn "reaper\|staleness\|freshness" src/backend/zuno/memory/`。

---

## §13 F-13 / F-14 / F-15 — 三条**明确不上调**的信号

### F-13 Runtime 恢复权威 / late result / Build-Buy
Q37–Q43（fixed workflow 何时不够 / PlanVersion 冻结什么 / late result / stale checkpoint /
recovery authority / 为什么不用纯 LangGraph / 删除判据）。
canonical：`docs/modules/runtime/README.md:101-105`（Target / Current / Gap 三段）、
`docs/architecture/reference.md` B5 / B7 / B8 / B9 / B12、`docs/decisions/0005`、
`0008`、`0012`。
判定：**NOT A GAP**。Owner（04 拥有控制事实，恢复先找 Owner fact）、Contract
（checkpoint ≠ Domain commit；late result 必须重新验收）、Build/Buy 因果（用官方
`PostgresSaver` 做 primitive，自研的是它不拥有的业务恢复语义）、删除判据（B12 / ADR 0012）
**四件都齐**。A37–A43 与 canonical 逐条对得上，A42 的 `graph.py:17-19` 注释引述与
`docs/decisions/0005` 一致。Current 的缺口（不可变 PlanVersion、Replan Barrier、
AdmissionReceipt recovery）已在 runtime README 的 Gap 段登记 → `IMPLEMENTATION_GAP`。

### F-14 Pilot / 法院 / 中文卷宗泛化
Q59–Q67。canonical：`docs/governance/project-fact-provenance.md` PF-015/016/018/019/020/022；
`docs/evidence/README.md`「COURT QA: UNKNOWN / NOT AVAILABLE」。
判定：**NOT A GAP**，且**无可用证据**。A59–A66 的处理是本届最干净的一段：
全部保留 Unknown，明确拒绝把"项目经历过 Pilot"扩写成"我做过 / 法院在用 / 已验收"，
并且主动把 `#201` / `#205` 的当前 fault probe 与"法院现场那次错在哪"切开（A63）。
唯一与架构相关的是 Q67（换真实卷宗还能用吗）——已并入 F-07。

### F-15 KnowledgeGeneration / ReadinessDecision 是 Target 概念
Q77–Q82。canonical：`docs/modules/knowledge/README.md:95/99`（Target 与 Gap 两段明确列了
generation activation、跨 Store purge、权限撤销后的召回收敛、**negative evidence 条件**、
GraphRAG 按 query class 的 holdout / ablation）；`platform/services/rag/vector_db/chroma_client.py`
的 `metadata={"hnsw:space": "cosine"}`（A99 的 ANN 判断与之一致）。
判定：**NOT A GAP**。A78（`src/` 内 literal `KnowledgeGeneration` 无命中）与 A80/A82
（`KnowledgeReadinessEvidence` 只是取证包装，不是运行时 readiness）都正确地
把 Target 与 Current 分开，且没有把"没搜到"泛化成"不存在"。
架构对"全案没有"有明确答案：Top-K 证不了否定，负证据需要一个覆盖前提——这正是
knowledge README 的 Gap 项。这是**已登记的 EVIDENCE/DESIGN gap**，不是设计矛盾。

---

## §14 本批 Blue 回答自身暴露的薄弱点

本节只谈回答质量，不重复 §1–§13。

1. **文件路径有两处错误，恰好都落在同一段核心论证上（T04 / 准入）。**
   - A8 / A56 写 `single_controller_runtime.py:497-501 抛 DYNAMIC_PLAN_RUNTIME_NOT_BOUND`。
     实测：该文件不在 `agent/runtime/execution/` 下，而在
     `platform/services/workspace/single_controller_runtime.py`；`:497-499`
     （`build_workspace_plan_steps`）只是 `return None`，**不抛**；真正的 fail-closed 是
     `:737-738` 计算 `complex_unbound` + `:814-818` 置 `admission_reason` + `_blocked_request`。
     答案的**结论**没错，**位置与动作**（"抛"）都错。
   - A8 写 `agent/runtime/execution/react_runner.py:20-67`。该文件**存在**
     （已实测 `src/backend/zuno/agent/runtime/execution/react_runner.py`），
     所以这一条是可信的；但**同一次回答里的另一个路径错了**，说明引用是凭印象写的，
     不是逐条校对过的。下轮若被 Red 拿 `sed -n '497,505p'` 对质，会很难看。
   - **建议**：凡带行号的引用，一律在回答前实跑一次 `sed -n`。

2. **A22 / A73 / A74 的"预测"含量被低估。** 三题都标了"预测"，但 A74 给出的
   "留 seed expansion、删别名归一化与 path ranking"读起来比 A22/A73 更**确定**。
   而 A68 / A86 同时承认"举不出受益 query"、"没有任何测量支撑"。把这两处并列读，
   会出现"在零测量下给出确定的保留排序"的观感。**建议**：A74 的下轮口径改为
   "如果必须今天选，我会先留 X；但这个选择的期望信息量低于先做整层 ablation"。

3. **A31 / A70 与 A33 对同一个门的描述不一致。** A31/A70 把 Current 的门描述为
   "同 scope + `review_status == APPROVED`"；A33 则正确列出四类排除
   （stale / conflict / revoked / sensitive）。实测 `_memory_exclusion_reason`
   （`engine.py:1054-1064`）支持 A33 的版本，A31/A70 漏了 `memory_state` 与 sensitive tags
   两个条件。**低估自己的防护**，与 F-07 是同一类毛病。

4. **A5 / A89、A11 / A92、A12 / A93、A20 / A85 是近乎逐字重复的两组。**
   Q5 与 Q89、Q11 与 Q92、Q12 与 Q93 同题异构；答案内容几乎一致。
   这不是造假，但在连续 30–60 分钟的口语面试里会读作"背诵稿"。
   **建议**：第二组改从**不同层**切入（例如 Q89 谈 `call_args` 的局部性 vs
   Q5 谈"为什么不是全局 dict 加锁"的语义差别）。

5. **A6 / A90 对 ContextVar 的处理是全轮最佳范式，值得复用。** 先答 Fundamentals
   （正确做法是 ContextVar），再明确"但今天这条路径没有用 ContextVar，用的是显式传参"，
   并给出选显式的理由。**没有**把框架/常识能力反写成自己的实现。这个结构应该成为
   所有"Project → Fundamental Bridge"题的模板。

6. **A15 的 bad case 细节无法自证。** A15 给出被注入的文档名
   （`Sinister (film)`、`Adam Collis`、`Charles Craft`），但同一答案又说三路精确 rank
   "没有单独存档"。可信来源 `PF-031` 只记了两条被挤出的 gold（`Ed Wood`、`Shirley Temple`）。
   **被注入方的文档名**在 A15 里没有对应证据指认。**建议**：下轮要么给出该名的取证
   来源，要么按 A15 自己"无直接证据保留 Unknown"的口径把它一起去掉。
   （本轮未去 git 里逐个核对 `7928df50` 的正文，因此这条只提为"需自证"，不下结论。）

7. **`Pilot` 与 `Production` 的口径是干净的。** A59–A66 全部保留 Unknown，
   且 A62 把"为什么简历只写到 Pilot"归因为**取证边界**而非人为动机——这与
   `PF-020` 的写法一致。这一段不需要修改。

---

## §15 下一轮必须复测什么（可执行清单）

按优先级排序。前三条**不依赖外部数据集**，在 `BLOCKED_PENDING_DATA` 期间即可执行。

```text
R1 [最高优先，不需数据] 逐条启发式的可消融性（F-06）
   动作：固定 corpus 的 stackless 单测，逐条关闭 H7/H8/H9，记录
        fusion.py:156-163 _graph_signal 与 :166-187 _candidate_group 的分布变化。
   判据：若分布显著变化 → 把协议 §3 的"可关闭"降级为"整组可关闭"，并考虑
        引入显式 heuristic_mask；否则 F-06 关闭，并入 F-05。
   为什么先做：它决定 F-05 的 ablation 到底能不能被真正执行。

R2 [不需数据] 准入边界的实机行为（F-01）
   动作：对 _plan_kind_for 的 8 个 token（含中文「报告」）各造一条 workspace 请求，
        记录是否落 single_controller_runtime.py:814-818 的 admission block。
   判据：任何一条普通请求被 DYNAMIC_PLAN_RUNTIME_NOT_BOUND 拦下 → F-01 升级，
        并触发一次最小 Architecture Revision（准入 owner + complex 对外语义）。

R3 [不需数据] 幂等键的 salt 契约（F-04）
   动作：读 capability/mcp/servers/lark_mcp/mcp_tool/calendar_event/create_calendar_event.py:57
        上下文，判定 .idempotency_key(uuid4().hex) 是 provider 幂等键还是普通 request id；
        并确认 tests/ 内是否存在"同一步骤重试 → 同一 key"的用例。
   判据：若为 provider 幂等键 → 记为 effect 幂等契约缺陷；否则 F-04 只保留 salt 命名/契约收口。

R4 [不需数据] ContextOrchestrator 契约等价性（F-09）
   动作：对比 platform/services/application/context/contracts.py 与
        memory/engine.py:645-753 的输出契约。
   判据：等价 → 删除孤儿组件；不等价 → 把契约接到 build_context 节点。

R5 [需数据] 逐条 leave-one-out（F-05 / F-06）
   动作：按 rb019-graphrag-ablation-protocol.md §6 执行；若 R1 判定强耦合，
        改为整层 on/off 两臂。
   判据：协议 §2；"一条都不留"是合法终点。

R6 [需数据] 中文法律语义的独立一臂（F-07）
   动作：用 tests/graphrag/test_contract_review_project_payload.py 的中文合同语料，
        验证 normalize_entity_name 是否把同集团括号区分的主体合并；
        并确认中文合同抽取链是否汇入同一个 merge()。
   判据：出现误合并 → 别名归一化的中文风险从"推理判断"升级为"已观测缺陷"。

R7 [Gap 状态巡检] F-02 / F-03 / F-08 / F-13 / F-15
   动作：逐条读 docs/evidence/README.md、docs/governance/effect-remote-query-reconciliation-status.md、
        docs/modules/{runtime,knowledge,security}/README.md 的 Gap 段。
   判据：任一状态从 Gap 转 Current 或反之，都要在本轮的复诊里改判。
```

**给 Controller 的三点提示**（详见下表）：

| # | 提示 | 依据 |
| --- | --- | --- |
| 1 | 准入边界（F-01）是本轮唯一确认的 ARCHITECTURE_GAP，且它是**可执行验证**的：`报告` 这个中文词会把普通请求翻成 complex 并触发 admission block | §1；`simple_agent.py:2149-2157`、`single_controller_runtime.py:737-738/814-818`、`main.py:113` |
| 2 | GraphRAG 的问题**不是**架构，是 gate 未执行（F-05）；真正可能升到架构层的是**可消融性**（F-06），而它不需要数据集就能先测 | §5 / §6；`fusion.py:156-163/166-187`、协议 §3 |
| 3 | A8/A56 里的 `single_controller_runtime.py` 路径与"抛"这个动作都不准确（真实位置在 `platform/services/workspace/`，且是 admission block 不是 raise）——这是 Red 最容易一击命中的引用错误 | §14.1 |

---

```text
诊断完毕。
ARCHITECTURE_GAP: 1 条确认（F-01）+ 1 条条件性（F-06，取决于 R1）。
本文件对 Red 封存；仅 Blue Architecture Reflection 可读。
```
