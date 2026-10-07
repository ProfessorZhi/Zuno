# Blue Architecture Reflection — rb-2026-10-07-formal-020

```text
base_sha: 7d3081f2ccaa20c7eeb0bfff75206d08584a6e51
inputs: 全部 Red/Blue 产物 + 两份 architecture notes + canonical docs + src
authority: Blue Team — Architecture Owner（本轮架构侧收口，判决性质）
judgement_target: 系统本身（Owner / Authority / State / Contract / Recovery / Security /
  Build-Buy 的因果是否成立），不评候选人措辞质量
```

## 0. 开工前必须先说清的三件事（否则本轮结论会被误读）

**(0.1) `04_red_evaluation.md` 在我开工时不存在，在我作业过程中出现了。如实记录全过程。**

我开工时（本分支工作区 14:47 快照）这份「Red Final 盲评」**不存在**：`00_manifest.yaml:129`
是 `red_evaluation_status: NOT_STARTED`、`00_artifact_links.md:27` 同样标 `NOT_STARTED`，
分支 `git log` 只有三条提交（Red Wave 1 / Red Wave 2 / Blue Wave 2）。
于是我按**内容**而不是文件名，先把 `04_red_wave2_review_and_questions.md` 的
**Part A（`blind: true`，`not_seen: canonical docs, source, Evidence`）** 当作 Red 盲评来判，
并在本文件先前版本里把「该文件缺失」记为 F-20。

**在我完成主体作业后、收尾复核时，`04_red_evaluation.md` 作为未跟踪文件出现了**
（`git status` 显示 `?? docs/red-blue/rounds/rb-2026-10-07-formal-020/04_red_evaluation.md`）——
即 Red 终评与我的作业是**并行**完成的。我**完整读完了它**（315 行），并**据此重写了第 9.3 节**：
Red 判错清单从「Part A 的 6 条」改为「Red Final 的 4 条」，并把 F-20 从「文件缺失」改写为
「并行完成，已纳入」。**这一处过程披露是必须的**——如果我不说，读者会以为我一直拿的是
Red Final，而事实上第 1–8 节是在只有 Part A 的情况下写成的，第 9.3 节是在 Red Final 到位后
重写的。**两轮的 Red 产出不是同一份东西，判出的错误也不同**（见 9.3 前置说明）。

**(0.1b) 一个重要的观察：Part A 判错的地方，Red Final 大部分自己修回来了。**
Part A 有 6 处判错（把真接线的层说成"没接线"、把 ANSWER_GAP 升级成 SYSTEM_GAP 等）。
这些在 Wave 2 被候选人当面纠正，**Red Final 吸收了对**：它的 §3 明确写出
「反例（他主动指出）：`assert_audit_durable_for_effect`（活）、abstain 路径（活）、
`citation_eligibility='REJECTED'`（活）、memory 版本 CAS（活）」，并且在 Implementation 维度
自己标注「**我不能判这是架构问题还是实现问题。后者是 Blue 架构侧的权限。**」
**这说明 Part A 的判错主要成因是"没有源码"，而不是"Judgement 差"**——一旦候选人把源码事实喂回去，
它立刻修正。这一点对本轮的 workflow 复盘有直接价值。

**(0.2) 我的判读口径。** 我不顺着 Red 的怀疑往下写。Red 是盲的，它的每一条怀疑我都
**先回源码打一遍**，站得住的才进第 1 节，站不住的进第 9 节的「Red 判错清单」。
本文件里每一个 `file:line` 都是我本轮**实际打开读到**的，不是转抄两份 architecture notes。
两份 notes 里有 3 处 `file:line` 路径错误（第一轮 S02/S03/S08，已在第二轮 `引用勘误` 表里自更），
我复核后确认第二轮给出的路径是对的，本文件采用修正后的路径。

**(0.3) 我不制造数字、不把 Target 说成 Current。** 本文件不出现任何收益百分比、QPS、
Latency、Cost、准确率。凡是「Target / Unknown」的地方，我写 Target / Unknown。

---

## 1. 当前架构真实存在的问题

**先说结论：Red 探到的 100 个坐标里，真正构成「问题」的只有 5 族——其中 P1/P2/P3/P5 是
架构问题（Owner / Authority / State / Contract / Recovery / Security），P4 是实现缺口而不是
架构缺口。** 其余坐标是文档滞后、表达问题、以及「Target 未实现」。

**诚实交代范围：这 5 族与两份 architecture notes 的 S01–S18 / N01–N04 大幅重叠——
它们不是我的新发现。我这一轮的实际增量在「判决」侧而不是「发现」侧**，具体是：
第 2 节（先问删/并/买）、第 4 节（形态是否要换的判断）、第 6 节（**带 caller 证据**的点名删除）、
第 7 节（四层切开）、第 8 节（可执行最小测量）、第 9.3 节（Red Final 的 4 处判错，均为「盲」所致）。
下面 5 族每条都带源码依据，**且每一条我都自己回源码打了一遍**，没有直接转抄 notes。

**关于定性，我改了两处：** notes 把 S06（执行面整套未接线）记成 `SYSTEM_GAP / P1`——
我改成 `IMPLEMENTATION_GAP`，因为 canonical 文档已自认它是 Target/Gap（见 P4）；
notes 第一轮 S13 已被第二轮自行撤回——我复核确认撤回正确，本轮不重报（见 9.3 前置说明）。

### P1 —— 「就绪 / 健康」这个事实有三个所有者，且读路径 default-open（真 Authority 缺陷）

系统的权威规则自己把这条事实写死了三遍：`docs/README.md:19`（「Project、Architecture、
Modules、Decisions、Evidence 和 Governance 继续保持各自唯一事实边界」）；
`docs/modules/reference.md:236`（架构不变量 2：「上传成功不等于 Knowledge Ready；
Readiness 相对于 DocumentVersion + generation + task scope + requirement + security」）；
`docs/modules/knowledge/README.md:27`（「平台不存在一个可以替代这些判断的全局绿色灯」）。
「某索引/图谱现在是否可用」这条事实**同时违反了这三条**：

| 所有者 | 位置 | 写入的什么 |
| --- | --- | --- |
| 配置模板常量 | `api/services/knowledge.py:53-55,73-74`（`DEFAULT_KNOWLEDGE_CONFIG`） | `health_status/text_index_status/bm25_index_status/graph_index_status = "ready"` 字面量 |
| DTO 缺省值 | `api/dto/knowledge.py:70-72,109-110`（`Field(default="ready")`） | 请求/响应模型缺失即绿 |
| 读路径兜底 | `retrieval/planner.py:91`、`retrieval/orchestrator.py:861`、`rag/handler.py:486`、`application/knowledge/query_service.py:155-156`、`graphrag/community/service.py:41` | 探活缺失 → `or "ready"` |
| 硬编码布尔 | `agent/planning.py:43`（`graph_available: bool = True`）、`api/services/product/runtime_engine.py:2862`（`graph_available=True`） | 图可用性写死为真 |

而**真正的判定链**（`platform/database/knowledge/domain.py:296 mark_ready`，要求 ≥2 类可见索引）
在 `api/services/knowledge.py:754` 只有**一个调用点**，其结论既不写入上面任何一个消费点，
也不被检索路径读取。

**这不是「一个常量写错了」，是「谁有权把未就绪改成已就绪」没有唯一写入点，并且读侧缺省即绿。**
两者叠加的直接后果：探活未接、探活失败、探活根本没部署三种情况，在检索路径上**都读成"可用"**。
这是 Authority / Contract 因果不成立 → `ARCHITECTURE_GAP`。

### P2 —— 已声明「跨案隔离」的读取层，实际只有 4 维 scope 且把 scope 相等当授权（真 Contract 缺陷）

权威文档把话说死了：`MemoryScope equality != Authorization`（`docs/modules/reference.md:86`），
并且「payload 不替代 Domain truth，冲突时 Domain 为准」（`docs/project/reference.md:51`）。

代码里 `MemoryScope` 只有 4 维：`user_id / agent_id / project_id / thread_id`
（`platform/services/memory/layers.py:43-47`），`project_id` 在写侧就是 `workspace_id`、
`agent_id` 硬编 `"agent_run"`（`agent/runtime/nodes/core.py:485-491`）。
**没有任何案件/事项维度。** 读侧唯一的闸门就是这 4 维相等
（`platform/services/memory/store.py:312-338` 的 `_scope_select`；应用层 `layers.py:284-291`）。

也就是说：文档声明「scope 相等**不等于**授权」，但**实现里 scope 相等就是全部授权**。
这条 doc-code 分裂本身是 `ARCHITECTURE_GAP`（Contract 的因果不成立：一句写在权威文档里的
安全前提，在代码里没有任何裁决点承载它）。

### P3 —— 「未确认副作用」的收敛闭环在设计里整类缺席（真 Recovery 缺陷）

系统**建模了**这件事：副作用结果未知时写 durable `UNKNOWN_EFFECT`、
`next_action="RECONCILE"`、`age_escalation_after_seconds=900`
（`capability/tool_runtime/invocation_gateway.py:560-564,612-616,729-733,860-864`），
并提供一个升级入口 `escalate_due_reconciliations`（同文件 `:1607`）。

我复核了两个维护入口和整个调度面：

- `escalate_due_reconciliations`：定义 `invocation_gateway.py:1607` + 下探实现
  `platform/database/tool_runtime/domain.py:1188` + **调用方只在**
  `tests/capability/test_tool_effect_postgres_boundary.py:211,308,389`。
- 它的兄弟 `timeout_due_async_jobs`：定义 `invocation_gateway.py:1614` + 下探
  `domain.py:1206` + **零非测试调用方**。
- 调度面：`grep -rniE "apscheduler|BackgroundScheduler|add_job|\.cron|periodic" src/backend/zuno/`
  → **零命中**。

结论比第一轮更重：这**不是「两个函数漏接线」**，而是**「常驻收敛任务」这一类机制在设计里
根本不存在**。900 秒的升级窗口是一个**永远不会到期的定时器**。

