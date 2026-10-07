# Red Wave 2 — Blind Evaluation + 100 Follow-ups

```text
round: rb-2026-10-07-formal-020
blind: true
seen: 01_simulated_resume.md, 02_red_questions.md, 03_blue_answers.md, attack-model.md
not_seen: 03_blue_architecture_notes.md, canonical docs, source, Evidence
```

---

## Part A — Blue Wave 1 Blind Evaluation

先给一个方法论上的前提，因为它决定我怎么读这 100 个回答。

Blue 的 100 答有一个非常统一的形态：**第一层口语 → 第二层展开 → `事实层 / 证据(file:line) / 边界` 三段收口**，而且几乎每一题的"边界"都在**主动削减自己的 claim**。这个形态本身就是一份信息：它说明候选人（a）确实在这套评测标准下训练过，或者（b）回答是被优化给评测器看的。我在 A80 的证据字段里抓到了直接的证据——他引用 `docs/governance/interview-acceptance-standard.md（§9 简化信号）` 作为"模块 09 该被质疑"的理由。**他把面试验收标准当成了他判断的技术依据。** 这件事我下面会反复用到（Q183）。

这带来一个不寻常的局面：**他把全部可信度押在了 file:line 的精度上**。A1 到 A100 里的每一个机制陈述都挂了 `src/...:行号`。这是一个**全有全无**的结构——只要有一处引用是编的，整轮崩塌；只要引用都能对上，他就是我这几年见过最诚实的一类候选人。我作为盲面试官无法核实，所以我只能评价**他讲得可不可信**，不能评价他对不对。

### 1. 哪些 Claim 已经可信（信任上升）

我信的部分，共同特征是：**自曝的方向是"削减自己"并且削减的是可交付物本身**。骗一个人去承认"我没实现"比让他承认"我实现了"要难得多。

- **A83 / A90（引用不可点开）** —— 他说服务端 `api/v1/` 没有 span/citation 解析端点、前端 `apps/web/src` 的 citation 是个纯 chip、没有 click handler，并且 `source_span_id` 可能是 span dict 的 SHA-256，**id 相等不蕴含位置相等**。他还主动纠正"我一开始想当然以为客户端高亮，是错的"。这是本次最可信的一段之一：一个想演的人会把这里演成"前端高亮已实现"。
- **A39（ADR-0005 与主线的矛盾）** —— ADR 要求官方 saver 唯一，主线却是自研桥；官方 saver 只在 `phase08.py` 接上且无 caller；还有一条测试**反过来禁止**存在一个 cutover 文件。这种"制度文件和真实实现不一致"的自曝，是极强的真实性信号——它不像编的，因为编的人不会编一个"我们自己违反了 ADR 且没人发现"的故事。
- **A36（两存储无 2PC）** —— `DOMAIN_COMMIT_BEFORE_CHECKPOINT` 这个崩溃点被命名、`recovery_rule ∈ {DOMAIN_WINS, CHECKPOINT_REPLAY, ESCALATE}`、domain+outbox 同事务而 checkpoint 是另一个引擎。密度和自洽度都很高。
- **A43（epoch 没有撤销生产者）** —— 他 grep 完整个 `src/backend/zuno`，结论是 `security_effective_epochs` 只有 INSERT/JOIN/SELECT，**唯一把 status 改成 revoked 的是测试里的裸 SQL**。这句话的杀伤力他自己是知道的（他称它"今天最想主动交代的一个洞"）。我信这段。
- **A47（对账无 reader/无执行器）** —— 对账查询描述"只被写入和被 hash，没有 reader、没有执行器"。同上，这是自曝。
- **A22（`agent_id` 被写死成 `"agent_run"` 且无消费方）** —— 一个 typed contract 里的一维是个死字段。细节具体、方向对自己不利。
- **A86 / A94（两套融合实现 + 主动纠正 A86 的"并行"错误）** —— 他说仓库里有**两份答案**：产品侧是字典序 tuple，agentic 侧是真 RRF、`rrf_score += 1.0/(60.0 + rank)` 且 k=60 硬编；然后在 A94 里把自己在 A86 里说的"三路并行、超时就返回"直接撤回，改口成顺序 await。**自己能推翻自己上一答的人，可信度是往上走的。**
- **A92 / A94 / A95 / A97（工程基础）** —— 教科书级正确。A92 分清"语句内读"与"读-改-写拆到语句外"；A94 分清 coroutine 取消 ≠ 远端终止；A95 分清 `create_task` 拷贝 context 而 `run_in_executor` 不继承；A97 分清 `CancelledError` 继承 `BaseException`。这四题他不是背定义，是在解释语义边界。
- **A11（具体 bad case）** —— `Ed Wood`、`Shirley Temple` 被挤出 Top-K，回归里固化的是 `Sinister (film)` 不能进 top5。具体到片名，这不好编。
- **A52 / A59（blame 不可拆）** —— 他给出的理由是结构性的：仓库里"人"几乎只有一个身份谱系（`ProfessorZhi` / `WenHi Huang` / `vince` 同一邮箱），其余是自动化账号。这不是借口，这是可核的事实形态。

### 2. 哪些只有术语、缺实现

这一类我不是说他在编，而是说**他给不出这名词在代码里长什么样、或者给出来的东西没有依据**。

- **A3（bullet 1 的动机）** —— 他的边界原话："'漏传会静默降级'是我今天从代码结构推出的解释，我没有当时那版代码的失败记录。" 也就是说，**整条 bullet 1 的问题必要性（为什么必须删掉子 Agent 转发层）是他事后重建的**。术语（"配置隔离"）有了，当年的 failure 没有。
- **A8 / A100（direct route）** —— 这是本轮最重的一处术语塌陷。他自己说：`src` 里**不存在** `direct_route` / `falls back to ReAct` 这样的字面量；**没有任何一条断言"多步 query 应该回落到 ReAct"**；而且 canonical runtime 里 `plan_kind == "tool"` 被显式映射成 `StrategyMode.REACT`。所以简历里"收紧 Workspace Tool 路由 / 用回归测试固定路由边界"这句话，**在代码里没有对应的物**。他承认"这句简历措辞在今天代码里的对应物比它读起来要弱"。
- **A15 / A16（graph signal）** —— 四信号等权相加（`graph_support_count + graph_seed_hit_count + graph_file_focus + graph_path_count`），他原话："我讲不出这四条信号为什么是等权相加的，没有权重依据可追。" 术语有了，依据没有。
- **A20（GraphRAG 的退出条件）** —— 他给出的"真正的退出条件"是测量性的，而测量 `BLOCKED_PENDING_DATA`。所以今天这层的存在理由是"测量缺席"，不是"被证明有效"。
- **A25 / A28（授权与 Domain 权威）** —— 支撑这两题的是 `docs/project/reference.md` 的**措辞**（"Provenance != Truth != Authorization"、"optional non-authoritative provider boundary"），不是代码里的裁决点。术语级正确，实现级空。
- **A29 / A30 / A40 / A50 / A80** —— 全部落在 `Target` / `Unknown`。这些不是错的，但它们**没有一个字是"已实现"**，读的时候不能当实现听。
- **A71 / A72 / A73（删模块）** —— 他承认"我没有统计过调用方数量"，"如果我给你一个清单，那是我凭印象编的"。整段减法实验是直觉，不是测量。
- **A81 / A82（两条 ready 链）** —— 他提出"这里有两条互不连通的真相链"、`ready` 在两条链上各有一个来源，但自己标注消费方未核对、产品侧那条链是否还在用也未确认。这是**发现**，不是**机制**。

### 3. 哪些 Ownership 不清

