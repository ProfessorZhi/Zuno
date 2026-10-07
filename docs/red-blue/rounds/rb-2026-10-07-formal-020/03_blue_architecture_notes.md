# Blue Wave 1 — 架构初诊（Architecture Notes）

```text
round: rb-2026-10-07-formal-020
artifact: 03_blue_architecture_notes
role: Blue Team — Architecture Reviewer
sealed: true
readable_by: Blue Architecture Reflection only
base_sha: 7d3081f2ccaa20c7eeb0bfff75206d08584a6e51
head_observed: 4d9bf767 (仅新增本轮 red-blue 文件，src/tests/infra 无漂移)

inputs:
  - docs/red-blue/rounds/rb-2026-10-07-formal-020/01_simulated_resume.md
  - docs/red-blue/rounds/rb-2026-10-07-formal-020/02_red_questions.md
  - docs/red-blue/rounds/rb-2026-10-07-formal-020/00_manifest.yaml
  - .agent/red-blue/defense-model.md
  - AGENTS.md
  - docs/README.md / docs/project/ / docs/architecture/ / docs/modules/ / docs/decisions/ / docs/evidence/ / docs/governance/
  - src/backend/zuno/** , tests/** , tools/**

not_read: 03_blue_answers.md（隔离实例同时生成）；docs/red-blue/ 下任何历史 round
judgement_target: 系统本身是否存在这个洞（不评候选人措辞质量）
```

判读口径：Red 的 100 题是一张探针网。这里记录的是**它先扫到的那批系统断点**——
即「Zuno 真的有这个东西，但它今天要么没解释清、要么没实现、要么只存在于 Target」的坐标。
`gap_type = ANSWER_GAP` 表示系统成立、只是表达/归属需要澄清，`proposed_change` 一律写 `none`。
所有量化收益均为 `Unknown`（不制造数字）。

---

## 信号汇总

| # | signal（一句话） | fact_layer | gap_type | priority | 触发题号 |
|---|---|---|---|---|---|
| S01 | 「Ready」存在第二个所有者：`DEFAULT_KNOWLEDGE_CONFIG` 直接写字面 `"ready"`，与 `mark_ready` 的严格判定、以及文档「平台不存在全局绿灯」的说法三方矛盾 | Current | SYSTEM_GAP | P0 | Q82, Q81, Q74 |
| S02 | 系统无法证明「全案里没有这个信息」：只有 coverage_ratio 与固定 abstain 文案，不存在完整性 / 负证据判定层 | Current | SYSTEM_GAP | P0 | Q85, Q89 |
| S03 | Memory scope 只有 user/agent/project/thread，缺案件/事项维度，且 Memory↔Domain 冲突无裁决权 → 同一 user scope 下跨案互读 | Current | SYSTEM_GAP | P0 | Q25, Q28 |
| S04 | 授权层不完整：产品动作门把 tenant/workspace 硬编码为 `"system"`；per-user MCP 配置 CRUD（承载 APPCODE/API Key）无归属校验，GET/DELETE 仅凭 `config_id` | Current | SYSTEM_GAP | P0 | Q4, Q41, Q42, Q49 |
| S05 | 运行时与**已接受**的 ADR-0005 分叉：主路径是自研 `RuntimeGraphCheckpointer`（`graph.compile()` 不传 checkpointer），ADR 要求的官方 `PostgresSaver` 实现（`phase08.py`）未接线 | Current | SYSTEM_GAP | P1 | Q39, Q40, Q77 |
| S06 | 计划版本与「晚到结果」围栏在 Current 不可达：`PlanState.plan_version` 恒为字面量，`runtime/planning/` 的 fencing / barrier / join / recovery 全部无调用方 | Current | SYSTEM_GAP | P1 | Q33, Q34, Q35, Q72, Q73 |
| S07 | 未确认的副作用不会自动升级/对账：`escalate_due_reconciliations` 没有任何非测试调用方，无调度或定时器接入 | Current | SYSTEM_GAP | P1 | Q47, Q48 |
| S08 | 引用可用性链路未完成：无点开/定位 UI；旧版本引用只置 REJECTED 不重定向；长 unit >240 字符硬切且无 overlap（与配置 1024/120 不一致） | Current | SYSTEM_GAP | P1 | Q83, Q84, Q88, Q89, Q90 |
| S09 | 检索融合是两套并存实现 + 硬编码阈值 + 英文 benchmark 词典（`founded by` / `maternal grandfather` / 英文 stopwords）直接进入法律检索路径 | Current | SYSTEM_GAP | P1 | Q15, Q16, Q86, Q87, Q74 |
| S10 | Memory 撤销/失效没有生产写入方，已构建的 context pack 不失效不回滚；task summary 无版本/时间戳可比 | Current | SYSTEM_GAP | P1 | Q26, Q27 |
| S11 | 出站效果工具（阿里云物流）关闭 TLS 校验（`check_hostname=False` + `CERT_NONE`），同时携带 APPCODE 凭据 | Current | SYSTEM_GAP | P1 | Q48 |
| S12 | 文档与 main 脱钩：`docs/modules/security/README.md` 的 Gap 仍称 production composition / SecurityDecision binding 未建立，而 `main.py` 已绑定；`phase08.py` 这条 ADR 合规路线在全部文档中无任何记载 | Current | DOC_GAP | P1 | Q41, Q49, Q77 |
| S13 | `effect-security-slice-c-review.md` 自宣 `SUPERSEDED` 却未附收口 run SHA/证据，未知结果 restart-replay 那条 `FAILS_TARGET` 无当前证据接续 | Historical | DOC_GAP | P1 | Q45 |
| S14 | per-user MCP 配置按请求作用域拷贝注入（`call_args = dict(args)` + 调用时解析），并发不串 | Current | NO_GAP | P2 | Q5 |
| S15 | 执行前授权新鲜度已经存在：prepared_action_hash / epoch / approval deadline 三次复核，失效即失败关闭 | Current | NO_GAP | P2 | Q43 |
| S16 | 副作用前强制持久审计已接线；未知远端结果默认 `RECONCILE`（15 分钟升级窗口），不盲重试 | Current | NO_GAP | P2 | Q44, Q46 |
| S17 | T06 个人归属边界（第一笔改动 / 逐行 blame / 哪条 bullet 该删） | Historical | ANSWER_GAP | P2 | Q51–Q60 |
| S18 | T07 Pilot / 法院定性边界（谁给的定性、有没有真实 bad case、为什么不能叫 Production） | Historical | ANSWER_GAP | P2 | Q61–Q70 |