而且 canonical 文档把它错记在别处：`docs/governance/effect-remote-query-reconciliation-status.md`
记的是 `DEFERRED_BY_PROVIDER_CAPABILITY`（远端查询能力被 provider 限制）——但「本地定时把
超龄 OPEN 行升级为 MANUAL_ASSESSMENT」**不依赖任何 provider 能力**，是本地可完成的部分。
它被一起 Defer 了。Recovery 因果不成立 → `ARCHITECTURE_GAP`。

### P4 —— 执行面的「版本 / 晚到结果围栏 / 恢复」整套只有契约，没有一块在主路径上（真实现缺口，非设计缺口）

PlanState 的 `plan_version` 在 `agent/runtime/service.py:315,323,331` 被赋成**字面量 0/0/1**，
`contracts.py:392` 默认值 `1`；live replan 走 `model_copy` 只改 status、不递增版本
（`agent/runtime/planning/replan.py:39-45`）。
持久化入口 `append_plan_version` 只有定义（`agent/runtime/sqlite_store.py:318`），无调用方。

`agent/runtime/planning/` 下这一组执行器，我逐个查了外部调用方（`src/` + `tests/` + `tools/`）：

| 执行器 | 定义 | 外部调用方 |
| --- | --- | --- |
| `ReplanBarrierExecutor` | `planning/replan_barrier.py:159` | 无（仅 `planning/__init__.py` re-export） |
| `JoinControlDecisionEngine` | `planning/control_decision.py:98` | 无（同上） |
| `ParallelRecoveryPlanner` | `planning/recovery.py:176` | 无（同上） |
| `Phase21CrashRecoveryMatrix` | `planning/recovery.py:91` | 无（连 re-export 都没有） |
| `DynamicStepWorker` | `planning/dynamic_worker.py:53` | 无 |
| `BranchResultFencer` | `planning/branch_result.py:81` | 仅被 `DynamicStepWorker`（`dynamic_worker.py:63`）——而它自己也没调用方 |
| `RecoveryAction.RESEND_OUTBOX` 执行点 | `planning/recovery.py:12,64,154,222` | 无执行者 |

`grep -rln` 对上述类名扫 `tests/` → **零个测试文件**。

**这一条我要和第一轮/第二轮给出不同定性。** 两份 notes 把它记成 S06「SYSTEM_GAP / P1」，
但 canonical 文档**已经自己承认**这是 Target/Gap：`docs/modules/runtime/README.md:103` 明写
「三层运行图 / 不可变 PlanVersion / Replan Barrier / Domain matching Receipt recovery
仍是 Target/Gap」。既然 Target 文档如实标注了，它就**不是架构问题，是实现缺口** →
`IMPLEMENTATION_GAP`。真实风险不在于「设计错了」，而在于**这批 in-tree 的执行器让 Current
读起来比实际丰满**——这正是简历第 4 条 bullet 会被追问到底的原因。

### P5 —— 授权面：产品动作门不带租户范围，凭据型配置无归属校验（真 Security 缺陷）

两处，我逐个打开确认：

1. **租户/工作台被写死为字面常量。** `api/services/security_admin_actions.py:26-27`：
   `tenant_id = "system"` / `workspace_id = "system"`，随后原样塞进
   `SecurityProductActionRequest`。函数的签名里**只有 `principal_id`**，没有任何租户入参。
   这等于：这一层的授权判定**在类型上就取不到租户/工作台范围**。
2. **承载凭据的 per-user MCP 配置无对象级归属校验。**
   `api/services/mcp_user_config.py:121-125` 的 `delete_mcp_user_config(config_id)` 只接收
   `config_id`，DAO 层直接删；`api/v1/mcp_user_config.py` 里**只有 `/test` 这一条路由**
   （`:42`）调用了 `verify_user_permission`，GET（`:50-60`）与 DELETE（`:81-91`）都没有。
   这份配置里存的是 `APPCODE` / API Key 一类凭据。

Security 因果不成立 → `ARCHITECTURE_GAP`。

### （附带）两个已核实的**具体缺陷**，不是架构问题但必须点名

- **出站效果工具关闭 TLS 校验并携带凭据。** `capability/tools/delivery/action.py:41`
  （`Authorization: APPCODE {api_key}`）与 `:47-49`
  （`ctx.check_hostname = False` → `ctx.verify_mode = ssl.CERT_NONE` → `urlopen`）。
  这是本仓库里少数真实改变外部现实的出站路径之一。`IMPLEMENTATION_GAP`（安全严重）。
- **中文法律检索路径上挂着英文 HotpotQA 词典。**
  `platform/services/retrieval/fusion.py:18-30`（`ENTITY_STOPWORDS`，含 `same` / `nationality` /
  `birthplace` / `older` / `younger`）、`:36-55`（`BRIDGE_RELATION_CUES`：`founded by` /
  `father of` / `professor at` / `population of`）、`:56` 起（`GENEALOGY_RELATION_CUES`：
  `maternal grandfather` / `paternal grandfather`），且 `:344-349` 无条件按 query 子串命中。
  同一文件还硬编 9 个融合阈值（`:8-60`），代码里无任何来源标注。
  `EVIDENCE_GAP`（在中文法律 query 上的实际误伤率**从未被测**，见第 8 节 M5）。

---

## 2. 简单方案够不够

**口径：对每一个真问题，先问「删掉 / 合并 / 买现成的行不行」，只有都不行才问「是不是要新增机制」。**
结论是：**5 族问题里，4 族的最优解是删 / 收窄 / 回退，而不是新增机制；剩 1 族的降级解也是零新增。**

| 问题 | 先问删/并/买 | 我的判断 |
| --- | --- | --- |
| **P1 Ready 三所有者** | 删。把配置模板与 DTO 的 `"ready"` 缺省、读路径 `or "ready"`、两处 `graph_available=True` 全部改掉 | **够用，零新增**。最简形态 = 把 `or "ready"` 改成 `or "unknown"`，消费点把 unknown 视为不可用。不需要三态类型系统，不需要新的探活服务。若产品确需展示态，用一个从 `knowledge_domain_versions` 派生的只读视图。 |
| **P2 Memory scope ≠ 授权** | 收窄。不扩存储模型 | **够用，零新增**。最小改动 = 读取入口强制携带案件/事项过滤参数 + 单一条裁决规则（Domain 有值则 Memory 不注入）。**不需要新机制**，需要的是承认「文档那句真理必须在代码里有一个裁决点」——这是**删掉一句空话、补一个判定**，不是加一层。 |
| **P3 未确认副作用的收敛** | 买/删。不装调度器 | **够用，零新增**。「买现成的」在单体后端里没意义；正确解是**删掉那个想象中的常驻任务**——改为**写时升级**：写 durable UNKNOWN / 写 async job 时同步落一条待人工处置记录。语义与「900 秒后升级」等价，且不需要部署面配合。 |
| **P4 执行面整套未接线** | 删。这是最大一块无人调用代码 | **够用，零新增**。删/归档全部无 caller 的执行器（见第 6 节），只保留 `agent/runtime/planning/` 里**被 domain 层真正 import 的契约**（`DispatchCommit` / `BranchResultRef` / `ReducedJoinOutcome` / `ReplanBarrierRequest` / `DynamicStepSendEnvelope` / `PersistedStepRunSnapshot` / `DispatchItemStatus` / `StepRunStatus` / `ReplanBarrierStatus`，见 `platform/database/agent/domain.py:28-36`）。若日后真要接，只落「单调整数版本 + 到达时 stale 判定」一个判定点。 |
| **P5 授权面** | 收窄。不建授权框架 | **够用，零新增**。service 层方法接受由调用方传入的已认证 principal 并在内部做 owner 比对（断言级）；`tenant_id/workspace_id` 从请求上下文解析后传入，不再用常量。不引入 ABAC/RBAC 引擎。 |
| 出站 TLS | 删 | **够用**。删两行（恢复默认校验）。若端点证书确实不合法，会立即暴露失败——这正是期望行为。 |
| 融合英文词典 | 删 | **够用**。删英文/家谱词典，融合先降到单一 `baseline_preserving`。等 ablation 有数据再决定是否恢复图晋升。 |

**唯一一处我倾向「可能要新增」的，是 P2 的存储维度：** 如果不接受「读取时携带案件参数」的
轻量方案，那案件维度就必须真的进 Memory 存储与检索两侧。但这是**产品语义选择，不是架构必要性**——
两条路都能成立，我倾向先走零新增那条。

**「买现成的」在本轮全部问题上的适用性是零。** 这 5 族问题没有一个是「缺一个组件」，
全部是「自己的事实边界没收敛」。所以 Build/Buy 维度**没有一条**构成本轮的架构问题。

---

## 3. 在哪个 failure / constraint 下失效

每条给**可复现的触发条件**，不给形容词。

**F1 —— 跨案串读（击穿 P2）。** 触发条件：同一个律师在同一 workspace 下同时处理案件 A 与案件 B。
`MemoryScope` 只有 `user_id/agent_id/project_id/thread_id`，而 `project_id == workspace_id`
（`nodes/core.py:485-491`），两案在 scope 上**不可区分**；读侧按 scope 相等过滤
（`memory/store.py:312-338`）。→ 案件 A 的 task summary / structured memory 会被注入案件 B 的
`prepare_context()`。**这是最简单的现实约束就能击穿的**，不需要任何并发或故障。
（注：这条与 Red 的怀疑方向一致，但 Red 没有定位到 `project_id == workspace_id` 这个关键等号。）

**F2 —— UNKNOWN effect 永久悬挂（击穿 P3）。** 触发条件：一次工具调用 HTTP 超时（远端实际已执行）。
系统写 durable UNKNOWN + 900s 升级窗口，但**没有任何驱动**（`escalate_due_reconciliations` 零非测试
调用方；全仓无调度器）。→ 900 秒后**不进 MANUAL_ASSESSMENT，无人被通知**，那条 OPEN 行一直挂着。
人工结论路径（`record_manual_effect_assessment`，`invocation_gateway.py:1787`）是通的，但它需要
**有人知道要去点**——而"通知有人"这件事正是缺失的那一半。

