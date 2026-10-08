# Blue Final Architecture Reflection — rb-2026-10-08-formal-021

```text
base_sha: cdd2063b341e6919fafaa1395d1f3bdc837329f6
inputs:
  # 本轮产物
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/00_artifact_links.md
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/01_simulated_resume.md
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/02_red_questions.md
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/03_blue_architecture_notes.md      (Wave 1 初诊，复诊对象)
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/04_red_wave2_review_and_questions.md
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/04_blue_wave2_architecture_notes.md (Wave 2 复诊)
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/04_red_evaluation.md                 (Red Final 盲评)
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/03_blue_answers.md                   (抽样：A8/A15/A17/A56/A97/A98)
  - docs/red-blue/rounds/rb-2026-10-08-formal-021/04_blue_wave2_answers.md             (抽样：A101/A117/A118/A199 等)
  - .agent/red-blue/defense-model.md
  - .agent/red-blue/protocol.md
  # canonical — src（本轮亲自打开 / grep / sed 取行）
  - src/backend/zuno/main.py
  - src/backend/zuno/platform/services/workspace/simple_agent.py
  - src/backend/zuno/platform/services/workspace/single_controller_runtime.py
  - src/backend/zuno/platform/services/retrieval/fusion.py
  - src/backend/zuno/platform/services/graphrag/entity_alias.py
  - src/backend/zuno/platform/services/graphrag/retriever.py
  - src/backend/zuno/knowledge/agentic_graphrag.py
  - src/backend/zuno/knowledge/runtime_batch.py
  - src/backend/zuno/knowledge/ingestion/delete_restore.py
  - src/backend/zuno/capability/tool_runtime/invocation_gateway.py
  - src/backend/zuno/capability/mcp/mcp_tool_executor_adapter.py
  - src/backend/zuno/capability/mcp/servers/lark_mcp/mcp_tool/calendar_event/create_calendar_event.py
  - src/backend/zuno/api/services/mcp_user_config.py
  - src/backend/zuno/api/services/product/runtime_engine.py
  - src/backend/zuno/agent/harness.py
  - src/backend/zuno/agent/runtime/nodes/core.py
  - src/backend/zuno/agent/runtime/phase08.py
  # canonical — tests / docs
  - tests/capability/test_tool_effect_postgres_boundary.py
  - docs/architecture/reference.md
  - docs/modules/reference.md
  - docs/decisions/0014-round-02-cross-boundary-authority-and-recovery.md
  - src/backend/zuno/knowledge/README.md
  - src/backend/zuno/agent/core/README.md
authority: Blue Team — Architecture Owner（本轮架构侧收口，判决性质）
judgement_target: 系统本身（Owner / Authority / State / Contract / Recovery / Security / Build-Buy 的因果是否成立），不评候选人措辞质量
```

```text
审计声明（诚实边界）：
1. 本轮我未读取 docs/red-blue/rounds/**（归档轮次；已记录的泄漏向量 IMP-020-14）。本文件的所有 grep
   限定在 src/、tests/、docs/decisions/、docs/architecture/、docs/modules/，输出**没有**带回归档轮次片段，
   也**没有**带回本轮 workspace 其他被封存文件的片段。00_artifact_links.md 属本轮 Controller notes、
   对 Blue 可读，我已读。
2. 凡本文件写 file:line 的地方，都是本轮实际 grep / sed 取过该行原文的；凡写「未核」的，是我**没有**
   打开过、只作引用复述的。§9.3 只写我真的回源码核过的。
3. 本文件是 Reflection，不是 Apply。improvement_review_gate: REQUIRED 未过，因此我不修改任何
   Authority / Security Authority / Recovery 语义，只提出「建议」。
```

---

## 0. 开工前必须先说清的三件事

### 0.1 本轮 workflow 缺陷是否复现：**未复现**

round 020 的缺陷是：Red Final 与 Blue Reflection **并行**完成，Reflection 先按不完整的 Part A 判，产物到位后被迫重写。

本轮事实（`git log`，本轮分支）：`144ba412 rb-021: red final evaluation` 先于 `297257da rb-021: checkpoint red evaluation — advance to blue reflection`，即 Red Final 在 Blue Reflection 开工**之前**已落盘并提交。`05_blue_architecture_reflection.md` 在 Round Init 预创建时 `status: NOT_STARTED`，正文声明「在 Red Final 落盘之后才开始（不得并行）」——该约束本轮被遵守。**判定：020 的缺陷未复现，本节的时序是干净的。**

**但必须同时说清 Red Final 的性质**（它自己的诚实声明，`04_red_evaluation.md` 文件头与 §6）：Red Final 是**盲的**——它未读任何源码、canonical docs、Evidence、封存笔记；它对 `文件:行`、commit SHA、run id、测试名、常数的一切判断都是**结构判断**（自洽性 / 跨答一致 / 两波漂移），**不是核实**。它明确区分 `NOT_ESTABLISHED`（我不信他能证明）与 `FALSIFIED`（已证伪），并声明自己只能说前者。

⇒ 这条属性对本轮 Reflection 有一个直接后果：**我作为能读源码的一方，回源码核 Red Final 的「结构判断」是真增量**，而不是冗余劳动。§9.3 就是这件事的产物。

### 0.2 本轮已知的泄漏向量

- **重复出现的向量（Arch 实例自报）**：Wave 1 与 Wave 2 的封存笔记作者都自报对 `docs/` 做过跨目录 grep，输出顺带带回 `docs/red-blue/rounds/**` 与本轮 workspace 其他文件的片段。这是 `IMP-020-14` 记录的向量在本轮的**再次复现**，记为观测事实。
- **我本人**：见文件头审计声明第 1 条——**没有**发生同类越界。我对此负责，并主张本文件的 finding 不依赖任何历史轮次结论。

### 0.3 本轮的判据（先说结论）

- **`ARCHITECTURE_GAP` 最终只剩 1 条：F-01**（Owner + Contract）。F-06 的降级**成立**（§2 已独立复核理由）。
- 其余全部落在 `IMPLEMENTATION_GAP` / `EVIDENCE_GAP` / `DOC_GAP` / `NARRATIVE_GAP` / `GOVERNANCE`。
- 我复核了 Red Final 中**唯一一类它能做、我也能做的判断**（两波口径的自洽性 + 它与源码的对照），核出 **2 处过强表述**（§9.3），并闭合了 Red Final 主动保留的 2 个未知（均指向 Blue 正确）。