- **五条 bullet 没有一条是"从零写"（A53）** —— 他自己坚持这个前提不被省略，这一点我接受。但它同时意味着：**简历五条 bullet 全部是"在一个已存在系统上改"**。在此基础上，"我重构了 / 我构建了 / 我定位并修复了"这些动词的重量要整体下调。
- **A55 的时间线异常** —— 他能自证的 Tool/MCP 首笔和"直接绑定主 Agent 落地"**是同一天**（2026-04-15，`77346758`）。也就是说，简历第一条 bullet 的"重构"在这条线上**是我最早的改动之一**，不存在"先做别的、后来才动它"的历史。这既削弱"重构了长期遗留架构"的叙事，又和 A51 撞在一起（见下）。
- **A56：方向不是他提的** —— GraphRAG 图路由、planner 图开关在他之前就存在；他定的是 heuristic（seed expansion / 别名归一化 / path-aware ranking）和 9 个阈值。这个划线是清晰的，但要把"我定位并修复了排序回退"重新读成"在既有方向上做了很窄的一段"。
- **A41 的 Ownership 撤退** —— 他先说 `src/backend/zuno/security/` 不存在、安全在 `platform/security/`，然后明确"这一层不是我的 Ownership"。问题是：**A42–A48 他对这一层的细节（`_reauthorize_execute_epoch`、`assert_audit_durable_for_effect`、`DispatchCertainty`、`claim_idempotency_receipt`）讲得比对自己的 bullet 还细。** 一个"不是我的层"被讲到这个颗粒度，要么是他实际上摸过，要么是他在复述别人的设计。这两种我在盲态下**分不开**，所以要追（Q146）。
- **A21：需求不是他提的** —— "统一入口"这个需求是谁提 Unknown，能追的只有"方向层面的参与记录"，而那份参与产物（OpenViking）在 git 里没恢复。
- **A51 的存量基线** —— 他说不出一个"我亲眼看到它跑通的入口"。这条本身不要紧，但它与 A52 合起来形成一个很大的洞（见下）。
- **A65–A70：Pilot 的定性不是他给的** —— "Pilot Validation"是项目/架构文档的定性，没有法院侧验收文书；只有一条汇总反馈"回答质量还需要提高"。他承认"既然协议都没恢复，我不能把它讲成一次有第三方验收的测试"。所有权和证据都是空的。

### 4. 哪些数字 / Pilot / benchmark 可疑

这是我认为**最该被追的一节**，因为有两条数字在内部互相打脸。

- **最硬的一处自相矛盾：A11 与 A60 对 MRR@10 的两个版本对不上。**
  - A11 说：baseline `Recall@5=1.00 / MRR@10=0.90`，本地跑出来 `Recall@5=0.80 / MRR@10=0.80`。
  - A60 说：这条 bullet"有修复前后的指标（`Recall@5 0.80→1.00`，`MRR@10 0.80→1.00`）"。
  - 按 A11，baseline 的 MRR@10 是 **0.90**；按 A60，修复后是 **1.00**。也就是说**修复不但保住了 baseline，还超出了 baseline**。一个自称 `baseline_preserving`、自称"不是加权拼接、本质是保位"的改动，为什么会把 MRR@10 从 0.90 抬到 1.00？要么是 A60 记错了，要么 A11 的 baseline 记错了。这是他自己两答之间的差（Q113）。
- **A17 / A18：证据链的可复现性为零。** 5-query 怎么挑的 Unknown；原始报告 gitignore；`measurement_status: BLOCKED_PENDING_DATA`；limit=10/20/50 都不是 holdout。所以**他最强的一条 bullet，其数字既不可复现、也不构成分布证据**。
- **A16：9 个阈值没有任何依据。** 他自己说没有扫参、没有分布统计、代码里没有一行注释写理由，且 `measurement_status: BLOCKED_PENDING_DATA`。这是纯 post-hoc 拍值。
- **A17 里的 `enhanced Recall@5 = 0.98`** —— 他主动声明不把它当"优于 baseline"的证据（因为 limit=50 不是 holdout，且 baseline 是 1.00，0.98 其实**低于** baseline）。这个处理是诚实的，但它也暴露出 README 里的数会被误读。
- **A19：延迟/成本一个数都没有。** `MEASUREMENT_BLOCKED`。他给的是结构事实（顺序 await、`graph_hop_limit=2`、`max_paths_per_entity=10`），方向是"串行增量成本"。这个回答我信，但它意味着**GraphRAG 的成本账从未被算过**。
- **A63 / A67：Pilot 的使用强度和依赖性未知。** "持续用了几个月"这种话他不会讲，因为他没有数。连带 Q67（关掉会不会有人来问）也只能是 Unknown。
- **A66：`224 passed` 是固定快照的 CI run（`35516807526`），证据文档自己写 `FULL CI: NOT RUN`。** 这是一个**被截取**的测试基线，不是全量。
- **A69：可查的状态标签** —— `PRODUCTION_READINESS: NOT_ESTABLISHED`、`QUALITY: not_yet_proven`、`COURT QA: UNKNOWN`、无 QPS/latency/成本/高可用/容灾。这一组标签是全轮最有说服力的"这不是生产"证据，比任何形容词都硬。

### 5. 哪些 failure / 工程基础暴露薄弱

**工程基础本身（A91–A100）几乎没暴露薄弱**——A91、A92、A93、A94、A95、A97、A98 都是对的，A96 也是对的。薄弱不在基础层，而在**候选人自称做过的那套机制的 failure 覆盖**上。

- **A6：tool 执行那一步没有 `wait_for`。** 只有连接层 timeout（HTTP 连接 5s / SSE read 300s / streamable 30s+300s）在兜。`RuntimeLimits.timeout_ms` 存在但没有围着一次 tool 调用生效的定时器。也就是说**一个挂住的 tool 由谁来收**，他答不出来。这是硬功底题，答案不完整。
- **A7 + A47 + A96：幂等/重试的安全链有一个洞，而且是他自己指出的。** 幂等位 TTL **60 秒**；TTL 之外的收敛靠对账；而对账**没有 reader、没有执行器**（A47）。三条一叠，结论是：**"确定没执行才重发"这个守卫在 60 秒之后其实没有实现支撑。** 他在 A96 自己承认"安全是有条件的"。
- **A42：两次授权检查之间的 TOCTOU 窗口没有竞态测试。** 他从代码结构读出"落了 durable proof 之后、dispatch 之前要再查一次"，但承认"没有构造过竞态测试"。这是并发硬功底，答案停在"读出来的"。
- **A43：fail-closed 的门有、锁上了，但没人能转锁。** 生产侧没有任何代码路径会 revoke 一个 epoch。一个只在测试裸 SQL 下能触发的状态机分支，其"fail-closed"性质在生产里是未验的。他自认这是"今天最想主动交代的一个洞"。
- **A36：reconciliation 逻辑没有测试导入。** `phase08.py` 和 `planning/recovery.py` 在 `tests/` 里找不到 importer。"它被建模了"能自证，"它能修对"不能自证。
- **A5：并发注入没有对抗测试。** "不会串"是基于调用形态的判断，不是被测试固定住的事实。
- **A99：多轮并发写入没有对抗测试。** 他把兜底归给版本 CAS，并且明确 CAS 不是他这笔的贡献——这个划线很干净，但"CAS 能兜住"也只是结构判断。
- **A34 / A35 / A38 / A47 / A33：大量"写了但没接线"。** `append_plan_version` 无 caller、`BranchResultFencer` 无 caller 且它的唯一上游 `DynamicStepWorker` 也无 caller、`ParallelRecoveryPlanner` / `Phase21CrashRecoveryMatrix` 无 caller、`RecoveryAction.RESEND_OUTBOX` 没有任何地方执行它、`ReplayPort` 只有 in-memory 实现、对账无执行器。这串清单的规模本身就是一条 failure：**这个系统的"活路径"远窄于它的架构文档**。他每提到一处都在主动交代，但没有一次把这些合起来说"所以我的 A32–A48 有多少是活的"。

### 6. 哪些回答自己产生了新的攻击 handle

这是我最看重的一节，因为 Wave 2 的题应该长在这些 handle 上。

| handle | 出处 | 为什么是可攻击的 |
|---|---|---|
| `docs/governance/interview-acceptance-standard.md §9` | **A80** | 他判断"模块 09 该被质疑"的技术依据，是一份**面试验收标准**。这把"技术判断"和"面试表现优化"划到了一起，直接动摇前面所有"边界"字段的性质 |
| `docs/governance/rb019-graphrag-ablation-protocol.md` | A12/A16/A18/A20 | 协议编号是 `rb019` —— **上一轮 Red/Blue round 的产物**。他的"退出条件是测量性的"整套论证，挂在一个**面试流程产物**上，且状态是 `BLOCKED_PENDING_DATA` |
| `docs/evidence/implementation-wave-001.md` 负向历史 #201/#203/#205/#207 | A48/A49/A76 | 他的"演进动因"全部来自负向历史条目；而 #203 的描述本身就是"测试用裸 SQL 改 epoch" |
| `docs/decisions/0005-...` + 一条禁止 cutover 文件的测试 | A39 | 制度与实现的分裂，且有一条测试在**守护这个分裂** |
| `multi_agent_enabled` 字段存在但无 reader | A54 | 多 Agent 设计的残骸在仓库里没人读；简历说的"单 Agent"可能是**撤退**而非选择 |
| `MCPLangChainToolAdapter` 是壳 | A10/A77 | 他自己点名的可删层，但 A10 又把它当 delta 讲 |
| 两套融合实现（字典序 tuple / RRF k=60 硬编） | A86 | 仓库里同一件事有两份答案，且他承认别把它们当一套 |
| 两条不连通的 `ready` 链 + `knowledge_config` 硬编字符串 `"ready"` | A81 | 同名不同物，且产品侧那条链是否还在用他未确认 |
| `boundary_priority` 声明比实现宽 | A88 | 声明里有 section/paragraph/sentence/table_cell/code_block/character，实现只有 sentence + character |
| git 首 commit `eafeb1c2` = 2026-04-15 | A51/A52 | **与他的首笔改动同一天**（见下节） |
| 仓库"人"只有一个身份谱系 | A59 | 他用它来解释 blame 不可拆，但它同时也是"所有权永不可独立验证"的证明 |
| `docs/decisions/0007-reuse-first-build-requires-evidence.md` | A10 | 一条"复用优先、要建先举证"的自有决策文件——这句话在 A71–A80 的删减讨论里是双刃的 |