**F3 —— 图索引坏了但带病跑（击穿 P1）。** 触发条件：graph 索引构建失败 / 探活服务未部署 / 探活返回空。
`retrieval/planner.py:91` 的 `or "ready"` → `:97` 的
`graph_available = knowledge_capability == "rag_graph" and graph_health not in {unavailable,failed,stale}`
**为真**；`runtime_engine.py:2862` 的 `graph_available=True` 是写死的；`agent/planning.py:43` 默认 True。
→ 检索持续走一条坏掉的图路径。**系统自己声明「不存在全局绿灯」，但读路径缺省就是绿灯。**

**F4 —— 多租户下授权空转（击穿 P5）。** 触发条件：只要部署里存在两个及以上 tenant/workspace。
`security_admin_actions.py:26-27` 把 `tenant_id/workspace_id` 恒定为 `"system"` → 授权门
**在类型上无法区分租户**；同时 `mcp_user_config` 的 GET/DELETE 只凭 `config_id`
（`api/services/mcp_user_config.py:121-125`）→ 知道/猜到 `config_id` 即可读取或删除他人的
`APPCODE` 配置。**同时满足两条才算"多租户是承诺"，但今天单租户部署也会踩第二条。**

**F5 —— replan 之后的晚到结果（击穿 P4）。** 触发条件：一次发生 replan 的任务，同时有一个
分支结果在 replan 之后到达。`plan_version` 恒为字面量（`service.py:315,323,331`），
围栏执行器无调用方（第 1 节 P4 表）。→ **旧计划的产物无法被判定为 stale。** 今天之所以没出事，
是因为重规划的分支并行本身也没在主路径上跑——**两个缺口互相掩盖**。一旦按 Target 接上，
这个缺口就会立刻暴露。

**F6 —— 撤销一条错误 memory 之后（击穿 P2 的写侧）。** 触发条件：发现一条错误的 task summary。
读取侧**已经**会排除 `stale/conflict/revoked`（`memory/engine.py:1054-1064`），
但**没有任何生产代码写入这三个状态**——我复核了 writer 侧，只有测试构造它们
（`tests/memory/test_context_pack_engine.py:140-142`）。→ **撤销没有执行者**，且已构建并注入过的
context pack 不失效、不回滚。同时 task summary 无版本/`updated_at`（`layers.py:90-115`），
读取按 `created_at` 取第一条非空（`memory/store.py:328`）→ **旧 summary 与最新事实冲突时，
读取侧无从比较新旧。**

**F7 —— 中文法律查询被英文家谱线索干预（可能击穿，需测量）。** 触发条件：中文法律 query 里
出现与英文线索同形的子串（词面命中是**无条件**的，`fusion.py:344-349`）。
`ENTITY_STOPWORDS` 里的 `same` / `nationality` / `older` 一类词在中文语料里未必出现，
但 `QUERY_ENTITY_PHRASE_PATTERN`（大写实体短语）与 9 个硬编阈值对**任何**查询都生效。
→ **我诚实标注：这条的实际误伤率我不知道，也从没有被测过**（见第 8 节 M5）。不制造数字。

---

## 4. 替代方案判断（Multi-Agent / Specialist / Subgraph / Generic Host / Native Runtime / 单体）

**结论一句话：维持「Python 单体模块化后端 + Generic Host 边界 + measurement-gated 的
Native Runtime 子系统」；六种形态一个都不要换。**

理由（给判断，不罗列可能性）：

1. **形态这件事在本仓库已经不是开放问题，是已接受决策。** ADR-0012 明确把默认物理起点定为
   `Python Modular Backend`，并把微服务/独立服务列为**证据门控**的 Target Refinement
   （没有负载、故障、安全、部署生命周期证据就不预先承诺服务数量）。ADR-0008 定的是
   `Legal Domain Kernel + Generic Host`，且明写 **Native Runtime 继续由测量门控**。
   ADR-0013 冻结九模块，ADR-0014 冻结跨边界 Authority/Recovery。
   **「哪一个更合理」在 Zuno 里已经答过了——再讨论一次就是重新开一个已关闭的决策。**

2. **「换成 Multi-Agent」在本仓库是有反向证据的。** 仓库里**存在过多 Agent 的正式形态残骸**：
   `77346758`（PF-032）移除了 `tool_invocation_model` / `available_tools` / LLMToolSelector
   脚手架，以及把 `MCPAgent` / `SkillAgent` 当 Tool 嵌套的结构；`MCPAgentTable` +
   `api/v1/mcp_agent.py` 的 CRUD 面**至今还在**（`platform/database/dao/mcp_agent.py`）。
   也就是说 **Multi-Agent 是被撤下来的，不是没想到**。而 `multi_agent_enabled` 这个字段
   今天唯一被读的地方是一条**边界断言**：`product/runtime_batch.py:428` 的
   `if fixture.task_request.multi_agent_enabled: errors.append("Product Surface must not become
   a second controller")`。**仓库的表达是「产品面不许变成第二个 controller」，不是「多 Agent 是目标」。**
   → 往 Multi-Agent 走是逆着既有决策与既有边界断言走。

3. **「Subgraph / 独立服务」在 ADR-0012 下缺的正是证据，不是理由。** 今天的实际约束
   （单体后端 + 有限 selected verification + `FULL CI: NOT RUN`）不支持任何按负载或隔离
   推导出来的服务边界。**先拆服务等于把 P4 那类「写了没接线」的问题放大一个数量级。**

4. **「全量 Native Runtime / 去掉 Generic Host」同样没有证据。** canonical 记
   `PF-025: Native Runtime 必要性 = TARGET / MEASUREMENT_GATED`，且
   `docs/architecture/README.md` 的阅读主线就是从 **Generic Agent Host + Legal RAG baseline**
   起步、再被真实约束逼出边界。今天**没有一条对照证据**说 Native Runtime 对所有任务更好。
   反过来，Target 明确保留 「Simple QA 走 Generic Host / controlled RAG 短路径」
   （`docs/architecture/architecture.md:189`）。

5. **「Specialist」在 canonical 里明确是 measurement-gated 复杂度**，与 GraphRAG / Reflection /
   Long-term Memory / Native Runtime 并列（`architecture.md:173`、
   `architecture-views.md:186,199`、`modules/reference.md:244`）。**没有一个可以默认开启。**

**所以我给的不是「六选一」，而是「不要选」：真正需要做的不是换形态，而是把「哪一层在跑」
收敛清楚——把 P4 那一批无 caller 的执行器删掉或明确标注。** 换形态解决不了
「写完了但没接线」，只会让它更贵。

**唯一一条我会主动动的形态边界**：`phase08.py`。它是一条**已接受 ADR 的合规路线**
（官方 LangGraph `InMemorySaver`/`PostgresSaver`，`agent/runtime/phase08.py:36-56`），
在 adr-0005 里被写成「唯一基础」，但它**零功能调用方**（`agent/runtime/__init__.py:22,40` 只有
re-export）、**在 docs 全域零提及**、并且**有一条测试反向守护它的 cutover 文件不许存在**
（`tests/repo/test_agent_system.py:36`：断言 `phase08_cutover.py` 必须不存在）。
**ADR 与在跑的实现互为对方的反例，而一条测试在守护这个分裂。**
这不是形态问题，这是**已接受决策与现实的冲突**，必须显式收口（见第 5 节）。

---

## 5. Authority / Owner / State / Contract / Recovery / Security 调整建议

逐项给「动什么、动到哪」，不新建框架。

### Owner
- **就绪/健康事实收敛到单一所有者。** 只允许 `platform/database/knowledge/domain.py` 的
  `mark_ready` 判定结果单向写入；配置模板、DTO 缺省、读路径兜底**一律不得**产生 `"ready"`。
  未判定 = `unknown`。**这是删所有者，不是加所有者。**
- **GraphRAG 保留/删除的决定权明确归 architect（03/09 module owners），不归评测轮次协议。**
  今天 `docs/governance/rb019-graphrag-ablation-protocol.md:5-7` 的 `source` 是
  `red-blue rb-2026-09-15-formal-019 / IMP-019-05`——**一份面试轮次产物**（它的 `owner` 字段写的是
  03/09，方向是对的，但没有任何地方说清「数据到位前谁有决定权」）。补一行 authority 即可。

### Authority
- **Memory readback 的裁决点要真实存在。** 文档写了 `MemoryScope equality != Authorization`
  与「冲突时 Domain 为准」，但代码里没有裁决点。要么在读取入口建立它，要么把文档那句降级为
  「期望」并写进 Target 的未实现清单。**二选一，不许现状继续。**

### State
- **就绪态三值化（unknown / ready / not_ready），删掉布尔默认。** `graph_available` 的两个硬编码
  `True`（`agent/planning.py:43`、`runtime_engine.py:2862`）收敛为「由上游探活结果单一写入」。
- **Memory 需要一个案件/事项维度，或者一个强制的案件过滤参数。** 二者择一，但必须让
  「同 user + 同 workspace 的两个案件」在读取时**可区分**。
- **task summary 补 `updated_at`**（今天无版本/时间戳，`layers.py:90-115`），让「取最新」有依据。
- **memory 撤销语义显式化。** 今天读侧排除逻辑存在但无写入方 → 要么定义唯一撤销写入路径，
  要么把「不设撤销」写成**被接受的**语义。**「撤销是否回溯已构建的 context pack」必须在文档里有答案**——
  当前是没有答案，这才是架构缺口（不是「没实现」）。

### Contract
- **per-user MCP 配置的 service 方法必须接受已认证 principal 并在内部做 owner 比对**；
  路由层不得只凭 `config_id` 操作别人凭据（`api/services/mcp_user_config.py:121-125`）。
