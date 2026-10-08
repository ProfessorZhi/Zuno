# Blue Wave 2 — 架构复诊（Architecture Notes, Differential）

```text
sealed: true
readable_by: Blue Architecture Reflection only
round: rb-2026-10-08-formal-021
base_sha: cdd2063b341e6919fafaa1395d1f3bdc837329f6
head_observed: 957e8114

inputs:
  # 本轮成品与对手材料
  - docs/red-blue/workspace/rb-2026-10-08-formal-021/04_blue_wave2_answers.md   (A101–A200)
  - docs/red-blue/workspace/rb-2026-10-08-formal-021/03_blue_architecture_notes.md  (Wave 1 初诊，复诊对象)
  - docs/red-blue/workspace/rb-2026-10-08-formal-021/04_red_wave2_review_and_questions.md
  - docs/red-blue/workspace/rb-2026-10-08-formal-021/01_simulated_resume.md
  - docs/red-blue/workspace/rb-2026-10-08-formal-021/04_blue_wave2_architecture_notes.md  (预创建的 NOT_STARTED 占位)
  - .agent/red-blue/defense-model.md  (§12–§14 为重诊口径)
  # canonical — src（本轮亲自打开/实跑）
  - src/backend/zuno/main.py
  - src/backend/zuno/api/services/workspace.py
  - src/backend/zuno/api/services/product/command_service.py
  - src/backend/zuno/platform/services/workspace/simple_agent.py
  - src/backend/zuno/platform/services/workspace/single_controller_runtime.py
  - src/backend/zuno/platform/services/retrieval/fusion.py
  - src/backend/zuno/platform/services/graphrag/entity_alias.py
  - src/backend/zuno/platform/services/graphrag/retriever.py
  - src/backend/zuno/knowledge/ingestion/delete_restore.py
  - src/backend/zuno/knowledge/agentic_graphrag.py
  - src/backend/zuno/capability/tool_runtime/invocation_gateway.py
  - src/backend/zuno/memory/engine.py
  - src/backend/zuno/api/services/mcp_user_config.py
  - src/backend/zuno/platform/database/dao/mcp_user_config.py
  # canonical — tests / docs
  - tests/knowledge/test_ingestion_delete_restore.py
  - tests/capability/test_tool_effect_postgres_boundary.py
  - docs/governance/documentation-architecture.md
  - docs/governance/project-fact-provenance.md
  - docs/governance/rb019-graphrag-ablation-protocol.md
  - docs/modules/knowledge/README.md
```

```text
审计声明（诚实边界）：

1. 读了什么：本复诊以 04_blue_wave2_answers.md 为"候选人口径"，但所有结论一律回到 canonical
   source 重取——src 下逐个打开并 grep 了 F-01 / F-04 / F-05 / F-06 / F-07 / F-08 涉及的符号，
   docs 下读了 documentation-architecture.md（§"measurement-gated" 段）、project-fact-provenance.md
   （PF-017/019/020/025/031/032 及 GraphRAG 审计段）、rb019-graphrag-ablation-protocol.md（状态头
   与 §1 附近）、modules/knowledge/README.md（Target / Current / Gap 三段）。凡是本文件写
   file:line 的地方，都是本轮实际 sed/grep 过的行，不是从 Wave 1 或 Wave 2 答案里复述的。

2. 没读什么：**未打开** 03_blue_answers.md（A1–A100 原文）与 02_red_questions.md。对 A1–A100 的
   认识只来自 03_blue_architecture_notes.md 的引述与 04_red_wave2_review_and_questions.md 的
   Part A/B。凡引用 A1–A100 的地方都标为"经二次引述"。**未读** docs/red-blue/rounds/**（归档轮次，
   已记录的泄漏向量 IMP-020-14）。本文件的 finding 不依赖任何历史轮次结论。

3. 越界 grep 声明：为定位 `KnowledgeGeneration` / `ServingPointer` 在 canonical 文档里的出现位置，
   对本仓库 `docs/` 做过两次跨目录 grep（`grep -rln`）。输出顺带带回了
   `docs/red-blue/rounds/rb-2026-09-13-zuno-interview-batch-013/transcript-batch-001-{blue,red}.md`
   **两个路径名**（仅匹配文件名，**未打开、未读取其内容**），以及本轮 workspace 内
   `00_manifest.yaml` 的路径名。这些片段**没有被用作任何 finding 的证据**，本文件也不引用它们。
   已按要求如实声明。
```

---

## §0 复诊口径与 Wave 1 差分总表

本文件只做两件事：(a) 用 Wave 2 出现的新事实，逐条判定 Wave 1 那 15 条 finding 的去向；
(b) 把 Wave 2 新暴露、Wave 1 没有的系统性事实立为新条目。**它不是 Wave 1 的复述**。

§13 门槛重申并收紧执行：缺文档 / 没跑 benchmark / 候选人一时答不上 ⇒ 不得升级。
只有 Owner / Authority / State semantics / Contract / Recovery / Security Authority /
Build-Buy 因果 / 复杂度缺乏可删除-or-measurement gate 才够格。本波我对 Wave 1 的 F-06
**主动降级**，理由见 §2.1——这是本文件最实质的一次自我推翻。

