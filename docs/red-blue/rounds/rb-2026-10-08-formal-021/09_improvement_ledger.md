# Improvement Ledger — rb-2026-10-08-formal-021

```text
improvement_ledger_status: APPROVED_FOR_NEXT_ROUND
change_effective_scope: NEXT_ROUND_ONLY
current_round_verdict_recomputed: false
base_sha: cdd2063b341e6919fafaa1395d1f3bdc837329f6
head_observed: 8fce286e
improvement_review_gate: PASSED（2026-10-08）
applied_this_round: none（findings / verdict 层 —— 本轮结论未因本文件改变）
skill_harness_written_this_round: IMP-021-11..IMP-021-19 → .agent/red-blue/（下一轮生效）
```

**本文件已获用户批准（`USER_IMPROVEMENT_REVIEW`，2026-10-08，见 `07_user_feedback.md`）。**
批准**不改变本轮 verdict**，也不把任何 finding 的等级上调：`IMP-021-01` 仍是本轮唯一确认的 `ARCHITECTURE_GAP`，
只是状态由 `proposed` 变为 `approved`；`IMP-021-02`..`IMP-021-10`、`IMP-021-20` 维持原判等待下一轮处理。

**批准后各组的实际去向：**

| 组 | 条目 | 去向 |
| --- | --- | --- |
| A 架构 | `IMP-021-01` | 批准，**下一轮**写 owner + 最小 decision record（本文件已记录复测口径） |
| B 实现 | `IMP-021-02/03/04` | 批准，下一轮处理 |
| C 减法 | `IMP-021-05` | 批准（仅清单化，不新增删除动作） |
| D Evidence | `IMP-021-06/07` | 批准，`MEASUREMENT_NEEDED` 不变，**不新增收益数字** |
| E 表达 / 简历 | `IMP-021-08/09/10/20` | 批准；`G-01`..`G-06`/`G-08` 落入 `10_next_resume_candidate.md` |
| F 流程 | `IMP-021-11`..`IMP-021-19` | 批准，**本次写入 `.agent/red-blue/`**，下一轮生效 |

**时序边界（必须保留）：** 本轮 400 条记录是用**旧 Skill** 产出的。Skill 修改是**跨轮生效**，
不是对本轮的事后修补，也不回溯改判本轮的 findings、round report 或 verdict。

**判定纪律（沿用 round 020，未改）：**

- 系统本身没问题、只是讲不清的 → `NARRATIVE_GAP` / `SIMULATED_RESUME_GAP`，**`proposed_change: none`**。
- 设计写了但代码没有的 → `IMPLEMENTATION_GAP`，如实标 `Target`。
- 只有 Owner / Authority / State / Contract / Recovery / Security / Build-Buy 因果本身不成立，才进 `ARCHITECTURE_GAP`。
- **不制造任何收益数字。** 所有量化 TBD 一律标 `MEASUREMENT_NEEDED`，不填估计值。
- **不把 `IMP-020-09` / `IMP-020-10` 转换成架构改动。**

**Controller 独立验证声明：** 下表凡标 `CONTROLLER_VERIFIED` 的，由 Controller 本轮亲自打开源码/提交复核
（`file:line` 见「证据」列）；标 `BLUE_VERIFIED` 的沿用 Blue 架构侧本轮复核结论；标 `RED_STRUCTURAL` 的
来自 Red Final，**只作结构判断，不得当事实用**。

---

## A 组 · 架构（本轮唯一 `ARCHITECTURE_GAP`）

### IMP-021-01 — Workspace 准入边界无 Authority、无 Contract（`F-01`）

```text
owner: Architecture（docs/architecture/ + ADR）
tag: ARCHITECTURE_GAP（Owner + Contract）
verification: CONTROLLER_VERIFIED
verdict_recomputed: false
```