- **两套融合实现必须声明各自 profile，或收敛为一套。** 我复核确认**两套都在活路径上**：
  产品侧 `retrieval/fusion.py` 经 `retrieval/orchestrator.py:80` 被 `rag/handler.py:529` 与
  `graphrag/query_service.py:141` 消费；agentic 侧 RRF（`knowledge/agentic_graphrag.py:876`，
  `+ 1.0/(60.0+rank)`，k=60 硬编）经 `knowledge/agentic/runtime.py:393` 被
  `api/services/product/runtime_engine.py:3163` 消费。**不是「一条活一条死」**（Red 判错，见第 9 节 R2），
  但**同一语义两份口径、谁维护未声明**——这是真的 Contract 缺口。
- **负结论（「全案里没有 X」）必须有准入契约。** 今天只有 `coverage_ratio` + 4 类 `stop_reason`
  （`knowledge/agentic/evidence_ledger.py:58-86`）与固定 abstain 文案
  （`agent/runtime/synthesis/grounded_answer.py:87`）。最小动作是**契约收紧**：
  禁止输出绝对否定句，降级为「在当前检索范围内未见」。判定层等有真实 bad case 再建。

### Recovery
- **把「本地可完成的收敛」与「依赖 provider 能力的远端查询」拆成两条独立状态记录。**
  今天它们被同一条 `DEFERRED_BY_PROVIDER_CAPABILITY` 一起 Defer 掉了
  （`docs/governance/effect-remote-query-reconciliation-status.md`）——
  但**升级计时器没有驱动**是纯本地问题，不该被 provider 能力一起 Defer。
- **durable UNKNOWN 的收敛改为写时升级**（见第 2 节 P3），或接一个最小常驻扫描。
  **二者择一，但必须有一个。**

### Security
- **恢复 TLS 校验**（`capability/tools/delivery/action.py:47-49`）。一行级。
- **授权门的租户/工作台从请求上下文解析**，不再是 `"system"` 常量
  （`api/services/security_admin_actions.py:26-27`）。
- **per-user 凭据配置的对象级归属校验**（见 Contract 段）。
- **fail-closed 的门要被真实可触达。** 今天 epoch 撤销**在生产侧没有生产者**——把 status
  改成 revoked 的唯一代码路径在测试的裸 SQL 里（`tests/evidence` 的 #203 / run `34560042535`
  记录的正是这个 seam）。2026-10-07 之前这条一直没人在生产路径验证过。**一个只在测试里能触发的
  fail-closed 分支，其 fail-closed 性质在生产里是未验的。**

---

## 6. 应该删除的复杂度

**这一节我点名，并且只用我本轮实际查过 caller 的东西。** 判定尺子统一为：
「在 `src/backend/zuno` 里有没有非 re-export 的外部调用方（`tests/`、`tools/` 也算）」。

### 6.1 直接删 / 归档（无外部 caller，且无测试覆盖）

1. **`agent/runtime/planning/` 下的整套执行器**：
   `ReplanBarrierExecutor`（`replan_barrier.py:159`）、
   `JoinControlDecisionEngine`（`control_decision.py:98`）、
   `ParallelRecoveryPlanner`（`recovery.py:176`）、
   `Phase21CrashRecoveryMatrix`（`recovery.py:91`）、
   `DynamicStepWorker`（`dynamic_worker.py:53`）、
   `BranchResultFencer`（`branch_result.py:81`）。
   **注意保留同目录被 domain 层 import 的契约类**（`platform/database/agent/domain.py:28-36`
   引用了 `DispatchCommit` / `BranchResultRef` / `ReducedJoinOutcome` / `ReplanBarrierRequest` /
   `DynamicStepSendEnvelope` / `PersistedStepRunSnapshot` / `DispatchItemStatus` / `StepRunStatus` /
   `ReplanBarrierStatus`）。**删执行器、留契约**——这样 domain 层的类型标注不破。
2. **`recovery.py` 的 `RESEND_OUTBOX` 执行路径**（`:12,64,154,222`）：没有任何地方执行它。
3. **`agent/runtime/sqlite_store.py:318 append_plan_version`**：零调用方。
4. **`agent/runtime/phase08.py`**：ADR-0005 的合规路线，零功能调用方、docs 全域零提及、
   且被一条测试反向守护。**要么按 ADR 接线，要么退役。** 现状——「已接受的 ADR 与在跑的
   实现互为反例，还有测试守护这个分裂」——是本轮最不该保留的复杂度。
5. **`agent/runtime/contracts.py:61 RuntimeLimits.timeout_ms`**：声明了、没有任何读取点（死字段）。
   **要么接线（围着一次 tool 调用起定时器），要么删。**
6. **`agent/runtime/nodes/core.py:488 agent_id="agent_run"`**：硬编且无消费方的死维度。
7. **`capability/tools/delivery/action.py:47-49` 的两行 TLS 关闭**。
8. **`platform/services/retrieval/fusion.py` 的英文 HotpotQA 词典**（`ENTITY_STOPWORDS`、
   `BRIDGE_RELATION_CUES`、`GENEALOGY_RELATION_CUES`，`:18-56`，使用点 `:240,268,344-349,356,
   373,492,505,633`）。**证据驱动开发的原则下，一条没有来源标注、没有 ablation 依据、
   且形状明显来自英文多跳 benchmark 的词典，不该默认待在中文法律检索路径上。**
9. **9 个硬编融合阈值**（`:8-60`）：代码里没有任何一行注释写来源。

### 6.2 收敛成开关，不是删除（有写侧价值，但无读侧）

10. **四张「只写不读」的 memory 审计表**：`context_pack_versions`（`platform/database/memory/
    domain.py:383`）、`memory_use_traces`（`:486`）、`memory_candidates_v2`（`:171`）、
    `memory_snapshots`（`:326`）——**表名字面量在全仓各只出现一次，且那一次都是 INSERT；
    `FROM <表>` 零命中（连测试都没有）**。只有 `memory_versions` 有读侧（`:313,333`）。
    → **收敛为一个默认关的 trace 开关**，或给它们定义真实读取方。**不要继续把它们当已建立的
    审计能力描述。**
11. **`multi_agent_enabled`**：除边界断言（`product/runtime_batch.py:428`）外，没有实际启用路径
    （`platform/services/workspace/simple_agent.py` 里只赋值 `:288`、从不读）。
    **不要把它讲成能力**，也不要为它建 reader。

### 6.3 我**不**建议删的（防止下一轮误删）

- **`MCPLangChainToolAdapter` 不是壳，不要删。** 它有真实消费方：
  `platform/services/workspace/simple_agent.py:1340`（`build_mcp_langchain_tool_adapter`）与
  `wechat_agent.py:102,209`。候选人在 A10/A77 里自认它是「可删层」，但**源码不支持这个自认**——
  这一点我放进第 9 节的 Red/候选对照里。
- **`agent/runtime/planning/` 的契约类**（见 6.1-1 的保留清单）。
- **`capability/tool_runtime/runtime_batch.py`**：它是**枚举/契约定义文件**（`DispatchCertainty` 等），
  随包 `__init__` 导出，**没有「执行逻辑」可接线**，所以「无 caller」对它不适用。
- **`agent/runtime_batch.py validate_agent_runtime_batch`**：它是**校验工具**
  （被 `tools/scripts/verify_agent_runtime_batch.py:11` 与测试消费），工具没有产品 caller
  是它的本来用途。
- **`platform/recovery/replay.py InMemoryReplayPort`**：只有 in-memory 实现属实，但它是
  Protocol 的合法最小实现，删它不会让恢复更正确。

**这一节的总结：本仓库「写了但没接线」的最大一块是 04 Runtime 的控制面（第 6.1-1~4），
其次是 09/03 的审计面（第 6.2-10）。两者性质不同：前者应删，后者应收敛为开关。**

---

## 7. Current / Target / Evidence / Unknown 分层清单

**这是本轮最重要的产物。** 四层严格分开，任何一条都不得跨层。所有 `file:line` 为本轮实读。

### 7.1 Current —— 代码 / 测试今天可以复核的

