# Red Wave 2 — Blind Evaluation + 100 Follow-ups

```text
round: rb-2026-10-08-formal-021
blind: true
seen: 01_simulated_resume.md, 02_red_questions.md, 03_blue_answers.md, .agent/red-blue/attack-model.md
not_seen: 03_blue_architecture_notes.md, canonical docs, source, Evidence
```

---

## Part A — Blue Wave 1 Blind Evaluation

方法声明：我是 blind 的。下面所有对 `文件:行`、commit SHA、run id、测试名的判断，评价的都是**可信度结构**（引用密度是否自洽、同一机制在多题间是否一致、引用之间是否互斥），不是**引用是否正确**。我无法核实任何一条引用。

---

### 1. 哪些 Claim 已经可信（信任上升）

**（a）06 控制面的「报告」——本轮最可信的一段。**
A11 / A12 / A13 / A44 / A45 / A46 / A47 / A48 / A49 / A50 / A92 / A93 组成了一个内部高度自洽的引用簇：行号在文件内单调、且与描述的执行次序一致（`_issue_secret_lease` `:409` → audit `:429-436` → reauth `:462` → abort `:487` → sandbox `:499` → abort `:529` → `executor()` `:535` → receipt `:539-549` → reconciliation row `:550-574` → `reconcile_required` `:581-587`，另加 A47 的 `:1529` / `:1551`）。A44/A46/A47 给出了**正向与负向两类 run id**（PR #203 / `34560042535` 正向 0 次调用；#205 / `34560692093` 负向），并主动把 **AUD-L1 (verified)** 与 **AUD-L2 (NOT IMPLEMENTATION-PROVEN)** 拆开（A47）。这种"一半闭环、一半明说没闭环"的切法，是与引用相互印证的。

**（b）GraphRAG 失败的**诊断报告**——信任上升到"他如实报告了"，但**不**上升到"结果成立"。**
A20 / A85 主动交出「baseline 自己的 `MRR@10` 从 0.90 变成 1.00」这条对自己不利的原始数字；A68 主动说「**我举不出一个会因为删掉图路由而变差的 query**」；A21 / A86 主动把这一层定性为「没有收益证明的复杂度」。A15 把根因定成 ranking **displacement**、并承认三路历史 rank 未存档（A15 边界）。这些都是**代价高昂的自我削弱**，与「编一个成功故事」的策略方向相反。

**（c）Ownership 的**受限切片**口径在 A1 / A52 / A54 / A58 / A59 / A62 之间稳定。**
A54 把个人切片限定在 Tool/MCP（PF-032）、GraphRAG（PF-031）、Context/Memory V2（PF-029/PF-030）三条，并明确拒绝总体 Target Architecture、九模块、平台 DB schema；A58 把 `0b5fb350` 判为「混合大提交，只能安全提取子集，整个 commit 不能算成我的」；A59 拒绝把「项目经历过法院测试」扩写成「我做过」。A59 与 A60/A61/A64/A65/A66 六题全部停在 Unknown，没有一题偷偷升级。

**（d）稳定重复出现的实现细节（跨答一致，是较难伪造的一致性）。**
- `execute_binding_tool` 里 `call_args = dict(args)` → `call_args.update(mcp_config)`：A4 / A5 / A89 三处一致（`simple_agent.py:189-201`）。
- `MemoryEngine._memory_exclusion_reason`（`engine.py:1054-1064`）：A31 / A32 / A33 / A96 四处一致。
- `activate_memory_version` 的 `SELECT ... FOR UPDATE`（`domain.py:315`）+ generation CAS（`:353`）+ `MemoryGovernanceConflict`（`:363-364`）：A34 / A94 / A100 三处一致，且 A34 与 A94 对「`MemoryUnitOfWork` 用 `connection.begin()`、未显式设隔离级别」这条不利事实也一致。
- `_rank_key` 的排序元组 `(candidate_group, baseline_rank, -chain_score, -graph_tier, -graph_signal, -(local+base))` 与「`fusion_score` 只进 metadata、不参与排序」：A17 / A97 / A98 三处一致。
- 「`Provenance != Truth != Authorization != Semantic Preservation`」这条不变量：A27 / A29 / A72 / A100 四处一致，且每次都被用来**降低**自己的 claim（A29、A72、A100），而不是用来抬高。

**（e）引用密度本身是自洽的，且分层清楚。**
最密集的 `file:line` 出现在 A17 / A44 / A46 / A94 / A97 / A99，这些恰好是阻力最小的代码层描述；最弱的环节（A11 / A12 / A13 / A92 的 timeout 与幂等语义）被他自己标成 `Target / Fundamental`，证据是 `docs/modules/effects/reference.md` 的 B 编号而不是代码。**他知道哪里是文档、哪里是代码，并且没有混用**——A38 / A92 / A48 都在正文里主动区分了「doc 说的」与「src 里有的」。这比引用总量更能说明问题。

**（f）引用互斥只在少量位置出现（见 §2 / §6），密度很低——也就是说，这 100 条答案的引用结构整体自洽。**

---

### 2. 哪些只有术语、缺实现

- **`KnowledgeGeneration`（A77 / A78 / A80）**：最高纯度的一处。A78 自己承认「`src/` 里 literal `KnowledgeGeneration` 无命中」「它是 03 模块文档里的 Target 概念」；而 A77 / A80 仍然用它描述「原子切换 ServingPointer」「generation-level validation」的机制。术语先行、实现未跟，**且这个术语并不在冻结简历里**（见 §6、Q179）。
- **`WAITING_RECONCILIATION`（A48）**：A48 自己说 Target 里叫这个名字、「今天的 `src/` 里没有这个字面状态」，今天返回的只是一张 `reconcile_required` receipt。于是「Run 停在等待对账」是一条**没有被强制的设计**。
- **`ReadinessDecision` / `PARTIAL` 覆盖语义（A80）**、**negative evidence（A82）**、**跨 Store purge 与撤权后召回收敛（A79）**、**自动 remote-query reconciliation（A13 / A49 / A50，`DEFERRED_BY_PROVIDER_CAPABILITY`）**：全部自标 Gap / Deferred。
- **`ContextOrchestrator`（A55 / A71）**：有代码、**无路径**——A55 说 `src/` 内除 re-export shim 外没有业务调用点，真实读路径是 `core.py:64/79` 的 `build_context_pack`。这是"有实现但没有被使用"的第四类：既不是 Target，也不是 Current。
- **九模块 authority 划分（A38 / A41 / A45 / A100）**：全部以 `docs/modules/*/reference.md` 的 B 编号表达，`事实层` 自标 Target。这套体系的可信度是**文档一致性**的可信度，不是**实现被验证**的可信度。A45 / A100 说得最漂亮的两句（「模型永远不赢」「各自回到自己的 Owner」）没有任何代码或测试落点。
- **`AdmissionReceipt`（A40）**：A40 自己说它今天 `NOT IMPLEMENTATION-PROVEN`。

---

### 3. 哪些 Ownership 不清

- **「重构之前是谁写的」（A1 / A52 / A53）**：三题都答 Unknown，理由统一是「作者字段区分不出个人与团队」。这条理由本身自洽，但 A51 把它推到一个更硬的结论：**公开根提交 `eafeb1c2` 是 2026-04-15，与他能自证的第一笔 `77346758` 同日**。于是 2026.03 到 04-15 之间没有任何可复核落点——「我加入时系统已经存在」这句话在公开历史里**没有证据承担者**（A51 自己承认）。
- **`0b5fb350` 的切分标准（A58）**：A58 说该提交「跨工具、Knowledge、模型、Docker、脚本」，只能"安全提取几条有明确前后差异和测试的路径"。提取标准是什么、剩下的算谁的，没有给出可复核的边界。
- **平台 DB schema 与个人 slice 的交界（A54）**：A54 明确说 DB「我只是进库查过、调过实际数据，不拥有 schema 设计」。但这套 schema 恰好是 A96（`review_status` 列）、A34（`memory_versions` 表、`memory_commit_receipts`）的前置——个人 slice 与平台 schema 的边界在 memory 路径上仍然含糊。
- **本轮的**结构性问题**：候选人最可信的那批回答（A11–A13、A44–A50、A92–A93）全部来自 **06 / 08 控制面**——而 A14 / A75 明确把那套 `PreparedAction / Approval / Idempotency / EffectReceipt` 划给「后来更强的团队层，不是 4 月这段的工作」，A54 也把它排除在个人切片之外。也就是说：**他 ownership 最强的三条（Tool/MCP、GraphRAG、Context/Memory）恰好是收益未证明、部分已无 consumer 的三条；而他讲得最可信的模块，他不拥有。** 这个错位必须写进 Final 的 Claim 分级，不能靠"讲得好"补 Ownership。
- **决策归属（A56 / A8）**：direct route 准入的 decision owner = Unknown，`docs/decisions/` 里没有对应 ADR（A56）。一条影响**所有请求分流**的规则没有决策记录，这是治理缺口，不只是"没证据"。