### 7. 作为面试官的整体判断

**分层结论：**

- **术语层：强。** 名词用得准，从不把 RRF 说成加权和，能把 `CancelledError`、`DispatchCertainty`、`recovery_rule` 这类东西放在正确的位置上。
- **实现层：很强，但是"全有全无"型。** 每一个机制都挂 `src/...:行号`，密度高到不像即兴编的；但整个可信度押在这些行号上，我盲态无法核实任一条。
- **失败窗口层：反常地强，甚至过度自曝。** A36/A39/A43/A47 是他主动交出四把刀。真实面试里很少有人把"我的门锁没人能转"主动摆上桌。
- **历史真实性层：这是唯一真正塌陷的一层，但塌陷的形态是"证据不存在"，不是"编造"。**
  - 核心矛盾在 **A51 与 A52 的交点**：git 的第一个 commit 是 `eafeb1c2`（2026-04-15，Initial commit），而他能自证的第一笔改动也是 2026-04-15。也就是说——**他说"我加入时系统已经存在、不是绿地"，但这个"已存在"在 git 里没有任何证据，因为仓库历史从他自己那笔改动同一天才开始。** 那么"我重构了一个既有的子 Agent 转发层"这句话里的"既有"，唯一来源是他删掉它时的那笔 diff 的 before 一侧。
  - **同一套证据的两种用法**：A53 用 commit（`77346758` / `0b5fb350` / `5d9b719e` / `f3c74338`）来**主张** bullet 的归属；A52/A59 用同一批 commit 的"作者不可区分"来**放弃**归属。他可以说这两件事不冲突（前者是"我参与过这笔"，后者是"切不出三方"），但作为面试官我看到的是：**当证据对他不利时，证据不足；当证据对他有利时，同一批证据够了。**

**过不过：**

我给 **PASS（技术判断力侧偏 STRONG_PASS，真实性侧 PARTIAL）**。

理由：他在**可自查的部分**（代码结构、失败语义、工程基础）表现出的水平，明显高于"背了一套术语"的候选；而且他的"边界"字段反复指向对自己不利的事实——这不是典型的虚假简历行为。我没有抓到任何一处**实质性的向上编造**。

但我保留两个 Open 项，并且它们都有明确的 kill 触发条件：

1. `KILL_SWITCH: CLAIM_IMPLEMENTATION_NOT_ESTABLISHED`（**仅限应用范围**：bullet 1 的"路由收紧/回归固定"、以及全部历史归属）。当前证据状态是"不可建立"，不是"已证伪"。
2. `KILL_SWITCH: CLAIM_CREDIBILITY_NOT_ESTABLISHED`（**条件触发**：若 Wave 2 中他给出的 file:line 有任何一处被证明是编的，则由于他把全部可信度押在引用精度上，整轮评级直接打到 FAIL）。

**他没垮在术语层，也没垮在实现层，更没垮在失败窗口层。** 他唯一站不稳的是**历史真实性层**——而且他用一种很聪明的方式站在这里：不是声称"我知道当时的历史"，而是声称"历史不可恢复"。这既是最诚实的位置，也是最难被证伪的位置。Wave 2 的全部火力，就压在这里：**"你怎么知道别的部分你是知道的？"**

---

## Part B — Targeted Follow-ups Q101–Q200

### T01 — Tool / MCP（追杀 A1–A10）

**Q101.** 你在 A51/A52 说 git 的第一个 commit 是 `eafeb1c2`（2026-04-15），而你能自证的第一笔改动也是 2026-04-15 —— 那么你说"我重构的那套子 Agent 转发层"的**存在**，唯一证据是不是就是 `77346758` 这笔 diff 的 before 一侧？如果那套脚手架是在同一笔或同一周内被引入又被删除的，你的"重构"这个词还成立吗？
> `chases`: A51, A52, A1, A54 ｜ `intent`: 检验 headline claim 的"既有物"是否有独立历史 ｜ `depth`: L3

**Q102.** 承 A53：你既说 `77346758` 是一笔"范围很宽的 commit、我不能把整笔都算成 Tool Calling 的贡献"，又说它是你那条 bullet 的落点。那**在这笔 commit 里，哪一处 hunk 是你写的、可以通过行为差异被指认出来**？
> `chases`: A53, A1 ｜ `intent`: 把宽 commit 里的个人 delta 逼到可指认粒度 ｜ `depth`: L2

**Q103.** 你在 A3 的边界里自己承认"漏传会静默降级"是**你今天从代码结构推出的解释**，没有当年那版代码的失败记录。那"必须删掉子 Agent 转发层"这个决定的真实依据是什么 —— 是有人踩过这个坑，还是你们只是觉得重构更干净？
> `chases`: A3, A53 ｜ `intent`: bullet 1 的问题必要性是否有真实 failure 支撑 ｜ `depth`: L3

**Q104.** A2 说这张 tool 表是"每个会话、每个 Agent 实例"动态装的，A5 说隔离靠"一个会话一个实例"。那**同一个会话内并发发起两个请求**时（比如用户在等第一个回答时又发了一条），是同一个实例还是两个实例？如果是同一个，`execute_binding_tool` 现查现注的配置靠什么不串？
> `chases`: A2, A5 ｜ `intent`: 会话内并发这一层是否覆盖面 ｜ `depth`: L2

**Q105.** A4 说 `server_dict` 是"运行时注册表"，说它不可变是"没找到写入口、不是设计上禁止写"。既然它是 agent 初始化时从 `mcp_servers_info` 现算的 —— 那 `mcp_servers_info` 是谁提供的？它第一次进入进程的路径在哪，谁有权改它？
> `chases`: A4 ｜ `intent`: 追到注册表的真正上游所有权 ｜ `depth`: L2

**Q106.** 承 A5：配置不靠 ContextVar、靠显式实参（`user_id/tenant_id/workspace_id/run_id/step_run_id/trace_id`）一路往下传。那么**当一个 Tool 是在 Agent 循环内部、由模型自己决定调用时**，"这一层"的调用点是怎么拿到 `user_id` 的？还是说捕获点根本不在那里？
> `chases`: A5, A1 ｜ `intent`: 显式传参在模型驱动路径上的可达性 ｜ `depth`: L2

**Q107.** A6 说连接层有三个 timeout（5s/300s/30s+300s），但"tool 执行那一步没有 `wait_for`"，`RuntimeLimits.timeout_ms` 只是声明式的 budget。那么**一个既不返回也不断开连接的 MCP server，会把这个 tool step 挂多久**？谁最终把它解开 —— 上层的 step 级 timer、worker 重启，还是没人解？
> `chases`: A6 ｜ `intent`: 无定时器路径下挂死调用的实际收口者 ｜ `depth`: L2

**Q108.** 承 A7/A96：幂等位 TTL 60 秒，TTL 之外的重试靠对账，而 A47 说对账**没有 reader、没有执行器**。那在真实运行中，**60 秒之后的第二次同类调用实际会发生什么** —— 是重新拿一张 receipt 再打一次网络吗？
> `chases`: A7, A47, A96 ｜ `intent`: 三条机制叠加后的实际安全边界 ｜ `depth`: L3

**Q109.** 承 A7：`claim_idempotency_receipt` 的 TTL 到期，语义到底是"这张 receipt 被删掉、可以重新 claim"，还是"记录还在、只是不再算数"？这两种语义下，**同一个 `call_id` + `prepared_action_hash` 的第二次调用**分别会走到哪一支？
> `chases`: A7 ｜ `intent`: TTL 的精确语义与重放分支 ｜ `depth`: L2

**Q110.** A9/A46 给了 `age_escalation_after_seconds=900` 和 sweep 入口（`escalate_due_reconciliations`），但 A47 承认"调度这些 sweep 的 cron/worker，我没有证据说它存在"。那这条 900 秒的升级规则，**今天由什么触发**？如果没有任何东西触发它，"转人工"这个默认动作是不是也只是纸面默认？
> `chases`: A9, A46, A47 ｜ `intent`: 升级规则的执行者是否存在 ｜ `depth`: L2

