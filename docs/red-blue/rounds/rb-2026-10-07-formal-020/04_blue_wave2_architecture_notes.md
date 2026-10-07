# Blue Wave 2 — Architecture Notes（SEALED FROM RED）

```text
round: rb-2026-10-07-formal-020
sealed: true
readable_by: Blue Architecture Reflection only
base_sha: 7d3081f2ccaa20c7eeb0bfff75206d08584a6e51
supersedes: none（与 03_blue_architecture_notes.md 并存；本文件只记录变化）
```

判读口径与第一轮相同：`gap_type = ANSWER_GAP` 表示系统成立、只是表达/归属需要澄清，`proposed_change` 一律写 `none`。
本文件所有 `source_check` 均为本轮**实际打开并读到**的 `file:line`（不制造数字，不转抄）。
本轮的主要工作是「按 Red 点名的**审计口径**去把代码真打开」——Red Part A 怀疑的部分代码「写了没接线」，我逐处查了调用方，结论见下。

---

## 一、第一轮信号的复核结果

| 信号 | 第一轮判断 | 复核结论 | 依据 |
| --- | --- | --- | --- |
| S01 Ready 第二所有者 | SYSTEM_GAP / P0 | **维持，并扩围**（不止一个常量，是读路径的 default-open 模式） | `api/services/knowledge.py:53-55,73-74`；`api/dto/knowledge.py:70-72,109-110`；`retrieval/planner.py:91`；`retrieval/orchestrator.py:861`；`rag/handler.py:486`；`product/runtime_engine.py:360,459,1613` |
| S02 无法证明「全案里没有」 | SYSTEM_GAP / P0 | **维持**（撤回的只是引用路径，不是判断） | 引用修正见下方「引用勘误」；`knowledge/agentic/evidence_ledger.py`、`knowledge/agentic/corrective.py:21,33,46,55` 复核无误 |
| S03 Memory scope 缺案件维度 | SYSTEM_GAP / P0 | **维持**（引用路径修正） | `memory/store.py:217,252-274,312-338`（`MemoryRuntimeDao` / `_scope_select` / 4 列 scope）；`agent/runtime/nodes/core.py:485-491` |
| S04 授权层不完整 | SYSTEM_GAP / P0 | **维持** | `api/services/security_admin_actions.py:26-27`（tenant/workspace 字面 `"system"`）；`api/services/mcp_user_config.py:121-125`（delete 仅凭 config_id） |
| S05 运行时 vs ADR-0005 分叉 | SYSTEM_GAP / P1 | **维持** | `agent/runtime/phase08.py:342,835` + `agent/runtime/__init__.py:22,40`（**仅 re-export，无功能调用方**）；`tests/repo/test_agent_system.py:36`（断言 `phase08_cutover.py` 必须不存在） |
| S06 计划版本/晚到围栏不可达 | SYSTEM_GAP / P1 | **维持** | `agent/runtime/sqlite_store.py:318`（`append_plan_version` 全仓无调用方）；`planning/branch_result.py:91,96-105` + `planning/dynamic_worker.py:63`（`DynamicStepWorker` 自身无外部调用方）；`planning/recovery.py:12`（`RESEND_OUTBOX` 无执行点）；`ParallelRecoveryPlanner`/`Phase21CrashRecoveryMatrix`/`ReplanBarrierExecutor`/`JoinControlDecisionEngine` 全仓零外部引用 |
| S07 未确认副作用不自动升级 | SYSTEM_GAP / P1 | **维持，并强化** | `invocation_gateway.py:1607`（`escalate_due_reconciliations`）与 `:1613`（`timeout_due_async_jobs`）**两个维护入口都只有测试调用方**；`main.py` 与 `platform/queue/` 内**零** `BackgroundScheduler`/`add_job`/`cron`/`periodic` 命中 → 不存在任何调度驱动 |
| S08 引用可用性链路未完成 | SYSTEM_GAP / P1 | **维持**（引用路径修正） | `knowledge/ingestion/router.py:15`（`DEFAULT_CITATION_CHUNK_CHAR_LIMIT = 240`）、`:579,583`（`_split_long_unit` 硬切） |
| S09 两套融合实现 + 硬编码阈值 | SYSTEM_GAP / P1 | **维持，但修正一处措辞** | 产品侧 `retrieval/fusion.py:8,1065` 经 `retrieval/orchestrator.py:80` 被 `rag/handler.py:529` 与 `graphrag/query_service.py:141` 消费；agentic 侧 `agentic_graphrag.py:876`（k=60）经 `knowledge/agentic/runtime.py:393` 被 `product/runtime_engine.py:3163` 消费 → **两条都在活路径上**（见「Red 抓错」#2） |
| S10 Memory 撤销无生产写入方 | SYSTEM_GAP / P1 | **维持**（引用路径修正） | `memory/engine.py:1054-1064`（读取侧排除 stale/conflict/revoked）；`memory/runtime_batch.py:34`（`VersionStatus.REVOKED` 定义处）→ 无生产写入方 |
| S11 出站工具关 TLS | SYSTEM_GAP / P1 | **维持** | `capability/tools/delivery/action.py:41`（`APPCODE` 头）、`:47-49`（`check_hostname=False` + `CERT_NONE`） |
| S12 文档与 main 脱钩 | DOC_GAP / P1 | **维持** | 同第一轮；`main.py` 已绑定 composition 而 `modules/security/README.md` Gap 段未更新 |
| S13 自宣 SUPERSEDED 却缺收口证据 | DOC_GAP / P1 | **撤回核心指控**（见下） | `effect-security-slice-c-review.md:3-4` 存在 `superseded_current_evidence: main@9b7891c6… / run 35053215987`；`current-test-baseline.md:162,271` 有 AUTH-A/B 收口 commit + run `35056938670` |
| S14 per-user MCP 并发隔离成立 | NO_GAP / P2 | **维持** | `workspace/simple_agent.py:188-208,1319` |
| S15 执行前授权新鲜度已存在 | NO_GAP / P2 | **维持** | `invocation_gateway.py:388,462`（两次 `_reauthorize_execute_epoch`）、`:1499`（审计持久性复核） |
| S16 副作用前强制审计 + 默认 RECONCILE | NO_GAP / P2 | **维持** | `invocation_gateway.py:430`（在 `invoke_readonly` 内、早于派发）、`:1426` |
| S17 T06 个人归属边界 | ANSWER_GAP / P2 | **维持** | 同第一轮 |
| S18 T07 Pilot/法院定性边界 | ANSWER_GAP / P2 | **维持** | 同第一轮；本轮复核 `src/backend/zuno/` 全域 `court|法院|judicial` **零命中**（`grep` 无输出），与 S18 一致 |