分布：`SYSTEM_GAP` 11 / `DOC_GAP` 2 / `NO_GAP` 3 / `ANSWER_GAP` 2 = 18。

---

## S01 — Knowledge「Ready」的第二个所有者：配置模板里的字面 `"ready"`

```text
signal: DEFAULT_KNOWLEDGE_CONFIG 在代码里直接把 health_status / text_index_status /
  bm25_index_status / graph_index_status 写成字面字符串 "ready"（community_detection_status
  写 "not_built"）。它不读 knowledge_domain_versions.mark_ready 的判定结果，也不读任何索引
  探活。于是「Ready」同时有两个所有者：领域侧的严格判定链路，和配置模板里的常量。
source_check:
  - src/backend/zuno/api/services/knowledge.py:16-90（DEFAULT_KNOWLEDGE_CONFIG，index_settings
    :52-57、graph_index_settings :73-75 的 "ready" 字面量）
  - src/backend/zuno/platform/database/knowledge/domain.py:296-320（mark_ready 要求 ≥2 类可见索引）、
    :322-352（create_snapshot）、:354-447（cutover）
  - docs/modules/knowledge/README.md:97-99（文档称平台不存在可替代这些判断的「全局绿色灯」）
  - docs/modules/reference.md:127 起（同一权威事实不得由两个文档声明不同所有者）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 让配置模板不再默认输出 "ready" —— 未计算过的 status 一律输出 unknown/not_built，
  只允许由 mark_ready 的判定结果单向写入；把「谁有权把没准备好改成准备好」收敛到唯一写入点，
  并让读侧在缺失判定时失败关闭（不是默认绿）。
simpler_alternative: 不新建模型，直接删除这 4 个字面量，缺失即 "unknown"。这是本轮改动量最小的
  合法解法；若产品确实需要展示态，用一个只读视图从 knowledge_domain_versions 派生。
cost_and_exit: 改动集中在一个默认值构造 + 一个读侧映射，回归面在既有的 knowledge readiness 测试。
  退出方式是恢复常量默认值；退出后回到当前的三方矛盾状态。
priority: P0
```

## S02 — 「全案里没有」无法被证明

```text
signal: 系统对「没检索到」的处理是产生 coverage_ratio 与 stop_reason（coverage_incomplete /
  strict_citation_missing / conflict_unresolved / no_evidence），再输出固定的 abstain 文案。
  没有任何机制对「语料整体是否覆盖该命题」下判断 —— 即不存在负证据/完整性判定层。「语料里
  没有 X」与「我没检到 X」在 Current 里是同一句话。
source_check:
  - src/backend/zuno/knowledge/agentic/evidence_ledger.py:45-88（coverage_ratio + stop_reasons）
  - src/backend/zuno/knowledge/agentic/corrective.py:19-49（ABSTAIN）、quality.py:6-16
  - src/backend/zuno/knowledge/agentic/grounded_answer.py:87-88（abstain 文案）
  - src/backend/zuno/knowledge/agentic_graphrag.py:470-490（unsupported-claim 检查是词面子串比对）
  - docs/modules/knowledge/README.md:99（把 negative evidence conditions 列为 Gap）
fact_layer: Current（同时是 Target 缺口）
gap_type: SYSTEM_GAP
proposed_change: 在 Knowledge 模块显式定义「负结论」的准入条件与表达契约（可判定的语料边界 +
  覆盖度门槛 + 缺失判定证据），并让输出层区分「未检索到」和「已判定不存在」两种语义；
  后者必须携带可复核的覆盖范围证据。
simpler_alternative: 先在契约层禁止输出绝对否定语句（把结论降级为「在当前检索范围内未见」），
  把判定层留到有真实 bad case 再建。这是纯契约收紧，不改检索链路。
cost_and_exit: 契约收紧可独立落地并独立回退；建判定层则要动检索与合成两侧。两种做法的收益均
  为 Unknown（没有可用的评测数据）。
priority: P0
```

## S03 — Memory scope 缺案件维度，且 Memory↔Domain 没有裁决权

```text
signal: MemoryScope 只有 user_id / agent_id / project_id / thread_id 四个维度，project_id 在
  写侧就是 workspace_id，agent_id 被硬编码为 "agent_run"。系统里不存在案件/事项这一级作用域，
  因此「同一个 user + 同一个 workspace 下的两个案件」在 scope 上不可区分，同 scope 读取足以
  把 A 案的 memory 带进 B 案的上下文。配套的 Memory↔Domain 冲突裁决在 Current 里没有接线
  （ConflictRecord / MemoryRuntimeBatch 无调用方），冲突事实没有所有者。
source_check:
  - src/backend/zuno/platform/services/memory/layers.py:42-55（MemoryScope 字段）、:284-291（应用层 scope 过滤）
  - src/backend/zuno/platform/services/memory/store.py:320,327,336,412,427-430,520-526（SQL 侧 scope 过滤）
  - src/backend/zuno/agent/runtime/nodes/core.py:485-491（scope 构造：agent_id="agent_run"、project_id=workspace_id）
  - src/backend/zuno/platform/services/memory/runtime_batch.py:150-154,291（ConflictRecord/MemoryRuntimeBatch 未接线）
  - docs/modules/reference.md:71-107（MemoryScope equality != Authorization）、:233-254（invariant 13/14）
  - docs/project/reference.md:51（payload 不替代 Domain truth；冲突时 Domain 为准 —— 目前无实现承载）
fact_layer: Target（Current 只有更粗的 scope）
gap_type: SYSTEM_GAP
proposed_change: 在 MemoryScope 增加案件/事项维度并让读写两侧都按它过滤；同时把「同 scope」
  降级为必要条件而非充分条件（scope 相等不构成读取授权），并显式定义 Domain 优先的冲突裁决点。
simpler_alternative: 不扩 scope，改为在读取入口强制携带案件标识作为过滤参数（等价于把 scope
  加宽一列），裁决逻辑先只做「Domain 有值则 Memory 不注入」单一规则。两者都需要动读路径，
  但后者不需要改 Memory 的存储模型。
cost_and_exit: scope 变更影响存储与检索两侧，回归面覆盖 tests/memory/ 与 tests/storage/。退出方式
  是移除新增维度并恢复原 scope 相等语义。
priority: P0
```