**Q111.** A10 把 `MCPLangChainToolAdapter.execute` 描述成"就是个 `binding.ainvoke` 的包壳，delta 只是上下文和幂等 key"，A77 又把它列为"最像包壳的自研层"。既然它只是壳，**为什么不是把上下文的构造挪到调用点、直接 `ainvoke`**？保留这一层的唯一理由是什么？
> `chases`: A10, A77 ｜ `intent`: 壳层的存留理由（Defer/Delete） ｜ `depth`: L2

**Q112.** 你在 A33/A35/A38/A47 里对 `agent/runtime/planning/` 和 `recovery/` 反复做了"有没有 caller"的审计，但 A7/A9/A42–A48 那一整套（`invocation_gateway.py`、`runtime_batch.py`、`effect_policy.py`）你**一次都没有做同样的审计**。为什么审计口径是**不均匀**的？`invocation_gateway` 上的调用方是谁、它是在活路径上吗？
> `chases`: A33, A35, A38, A47, A7, A9, A42, A43, A44 ｜ `intent`: 方法论一致性；检验"活路径"的范围 ｜ `depth`: L3

### T02 — GraphRAG（追杀 A11–A20）

**Q113.** A11 说 baseline 是 `Recall@5=1.00 / MRR@10=0.90`，A60 却说这条 bullet 的"修复前后指标"是 `Recall@5 0.80→1.00 / MRR@10 0.80→1.00`。**修复后的 MRR@10 到底是 1.00 还是 0.90+**？如果真是从 0.90 抬到 1.00，一个自称 `baseline_preserving`、只做"保位"的改动为什么会**超过** baseline？
> `chases`: A11, A60 ｜ `intent`: 两答数字之间的直接矛盾 ｜ `depth`: L3

**Q114.** A11 说"graph candidates 把 baseline 已命中的两篇挤出"是在 **HotpotQA development smoke** 上发现的，A17 说证据是 **5-query smoke**。被挤出的 `Ed Wood` / `Shirley Temple` 和那 5 条 query 是**同一批**吗？如果不是，你 A60 里"有具体 bad case + 有回归测试 + 有修复前后指标"这三件事，是不是来自两个不同的实验？
> `chases`: A11, A17, A60 ｜ `intent`: bad case 与指标的样本同一性 ｜ `depth`: L2

**Q115.** A11 说那几条 query 的原始报告是 gitignore 掉的，A66 说指标记录在 PF-031 和 eval README 里。那么 `0.80` / `0.90` / `1.00` 这几个数**今天到底写在哪个可打开的文件里**？如果只能从 README 读到，而 README 又不带 raw run，**你凭什么说这几个数不是转抄的**？
> `chases`: A11, A17, A66 ｜ `intent`: 最强 bullet 的证据可复现性 ｜ `depth`: L3

**Q116.** A12 说"我参与制定过口径的哪一部分，我记不清了"，A56 却明确说"我定了 heuristic、fusion 里那 9 个阈值和分层"。**定阈值和定口径是两件事还是同一件事**？你对自己 Ownership 的记性，为什么在指标体系上模糊、在阈值上精确？
> `chases`: A12, A16, A56 ｜ `intent`: Ownership 记忆的边界是否被结果反向选择 ｜ `depth`: L2

**Q117.** A13 说 vector+BM25 会在 comparison/bridge/genealogy 上答错，A18 承认图检索的必要性**从未被测量**。那这条 GraphRAG 的 bullet 要留在简历上，靠的是"机制上应该有用"还是"我们测出来有用"？如果是前者，**它和"我加了一个可能没用的层"的区别在哪**？
> `chases`: A13, A18, A20 ｜ `intent`: 复杂度举证责任落到候选人身上 ｜ `depth`: L3

**Q118.** A14 给了一个六元字典序 tuple：`(candidate_group, baseline_rank, -chain_score, -graph_tier, -graph_signal, -(local_score + base_score))`。当这六个字段**全部相等**时（同一 group、同一 rank、score 全同），最终的 tie-break 是什么？排序是稳定的吗？
> `chases`: A14 ｜ `intent`: 排序键的完备性与确定性 ｜ `depth`: L2

**Q119.** 承 A14/A15：既然最终顺序里 `baseline_rank` 排在 `chain_score` / `graph_tier` / `graph_signal` **之前**，那图那三个信号在**绝大多数比较**里其实不参与决断。那么 fusion 的**真实行为**是不是"几乎总是按 baseline 的位次排，只在 group 和 rank 都打平时图信号才生效"？
> `chases`: A14, A15 ｜ `intent`: 排序优先级是否让图信号形同虚设 ｜ `depth`: L2

**Q120.** A16 列了 9 个常量并说"谁定的：我在修那三个 heuristic 的时候定的"，但 A56 说"方向不是我提的"。**"定了 9 个阈值"和"定了要往图证据方向改进排序"**这两件事里，你实际有权决定的是哪一件？如果阈值是你拍的、而方向是别人的，那这套 heuristic 的**设计者**是谁？
> `chases`: A16, A56 ｜ `intent`: 阈值权与方向权的归属切分 ｜ `depth`: L2

**Q121.** A74 说 fusion 的 guardrail 阈值层是"我为架构完整性加的、而不是 bad case 逼出来的"，A16 又说这套阈值是为了"让 bad case 不再复现"才定下来的。**这两个说法互斥吗** —— 到底是 bad case 逼出来的，还是为了完整度加的？请只挑一组阈值（比如 comparison 三件套）回答。
> `chases`: A16, A74 ｜ `intent`: 同一层的两个动因说法对齐 ｜ `depth`: L3

**Q122.** A17 说 5 条 query 的选取口径是 Unknown、原始报告 gitignore。那你凭什么相信**这个修复不是对着这 5 条过拟合的**？你手上有没有任何一条**不在那 5 条里**的 query，证明修复后它也没坏？
> `chases`: A17, A18 ｜ `intent`: 修复的泛化性是否有任何一点外围证据 ｜ `depth`: L2

**Q123.** A18/A20 的论证挂在一份 `rb019-graphrag-ablation-protocol.md` 上。这个名字里的 `rb019` 看起来是**上一轮 Red/Blue round 的编号**。这份协议是**产品工程**的产物，还是**面试流程**的产物？`measurement_status: BLOCKED_PENDING_DATA` 是谁维护的，产品侧有人读它吗？
> `chases`: A12, A16, A18, A20 ｜ `intent`: 关键论证所依附的产物是否属于工程而非评测 ｜ `depth`: L3

**Q124.** A19/A94 说检索是顺序 await、`retrieval/` 里没有 `asyncio.gather` 也没有超时取消。那么一条带 graph 的 query，**它的总延迟 = vector + requery + bm25 + graph 之和**。`graph_hop_limit=2`、`max_paths_per_entity=10` 这两条上限，是**怎么定**的？和 A16 那 9 个阈值一样是拍的吗？
> `chases`: A19, A94, A16 ｜ `intent`: 图侧上限常量的依据（与阈值层同一根线） ｜ `depth`: L2

**Q125.** A20 说图路由只在 `internal_route == "local_graphrag"` 且 `graph_available` 时才开。`graph_available` 是**谁写的**、多久刷新一次？如果一个项目曾是 ready、之后图索引坏了但 `graph_available` 还停在 true，系统会一直带着一个坏图跑吗？
> `chases`: A20, A82 ｜ `intent`: 可用性开关的新鲜度 ｜ `depth`: L2

### T03 — Memory / Context（追杀 A21–A30）

**Q126.** A53 第 4 条说"我做的，但它所在的文件后来被删了（`ab1222da`）"，A24 说 `prepare_context()` 今天连函数都不是。也就是说**简历五条 bullet 里有两条描述的是已经不存在的代码**。那么"我做过"这件事今天**靠什么被验证** —— 只剩 commit 存在与否，而 A59 又说 commit 切不出归属？这个环是不是闭合的？
> `chases`: A53, A24, A59 ｜ `intent`: 已被删除的两条 bullet 的归属验证路径 ｜ `depth`: L3

**Q127.** A22 说 `MemoryScope` 是四元组，A78 又说 `agent_id` 被写死成 `"agent_run"`、不区分任何东西、也无消费方。**一个 typed contract 里带着一个永远填同一个值的维度**，这本身是不是"typed contract 是后补的、不是从需求长出来的"的证据？
> `chases`: A22, A78 ｜ `intent`: typed contract 的真实来源 ｜ `depth`: L2