**复核小结：维持 16 / 扩围维持 1（S01）/ 强化维持 1（S07）/ 撤回核心指控 1（S13）。未整条撤回任何信号。**

### S13 的撤回说明（诚实修正）

第一轮我把 S13 立成「自宣 SUPERSEDED 却未附收口 run SHA/证据，不满足『历史负面证据与收口证据成对保留』规则」。
本轮打开确认：该文档**头部第 4 行就有** `superseded_current_evidence: main@9b7891c63f007c8a0868d7dd262ceec5869bee4e / run 35053215987`，
且同级 `docs/evidence/current-test-baseline.md:162`（AUTH-A `18e4973365461ec939b95063c74f4a0457507e75`）、`:271`（AUTH-B
`2f709ec9344b94bdc87289793d22bcac3ba2a10b`）与 `docs/evidence/README.md:60-62` 都保留了逐条收口指针。**收口证据是存在的，我第一轮的判断错了。**
残留的真实（且窄得多的）部分只有一条：`slice_c` 结论块里的 `reconciliation_convergence: NOT_IMPLEMENTATION_PROVEN` 与
`cancel_in_flight_orchestration: NOT_IMPLEMENTATION_PROVEN` 仍是**开放的**——这不是「文档缺陷」，而是一条**仍未闭合的实现缺口**（它的驱动侧与 S07 是同一个洞）。
因此 S13 从 `DOC_GAP/P1` 降级为「无独立信号，其唯一有效残余并入 S07」。

### 引用勘误（第一轮有 3 处 `file:line` 路径是错的，判断本身不错）