| # | 事实 | 依据 |
| --- | --- | --- |
| C01 | per-user MCP 配置按请求作用域拷贝注入（`call_args = dict(args)`），缺失即抛 `MCPToolAdapterNotBound`，并发不串 | `platform/services/workspace/simple_agent.py:188-208` |
| C02 | 执行前两次授权新鲜度复核（发放 secret lease 前、真实派发前） | `capability/tool_runtime/invocation_gateway.py:388,462` |
| C03 | 副作用前强制持久审计 + 读回验证持久性，写失败则 `dispatch_aborted` | `invocation_gateway.py:430,1426,1499` |
| C04 | 远端结果未知 → durable UNKNOWN + `next_action="RECONCILE"` + `age_escalation_after_seconds=900` | `invocation_gateway.py:560-564,612-616,729-733,860-864` |
| C05 | 幂等位 TTL = 60 秒 | `invocation_gateway.py:1298,1321`（`ttl_seconds=60`） |
| C06 | `escalate_due_reconciliations` 与 `timeout_due_async_jobs` **零非测试调用方**；全仓无调度器 | 定义 `invocation_gateway.py:1607,1614`；调用方仅 `tests/capability/test_tool_effect_postgres_boundary.py:211,308,389`；`grep -rniE "apscheduler\|BackgroundScheduler\|add_job\|\.cron\|periodic" src/backend/zuno/` 零命中 |
| C07 | 两条融合实现**都在活路径上** | 产品侧 `retrieval/fusion.py` ← `retrieval/orchestrator.py:80` ← `rag/handler.py:529` / `graphrag/query_service.py:141`；agentic 侧 `knowledge/agentic_graphrag.py:876` ← `knowledge/agentic/runtime.py:393` ← `product/runtime_engine.py:3163` |
| C08 | `CorrectiveAction.ABSTAIN` 已接线（真分叉） | `knowledge/agentic/corrective.py:21,33,46,55` → `knowledge/agentic/runtime.py:349,595-596` |
| C09 | 就绪/健康读路径 default-open（多处 `or "ready"` + 硬编 `True`） | `retrieval/planner.py:91`；`retrieval/orchestrator.py:861`；`rag/handler.py:486`；`application/knowledge/query_service.py:155-156`；`api/dto/knowledge.py:70-72,109-110`；`api/services/knowledge.py:53-55,73-74`；`agent/planning.py:43`；`product/runtime_engine.py:2862` |
| C10 | `MemoryScope` 只有 4 维；`project_id == workspace_id`；`agent_id` 硬编 `"agent_run"` | `platform/services/memory/layers.py:43-47`；`agent/runtime/nodes/core.py:485-491` |
| C11 | memory 撤销的**读取侧**排除已实现（`stale/conflict/revoked`），**写入侧**只有测试 | `memory/engine.py:1054-1064`；`tests/memory/test_context_pack_engine.py:140-142` |
| C12 | 四张 memory 审计表只写不读 | `platform/database/memory/domain.py:110,171,313,326,333,348,383,486`；`FROM context_pack_versions` / `FROM memory_use_traces` / `FROM memory_candidates_v2` / `FROM memory_snapshots` 全仓零命中 |
| C13 | `plan_version` 恒为字面量；`append_plan_version` 无调用方；围栏/恢复执行器整组无 caller | `agent/runtime/service.py:315,323,331`；`agent/runtime/sqlite_store.py:318`；`planning/replan_barrier.py:159`、`control_decision.py:98`、`recovery.py:91,176`、`dynamic_worker.py:53`、`branch_result.py:81` |
| C14 | 商品动作授权门 `tenant_id/workspace_id` 恒为 `"system"` | `api/services/security_admin_actions.py:26-27` |
| C15 | per-user MCP 配置 GET/DELETE 仅凭 `config_id`；只有 `/test` 路由做权限校验 | `api/services/mcp_user_config.py:121-125`；`api/v1/mcp_user_config.py:42,50-60,81-91` |
| C16 | 出站物流工具关闭 TLS 主机名/证书校验并携带 `APPCODE` | `capability/tools/delivery/action.py:41,47-49` |
| C17 | `main.py` 已构造并绑定产品安全 composition | `main.py:59-115`（`PostgresSecurityDecisionResolver:59,68`；`WorkspaceRuntimeComposition:61,99`；`configure_workspace_product_composition:62,115`） |
| C18 | `court` / `法院` / `judicial` 在 `src/backend/zuno/` **零命中** | 全仓 grep 无输出 |
| C19 | `direct_route` 字面量**只出现在一个测试函数名**里 | `tests/agent/test_workspace_simple_agent.py:16` |
| C20 | 有一条测试断言 `phase08_cutover.py` 必须不存在 | `tests/repo/test_agent_system.py:36` |
| C21 | 英文 HotpotQA 词典与 9 个硬编阈值在检索融合文件内，无条件按 query 子串命中 | `platform/services/retrieval/fusion.py:8-60,240,268,344-349,356,373,492,505,633` |
| C22 | `RuntimeLimits.timeout_ms` 声明无读取点 | `agent/runtime/contracts.py:61` |
| C23 | `self.user_id` 是**构造时冻结的实例属性**（`self.user_id = user_id`，`simple_agent.py:285`），`_execute_binding_tool` 传的是它（`:1374-1401`，`:1388,1397`）；而该实例**每请求新建一次**（`build_simple_agent` 是 `@staticmethod`，`WorkSpaceSimpleAgent(user_id=login_user.user_id, ...)`，`api/services/workspace.py:149,162-186,321`，无缓存 / 无单例）→ **当前代码里不存在"同实例跨用户复用"的可达路径** | `platform/services/workspace/simple_agent.py:280-285,1374-1401`；`api/services/workspace.py:149,162-186,321` |
| C24 | `memory_state` 的**唯一写入值**是 `"decayed"`；`{stale, conflict, revoked}` **只出现在读侧排除集合里**，无写入方 | `memory/engine.py:440`（写 `"decayed"`）vs `:1057-1059`（读侧排除 stale/conflict/revoked） |
| C25 | `evidence_stale` 只在 `knowledge/provenance.py:88` 被产出（`_reject(..., STALE, "evidence_stale")`），**无消费方**；而 `citation_eligibility='REJECTED'` 被 SQL 读过滤（有消费方） | `knowledge/provenance.py:88`；`platform/database/knowledge/domain.py:696-713` |
| C26 | `reconcile_generations` 定义于 `agent/runtime/phase08.py:342`、被 `agent/runtime/__init__.py:40,118` re-export，**零调用方** | `agent/runtime/phase08.py:342,835`；`agent/runtime/__init__.py:40`；`grep -rn reconcile_generations src/ tests/ tools/` 仅上述四处 |
| C27 | `general_agent.py` **已不存在**（`ab1222da` "retire unreachable product agent runtimes" 删除） | `git log --diff-filter=D --all -- '*general_agent.py'` → `ab1222da` |
| C28 | 根提交 `eafeb1c2`（2026-04-15）的 tree 里**已包含** `src/backend/agentchat/services/memory/`（`client.py` / `config.py` / `vector_stores/` 等）→ 「加入时系统已存在」有**独立于文档的、git 可核的代码证据** | `git ls-tree -r --name-only eafeb1c2` |
| C29 | `architecture.md` 头部注释为 `status: normative-target` / `architecture_state: ACCEPTED_TARGET` / `overall_architecture_state: ROUND_02_FROZEN`；ADR-0005 `status: accepted` / `date: 2026-07-18`，**无 approver 字段** | `docs/architecture/architecture.md`（头部 HTML 注释）；`docs/decisions/0005-...md:3-4` |
| C30 | 两条 fusion 之外，`mark_ready` 结论不被检索路径读取；索引/图可用性读的是配置常量或读侧兜底 | `platform/database/knowledge/domain.py:296`；`api/services/knowledge.py:754`；见 C09 |

### 7.2 Target —— 已接受的设计，代码**没有**实现

| # | Target | 依据 | 为什么是 Target 不是 Current |
| --- | --- | --- | --- |
| T01 | 官方 LangGraph `PostgresSaver` 为唯一 checkpoint 基础 | `docs/decisions/0005-...md`（status: accepted）；ADR 合规实现在 `agent/runtime/phase08.py:36-56` | 主路径 `agent/runtime/graph.py:14-20,75` 用的是自研桥，`graph.compile()` 不传 checkpointer；phase08 零功能调用方 |
| T02 | 三层运行图 / 不可变 `PlanVersion` / Replan Barrier / Domain matching Receipt recovery | `docs/modules/runtime/README.md:103` **自认仍是 Target/Gap** | 见 C13 |
| T03 | Memory recall / revocation lifecycle 归 Security/Governance，消费者只读当前 eligible 快照 | `docs/project/reference.md:51`；`docs/modules/reference.md:247-248`（invariant 13/14） | 见 C11：读侧有、写侧无 |
| T04 | Memory↔Domain 冲突时 Domain 为准 | `docs/project/reference.md:51` | 代码里无裁决点 |
| T05 | 「已判定不存在」的负证据/完整性判定层 | `docs/modules/knowledge/README.md`（列为 Gap）；代码只有 `coverage_ratio` + `stop_reason`（`evidence_ledger.py:58-86`）+ 固定 abstain 文案（`synthesis/grounded_answer.py:87`） | 语义缺一层 |
| T06 | 引用可点开定位 / 旧引用重定向 / 切分由配置驱动 | `SourceSpan` 存了字符区间（`knowledge/ingestion/contracts.py:53-69,295-331`）；但 UI 无点击处理器、旧引用只置 `REJECTED`、`ingestion/router.py:15,579,583` 用 240 硬切无 overlap | Current 只有数据位，没有可用链路 |
| T07 | Product Approval flow / formal Budget owner admission | `docs/evidence/README.md`（`PRODUCT APPROVAL FLOW: NOT IMPLEMENTED`、`PSC-C DEFERRED_BY_SCOPE`） | 明确 NOT IMPLEMENTED / DEFERRED |
| T08 | 「不设全局绿灯」的就绪语义 | `docs/modules/knowledge/README.md:27`；`docs/modules/reference.md:236`（invariant 2） | 见 C09：读路径缺省即绿 |
| T09 | 物理服务拆分 / 独立 Worker | `docs/decisions/0012-...md`（evidence-gated；默认 `Python Modular Backend`） | 当前无证据，不拆 |
| T10 | 常驻收敛任务（对账升级 / async job 超时） | 语义在 C04 建模，需一个驱动 | 见 C06：驱动不存在 |

### 7.3 Evidence —— 有可复核指针的事实

| # | Evidence | 出处 |
| --- | --- | --- |
| E01 | `SELECTED CODE VERIFICATION @ 5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660` / run `35516807526` / `224 passed, 32 warnings` | `docs/evidence/README.md` |
| E02 | PSC-A run `35071244101` / PSC-B run `35121830478` / PSC-D run `35202465804`：composition root、Security owner fact、approval projection ownership | 同上 |
| E03 | Slice C 负向 #201 / run `34559517466`、#205 / run `34560692093` 已分别由 AUTH-A `18e49733…`、AUTH-B `2f709ec9…` 收口，进入 main regression | `docs/evidence/current-test-baseline.md:162,244`；`docs/evidence/README.md:60-62` |
| E04 | #203 / run `34560042535`：pre-send SecurityEpoch 撤销 fail closed（**test seam 用裸 SQL 改状态**） | 同上 |
| E05 | PF-031：baseline `Recall@5=1.00 / MRR@10=0.90`，local `Recall@5=0.80 / MRR@10=0.80`；同日 rerun local 恢复 `Recall@5=1.00 / MRR@10=1.00`；**且 baseline 自身 MRR@10 也从 `0.90` 变为 `1.00`**，并明文禁止制造精确单机制收益百分比 | `docs/governance/project-fact-provenance.md:92,96` |
| E06 | `PRODUCTION_READINESS: NOT_ESTABLISHED` / `QUALITY: not_yet_proven` / `FULL CI: NOT RUN / NOT ESTABLISHED` / `COURT QA: UNKNOWN / NOT AVAILABLE` | `docs/evidence/README.md` |
| E07 | PF-032：`77346758`（2026-04-15）移除 nested Agent-as-Tool 与 selector 脚手架；`0b5fb350`（2026-04-28）修 custom MCP 自递归 + 高德天气参数抽取，并新增 direct-route / config gate regression test artifact；**但这两个 SHA 没有恢复 PR-triggered Actions run** | `docs/governance/project-fact-provenance.md:64,80-84` |
| E08 | 权威文档已划定「精确个人闭环 → Unknown unless separately recovered」；`docs/project/README.md:142,146,148,156` | 两份 notes 已复核，我复核一致 |
| E09 | `effect-security-slice-c-review.md` 头部第 4 行**有** `superseded_current_evidence: main@9b7891c6… / run 35053215987` | 第一轮 S13 的指控不成立，本轮不重报 |