**Q128.** A23 说一次 `post_turn_commit` 写五张表（`memory_candidates_v2` / `memory_versions` / `memory_snapshots` / `context_pack_versions` / `memory_use_traces`）。按你在 A33/A35/A47 的审计习惯 —— 这五张表**各自有没有 reader**？尤其 `memory_use_traces` 和 `context_pack_versions`，谁在读？
> `chases`: A23, A26, A33 ｜ `intent`: 写入侧的读者是否存在（同口径审计） ｜ `depth`: L2

**Q129.** A24 说简历那句"注入 `prepare_context()`"按今天的代码读会失准，准确说法是"注入到回合前的上下文构建节点"。既然你在 A24 里已经意识到了这一点 —— **为什么简历上保留的是那个按今天代码会失准的措辞**？
> `chases`: A24, A53 ｜ `intent`: 已知措辞失准却未修的原因 ｜ `depth`: L2

**Q130.** A25 说两个案件共用 `user_id` 时靠 `project_id`(=`workspace_id`) 和 `thread_id` 分开，"但这个保护的前提是调用方传对"。那么**调用方是谁**？是 `_memory_scope()` 的调用点吗（A22 说 `project_id` 取 `workspace_id`）？有没有一条测试故意传错 `workspace_id` 看会不会串读？
> `chases`: A25, A22 ｜ `intent`: scope 保护的实际边界与测试覆盖 ｜ `depth`: L2

**Q131.** A26 说 memory 版本有 `REVOKED` / `SUPERSEDED` 状态、激活走 CAS，被撤销后不再 eligible。但 A26 的边界又说"下游结论要不要回滚：没有自动失效传播机制"。那 **`REVOKED` 这个状态实际改的是"未来召回"还是"当前上下文"**？如果只改未来召回，它和"删掉这条记录"在效果上有什么区别？
> `chases`: A26 ｜ `intent`: 撤销语义的实际作用域 ｜ `depth`: L2

**Q132.** A27 的边界说"'stale 是谁标的、按什么规则标的'我没有追到底"。但 A27 的核心论证是"靠状态位和版本，不靠时间戳"。如果 `stale` 这个状态**没有已知的生产者**，那"状态机在兜底"这句话是不是和 A43 里 epoch 的处境一样 —— 门在、没人开门？
> `chases`: A27, A43 ｜ `intent`: stale 状态生产者的存在性（跨题一致性） ｜ `depth`: L3

**Q133.** A28 说冲突时信 Domain，"Provider records do not replace Domain truth"。那**一条纯粹只存在于 memory 里的事实**（比如"用户偏好用中文回复"）算不算 Domain truth？如果 Domain 里没有对应字段，A28 这条原则还适用吗，谁判？
> `chases`: A28, A25 ｜ `intent`: "Domain 权威"原则的适用边界 ｜ `depth`: L2

**Q134.** A29 说这层复杂度今天是"举证不足但失败类真实"，A30 说三个删除条件**一条都不成立**。那"留着"的理由是"三个条件都不成立"还是"我拿不出收益对照"？这两件事的区别在于：**前者说明它必要，后者说明它没被证明必要** —— 你选哪个？
> `chases`: A29, A30 ｜ `intent`: 存留理由与举证不足的区分 ｜ `depth`: L3

**Q135.** A78 说只留 `project_id`，`user_id` 交给授权上下文、`thread_id` 交给运行时。按这个压缩，V2 的"typed contracts + scope 约束"里**有一半维度立刻消失**。那这两条 bullet 里"构建 scoped Context/Memory V2"的工作量，有多少花在了一个你今天就愿意删掉的三维上？
> `chases`: A78, A22, A53 ｜ `intent`: 自认可压缩的抽象与其 Original Claim 的落差 ｜ `depth`: L2

### T04 — Runtime（追杀 A31–A40）

**Q136.** A31 说"某年某月这个 case 逼我们上 Runtime"的具体事件你恢复不出来，能给的是**文档里的四种失效窗口**。那份写四种失效窗口的 `docs/architecture/architecture.md` —— **是谁写的、什么时候写的**？它是在 Runtime 建好之后补的说明，还是建它之前的立项依据？
> `chases`: A31 ｜ `intent`: 立项依据文档的时序与作者 ｜ `depth`: L2

**Q137.** A33 说 `append_plan_version` 写了没接线，A35 说 `BranchResultFencer` 没接线、它的上游 `DynamicStepWorker` 也没接线。既然"计划只能激活一次""晚到结果按 epoch 拒收"这套语义**在运行时没有任何执行者**，那它今天是**约束吗**，还是**一组只被领域聚合实现、与被拒结果无关的领域规则**？
> `chases`: A33, A34, A35 ｜ `intent`: plan version 语义是否真的在运行时生效 ｜ `depth`: L3

**Q138.** A34 主动纠正了 A33 里"单调 plan_version 是核心信号"的说法，说 canonical 路径上 `plan_version` 只被赋 0 或 1、没有任何递增路径。**你是在准备这轮回答的时候发现的，还是在更早的某个时候？** 如果是这轮才发现，那 A33 那一整段的其余部分（比如 `agent_runtime_plan_versions` 表的存在）还能按同样方式被信任吗？
> `chases`: A33, A34 ｜ `intent`: 自我纠正的时点，以及它对同段其余陈述的连带影响 ｜ `depth`: L3

**Q139.** A35 说活的图是通过 `PlanExecutor` **顺序执行** step、完全没有分支/晚到结果的 fencing；Domain 的 stale 守卫管的是"写冲突"不是"晚到结果"。那么**今天如果一个旧版本的 Tool 结果晚到了，实际会发生什么** —— 被丢弃、被当作当前结果使用，还是根本不可能出现这种情况（因为顺序执行）？
> `chases`: A35, A32 ｜ `intent`: 顺序执行是否让 late result 问题消失 ｜ `depth`: L2

**Q140.** A36 说两存储无 2PC，但 Domain 侧自己的补偿是"同库 outbox（domain 事实 + outbox 事件在同一个事务里写）"。**outbox 保证的是 domain→事件这一对，而你说的崩溃窗口是 domain→checkpoint**。所以 outbox 对你的 `DOMAIN_COMMIT_BEFORE_CHECKPOINT` 窗口**一点帮助都没有**，对吗？
> `chases`: A36 ｜ `intent`: 补偿机制是否覆盖所声称的窗口 ｜ `depth`: L3

**Q141.** A36/A37 说一致性靠 `reconcile_generations(domain_generation, checkpoint_generation)` 事后比对，A36 的边界又说 `phase08.py` / `planning/recovery.py` 在 `tests/` 里找不到 importer。那 **`reconcile_generations` 在活路径上是被谁调的**？它属于 `phase08.py` 那一族吗？如果是，A37 的"以 Domain 为准"今天是谁在执行的？
> `chases`: A36, A37, A39 ｜ `intent`: reconciliation 的执行者是否在活路径上 ｜ `depth`: L3

**Q142.** A38 说恢复"主要靠人点"，入口要求"存在 pending interrupt"且"存在最新 checkpoint"，并带 approval decision。在一个**没有生产环境、没有 SLA、没有值班**的试点里（A69），**这个 approval 今天是谁点的**？如果没有人点，"人点恢复"实际上是不是等于"不恢复"？
> `chases`: A38, A69 ｜ `intent`: 人工审批路径在无运维环境下的实际可达性 ｜ `depth`: L2

**Q143.** 承 A39：ADR-0005 明确要求官方 saver 是唯一基座、且不允许自研桥替代，而主线恰好是自研桥。**这份 ADR 是谁批准的**？批准的人知不知道主线和它不一致？如果不一致持续到现在都没被纠正，那 ADR 在你们项目里的**实际效力**是什么？
> `chases`: A39 ｜ `intent`: 制度文件与实现分裂的治理责任 ｜ `depth`: L3

**Q144.** A39 说"还有一条测试反过来禁止存在一个 cutover 文件"（`tests/repo/test_agent_system.py:36`）。**A39 内部还有一个矛盾要说清**：既然主线**已经**没接官方 saver，那这条测试是在**防**什么 —— 防有人做 cutover，还是防有人把桥删掉？
> `chases`: A39 ｜ `intent`: 守护分裂的测试的真实意图 ｜ `depth`: L2

**Q145.** A40 说三条收回条件里第一条（Domain 提交与 checkpoint 能做成一次原子写）是硬前置，但边界又写"我没有验证过能不能做到原子，这是判断不是已评估的方案"。**在一个 PostgreSQL 单实例里**，Domain 提交和 checkpoint 写入如果放同一个库同一个事务，技术上可不可行？如果可行，"两个引擎"是**技术限制**还是**架构选择**？
> `chases`: A40, A36 ｜ `intent`: 硬前置是技术不可行还是选择 ｜ `depth`: L3

### T05 — Security / Effect（追杀 A41–A50）