### 差分总表

| Wave 1 | 主题 | Wave 1 分类 | Wave 2 判定 | 依据（Wave 2 新事实） |
| --- | --- | --- | --- | --- |
| F-01 | Workspace 准入边界无 Authority | **ARCHITECTURE_GAP** | **维持（强化）** | 独立复现链路；`_blocked_request` 产出的是"空 plan 的 run"而非异常；A105/A159 作者与 ADR 双 Unknown |
| F-02 | 远端 Effect 收敛人工兜底 | IMPLEMENTATION | **维持** | A147/A148：`escalate_due_reconciliations` 与 `record_manual_effect_assessment` **仅测试调用**（已实测）|
| F-03 | AUD-L2 未证明 | IMPLEMENTATION | **维持（强化）** | A150 给出最坏态（效果已发生 vs 报告 blocked，且无驱动对账）|
| F-04 | 幂等键 `salt` 无契约 | CONTRACT | **降级 / 改写** | A106/A107：salt 确定（撤回随机风险）；残余改为"key 含 run_id/step_run_id 的跨 run 身份语义" + `uuid4` 角色仍未判 |
| F-05 | 9 条启发式无已执行 measurement | **EVIDENCE_GAP** | **维持（强化）** | A112/A113/A114 排除"换模型"混淆；A187 明确"方向可归因、幅度不可分离"；N-03 新增仓内 RRF 未试 |
| F-06 | 逐条 heuristic 的可消融性 | **conditional ARCHITECTURE_GAP** | **降级为 EVIDENCE / GOVERNANCE** | 耦合被静态证实（alias→seed；`_graph_signal` 求和），但正解是"整层 on/off + 修协议消融单位"，非架构变更 |
| F-07 | "GraphRAG 只面向英文"过强 | ANSWER_QUALITY+EVIDENCE | **维持（强化）** | A123/A124/A125：英文关系词渗入域词汇；目标域**零验证**；迁移性只是假设 |
| F-08 | Recall eligibility 的 08 门无落点 | IMPLEMENTATION（安全） | **维持（强化）** | 实测 `recall_eligibility` 在 `src/` 仍 0 命中；A134 承认"未被记成待办" |
| F-09 | `ContextOrchestrator` 无 consumer | DOCS/ANSWER+CLEANUP | **升级范围** | 并入 N-01：孤儿组件是**模式**，非孤例（A183/A141/A147/A148）|
| F-10 | MemoryScope 四维实际三维 | SEMANTICS（小） | **维持** | A130：agent 轴被塌成常量 |
| F-11 | 冲突 memory 无语义仲裁 | **NOT A GAP** | **维持** | A133 补充"两条冲突候选各自独立走到 APPROVED"，与设计一致 |
| F-12 | staleness 无刷新 owner | OWNER_QUESTION（小） | **维持** | A131：状态迁移靠调用方自觉，无 reaper |
| F-13 | Runtime 恢复权威 / Build-Buy | NOT A GAP | **维持** | A139/A143 增加"实现未证"，但 Owner/Contract/删除判据仍齐 |
| F-14 | Pilot / 法院 / 中文泛化 | NOT A GAP（无证据） | **维持** | A162–A167 全 Unknown，无升级 |
| F-15 | `KnowledgeGeneration` 是 Target | NOT A GAP | **维持**（并派生 N-02） | A179/A180/A181：`src/` 0 命中已实测；发现 Target 词↔代码符号漂移 |

**新增（Wave 2 才成立的系统性事实）：**

| 编号 | 主题 | 分类 | 一句话 |
| --- | --- | --- | --- |
| N-01 | 孤儿组件是一个模式 | DOCS / ANSWER_QUALITY（范围扩自 F-09） | 多个"已实现 + 有测试 + 零生产调用点"的组件并存，使若干被讲成 Current 的行为其实是"代码在、驱动不在" |
| N-02 | Target 词 ↔ 代码符号无对照 | DOCS / EVIDENCE（新） | 按 Target 词搜 `src/` 得到假阴性；同一概念在两套命名下部分存在 |
| N-03 | 仓内已有 RRF 但未用于知识检索路径 | EVIDENCE / Build-Buy（新） | "重新发明"不成立，正确批评是"已存在的成熟 baseline 没试" |
| N-04 | 冻结协议的消融单位有缺陷 | GOVERNANCE / EVIDENCE（新） | H 系列把耦合机制当独立机制，逐条臂会把同一收益算两遍 |
| N-05 | Zuno delta 塌缩后收敛到"准入" | Build-Buy 因果（新） | A174/A75 的三分法里"注参"大多 commodity，残余 delta 集中在无 owner 的准入（与 F-01 合流）|

**ARCHITECTURE_GAP 计数：Wave 1 = 1 确认 + 1 条件性；Wave 2 = 1 确认（F-01）+ 0 条件性（F-06 已降级）。**

---

## §1 F-01 复诊 — 独立复现，判定"维持并强化"