| 第一轮写的 | 实际存在的 | 影响 |
| --- | --- | --- |
| `src/backend/zuno/knowledge/agentic/grounded_answer.py:87-88` | `src/backend/zuno/agent/runtime/synthesis/grounded_answer.py:87-88` | S02 判据不变，路径错 |
| `src/backend/zuno/platform/services/memory/store.py`、`.../memory/runtime_batch.py` | `src/backend/zuno/memory/store.py`、`src/backend/zuno/memory/runtime_batch.py` | S03/S10 判据不变，路径错 |
| `src/backend/zuno/platform/services/retrieval/router.py:15-16,566-600` | `src/backend/zuno/knowledge/ingestion/router.py:15,579,583` | S08 判据不变，路径错 |

（这三处是**我的**笔记缺陷，不是系统缺陷；列出以免下一轮继续引错。）

---

## 二、Red Wave 2 新暴露的系统断点

本轮 Red 最有效的攻击是 Part A 第 5 节那句「大量写了但没接线」，以及 T08/T09 反复用同一把尺子量不同层。
我按它点名的坐标逐个开箱，得到 4 条新信号（其中 N03 是 S07 的同一根线，独立列出因为它是**新查实的事实**）。

### N01 — 五张 memory 写入表中，有四张只写不读

```text
signal: post-turn 提交会往 memory_versions / memory_candidates_v2 / memory_snapshots /
  context_pack_versions / memory_use_traces 五张表写数据，但全仓（src/ + tests/）里
  context_pack_versions、memory_use_traces、memory_candidates_v2、memory_snapshots
  这**四张表的表名字面量各只出现一次**，且那一次都是 INSERT；不存在任何 `SELECT ... FROM`
  引用它们（连测试都没有）。只有 memory_versions 有读侧。也就是说：上下文打包版本、
  memory 使用溯源、候选、快照这四类「为了可审计而写」的记录，今天没有消费者。
  这与 Red Part A #5 观察到的现象同源（「活路径远窄于架构文档」），但这次不是控制面，
  而是**审计面**——A23 声称的「一次提交写五张表」在写入侧成立、在读取侧只成立一张。
source_check:
  - src/backend/zuno/platform/database/memory/domain.py:110（INSERT INTO memory_versions）、
    :171（INSERT INTO memory_candidates_v2）、:313,333（FROM memory_versions，唯一的读）、
    :326（INSERT INTO memory_snapshots）、:348（UPDATE memory_versions）、
    :383（INSERT INTO context_pack_versions）、:486（INSERT INTO memory_use_traces）
  - 全仓 `grep -rn "FROM context_pack_versions|FROM memory_use_traces|FROM memory_candidates_v2|FROM memory_snapshots" src/ tests/` → 零命中
  - 各表字面量计数：memory_use_traces=1、context_pack_versions=1、memory_candidates_v2=1、
    memory_snapshots=1、memory_versions=4（均在 domain.py 内）
  - src/backend/zuno/memory/store.py:312-338（读侧只覆盖 raw_events / task_summaries / memory_candidates，
    均 order_by created_at）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 二选一并显式记录：要么给这四张表定义真实的读取方（最小形态是让 09 的
  eval / regression 从 memory_use_traces + context_pack_versions 派生「哪些 memory 真被注入过」，
  以及让取证/复盘能重放某次 context pack），要么承认它们是「为将来取证预留」并写进 Target 的
  Defer 清单，停止把它们当作已建立的审计能力描述。
simpler_alternative: 先只保留 memory_versions 一张，把其余四张的写入收敛为一个可关闭的
  trace 开关（默认关）。这不需要新读取方，也不会丢掉今天真正被读的那部分。
cost_and_exit: 定义读取方要动 09 的派生链路；收敛写入是局部改动且可逆（恢复写入即可回退）。
两条路径收益均为 Unknown（无评测数据）。退出方式是恢复原写入。
priority: P1
触发题号: Q128（Red 用我在 A33/A35 的审计口径反问这五张表的 reader）；旁证 Q185、Q189
```

### N02 — 可用性/健康度是 default-open：缺失即「ready」