**Q146.** A41 说"这一层不是我的 Ownership"，但 A42–A48 你对 `_reauthorize_execute_epoch`、`assert_audit_durable_for_effect`、`DispatchCertainty`、`claim_idempotency_receipt`、`record_manual_effect_assessment` 的细节讲得比对自己 bullet 还细。**这些细节你是怎么知道的** —— 你读了这个层，还是有人给你讲过？
> `chases`: A41, A42, A43, A44 ｜ `intent`: "非我所有"与"细节极熟"之间的来源 ｜ `depth`: L3

**Q147.** A42 说授权查两次（选择/准入时、dispatch 前），并承认"两次检查之间有多大窗口、窗口里权限真的变了会不会被这次检查抓住 —— 没有构造过竞态测试"。**这个窗口的上界由什么决定** —— 是两次调用之间的代码路径长度，还是中间夹了一次网络/sandbox dispatch？如果在窗口里权限被收回，第二次检查**一定会**抓住吗？
> `chases`: A42, A43 ｜ `intent`: TOCTOU 窗口与 fail-closed 的实际保证 ｜ `depth`: L2

**Q148.** A43 说生产侧**没有任何代码路径会 revoke 一个 epoch**，唯一 revoke 的是测试里的裸 SQL。那么 fail-closed 这条性质在**真实运行中**能观察到吗？如果一个状态只能由测试制造，"fail-closed 已实现"这句话是在描述**能力**还是在描述**一片可执行代码**？
> `chases`: A43 ｜ `intent`: 只在测试接缝可达的状态机的可信度 ｜ `depth`: L3

**Q149.** 承 A43/A50：你在 A50 说"一个只有测试能触发的状态机分支，要么补上生产者，要么承认它不该有独立对象"。那你**今天的倾向**是哪一个 —— 补生产者，还是承认它不该存在？如果两者都不做，它明年还在吗？
> `chases`: A43, A50 ｜ `intent`: 对自身点名的缺口给出方向 ｜ `depth`: L2

**Q150.** A44 说审计在 effect 之前强制写、并且"落完之后立刻重读校验"（`assert_audit_durable_for_effect`），读不回来就 `FencingRejectedError`。**这个 `assert_audit_durable_for_effect` 今天是在活路径上被调用的吗**？按你在 A33/A35 的审计方式回答。
> `chases`: A44, A33, A35 ｜ `intent`: 关键安全断言是否接线（同口径审计） ｜ `depth`: L2

**Q151.** A45 给了 `DispatchCertainty ∈ {NOT_DISPATCHED, DISPATCHED, MAYBE_DISPATCHED}`，但边界说"'确定没发出去'的判定究竟基于什么证据（进程内标志？还是远端确认？）我没有逐行读"。**如果判据是进程内标志**，那"NOT_DISPATCHED"在**进程崩了**之后还成立吗？
> `chases`: A45 ｜ `intent`: 判据的持久性，与崩溃窗口的关系 ｜ `depth`: L2

**Q152.** A46 说默认动作是"转对账"，A47 说对账的执行器不存在。那么在**今天**，一次真实发生的 UNKNOWN effect 会走到哪一步就停住 —— 停在 OPEN、停在 `reconcile_required`，还是会有人手工 `record_manual_effect_assessment`？
> `chases`: A46, A47 ｜ `intent`: "默认动作"在无执行器下的实际终态 ｜ `depth`: L3

**Q153.** A7/A96 说"只有对账结论 `CONFIRMED_NOT_EXECUTED` 才允许重发同一个 effect"，而 A47 说对账的**远端查询没有实现**、只有人工评估路径能给出结论。那这条安全守卫今天**依赖一个人工动作**才能被满足 —— 也就是说，如果没有人做人工评估，一个 UNKNOWN 的副作用**永远不能被安全重发**。这是设计意图，还是缺口？
> `chases`: A7, A46, A47, A96 ｜ `intent`: 安全守卫对人工路径的隐式依赖 ｜ `depth`: L3

**Q154.** A48 说 `src/backend/zuno` 里 grep `court|法院|judicial|审判|立案` **没有任何命中**，真实对外效果是 SMTP / 物流 HTTP / Lark。那简历项目简介里"面向天津法院智慧平台相关场景"这句话，**代码支撑的是什么** —— 只是一个通用法律 RAG demo 被贴了个法院场景的标签吗？
> `chases`: A48, A61 ｜ `intent`: 项目场景定位是否有代码支撑 ｜ `depth`: L3

**Q155.** A48 说"真的改过外部现实"（真连 smtplib、真打阿里云、真 lark_oapi 客户端），又说"没有生产环境"。那这些**真对外发出去的动作发生在哪个环境**、发给谁？是一个测试租户、一个内部邮箱，还是真实外部对象？
> `chases`: A48, A67, A69 ｜ `intent`: "真实副作用"的实际作用对象 ｜ `depth`: L2

**Q156.** A49 的演进论证完全来自 `docs/evidence/implementation-wave-001.md` 的负向历史 #203/#205/#207。**这份 evidence 文档是谁写的、什么时候写的**？这三条负向历史是**真实事故记录**，还是**上一轮评测复盘里被命名的条目**（类似 `rb019` 那种编号）？
> `chases`: A48, A49, A76, A123 ｜ `intent`: 演进叙事的证据文件的性质 ｜ `depth`: L3

**Q157.** A50 说"回执三件套可以收：留 effect + reconciliation，把 execution 折进 effect 的 certainty 里"，同时又说"这一层不是我的 Ownership"。**你凭什么对不是自己拥有的层给出重构方案**？并请说一个具体后果：如果把 execution receipt 折进 effect certainty，**哪一条 / 哪一类判定会失去依据**？
> `chases`: A50, A41, A45 ｜ `intent`: 非所有权层的重构判断依据 ｜ `depth`: L2

### T06 — Project History（追杀 A51–A60）

**Q158.** A51 说"约 2026-03 加入、项目和代码已经存在、不是绿地"，A52 说 git 的第一个 commit 是 `eafeb1c2`（2026-04-15）。**如果 git 历史从 2026-04-15 才开始，那"项目早在 3 月就存在"这件事唯一的依据是 `docs/project/reference.md` 的一句话**。那份 reference 是谁写的？有没有任何一个非文档的、能独立证明"3 月已经有系统"的物证？
> `chases`: A51, A52 ｜ `intent`: 存量基线的独立证据 ｜ `depth`: L3

**Q159.** A53 用 `77346758` / `0b5fb350` / `5d9b719e` / `f3c74338` 这些 commit **主张**归属，A52/A59 用同一批 commit 的"作者不可区分"**放弃**归属。**同一套证据，什么时候算数、什么时候不算数**？请你给一个明确规则：什么条件下 commit 能证明是你做的？
> `chases`: A52, A53, A59 ｜ `intent`: 所有权证据标准的自洽性 ｜ `depth`: L3

**Q160.** A55 说 2026-03 到 2026-04-15 之间"历史里没有我的可辨识痕迹"，A51 说你是 3 月加入的。**这中间一个月你在做什么** —— 是没提交，还是提交了但归到了那个统一身份谱系下？如果是后者，那你自己"第一笔"的判断本身就建立在不可靠的作者字段上。
> `chases`: A51, A52, A55 ｜ `intent`: 空窗期与作者字段可靠性的交叉 ｜ `depth`: L2

**Q161.** A60 说五条 bullet 里你只留第 2 条（GraphRAG 排序回退），理由是"它的 claim 和证据匹配"。但 A113 那个矛盾（A11 的 0.90 vs A60 的 1.00）、A17 的不可复现、A16 的无依据阈值，全都挂在这条上。**按你自己的标准，"claim 和证据匹配"这条它真的满足吗**？
> `chases`: A60, A11, A16, A17 ｜ `intent`: keeper bullet 是否通过它自己的判据 ｜ `depth`: L3

**Q162.** A54 说被删的脚手架形状可查、动机是推断，A52 又说无法区分作者。**那"有这么一套子 Agent 转发层"这件事，除了 `77346758` 的 diff，还有别的地方能证明它曾经在跑吗** —— 比如它的测试、它的 API 面、或它的配置？
> `chases`: A54, A52 ｜ `intent`: 被重构对象曾经运行过的独立证据 ｜ `depth`: L2

**Q163.** A54 说 `MCPAgentTable` 和 `api/v1/mcp_agent.py` 的 CRUD 面**到今天还在**、但已不被 workspace adapter 引用；`multi_agent_enabled` 字段还存着但**没有任何 reader**。这说明**曾经有过一个多 Agent 的正式设计** —— 是谁做的？为什么被撤回？简历说的"单 Agent"是这个设计的**结论**还是**撤退**？
> `chases`: A54 ｜ `intent`: 多 Agent 残骸背后的历史与"单 Agent"的性质 ｜ `depth`: L3