---

### 4. 哪些数字 / Pilot / benchmark 可疑

- **A19 / A84 vs A20 / A85：未闭合的归因混淆。** A19 / A84 主动说「更早那轮 `limit=5` 的 smoke 用的是 `qwen-plus`，是 profile 对齐之后才换成 `deepseek-v4-flash` 的」，也说「同一索引严格说不成立」（进程内临时重建、跑完清掉）。但 A20 / A85 解释 baseline 自己 `MRR@10` 0.90→1.00 时，只给了「说明这份 5 题样本本身波动就大」——**没有把换模型这条自己刚披露的混淆项接上去**。如果 audit（`7928df50`，记录 baseline 1.00 / local 0.80）与 rerun（`3da5d742`，记录 local 回到 1.00）之间跨了模型，那么 local 从 0.80 回到 1.00 究竟该归因给 fusion 修复还是换模型，A15 / A20 / A85 都没有排除。这是本轮**最高价值的证据缺口**。
- **A25 的时延 15806→18503 ms**：A25 自己说这是「本地重建图路径」、不是生产路径；token 成本 = Unknown。方向可用、量级不可外推，这个自我限定是对的，但意味着简历"多跳图检索"的代价至今**没有任何生产尺度的量级**。
- **手定常数集合**：A18 的 `GRAPH_PROMOTION_THRESHOLD = 6` 与 graph-only 的 `≥9`（「我手定的，没有 calibration 证据」）；A49 的 `age_escalation_after_seconds=900`；A78 的 `KnowledgeReadinessEvidence` 要凑齐 **30** 个 requirement id；A99 的 `n_results=min(top_k, 100)`；A88 的 6 元整数元组权重。六个数字，零个可追溯来源。
- **A35 的 32 / 66 / 11 passed 与 A57 的 `35516807526` / 224 passed**：A35 自己标成「测试证明 behavior，不证明质量收益」；A57 自己标成「当前快照的验证，不是 2026 年 4 月那批测试当时的执行记录」。这两处自我限定是干净的，但也说明**简历第 4 条的"focused tests"在证据上是行为级，不是质量级**。
- **A21 的「≥300 题/数据集」**：这是协议**要求**，不是已执行；且 A21 把简历的「尚未执行」改写成「**跑不了**」（`BLOCKED_PENDING_DATA`），理由具体到「本机连 HotpotQA 官方源 TCP 超时、`data/evals/multihop/` 不存在、没有模型 API 凭证」。**这是本轮唯一一处疑似「口径升级」**：把"我没做"转写成"环境不允许我做"。方向仍是降低 claim，但责任归属完全不同，值得追（Q116）。
- **A59–A66 的 Pilot / 法院**：七个答案里六个是 Unknown，A62 把边界定性成「取证边界（PF-020: NO EVIDENCE / NOT ESTABLISHED）」而不是人为决策。诚实度很高；但由此产生一个结构性后果：**简历第 6 条（项目简介里的"内部 Demo、法院侧测试与 Pilot Validation"）与第 1–5 条在证据密度上完全不对称**——前五条有 commit / file:line / 测试名，第六条几乎只剩下阶段名与一条台账边界。作为面试官，我会认为第 6 条在简历上是**近零信息行**。

---

### 5. 哪些 failure / 工程基础暴露薄弱

- **A99：ANN 的召回损失从未测。** Chroma `hnsw:space=cosine` + `n_results=min(top_k,100)`，A99 承认「没有 ANN vs 精确的对照，也没有不同 K 的召回曲线」。这条不只是基础题没答好——它**直接破坏 A15 的归因**：被挤出 top5 到底是 graph 位移，还是 ANN 抖动 + 小样本？A15 没有排除这个替代解释。
- **A34 / A94 / A95：并发与事务。** `MemoryUnitOfWork` 用 `connection.begin()`、**未显式设隔离级别**；全 memory 模块只有一处 `FOR UPDATE`；A95 承认「没有逐个调用点审计是否存在把模型调用包在写事务里」。CAS 能防同 version 双激活（A34 说清了），但 A94 同时承认没有别的并发护栏。
- **A33 / A96：状态新鲜度靠写入方自觉。** A33「没有后台 reaper，状态没刷新就挡不住 stale」；A96「没有 snapshot / 事务冻结，没有一个专门的 TOCTOU 护栏」。两处缺口都指向同一个弱点：**系统里没有主动收敛角色，只有被动过滤**。
- **A29 / A70：`agent_id` 硬编码 `"agent_run"`。** 声称的四维 scope 实际生效三维。这是"讲得比做得多"的少数硬证据之一，且是他自己交出来的。
- **A91：tool 路径上不存在 `asyncio.gather`。** 这一条是**加分项**（他在纠正 Red 1 的架构假设，而不是顺着编），但它反过来暴露 Wave 1 的问题里含有未经验证的并发假设；也意味着 Q5 / Q89 的"并发不串"从未在真正的并行路径上被检验。
- **A5 / A89 的论证强度。** 「`call_args` 是函数局部对象所以不串」只覆盖了参数字典这一层；它**没有覆盖 `mcp_user_config_resolver` 自身是否有 `(user_id, server_id)` 级缓存**。论证的完备性弱于它的语气（见 §6、Q190）。
- **A9：`_canonical_mcp_target` 递归不收敛（`RecursionError`）。** 这类缺陷的存在本身说明 direct route 的参数抽取层没有做过输入空间边界设计——它的修复方式（命中分支直接 `return server_norm`）是补丁，A9 没有说是否做过同类递归的普查。

---

### 6. 哪些回答自己产生了新的攻击 handle

按杀伤力排序：