```text
signal: 索引与图的可用性判定在**读路径上默认放行**。只要 health/index_health 里没有该键，
  代码就取字面量 "ready"；再叠上两处硬编码的 graph_available=True，结果是「探活缺失」
  被解释成「健康」。这比第一轮 S01 记的单个常量更宽：S01 是「写入侧多了一个所有者」，
  N02 是「读取侧缺省即绿」。两者合起来才能回答 Red 的 Q125——「图索引坏了但开关还停在
  true 会不会一直带病跑」：会，因为开关的输入之一在缺失时就是绿的。
source_check:
  - src/backend/zuno/platform/services/retrieval/planner.py:91（graph_health = ... or "ready"）、
    :97（graph_available = knowledge_capability == "rag_graph" and graph_health not in {unavailable,failed,stale}）
  - src/backend/zuno/platform/services/retrieval/orchestrator.py:859-861（.get("graph") or "ready"）
  - src/backend/zuno/platform/services/rag/handler.py:486（index_settings.get("health_status") or "ready"）
  - src/backend/zuno/agent/planning.py:43（graph_available: bool = True，默认值）
  - src/backend/zuno/api/services/product/runtime_engine.py:2862（graph_available=True 硬编码）、
    :360,459,1613（status="ready" 硬编码）
  - src/backend/zuno/api/dto/knowledge.py:70-72,109-110（Field(default="ready")）
  - src/backend/zuno/api/services/knowledge.py:53-55,73-74（DEFAULT_KNOWLEDGE_CONFIG 字面 "ready"）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 把「未探活」与「已探活且健康」在类型上分开（三态：unknown / ready / not_ready），
  读侧遇到 unknown 时按调用场景失败关闭（检索降级为无图、或显式告知不可用），不允许 `or "ready"`；
  同时把 graph_available 的两个硬编码 True 收敛为「由上游探活结果单一写入」。
simpler_alternative: 不引入三态，直接把所有 `or "ready"` 改成 `or "unknown"`，并让消费点把
  unknown 视为不可用。这是纯字符串级改动，且能让 Q125 那个场景立即变成「带病跑会先降级」。
cost_and_exit: 集中在 5 处取默认值 + 2 处硬编码，回归面在 knowledge/readiness 与 retrieval planner 测试。
  退出方式是改回 "ready"。收益 Unknown。
priority: P0（与 S01 合并计为同一族：Ready 的权威散落在写入常量、DTO 缺省、读路径兜底三个位置）
触发题号: Q125、Q186、Q81/Q82 的续问
```

### N03 — 回收侧的两个维护入口都没有驱动（S07 的同一根线，本轮查实「两个都没有」）

```text
signal: 第一轮只记了 escalate_due_reconciliations 没有调用方。本轮把它和它的兄弟
  timeout_due_async_jobs 一起查：**两个维护入口在 src/ 里都只有定义、没有调用方**，
  调用方全部在 tests/。进一步查调度面：main.py 与 platform/queue/ 内不存在任何
  BackgroundScheduler / add_job / cron / periodic 命中。结论是「对账升级」和「异步作业超时」
  两条周期性收敛都没有执行者——它们不是「未接线的函数」，而是「这一整类常驻任务在设计里缺席」。
source_check:
  - src/backend/zuno/capability/tool_runtime/invocation_gateway.py:1607（escalate_due_reconciliations 定义）、
    :1613（timeout_due_async_jobs 定义）
  - src/backend/zuno/platform/database/tool_runtime/domain.py:1188（下探实现）
  - 调用方仅有 tests/capability/test_tool_effect_postgres_boundary.py:211,308,389
  - 全仓 grep `timeout_due_async_jobs`（排除定义处）→ 零非测试调用方
  - 全仓 grep `APScheduler|BackgroundScheduler|add_job|cron|periodic`（main.py、platform/queue/）→ 零命中
  - docs/governance/effect-remote-query-reconciliation-status.md（DEFERRED_BY_PROVIDER_CAPABILITY
    只覆盖「远程查询能力」缺失，不覆盖「本地定时升级没有驱动」——两者应分开记录）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 见 S07（写时升级，或最小常驻扫描）。补一条：把「本地可完成的升级/超时」
  与「依赖 Provider 能力的远端查询」拆成两条独立状态记录，前者不该被后者一起 Defer。
simpler_alternative: 写 UNKNOWN / 写 async job 时同步落一条待处置记录（写时升级），
  无需常驻任务，语义等价。
cost_and_exit: 同 S07。收益 Unknown。
priority: P1
触发题号: Q108、Q110、Q152、Q153、Q197、Q181
```