---

## 1. 当前架构真实存在的问题

每条给：问题 / 最简单方案 / 当前方案在哪里失败 / 是否真需要 Architecture Revision / 成本 / 退出条件 / 下一轮如何复测。

### P1 — Workspace 准入边界：一条改变执行语义的准入门既无 Authority、也无 Contract（= F-01）**【ARCHITECTURE_GAP】**

**问题。** 普通 workspace 请求会被一张字符串表判成 `complex`，而 `complex` 在 shipped composition 下被准入拦下，产出的不是错误、而是**一条「有 entrant、无 Plan」的 run**。

**我本轮独立复现的全链（逐行核过）：**
- `platform/services/workspace/simple_agent.py:2150-2156`：`_plan_kind_for` 对 `original_query.lower()` 做**子串**匹配，命中 `("compare","across","conflict","multi-hop","multihop","analyze","synthesize","报告")` 任一即 `return "complex"`。**中文「报告」确在表里**。无模型参与。
- 调用点 `simple_agent.py:2032`（`_run_request`）与 `:2080`（`retry_run`）：`plan_kind = "tool" if resolved_tool_id else self._plan_kind_for(original_query)`。
- 装配 `src/backend/zuno/main.py:113`：产品组合 `dynamic_dag_planner=None`。
- 拦截 `single_controller_runtime.py:737-739`：`complex_unbound = bool(plan_kind == "complex" and self._dynamic_dag_planner is None)`。
- `:814-818`：`elif complex_unbound:` → `admission_reason = DYNAMIC_PLAN_RUNTIME_NOT_BOUND`（常量 `:103`），注释明写「an unbound composition must never fake a fixed three-step DAG or fall back to a direct answer」。
- `:825`：`return self._blocked_request(...)`。
- `_blocked_request`（`single_controller_runtime.py:870-911`）**不抛异常、也不拒收**，而是返回一个**正常的 `RuntimeStartRequest`**：`plan_steps=()`、`capability_ids=()`、`allowed_tools=()`、`approval_required_tools=()`、`strategy_mode=None`、`security_summary={"decision":"block","recommended_action":"refuse",...}`、`budget_verdict={"allowed": False, ...}`。
- 对照 canonical 不变量：`docs/modules/reference.md:237`「Native Runtime entrant 一定有 Plan：简单单步，复杂 Dynamic DAG。」
- 复核 A8/A56 的引用动作：`build_workspace_plan_steps`（`:465`）在 `:497-501` 对 complex+planner=None 是 **`return None`**，全文件**不存在** `raise DYNAMIC_PLAN_RUNTIME_NOT_BOUND`。⇒ A8/A56「抛」这个动作**错**（A101 已自认并收回）。

**三条被接受的来源互斥（这是系统问题，不是回答问题的措辞问题）：**
```text
简历第 1 条：复杂请求 → ReAct 路径
架构 B1 #3 / B4 Profile B：复杂请求 → Dynamic DAG（immutable PlanVersion）
今天代码：复杂请求 → 空 plan 的 RuntimeStartRequest（decision=block，不回落、不 ReAct）
```

**最简单方案。** 不新增对象、不新增状态机。给这条边界一个 **owner + 一份最小 decision record**（可以只是模块 reference 的一条 Guard 条目，不必是完整 ADR），并把「planner 未绑定时 complex 的对外语义 = **受控拒绝**」正式写成受控语义。判据（关键词表）的作者与解释权目前**双 Unknown**（A105/A159 自认；`docs/decisions/` 经本轮确认无对应 ADR，见 §9.1 F-01 依据）。

**当前方案在哪里失败。** 不在「规则准入不如模型准入」——规则准入是可辩护的简化。失败点在：**一条改变执行语义与授权路径的决定，既没有 Authority（没有 owner、没有 decision record），也没有 Contract 说明「被拦时这条 run 算什么」**。B1 #3 要求 entrant 必有 Plan；实现产出的恰是「有 entrant、无 Plan」。这是 Owner + Contract 的站不住，命中 §13 门槛。

**是否真需要 Architecture Revision？** **需要，且只需最小一次**：写 owner + 收口「complex 未绑定 = 受控拒绝」。**不需要**新增模块、状态机、Receipt 或 Provider。

**成本。** 最小方案 ≈ 一份 decision record + 一处措辞修正，接近零代码。替代方案（删掉 `_plan_kind_for` 的 complex 判据，全部走 `simple` 单步 + `tool` 直连）的代价是**放弃「复杂任务」这个产品叙事**，需产品侧同意——但它同时**消灭了「空 plan run」这个形态**，与 B12 的 Delete 判据一致，因此是更干净的减法。

**退出条件。** 当且仅当 (a) 产品组合绑定 Dynamic DAG planner 且 B4 Profile B 端到端可跑；或 (b) 接受一次 Revision，把 complex 的对外语义正式定义为受控拒绝并记录。二者未发生前，F-01 关闭不了。