Wave 1 说 F-01 是本轮唯一确认的 ARCHITECTURE_GAP。复诊要求**不复述**，所以我重新走了一遍链路，
结论：**Wave 2 没有削弱它，而且给出了比 Wave 1 更精确的 Current**。

**Red signal 是什么？** Q101（简历"复杂请求进入 ReAct 路径" vs A8"complex fail closed"到底哪个是现状）、
Q102（complex 臂不可达时，测试代价为何被讲成 fixture 问题）、Q105（"报告"这个中文词）、
Q111（4 月那段在 live path 上还剩多少）、Q159（影响所有请求分流的规则为何无 ADR）。

**canonical source 怎么说（本轮独立实测）？**
- 判据（实测）：`platform/services/workspace/simple_agent.py:2150` `_plan_kind_for` 是
  `@staticmethod`，对 `original_query.lower()` 做**子串**匹配，命中
  `("compare","across","conflict","multi-hop","multihop","analyze","synthesize","报告")`
  任一即 `return "complex"`，否则 `"simple"`。无模型参与。
- 调用点（实测）：`simple_agent.py:2032`（`_run_request`）与 `:2080`（`retry_run`）
  `plan_kind = "tool" if resolved_tool_id else self._plan_kind_for(original_query)`，
  随后 `plan_kind=plan_kind` 装进 `WorkspaceRunRequest`，再 `self._runtime.start_with_replay(request)`。
- 装配（实测）：`api/services/workspace.py:162` 构造 `WorkSpaceSimpleAgent`；它用
  `composition.dynamic_dag_planner` 建 `WorkspaceAgentRuntime`（`simple_agent.py:1277`）；
  产品组合在 `main.py:113` 明确 `dynamic_dag_planner=None`，经
  `configure_workspace_product_composition(...)`（`main.py:114`）发布。
- 准入拦截（实测）：`platform/services/workspace/single_controller_runtime.py`
  `:737-739` `complex_unbound = bool(request.plan_kind == "complex" and self._dynamic_dag_planner is None)`；
  `:817-818` 命中后 `admission_reason = DYNAMIC_PLAN_RUNTIME_NOT_BOUND`（常量 `:103`）；
  `:825` `return self._blocked_request(...)`。该处注释明写这是 PHASE22 修复，且
  "an unbound composition must never fake a fixed three-step DAG or fall back to a direct answer"。
- `build_workspace_plan_steps`（`:465`）在 `:498-499` 对 complex + planner=None **`return None`**，
  **不抛**——Wave 1 §14.1 对 A8/A56 的纠错成立，A101 已自认并收回。

**Wave 2 新增的、Wave 1 没有的精确事实（强化点）：**
- `_blocked_request`（`:870-911`）**不是异常、也不是拒收**，而是返回一个**正常的
  `RuntimeStartRequest`**，其区别是：`plan_steps=()`、`capability_ids=()`、`allowed_tools=()`、
  `approval_required_tools=()`、`strategy_mode=None`、且
  `security_summary={"decision":"block","recommended_action":"refuse","reason": reason}`、
  `budget_verdict={"allowed": False, "reason": reason}`。
  也就是说：**被拦下的 complex 请求会形成一条"空 plan 的 run"**。B1 #3 说
  "Native Runtime entrant 一定有 Plan"，而这条 run **正是一个无 Plan 的 entrant**——
  冲突比 Wave 1 描述的"被挡在门外"更字面。
- 归属（实测 + A105/A159）：token 表作者 Blue **自认 Unknown**（A105"拿不出作者是我独立证据"）；
  `docs/decisions/` 无对应 ADR（A159"我不知道为什么没有 ADR"）。
  ⇒ Wave 1 的 Owner 缺口被 Wave 2 **正面确认**，不是被抹掉。

**这是回答问题还是系统问题？** 系统问题，且 Wave 2 让它更清楚。三条被接受的来源仍互斥：
```text
简历第 1 条：复杂请求 → ReAct 路径
B1 #3 / B4 Profile B：复杂请求 → Dynamic DAG（immutable PlanVersion）
今天代码：复杂请求 → 空 plan 的 RuntimeStartRequest（decision=block，无回落、无 ReAct）
```
且判据仍无 owner（A159）、无 decision record（A105/A159 双 Unknown）。

**Current / Target / Evidence / Unknown**
- CURRENT：`tool` / `simple` / `complex` 三值准入；complex 在 shipped composition 下产出
  **空 plan + decision=block** 的 run；`报告` 会把一次普通请求判成 complex。全部有 file:line。
- TARGET：B1 #3 + B4 Profile B —— complex 必须落到 immutable PlanVersion 的 Dynamic DAG。
- EVIDENCE：A102 明说"complex + planner=None ⇒ block"这条**可写确定性断言、不需要模型**，
  但**今天没有写**（ReAct 侧与准入侧都空）⇒ 无 evidence。
- UNKNOWN：空 plan 的 run 在**下游**如何被 runtime 呈现（是终态失败、还是空跑、还是被上层包装）；
  UI 层具体文案（A105 自认未核）。

**最简单方案是什么？** 与 Wave 1 同：给这条准入边界一个 owner + 一份最小 decision record
（A159 自己说"最想改的一件事"就是补 ADR），并把"planner 未绑定时 complex 的对外语义"
正式写成**受控拒绝**。不需要新对象。