## S04 — 授权层不完整：tenant 硬编码 + 用户配置无归属校验

```text
signal: 两处具体的授权缺口。其一，产品动作授权门 require_admin_action_authorized 把
  tenant_id / workspace_id 直接写死为 "system"，所以这一层的授权判定不带租户/工作台范围。
  其二，per-user MCP 配置（存的是 APPCODE / API Key 一类凭据）的 service 层
  create/update/delete 没有任何归属校验；DELETE 只接收 config_id，GET 也只按 config_id 返回。
  只有 /mcp_user_config/test 这一条路由调用了 verify_user_permission。
source_check:
  - src/backend/zuno/api/services/security_admin_actions.py:21-49（tenant_id="system"、workspace_id="system"，:29-30）
  - src/backend/zuno/api/services/mcp_user_config.py:65-71（create）、:82-92（update）、:121-125（delete 仅 config_id）
  - src/backend/zuno/api/v1/mcp_user_config.py:42（仅 test 路由做 verify_user_permission）、:50-60（GET by id）、
    :81-91（DELETE by body config_id）
  - src/backend/zuno/main.py:144-157（product action guard 在启动时接线）
  - docs/governance/rb019-post-implementation-review.md（剩余 gap：manually-reviewer 前缀的 authority 仍偏弱）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 给 per-user MCP 配置的读写删除补上对象级归属校验（资源属于当前 principal），
  并把 tenant/workspace 从常量改为从请求上下文解析后传入授权门。
simpler_alternative: 最小改动是让 service 层方法接受并由调用方传入已认证 principal，内部做
  owner 比对（一行断言级改动），不引入新的授权框架。
cost_and_exit: 单点改动 + 路由回归；退出方式是恢复原签名。修复收益（防住的具体攻击面）为 Unknown，
  但缺口本身是确定存在的。
priority: P0
```

## S05 — 运行时与已接受的 ADR-0005 分叉

```text
signal: docs/decisions/0005-official-langgraph-postgres-checkpointer.md 状态是 accepted，明确
  规定官方 PostgresSaver 为「唯一基础」，并要求官方 checkpoint_* 表不被替代、不批准永久 dual
  checkpointer runtime。但主路径 agent/runtime/graph.py 用的是 Zuno 自己的 checkpoint 桥
  （模块 docstring 明说「不是 LangGraph BaseCheckpointSaver」），并以 graph.compile() 编译、
  不传 checkpointer；符合 ADR 的那条实现路径在 agent/runtime/phase08.py（官方 InMemorySaver /
  PostgresSaver、phase08_postgres_checkpointer），无人调用且在任何文档里都不存在。
source_check:
  - src/backend/zuno/agent/runtime/graph.py:14-20, 75（docstring + graph.compile() 无 checkpointer 参数）、:82-96
  - src/backend/zuno/agent/runtime/phase08.py:8-11, 36-56（官方 saver 接线）、:342-433（reconcile_generations 无调用方）
  - docs/decisions/0005-official-langgraph-postgres-checkpointer.md（status accepted, 2026-07-18）
  - tests/repo/test_agent_system.py:36（断言 phase08_cutover.py 必须不存在）
  - docs/architecture/reference.md B14（L287：代码采用不同语义 = Target/Current 分叉，只有被接受的
    Architecture Revision/ADR 才能改 Target）
  - docs/modules/runtime/reference.md（全文无 checkpointer / langgraph 出现）
fact_layer: Current（与 Target 分叉）
gap_type: SYSTEM_GAP
proposed_change: 先做一次收敛决定：要么让主路径改为按 ADR-0005 使用官方 PostgresSaver（并把
  Zuno 自研桥降级为纯控制语义层），要么按 B14 提出一份明确的 Architecture Revision 把「自研桥
  为唯一基础」写进 Target。不允许现状继续：已接受的 ADR 与在跑的实现互为对方的反例。
simpler_alternative: 保留自研桥、修订 ADR-0005（记录为什么官方 saver 不满足控制语义需求），
  同时删除或明确标注 phase08.py 的归属。成本低于迁移运行时。
cost_and_exit: 修订 ADR 是文档动作、可回退；迁移运行时涉及 checkpoint 表与恢复路径，退出成本高。
两条路径的收益均为 Unknown。
priority: P1
```

## S06 — 计划版本与「晚到结果」围栏在 Current 不可达