### N04 — GraphRAG 的「退出条件」权威挂在一份面试轮次产物上

```text
signal: A18/A20 论证 GraphRAG 该怎么留/怎么删，依据是 rb019-graphrag-ablation-protocol.md。
  打开该文件确认它的 `source` 字段就是 `red-blue rb-2026-09-15-formal-019 / IMP-019-05`——
  **它的出身是一轮 Red/Blue round，不是产品工程**。但它的 `owner` 写的是
  `03 Knowledge & Evidence + 09 Observability & Evaluation`，且冻结在 main `5844fe59`。
  即：它是一份「由评测轮次提出、被治理层收编」的协议。这不是造假（文件自己声明了来源，
  状态 BLOCKED_PENDING_DATA 也如实写着），但它意味着：一条关于「某层该不该删」的正式判据，
  其**问题定义**来自面试流程而非需求/事故。Red 的 Q123 抓对了这半，不是「抓错」。
source_check:
  - docs/governance/rb019-graphrag-ablation-protocol.md:5（measurement_status: BLOCKED_PENDING_DATA）、
    :8-9（owner + source: red-blue rb-2026-09-15-formal-019 / IMP-019-05）、
    :12（自称 current-eval-baseline 的配套协议）、:92-94
  - docs/evidence/current-eval-baseline.md:3（状态 MEASUREMENT_BLOCKED）
  - docs/governance/project-fact-provenance.md:63（PF-031 明确禁止制造精确单机制收益百分比）
fact_layer: Current（协议是 Current 的治理产物，衡量的对象是 Current 代码）
gap_type: DOC_GAP
proposed_change: 在协议头部把 source 与 owner 的关系写清：**问题来自评测轮次，判据由 03/09 拥有**；
  并补一句「在数据到位前，保留/删除的决定权归 architect，不归本协议」。这样既保留可追溯性，
  又不让「面试问题」成为架构决策的唯一依据。
simpler_alternative: 只需在 source 行旁加一行 `authority: 03/09 module owners（非评测流程）`。
cost_and_exit: 纯文档，一行。收益 Unknown。
priority: P2
触发题号: Q123、Q156、Q183、Q184
```

---

## 三、Red 抓错的地方

Red 是盲的，只能按候选人的话判断；以下 5 条我**实际打开了代码**，结论是「系统没问题，是 Red 的怀疑方向或候选人的转述错了」。

### 1. 「写了没接线」是否也覆盖 `invocation_gateway`（Q112、Q150）→ Red 的怀疑在这一层不成立

Red 问：为什么在 `planning/`、`recovery/` 反复做「有没有 caller」的审计，却对
`invocation_gateway.py` / `runtime_batch.py` / `effect_policy.py` 一次都不做，是不是审计口径不均匀。
开箱结论：**这一层是真接线的，审计口径本身没有偏**，五处逐个查实——

- `ToolInvocationGateway` 在 `src/backend/zuno/capability/runtime.py:861` 被构造并
  `gateway.invoke_readonly(...)` 调用，而 `build_default_tool_control_plane_runtime` 被
  `src/backend/zuno/main.py:55` 与 `src/backend/zuno/agent/runtime/factory.py:120` 消费 → 活路径。
- `analyze` 所问的 `assert_audit_durable_for_effect` **在活路径上**：定义在
  `platform/database/foundation.py:1747`，调用点在 `invocation_gateway.py:1499`，
  该调用点所属的 `_persist_mandatory_audit_before_effect` 在 `invocation_gateway.py:430`
  被 `invoke_readonly` 调用（同函数内 `:388`、`:462` 还有两次 `_reauthorize_execute_epoch`）。
- `effect_policy.classify_tool_effect` 被 `capability/runtime.py:919` 调用 → 活路径。
- `capability/tool_runtime/runtime_batch.py` 是**枚举/契约定义文件**（`DispatchCertainty` 等），
  随包 `__init__` 导出；它没有「执行逻辑」可接线，所以「无 caller」对它不适用——Red 把
  「契约定义文件」和「控制面实现」当成了同类。
- 唯一确属「没接线」的是 `agent/runtime_batch.py` 的 `validate_agent_runtime_batch`，它被
  `tools/scripts/verify_agent_runtime_batch.py:11` 与测试消费 → 它是**校验工具**，不是运行时路径；
  「工具没有产品 caller」是它的本来用途，不是缺口。