**当前设计在哪里失败？** 失败点从"不可达的三值准入"精确化为：**一条改变执行语义与授权路径的
准入决定，既没有 Authority，也没有 Contract 说明"被拦时这条 run 算什么"**——B1 #3 要求
entrant 必有 Plan，而实现产出的恰是"有 entrant 无 Plan"。这是 Owner + Contract 的站不住。

**是否真的需要 Architecture Revision？** 需要，且只需最小一次（同 Wave 1）：写 owner +
收口"complex 未绑定 = 受控拒绝"。**不需要**新增模块或状态机。

**有没有更简单替代？** 有，且 Wave 2 让它更可取：A111 自己说三件 delta 里只有"约一件半"在跑；
若把 `_plan_kind_for` 的 complex 判据直接删掉（全部走 `simple` 单步 + `tool` 直连），
就消灭了"空 plan run"这个形态，与 B12 的 Delete 判据一致。代价是放弃"复杂任务"产品叙事。

**增加什么成本？** 最小方案 ≈ 一份 decision record + 一处措辞；替代方案 = 产品侧同意。

**退出条件是什么？** (a) 产品组合绑定 Dynamic DAG planner 且 B4 Profile B 端到端可跑；或
(b) 接受一次 Revision，把 complex 对外语义定义为受控拒绝并记录。二者未发生前，F-01 关闭不了。

**下一轮如何复测？**
① `grep -rn "dynamic_dag_planner" src/backend/zuno/main.py` 是否仍为 `None`；
② 补并运行"`complex` + planner=None ⇒ `_blocked_request` 产出 `plan_steps=()`"这条确定性断言；
③ 检查 `docs/decisions/` 是否出现准入 owner 记录；④ 检查空 plan run 的下游呈现是否被定义。

**差分判定：F-01 = 维持，且被 Wave 2 强化。** Wave 2 的贡献是把它从"被挡在门外"
精确到"产出一条无 Plan 的 run"，并把 Owner/ADR 缺口从推断变成候选人自认的 Unknown。

---

## §2 被撤回 / 降级 / 升级的条目（复诊的实质）

### §2.1 F-06 — 从"条件性 ARCHITECTURE_GAP"**降级**为 EVIDENCE / GOVERNANCE

这是本波最重要的一次自我推翻。Wave 1 说 F-06 是本轮**唯一可能**需要第二次 Architecture
Revision 的地方，其升级条件写得很明确："可消融性检查确认强耦合"。Wave 2 把耦合**证实**了——
但正因为被证实，**升级闭锁反而解除了**。

**Wave 2 证实的耦合（本轮独立实测）：**
- `alias → seed` 是一条**链**，不是两个机制：`graphrag/retriever.py:343/363/366/369`
  把 `resolve_alias(...)["resolved_to"]` 直接喂进 `add_seed(...)`，来源标签就是 `"alias"`；
  而 `resolve_alias` 的 `allow_fuzzy` 分支（`entity_alias.py:56-59`）复用的是**已经比过**的
  `normalized_map`，实际是 no-op。⇒ A172/A173/A168 成立：别名归一化是 seed expansion 的
  **输入预处理**，"删 alias 留 seed" 会把失败形态又带回来。
- `_graph_signal` 仍四计数器求和（`retrieval/fusion.py:157-163`），`_candidate_group`（`:166-187`）
  用它比 `GRAPH_PROMOTION_THRESHOLD`（`:9`，=6，另 +3）。⇒ Wave 1 §6 的共享状态判断成立。

**为什么这不构成 ARCHITECTURE_GAP（本次改判的核心理由）：**
Wave 1 的升级逻辑是"gate 本身不可执行 ⇒ 越过门槛"。但 §13 的触发条件是
"**复杂度缺乏**可删除 / measurement gate"——这里**gate 是存在的、冻结的、有 owner（03+09）的**，
只是它的**消融单位**选错了（把链式耦合当独立机制）。同时，Wave 2 给出了**不需要架构变更**的
正解，且 Wave 1 §6 自己也提过：**整层 on/off 消融**（A169/A176 同向）。把"协议该把 9 条合并成
几组臂"这件事，判成 Architecture Revision，会与 §13 高门槛正面冲突。

**故判定：F-06 = 降级。** 残余是一条 **GOVERNANCE / EVIDENCE** 项（见 N-04）：冻结协议 §3 的
H 清单粒度与实现的可归因性不匹配，应把"逐条可关闭"改写为"按耦合链分组可关闭"，或直接采用
整层 on/off 两臂。**不需要**引入 `heuristic_mask` 之类的架构改造（Wave 1 §6 的备选，本波不再推荐）。

### §2.2 F-04 — CONTRACT 问题**改写**（salt 部分撤回，残余换了内容）

Wave 1 F-04 的两个抓手，Wave 2 各自变了：
- **"随机 salt 破坏幂等"这条风险撤回。** 实测 `capability/mcp/mcp_tool_executor_adapter.py`
  的 `idempotency_key(self, *, tool_name, salt="")`，唯一生产调用点
  `simple_agent.py:217` 传 `salt=str(getattr(binding,"name","") or resolved_tool_id)`——
  由动作身份确定。A106/A107 收回"随机 salt"叙事，成立。