```text
signal: 简历与 Target 都在讲「旧计划留下的动作不能被当成当前产物」。代码里这套机制的每一块
  都写完了，但没有一块在主路径上：PlanState 是进程内对象，plan_version 被赋成字面量 0/1 且
  从不递增；live replan 只改 status（model_copy）不含版本递增；Domain 侧 PlanVersion 聚合
  （aggregate_version / reject_mutation）与 append_plan_version 的持久化入口没有调用方；
  BranchResultFencer 只在 DynamicStepWorker 里被调用，而 DynamicStepWorker 本身没有调用方；
  ReplanBarrierExecutor / JoinControlDecisionEngine / ParallelRecoveryPlanner /
  Phase21CrashRecoveryMatrix / recovery.py 的侧效重放路径同样无调用方。
source_check:
  - src/backend/zuno/agent/contracts.py:380-394（PlanState）
  - src/backend/zuno/agent/runtime/service.py:301-334（plan_version 字面量 0/1，:315,323,331）
  - src/backend/zuno/agent/runtime/planning/replan.py:39-45（model_copy 改 status，不递增版本）
  - src/backend/zuno/agent/domain/task_contracts.py:344-508（PlanVersion 聚合，aggregate_version :488,502，
    reject_mutation :505-507）
  - src/backend/zuno/agent/runtime/sqlite_store.py:318-325（append_plan_version 无调用方）、:469-475（表定义）
  - src/backend/zuno/agent/runtime/planning/branch_result.py:96-105（fencing，:91 由
    DynamicStepWorker 调用，写对象存储在 :90 早于 fencing）
  - src/backend/zuno/agent/runtime/planning/recovery.py:12,218-225（RESEND_OUTBOX 未接线）
  - docs/modules/runtime/README.md:103（自带声明：三层运行图/不可变 PlanVersion/Replan Barrier/
    Domain matching Receipt recovery 仍是 Target/Gap）
fact_layer: Target（Current 只有围栏之后才可达的一部分语义）
gap_type: SYSTEM_GAP
proposed_change: 二选一，且必须显式选。要么把版本与围栏接进主路径（最小可用形态是：plan_version
  由 Domain 单调递增并随步骤传播，围栏在结果到达时判 stale），要么把它们从 Target 文档中降级为
  「已识别但当前不采用」，并停止在简历/设计里当作既有能力描述。
simpler_alternative: 不做完整三层运行图，只落「单调整数版本 + 到达时 stale 判定」这一个判定点，
  其余 barrier/join/matrix 先删或归档。这能去掉最大一块无人调用的代码。
cost_and_exit: 接线会改动 runtime 状态机与恢复路径，回归面覆盖 tests/agent/runtime/。删除路线
  可随时从 git 恢复，但它等于承认当前 Target 与实现之间的距离。
priority: P1
```

## S07 — 未确认的副作用不会自动升级/对账

```text
signal: 副作用进入未知状态后，系统写入 durable UNKNOWN、next_action="RECONCILE"、
  age_escalation_after_seconds=900，并把 escalate_due_reconciliations 作为升级入口。但该方法
  在仓库里只有测试与自身定义两处引用，没有任何 cron / scheduler / worker loop / API 路由调用它。
  也就是说：对账的「持续运行」这一半不存在，未解决的 UNKNOWN 不会被自动升级为
  MANUAL_ASSESSMENT，也不会有人被通知。手动结论路径（record_manual_effect_assessment）是通的。
source_check:
  - src/backend/zuno/capability/tool_runtime/invocation_gateway.py:560-564, 612-616, 729-733, 860-864
    （status="OPEN" / next_action="RECONCILE" / age_escalation_after_seconds=900 字面量）、
    :1787（record_manual_effect_assessment）、:1607（escalate_due_reconciliations 定义）
  - src/backend/zuno/platform/database/tool_runtime/domain.py:862（record_effect_reconciliation）、
    :1028-1099（resolve，conclusive receipt，second-conclusion 冲突失败关闭）、:1188-1204（升级到 ESCALATED）
  - tests/capability/test_tool_effect_postgres_boundary.py:211,308,389（仅有测试调用方）
  - docs/governance/effect-remote-query-reconciliation-status.md（DEFERRED_BY_PROVIDER_CAPABILITY；
    但该状态只覆盖「远程查询能力」，未覆盖「升级计时器没有驱动」）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 给升级路径接入一个真实驱动（最小形态：按 age_escalation_after_seconds 扫描 OPEN
  行的定时任务 + 升级后的人工队列），并把它与「远程查询能力 deferred」分开记录 —— 前者不依赖
  provider 能力，是本地可完成的部分。
simpler_alternative: 不加调度器，改为在写 UNKNOWN 时同步产生一条需人工处置的记录（写时升级而非
  定时升级），语义等价且无需常驻任务。
cost_and_exit: 写时升级改动集中在一处；定时器方案需要部署面配合。退出方式是停止升级任务，回到
  现在的「记录存在但无人推进」状态。
priority: P1
```

## S08 — 引用可用性链路未完成（点开 / 旧版本 / 切分）

```text
signal: 三处叠加使「引用」在用户侧不可用。其一，Citation / CitationBinding / SourceSpan 已经把
  char_start/char_end/bbox/page 与 source_span_id 存下来了，但没有点开定位的 UI —— 工作台页面
  没有点击处理器，dashboard 的 source_span_accuracy 是占位值（null / sample_count 0 /
  missing_dataset）。其二，文档更新后旧引用只被置为 citation_eligibility="REJECTED" 或
  deleted_or_tainted，没有重定向/re-anchor。其三，切分实现与配置不一致：router.py 用
  240/1200，超过 240 的 unit 被 _split_long_unit 硬切且不带 overlap，而配置里的 chunk_size
  1024 / overlap 120 并不驱动这条路径 —— 于是点开可能落在残句上。
source_check:
  - src/backend/zuno/knowledge/agentic_graphrag.py:434-462（Citation 含 chunk_id + source_span）
  - src/backend/zuno/knowledge/ingestion/contracts.py:53-69, 295-331（SourceSpan 真实字符区间/bbox/page）
  - src/backend/zuno/agent/runtime/synthesis/citation_binding.py:16-28（source_span_id）
  - apps/web/src/pages/workspace/defaultPage/defaultPage.vue:2695-2709（无点击处理器）、
    apps/web/src/apis/workspace.ts:188-198
  - src/backend/zuno/platform/database/knowledge/domain.py:418-434（supersede）、:636-694（mark_source_deleted）、
    :696-713（strict_evidence_ids 读过滤）
  - src/backend/zuno/knowledge/provenance.py:71-133,238-254（identity 相等 + SHA-256 兜底）、:87-92（STALE）
  - src/backend/zuno/platform/services/retrieval/router.py:15-16（240/1200）、:566-580、:583-600（硬切无 overlap）、
    :504-553、:480-501、:607-613
  - src/backend/zuno/api/services/knowledge.py:52-57（配置 chunk_size 1024 / overlap 120）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 把这条链的完成条件写成显式契约并逐项补齐：引用必须可点开定位（消费已有的
  source_span）；被 supersede/删除的引用要么重定向到新锚点、要么给出明确的「依据已失效」态；
  切分实现必须由配置驱动且长 unit 切分保留 overlap。
simpler_alternative: 先只做「配置驱动 + 长 unit 保留 overlap」这一项（纯实现对齐，不碰 UI 与
  引用模型），把 UI 与重定向留到有真实使用者反馈再排期。
cost_and_exit: 三项可独立落地、独立回退；UI 一项依赖前端，另两项是后端局部改动。收益 Unknown。
priority: P1
```