### 7.4 Unknown —— 证据不足，**必须**保持 Unknown

| # | Unknown | 为什么不能填 |
| --- | --- | --- |
| U01 | GraphRAG 每一条启发式的独立增量收益 | ablation `BLOCKED_PENDING_DATA`（`docs/governance/rb019-graphrag-ablation-protocol.md:5`）；`docs/evidence/current-eval-baseline.md:3` = `MEASUREMENT_BLOCKED` |
| U02 | Memory / Context 的 A/B 对照 | 未做；被 `QUALITY: not_yet_proven` 覆盖 |
| U03 | 5-query smoke 的选样规则、原始报告 | 选择规则 Unknown；raw reports 在 gitignored 目录 |
| U04 | 历史 Pilot 的规模 / 题集 / 时长 / 指标 | `PF-018..PF-022` 全部 UNKNOWN / NOT_RECOVERED |
| U05 | 个人 PR / 接口 / SQL / bug 的精确闭环 | `docs/project/reference.md` 明确划为 Unknown |
| U06 | 四张只写不读表的「未来读者是否存在」 | 无记录 |
| U07 | **中文法律 query 上英文 bridge/genealogy 线索的实际误伤率** | **从未被测**（本轮新增缺口，见第 8 节 M5） |
| U08 | `escalate_due_reconciliations` 一旦接上驱动后的真实行为 | 无驱动即无观测 |
| U09 | 生产侧是否曾真的撤销过一个 epoch | 唯一路径在测试裸 SQL（E04） |
| U10 | 完整历史技术栈、真实法院质量、SLA / QPS / HA / DR | `PF-021/PF-022` UNKNOWN |

**跨层纪律检查（我自己做的）：** 我没有把 U 层任何一条写成 Cost/收益数字；
我没有把 T 层任何一条写成 Current；我没有把 E 层的 `224 passed` 写成「全量 CI 通过」
（证据文档自己写 `FULL CI: NOT RUN`）。

---

## 8. 还缺什么 measurement

**只给可执行的最小测量方案，且标注「今天能不能跑」。** 全部为可证伪实验，不产生收益数字。

### M1 —— 就绪三态回归（今天可跑，零新数据）
把 `retrieval/planner.py:91`、`retrieval/orchestrator.py:861`、`rag/handler.py:486`、
`application/knowledge/query_service.py:155-156` 的 `or "ready"` 改为 `or "unknown"`，
消费点把 `unknown` 视为不可用。**新增一条断言**：探活缺失时，检索**不**启用图路径。
**今天就会红**（因为改之前是 `or "ready"` → 图路径仍启用）。这一步同时是修复，测量与修改合一。

### M2 —— 调用图门禁（今天可跑，零新数据）
在 `tests/repo/` 加一个测试：统计 `src/backend/zuno` 中「public class/function 无外部 caller」
的数量，并设一个**上限基线**，防止「写了没接线」继续增长。这与仓库既有的 repo-gate 风格一致
（`tests/repo/test_agent_system.py` 已经在做「某文件必须不存在」这类结构性断言）。
**这是把第 6 节的一次性清理变成常设约束的唯一可执行办法。**

### M3 —— Memory 跨案击穿实验（今天可跑，零新数据）
构造同 `user_id` + 同 `workspace_id` 下两个案件（case A / case B）的 fixture，
写入 A 的 task summary，然后在 B 的上下文组装中断言 **B 的 context 不含 A 的 summary**。
**我预期今天 FAIL**（因为 scope 里没有案件维度，`layers.py:43-47`）。
这条实验直接把 P2/F1 从「我认为」变成「可复现证据」。**这是本轮性价比最高的一条测量。**

### M4 —— UNKNOWN 收敛可达性实验（今天可跑，零新数据）
构造一条 `status="OPEN"` 且 `age > age_escalation_after_seconds` 的 reconciliation 行，
断言**存在一条非测试路径**能把它推进 `MANUAL_ASSESSMENT`。
**我预期今天 FAIL**（C06：零非测试调用方 + 零调度器）。给出 P3 的可复现证据。

### M5 —— 英文线索对中文法律 query 的影响（今天可跑，需构造小样本）
不改系统，只加一个**离线对照**：取一批中文法律 query，比较
(a) 现状 vs (b) 禁用 `BRIDGE_RELATION_CUES` / `GENEALOGY_RELATION_CUES` /
`QUERY_ENTITY_PHRASE_PATTERN` 后的 top-k 变化。
**关键：这条不需要 holdout 也能做 kill 判断**——它测的是「英文线索是否**改变**了中文法律 query
的排序」，不是「提升了多少」。若排序根本不变 → 这批词典是纯死重量，删之无需 ablation。
若排序变了但方向不定 → 才有资格谈 ablation。**这一条同时回答 U07 和第 3 节 F7。**

### M6 —— 测量口径必须冻结「baseline 自身漂移」（今天可跑，零新数据）
把 E05 那条事实写成 eval 报告的**必填字段**：任何「修复前后」对比，**baseline 必须在同一
同批次样本上前后各测一次**。理由已经在 canonical 里写明（`project-fact-provenance.md:96`：
baseline 的 `MRR@10` 在 rerun 中也从 `0.90` 变为 `1.00`）。
**没有这个字段，任何「修复超 baseline」的读数都不可解释**——Red **Part A** §4 抓到过这个矛盾
（它的观察对、定性错；该处已被 Red Final 自行修回，见 0.1b 与 9.3 前置说明二）。

### M7 —— 授权门的租户传播实验（今天可跑，零新数据）
断言两个不同 tenant 的 principal **不能**互相读取对方经 `config_id` 定位的 per-user MCP 配置。
**我预期今天 FAIL**（C15）。给出 P5 的可复现证据。

### M8 —— 已冻结但缺数据的那一条（今天**不能**跑）
GraphRAG leave-one-out ablation：协议已冻结（`rb019-graphrag-ablation-protocol.md`），
缺的是 holdout 数据。**不要在没有数据时把它写成"待做"以外的任何状态。**
在 M5 给出「英文线索是否有效」之后，才值得为它准备数据。

**优先级：M3 → M4 → M1 → M7 → M5 → M2 → M6 →（阻塞的 M8）。**
前四条都是零新数据、当天可跑、预期今天就是红的——**这是本轮最该立刻执行的四条。**

---

## 9. Findings

分类标签口径：只有 **Owner / Authority / State / Contract / Recovery / Security / Build-Buy
的因果本身不成立** 才进 `ARCHITECTURE_GAP`；系统没问题、只是讲不清的进
`NARRATIVE_GAP` / `SIMULATED_RESUME_GAP`（`proposed_change: none`）；
设计写了代码没有的进 `IMPLEMENTATION_GAP`，如目标层标 `Target`。

### 9.1 架构侧（本轮的判决）