因此 Q112 的正确回答是：「审计口径没有不均匀——我在 planning/recovery 报『无 caller』，
是因为那两处**真的**无 caller；到 gateway 这一层同样去查，查出来是**有** caller，所以不报。」
真实存在的不均匀只有一处，且不是 Red 猜的那处：`escalate_due_reconciliations` 与
`timeout_due_async_jobs` 两个**维护入口**确实无 caller（见 N03 / S07）。

### 2. 「两套融合里哪一套是死代码」（Q191）→ 两套都在活路径上，不存在死代码

`RetrievalFusion`（字典序 tuple）经 `platform/services/retrieval/orchestrator.py:80` 被
`platform/services/rag/handler.py:529` 与 `platform/services/graphrag/query_service.py:141` 消费；
agentic 侧 RRF（`agentic_graphrag.py:876`，`+ 1.0/(60.0+rank)`）经
`knowledge/agentic/runtime.py:393`（`fusion_score=float(item.rrf_score)`）被
`api/services/product/runtime_engine.py:3163` 消费。**两条链路各自有产品入口**，
不是「一条活一条死」。「两套并存、口径由谁维护」这个**问题**是真的（我第一轮 S09 也记了），
但 Red 把它表述成「哪一套是死代码」就**错了**——它是一条双 profile 双实现，不是一个能靠删死代码收敛的东西。

### 3. 「abstain 路径接线了吗」（Q190）→ 接了

`CorrectiveAction.ABSTAIN` 在 `knowledge/agentic/corrective.py:21,33,46,55` 产出，
在 `knowledge/agentic/runtime.py:349` 与 `:595` 被真正分叉处理（`final_action == CorrectiveAction.ABSTAIN`
→ `KnowledgeControlProposalType.ABSTAIN`），而 `agentic/runtime.py` 是活路径（见上一段）。
弃答**不是**「只定义了常量没人用」。真正的缺口是 S02 那一条（**不存在「已判定不存在」这一层**），
不是「abstain 没接线」——Red 把「语义缺一层」误认成了「函数没接线」。

### 4. 「负向历史 #201/#203/#205/#207 是不是像 rb019 那样的评测复盘条目」（Q156）→ 不是，是真实诊断 PR

这四条在 `docs/evidence/current-test-baseline.md` 里是**带 PR 号 + run 号 + 收口 commit** 的故障注入记录：
`:162`（#201 / run `34559517466`，收口 AUTH-A `18e49733…`）、`:183`（#203 / run `34560042535`，
test seam 把 `security_effective_epochs` 改成 revoked）、`:244`（#205 / run `34560692093`，
收口 AUTH-B `2f709ec9…`）、`:213`（#207 / run `34566365522`）。`docs/evidence/README.md:60-62` 亦逐条列出。
它们是**真实的、未合并的 test-only 诊断分支**，不是「评测复盘里被命名的条目」。
Red 的怀疑方向错了。（顺带：这些是**真实证据**这一点，对候选人的演进叙事是**利好**，不是利空。）

### 5. 「A11 的 0.90 与 A60 的 1.00 是系统产不出自洽指标口径」（Part A §4 / Q113）→ 系统口径是自洽的，是候选人转述掉了前提

Red 认定这是「系统本身就产不出自洽的指标口径」的证据。开箱 `docs/governance/project-fact-provenance.md`：`:92` 记 baseline
`Recall@5=1.00 / MRR@10=0.90`、local `Recall@5=0.80 / MRR@10=0.80`；`:96` 记同日 rerun local
恢复到 `Recall@5=1.00 / MRR@10=1.00`，并**额外写明**：

> 「尤其 baseline 的 `MRR@10` 在 rerun 中也从 `0.90` 变为 `1.00`，因此不应制造精确的单机制收益百分比。」