## S09 — 两套融合栈 + 硬编码阈值 + 英文 benchmark 词典进入法律检索路径

```text
signal: 检索融合在仓库里有两套互不相连的实现：platform/services/retrieval/fusion.py 的
  RetrievalFusion（策略名 "baseline_preserving"，由 retrieval/orchestrator.py 消费）和
  knowledge/agentic_graphrag.py 内部的 RRF（k=60，trace 名 "local_rrf_then_score_rerank"）。
  RetrievalFusion 里九个分层/晋升阈值全部是文件内常量，代码里没有任何来源标注；同一文件里
  还硬编码了英文、且明显是 HotpotQA 形状的词典与线索：ENTITY_STOPWORDS（含 same / nationality /
  birthplace / older / younger…）、QUERY_ENTITY_PREFIX_PATTERN、QUERY_ENTITY_PHRASE_PATTERN
  （大写实体短语）、BRIDGE_RELATION_CUES（"founded by" / "father of" / "professor at" /
  "population of"）、GENEALOGY_RELATION_CUES（"maternal grandfather" / "paternal grandfather"）。
  这些常量直接位于法律场景的检索路径上，没有按 QueryClass 或语言收窄。
source_check:
  - src/backend/zuno/platform/services/retrieval/fusion.py:8-60（九个阈值 + :18-30 ENTITY_STOPWORDS +
    :36-55 BRIDGE_RELATION_CUES + :56 起 GENEALOGY_RELATION_CUES）、:156-187、:951-977、:979-1073（merge）、
    :1065（strategy="baseline_preserving"）
  - src/backend/zuno/platform/services/retrieval/orchestrator.py:1111（消费 strategy）
  - src/backend/zuno/knowledge/agentic_graphrag.py:876（RRF k=60）、:1409-1419（_fusion_trace）
  - docs/governance/rb019-graphrag-ablation-protocol.md（FROZEN_PROTOCOL / BLOCKED_PENDING_DATA；
    H1–H9 指向 fusion.py:9,179-205,1065 与 retriever.py 的 seed/alias/path 三处）
  - docs/decisions/0006-evidence-driven-agentic-graphrag.md（fusion/RRF 必须对同源族去重；
    EvidenceCandidate != Evidence）
  - docs/governance/project-fact-provenance.md PF-031（明确「不能制造精确的单机制收益百分比」）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 两套融合收敛为一套（或明确二者各自的适用 profile 并写进 Target）；把阈值与
  词典从代码常量提升为带来源标注的配置，并按 QueryClass/语言限定生效范围 —— 英文系线索不应在
  中文法律查询上默认开启。
simpler_alternative: 删除英文/家谱类词典与阈值，把融合降级为单一 baseline_preserving 路径，
  等 ablation 有数据再决定是否恢复图晋升。这是最直接的减复杂路径，且符合 Evidence 驱动的既有
  决策语气。
cost_and_exit: 删词典与降级融合是局部改动、可回退；合并两套栈要动 agentic 侧调用方。收益 Unknown
  （ablation 处于 BLOCKED_PENDING_DATA）。
priority: P1
```

## S10 — Memory 撤销/失效没有生产写入方，上下文不回滚

```text
signal: 读取侧已经有排除逻辑（review_status != APPROVED、memory_state ∈ {stale, conflict,
  revoked}、敏感标签），但没有任何生产代码写入 stale / conflict / revoked —— 目前只有测试构造
  这些状态。因此「撤销一条 memory」在生产里没有执行者，且已经构建并注入过的 context pack 不会
  失效或回滚。同时 task summary 没有版本/updated_at，读取按 created_at 排序取第一条非空，
  不存在 as_of 语义，旧 summary 与最新事实冲突时读取侧无从比较新旧。
source_check:
  - src/backend/zuno/memory/engine.py:1054-1064（_memory_exclusion_reason，含 stale/conflict/revoked 分支）、
    :1021（取第一条非空 summary）、:769,953-954,1060（sensitivity_tags）
  - src/backend/zuno/platform/services/memory/layers.py:90-115（task summary 无版本/updated_at）
  - src/backend/zuno/platform/services/memory/store.py:328（order_by created_at）
  - tests/memory/test_context_pack_engine.py:140-142（仅测试写入 stale 状态）
  - docs/project/reference.md:51-53（recall/lifecycle policy 归属 Security/Governance，消费者只用
    当前 eligible 快照 —— 目前无实现承载）
  - docs/modules/reference.md:233-254（invariant 13）
fact_layer: Target（Current 只有读取侧的半条链）
gap_type: SYSTEM_GAP
proposed_change: 定义唯一的撤销/失效写入路径（谁有权限置 stale/conflict/revoked，以及它的
  持久化位置），并明确「撤销是否回溯已构建的上下文」的策略 —— 若回溯，给出失效传播方式；
  若不回溯，把这一点写成显式的、被接受的语义。
simpler_alternative: 只做「写时撤销 + 读取侧立即排除 + 不回溯」这一种语义并写进文档，不建传播
  机制。对 task summary 先补 updated_at 一列以支持「取最新」。
cost_and_exit: 写路径 + 一列时间戳，改动小、可回退；传播机制成本高，建议本轮不做。
priority: P1
```