- **残余是另一条**：A107 指出 key 模板含 `run_id` / `step_run_id`，于是**跨 run 重发不会命中
  既有 receipt**——幂等命名空间到底是"step run 内"还是"逻辑动作级"，没有契约。
- `create_calendar_event.py` 里 `.idempotency_key(uuid4().hex)` 的**角色仍未判**（本轮亦未判定）。

**判定：F-04 = 降级（small CONTRACT，内容换过一次）。** 仍是"需复测的契约问题"，
**不是**已确认缺陷。

### §2.3 F-09 → 升级为 N-01（孤儿组件是模式）

Wave 1 把 `ContextOrchestrator` 当**孤立**的 DOCS/ANSWER+CLEANUP 项（一个组件 + 一句过强简历）。
Wave 2 暴露出**同一个形态反复出现**，实测确认：
- `knowledge/ingestion/delete_restore.py:327 DeleteRestoreRuntime` /
  `:582 PersistentDeleteRestoreCoordinator`：状态机完整（`DeleteState` `:17-24`、
  `request_delete`→`request_cleanup`→`mark_physical_delete`→`verify_delete`，每步产 receipt），
  **生产无调用方**（grep 全仓只有 `tests/knowledge/test_ingestion_delete_restore.py`）⇒ A183 成立。
- `agent/runtime/phase08.py` 的官方 `PostgresSaver` 路径**未接线**，只在 `__init__` 被 re-export（A141）。
- `capability/tool_runtime/invocation_gateway.py:1607 escalate_due_reconciliations`：
  **仅测试调用**（`tests/capability/test_tool_effect_postgres_boundary.py` 三处）⇒ A147 成立。
- 同文件 `:1787 record_manual_effect_assessment`：**仅测试调用** ⇒ A148 成立。
- `agent/runtime/planning/recovery.py` 的 late-result 分支（A140）"没有非测试调用方"。

⇒ 这不是"一个孤儿组件"，是**一条实现纪律**：Target 设计先落成代码与测试，运行时接线在后。
它使若干被讲成 **Current** 的行为实际上是"**代码在、驱动不在**"。**判定：F-09 升级范围并入 N-01。**

### §2.4 其余 Wave 2 自撤回项（对 Wave 1 判断的影响：中性偏正向）

以下都是候选人在 Wave 2 主动收回的 Wave 1 表述错误。它们**不改**Wave 1 的架构分类，
但修正了 Wave 1 §14"Blue 自身薄弱点"清单的权重，并应被 Final 记为"回答质量提升"：
- **A8/A56 的 `single_controller_runtime.py` 路径与"抛"**：A101 自认并给出真实位置与动作（Wave 1 §14.1 命中）。
- **A28 `GeneralAgent.prepare_context()`**：A127/A181 收回——真路径是
  `agent/runtime/nodes/core.py:79 → memory/engine.py:645 build_context_pack`，
  `prepare_context` 只是 harness 节点名（`harness.py:269`）。**注意**：这**不**产生新 gap，
  它是 F-09 同一"命名即实现"毛病的第二个实例（见 N-02）。
- **A38 的 `ACTIVATED`**：A138 收回，给出两套**互不一致**的代码枚举
  （`task_contracts.py:38-42` 用 `REJECTED`；`runtime_batch.py:104` 用 `VALIDATING`）。
  这是回答错误 + 一处**真实实现内命名漂移**，但仍属 ANSWER_QUALITY / DOCS，非架构。
- **A17 "baseline-preserving 是全局不变量"**：A117/A118/A169 收回"全局"二字。实测
  `fusion.py:922 selected[weakest_index] = candidate`、`:943 floor_preserved = promoted_candidate is None`
  ——genealogy guardrail **故意**允许在晋升时放弃 baseline 下限。这是对 Wave 1 §5"Current"描述
  的一次**重要修正**（那段把"不劣于 baseline"讲得比实现更强）。
- **A97 "全仓没有 RRF"**：A199 收回——RRF **在仓里**（见 N-03）。
- **A116 "跑不了"**：A116 收回为"没做"（区分 6 月未执行 vs 后来的治理产物 blocked）。
- **A19 的模型混淆**：A112/A113/A114 排除——`a25c95a2` 使 audit(`7928df50`) 与 rerun(`3da5d742`) **同模型**。
- **A21 的"未执行→跑不了"**：A116 收回。⇒ Wave 1 §14 未涉及、但 Red 2 §4 高亮的这条口径移动已闭合。

---

## §3 维持的条目（一句话 + 新证据）

- **F-02**：维持 IMPLEMENTATION。A147/A148 进一步证明对账链**无驱动**（仅测试调用）——
  这加强了"人工兜底"的 Current 描述，但仍不改分类（Owner/Contract 齐）。