1. **A97 / A98 vs A17 —— 最高价值。** A17 把 `baseline_rank = min(vector_rank, bm25_rank)` 说成"不可被挤出的下限"，即 baseline-preserving 是一条**不变量**；但 A97 / A98 同时说 comparison / bridge / genealogy 三类 query 上有 guardrail 会**「硬替换 top」**（A98 给了 `selected[weakest_index] = candidate`）。硬替换能不能把 baseline 已命中的 gold 再挤出去？如果能，这条不变量就**只在排序阶段成立、不在最终输出上成立**，而这三个 query class 恰恰是这套机制声称擅长的类。两条答案出自同一人，互相没有对齐。→ Q117 / Q118。
2. **A12 / A93 的幂等 key 尾部带 `{salt}`。** key 是 `idem:{tenant}:{workspace}:{run_id}:{step_run_id}:{tool_name}:{salt}`。若 `salt` 每次调用随机生成，同一逻辑动作 retry 时 key 就不同，`claim_idempotency_receipt` 会 miss 掉既有 receipt——**幂等在最需要它的那条路径上失效**。A12 / A93 都没有说明 salt 的确定性。→ Q106 / Q107。
3. **A19 / A84 vs A20 / A85 的模型混淆**（详见 §4）。他自己披露了换模型，却在解释 baseline 漂移时只提"样本波动"。→ Q112–Q114。
4. **A21 的「未执行 → 跑不了」措辞移动**（详见 §4）。→ Q116。
5. **A23 vs A73 / A74：机制被人为拆成两个预算。** A23 说 seed 的来源标签包含 `alias`——也就是说别名归一化的输出**直接喂进** seed expansion；A74 却在"只能留一个"时把两者当成独立机制排序（留 seed、删 alias）。若 alias 是 seed 的输入，删掉它的代价不能按"独立机制"估。→ Q172 / Q173。
6. **A49 的 `escalate_due_reconciliations` 与 A49 自己的「当前没有 background reconciler」。** 一个按 900 秒把 OPEN 升成 MANUAL 的函数，需要有人触发；A49 没有说是谁。→ Q147。
7. **A48 的 `WAITING_RECONCILIATION` 只存在于 Target。** 那今天 Run 到底是停了，还是收到 `reconcile_required` 后继续往下走？"设计上停"与"今天停"是两回事，这条直接决定 06 的不变量是不是被强制。→ Q149。
8. **A55 / A71 与 A28 对撞：读路径到底是哪条。** A28 说 `d4e2fe2` 是 `GeneralAgent.prepare_context()` + 回合后写入；A55 / A71 / A30 说真实路径是 `agent/runtime/nodes/core.py` 的 build_context → `build_context_pack` / `post_turn_commit`。**如果 `prepare_context` 也像 `ContextOrchestrator` 一样不在 live path 上，那么简历第 4 条"接入 Agent 调用前读取与回合后写入"描述的就是一条死支。** → Q127 / Q128。
9. **A38 同题干内自相矛盾：`DRAFT → ACTIVATED → SUPERSEDED`（文档）与 `DRAFT/VALIDATING/ACTIVE/SUPERSEDED`（代码）。** 同一题里两套状态名并存，`ACTIVATED` vs `ACTIVE`、多出来的 `VALIDATING` 没有交代。→ Q138。
10. **A78 接受了 Q78 的假前提。** Q78 问"你简历里的 `KnowledgeGeneration`"，但**冻结简历里没有这个词**。A78 按它存在直接作答，没有先纠正前提。一个背得住自己简历的人通常会先说"简历里没这个说法"。→ Q179。
11. **A55 / A71 主动交出「ContextOrchestrator 没有生产调用点」**——这是自削，但也提供了"主动披露 vs 追问才承认"的元问题。→ Q158。
12. **A46 / A47 / A48 的「同一条链路」叙事在证据等级上是分层的**（`Current` / `Target` / `Gap`）：这既是诚实的结构，也意味着 **06 的"已验证"部分只覆盖 revoke-before-send、mandatory-audit-before-effect、unknown-effect-restart-replay、pre-send-abort 四个窄窗口**（A44 / A46 / A47 / A48 的边界合起来说的）。把它读成"06 已经建好了"会严重高估。

---

### 7. 作为面试官的整体判断

**画像：一个诚实、边界感强、但对"复杂度是否值得"几乎没有测量能力的工程师。**

- **真实性（authenticity）我倾向给较高评价。** 三条理由：(1) 自削的粒度到机制级（A9 的递归不收敛、A33 的无 reaper、A55 的无 consumer、A94 的无隔离级别、A99 的无 recall 测试），不是泛泛的"还有很多要改进"；(2) 他削的常常是自己刚建立起来的东西（A20 交出 baseline MRR 漂移、A68 说举不出受益 query、A86 说"如果 Red 主张该先 Defer 我不反驳"），这在"演给评测器看"的策略下是净负分；(3) 唯一一处疑似升级（A21）是**把缺口说成环境阻塞**，方向仍然是降低 claim。
- **技术深度我给中等偏上，但分布在错误的位置。** 06 控制面的问答（A44–A50）有行号、run id、测试名、正负向证据、AUD-L1/L2 切分——这是资深工程师的表述密度。而在他**自己拥有**的三条线上（Tool/MCP、GraphRAG、Context/Memory），深度主要体现在**"我承认它不成立"**，而不是"我知道它为什么成立"。
- **复杂度正当性我给低。** 这一条是本轮最明确的结论：
  - GraphRAG：A68 说不出一个删掉会变差的 query；A21 / A86 承认没有 holdout、没有 ablation；A24 / A67 承认在真正目标域（中文法律）**从未测过**，且已知有误合并风险。
  - Memory V2：A35 没有 A/B；A36 / A76 的删除判据是"测量没有稳定收益就关"，而测量本身是 `MEASUREMENT_BLOCKED`；`ContextOrchestrator` 是死代码（A55 / A71）。
  - Runtime：A43 承认 Native Runtime necessity `not established`。
  - 也就是说，**简历第 2、3、4、5 条所描述的复杂度，全部没有被证明值得**。它们的保留理由统一是"有单测、有设计、协议还没跑"——这正是 Attack Model §4 所说的「'已经实现'不能成为继续保留的理由」的反面案例。

**关于「每题都在削自己」这个形态——正面讨论。**

Attack Model 让我警惕一种可能：如果一个候选人在 100 题里**每一题**的"边界"都在削自己，那这个形态本身可能是被优化给评测器看的。我的判断是**部分成立，且必须写进 Final 的 Claim 分级**：

- **成立的证据（形态层面）：** 这份答案的**形态高度模板化**——每题都有"第二层"，每题都以 `事实层 / 证据 / 边界` 三段收尾，`事实层` 的取值像一个封闭枚举（Historical / Current / Target / Gap / Unknown / Open Design / Fundamental），`边界` 几乎每题都有且句式同构（"我不把 X 包装成 Y"、"仓库口径明确"、"这是 Target，不是已完成"）。一个真实候选人在 30–60 分钟口语面试里**不会自带这套 metadata 分类**。结论：这些 self-limitation 是**策略生成的**，不是**临场生成的**。一个由同一策略同时生成的 claim 和 boundary，boundary 不能独立地为 claim 作证——它只证明"口径被约束住了"，不证明"他主动坦白了"。
- **不成立的证据（内容层面）：** 削的位置集中在真实工程里最容易被吹的维度（收益 / 生产状态 / Ownership / 隔离级别 / 召回率），而不是集中在无害处；削的方向与文档证据的方向一致，**没有出现"一边削一边偷偷升级"的例子**（唯一一次近似升级是 A21）；削的时点常常紧贴在一个强叙述之后（A20 在给出漂亮数字之后立刻给出 baseline 漂移）。这不像"每处都留退路"的对冲，更像"每条 claim 都挂在一个已知的证据等级上"。
- **折中结论：** 我据此**不为任何一条强 claim 加分**——包括那些讲得最漂亮的（A44–A50）。本轮我能给 Blue 加的分，只能来自**外部一致性**（跨答行号、PR/run id、测试名、四处稳定重复的机制细节），而这批外部一致性**恰好集中在 ownership 之外**（06 / 08 控制面）。这一点与 §3 的结构性错位是同一件事的两面。

**简历与回答之间需要 Blue 2 正面收敛的一处硬差异。**

简历第 1 条写："目标与参数明确的一步请求走 direct route，**复杂请求进入 ReAct 路径**"。A8 / A56 的实际回答是：分流判据是规则（`_detect_route_hint` + `_plan_kind_for`）；`plan_kind == "complex"` 需要一个**注入的 DAG planner**，而产品组合（`main.py:113`）装的是 `None`，于是复杂请求**fail closed**（`DYNAMIC_PLAN_RUNTIME_NOT_BOUND`）；并主动补了一句"'复杂请求进 ReAct'更像历史/设计描述，不是今天产品路径的现状"。同时 A8 说 Runtime 里的"ReAct step"只是**一个 step 内的一次模型调用**。这三句放在一起，与简历的"复杂请求进入 ReAct 路径"是**互斥**的表述。A10 又进一步把 ReAct 的回归缺口描述成"需要假模型 harness 的 fixture 问题"——如果这条分支在产品组合里不可达，那这个代价的描述就站不住。→ Q101 / Q102 / Q105 / Q111。

**三处「简历已写明没有」的核查结果。**