## S11 — 出站效果工具关闭 TLS 校验

```text
signal: 物流查询工具在发起真实出站请求时构造 ssl 上下文并显式关闭主机名校验与证书校验
  （check_hostname = False，verify_mode = ssl.CERT_NONE），同一次请求头里携带 APPCODE 凭据。
  这是本仓库里少数几个真实改变外部现实的出站路径之一，属于可直接观察到的安全缺口。
source_check:
  - src/backend/zuno/capability/tools/delivery/action.py:41-51（Authorization: APPCODE 头 +
    ssl.create_default_context() → check_hostname=False → CERT_NONE → urlopen）
fact_layer: Current
gap_type: SYSTEM_GAP
proposed_change: 恢复默认证书与主机名校验；若目标端点确有证书问题，用显式 pinning 或受控的
  CA 配置解决，而不是全局关校验。
simpler_alternative: 直接删掉这两行（等价于恢复默认校验），改动量最小且不需要新配置。
cost_and_exit: 一行级改动；若端点证书确实不合法会立即暴露失败，这是期望行为。退出方式是把两行
  加回来（不推荐）。
priority: P1
```

## S12 — 文档与 main 脱钩

```text
signal: 至少两处文档与当前 main 不符。其一，docs/modules/security/README.md 的 Gap 段仍写着
  production WorkspaceRuntimeComposition / SecurityDecision resolver binding 尚未建立 Current
  proof，而 src/backend/zuno/main.py 已经构造并绑定了 WorkspaceRuntimeComposition 与
  PostgresSecurityDecisionResolver。其二，agent/runtime/phase08.py 这条 ADR-0005 合规的官方
  checkpointer/run service 路线，在 docs 全域内没有任何被提及之处（既非 Current 也非 Target），
  且它对应的 cutover 文件被测试断言禁止存在。文档层因此不是当前系统的准确投影。
source_check:
  - src/backend/zuno/main.py:59-115（PostgresSecurityDecisionResolver :59/:68、
    WorkspaceRuntimeComposition :61/:99、configure_workspace_product_composition :62/:115）
  - src/backend/zuno/api/services/product/runtime_engine.py:350（configure_workspace_product_composition(None)）
  - docs/modules/security/README.md:91（仍称未建立）
  - docs/governance/product-security-composition-implementation-status.md（PSC-A/B IMPLEMENTED /
    SELECTED VERIFIED；main 证据指针 293fa144 / run 35202465804 / 214 passed）
  - src/backend/zuno/agent/runtime/phase08.py:36-56（文档全域无对应描述）
  - tests/repo/test_agent_system.py:36（phase08_cutover.py 必须不存在）
fact_layer: Current
gap_type: DOC_GAP
proposed_change: 用一次文档同步把 security 模块的 Gap 段对齐到 PSC-A/B 的实际状态；并为
  phase08.py 明确归属（要么写进 Target 与 ADR-0005 的落地路径，要么标记为待退役实现）。
simpler_alternative: 只更新 security README 的这一段（导致读者误判的最大单点），其余留待运行时
  收敛决定（S05）之后一并处理。
cost_and_exit: 纯文档改动，无回退成本。收益 Unknown。
priority: P1
```

## S13 — 自宣 SUPERSEDED 但缺收口证据

```text
signal: docs/governance/effect-security-slice-c-review.md 记有多条 FAILS_TARGET（其中
  unknown_effect_restart_replay @ run 34559517466、mandatory_audit_before_effect @ run
  34560692093），同时把自己的状态写成 SUPERSEDED_BY_RB019_IMPLEMENTATION_EVIDENCE，却没有给出
  收口用的后续 run SHA 与结论。当前 HEAD 上 mandatory_audit 那条可以读到已接线的实现（见 S16），
  但 restart-replay 那条既没有反向证据也没有收口证据。上级规则要求「修复后的历史负面证据仍保留，
  且必须与后来的收口 SHA/run 成对保存」，该文档不满足。
source_check:
  - docs/governance/effect-security-slice-c-review.md（status 行；:73-84、:86-98 的 FAILS_TARGET；
    :131-146 判定块）
  - docs/project/reference.md:66（历史负面证据与收口证据成对保留的规则）
  - docs/evidence/README.md:22-54（边界声明：AUD-L2 NOT IMPLEMENTATION-PROVEN 等）
  - src/backend/zuno/capability/tool_runtime/invocation_gateway.py:581-587（reconcile_required 与
    重放结果的区分）、platform/database/tool_runtime/domain.py:943-960（result_ref 种类描述）
  - docs/governance/aud-l1-implementation-status.md（AUD-L1 verified，AUD-L2 未证）
fact_layer: Historical
gap_type: DOC_GAP
proposed_change: 为每一条 FAILS_TARGET 补上收口证据（run SHA + 结论）或明确标注「仍开放」；
  SUPERSEDED 这个状态不应在没有收口指针的情况下使用。若 restart-replay 那条确实未修复，把它从
  「已超越」改回声明的开放项。
simpler_alternative: 直接删掉 SUPERSEDED 标注，把该文档还原为 HISTORICAL，等有 run 证据再改状态。
cost_and_exit: 文档层动作；风险是若真存在未修复的重放缺陷，降级文档等于把它留在暗处，因此建议
  与 S07 一起看。
priority: P1
```

## S14 — per-user MCP 配置的并发隔离是成立的