- **F-03**：维持并强化。A149 给出更精确的"今天停"=**工具层 BLOCK**（`capability/runtime.py:700-745`
  置 `gateway_effect_certainty="UNKNOWN_EFFECT"` + `SecurityDecision.BLOCK`），
  Run 级 `WAITING_RECONCILIATION` 在 src **不存在**（仅 `docs/modules/runtime/reference.md`）；
  A150 给出最坏态。仍为 IMPLEMENTATION（"没做到"≠"设计不成立"）。
- **F-05**：维持 EVIDENCE_GAP 并强化。A113 明确"能排除换模型、不能证明是 fusion 修复"；
  A114 修正范围；A187 给出"方向可归因、幅度不可分离"。Wave 1 §5 的"小样本区分不出机制与噪声"**原样成立**。
  本轮**新增**：N-03（仓内 RRF 未试）应挂到 F-05 的"更简单替代"里。
- **F-07**：维持并强化。A123/A124/A125 把"英文调优"精确为**域不匹配**（英文关系词渗入域词汇）
  且**目标域零验证**。Wave 1 §7 的限定版说法（平台另有中文合同抽取链）**未被 Wave 2 反驳**——
  A123 谈的是 fusion/alias 的词汇，与结构化抽取器不冲突，故 Wave 1 的"过强口径"判断仍成立。
- **F-08**：维持（安全 IMPLEMENTATION）。实测 `grep -rn "recall_eligibility\|RecallEligibility" src/`
  **仍 0 命中**；A134 承认缺口"未被记成待办"。Wave 1 §8 的擦边点（声明的不变量在 Current 无独立落点）
  不变。
- **F-10**：维持（小 SEMANTICS）。A130 确认 agent 轴塌成常量。
- **F-11**：维持 NOT A GAP。A133 补充"两条冲突候选各自独立走到 APPROVED"，与"memory 非权威"
  一致，无需仲裁。
- **F-12**：维持（小 OWNER）。A131："状态迁移靠调用方显式发起，无 reaper"。
  **注意**：A174/A75 的 Build-Buy delta 与 F-12 **正交**——两者不互相影响，本文件不强行连结。
- **F-13**：维持 NOT A GAP。A139（版本比对"设计意图在、live comparator 未证"）、
  A143（恢复顺序是文档顺序、无单一编排器）**增加了实现缺口**，但 Owner/Contract/Build-Buy/删除判据
  四件仍齐，故分类不变。
- **F-14**：维持 NOT A GAP。A162–A167 全 Unknown，且 A163 把"停在 Pilot"拆成"事实边界 + 个人措辞"，
  处理干净，无升级。
- **F-15**：维持 NOT A GAP。实测确认 `KnowledgeGeneration` / `ServingPointer` 在 `src/` **0 命中**；
  A179/A180 已分别承认"未纠正前提"与"原子切换未落地"。**并派生出 N-02。**

---

## §4 新增条目

### N-01 — 孤儿组件是一个模式（范围扩自 F-09）

见 §2.3。**分类：DOCS_GAP + ANSWER_QUALITY**。判定为**不上调**：这组"有实现无驱动"的组件，
与仓库自己的 Target/Current/Gap 三段式纪律**一致**（Target 设计先落代码、接线在后），
不是"两条来源对同一事实互斥"。但**必须**记入 Final 的 Claim 分级：凡引用这些组件作为
**Current 证据**的回答（A77/A80 的 generation、A48 的 `WAITING_RECONCILIATION`、
A79 的 delete lifecycle、A147/A148 的对账），其"Current"强度应降为"**代码存在、无驱动**"。
**下一轮复测**：对每个此类组件跑一次"是否有非测试调用方"的 grep，输出一张**接线状态表**。

### N-02 — Target 词 ↔ 代码符号没有对照表

实测：`KnowledgeGeneration` / `ServingPointer` 在 `src/` **0 命中**，但在 `docs/modules/knowledge/README.md:69`、
`docs/architecture/reference.md`、`docs/decisions/0006/0007/0008/0013` 等**大量 canonical 文档**里出现
（A181：同一概念在代码里叫 `KnowledgeVersionRecord` / `KnowledgeVersionState` / `document_version_id`）。
**分类：DOCS_GAP（新）**，非架构。
后果是一个**取证陷阱**：按 Target 词搜 src 得到"0 命中 → 未实现"的**假阴性**（A179/A180 正是这么判的），
按代码词搜才看到版本/就绪/引用机制**部分存在**。这是**可执行的确定性**修复：补一张
"Target 词 ↔ 代码符号 / 或 'src 无实现'"的对照表，并把候选人的引用规则改成"凡带行号的引用必须实跑"。
**不上调**理由：这是文档与命名问题，不是 Owner/Contract/State。

### N-03 — 仓内已有 RRF，但知识检索路径用的是自制融合