| ID | Finding | 标签 | 源码依据 |
| --- | --- | --- | --- |
| F-01 | 「就绪/健康」事实有三个所有者（配置模板常量 / DTO 缺省 / 读路径兜底）外加两处硬编 `True`，真正的判定链 `mark_ready` 结论不被任何消费点读取 → 单一写入点不存在 | `ARCHITECTURE_GAP`（Authority） | `api/services/knowledge.py:53-55,73-74`；`api/dto/knowledge.py:70-72,109-110`；`retrieval/planner.py:91`；`retrieval/orchestrator.py:861`；`rag/handler.py:486`；`application/knowledge/query_service.py:155-156`；`agent/planning.py:43`；`product/runtime_engine.py:2862`；`platform/database/knowledge/domain.py:296`；`api/services/knowledge.py:754` |
| F-02 | 读路径 default-open：探活缺失被解释成健康（`or "ready"` + `graph_available=True`），与系统自述「不存在全局绿灯」直接矛盾 | `ARCHITECTURE_GAP`（Contract / fail-open） | 同 F-01 的读路径四处 + `agent/planning.py:43` + `runtime_engine.py:2862`；反证 `docs/modules/knowledge/README.md:27` + `docs/modules/reference.md:236`（invariant 2） |
| F-03 | 权威文档声明 `MemoryScope equality != Authorization`，但实现里 scope 4 维相等是**唯一**闸门；`project_id == workspace_id` 使同 user 同 workspace 的两个案件在 scope 上不可区分 | `ARCHITECTURE_GAP`（Contract） | `docs/modules/reference.md:86`；`platform/services/memory/layers.py:43-47,284-291`；`memory/store.py:312-338`；`agent/runtime/nodes/core.py:485-491` |
| F-04 | 已声明「冲突时 Domain 为准」（`project/reference.md:51`），代码里没有裁决点 | `ARCHITECTURE_GAP`（State） | `docs/project/reference.md:51`；`platform/services/memory/runtime_batch.py`（`ConflictRecord` 无调用方） |
| F-05 | durable UNKNOWN 的 900s 升级窗口**没有驱动**；`escalate_due_reconciliations` 与 `timeout_due_async_jobs` 零非测试调用方，全仓无调度器 → 常驻收敛任务这一类机制在设计里缺席 | `ARCHITECTURE_GAP`（Recovery） | `invocation_gateway.py:1607,1614`；`platform/database/tool_runtime/domain.py:1188,1206`；调用方仅 `tests/capability/test_tool_effect_postgres_boundary.py:211,308,389`；调度面 grep 零命中 |
| F-06 | 产品动作授权门把 `tenant_id/workspace_id` 写死为 `"system"`，签名里没有租户入参 → 该层在类型上取不到租户范围 | `ARCHITECTURE_GAP`（Security） | `api/services/security_admin_actions.py:21-49`（`:26-27`） |
| F-07 | 承载 `APPCODE`/API Key 的 per-user MCP 配置，GET/DELETE 仅凭 `config_id`，无对象级归属校验；仅 `/test` 路由做权限校验 | `ARCHITECTURE_GAP`（Security） | `api/services/mcp_user_config.py:121-125`；`api/v1/mcp_user_config.py:42,50-60,81-91` |
| F-08 | 同一「融合排序」语义有两份实现（产品侧 tuple 策略 / agentic 侧 RRF k=60），**两条都在活路径上**；跨模块契约未声明二者关系与各自 profile | `ARCHITECTURE_GAP`（Contract） | `retrieval/fusion.py:1065`；`retrieval/orchestrator.py:80`；`rag/handler.py:529`；`graphrag/query_service.py:141`；`knowledge/agentic_graphrag.py:876`；`knowledge/agentic/runtime.py:393`；`product/runtime_engine.py:3163` |
| F-09 | 已接受 ADR-0005（官方 `PostgresSaver` 为唯一基础）与在跑的主路径（自研 checkpoint 桥）互为反例，且有一条测试守护这条分裂（断言 cutover 文件必须不存在） | `ARCHITECTURE_GAP`（Authority / 已接受决策未收口） | `docs/decisions/0005-...md`；`agent/runtime/graph.py:14-20,75`；`agent/runtime/phase08.py:36-56`；`tests/repo/test_agent_system.py:36` |
| F-10 | 出站效果工具关闭 TLS 证书与主机名校验，同时携带 `APPCODE` 凭据 | `ARCHITECTURE_GAP`（Security，实现级具体缺陷） | `capability/tools/delivery/action.py:41,47-49` |
| F-11 | 生产侧没有任何代码路径会撤销一个 epoch；唯一把 status 改成 revoked 的路径在测试裸 SQL 里 → 该 fail-closed 分支在生产未验 | `ARCHITECTURE_GAP`（Security） | 撤销态唯一写入在测试 seam（`docs/evidence/current-test-baseline.md` #203 / run `34560042535`） |
| F-12 | 运行时控制面整组执行器无外部 caller、无测试：`ReplanBarrierExecutor` / `JoinControlDecisionEngine` / `ParallelRecoveryPlanner` / `Phase21CrashRecoveryMatrix` / `DynamicStepWorker` / `BranchResultFencer` / `RESEND_OUTBOX` 执行点 / `append_plan_version` | `IMPLEMENTATION_GAP`（Target = T02） | `planning/replan_barrier.py:159`；`control_decision.py:98`；`recovery.py:12,91,176`；`dynamic_worker.py:53`；`branch_result.py:81`；`sqlite_store.py:318`；`tests/` 零命中 |
| F-13 | `plan_version` 恒为字面量，live replan 不递增版本 → 晚到结果无法被判定 stale | `IMPLEMENTATION_GAP`（Target = T02） | `agent/runtime/service.py:315,323,331`；`planning/replan.py:39-45`；`contracts.py:392` |
| F-14 | 四张 memory 审计表只写不读（表名各只出现一次且都是 INSERT，`FROM <表>` 全仓零命中，连测试都没有） | `IMPLEMENTATION_GAP`（审计面；Target 未声明 → 需显式决策） | `platform/database/memory/domain.py:110,171,313,326,333,348,383,486`；`FROM context_pack_versions/memory_use_traces/memory_candidates_v2/memory_snapshots` 零命中 |
| F-15 | memory 撤销/失效**没有生产写入方**；已构建注入过的 context pack 不失效不回滚；task summary 无版本/`updated_at`，读取按 `created_at` 取首条非空 | `IMPLEMENTATION_GAP`（Target = T03） | `memory/engine.py:1021,1054-1064`；`layers.py:90-115`；`memory/store.py:328`；写入方仅 `tests/memory/test_context_pack_engine.py:140-142` |
| F-16 | 「撤销是否回溯已构建的上下文」在文档里**没有答案** | `ARCHITECTURE_GAP`（State，语义未定） | `docs/project/reference.md:51`；`docs/modules/reference.md:247` 无该语义 |
| F-17 | 「已判定不存在」的负结论层不存在；只有 `coverage_ratio` + 4 类 `stop_reason` + 固定 abstain 文案，词面子串比对承担 unsupported-claim 检查 | `IMPLEMENTATION_GAP`（Target = T05） | `knowledge/agentic/evidence_ledger.py:58-86`；`corrective.py`；`agent/runtime/synthesis/grounded_answer.py:87` |
| F-18 | 英文 HotpotQA 词典（`ENTITY_STOPWORDS` / `BRIDGE_RELATION_CUES` / `GENEALOGY_RELATION_CUES`）与 9 个无来源标注的硬编阈值，无条件生效于检索融合，包括中文法律路径 | `EVIDENCE_GAP`（在中文法律 query 上的实际影响从未被测 → M5） | `retrieval/fusion.py:8-60,240,268,344-349,356,373,492,505,633` |
| F-19 | `RuntimeLimits.timeout_ms` 是死字段（声明无读取点）；`agent_id` 硬编 `"agent_run"` 无消费方 | `IMPLEMENTATION_GAP` | `agent/runtime/contracts.py:61`；`agent/runtime/nodes/core.py:488` |
| F-20 | 本轮 `04_red_evaluation.md` 与 Blue 架构收口**并行**完成（开工时 manifest `red_evaluation_status: NOT_STARTED`，收尾时文件已出现且未跟踪）；我按内容先以 Part A 为判据、到位后重写 9.3 | `NO_ZUNO_CHANGE`（本轮 workflow 产物时序问题，`proposed_change: none`，action → Controller：终评应在 Blue Reflection 之前冻结） | `00_manifest.yaml:129`；`00_artifact_links.md:27`；收尾 `git status` 显示 `?? 04_red_evaluation.md` |
| F-21 | 「同一 Agent 实例跨用户复用会串」这个不变量，**今天由构造点隐式维持**：`self.user_id` 在构造时冻结（`simple_agent.py:280-285`），而实例是**每请求新建**的（`api/services/workspace.py:149,321` 的 `build_simple_agent` 是 `@staticmethod`、`WorkSpaceSimpleAgent(user_id=login_user.user_id, ...)`，无缓存 / 无单例）。**但没有任何测试断言"实例不被跨请求复用"**——这个安全前提今天无守卫 | `EVIDENCE_GAP`（不变量无测试固定；非 Current 缺陷） | `platform/services/workspace/simple_agent.py:280-285,1374-1401`；`api/services/workspace.py:149,162-186,321`；`grep -rn "_agent_cache\|lru_cache\|singleton" api/services/workspace.py` 零命中 |

### 9.2 非架构侧（改措辞 / 归属 / 材料，不改代码 → `proposed_change: none`）

| ID | Finding | 标签 |
| --- | --- | --- |
| N-01 | 简历第 1 条「收紧 Workspace Tool 路由 / 用回归测试固定路由边界」在代码里**无对应物**：`direct_route` 字面量只出现在一个测试函数名（`tests/agent/test_workspace_simple_agent.py:16`），**没有任何断言说「多步 query 应回落 ReAct」**。措辞过强 | `SIMULATED_RESUME_GAP` |
| N-02 | A60 转述 PF-031 时**丢了边界句**（baseline 的 `MRR@10` 自身也从 `0.90` 漂到 `1.00`），读起来像「保位改动反超 baseline」。系统口径**是自洽的** | `NARRATIVE_GAP` |
| N-03 | 历史归属空窗（第一笔改动 / 逐行 blame / 哪条 bullet 该删）：`docs/project/reference.md` 已划定「精确个人闭环 → Unknown unless separately recovered」 | `NARRATIVE_GAP` |
| N-04 | Pilot / 法院定性：文档比简历更保守（`COURT QA: UNKNOWN`、`court` 在 src 零命中），问题在简历措辞 | `NARRATIVE_GAP` |
| N-05 | 材料引用路径错：候选人把负向历史 #201/#203/#205/#207 归到 `docs/evidence/implementation-wave-001.md`，正确出处是 `docs/evidence/current-test-baseline.md` | `DOC_GAP`（候选材料） |
| N-06 | `docs/modules/security/README.md` 的 Gap 段仍写 production `WorkspaceRuntimeComposition` / `SecurityDecision resolver binding` 尚未建立 Current proof，而 `main.py:59-115` 已绑定、evidence 已标 PSC-A/B `SELECTED VERIFIED` | `DOC_GAP` |
| N-07 | `rb019-graphrag-ablation-protocol.md` 的 `source` 出身是**评测轮次产物**（`red-blue rb-2026-09-15-formal-019 / IMP-019-05`），而 `owner` 是 03/09。缺一句「数据到位前决定权归 architect」 | `DOC_GAP` |
| N-08 | 两处候选自认**与源码不符**：A10/A77 说 `MCPLangChainToolAdapter` 是「可删壳」，但它有真实消费方（`simple_agent.py:1340`、`wechat_agent.py:102,209`）；A54 说 `multi_agent_enabled`「没有任何 reader」，但它有 reader（`product/runtime_batch.py:428`，且候选人自己已在 Wave 2 撤回 A54） | `NARRATIVE_GAP` |