```text
signal: 用户的 MCP 配置不是存在进程级共享结构里，而是在每次工具调用时按 user_id + tool→server
  解析后，拷贝进本次调用的参数副本（call_args = dict(args)），再交给 provider。并发调用读的是
  各自的副本，不存在跨用户串配置的路径；当注册表缺失时直接抛 MCPToolAdapterNotBound（失败关闭）
  而不是回落到默认配置。
source_check:
  - src/backend/zuno/platform/services/workspace/simple_agent.py:188-208（call_args = dict(args) →
    mcp_requires_user_config 判定 → 解析 mcp_config → call_args.update → 缺失即 raise
    MCPToolAdapterNotBound）
  - src/backend/zuno/platform/services/workspace/simple_agent.py:103-116（MCPConfig 模型）、:272（mcp_configs）、
    :327（server_dict）、:2920-2926（get_mcp_id_by_tool）
  - src/backend/zuno/agent/contracts.py:71-81（ContextPack 为受治理契约，不含逐用户注入）
  - docs/governance/project-fact-provenance.md PF-032（子 Agent 转发被移除、按 tool→server 映射注入）
fact_layer: Current
gap_type: NO_GAP
proposed_change: none
simpler_alternative: none（当前实现即为合理解）
cost_and_exit: none
priority: P2
```

## S15 — 执行前授权新鲜度已经存在

```text
signal: 授权不是「计划构建时判一次」。安全准备阶段建立 epoch / principal context / authorization
  decision / approval，随后在执行前被复核两次（发放 secret lease 之前、真正派发之前），复核内容
  包括 prepared_action_hash 是否变化、epoch 是否仍 active、decision 是否 DENY、approval 是否
  已批准且未过期；任一不满足即失败关闭。因此「计划构建后权限被收回」这一场景在 Current 里有
  确定行为。
source_check:
  - src/backend/zuno/capability/tool_runtime/invocation_gateway.py:974-1065（_record_security_prepare：
    ensure_effective_epoch / principal_context / authorization_decision / approval / audit_requirement，
    validate_pre_effect_authorization :1060）、:388、:462（执行前复核点，:459-461 注释）、:535（真实派发）、
    :1260-1271（_reauthorize_execute_epoch）
  - src/backend/zuno/platform/security/persistence.py:1045-1084（hash/epoch/decision/deadline 判定）
  - docs/evidence/README.md:22-54（边界声明）
fact_layer: Current
gap_type: NO_GAP
proposed_change: none
simpler_alternative: none
cost_and_exit: none
priority: P2
```

## S16 — 副作用前强制审计 + 未知结果默认 RECONCILE

```text
signal: 带副作用的派发之前会先持久化强制审计，并把该审计读回来验证其持久性（写失败则中止
  前置条件、把行标记为 dispatch_aborted、终态失败而不是带着未知状态继续）。远端结果未知时，
  系统写入 durable UNKNOWN 并默认 next_action="RECONCILE"（15 分钟升级窗口），返回给调用方的是
  reconcile_required 而不是重试；盲目重试是被明确排除的非目标。这两点与 Target 不变量一致。
source_check:
  - src/backend/zuno/capability/tool_runtime/invocation_gateway.py:1426（_persist_mandatory_audit_before_effect）、
    :430（调用点，早于 :499 sandbox prepare 与 :535 派发）、:1478-1488（审计 payload 含
    authorization_decision_id / security_epoch_ref / prepared_action_hash）、:1499、:1551（dispatch_aborted）、
    :581-587（reconcile_required / UNKNOWN_EFFECT_RECONCILIATION_REQUIRED）、:1958-1998（unknown payload）
  - infra/db/alembic/versions/20260718_12_mandatory_audit.py、
    20260918_59_mandatory_audit_tenant_scope.py、20260920_60_mandatory_audit_dispatch_abort.py（:33 状态枚举）
  - docs/project/reference.md:53-54（Current 证据：durable UNKNOWN、typed restart replay、发送门消费已提交审计证明）
  - docs/governance/effect-remote-query-reconciliation-status.md（盲重试是非目标）
fact_layer: Current
gap_type: NO_GAP
proposed_change: none（若要动，动的是 S07 的驱动侧，不是这里的语义）
simpler_alternative: none
cost_and_exit: none
priority: P2
```

## S17 — T06 个人归属边界

```text
signal: 「第一笔改动是哪一笔」「逐行 blame 谁是主要贡献者」「哪条 bullet 该留」这一类问题，
  系统的权威文档已经给出可支撑的边界：项目 2026-03 前已存在（非 greenfield）、个人参与是方向级
  + 若干有界的切片、精确到 PR/接口/SQL/bug 的个人闭环在没有额外证据时属于 Unknown。因此这不是
  系统缺口：无论候选人答得清不清楚，系统侧都已经把可说与不可说划开了。若候选人在回答里把团队
  能力说成个人实现，那是表达/归属问题，不是架构问题。
source_check:
  - docs/project/README.md:142,146,148,156（加入时系统已存在；法院侧测试规模未恢复；Pilot 不等于
    Production；个人参与清单）
  - docs/project/reference.md:25-35,37-47,60-67（Confirmed personal participation / claim boundaries /
    Current-Target-Unknown routing；「精确个人闭环 → Unknown unless separately recovered」）
  - docs/governance/project-fact-provenance.md PF-007…PF-032（含 PF-029 Memory readback、PF-031 GraphRAG、
    PF-032 子 Agent 转发移除）
  - docs/red-blue/rounds/rb-2026-10-07-formal-020/02_red_questions.md Q51–Q60
fact_layer: Historical
gap_type: ANSWER_GAP
proposed_change: none
simpler_alternative: none
cost_and_exit: none
priority: P2
```

## S18 — T07 Pilot / 法院定性边界