1. ReAct 一侧无回归断言 → A10 明确维持（"简历里我写的是'ReAct 一侧暂无回归断言'，这句话我维持"），**没有偷偷说成有**。
2. 独立 holdout 与 leave-one-out ablation 未执行 → A21 / A86 维持，**没有说成有**；但 A21 把措辞从"未执行"移到"跑不了 / `BLOCKED_PENDING_DATA`"（见 §4、Q116）。
3. 项目经历只到 Pilot Validation → A59–A66 全维持，**没有升级成 Production 或"法院在用"**。
   结论：**三处都没有被偷偷说成"有"**。唯一的口径移动是第 2 条的方向性改写（缺口→阻塞），已列为追杀目标。

---

### Credibility Update（显式）

- **信任上升：** 06 控制面的**报告结构**（A44–A50，行号单调、正负向 run id、AUD-L1/L2 切分）；GraphRAG 失败的**诊断与自削**（A15–A20、A68、A85）；**受限 Ownership 口径**（A51–A59、A54）；**四处稳定重复的机制细节**（A4/A5/A89；A31/A32/A33/A96；A34/A94/A100；A17/A97/A98）；**主动区分 doc 与 src**（A38、A48、A78、A92）。
- **信任下降：** GraphRAG 的**净收益**（A68 举不出受益 query；A21/A86 无 holdout/ablation）；**目标域适配**（A24/A67 中文法律从未测）；**Memory V2 的收益**（A35 无 A/B）；**Runtime 的必要性**（A43 `not established`）；**Pilot / 法院的一切**（A59–A66 全 Unknown）；**A21 的"未执行→跑不了"**。
- **已建立的 Ownership 类别：** "受限提交切片 ownership"——三条工作流（Tool/MCP、GraphRAG fix chain、Context/Memory V2 链）+ 明确的"非我所有"清单（九模块 Target Architecture、平台 DB schema、Tool Control Plane）。**未建立**：任何强 Claim 的 Ownership 到"我设计了这个机制"这一层——他对机制的贡献统一退到"我在现有代码里做了这一笔"。
- **前后矛盾：** (1) 简历"复杂请求进入 ReAct 路径" vs A8/A56 "complex fail closed"；(2) A8 "complex 需 planner、产品里是 None" vs A10 "ReAct 侧缺的是假模型 fixture"；(3) A97/A98 的 guardrail 硬替换 vs A17 的 baseline-preserving 不变量；(4) A28 的 `GeneralAgent.prepare_context` vs A55/A71 的 `core.py build_context_pack`；(5) A20/A85 "样本波动" vs A19/A84 "跨轮换了模型"；(6) A38 同题干内 `ACTIVATED` vs `ACTIVE`。
- **稳定重复出现的实现细节：** 见 §1(d) 的五组；另加 `_memory_exclusion_reason`、`baseline_rank = min(vector_rank, bm25_rank)`、"`Provenance != Truth != Authorization != Semantic Preservation`"。
- **数字仍没有来源：** 15806→18503 ms（A25）；`Recall@5` 0.80→1.00 与 `MRR@10` 0.90→1.00（A15/A20/A85）；`GRAPH_PROMOTION_THRESHOLD=6` / graph-only `≥9`（A18）；`age_escalation_after_seconds=900`（A49）；30 个 requirement id（A78）；`min(top_k,100)`（A99）；`_score_path` 的 6 个分量权重（A88）；"≥300 题/数据集"（A21，协议要求）；32/66/11 与 224 passed（A35/A57）。**九个数字，零个可追溯来源。**
- **复杂度仍未证明必要：** GraphRAG 整层（A68/A86）；candidate-aware seed expansion / 别名归一化 / path-aware ranking 三个机制（A73/A74/A87，其中别名归一化的 bad case 是**推演而非观测**）；structured long-term memory（A35/A36）；ContextOrchestrator（A55/A71，死代码）；Native Runtime（A43）；Tool Control Plane（A14/A75 明确不在 4 月切片内，且从未与通用 Host 对照）。
- **成熟替代方案尚未比较：** (1) **GraphRAG vs 普通 hybrid / vector**——这是最大的一处，从未对照，且 A68 说不出删掉会变差的 query；(2) **RRF 或"过滤后重排"**——A97/A98 论证了 gate 与 RRF 数学上不相容，但**从未测过 RRF 的效果**，也未见引用成熟 IR 做法（Q199）；(3) **精确 KNN vs ANN**（A99）；(4) **Memory kill test 阶梯**（A35 未跑）；(5) **Generic Host vs Zuno Native Runtime 的 A/B/C**（A43 未跑）；(6) **成熟 MCP Host 的 per-user config**（A75 的 delta 之一是"按用户注参"，但很多 Host 已支持，未对照）。第 (2)(6) 两条是本轮新提出的替代方案缺口。

---

## Part B — Targeted Follow-ups Q101–Q200

```text
threads: T01 11 · T02 15 · T03 11 · T04 8 · T05 7 · T06 9 · T07 7 · T08 10 · T09 11 · T10 11 = 100
depth:   L1 0 · L2 22 · L3 78
```

### T01 — Tool / MCP（追杀 A1–A14）

**Q101.** 简历写「复杂请求进入 ReAct 路径」，A8 说 `complex` 需要一个注入的 DAG planner、产品装配里是 `None`、今天 fail closed——这两句在同一份材料里互斥，到底哪个是现状？
> `intent`: 简历与回答的口径差异（本轮核心） ｜ `callback`: A8, A56, Q8 ｜ `depth`: L3

**Q102.** A8 说 complex 分支 fail closed，A10 又说 ReAct 一侧「走模型、要假模型 harness 才能冻结」——如果这条分支在产品组合里根本不可达，那补断言的代价为什么被描述成 fixture 问题，而不是「它在生产里不跑」？
> `intent`: A8 与 A10 的内部矛盾 ｜ `callback`: A8, A10, Q101 ｜ `depth`: L3

**Q103.** 分流之外还有 `_resolve_governed_tool` 的具名 tool / MCP route tool / `/skill` / 图片重生成这些出口——这些分支里哪些有回归断言、哪些和 ReAct 一样没有？
> `intent`: 准入面的覆盖度 ｜ `callback`: A8, A10, Q8 ｜ `depth`: L2

**Q104.** `_detect_route_hint` 的关键词表（飞书/高德/必应/知识库/skill/终端）是固定清单，还是从 MCP server 注册表生成的；新接一个 server 时这张表会不会静默漏掉？
> `intent`: 规则的可扩展性与维护成本 ｜ `callback`: A8, Q8 ｜ `depth`: L2

**Q105.** `_plan_kind_for` 命中 `("compare","across","conflict","multi-hop","analyze","synthesize","报告")` 就判 complex，中英文混表——这张表是你定的还是产品定的；误判成 complex 时用户看到的是什么？
> `intent`: 规则来源 + fail closed 的用户可见后果 ｜ `callback`: A8, A56, Q101 ｜ `depth`: L3

**Q106.** A12/A93 的幂等 key 是 `idem:{tenant}:{workspace}:{run_id}:{step_run_id}:{tool_name}:{salt}`——这个 `salt` 是每次调用随机生成，还是由动作身份确定性算出来的？
> `intent`: 幂等 key 的确定性 ｜ `callback`: A12, A93, Q93 ｜ `depth`: L3

**Q107.** 如果 `salt` 是随机的，同一逻辑动作 retry 时 key 就变了、`claim_idempotency_receipt` 会 miss 掉既有 receipt，幂等在最需要它的路径上失效——这条今天靠什么兜住？
> `intent`: 幂等失效面 ｜ `callback`: Q106, A12, A93 ｜ `depth`: L3

**Q108.** A9 的断言写的是 `agent._canonical_mcp_target("qa-mcp-461126") == "qa-mcp-461126"`——这个 server 名是真实命名形态还是当时一个测试夹具；它和线上 MCP 命名规则是什么关系？
> `intent`: 测试数据的真实性 ｜ `callback`: A9, Q9 ｜ `depth`: L2