**问题**：`_plan_kind_for`（`simple_agent.py:2150-2156`，含中文「报告」）把请求分为 `tool` / `simple` / `complex`；
产品装配 `main.py:113` 的 `dynamic_dag_planner=None`；`single_controller_runtime.py:737-739` 判 `complex_unbound`
→ `:814-818` 置 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND` → `:825` `_blocked_request`。**拦截不抛异常**，而是返回一个
`plan_steps=()` / `capability_ids=()` / `allowed_tools=()` / `strategy_mode=None` /
`security_summary={"decision":"block"}` 的**正常 `RuntimeStartRequest`**（`:870-911`，docstring 自称
"Fail-closed RuntimeStartRequest: no plan, no tools, reason visible"）。

**为什么是架构缺口（不是措辞）**：`docs/modules/reference.md:237` 是**已接受的架构不变量**——
「Native Runtime entrant 一定有 Plan：简单单步，复杂 Dynamic DAG」。而被拦下的复杂请求产出的正是一个
**无 Plan 的 entrant**。⇒ 一个改变执行语义与授权路径的准入决定，既没有 Authority（`A105` token 表作者自认 Unknown、
`docs/decisions/` 无对应 ADR），也没有 Contract 说明「被拦时这条 run 算什么」。

**建议动作**：写 owner + 一份**最小 decision record**，把「planner 未绑定时的复杂请求」正式定义为
**受控拒绝**。**不需要**新增模块或状态机。

**成本 / 退出条件**：成本 ≈ 一份 decision record + 一处措辞。
退出条件：(a) 产品组合绑定 Dynamic DAG planner 且 B4 Profile B 端到端可跑；或 (b) 接受一次 Revision，
把 complex 对外语义定义为受控拒绝并记录。

**下一轮复测**：① `grep -rn "dynamic_dag_planner" src/backend/zuno/main.py` 是否仍为 `None`；
② 补并运行「`complex` + planner=None ⇒ `_blocked_request` 产出 `plan_steps=()`」这条**确定性断言**（A102 说可写、今天没写）；
③ 检查 `docs/decisions/` 是否出现准入 owner 记录；④ 检查空 plan run 的下游呈现是否被定义（今天 Unknown）。

> `N-05`（Zuno 自研 delta 塌缩到「准入」）与 `F-01` 合流，**不单列**。

---

## B 组 · 只做了一半的实现

### IMP-021-02 — Recall eligibility 的 08 门在 Current 无落点（`F-08`）

```text
owner: Implementation
tag: IMPLEMENTATION_GAP（Security）
verification: BLUE_VERIFIED
```

**问题**：`recall_eligibility` / `RecallEligibility` 在 `src/` **0 命中**；今天 scope 相等事实上即授权，
与「scope equality != authorization」的声明相反。
**动作**：如实标 `Target`，或在实现层给出落点。**下一轮复测**：重跑该 grep。

### IMP-021-03 — 远端 Effect 收敛只有人工兜底，无后台 reconciler（`F-02`）

```text
owner: Implementation
tag: IMPLEMENTATION_GAP
verification: CONTROLLER_VERIFIED（`invocation_gateway.py:1607` 调用方仅测试）
```

**动作**：`Target`。**下一轮复测**：`escalate_due_reconciliations` / `timeout_due_async_jobs` 是否出现非测试调用方。

### IMP-021-04 — AUD-L2（send 后 crash/restart）未实现证明（`F-03`）

```text
owner: Evidence（与 IMP-021-03 同源）
tag: IMPLEMENTATION_GAP
verification: BLUE_VERIFIED（引用复述 `docs/evidence/README.md`，未核原文行 —— 标为待核）
```

**动作**：补一条崩溃窗口实验，或维持 `NOT-IMPLEMENTATION-PROVEN` 的诚实标注。

---

## C 组 · 可以做减法

### IMP-021-05 — 孤儿组件是**模式**，不是孤例（`N-01`）

```text
owner: Narrative / Docs + Implementation（清单化）
tag: DOC_GAP + NARRATIVE_GAP
verification: BLUE_VERIFIED（本轮 grep 实测）
proposed_change: 仅清单化，不新增删除动作
```

**问题**：以下代码在、驱动不在（非测试调用方为零）：`ContextOrchestrator`、`DeleteRestoreRuntime`、
phase08 `PostgresSaver` 桥、`escalate`、`record_manual`。
**动作**：把「命名组件 ≠ 在跑的组件」做成一份**可复核清单**（组件 / 是否有非测试调用方 / 是否 Target），
逐个决定删 / 收敛成开关 / 保留。**不建议**在缺测量的前提下直接删。

> `F-11` / `F-13` / `F-14` / `F-15` 本轮判定 **NOT A GAP**（冲突 memory 不仲裁是 by design；Runtime 恢复四件齐；
> Pilot 全 Unknown；Generation 是 Target）。**不上调**。

---

## D 组 · Evidence / 先测再决定架构

### IMP-021-06 — 检索启发式的 measurement gate 未执行（`F-05` + `N-04`）

```text
owner: Evidence
tag: EVIDENCE_GAP（`N-04` 为 GOVERNANCE / EVIDENCE，不上调）
verification: BLUE_VERIFIED
```

**问题**：`fusion.py:9` `GRAPH_PROMOTION_THRESHOLD = 6` 无 calibration 落盘；冻结协议状态 `BLOCKED_PENDING_DATA`。
且协议（`N-04`）的**消融单位**把耦合链当独立机制：`alias → seed` 是一根链
（`entity_alias.py:56-59` → `retriever.py:343`）、`_graph_signal` 是共享信号
（`fusion.py:156-163` 四计数器求和，`:166-187` `_candidate_group` 依赖它）。
**动作**：`MEASUREMENT_NEEDED`。按**耦合链**分组、或整层 on/off，再跑消融。**不新增收益数字。**

### IMP-021-07 — 仓内已有 RRF，但未用于知识检索路径（`N-03`）

```text
owner: Evidence
tag: EVIDENCE_GAP（Build-Buy 边缘，不上调：替代方案未经 A/B 证明更优）
verification: CONTROLLER_VERIFIED（`agentic_graphrag.py:876` k=60，`local_rrf_then_score_rerank` `:1411`）
```

**动作**：`MEASUREMENT_NEEDED`。先做 A/B，再决定是否替换自研融合。
**诚实边界**（Reflection `RF-04`）：未追完 `product/runtime_engine.py:23` 对 `agentic_graphrag` 的调用图，
**无法判定**该 RRF 路径是否是一条 live 的产品检索路径 —— 这是**待复测的未知**。

---

## E 组 · 表达 / 简历（**明确不得走架构改动**）

### IMP-021-08 — 简历五条 + 项目简介的措辞处置（`G-01`..`G-06`、`G-08`）

```text
owner: Resume（下一轮 Resume Candidate）
tag: SIMULATED_RESUME_GAP / NARRATIVE_GAP
proposed_change: none（改措辞，不改代码）
```

逐条（ID 与 `05_blue_architecture_reflection.md §9.2` 一致）：

| ID | 简历条 | 问题 | 处置 |
| --- | --- | --- | --- |
| G-01 | 第 1 条 | 「复杂请求进入 ReAct 路径」与 Current（准入层 fail closed）**互斥** | **下一轮改成可复核措辞**：「复杂请求需要绑定动态规划器，未绑定时在准入处 fail closed」 |
| G-02 | 第 4 条 | 用 `ContextOrchestrator` 作集成点；真实入口是节点层 | 降为 typed contract 层表述 |
| G-03 | 第 3 条 | 把 `alias → seed` 一根链讲成两个独立机制 | 合并为一个耦合机制 |
| G-04 | 第 2 条 | 「baseline-preserving」被读成**全局**不变量；guardrail 在三类 query 上**故意**覆盖下限 | 收窄为「排序阶段的不变量」 |
| G-05 | 第 6 条（Pilot） | 近零信息行 | 保持 Unknown，或删 |
| G-06 | 通篇 | 「命名组件 ≠ 在跑的组件」（同 `N-01`） | 逐条核对是否在 live path |
| G-08 | — | **Controller 自己在 Resume Gate 把第 1 条改错了方向**（`00_artifact_links.md` 已记录） | 必须由下一轮 Resume Gate 连同核验一起改 |

### IMP-021-09 — Target 词 ↔ 代码符号缺对照表（`N-02`）

```text
owner: Narrative / Docs（canonical documentation owner）
tag: DOC_GAP
proposed_change: 建表，不改代码
```

**问题**：`KnowledgeGeneration`、`ServingPointer` 在 `src/` **0 命中**（Target 词），却容易被当成 Current 讲。
**动作**：建一份「Target 词 → 对应代码符号（或「无」）」对照表，防假阴性陷阱。

### IMP-021-10 — 引用纪律：带行号的引用必须实跑（`G-07`）

```text
owner: Blue Skill（下一 Round 生效）
tag: BLUE_SKILL_GAP / NARRATIVE_GAP
proposed_change: none
```

**问题（三轮叠在一起）**：① `A8`/`A56` 把 `:497-501` 的 `return None` 说成「抛」（动作错）；
② `A101` 对自己 Wave 1 错误的复述**又不准**（说「写成在 `agent/runtime/execution/` 下」，
实际 Wave 1 **根本没写目录**，是欠指定不是写错）；
③ Red Final 把 `prepare_context` 说成「不存在的对象」（它作为符号存在：`agent/harness.py:9`/`:269`）。
**动作**：带 `file:line` 的引用必须**实跑**该行；**自我修正**同样要回源码核（见 `IMP-021-13`）。

### IMP-021-20 — 幂等 key 的跨 run 身份语义（`F-04`，small CONTRACT）

```text
owner: Architecture（小）
tag: small CONTRACT（salt 随机性风险本轮已排除，故已降级）
verification: CONTROLLER_VERIFIED
```

**问题**：key 模板是 `{run_id}:{step_run_id}:{tool_name}:{salt}`（`mcp_tool_executor_adapter.py:70-73`），
`salt` **确定**（唯一生产调用点 `simple_agent.py:216-218` 传 `salt=str(getattr(binding,"name","") or resolved_tool_id)`，
默认空串）。⇒ 同 step run 内会**过度收敛**撞同一 key；跨 run 重跑 `run_id` 变化 ⇒ **不命中**旧 receipt。
另：`create_calendar_event.py:57` 用了 `uuid4().hex` 作幂等键，**其角色未判**。
**动作**：写清「跨 run 重发时谁去查旧 receipt」（A107 自标未证明），并判定那个 `uuid4` 的角色。

---

## F 组 · 流程 / 方法论（进入下一轮 Skill / Harness）

| ID | 提案 | Owner | 触发（`06_workflow_retrospective.md`） |
| --- | --- | --- | --- |
| IMP-021-11 | Resume Gate 核验清单新增「**装配侧确认**」：任何运行行为 claim 必须追到组装点（`main.py` / composition），不得停在类定义或单测 | Resume Builder / Skill | §1.1、§1.2 |
| IMP-021-12 | Attack Model 写入「**claim 被证伪 ≠ premise 被证伪**」；前提不成立不作候选人强弱证据 | Red Skill | §2.2 |
| IMP-021-13 | 「**自我修正**」不得直接采信，需回源码核；三段式格式不得作加分依据 | Blue Skill | §3.1 |
| IMP-021-14 | 每个 stage commit 增加 **manifest validator**（`yaml.safe_load` + 必需键） | Harness / Protocol | §4.4(a) |
| IMP-021-15 | 派发带 git 的 subagent 必须给**绝对仓库路径**并要求 `git -C <repo>` | Harness | §4.4(b) |
| IMP-021-16 | 产物**形态可校验清单**（标题层级 / 必需头部键 / 章节名） | Harness / Templates | §4.4(c) |
| IMP-021-17 | 等待条件须带**尺寸阈值 + mtime**（占位 blob 会被误当产物） | Harness | §4.4(d) |
| IMP-021-18 | `IMP-020-14` 修法**扩展**到「封存文件名不得出现在 Red 可见文件正文」（本轮新形态） | Harness / Protocol | §4.2 第 3 条 |
| IMP-021-19 | **Red Final 之后必须有回源码核对**（本轮由 Blue Reflection 承担，不可省） | Protocol | §2.4、§4.3 |

---

## 汇总

| 组 | 条数 | 说明 |
| --- | --- | --- |
| A 架构 | 1 | `IMP-021-01`（`F-01`，唯一 `ARCHITECTURE_GAP`） |
| B 实现 | 3 | `IMP-021-02/03/04` |
| C 减法 | 1 | `IMP-021-05`（清单化，不新增删除） |
| D Evidence | 2 | `IMP-021-06/07` |
| E 表达 / 简历 | 4 | `IMP-021-08/09/10/20` |
| F 流程 | 9 | `IMP-021-11`..`IMP-021-19` |
| **合计** | **20** | 全部 `NEXT_ROUND_ONLY`，`applied_this_round: none` |

**沿用 round 020 未决条目（本轮只做 base-alignment，未应用）**：
`IMP-020-04`、`IMP-020-05`、`IMP-020-06`、`IMP-020-07`、`IMP-020-08`、
`IMP-020-11`、`IMP-020-12`、`IMP-020-13`、`IMP-020-14`、`IMP-020-15`（共 10 条，状态仍 `NEXT_ROUND_ONLY`）。
其中 `IMP-020-11`..`IMP-020-15` 提议修改 Red / Blue Skill 与 Harness —— 本轮 pin 的 Skill blob 与 020
**逐字节相同**，即这些提案**尚未生效**，本轮仍按原 Skill 运行。

**用户已决定的三件事（2026-10-08，`USER_IMPROVEMENT_REVIEW`）**：

1. `IMP-021-01` —— **批准，最小方案**：下一轮写 owner + 最小 decision record，把「planner 未绑定时的复杂请求」定义为受控拒绝，**不新增模块或状态机**。
2. `IMP-021-08` —— **按上表全表落地**（`G-01`..`G-06`、`G-08`），由 `10_next_resume_candidate.md` 承载。
3. `IMP-021-11`..`IMP-021-19` —— **全部授权**修改 `.agent/red-blue/`，本次写入、下一轮生效。

原始提问与逐字选项文本见 `07_user_feedback.md`。