```text
signal: 「Pilot Validation 是谁给的定性」「法院有没有出自己的题」「这个系统在生产跑过吗」这一类
  问题，系统侧已经有一致且更保守的答案：Pilot Validation 不构成 Production，生产就绪状态未被建立，
  法院 QA 属于 UNKNOWN / NOT AVAILABLE，且没有任何一条证据能支持「真的改过法院侧系统」。所以
  T07 打到的是表达与措辞纪律，不是系统缺口 —— 文档没有夸大，是简历措辞可能夸大。
source_check:
  - docs/project/README.md:148（Pilot Validation 仍属试点，无资料支持 Production）、:156（历史链条）
  - docs/project/reference.md:23（Pilot Validation does not establish Production）、:56（measurement-gated）
  - docs/evidence/README.md:22-54（PRODUCTION_READINESS: NOT_ESTABLISHED、COURT QA: UNKNOWN、
    QUALITY: not_yet_proven、FULL CI: NOT RUN）、:53,68,88
  - docs/red-blue/rounds/rb-2026-10-07-formal-020/01_simulated_resume.md（bullet 表述限于内部 Demo /
    法院侧测试 / Pilot Validation）
  - src/backend/zuno/**（「法院 / court」在 Python 源码中零命中，仅出现在文档）
fact_layer: Historical
gap_type: ANSWER_GAP
proposed_change: none
simpler_alternative: none
cost_and_exit: none
priority: P2
```

---

## 我确认过但判断为 NO_GAP 的部分

下面这些是 Red 探到的坐标，我实际打开了对应用代码/文档后确认**系统没有洞**，因此不立为信号，
只在此留痕（避免下一波把它们当成新缺口重报）：

1. **Q6 / Q94 — 超时分布。** 超时是分层设置的：MCP discovery 10s（`platform/services/mcp/manager.py:17,25`）、
   HTTP 5s / SSE 300s / streamable 30s（`mcp/sessions.py:27-31`）、tool binding 30s
   （`workspace/single_controller_runtime.py:254`）、sandbox wall_time（`capability/tool_runtime/sandbox.py:194,278`）。
   唯一的缝隙是 `RuntimeLimits.timeout_ms`（`agent/runtime/contracts.py:56-61`）声明了却没有任何读取点 ——
   这属于死字段，量级不足以单立信号，记在这里。
2. **Q7 / Q9 / Q93 — 无法确认远端是否执行。** 系统的前提与 Red 的追问方向一致：
   HTTP 超时不能推断远端未执行，因此走 `ToolEffectUnknownError` → `UNKNOWN_EFFECT` →
   `reconcile_required`（`capability/tool_runtime/invocation_gateway.py:46-56,536-782`），不做盲重试。
3. **Q36 / Q37 / Q38 — Domain 提交与 checkpoint 不同事务。** 这是被显式选择的设计：本地强一致
   + 事务内 outbox（`platform/database/agent/domain.py:511-521`，`infra_outbox_events`），
   不使用跨存储 2PC（`docs/architecture/architecture.md:155`）。恢复以 owner fact 为准且由人触发
   （`agent/durable_runtime.py:272-312`），与 Target 一致，不是缺口。
4. **Q30 / Q20 — 删除条件与降级条件是有文档的。** Memory/Context 的合法下一步已被收敛为
   「A/B 后冻结或删除/收缩」两条（`docs/governance/rb019-p0-implementation-freeze.md`）；
   GraphRAG 的 keep/delete 判据与主指标写在 `docs/governance/rb019-graphrag-ablation-protocol.md`。
   缺的是数据，不是判据 —— 属 `docs/evidence/current-eval-baseline.md` 已声明的 `MEASUREMENT_BLOCKED`。
5. **Q29 — Memory/Context 的 A/B。** 无对照实验属实，但这一点已被 architecture reference 的
   「measurement-gated complexity」不变量与 evidence 的 `QUALITY: not_yet_proven` 覆盖，不是新洞。
6. **Q10 / Q77 — 自研 MCP 层补的 delta。** 子 Agent 转发被移除、按 tool→server 映射注入这件事
   在 provenance（PF-032 / 0b5fb350）里有记录，`MCPManager.call_mcp_tools` 也已改为直接抛
   `RuntimeError`（`platform/services/mcp/manager.py:64+`），命名残留（`mcp_as_tool_name`）不影响语义。
   唯一缺的是「客户原始需求」的恢复，文档已如实声明「没有恢复」。
7. **Q8 / Q100 — direct route vs ReAct 的判定位置。** 判定是规则/关键词驱动的
   （`agent/planning.py:189-236`、`agent/runtime/planning/selector.py:27-50`、`agent/runtime/routing.py:47-52`），
   与简历「一步明确走 direct、复杂/参数不全回落 ReAct」的表述一致；`_canonical_mcp_target()` 的自
   递归修复与 `_extract_gaode_weather_city()` 都是真实存在的代码。需要提醒的只是：自然语言参数抽取
   在 Current 里是一个工具一个手写抽取器，不是通用能力 —— 这属于简历措辞的边界，不是系统缺口。
8. **Q44 / Q43 — 见 S15、S16**，两处均为已实现的 Current 能力，不是缺口。
9. **Q48 — 「有没有真的改过外部现实」。** 通用的出站能力确实存在（MCP executor → provider、
   OpenAPI POST、图/文/搜索类 HTTP 调用、Lark 日历创建/删除），但**没有任何法院侧系统的证据**，
   文档也如实标注 `COURT QA: UNKNOWN`。诚实性上没有缺口（唯一的实现级问题已单列为 S11）。
10. **工程基础题（Q91 / Q92 / Q95 / Q96 / Q97 / Q98 / Q99）。** 这些是对候选人基础能力的探针，
    与系统实现无关；系统侧相关的两点（写操作重试的安全性、scope 查询的复合索引）分别由
    idempotency key（`capability/mcp/mcp_tool_executor_adapter.py:70-74`）与 scope 过滤路径承载，
    未发现系统性缺陷。
11. **Q71 / Q73 / Q76 / Q78 / Q80 — 模块合并/删除条件。** 这些是设计判断题。系统侧唯一可判定的部分
    （哪些模块当前无调用方、哪些抽象是「为完整性而加」）已经分别落在 S06（planning 控制面）与
    S09（融合词典/阈值）两条信号里，不重复立信号。

---

初诊到此为止。上面 18 条里，S01–S04 是我认为**在下一波最该被当成系统事实（而非表达问题）追问**的四条；
S05–S13 是同一批断点的次要面；S14–S18 记录的是「系统成立、问题在措辞或归属」的部分。