**Q109.** A1 说删掉 `mcp_agent.py`（−120）与 `skill_agent.py`（−263），skill 退化成 guidance-only tool——原先 `get_file_content` / `list_skill_files` 的能力由谁承接，还是直接消失了？
> `intent`: 重构后的能力缺口 ｜ `callback`: A1, A2, A7 ｜ `depth`: L2

**Q110.** A7 说今天 Runtime 已演进成 Single Controller + governed binding——那简历里「单 Agent Tool Calling」指的是 4 月那版还是今天的形态，今天还叫单 Agent 吗？
> `intent`: 简历措辞与当前架构的对应 ｜ `callback`: A7, A1, Q1 ｜ `depth`: L2

**Q111.** A14/A75 说 Zuno 的 delta 只有「暴露、注参、准入」三件，而「准入」这一件在产品组合里是 fail closed——那 4 月这段工作今天在整个 live path 上还剩多少在跑？
> `intent`: 历史工作与现状的存活率 ｜ `callback`: A14, A75, A55, Q101 ｜ `depth`: L3

### T02 — GraphRAG（追杀 A15–A26）

**Q112.** A19/A84 说早期 `limit=5` 的 smoke 用 `qwen-plus`、profile 对齐后才换 `deepseek-v4-flash`——`7928df50` 那次记下 baseline 1.00 / local 0.80 的 audit，用的是哪个模型？
> `intent`: audit 与 rerun 是否同模型 ｜ `callback`: A15, A19, A84, Q19 ｜ `depth`: L3

**Q113.** 如果 audit 是 qwen-plus、rerun 是 deepseek-v4-flash，那 local 从 0.80 回到 1.00 该归因给 fusion 修复还是换模型——你今天能排除哪一个？
> `intent`: 归因混淆（本轮最高价值） ｜ `callback`: Q112, A20, A85 ｜ `depth`: L3

**Q114.** A20/A85 把 baseline 自己 `MRR@10` 0.90→1.00 解释成「样本波动大」，但 A19 同时说了跨轮换过模型——你为什么不把这两件事连起来讲？
> `intent`: 跨答未对齐的因果解释 ｜ `callback`: A20, A85, A19, Q112 ｜ `depth`: L3

**Q115.** rerun `3da5d742` 排在 fusion → seed → alias → path 之后，所以那个 1.00 是**全配置**结果；简历说「同日 rerun 不再低于 baseline」——这 7 个提交是同一天做完的吗，那句结论证明了哪个机制？
> `intent`: 结果归属 + 同日时间线 ｜ `callback`: A16, A19, A20, Q19 ｜ `depth`: L3

**Q116.** A21 把简历的「尚未执行」改写成「跑不了（`BLOCKED_PENDING_DATA`）」，理由是「本机连 HotpotQA 官方源 TCP 超时、`data/evals/multihop/` 不存在」——这是「没做」还是「做不了」，两者责任归属不同。
> `intent`: 缺口 vs 阻塞的口径移动 ｜ `callback`: A21, A86, Q21 ｜ `depth`: L3

**Q117.** A97/A98 说 comparison / bridge / genealogy 三类 query 上有 guardrail「硬替换 top」——这个硬替换会不会把 baseline 已命中的 gold 又挤出去，从而破坏 A17 的 baseline-preserving 不变量？
> `intent`: 两个机制是否互斥 ｜ `callback`: A97, A98, A17 ｜ `depth`: L3

**Q118.** 如果 guardrail 能在某些 query class 上覆盖 baseline rank 下限——那「不劣于 baseline」到底是全局不变量，还是只在排序阶段成立、在最终输出上不成立？
> `intent`: 不变量的作用域 ｜ `callback`: Q117, A17, A69 ｜ `depth`: L3

**Q119.** A18 说 `GRAPH_PROMOTION_THRESHOLD=6` 与 graph-only 的 `≥9` 是手定的、无 calibration——这两个数最初是从哪条具体失败形态反推出来的，还是拍的？
> `intent`: 常数来源 ｜ `callback`: A18, Q18 ｜ `depth`: L2

**Q120.** A17 的 `_graph_signal()` 把四个语义不同的计数器（support / seed_hit / file_focus / path）直接整数相加再比 6 和 9——为什么不分别设阈或归一化？
> `intent`: 打分设计的合理性 ｜ `callback`: A17, A18, A88 ｜ `depth`: L3

**Q121.** A88 说 `_score_path` 返回 6 元整数元组、权重手定、验证只到单测——这 6 个分量在跑 HotpotQA 之前有没有做过任何一次人工排序对齐？
> `intent`: 打分是否被验证过 ｜ `callback`: A88, Q88 ｜ `depth`: L3

**Q122.** A68 说你举不出一个「删掉图路由会变差」的 query——那这层今天存在的唯一**已记录**收益是什么，只剩「不劣于 baseline」吗？
> `intent`: 收益为零的复杂度 ｜ `callback`: A68, A22, Q68 ｜ `depth`: L3

**Q123.** A67 说 `GENERIC_ENTITIES`（Introduction / Overview / High / Low）与 `founded by` / `maternal grandfather` / `director of` 全是英文——一个天津法院的法律平台，为什么整套多跳机制按英文问答数据集的关系类型来建？
> `intent`: 域适配的根本问题 ｜ `callback`: A67, A24, Q67 ｜ `depth`: L3

**Q124.** A24/A67 说中文法律主体上有已知误合并风险、且从未测过——那这套检索在它真正的目标域上有没有跑过一次，哪怕一次人工看结果？
> `intent`: 目标域零验证 ｜ `callback`: A24, A67, Q24 ｜ `depth`: L3

**Q125.** A15 说被挤出的是 `Ed Wood`（电影）和 `Shirley Temple`（人）、两条 question id 是 `5a8b57f2…` / `5a8c7595…`——这两类实体与法院卷宗里的主体（公司、法人、案号）有什么共同点，值得同一套 seed/路径机制复用？
> `intent`: 机制可迁移性 ｜ `callback`: A15, A67, A23 ｜ `depth`: L3

**Q126.** A25 说 `local_graphrag` 平均时延 15806→18503 ms，是本地进程内重建图路径的数字——生产路径上这套东西的时延量级你估得出来吗，估的依据是什么？
> `intent`: 代价在生产尺度上的外推 ｜ `callback`: A25, Q25 ｜ `depth`: L3

### T03 — Memory / Context（追杀 A27–A36）

**Q127.** A28 说 `d4e2fe2` 是 `GeneralAgent.prepare_context()` + 回合后写入，A55/A71/A30 说真实路径是 `agent/runtime/nodes/core.py` 的 build_context → `build_context_pack` —— `GeneralAgent.prepare_context` 今天是 live path，还是和 ContextOrchestrator 一样没有生产调用点？
> `intent`: 两个集成点哪个活着 ｜ `callback`: A28, A55, A71, Q28 ｜ `depth`: L3

**Q128.** 如果 `prepare_context` 也不在 live path 上，那简历第 4 条「接入 Agent 调用前读取与回合后写入」描述的是哪条链？
> `intent`: 简历条目与 live path 的对应 ｜ `callback`: Q127, A55, A71 ｜ `depth`: L3

**Q129.** A55/A71 说 ContextOrchestrator 是没有 consumer 的抽象——它是这轮的产物还是更早的遗留；如果重做，你会删掉它还是把它挂到真实入口上？
> `intent`: 无 consumer 组件的归属与处置 ｜ `callback`: A55, A71, Q55 ｜ `depth`: L2

**Q130.** A29/A70 说 runtime 侧 `agent_id` 硬编码成 `"agent_run"`——那四维 `MemoryScope` 今天实际生效的是几维？简历说的「作用域」还剩下什么？
> `intent`: 声称的机制与实际生效维度 ｜ `callback`: A29, A70, Q29 ｜ `depth`: L3

**Q131.** A33 说没有后台 reaper、状态没刷新就挡不住 stale——那 stale 状态是由谁在哪一步写的，写入方是同步写还是靠调用方自觉？
> `intent`: 状态刷新的归属 ｜ `callback`: A33, A96, A30, Q33 ｜ `depth`: L3