实测：`knowledge/agentic_graphrag.py:876 entry["rrf_score"] += 1.0/(60.0+rank)`，
strategy 名 `local_rrf_then_score_rerank`（`:1411`），sort key `:883`；
而**知识检索路径**用的是 `retrieval/fusion.py` 的 group/tier/baseline_rank 自制方案
（`_rank_key` `:951-977`；`fusion_score` 写入 metadata **但不进排序键**，A198 已实测）。
**分类：EVIDENCE_GAP（新），并触发 §13 的 "Build-Buy 因果" 边缘。**
判定 **不上调**：A199 自己说"不主张 RRF 在这条路上一定更好——那需要 A/B"，即**替代方案未被证明更优**，
按 §13 只到 EVIDENCE。但它把 Wave 1 F-05 的"更简单替代"从"普通 hybrid / vector"
**具体化为"仓内已有的 RRF（k=60）"**——成本更低、更该先试。**应并入 F-05 的替代清单。**
**下一轮复测**：确认知识检索路径是否**任何配置**下都不经过 RRF；若可配置，测一次 A/B。

### N-04 — 冻结协议的"消融单位"缺陷

见 §2.1。**分类：GOVERNANCE / EVIDENCE（新）**。`rb019-graphrag-ablation-protocol.md` 的
`status: FROZEN_PROTOCOL / measurement_status: BLOCKED_PENDING_DATA`、`owner: 03+09` 均实测成立；
缺陷在于 §3 的 H 清单粒度把**耦合链**（alias→seed）与**共享信号**（H1←H7/H9 经 `_graph_signal`）
当成独立机制。**不上调**（gate 存在且有序），但**需修订协议**：改成"按耦合链分组"或
"整层 on/off 两臂"。这是**不需要数据集就能先做**的一步（与 Wave 1 §6 的性价比判断一致）。

### N-05 — Zuno delta 塌缩后收敛到"准入"（与 F-01 合流）

A174/A75 把自研三分法修正为：**"注参"大部分是 commodity**（`call_args.update(mcp_config)`
这类若 Host 原生支持 per-user config 就属于 Host），残余 delta 收敛为
**"暴露 + 准入 + 一小块绑定语义"**（tool→server 映射 `simple_agent.py:197-200`、
确定性 salt `:217`、未注册 adapter 的 `MCPToolAdapterNotBound` `:206` 一带）。
**分类：Build-Buy 因果（新条目，但结论与 F-01 合流）。**
判定：**不上调为新 gap**，因为它不引入新的 Owner/Contract 问题；它的作用是**收紧 F-01**——
自研价值的最小内核（"准入"）恰好就是那条**无 owner、无 ADR、在 shipped composition 下 fail closed**
的边界。也就是说：Zuno 自研 delta 的三分之一，是一个没有 Authority 的决定。
**附带澄清**：A174/A75 与 **F-12（staleness owner）无因果关系**——两者只是都被归到"OWNER"类，
本文件不制造连结。**下一轮复测**：确认自研 delta 是否在任何**已接受来源**里被写成"值得保留"，
还是仅存在于 4 月历史（UF-032）。

---

## §5 Blue 自身在 Wave 2 暴露的薄弱点

只谈 Wave 2 新出现的，不重复 Wave 1 §14。

1. **"先答后纠前提"的形态**。A179（未纠正"简历里的 `KnowledgeGeneration`"这个假前提）、
   A178（未先识别"30 是魔法数"这个怀疑方向的机制不同）都是**顺着错误前提作答，再在第二层修正**。
   在 30 分钟口语面试里，第一句话答错前提 = 第一印象落地。**建议**：凡题目含专有名词，
   第一句先判"这个词在冻结简历 / `src/` 里是否存在"。

2. **引用错误的**分布**比 Wave 1 好转，但仍是同一类**。Wave 1 §14.1 指出 A8/A56 一处路径错；
   Wave 2 里 A101（自纠）、A127（自纠对象名）、A146（自纠遗漏 `:388`）、A149（自纠含糊）
   全部是**主动**交出，这是进步。但 A101 同时把 `simple_agent.py:2150` 与"准入链 `:787-827`"
   混列，而 `build_workspace_plan_steps` 的 `return None`（`:498-499`）与
   `_blocked_request`（`:870`）是**两个不同函数**——同一段论证仍把"哪个函数做的"讲糊。
   **建议维持 Wave 1 的规则**：带行号的引用一律实跑 `sed -n`。

3. **对"静态可读的耦合"与"测量可归因的耦合"区分不足**。A172/A173 正确发现 alias→seed 是链，
   但随即把结论推到"消融设计应该串成一个臂"——**链式耦合**（可逐环关，只是预算会重复）
   与**共享信号耦合**（关一环会改另一环的输入分布，`_graph_signal`）是两种不同强度的耦合，
   A172 把它们并成一类。这恰好也是 F-06 降级的关键区分点（§2.1）。**建议**：下轮把"关一环后
   另一环的输入分布是否变化"作为判据分开表述。

4. **A169 的"同生共死"叙事强于其证据**。A169 说"删融合和删图路由是一件事的两半"，
   这对**baseline-preserving 部分**成立；但 `fusion.py` 里 comparison/bridge guardrail
   （`:756/:815`）**换入的是 baseline 候选**（A169 自己也说"大多在保护链路"），
   genealogy guardrail（`:877/:922`）才是**驱逐**方。把三者统称"融合"再宣布与图层同命，
   是**用词过度概括**。**建议**：下轮把这三件拆名讨论（Wave 1 §5 也提过这点，A169 部分吸收了）。