也就是说，canonical 记录**自己**处理了「0.90→1.00」——baseline 在同一 5 样本上的 MRR@10 本身就从
0.90 漂到了 1.00，这是小样本抖动，不是「修复超出了 baseline」。系统给出的口径是**自洽**的，并且明确
禁止据此声称「GraphRAG 更好」。A60 在转述时把这条前提（「baseline 自己也漂了」）丢了，才显得像
「保位改动反超 baseline」。**结论：这是 `ANSWER_GAP`（A60 漏了 PF-031 的边界句），不是 `SYSTEM_GAP`。**
Red 的两答矛盾抓得对，但它对这个矛盾**性质的定性**错了（它把「转述丢前提」升级成了「系统口径不可自洽」）。

---

## 四、需要 Agent 侧（候选人表达 / 简历 / 文档）而非架构侧解决的问题

以下问题**不要去改代码**——它们改的是候选人的措辞、归属与材料，不是系统。

1. **Q113 / Q161 / Q168 —— A60 对 PF-031 的转述丢了边界句。** PF-031 原文（`:96`）写明「baseline 的
   MRR@10 在 rerun 中也是 0.90→1.00」，并以「禁止制造精确单机制收益百分比」收口。候选人应在
   candidate 侧把这条前提补回去；keeper bullet（第 2 条）的措辞本身没有越界。**架构侧 `none`。**
2. **Q129 / Q200 —— 已知失准的简历措辞未修。** 简历第 1 条「收紧 Workspace Tool 路由 / 用回归测试固定路由边界」
   在代码里没有对应物：全仓 `direct_route` 字面量只出现在一个测试函数名
   `tests/agent/test_workspace_simple_agent.py:16`，没有任何断言「多步 query 应回落 ReAct」。
   这是**简历措辞**问题，不是系统缺一条路由规则。建议候选人当场改写为「绑定了 direct route 的
   行为由一条回归测试覆盖」，并在材料里删掉「固定路由边界」这种过强表述。
3. **Q101–Q103、Q158–Q168 —— 历史归属空窗。** 这是 `docs/project/reference.md` 已划定的
   「精确个人闭环 → Unknown unless separately recovered」，系统侧没有缺口（第一轮 S17 已立）。
4. **Q169–Q175 —— Pilot / 法院定性。** 同 S18。文档比简历更保守，问题在简历措辞可能夸大。
5. **Q146 / Q157 —— 「非我所有却讲得极细」的来源问题。** 这是面试叙事的一致性问题（读过的 vs 做过的），
   不是架构问题；架构侧只记录「这一层的实现是真实存在且接线的」（见第三节 #1）。
6. **Q127 / Q135 / Q182 —— `agent_id` 死维度与 typed contract 的语义。** `agent/runtime/nodes/core.py:488`
   确实把 `agent_id` 硬编为 `"agent_run"`（本轮复核无误），但「这个 contract 是不是后补的」是
   解释题，不是系统缺陷；架构侧只记录事实，不新增对象。
7. **材料引用的勘误（非架构）**：候选人（A48/A49/A76）把负向历史 #201/#203/#205/#207 归到了
   `docs/evidence/implementation-wave-001.md`，而该文件只有 45 行、不含这些条目；正确出处是
   `docs/evidence/current-test-baseline.md`。**建议 candidate 侧改引用路径**，这与系统无关。
8. **本文件第一节的 3 处引用勘误（S02/S03/S08 的路径）** 是**我**上一轮笔记的缺陷，
   已在本文件更正；不触发任何代码改动。

---

## 本轮与第一轮的关系（给 Blue Architecture Reflection 用）

- 第一轮 18 条：**全部保留**，其中 S01 扩围、S07 强化、S13 撤回核心指控、S02/S03/S08 更正引用路径。
- 新增 4 条：N01（写-only 的 memory 审计表）、N02（可用性 default-open）、N03（回收侧两个维护入口都无驱动）、
  N04（GraphRAG 退出条件的权威出身）。
- Red Wave 2 里 **5 处**属「抓错 / 抓偏」（第三节），其中 **2 处**（第三节 #1、#2）是 Red 对
  「哪一层没接线」判断错了，**1 处**（第四节 #5）是 Red 把一个 `ANSWER_GAP` 升级成了 `SYSTEM_GAP`。
- 下一轮最该复测的两点：**N02**（把所有 `or "ready"` 改成 `or "unknown"` 后，Q125 那个「带病跑」场景是否真的降级）
  与 **N01/N03**（四张只写不读的表 + 两个无驱动的维护入口，具体怎么删或怎么补读取方）。

初诊与复诊到此为止。