### 9.3 Red Final 判错清单（我**独立**回源码核过；**共 4 条**）

**前置说明一（范围与时序）。** Red Final（`04_red_evaluation.md`）与我并行完成，见 0.1。
它是**盲的**（`not_seen: canonical docs, src, tests, Evidence`），并且**自己诚实地声明**了这一点——
§6 第 1 条写着「任何一条 `file:line` 我都无法核实……我这一整份评估的『实现层』结论，
都是在**评价他说得可不可信**，不是在评价**他说得对不对**」。
**正因为它盲，下面 4 条全部属于同一类型：Red 只能按候选人的转述判断，而源码给出相反或更窄的事实。**

**前置说明二（不重报 Part A 的错误）。** 我本文件先前版本列的是 Wave-2 **Part A** 的 6 处判错
（审计口径不均匀 / 两套融合哪套是死代码 / abstain 未接线 / 负向历史性质 / A11-A60 定性 /
`multi_agent_enabled` 无 reader）。**这 6 处在 Red Final 里已被它自己修回**：候选人把源码事实
当面喂回去之后，Red Final §3 明确写出反例（`assert_audit_durable_for_effect` 活、abstain 活、
`citation_eligibility='REJECTED'` 活、memory 版本 CAS 活），并把 Implementation 维度标为
`NARRATIVE_GAP + UNVERIFIED_BY_BLIND_RED`，注明「这是 Blue 架构侧的权限」。
**所以本轮的「Red 抓错」以 Red Final 为准，共 4 条。**

| # | Red Final 的判断 | 为什么错 | 源码依据 |
| --- | --- | --- | --- |
| **R1** | §1「Wave 2 里**新挖出的洞**至少有五个：`user_id=self.user_id` 是**实例冻结**而非请求级（A104/A106）」；§3 Failure 把它列为「他自己新发现的失败窗口」；§5 F03 标 `FUNDAMENTAL_GAP`；§6.7 称「**这是他自挖的最硬的一个洞**」 | **候选人的原话带前提，Red 把前提丢了。** A104 原话：「同一用户同一会话没问题；**同一实例被不同用户复用才会串——而那取决于实例怎么来**」。源码给出答案：实例**每请求新建**——`build_simple_agent` 是 `@staticmethod`（`api/services/workspace.py:149`），在请求处理里构造 `WorkSpaceSimpleAgent(user_id=login_user.user_id, ...)`（`:321` → `:162-186`），**无缓存、无单例**（`grep _agent_cache\|lru_cache\|singleton` 零命中）。→ **「同实例跨用户复用」这个前件在当前代码里不可达**。它不是洞，是一个被**正确 hedge 过**的观察。**Red 把「可能」升格成了「洞」。** 其中真实且我认领的那一半另立为 F-21（该不变量无测试固定） | `platform/services/workspace/simple_agent.py:280-285,1388,1397`；`api/services/workspace.py:149,162-186,321`；`04_blue_wave2_answers.md:47` |
| **R2** | §5 F18：「『既有系统』这个前提本身没有独立历史……**3 月已存在这件事的唯一依据是 `docs/project/reference.md` 的一句话，独立可核性 = 0**」 | **有独立于文档、且 git 可核的证据。** 根提交 `eafeb1c2`（2026-04-15）的 tree **已包含** `src/backend/agentchat/services/memory/`（`client.py` / `config.py` / `vector_stores/` 等）——一个候选人不是从零写、后来被 `89249291 Retire agentchat compat namespace` 退役的**既有子系统**。同页 canonical（PF-032）还记录 `77346758` **父提交**里 `GeneralAgent` 仍带 `tool_invocation_model` / `available_tools` / `LLMToolSelectorMiddleware` 与 MCPAgent-as-Tool 脚手架。**这两条是代码事实，不是文档句式。** 而且 Red 在 §7 又承认「唯一凭证是那笔 diff 的 **before 一侧**」——**前后自相矛盾**：before 一侧本身就是独立可核的 | `git ls-tree -r --name-only eafeb1c2`（`src/backend/agentchat/services/memory/...`）；`docs/governance/project-fact-provenance.md:64,80-84` |
| **R3** | §5 F14：「ADR 明确『不批准永久 **dual** checkpointer runtime』，而**主线恰是 dual**（自研桥在跑、官方 saver 只挂在无生产 caller 的 `phase08.py`）」 | **不是 dual，是「一条活的 + 一条不可达的」。** 主路径 `agent/runtime/graph.py:75` 的 `graph.compile()` **不传 checkpointer**（函数 `:14` 收 `checkpointer` 参数，但 `:17` docstring 明写「是 Zuno 的领域 checkpoint 桥，**不是** LangGraph `BaseCheckpointSaver`」）→ LangGraph 官方 checkpointer 在主路径上**根本没有被激活**；官方 saver 只在 `phase08.py` 存在且零功能调用方。ADR-0005 禁止的是**同时运行两个** checkpoint runtime，这里是**一个在跑 + 一个死实现**。Red 的**核心指控成立**（ADR 明文与实现分裂 → 我已立为 F-09），但 `dual` 这个词用错了——而 `dual` 恰是 ADR 里的**禁用术语** | `agent/runtime/graph.py:14-20,75`；`agent/runtime/phase08.py:36-56`；`agent/runtime/__init__.py:22,40`（仅 re-export）；`docs/decisions/0005-...md` |
| **R4** | §1「GraphRAG 的退出条件挂在一份**面试流程产物**上」+ §5 F11「他唯一诚实的复杂度举证策略，**本身没有工程侧的落点**」 | **前半对，后半过强。** 前半我复核成立（`source: red-blue rb-2026-09-15-formal-019 / IMP-019-05`，`:7`），已立为 N-07。但「没有工程侧的落点」不成立：该协议有 **canonical 的配套 Evidence 文档**（`docs/evidence/current-eval-baseline.md`，状态 `MEASUREMENT_BLOCKED`）与**明确的模块 owner**（`:6` 写 `03 Knowledge & Evidence + 09 Observability & Evaluation`），且冻结在 main `5844fe59`（`:9`）。**真实缺陷比 Red 说的窄得多**：问题只是「这个问题的**定义**来自评测轮次」，不是「它没有工程载体」。Red 把一行治理注释问题放大成了「举证策略失去落点」 | `docs/governance/rb019-graphrag-ablation-protocol.md:5,6,7,9`；`docs/evidence/current-eval-baseline.md:3` |

**一句话：Red Final 比 Part A 准得多。它剩下的 4 处错误全部来自「盲」——**
R1/R4 是把候选人**带前提的表述**当结论用，R2 是在自己承认有 before-side 证据的同时写下
「独立可核性 = 0」，R3 是拿 ADR 的禁用术语去描述一个非 dual 的现状。
**没有一处属于「顺话」或「编造」**，这与它 §6 自列的 12 条「我仍然无法确认」是自洽的。

### 9.4 分布

```text
架构侧 (21 条)
  ARCHITECTURE_GAP  12 : F-01 F-02 F-03 F-04 F-05 F-06 F-07 F-08 F-09 F-10 F-11 F-16
  IMPLEMENTATION_GAP 6 : F-12 F-13 F-14 F-15 F-17 F-19
  EVIDENCE_GAP       2 : F-18 F-21
  NO_ZUNO_CHANGE     1 : F-20

非架构侧 (8 条)
  DOC_GAP               3 : N-05 N-06 N-07
  NARRATIVE_GAP         4 : N-02 N-03 N-04 N-08
  SIMULATED_RESUME_GAP  1 : N-01

Red Final 判错              : 4 条（R1–R4；均为「盲」所致）
第一轮已撤回、本轮不重报    : 1 条（S13）
```

分类口径自检：12 条 `ARCHITECTURE_GAP` 全部落在 Owner / Authority / State / Contract /
Recovery / Security（F-16 是 State 语义未定）；**没有任何一条是因为「候选人没讲清」而被归入
`ARCHITECTURE_GAP`**——那类全部在 9.2 的 `proposed_change: none` 里。
Build/Buy 维度**零条**：本轮的 5 族真问题没有一族的因果是「该买什么」，全是「自己的事实边界没收敛」。

---

## 10. 本轮架构判决（一句话）

**Zuno 的架构问题不在形态，在「事实边界没有收敛」：就绪态有三个所有者且读路径 fail-open、
授权层在类型上取不到租户、Memory 把 scope 相等当成了授权、durable UNKNOWN 的收敛驱动
在设计里整类缺席；同时 04 Runtime 的控制面与 09/03 的审计面存在两大块「写了没接线」。
这些的正确解法是删、收窄、回退，不是新增机制——除了 Memory 的案件维度与 UNKNOWN 的收敛闭环
这两处需要一个新的（很轻的）承载点。**

**对 Red：** 它的探针网很有效（「写了没接线」这一击打中了 04 控制面），
它也在被喂回源码后**主动修回了 Wave-2 Part A 的 6 处判错**，并把实现层维度诚实标为
`UNVERIFIED_BY_BLIND_RED`。但它**终究是盲的**，剩余 **4 处判断错误**（R1–R4）：
R1 把候选人**带前提的**「同实例跨用户复用才会串」升格成了洞（源码里实例每请求新建，前件不可达）；
R2 一边承认有 diff before-side 证据、一边写下「独立可核性 = 0」（根提交 tree 里就是既有子系统）；
R3 用 ADR 的**禁用术语** `dual` 去描述一个「一条在跑 + 一条死实现」的现状；
R4 把一行**测评轮次出身**的治理注释放大成「举证策略失去工程落点」（该协议有 canonical Evidence 配套与明确 owner）。
**这 4 处无一是「顺话」或「编造」，全部来自它无法看源码这一物理约束。**
**顺着它的怀疑往下写会把这 4 处错误固化成本轮的架构结论——我没有那样做；
我认领的是它背后真实的那一半（分别落成 F-09、F-21、N-07）。**