**下一轮如何复测（全部不需外部数据）。**
① `grep -rn "dynamic_dag_planner" src/backend/zuno/main.py` 是否仍为 `None`；
② 补并运行一条**确定性断言**：`plan_kind=complex` 且 `planner=None` ⇒ `_blocked_request` 且 `plan_steps=()`（本轮已核：**当前 tests/ 里没有任何断言涉及 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND` / `_plan_kind_for` / complex block**）；
③ `docs/decisions/` 是否出现准入 owner 记录；
④ 「空 plan run」在 runtime 下游如何被呈现（是终态失败、空跑、还是被上层包装）是否被一句话定义。

---

### P2 — 「孤儿组件」是一个模式：代码在、驱动不在（= N-01）

**问题。** 多个组件「已实现 + 有测试 + **零非测试调用方**」并存，使若干被讲成 **Current** 的行为实际是「代码存在、无驱动」。本轮实测（`grep -rn` 全仓）：
- `ContextOrchestrator`：`src/` 内除自身与 re-export shim（`agent/context.py:10/24/37`、`agent/__init__.py:14/41/66`、`platform/services/application/context/__init__.py:14/20`）外**无实例化、无 `.prepare(...)` 调用**。
- `DeleteRestoreRuntime`（`knowledge/ingestion/delete_restore.py:327`）/ `PersistentDeleteRestoreCoordinator`（`:582`）：`src/` 内只有定义与 re-export，**无生产调用点**。
- `phase08.py` 的官方 `PostgresSaver` 路径（`:9`/`:40`，经 `phase08_postgres_checkpointer` `:37` 暴露）：只在 `agent/runtime/__init__.py` 被 re-export，**无产品调用方**。
- `escalate_due_reconciliations`（`invocation_gateway.py:1607`）/ `record_manual_effect_assessment`（`:1787`）：全仓调用方**只在** `tests/capability/test_tool_effect_postgres_boundary.py`。

**最简单方案。** 不删代码、不改架构——只做一张**接线状态表**（组件 | 定义位置 | 非测试调用方 Y/N | 被谁当 Current 讲过），并把凡引用这些组件当 Current 证据的回答，强度降为「代码存在、无驱动」。

**当前方案在哪里失败。** 它不失败——它与仓库自己的 Target/Current/Gap 三段式纪律**一致**（Target 设计先落代码、接线在后）。问题只在**叙述层**：讲的时候没区分「在跑」与「写好了」。

**是否真需要 Architecture Revision？** **不需要。** 分类 `DOC_GAP` + `NARRATIVE_GAP`。**成本**：一次 grep 表的成本。**退出条件**：接线状态表产出。**复测**：对每个可疑孤儿重跑「是否有非测试调用方」。

---

### P3 — Recall eligibility 的 08 门在 Current 没有落点（= F-08，安全相关）**【IMPLEMENTATION_GAP】**

**问题。** 架构要求「消费 current 08 recall/lifecycle/security eligibility」（`docs/architecture/reference.md` B2/B10/B18），但 `src/` 内 `recall_eligibility` / `RecallEligibility` / `recall_decision` 本轮实测 **0 命中**。今天生效的是一张**存储状态位 + scope 相等**的过滤。

**最简单方案。** 不新建对象：把过滤的判定输入从「存储状态位」改为「当前 08 资格查询」，并把 scope 相等从「授权条件」降级为「范围条件」。

**当前方案在哪里失败。** 声明的不变量「scope equality != authorization」在 **Current 里连落点都不存在**——今天「scope 相等」**事实上就是**授权，与声明相反（§0 规则 C 的第二半擦边）。

**是否真需要 Architecture Revision？** **不需要。** Owner（08）与 Contract（消费 current decision）都明确，差距被候选人主动标注。分类 **IMPLEMENTATION_GAP（安全）**。

**成本**：一次接线 + 一条负向测试。**退出条件**：`grep -rn "recall_eligibility" src/` 出现，或该字段在 security README 从 Target 移出。**复测**：① 该 grep；② `_memory_exclusion_reason` 是否新增 08 输入。

---

### P4 — GraphRAG 的 measurement gate 未执行，且仓内已有更简单的成熟替代未试（= F-05 + N-03）**【EVIDENCE_GAP，触发 Build-Buy 边缘】**

**问题。** 检索层的一组手定启发式随默认路径生效，其保留判据被一个当前**不可执行**的协议 gate 住（`rb019-graphrag-ablation-protocol.md`：`status: FROZEN_PROTOCOL` / `measurement_status: BLOCKED_PENDING_DATA`，owner 03+09）。同时本轮实测：**仓内已有 RRF**——`knowledge/agentic_graphrag.py:876` `entry["rrf_score"] += 1.0 / (60.0 + rank)`，strategy 名 `local_rrf_then_score_rerank`（`:1411`），sort key `:883`；而知识检索路径用的是 `retrieval/fusion.py` 的自制 group/tier/baseline 方案（`_rank_key` `:951-977`，`fusion_score` 写 metadata 但不进排序键）。

**最简单方案。** 两件都已写在协议里：① 整层 on/off 两臂（含「一条都不留」这个合法终点）；② 加一臂「改用仓内已有的 RRF」。

**当前方案在哪里失败。** 不是设计矛盾（协议就是为它写的），而是**已知未收敛的复杂度债**：复杂度已经在默认路径上生效，而它的 gate 当前不可执行。gate 本身**存在、冻结、有 owner**，因此按 §13 门槛**不升为架构**。

**是否真需要 Architecture Revision？** **不需要。** 需要的是执行协议 + 把 N-03 的替代方案摆进候选清单。

**成本。** 2026-10-08 当天：**零新数据即可推进 N-03 的静态部分**（确认知识检索路径在任何配置下都不经过 RRF），RRF 的 A/B 与整层 on/off 需数据。**退出条件**：协议 §2 逐条判决完成，或整层判退回 hybrid；N-03 的 A/B 完成。**复测**：`fusion.py:9` 的 `GRAPH_PROMOTION_THRESHOLD = 6` 是否仍是裸常数（本轮实测仍为 6，无 calibration 落盘）；是否出现任何 `full-minus-H` 落盘结果；知识检索路径是否任何配置下都不经 RRF。

---

### P5 — 远端 Effect 收敛仍是人工兜底、AUD-L2 未证明（= F-02 / F-03）**【IMPLEMENTATION_GAP】**

**问题。** 无后台 reconciler；自动 remote query 走 `DEFERRED_BY_PROVIDER_CAPABILITY`；`escalate_due_reconciliations` / `record_manual_effect_assessment` **仅在测试里被调用**（本轮实测）。`AUD-L1` 已 verified，`AUD-L2`（send 后 crash/restart 的 audit lifecycle）明确 `NOT IMPLEMENTATION-PROVEN`。

**最简单方案。** 沿用已登记治理文档（`docs/governance/effect-remote-query-reconciliation-status.md`）的收敛路径，不新增对象。

**当前方案在哪里失败。** Owner（06）与 Contract（unknown 不得映射成 Failed、不得盲重试）**都成立**——这是「没做到」，不是「设计不成立」（§0 规则 A）。分类 **IMPLEMENTATION_GAP**，不上调。

**是否真需要 Architecture Revision？** **不需要。** **成本**：接一个真驱动（后台或运维触发）。**退出条件**：对账链出现非测试调用方；AUD-L2 从 NOT-PROVEN 移出。**复测**：该治理文档状态是否从 DEFERRED 变化；`escalate_due_reconciliations` / `record_manual_effect_assessment` 是否出现非测试调用方。

---

### P6 — Target 概念词 ↔ 代码符号无对照表（= N-02）**【DOC_GAP】**

**问题。** 按 Target 词搜 `src/` 得到假阴性。本轮实测：`KnowledgeGeneration` / `ServingPointer` 在 `src/` **0 命中**，但在 canonical 文档（`docs/modules/knowledge/README.md`、`docs/architecture/reference.md`、若干 ADR）里大量出现；同一概念在代码里换了名（`KnowledgeVersionRecord` / `KnowledgeVersionState` / `document_version_id`）。

**最简单方案。** 补一张「Target 词 ↔ 代码符号 / 或『src 无实现』」对照表；引用纪律改为「凡带行号的引用必须实跑」。

**当前方案在哪里失败。** 它是**取证陷阱**，不是设计问题——按 Target 词搜得到「0 命中 ⇒ 未实现」的假阴性，按代码词搜才看到机制**部分存在**。分类 **DOC_GAP**，`proposed_change` 落在文档 owner，不是架构。

**成本**：一张表。**退出条件**：表产出并进入引用纪律。**复测**：Target 名词逐个人肉/脚本比对 `src`。

---

## 2. 简单方案够不够

**够，除 P1 外。** 逐条回答：

- **P1（F-01）**：简单方案**不够**，但不因为需要更多机制，而因为**缺的是两个「归属」而非任何代码**——一个 owner、一份 decision record。补上即闭合，仍不需要新对象。
- **P2（N-01）**：简单方案（一张接线状态表）**完全够**。这层问题只要叙述分级，不要动代码。
- **P3（F-08）**：简单方案**够**——把过滤输入换成 08 查询，不建新对象。
- **P4（F-05 / N-03）**：简单方案**够**——按冻结协议执行 + 加一臂 RRF。「一条都不留」是合法终点。
- **P5（F-02 / F-03）**：简单方案**够**——接真驱动，设计已给出 owner 与 contract。
- **P6（N-02）**：简单方案**够**。

**结论：本轮没有任何一条问题需要「增加能力」来解决。** 全部六条的正解要么是**归属/记录**（P1）、要么是**叙述分级**（P2/P6）、要么是**接线/测试**（P3/P5）、要么是**执行已冻结的协议**（P4）。这与 protocol.md §26「复杂度必须由问题和测量推导」一致——本轮**反向**验证了它：问题不在缺少机制，在缺少让机制可被裁决的归属与测量。

---

## 3. 在哪个 failure / constraint 下失效

| 问题 | 在哪个具体 failure / constraint 下失效 | 触发条件是否已可执行 |
| --- | --- | --- |
| P1 F-01 | **「复杂请求」这个产品语义存在时**。任何含 `报告` / `compare` / `analyze` / `multi-hop` 的普通 workspace 请求都会命中 `complex` → 准入 block → 空 plan run。约束是 shipped composition 未绑 planner 且**禁回落**。 | **是**。确定性、不需模型、不需数据。 |
| P3 F-08 | **并发撤回 / TOCTOU 出现时**。`_memory_exclusion_reason` 依赖已写入的状态位，无 reaper；review 刚通过、读回读旧状态的窗口没有被护栏挡住。 | 是（负向测试可写）。 |
| P4 F-05 / N-03 | **「无外部 benchmark 数据」约束下**，gate 不可执行；只要数据集不接，这层复杂度就无法被裁决保留或删除。N-03 另有**不依赖数据**的一半（确认路径是否可配置走 RRF）。 | 一半是（静态部分），一半否（A/B）。 |
| P5 F-02 / F-03 | **远端副作用已发生、本地结果未知**时。今天靠人工兜底；`escalate` 无驱动 ⇒ 时间阈值形同虚设。 | 是（接线可验）。 |
| P2 N-01 | **「把写好的组件讲成在跑的组件」时**。它不导致运行时 failure，只导致 **Claim 分级错误**。 | 是（grep 表）。 |
| P6 N-02 | **「按 Target 词搜 src」时**，得到假阴性。 | 是。 |

**共同根因（P1 与 P2/P6 的交汇点）：** Zuno 的自研价值最小内核集中在「暴露 + 准入 + 一小块绑定语义」（A174/A75），而「准入」恰好就是那条**无 owner、在 shipped composition 下 fail closed** 的边界。**自研叙事的正当性与 F-01 的收口是同一件事。**

---

## 4. 替代方案判断（Multi-Agent / Specialist / Subgraph / Generic Host / Native Runtime / 单体）

**先正面回答「Multi-Agent 是否真的值得」：不值得。** 至少不是本轮任何一条 finding 的解法。理由是**从 failure 推导**，不是从偏好推导：

1. **当前失败不是「单 Agent 做不动」，而是「准入没有 owner」。** 系统今天能跑的是 `tool` / `simple` 两条单步路径；唯一被拦下的是 `complex`，而它被拦的**原因是一条未绑定的依赖**，不是「一个 Agent 处理不了」。加 Multi-Agent **不解决**这个；它只会**复制**这个：每一个新增的 Agent 边界都会再引入一条「谁拥有准入」的问题。
2. **Authority 已经足够碎，且碎在有 owner 的地方（06/08），空在最该有 owner 的地方（准入）。** 讲得最可复核的一簇（06/08 控制面）有明确 owner、有正负向 probe；而准入——**影响所有请求分流**——owner 是 Unknown。再分层等于在**没有 owner 的地基上向上加层**。
3. **没有任何已执行的测量要求升一级。** 「复杂度阶梯」（Tool → Subgraph → parallel worker → Specialist → Persistent Multi-Agent）的每一级都应该由「上一级在某个 measured constraint 下失败」驱动。本轮 **measured constraint 为零**：整层 GraphRAG 的 holdout 未执行、Memory 无 A/B、Native Runtime 的必要性 `not established`。在没有一条「单级失败了」的测量之前，升 Multi-Agent 属于 Attack Model §4「『已经实现』不能成为继续保留的理由」的同型错误。

**逐个替代方案的判断：**

| 替代 | 判断 | 理由（从 failure/constraint 推） |
| --- | --- | --- |
| **Multi-Agent / Persistent Multi-Agent** | **不值得（今天）** | 见上三条。kill condition：当且仅当出现一个**已测量**的请求类，其单 Controller + 受管工具在准确率/可追溯性上**被证明**失败，且失败根因是**并行独立判断**而非准入/归属，才重新评估。 |
| **Specialist Agent** | **不值得（今天）** | 目标域（中文法律）**零验证**（A123-A125）。在域内没有一次人工看过结果的情况下，拆 Specialist 是在**未验证的域**上做**未验证的分解**。 |
| **Subgraph** | **保持现状** | 当前 Runtime 已经用「单 Controller + governed binding + 图」承载执行；子图只会移动边界，不解决归属。 |
| **Generic Host / 纯 LangGraph** | **需要一次真对照，但对照缺失** | A144 自认「通用 Host 从未对照」；A42/A43 自认 Native Runtime 必要性 `not established`。**正解不是切到 Generic Host，而是先跑那次从未跑过的 A/B/C**（P4 同型问题）。在对照完成前，两边都不可宣告。 |
| **Native Runtime（现有自研）** | **保留，但挂 measurement gate** | Owner / Contract / Build-Buy 因果 / 删除判据**四件都齐**（F-13 = NOT A GAP）；缺的是「被证明值得」。按 B12，保留的前提是它自己的 measurement gate 方向不翻。 |
| **单体（全删回单步）** | **P1 的最简单替代** | 删掉 `_plan_kind_for` 的 complex 判据 ⇒ 消灭「空 plan run」形态，代价是放弃「复杂任务」产品叙事。这是**唯一可零代码先做**的减法，且与 B12 一致。 |

**一句话：本轮所有「高级替代」都输给「先补归属、先跑测量」。** Multi-Agent 不是默认升级路线（protocol.md §Apply 明文）。

---

## 5. Authority / Owner / State / Contract / Recovery / Security 调整建议

> 本轮是 Reflection，`improvement_review_gate: REQUIRED` 未过。以下全部是**建议**，不改语义。

- **Authority（准入）**：给 `_plan_kind_for` 这张表一个 owner。它决定**所有** workspace 请求的分流，却落在一条字符串表上、无 decision record（`docs/decisions/` 经本轮确认无对应 ADR；`docs/decisions/0014` 只泛泛谈「调用准入」，不含这条边界）。**最小动作**：在模块 reference 落一条 Guard 条目，署名 owner。**不动 02/06/08 的既有 Authority。**
- **Owner（准入 + 状态新鲜度）**：把「planner 未绑定时 complex 的对外语义」写成**受控拒绝**，指定一个 owner；F-12 的 staleness owner 并入 F-08 处理，不单独立 gap。
- **State**：**不建议**为 complex 新增运行态。今天「空 plan run」这个形态本身就是问题——要么给它一个**定义**（受控拒绝，终态），要么**消灭它**（删判据）。**不新增状态机。**
- **Contract**：准入需要一个 contract 说明「被拦时这条 run 算什么」（`security_summary.decision="block"` 目前是事实，不是契约）。同时 F-04 的**残余**（幂等 key 含 `run_id`/`step_run_id`，跨 run 重发不命中旧 receipt）需要一个命名空间契约——但这是 small CONTRACT + 一条测试，**不是** Architecture。**注意**：`salt` 随机性风险本轮已被排除（见 §9.3），F-04 不应再被描述成缺陷。
- **Recovery**：**不改语义。** Owner-first recovery、checkpoint ≠ Domain commit、late result 必须重新验收，这些与 canonical 自洽（F-13）。Current 缺口（不可变 PlanVersion、Replan Barrier、AdmissionReceipt recovery）已在 runtime README 的 Gap 段登记，属 IMPLEMENTATION。
- **Security Authority**：**不改语义。** 08 拥有 recall/lifecycle/security eligibility 的声明保持；要做的是让 Current 追上（P3），而不是重新分权。

---

## 6. 应该删除的复杂度

### 6.1 直接删 / 归档

- **`ContextOrchestrator` 作为「统一入口」的身份**。本轮实测无生产调用点、canonical docs 从未命名它。**先删措辞、再判代码**：对比 `platform/services/application/context/contracts.py` 与 `memory/engine.py` 的 `build_context_pack` 输出契约——覆盖则删孤儿组件，不覆盖则把契约接到 `build_context` 节点。**这不是新抽象，是清理一个平行入口。**
- **`_plan_kind_for` 的 complex 判据（备选）**：若产品决定不做 Dynamic DAG，直接删 complex 判据，全部走 `simple` + `tool`。**零代码以外的代价**：放弃「复杂任务」产品叙事。与 B12 一致。
- **`fusion_score` 的死计算**：本轮实测它写进 metadata 但**不进排序键**（A198/A97 与 `_rank_key` 一致）。若确无消费者，删除或明确其为 trace-only 并接受「算而不用」。

### 6.2 收敛成开关（不删，但必须可 off）

- **GraphRAG 的 9 条启发式**：保留，但按冻结协议确保每条有可关闭开关——**或**按耦合链分组（`alias → seed` 是一根链；`_graph_signal` 是一个四计数器共享信号）。**不上调为架构改造**：**不要**引入 `heuristic_mask` 之类的架构级机制（Wave 1 曾备选，Wave 2 已撤回，我维持撤回）。
- **`escalate_due_reconciliations` 的时间阈值**：保留为开关，但**先接驱动**，否则它不生效。

### 6.3 我**不**建议删的

- **Native Runtime 的自研恢复语义**：Owner/Contract/Build-Buy/删除判据四件齐（F-13）。它**没有**被证明值得，但也**没有**被证明该删——缺的是那次从未跑的对照。
- **typed contracts 与 scope 语义**：是 Current 的真实行为（在节点层）。删的是 **ContextOrchestrator 这个入口身份**，不是契约层。
- **Memory 的 review/provenance 过滤**：它是当前唯一生效的读回护栏（P3）。删它会扩大安全缺口。
- **`DeleteRestoreRuntime` / `PersistentDeleteRestoreCoordinator` 代码本身**：状态机完整、有测试。它的问题只在于**被讲成 Current**（P2），不在于存在。

---

## 7. Current / Target / Evidence / Unknown 分层清单

| 层 | 内容 | 依据 |
| --- | --- | --- |
| **CURRENT** | `tool`/`simple`/`complex` 三值准入；complex 在 shipped composition 下产出**空 plan + decision=block** 的 run；中文「报告」会把普通请求判成 complex。 | `simple_agent.py:2150`、`main.py:113`、`single_controller_runtime.py:737-739/814-818/870-911` |
| **CURRENT** | memory 读回的真实门 = scope 四列 WHERE + 存储状态位（`review_status`/`memory_state`/sensitive tags）；**无**独立 08 recall decision。 | `recall_eligibility` 在 `src/` 0 命中（本轮实测） |
| **CURRENT** | 知识检索路径用 `retrieval/fusion.py` 自制 group/tier/baseline 方案；`fusion_score` 写 metadata 不进排序键。仓内另有 RRF（`agentic_graphrag.py:876`，k=60）**未用于该路径**。 | `fusion.py:9/951-977`、`agentic_graphrag.py:876/1411` |
| **CURRENT** | `ContextOrchestrator` / `DeleteRestoreRuntime` / phase08 `PostgresSaver` / `escalate_due_reconciliations` / `record_manual_effect_assessment` 均**无非测试调用方**。 | 本轮 `grep -rn` 实测 |
| **TARGET** | B1 #3 + B4 Profile B：complex 必须落到 immutable PlanVersion 的 Dynamic DAG。 | `docs/modules/reference.md:237` |
| **TARGET** | 08 拥有 recall/lifecycle/security eligibility，01/04 消费 current decision。 | `docs/architecture/reference.md` B2/B10/B18 |
| **TARGET** | `KnowledgeGeneration` / `ServingPointer` / `ReadinessDecision` / `WAITING_RECONCILIATION`：Target 概念，`src/` 0 命中。 | 本轮实测（N-02） |
| **EVIDENCE** | `AUD-L1` verified、`AUD-L2` NOT-IMPLEMENTATION-PROVEN；unknown-effect restart replay fix verified / unknown preserved。 | `docs/evidence/README.md` |
| **EVIDENCE** | 本轮实测：**没有**任何测试断言 complex 准入 block；**没有** `full-minus-H` 落盘结果；`GRAPH_PROMOTION_THRESHOLD` 无 calibration。 | 本轮 grep + sed |
| **UNKNOWN** | 空 plan run 在 runtime 下游如何呈现；「report/direct-route」准入门应由 01 还是 04 拥有；`_plan_kind_for` 关键词表作者（A105/A159 双 Unknown）；知识检索路径是否任何配置下都不经 RRF。 | 候选人自认 + 本轮未解 |
| **UNKNOWN** | 中文法律域上 GraphRAG 的方向；整层 on/off 的真实边际；token 成本。 | 协议 `BLOCKED_PENDING_DATA` |

---

## 8. 还缺什么 measurement

每条标注「今天可跑，零新数据」或「需新数据」。

- **M1（今天可跑，零新数据）— F-01 确定性断言。** 写并运行 `plan_kind=complex ∧ planner=None ⇒ _blocked_request ∧ plan_steps=()`；再追该 `RuntimeStartRequest` 在下游如何被消费。**判据**：断言通过 + 空 plan run 的下游语义被一句话定义 ⇒ F-01 的 Contract 缺口收口或保留。本轮已确认**当前无此断言**。
- **M2（今天可跑，零新数据）— N-01 接线状态表。** 对每个可疑孤儿跑「是否有非测试调用方」的 grep，产出「组件 | 定义位置 | 非测试调用方 Y/N | 被谁当 Current 讲过」。它同时决定 P2 / P3 / P5 的 Current 强度。
- **M3（今天可跑，零新数据）— N-02 Target 词 ↔ 代码符号对照表。** 逐词给「代码符号」或「src 无实现」二选一。
- **M4（今天可跑，零新数据）— N-03 的静态一半。** 确认知识检索路径是否**任何配置**下都不经过仓内 RRF；若可配置，把 A/B 排入 M6。
- **M5（今天可跑，零新数据）— 冻结协议的消融单位修订。** 读协议 §3，把启发式按 `alias→seed` 链与 `_graph_signal` 共享信号分组，输出「哪些应合并成一个臂」。**不需要数据集即可先做。**
- **M6（需新数据）— 整层 on/off（含 RRF 臂）。** GraphRAG 整层 on/off 两臂；若可用，加一臂「图权重 0」；再加一臂「改用仓内 RRF」。判据见协议 §2；「一条都不留」是合法终点。
- **M7（需新数据）— 中文法律域的第一件事。** 按 A168 的三步：先量 baseline 在中文卷宗上的 Recall@k；再查英文线索是否触发；再量 CitationProvenanceGuard 的拒绝率。第一步过不了 ⇒ GraphRAG 修复对法院域「暂时不适用」。
- **M8（需新数据）— 那次从未跑的 A/B/C。** Native Runtime vs Generic Host vs 纯 LangGraph。A144/A42/A43 自认从未对照、必要性 `not established`。这是「保留/外置 Native Runtime」唯一缺的测量。

**优先级：M1 > M2 > M3 > M4 > M5（全部零新数据） > M6 / M7 / M8（需数据）。**

---

## 9. Findings

### 9.1 架构侧

| ID | Finding | 标签 | 源码依据（本轮核过） |
| --- | --- | --- | --- |
| **F-01** | Workspace 准入边界（`_plan_kind_for` → complex → `_blocked_request`）无 Authority、无 Contract；产出「有 entrant、无 Plan」的 run，违反 B1 #3。**本轮独立复现全链。** | **ARCHITECTURE_GAP**（Owner + Contract） | `simple_agent.py:2150-2156`；`main.py:113`；`single_controller_runtime.py:737-739/814-818/825/870-911`；`docs/modules/reference.md:237` |
| F-08 | Recall eligibility 的 08 门在 Current 无落点；今天 scope 相等事实上即授权，与声明相反。 | IMPLEMENTATION_GAP（Security） | `recall_eligibility`/`RecallEligibility` 在 `src/` 0 命中（本轮 grep） |
| F-02 | 远端 Effect 收敛人工兜底；无后台 reconciler。 | IMPLEMENTATION_GAP | `invocation_gateway.py:1607`（`escalate_due_reconciliations` 仅测试调用） |
| F-03 | AUD-L2（send 后 crash/restart）NOT-IMPLEMENTATION-PROVEN。 | IMPLEMENTATION_GAP | `docs/evidence/README.md`（引用复述，未核原文行） |
| F-05 | 检索启发式的 measurement gate 未执行（`BLOCKED_PENDING_DATA`）。 | EVIDENCE_GAP | `fusion.py:9`（`GRAPH_PROMOTION_THRESHOLD = 6`，无 calibration 落盘） |
| N-01 | 孤儿组件是**模式**：代码在、驱动不在。 | DOC_GAP + NARRATIVE_GAP | `grep -rn` 实测：ContextOrchestrator / DeleteRestoreRuntime / phase08 PostgresSaver / escalate / record_manual 均无非测试调用方 |
| N-02 | Target 词 ↔ 代码符号无对照表（假阴性陷阱）。 | DOC_GAP | `KnowledgeGeneration`/`ServingPointer` 在 `src/` 0 命中（本轮 grep） |
| N-03 | 仓内已有 RRF（k=60）但未用于知识检索路径。 | EVIDENCE_GAP（Build-Buy 边缘，**不上调**：替代方案未经 A/B 证明更优） | `agentic_graphrag.py:876/883/1411` |
| N-04 | 冻结协议的消融单位把耦合链/共享信号当独立机制。 | GOVERNANCE / EVIDENCE（**不上调**：gate 存在且有序） | `fusion.py:156-163`（`_graph_signal` 四计数器求和）；`:166-187`（`_candidate_group` 依赖它）；`entity_alias.py:56-59` → `retriever.py:343`（alias→seed 一根链） |
| N-05 | Zuno 自研 delta 塌缩到「准入」，与 F-01 合流。 | Build-Buy 因果（**不单列新 gap**） | 同 F-01 |
| F-04 | 幂等 key 的 `salt` 契约 + 跨 run 命名空间；`create_calendar_event.py:57` 的 `uuid4` 幂等键角色未判。 | **small CONTRACT（已降级；salt 随机性风险本轮排除）** | `mcp_tool_executor_adapter.py:136`、`simple_agent.py:217`（salt 确定）、`create_calendar_event.py:57` |
| F-10 | `MemoryScope` 第四维 `agent_id` 在 Current 塌成常量。 | SEMANTICS（小） | A130 自认（未核 `core.py` 该行） |
| F-12 | staleness 无刷新 owner。 | OWNER（小，并入 F-08） | A131 自认（未核） |
| F-11 / F-13 / F-14 / F-15 | 冲突 memory 不仲裁（by design）；Runtime 恢复四件齐；Pilot 全 Unknown；Generation 是 Target。 | **NOT A GAP** | 本轮对 F-13/F-15 的 Current 侧做了 grep 支持（phase08 未接线、Target 词 0 命中） |

**`ARCHITECTURE_GAP` 最终清单：只有 F-01 一条。** 条件性集合为**空**（F-06 已降级）。

**关于 F-06 降级是否成立——我判定成立。** 理由（我在源码上复核过）：Wave 1 的升级逻辑是「gate 本身不可执行 ⇒ 越过 §13 门槛」。但 §13 的触发条件是「**复杂度缺乏**可删除 / measurement gate」。实测表明 gate **存在、冻结、有 owner**（协议 `FROZEN_PROTOCOL` / owner 03+09），缺陷只在**消融单位**（把 `alias→seed` 这根链、把 `_graph_signal` 这个共享信号当成独立机制）。而正解（按耦合链分组 / 整层 on/off）**不需要**架构变更。把「协议该把 9 条合并成几组臂」判成 Architecture Revision，会与 §13 高门槛正面冲突。**⇒ F-06 = GOVERNANCE / EVIDENCE，降级成立。** 残余记为 N-04。

### 9.2 非架构侧（改措辞 / 归属 / 材料，不改代码 → `proposed_change: none`）

| ID | Finding | 标签 | proposed_change |
| --- | --- | --- | --- |
| G-01 | 简历第 1 条「复杂请求进入 ReAct 路径」与候选人自述的 Current（准入层 fail closed）互斥。 | SIMULATED_RESUME_GAP / NARRATIVE_GAP | none |
| G-02 | 简历第 4 条用 `ContextOrchestrator` 作为集成点；真实入口是节点层。 | NARRATIVE_GAP | none |
| G-03 | 简历第 3 条把 `alias → seed` 一根链讲成两个独立机制。 | NARRATIVE_GAP | none |
| G-04 | 简历第 2 条「baseline-preserving」被读成全局不变量；guardrail 在三类 query 上**故意**覆盖下限。 | NARRATIVE_GAP | none |
| G-05 | 简历第 6 条（Pilot）是近零信息行。 | SIMULATED_RESUME_GAP | none |
| G-06 | 「命名组件 ≠ 在跑的组件」在候选人自述里普遍存在（N-01）。 | NARRATIVE_GAP | none |
| G-07 | 引用纪律：带行号的引用必须实跑（本轮 `A8/A56` 的「抛」动作错、目录欠指定；`A101` 对自己 Wave 1 错误的复述又不准）。 | NARRATIVE_GAP / BLUE_SKILL_GAP | none |
| G-08 | Resumer Gate 自身引入的措辞方向错误（`00_artifact_links.md` 已记录：把「复杂或参数不完整回落 ReAct」改成「复杂请求进入 ReAct 路径」，方向反了）。 | SIMULATED_RESUME_GAP（NEXT_ROUND_ONLY） | none |

> 注：G-01..G-08 的正解全部是**改措辞 / 归属 / 材料**，不动代码。按本轮分类口径，它们进 `NARRATIVE_GAP` / `SIMULATED_RESUME_GAP`，`proposed_change: none`。

### 9.3 Red Final 判错清单（我独立回源码核过的）

> 口径：只写我真的打开过源码核过的。Red Final 是盲的、且自我声明只做结构判断，因此它的「判错」几乎全是**过强表述**，不是凭空错误。这一节的价值在于：**只有能读源码的一方才能说清它错在哪。**

**RF-01 —— 「不存在的对象」（`04_red_evaluation.md` §2.3，A128 之于简历第 4 条）：过强。**
Red Final 写：「第 4 条的『接入 Agent 调用前读取与回合后写入』在 Wave 1 里是靠一个**不存在的对象**支撑的。」
本轮核实：`prepare_context` **确实作为符号存在**——`agent/harness.py:269`（`name="prepare_context"` 的节点）、`:9`（在列表中）、`agent/durable_runtime.py:416`、`agent/post_turn.py:43`、`agent/runtime_batch.py:501`；`src/backend/zuno/agent/core/README.md:11` 也以它为阶段名。
**准确说法**：错的是**对象归属与 live 路径**——`GeneralAgent.prepare_context` 不是一个 live 方法，真实装配入口是 `agent/runtime/nodes/core.py:62 build_context` → `:79 build_context_pack`（写入侧 `:391 post_turn_commit`）。**它是「命名错位的对象」，不是「不存在的对象」。** Red Final 的用词把一个**归属错误**说成了一个**存在性错误**。

**RF-02 —— 「两处硬错」（`04_red_evaluation.md` §2.1 #1）：过强，且它接受的是 Blue 自己的不准自述。**
Red Final 写：A101「**主动修正 Wave 1 两处硬错**（`single_controller_runtime.py` 的真实路径；`:497-501` 是 `return None` 而非抛异常）」。
本轮核实：`03_blue_answers.md` 的 A8（`:121`）只写 `single_controller_runtime.py:497-501`，**根本没写目录**（`:122` 里的 `agent/runtime/execution/react_runner.py` 指的是**另一个文件**）。而「写成在 `agent/runtime/execution/` 下」这个说法出自 **Blue-2 自述**（`04_blue_wave2_answers.md:21`）——它**误述了自己 Wave 1 的错误**。
**准确说法**：真正的硬错只有**一处**（把 `:497-501` 的 `return None` 说成「抛」）；「目录」只是**欠指定**（没写目录 ≠ 写错目录）。§9.1 的 F-01 依据本轮已独立确认：全文件**不存在** `raise DYNAMIC_PLAN_RUNTIME_NOT_BOUND`，`build_workspace_plan_steps`（`:465`）在 `:497-501` 是 `return None`。
（附注：Controller 在 `00_artifact_links.md` 已独立得出同一结论，并记录这是「关于错误的错误」。本轮从源码侧再次确认。）

**RF-03 —— Red Final 主动保留的 2 个未知，本轮闭合，且方向皆指向 Blue 正确（不是 Red 判错，是它的保留被证明不必要）：**
1. `04_red_evaluation.md` §6 #2：Red Final 说无法核实 `{salt}` 是否确定，若另有随机来源则 A106/A107 会从「反击」变成「辩护」。**本轮核实：`salt` 是确定的**——`capability/mcp/mcp_tool_executor_adapter.py:136` 透传，唯一生产调用点 `simple_agent.py:217` 传 `salt=str(getattr(binding,"name","") or resolved_tool_id)`，由动作身份决定，默认空串。**Red Final 的保留不必要；A106/A107 的「证伪攻方」成立。**
2. `04_red_evaluation.md` §6 #4：Red Final 说无法核实 `final_top5_floor_preserved` 是否真存在。**本轮核实：存在**——`fusion.py:888`（置 `None`）、`:948`（返回 `floor_preserved`）、`:1037`，而 `:943 floor_preserved = promoted_candidate is None`。**Red Final 的保留不必要；A117/A118 的「真矛盾」在代码层有落点。**

**RF-04 —— 一处我没有核、因此不写成判错的地方（诚实边界）。**
Red Final §5 F9 与 §2.3 说「仓内已有 RRF 但**未用在知识检索路**」（承接 A199）。本轮核实 RRF **确实存在于** `agentic_graphrag.py:876`（strategy `local_rrf_then_score_rerank`）；但我**没有**追完 `api/services/product/runtime_engine.py:23` 对 `agentic_graphrag` 的调用图，因此**无法判定** agentic_graphrag 的 RRF 路径是不是一条 live 的产品检索路径，还是知识 README 所称的 facade/trace 契约层。**故我不把「未用在知识检索路」写成 Red 的判错**——它是一条**待复测的未知**（已并入 §8 M4）。这与 A199 自己的边界一致（它也不主张 RRF 一定更好）。

**小结：本轮我核出 Red Final 2 处过强表述（RF-01、RF-02），并闭合它 2 个主动保留的未知（均指向 Blue 正确）。** 这个比例本身是交叉验证信号：Red Final 在没有源码的情况下，**几乎没有**产生凭空错误，它的偏差集中在「把归属错误说成存在错误」「接受候选人不准的自述」这两类**过度精确**上。

---

```text
Reflection 完毕。
ARCHITECTURE_GAP: 1 条确认（F-01，独立复现全链）。条件性集合：空（F-06 降级成立）。
非架构：N-01 孤儿组件模式 / N-02 Target 词漂移 / N-03 仓内 RRF 未试 / N-04 协议消融单位 / N-05 delta 塌缩（合流 F-01）；
        F-02/F-03/F-08 IMPLEMENTATION；F-05 EVIDENCE；F-04 small CONTRACT（salt 随机性已排除）。
Multi-Agent：不值得（今天）。正解是先补归属（F-01）与先跑测量（M6/M7/M8），不是升层。
§9.3：核出 Red Final 2 处过强表述（RF-01「不存在的对象」、RF-02「两处硬错」），闭合其 2 个保留未知（均指向 Blue 正确）。
越界读取：无（未读 docs/red-blue/rounds/**，未带回任何归档片段）。
```