**Q132.** A30 说写入在 `post_turn_commit` 一个 UoW 里一次写 raw event / task summary / version / context pack / usage trace——失败时置 `memory_persistence_unavailable` 只影响读回吗，会不会让 run 看起来成功但记忆静默丢了？
> `intent`: 失败语义与静默降级 ｜ `callback`: A30, A33, Q30 ｜ `depth`: L3

**Q133.** A34 说同一 version 不会被双激活，但两条内容冲突的 memory 不会被仲裁——那 review 的人看得到「两条冲突候选并列」吗，还是它们各自独立走到 APPROVED？
> `intent`: 冲突可见性 ｜ `callback`: A34, A31, Q34 ｜ `depth`: L3

**Q134.** A31/A100 说 recall eligibility 属于 08 但今天没接上、实际生效的是 scope + APPROVED——这个缺口有没有被记成一条待办，还是就这样放着？
> `intent`: Target/Current 差距的处置 ｜ `callback`: A31, A100, A29 ｜ `depth`: L2

**Q135.** A35 说没有 A/B、ADR 0007 的 memory kill test 阶梯没跑——这个 kill test 阶梯是你起草的、别人起草的，还是从框架文档里搬的？
> `intent`: Ownership（判据的来源） ｜ `callback`: A35, A76, Q35 ｜ `depth`: L2

**Q136.** A35 说 PR #8 记了 focused tests 32 passed / repo 66 / legacy 11 / 三 profile contract eval ok——这些数是你跑的还是 PR 描述里抄的，那 32 条锁的是哪些行为？
> `intent`: Evidence 粒度与来源 ｜ `callback`: A35, A28, Q35 ｜ `depth`: L3

**Q137.** A36/A76 的删除判据是「没有稳定边际收益就关掉」——那这套 structured memory 从上线到今天，有没有留下任何一次**人工使用它**的记录？
> `intent`: 使用痕迹 vs 设计 ｜ `callback`: A36, A76, A35 ｜ `depth`: L3

### T04 — Runtime（追杀 A37–A43）

**Q138.** A38 先给状态机 `DRAFT → ACTIVATED → SUPERSEDED`，随后代码里是 `DRAFT/VALIDATING/ACTIVE/SUPERSEDED`——哪一套是真的，多出来的 `VALIDATING` 是谁加的？
> `intent`: 同题干内的状态命名矛盾 ｜ `callback`: A38, Q38 ｜ `depth`: L3

**Q139.** A38 说 PlanVersion 冻结「运行因果」、不冻结工具/prompt/模型版本，具体版本记在 StepRun 的 resolved input-version set 上——恢复时谁来比对这两个集合，Runtime 还是各 Owner？
> `intent`: 兼容性判定的归属 ｜ `callback`: A38, A41, Q38 ｜ `depth`: L3

**Q140.** A39 说晚到结果要重新验收、且若它对应已发生的现实 Effect 就不能否认——那如果它「纯计算但基于旧材料」，你今天走的是 reject 还是重算？代码里是哪一支？
> `intent`: late result 的实际分支 ｜ `callback`: A39, A40, Q39 ｜ `depth`: L3

**Q141.** A42 说 canonical graph 不把 LangGraph `BaseCheckpointSaver` 当权威，但 `phase08.py` 里又引入了官方 `PostgresSaver`——这两套 checkpoint 同时存在吗，runtime 恢复时实际读的是哪份？
> `intent`: 双 checkpoint 的真实关系 ｜ `callback`: A42, A41, Q42 ｜ `depth`: L3

**Q142.** A42 说 `interrupt()` 恢复会从节点起点重跑、所以 interrupt 前的可见副作用必须幂等——你们的图里哪个节点真的这么拆了，还是这条只是约束、没落地？
> `intent`: 框架限制的实际处理 ｜ `callback`: A42, A46, Q42 ｜ `depth`: L3

**Q143.** A41 的恢复顺序是「load checkpoint → 02 Receipt → 06 Effect → 08 授权 → 03/05/07 → 修 Runtime」——这是文档里的 Target，还是代码里真的按这个次序执行？
> `intent`: 恢复顺序的实现度 ｜ `callback`: A41, A40, Q41 ｜ `depth`: L3

**Q144.** A43 的 A/B/C 对照里 A 臂是「Generic Host + Legal Skills」——你们有没有真的拿一个通用 Agent Host 跑过哪怕一次对照，还是这条对照一直停在设计？
> `intent`: 替代方案是否真被比较 ｜ `callback`: A43, A14, Q43 ｜ `depth`: L3

**Q145.** A37 举的「合同争议并行三分支 + 补充协议改写付款日期」那次 case 是真发生过的，还是为了回答必要性现推的？
> `intent`: 必要性论证的实例真实性 ｜ `callback`: A37, Q37 ｜ `depth`: L2

### T05 — Security / Effect（追杀 A44–A50）

**Q146.** A44 说 send 前重新校验两次（一次在 prepare/approval 之后、一次在 audit 之后），A46 的调用序列里只出现一次 reauth（`:462`）——第一次调用落在哪一行，为什么 A46 没列出来？
> `intent`: 两答的机制细节对齐 ｜ `callback`: A44, A46, Q44 ｜ `depth`: L3

**Q147.** A49 说「当前没有后台 reconciler」，但又有 `escalate_due_reconciliations` 按 900 秒把 OPEN 升成 MANUAL——这个 escalate 是谁触发的，请求驱动、定时任务还是运维手工？
> `intent`: 无人驱动的时间阈值 ｜ `callback`: A49, A48, Q49 ｜ `depth`: L3

**Q148.** A49 说人工结论要求「授权 reviewer principal」，A49 的边界又说 reviewer 的 role / tenant / approval-policy binding 未证明——那今天跑起来的 `record_manual_effect_assessment` 实际拿什么身份过的？
> `intent`: 人工兜底是否真能跑通 ｜ `callback`: A49, Q49 ｜ `depth`: L3

**Q149.** A48 说对外是 `UNKNOWN_EFFECT` + `reconcile_required`，但 Target 里的 `WAITING_RECONCILIATION` 在 src 里不存在——那今天 Run 到底是停了，还是收到 receipt 后继续往下走？
> `intent`: 「设计上停」与「今天停」的差别 ｜ `callback`: A48, A13, Q48 ｜ `depth`: L3

**Q150.** A47 把 AUD-L1（verified）与 AUD-L2（crash/restart lifecycle 未证明）分开——AUD-L2 若在真实 Provider 上触发，最坏会呈现什么状态，用户会看到什么？
> `intent`: 未证明窗口的真实后果 ｜ `callback`: A47, A46, A50 ｜ `depth`: L3

**Q151.** A44 的正向证据是「epoch 在 send 前被 revoked 时 executor 调用 0 次」（#203 / `34560042535`）——这个 fault probe 注入的 revoke 是打在 gateway 内部，还是模拟一个外部撤销？
> `intent`: 正向证据的注入点 ｜ `callback`: A44, A46, Q44 ｜ `depth`: L3

**Q152.** A45/A100 说授权不能由模型/Runtime/Tool 放宽、08 拥有 policy decision——这套九模块的 authority 划分是你在做 effect 这段时设计的，还是后来团队系统化时成文的？
> `intent`: Ownership Interrupt（这套控制面归谁） ｜ `callback`: A45, A54, A14, Q45 ｜ `depth`: L2

### T06 — Project History（追杀 A51–A59）

**Q153.** 简历写 2026.03 加入，A51 说公开根提交 `eafeb1c2` 是 2026-04-15 且与你第一笔可自证提交同日——那 3 月到 4 月 15 日之间你在这个仓库里做了什么，为什么公开历史里看不到？
> `intent`: 时间线空窗 ｜ `callback`: A51, A52, Q51 ｜ `depth`: L3

**Q154.** A51 说 before 状态只能从 `77346758` 的父提交看——那 4 月 15 日之前你有没有任何一次写的代码 / 设计 / 文档能被今天复核？
> `intent`: before-state 的可复核性 ｜ `callback`: A51, A52, A53 ｜ `depth`: L3