5. **A106/A107 的收回不完整**。A106 说"风险不在 salt 而在 key 其他分量"，但**没有**把
   `create_calendar_event.py` 的 `uuid4` 幂等键角色判掉（Wave 1 F-04 的 R3 复测项之一已存在两轮）。
   这是"收回了一条、留下了一条没问"的形态。

---

## §6 下一轮必须复测什么（可执行清单）

按"是否依赖外部数据集"排序。**前四项在 `BLOCKED_PENDING_DATA` 期间即可执行。**

```text
R1 [不需数据，最高优先] N-01 接线状态表
   动作：对每个"可疑孤儿"组件跑一次"是否有非测试调用方"的 grep：
        ContextOrchestrator / DeleteRestoreRuntime / PersistentDeleteRestoreCoordinator /
        phase08 PostgresSaver / escalate_due_reconciliations / record_manual_effect_assessment /
        agent/runtime/planning/recovery.py 的 late-result 分支 / build_workspace_plan_steps 的 complex 臂。
   判据：输出一张 "组件 | 定义位置 | 非测试调用方(Y/N) | 该组件被谁当 Current 讲过" 的表。
   为什么先做：它同时决定 F-09 / N-01 / F-13 / F-03 的 Current 强度。

R2 [不需数据] F-01 的确定性断言 + 下游呈现
   动作：写并运行 "plan_kind=complex 且 dynamic_dag_planner=None ⇒ _blocked_request 且 plan_steps=()"
        （已知确定性、不需模型）；再追这一步产出的 RuntimeStartRequest 在 runtime 里如何被消费
        （是终态失败、空跑、还是被上层包装）。
   判据：断言通过 + 空 plan run 的下游语义被一句话定义 ⇒ F-01 的 Contract 缺口收口或保留。

R3 [不需数据] N-02 的 Target 词↔代码符号对照表
   动作：对 docs 里的 Target 名词（KnowledgeGeneration / ServingPointer / ReadinessDecision /
        WAITING_RECONCILIATION / PlanVersionStatus 等）逐个人肉/脚本比对 src 符号。
   判据：每个词有"代码符号"或"src 无实现"二选一；产出后作为候选人引用纪律。

R4 [不需数据] F-04 残余 + N-04 协议粒度
   动作：(a) 判定 capability/mcp/servers/lark_mcp/.../create_calendar_event.py 里
        .idempotency_key(uuid4().hex) 是 provider 幂等键还是普通 request id；
        (b) 读协议 §3，把 H1–H9 按 alias→seed 链与 _graph_signal 共享信号分组。
   判据：(a) 若为 provider 幂等键 → 记为 effect 幂等契约缺陷；(b) 输出"哪些 H 应合并成一个臂"。

R5 [需数据] 整层 on/off（F-05 / F-06 / N-03）
   动作：GraphRAG 整层 on/off 两臂；若可用，加一臂"图权重 0"；再考虑一臂"改用仓内 RRF(k=60)"。
   判据：协议 §2；"一条都不留"是合法终点；N-03 的 A/B 是新增的必选项。

R6 [需数据] 中文法律域的第一件事（F-07）
   动作：按 A168 的三步——先量 baseline 在中文卷宗上的 Recall@k；再查英文线索是否触发；
        再量 CitationProvenanceGuard 的拒绝率。
   判据：第一步过不了 ⇒ GraphRAG 修复对法院域"暂时不适用"（可三天内得到的结论）。

R7 [Gap 状态巡检] F-02 / F-03 / F-08 / F-13 / F-15 / N-05
   动作：逐条读 docs/evidence/README.md、effect-remote-query-reconciliation-status.md、
        modules/{runtime,knowledge,security}/README.md 的 Gap 段、project-fact-provenance.md
        的 PF-025（Native Runtime）/ PF-032（Tool Calling 切片）。
   判据：任一状态在 Gap/Current/Target 间移动 ⇒ 本轮复诊相应改判。
```

**给 Blue Architecture Reflection（Final）的三点提示：**

| # | 提示 | 依据 |
| --- | --- | --- |
| 1 | 本轮 ARCHITECTURE_GAP **只剩 1 条**（F-01），且 F-06 已由我自己降级为协议/证据问题——Final 不应再称"两个架构缺口" | §2.1、§1 |
| 2 | 最大的**非架构**风险已从"GraphRAG 没测量"转移为"**若干被讲成 Current 的组件无生产驱动**"（N-01/N-02）——它影响的是 Claim 分级，不是设计 | §2.3、§4 |
| 3 | Zuno 自研的最小内核（"准入"）恰是 F-01 那条无 owner 的边界；自研叙事的正当性与 F-01 的收口**是同一件事** | §4 N-05、§1 |

---

```text
复诊完毕。
ARCHITECTURE_GAP: 1 条确认（F-01 维持并强化，独立复现），0 条条件性（F-06 降级）。
新增非架构条目：N-01 孤儿组件模式 / N-02 Target 词漂移 / N-03 仓内 RRF 未试 / N-04 协议消融单位 / N-05 delta 塌缩。
本文件对 Red 封存；仅 Blue Architecture Reflection 可读。
```