**Q164.** A56 说"方向不是我提的，我定的是 heuristic"。请**指认出你第一次触碰某一个 heuristic 的那一笔**（就像你在 A1 里能指认 `77346758` 那样）—— 如果指不出，那"三个 heuristic 是我实现的"这个 claim 和你批评别人 bullet 的"归属不可切"是不是同一处境？
> `chases`: A56, A53, A59 ｜ `intent`: 最窄 Ownership 的可指认性 ｜ `depth`: L3

**Q165.** A57 说 typed contract / 版本 / receipt 在你加入第一个月**都不存在**，A29 又说这一套没有对照实验。它们是什么时候出现的？**出现的时候你在不在**？如果出现了但你没有参与，那"scoped Context/Memory V2"这条 bullet 描述的是**你建的那一版**，还是**别人建的那一版**？
> `chases`: A57, A21, A53 ｜ `intent`: V2 这套机制的时间线与参与 ｜ `depth`: L2

**Q166.** A58 说"我没碰过 ≠ 它没被改过"，并给出"07 Model Gateway、09 Observability & Evaluation 可以被认为没碰过"。**这九个模块里，有没有任何一个接口是你定的**（哪怕是一小块）？如果没有，那你的角色更接近"局部改动的实现者"，你接受这个定位吗？
> `chases`: A58, A53 ｜ `intent`: 个人角色的自我定位与覆盖面 ｜ `depth`: L2

**Q167.** A59 说"约 7–8 人核心研发"是**文档**给的、不是 blame 给的。那份文档是谁写的、写在什么时候？**这 7–8 人是怎么定义"核心"的** —— 是全员名单，还是某个时点的快照？
> `chases`: A59, A51 ｜ `intent`: 团队规模数字的来源与口径 ｜ `depth`: L2

**Q168.** A60 的边界说："即便留这一条，它的正确上限也是 bounded regression fix，不是 GraphRAG 更好。" 那**简历里第 2 条的措辞（"定位并修复 GraphRAG 排序回退"）有没有越过这个上限**？如果没越过，你为什么在 A60 里还要专门给它加一个上限？
> `chases`: A60, A11 ｜ `intent`: bullet 措辞与其自认上限的一致性 ｜ `depth`: L2

### T07 — Pilot / 法院（追杀 A61–A70）

**Q169.** A61/A62 说发起方、在场角色、你本人有没有跑现场 demo 全是 Unknown。**那简历里"项目经历内部 Demo、法院侧测试与 Pilot Validation"这句话是谁写的**？如果所有细节都不可恢复，写这句话的人依据什么？
> `chases`: A61, A62, A1 ｜ `intent`: 简历关键措辞的作者与依据 ｜ `depth`: L2

**Q170.** A63/A67 说使用时长、频次、有没有人依赖全是 Unknown。**有没有任何一件用户侧留下的物证** —— 一条聊天记录、一份评审意见、一张截图、一个日志时间戳？一件都没有，还是你没找过？
> `chases`: A63, A65, A67 ｜ `intent`: Pilot 的物理痕迹是否存在 ｜ `depth`: L2

**Q171.** A64/A70 说"Pilot Validation"是**项目/架构文档里的定性**，你找不到法院侧验收文书。那这个**词**是你们内部给自己定的里程碑名，还是法院/甲方用过这个词？如果是前者，它和"我们做完了一轮试点"在语义上有什么区别？
> `chases`: A64, A70 ｜ `intent`: Pilot 定性词的真实出处 ｜ `depth`: L2

**Q172.** A65 说唯一的客户反馈汇总只有一句"回答质量还需要提高"。那这次 Pilot 到底**验证了什么**？如果结论只有"还要提高"，把它叫做"Validation"的依据是什么 —— 验证了"系统能跑通流程"这件事本身吗？
> `chases`: A65, A63, A64 ｜ `intent`: Validation 的实际内容 ｜ `depth`: L2

**Q173.** A66 说 `224 passed` 来自固定快照 `5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660` 的一次 CI run，且 `FULL CI: NOT RUN`。**为什么简历/材料上呈现的是"某次跑过"，而不是"从没跑全过"**？这个 224 是谁挑出来放进 baseline 文档的？
> `chases`: A66, A69 ｜ `intent`: 测试基线的呈现选择 ｜ `depth`: L2

**Q174.** A68 说"如果题目集和验收标准都是我们自己出的，那它就是自证"，并承认无法排除这个可能。**能不能反过来举证**：哪怕一条——法院侧的某个人给过某条要求、提过某个问题形状？
> `chases`: A68, A65, A61 ｜ `intent`: 独立第三方标准的反向举证 ｜ `depth`: L2

**Q175.** A69 给了一组状态标签（`PRODUCTION_READINESS: NOT_ESTABLISHED`、`FULL CI: NOT RUN`、`COURT QA: UNKNOWN`）。**这些标签写在哪份文档里、是谁写的、什么时候写的**？如果它们也是项目侧自己贴的，那"这不是生产"这个结论的证据链，是不是从头到尾都是自证？
> `chases`: A69, A66, A64 ｜ `intent`: 生产就绪判断的证据链是否自证 ｜ `depth`: L3

### T08 — 系统简化 / Delete（追杀 A71–A80）

**Q176.** A71 说"我没有统计过调用方数量"，A72 说按"删掉主流程还能不能跑完"来测。**这两个测试其实都不需要跑代码** —— 一次 import 图扫描或调用方检索就够了。你既然能在 A33/A35 精确地说"某某函数无 caller"，为什么在 A71 这里说"没统计过"？
> `chases`: A71, A72, A33, A35 ｜ `intent`: 审计能力在同一轮里的一致使用 ｜ `depth`: L3

**Q177.** A72 要合并 05 进 06，A73 又说那是"接管不是无损"，A75 又说"05 的问题今天还在、只是换了容器"。**合并第一天，最具体的哪一件事会没人负责**？
> `chases`: A72, A73, A75 ｜ `intent`: 合并代价落到具体责任 ｜ `depth`: L2

**Q178.** A74 说 `domain.py:249` 那个对象"不是我的 Ownership，我引用它是作为'我观察到同样气味'的例子"。**你在 A74 里既承认 fusion 阈值层是为完整度加的，又用它来给你的第 2、3 条 bullet 埋雷**。那你到底认为**第 2 条 bullet 的核心工作**是"止血"还是"架构自嗨"？
> `chases`: A74, A79, A60 ｜ `intent`: 自认与 keeper bullet 之间的关系 ｜ `depth`: L3

**Q179.** A75 说 05 是"两份 authority 重叠"，但 A75 的边界又说"当年为什么要单独设 05 我没找到记录"。**找不到记录的情况下，你怎么判断它是重叠而不是两个不同 authority**？你依据的是什么——名字像、还是行为像？
> `chases`: A75, A72 ｜ `intent`: 重叠判断的依据 ｜ `depth`: L2

**Q180.** A76 预测了两条合并会回来的 failure（06 的 `UNKNOWN_EFFECT` 不降级边界泡软、08+09 变成"先记录再拒"）。**这两条预测有历史支撑吗** —— 有没有哪次真实的合并/重构，就出现过这两个形状中的一个？还是纯推演？
> `chases`: A76, A49 ｜ `intent`: 合并预测的经验来源 ｜ `depth`: L2

**Q181.** A77 说 checkpoint 桥"有相当一部分是包壳"，但里面"和 Domain 对账"那部分是真 delta。**A36 说这套 reconciliation 在 `tests/` 里找不到 importer、A40 说收回条件第一条没验证过**。那这层"真 delta"今天**在跑吗**，还是它也是"写了没接线"清单上的一员？
> `chases`: A77, A36, A40 ｜ `intent`: 自研 delta 是否在活路径上 ｜ `depth`: L3

**Q182.** A78 说 `agent_id` 是死维度、最容易去掉。**除了 `agent_id`，这套 typed contract 里还有多少个"永远填同一个值 / 没有消费方"的字段**？如果你答不出来，那你"scope 是四元组合"这个描述本身，有多少是照结构念的、有多少是照语义讲的？
> `chases`: A78, A22 ｜ `intent`: typed contract 里死字段的规模 ｜ `depth`: L2

**Q183.** A80 的证据字段里，你把 `docs/governance/interview-acceptance-standard.md（§9 简化信号）`当作"模块 09 该被质疑"的依据。**这份文件是面试/评测的验收标准**。请说清：你判断 09 写不出删除条件，是因为技术直觉，还是因为你读到了这份标准里的哪一条？**你的"边界"字段里，有多少是按这份标准写的**？
> `chases`: A80, A29, A50 ｜ `intent`: 技术判断与面试标准之间的边界 ｜ `depth`: L3