**Q155.** A52 说 `77346758`「没有关联 PR、Review 或历史 status check」——一个删两个文件、改写主 Agent 的重构为什么没走 PR，当时的流程是什么？
> `intent`: 工程流程的真实性 ｜ `callback`: A52, A57, A58 ｜ `depth`: L3

**Q156.** A54 把个人切片限定在 Tool/MCP、GraphRAG、Context/Memory 三条——这三条之外，你这几个月还做过什么没写进简历的？
> `intent`: 简历覆盖面 vs 实际工作 ｜ `callback`: A54, Q54 ｜ `depth`: L2

**Q157.** A58 说 `0b5fb350` 是跨工具/Knowledge/模型/Docker/脚本的大提交、只能「安全提取子集」——这个提交里有几成是你写的，剩下的谁写的，你的提取标准是什么？
> `intent`: 混合提交的切分 ｜ `callback`: A58, A52, Q58 ｜ `depth`: L3

**Q158.** A55/A78 是你主动说「ContextOrchestrator 没有生产调用点」「`KnowledgeGeneration` 在 src 里搜不到」——如果是 30 分钟口语面试，你有多大概率会主动讲这两条，而不是被追问才说？
> `intent`: 主动披露 vs 追问才承认 ｜ `callback`: A55, A78, A71 ｜ `depth`: L2

**Q159.** A56 说 direct route 准入的 decision owner 是 Unknown、`docs/decisions/` 里没有对应 ADR——一条影响**所有请求分流**的规则为什么没有任何决策记录？
> `intent`: 决策治理的缺口 ｜ `callback`: A56, A8, Q56 ｜ `depth`: L3

**Q160.** A57 说今天有一个 main run（`35516807526`，224 passed）——这个 run 是这次面试前专门跑的，还是日常流水线上的最近一次？它覆盖了哪些 4 月的路径？
> `intent`: 当前证据的时效与动机 ｜ `callback`: A57, A52, Q57 ｜ `depth`: L2

**Q161.** A1/A52 反复说「作者字段区分不出个人与团队」——这句是仓库的书面口径，还是你自己为了保护边界说的？两者的可信度不一样。
> `intent`: 边界口径的来源 ｜ `callback`: A1, A51, A52, Q1 ｜ `depth`: L2

### T07 — Pilot / 法院（追杀 A60–A67）

**Q162.** A59–A66 七条答案全部落在 Unknown——那简历把「法院侧测试与 Pilot Validation」写进项目简介，对读简历的人提供了什么可验证信息？
> `intent`: 简历 bullet 的信息含量 ｜ `callback`: A59, A60, A62, Q62 ｜ `depth`: L3

**Q163.** A62 说这条边界是「取证边界」而不是人为决策——那「只写到 Pilot 为止」这个写法本身是你在准备简历时定的吗？
> `intent`: 简历边界的作者 ｜ `callback`: A62, A51, Q62 ｜ `depth`: L2

**Q164.** A61 说历史性能指标（QPS/Latency/Token/Cost/HA/DR）在台账里就是 UNKNOWN——这套台账是谁维护的，你在里面提交过条目吗？
> `intent`: 证据台账的 Ownership ｜ `callback`: A61, A59, Q61 ｜ `depth`: L2

**Q165.** A63 说 PF-017 只确认客户反馈过「回答质量还需要提高」——这条反馈通过什么渠道来的，你本人看到过原文吗？
> `intent`: 一手证据 vs 转述 ｜ `callback`: A63, A60, Q63 ｜ `depth`: L3

**Q166.** A64/A65 说 Pilot 没有 pass/fail 判据、也没进 Production 的原因不可考——如果连这两条都不知道，你当时在项目里的位置离 Pilot 有多远？
> `intent`: 从证据缺口反推参与深度 ｜ `callback`: A64, A65, A59 ｜ `depth`: L3

**Q167.** A66 说 `COURT QA: UNKNOWN / NOT AVAILABLE`——那这套系统最后一次被法院侧的人碰到是什么时候，你有没有任何印象（哪怕不可复核）？
> `intent`: 记忆 vs 台账 ｜ `callback`: A66, A61 ｜ `depth`: L2

**Q168.** A67 说没在中文卷宗上测过 GraphRAG——如果给你三天和一份真实卷宗样本，你会先测哪一件事来判定这套检索在法院域能不能用？
> `intent`: 从 Unknown 到一个可执行判据 ｜ `callback`: A67, A24, Q67 ｜ `depth`: L3

### T08 — 系统简化 / Delete（追杀 A68–A76）

**Q169.** A68 说第一步该动的是 baseline-preserving 融合而不是整层图路由——但那条融合恰恰是唯一有「不劣于 baseline」证据的部分，删它的依据是什么？
> `intent`: 减法顺序的依据 ｜ `callback`: A68, A69, Q68 ｜ `depth`: L3

**Q170.** A69 说「把图权重调到 0 就是 full-minus-H1 的一个臂」——你们有没有真的跑过一次权重 0，还是这只是一个可执行的实验设想？
> `intent`: 更简单方案是否被实测 ｜ `callback`: A69, A18, Q69 ｜ `depth`: L3

**Q171.** A86 说「如果 Red 主张没 ablation 就该先 Defer 掉，我不反驳」——这是你真实的工程判断，还是对面试压力的让步？换你自己的项目你会怎么处理？
> `intent`: 让步 vs 判断 ｜ `callback`: A86, A26, Q86 ｜ `depth`: L3

**Q172.** A73 挑「别名归一化」最该删，A74 却留 seed expansion——如果别名归一化删了，A74 说的「seed 命中不到图节点」这条失败形态由谁覆盖？
> `intent`: 两答之间的依赖关系 ｜ `callback`: A73, A74, Q73 ｜ `depth`: L3

**Q173.** A23 说 seed 会带 `alias` 标签——也就是别名归一化的输出直接喂进 seed expansion；那这两个机制其实是一个，为什么按两个预算它们的边际收益？
> `intent`: 机制是否被人为拆成两个 ｜ `callback`: A23, A73, A74 ｜ `depth`: L3

**Q174.** A75 说自研 delta 是「暴露、注参、准入」三件——如果成熟 MCP Host 已经带 per-user config（不少已经支持），第一件还剩多少 Delta？
> `intent`: Build/Buy 的真实 Delta ｜ `callback`: A75, A14, Q75 ｜ `depth`: L3

**Q175.** A55/A71 说 ContextOrchestrator 今天删掉不损失任何东西——那它当初为什么会被建出来，是谁需要它？
> `intent`: 无 consumer 组件的成因 ｜ `callback`: A55, A71, A28, Q71 ｜ `depth`: L2

**Q176.** A36/A76 的删除判据都是「测量没有稳定收益就删」——但测量今天是 `MEASUREMENT_BLOCKED`；按这个判据，所有可选层今天是该留还是该删？
> `intent`: 判据在阻塞状态下的后果 ｜ `callback`: A36, A76, A21, Q76 ｜ `depth`: L3

**Q177.** A42/A43 说 Native Runtime 的必要性是 `not established`——那在被证明之前，今天自研的这部分 Runtime 靠什么理由继续维护？
> `intent`: 无证据的保留理由 ｜ `callback`: A43, A42, A41 ｜ `depth`: L3

**Q178.** A78 说 `KnowledgeReadinessEvidence` 要凑齐 30 个 requirement id——这个 30 是怎么来的，是不是又一个手定常数？
> `intent`: 新的手定常数 ｜ `callback`: A78, A80, A18 ｜ `depth`: L2

### T09 — Knowledge / Retrieval（追杀 A77–A88）

**Q179.** Q78 的前提是「你简历里的 `KnowledgeGeneration`」，但冻结简历里没有这个词——你当时为什么没有先纠正这个前提，而是按它存在直接作答？
> `intent`: 前提校验 / 对自己简历的熟悉度 ｜ `callback`: A78, Q78, A55 ｜ `depth`: L2

**Q180.** A77 说靠「原子切换 ServingPointer」判断检索侧切到新版，同题边界又说这是 Target/Gap——那今天文档更新之后，检索侧实际靠什么避免读到旧 embedding？
> `intent`: Current 下的真实机制 ｜ `callback`: A77, Q77 ｜ `depth`: L3

**Q181.** A78 说 `src/` 里 literal `KnowledgeGeneration` 无命中，但 A77/A80 都用它描述机制——是文档先行、代码未跟，还是它在代码里换了别的名字？
> `intent`: 概念与实现的对应 ｜ `callback`: A78, A77, A80 ｜ `depth`: L3

**Q182.** A81 说 Citation 存 `document_version_id` + `source_span_id`、原文改了宁可拒绝也不指错——用户看到「引用被拒」时的产品表现是什么，空答案、报错还是降级回答？
> `intent`: 护栏的用户可见后果 ｜ `callback`: A81, A79, Q81 ｜ `depth`: L3

**Q183.** A79 说删除走 `visibility_revoked → cleanup_requested → physically_deleted → verified`——这条生命周期今天有几步真的会被走到，还是只有第一步会被触发？
> `intent`: 生命周期的实现度 ｜ `callback`: A79, Q79 ｜ `depth`: L3

**Q184.** A82 说 zero-evidence 只能证明「我没检索到」——那今天面向用户、遇到全案无相关内容时，系统实际回的是什么？
> `intent`: 「证明没有」的当前产品行为 ｜ `callback`: A82, Q82 ｜ `depth`: L3

**Q185.** A80 说 `PARTIAL` 必须带「覆盖了什么、缺了什么」——这个覆盖计算需要知道「这个任务该覆盖什么」，那份范围定义今天存在吗，谁维护？
> `intent`: 覆盖语义的前置条件 ｜ `callback`: A80, A82, Q80 ｜ `depth`: L3

**Q186.** A83 说 `limit=5` 是样本条数、`top_k` 默认 10、`rerank_top_k = min(top_k,5)`——那简历里「`limit=5` smoke 中被挤出 Top-K」的 Top-K 指的是 rerank 之后的 5，还是候选的 10？
> `intent`: 简历数字的准确含义 ｜ `callback`: A83, A20, Q83 ｜ `depth`: L3

**Q187.** A99 说向量侧是 Chroma HNSW、小 K 召回损失没测过——那你们凭什么认定「被挤出 top5」是 graph 造成的，而不是 ANN 抖动加 5 条小样本？
> `intent`: 归因的替代解释（ANN） ｜ `callback`: A99, A15, Q99 ｜ `depth`: L3

**Q188.** A99 说 Milvus 走 `MilvusLiteClient`，A28 说 Memory V1 默认 Chroma——两套向量库同时存在时，哪一套服务知识检索、哪一套服务记忆，是有意分开的吗？
> `intent`: 双向量库的职责划分 ｜ `callback`: A99, A28, Q99 ｜ `depth`: L2

**Q189.** A82/A79 说负证据条件在 Gap 清单里——有没有一个明确条件会让你们决定「这条缺了以后就永远不宣称全案没有」？
> `intent`: Gap 的收敛条件 ｜ `callback`: A82, A79, A26 ｜ `depth`: L3

### T10 — 工程基础（追杀 A89–A100）

**Q190.** A5/A89 用「`call_args` 是本次调用的局部对象」证明配置不串——那 `mcp_user_config_resolver` 自己有没有按 `(user_id, server_id)` 缓存？如果有且没有失效策略，隔离还在吗？
> `intent`: 隔离论证的完备性 ｜ `callback`: A5, A89, Q5 ｜ `depth`: L3

**Q191.** A6/A90 说今天用显式参数、ContextVar 只用于 tracing——那 `platform/common/contexts.py` 里的 `user_id` ContextVar 与显式传的 `user_id` 会不会不一致，冲突时谁赢？
> `intent`: 双来源身份的一致性 ｜ `callback`: A6, A90, Q90 ｜ `depth`: L3

**Q192.** A91 说 tool 路径上没有 `asyncio.gather`——那 GraphRAG 的多路检索（vector / BM25 / graph）是怎么并发的：顺序、gather，还是框架内部并发？
> `intent`: 并发模型的实际形态 ｜ `callback`: A91, A17, Q91 ｜ `depth`: L3

**Q193.** A91 说 cancel 在 send 之后只是「可选尝试」——那你们今天有没有一个远端 Tool 支持真正的 cancel，还是这条规则从来没有被触发过？
> `intent`: 规则的实现度 ｜ `callback`: A91, A11, Q91 ｜ `depth`: L3

**Q194.** A92 说只有 `KNOWN_NOT_SENT` 才允许重试——从持久化 Attempt 到真正 socket send 之间仍有一个窗口，你怎么保证那条 Attempt 的写入与这次 send 是同一个动作？
> `intent`: 持久化与网络栈之间的窗口 ｜ `callback`: A92, A11, Q11 ｜ `depth`: L3

**Q195.** A94 说 `MemoryUnitOfWork` 用 `connection.begin()`、未显式设隔离级别，PostgreSQL 默认 READ COMMITTED——那 CAS 能防 lost update，能防「读到未提交的另一条 memory 再基于它写」吗？
> `intent`: 隔离级别与业务语义 ｜ `callback`: A94, A34, Q94 ｜ `depth`: L3

**Q196.** A95 说没逐点审计「是否有地方把模型调用包在写事务里」——你怎么在代码层面搜这类反模式，有没有一条静态检查或 CI 规则？
> `intent`: 从抽查到可执行的检查 ｜ `callback`: A95, Q95 ｜ `depth`: L3

**Q197.** A96 说 review 列在 DB、过滤在应用层、没有 TOCTOU 护栏——如果把过滤下沉成 SQL 谓词（`WHERE review_status='approved'`），这个 TOCTOU 会不会自然消失？
> `intent`: 是否存在更简单的修法 ｜ `callback`: A96, A31, Q96 ｜ `depth`: L3

**Q198.** A97 说代码里算了 `fusion_score` 但只写进 metadata、不参与排序——一个不影响任何决策的计算为什么还在跑，它的意义是什么？
> `intent`: 死计算 ｜ `callback`: A97, A17, Q97 ｜ `depth`: L2

**Q199.** A98 说 gate（离散资格）与连续融合分数学上不相容——这套「过滤后重排」在 IR 里有没有成熟做法，你们查过吗，还是重新发明的？
> `intent`: 自研 vs 已知方案 ｜ `callback`: A98, A97, Q98 ｜ `depth`: L3

**Q200.** A100 说「模型永远不赢」、冲突仲裁各自回到自己的 Owner——有没有一个**实际遇到**过的场景是这三个 Owner 判断直接冲突的，还是它一直是设计上的不变量？
> `intent`: 不变量有没有被真实压力测过 ｜ `callback`: A100, A31, Q100 ｜ `depth`: L3

---

## 附录：本次实际打开的文件

| # | 文件 | 状态 |
|---|---|---|
| 1 | `D:\projects\zuno\.agent\red-blue\attack-model.md` | 允许（Red Skill，完整读） |
| 2 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\01_simulated_resume.md` | 允许（冻结简历） |
| 3 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\02_red_questions.md` | 允许（Red Wave 1 的 100 题） |
| 4 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\03_blue_answers.md` | 允许（主材料） |

**越界打开：无。**
**唯一一次越界工具调用尝试：`wc -l -c` 在 `03_blue_answers.md` 上取行数/字节数——只作用于已允许文件，未读取其他路径。**
**未打开（遵守禁令）：** `03_blue_architecture_notes.md`、`04_blue_wave2_answers.md`、`04_blue_wave2_architecture_notes.md`、`04_red_evaluation.md`、`docs/**` 下的 canonical 文档、`src/**`、`tests/**`、任何 Evidence、`docs/red-blue/rounds/**`。

**自我申报的诚实边界：** 本报告对 `文件:行`、commit SHA、run id、测试名的全部判断都是**结构判断**，不是核实。我未打开任何源码或 Evidence，因此无法确认 A1–A100 中任何一条引用是否指向它声称的东西。