**Q184.** A80 说 09 的删除条件"写不出来"，并把它当成"未举证的复杂度"留在桌上。**那在你今天的判断里，09 是一个模块，还是一个证据存放目录**？如果它没有独立运行时行为，"模块"这个身份是谁给的？
> `chases`: A80, A71, A73 ｜ `intent`: 09 的身份与其在架构视图中的来源 ｜ `depth`: L2

### T09 — Knowledge / Retrieval（追杀 A81–A90）

**Q185.** A81 说这里有**两条互不连通的"真相"链**（产品侧 pipeline 表 vs 严格知识域版本/snapshot/evidence 链），并且你承认"产品侧那条链是不是还在被使用，我也没有确认"。**产品侧那条链今天有没有读者**？按你在 A33/A35 的口径回答。
> `chases`: A81, A33, A35 ｜ `intent`: 双链中产品侧的存活状态 ｜ `depth`: L2

**Q186.** A81/A82 说 `ready` 在两条链上各有一个来源，其中一条是 `knowledge_config` 里**硬编的字符串** `"ready"`。**cutover 和检索读的是哪一个**？如果存在两个同名不同源的状态，**谁在防它们的漂移**？
> `chases`: A81, A82 ｜ `intent`: 同名双源状态的权威判定 ｜ `depth`: L2

**Q187.** A83 说服务端没有 span 解析端点、前端 citation 是纯 chip 没有 click handler。那"用户点得到引用"这件事在这个产品里**从来没有成立过**？如果是，Q81 那个"从文档进来到用户点得到引用"的前提是谁提的 —— **是你在回答里接受了这个前提**，还是产品确实有这个行为？
> `chases`: A83, A81, A90 ｜ `intent`: 关键用户行为的真实性 ｜ `depth`: L3

**Q188.** A83/A90 说绑定层存的 `source_span_id` 可能是 span id、chunk id、block id，甚至是整个 span dict 的 SHA-256。**一个"身份"字段承载四种不同语义** —— 这是设计，还是一个没人收敛的洞？如果将来要做点击定位，这四种语义要不要先统一？
> `chases`: A83, A90 ｜ `intent`: 身份字段的多义性 ｜ `depth`: L2

**Q189.** A84 说旧引用"不失效也不重定向"，但校验时会给出 `evidence_stale` / `document_version_mismatch`，源被删时标 `citation_eligibility='REJECTED'`。**谁消费 `evidence_stale` 这个标记，消费之后做什么**？如果没人消费，这个标记和"这条引用已经废了但没人知道"有什么区别？
> `chases`: A84, A83 ｜ `intent`: 陈旧标记的消费方 ｜ `depth`: L2

**Q190.** A85 说出口是弃答（`Abstain: unsupported claims remain` / `Insufficient cited evidence to answer`），A28 的边界又说"如果一条 memory 与 Domain 冲突但没人触发 abstain，这条冲突会不会静默漏过去——我没有见过对应的失败测试"。**abstain 这条路径今天接线了吗**？按你在 A33/A35 的口径回答。
> `chases`: A85, A28 ｜ `intent`: 弃答路径是否在活路径上 ｜ `depth`: L2

**Q191.** A86 说仓库里有**两套融合实现**：产品侧是字典序 tuple，`knowledge/agentic_graphrag.py` 侧是真 RRF（`rrf_score += 1.0/(60.0 + rank)`，k=60 硬编）。**哪一套跑在真实检索里，哪一套是死代码**？两套并存这件事，谁在维护它们的口径一致？
> `chases`: A86, A14, A94 ｜ `intent`: 双实现的存活判定与维护责任 ｜ `depth`: L3

**Q192.** A87 说淘汰候选时有"一个 penalty 逻辑在算该拿掉哪一条"。**这个 penalty 函数的形状是什么**？它里面有没有和 A16 那 9 个常量同性质的、无依据的魔数？
> `chases`: A87, A16 ｜ `intent`: penalty 逻辑是否又是一层无依据阈值 ｜ `depth`: L2

**Q193.** A88 说切分是句子正则 + 超长句按字符窗口硬切（citation chunk 上限 240 字符），兜底是 `parent_context`（最多 1200 字符）和 `neighbor_chunk_ids` / `parent_chunk_id`，**没有 overlap、没有检索时的邻接扩展**。那么一个被硬切在句子中间的引用，**用户看到的是残句，还是被 1200 字符的 parent_context 补全**？补全那一步在服务端还是前端？
> `chases`: A88, A83 ｜ `intent`: 切分与展示的一致性实现位置 ｜ `depth`: L2

**Q194.** A89 说"引用失效 → coverage 不足 → abstain"两条线"不冲突"，但边界又说"我不能指出有一个回滚机制"。**"引用失效会导致 coverage 不足"这件事，是你从代码读出来的因果，还是你的推断**？请指出把它连起来的那一处代码。
> `chases`: A89, A85, A84 ｜ `intent`: 跨子系统因果链是否有实现依据 ｜ `depth`: L2

### T10 — 工程基础（追杀 A91–A100）

**Q195.** A95 的边界说"我没有写过一个故意在 executor 里读 ContextVar 看它丢的验证测试"，A5 又说这个项目根本不用 ContextVar 存配置。**那你对这个项目里取消安全的实际了解有多少** —— 你能不能指出一条**本项目的、真实存在**的 `finally` 清理路径，或者一次你亲自排查过的取消/超时问题？
> `chases`: A95, A97, A5 ｜ `intent`: 基础题是否落到本人真实经验 ｜ `depth`: L2

**Q196.** A99 说丢失更新由版本 CAS 兜底，A99 的边界又说"CAS 能兜住是从代码结构判断的、没见过实测"，A26 说激活走 CAS、A33 说运行时没有持久化 plan version。**memory 侧的写入到底是 CAS 还是普通覆盖写**？请你把"读 → 判断版本 → 写"这三步的落点说出来。
> `chases`: A99, A26, A33, A27 ｜ `intent`: CAS 兜底的可落地性 ｜ `depth`: L3

**Q197.** A93 说超时不能断定远端没执行，A96 说安全重发依赖 `CONFIRMED_NOT_EXECUTED`，A47 说对账执行器不存在。**那么今天这个系统里，一个"已发出但未知"的副作用，从产生到被安全处置，最短路径是什么**？这条路径今天走得通吗？
> `chases`: A93, A96, A47, A46 ｜ `intent`: 未知副作用的端到端处置可达性 ｜ `depth`: L3

**Q198.** A97 讲了 `CancelledError` 的正确写法。**在你这个项目里，哪一处代码是你亲自写的、带 `try/finally` 的清理逻辑**？如果没有一处，那这道题你答的是通用语义，和你"写过并发代码"的画像之间有一条缝。
> `chases`: A97, A5, A23 ｜ `intent`: 通用语义与本项目经验的连接 ｜ `depth`: L2

**Q199.** A98 说索引应该定成 `(user_id, project_id, created_at DESC)`，但 A22 说存储层的"project"实际是 `workspace_id`、`thread_id` 也进 WHERE。**那真实的 WHERE 到底是几个条件**？如果实际查询是 `user_id + agent_id + project_id + thread_id` 四个等值列，你的索引建议要不要改？
> `chases`: A98, A22, A24 ｜ `intent`: 索引建议是否匹配真实查询形状 ｜ `depth`: L2

**Q200.** A100 说"今天的回归集并没有真正固定住这条边界"——有 direct route 的断言，但没有任何一条断言"这类 query 应该回落到 ReAct"。那**简历第一条 bullet 里的"用回归测试固定路由边界（含自定义 MCP 名称递归与自然语言参数抽取）"这句话，今天还算不算数**？你会不会现在就把它改掉，改成什么？
> `chases`: A100, A8, A53 ｜ `intent`: 收口——把已自认失准的措辞当场修正 ｜ `depth`: L3

---

## 附录：本次实际打开的文件

- `D:\projects\zuno\docs\red-blue\rounds\rb-2026-10-07-formal-020\01_simulated_resume.md`
- `D:\projects\zuno\docs\red-blue\rounds\rb-2026-10-07-formal-020\02_red_questions.md`
- `D:\projects\zuno\docs\red-blue\rounds\rb-2026-10-07-formal-020\03_blue_answers.md`（分三次读完：1–773、774–1168、1169–1425）
- `D:\projects\zuno\.agent\red-blue\attack-model.md`

未打开：`03_blue_architecture_notes.md`、`docs/red-blue/` 下任何其他文件、Zuno 的 `src/` / `tests/` / `Evidence` / canonical docs / `docs/governance/` 下任何被候选人引用到的文件（均为盲态，未核实）。
