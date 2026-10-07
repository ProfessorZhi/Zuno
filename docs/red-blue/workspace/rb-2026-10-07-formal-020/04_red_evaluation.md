# Red Final Evaluation — rb-2026-10-07-formal-020

```text
blind: true
seen: 01_simulated_resume.md, 02_red_questions.md, 03_blue_answers.md,
      04_red_wave2_review_and_questions.md, 04_blue_wave2_answers.md,
      .agent/red-blue/attack-model.md
not_seen: 03_blue_architecture_notes.md, 04_blue_wave2_architecture_notes.md,
          canonical docs, src, tests, Evidence, docs/governance, docs/decisions,
          docs/evidence, 任何其他 docs/red-blue/ 文件
```

---

## 1. 总判断

**综合：PARTIAL。**
**技术判断力侧 PASS（偏 STRONG_PASS）；实现叙述与引用精度 PARTIAL；历史真实性 NOT_ESTABLISHED —— 而且 Wave 2 让这一层变差，不是变好。**

我不给 STRONG_PASS，因为我认为整轮最该被信任的那一层（历史真实性）从 Wave 1 到 Wave 2 **没有被修复，反而被候选人自己进一步拆掉**（A101 / A136 / A143 / A156 / A158）。
我不给 FAIL，因为两轮 200 个回答里，我没有抓到**一处实质性的向上编造**；相反，Wave 2 里有约 55–60 处主动削减自身 claim、约 7–8 处直接反驳我的问题框架，其中若干处方向对他自身不利。

分层结论：

- **技术判断力：可信，且是本轮最强的资产。**
  他能稳定区分「机制存在 / 机制接线」「被测量 / 被推断」「能力 / 在跑的约束」「设计默认 / 今天可达」。这三组区分不是背出来的，因为他在 Wave 2 里用这三组区分**推翻了自己 Wave 1 的多个说法**，并且在我把推论做过头时把我推回来（A144、A150、A125、A111）。一个只会顺话的候选人不会做后一件事。

- **实现细节：方向可信，粒度不可信。**
  他对「这套机制长什么样、缺哪一半」的描述两轮高度自洽；但他对「这套机制在哪一行」的自述在 Wave 2 里被他自己修了 4 处（A156 / A186 / A196 / A199），并撤回了 6 处 Wave 1 里讲得比证据强的断言（A132 / A141 / A161 / A163 / A192 / A194）。
  **这意味着 Wave 1 的"全押在 file:line 精度上"这个溢价必须打折** —— 他不是逐行读着写的，有相当一部分是记得 + 部分 grep 拼出来的。这不等于编造（他修的是"位置"，不是"事实"），但它确实把"引用精度 ≈ 真实性"的等式废掉了。

- **失败窗口意识：反常地强，而且 Wave 2 是他自己往下挖的。**
  Wave 2 里**新挖出**的洞至少有五个：`user_id=self.user_id` 是实例冻结而非请求级（A104/A106）、幂等位 TTL 到期后是重新 dispatch（A108/A109）、`reconcile_generations` 零调用方（A141）、`stale` 没有生产者（A132）、`evidence_stale` 没有消费方（A189）。这五处**没有一处是我在 Wave 1 供给他的**。这是我两轮里看到的最硬的真实性信号。

- **历史真实性：结构性不可恢复，且两轮独立确认。**
  非文档物证 = 0（A158）；git 首 commit 与他的首笔改动同日、同身份谱系（A101）；`architecture.md` 是 Runtime 建好之后写的 Target 文档（A136）；ADR-0005 无 approver 且实现层未被执行（A143）；ablation 协议是上一轮 Red/Blue 的产物（A123）；Pilot 只有一句汇总反馈、零物证、零第三方标准（A169–A175）。
  注意措辞：这一层是 **NOT_ESTABLISHED（无法建立）**，**不是 FALSIFIED（已证伪）**。作为盲面试官，我只能说"我不信他能证明"，不能说"Zuno 的真实历史不是这样"。

- **工程基础功底：教科书级正确，但项目内不落地。**
  Wave 1 的 A91–A100 我基本认可。Wave 2 的 A195–A199 把这条线的缝暴露了：`grep finally` 在他工作过的文件里 = 0；他没有一次"我亲自排查过的取消/超时 bug"；没有一次 EXPLAIN；A98 的索引建议建立在错误的 WHERE 形状上（A199 自己改了）。所以他的基础是**通用语义层扎实，项目经验层空缺**。

**对整轮读法的元警告（必须写在最前面）：**
A183 是本轮信息量最大的一个回答。他承认自己的「边界」字段——也就是 Wave 1 里我判为"最强真实性信号"的那个东西（"骗一个人去承认我没实现，比让他承认我实现了要难得多"）——**它的形态被一份他读过的面试验收标准塑造过**。这意味着：**"自曝 = 真实"这个推理的权重，必须整体下调。** 我仍然认为自曝的事实陈述是真的（自曝的具体事实不因形态被塑造而变成假的），但我不能再把"自曝的密度"当作独立的真实性证据。我 Wave 1 的 §2.1 那一节需要按这个折扣重读。

---

## 2. Blue 1 → Blue 2：真解释还是话术补洞

先把方法论说清：Wave 2 是我**指名追问**的一波，所以"他按题作答"本身不构成信息。有信息量的是两件事 —— 一是**修正的方向**（削减自身 / 维持 / 增强），二是**修正是新增了事实，还是只换了一种说法**。

### 2.1 逐条点名：Wave 1 缺口在 Wave 2 的处理

| Blue 1 的缺口 | Blue 2 的处理 | 判定 |
| --- | --- | --- |
| A3 删转发层的动机是事后重建的，无当年 failure | A103 原样维持：`Unknown（动机）`；只补了一个 after-state（`MCPToolAdapterNotBound` fail-closed） | **真解释（诚实的 Unknown）**，但 bullet 1 的必要性至今**没有任何证据** |
| A8/A100 direct route 在 `src` 里没有对应物；"用回归测试固定路由边界"只固定了一半 | A200 **当场重写**整句，给出逐段可核的替换版本，明确标出"ReAct 回落侧暂无回归断言" | **真解释 + 主动修正**。这是全轮处理得最干净的一条 |
| A15/A16 四信号等权相加、9 个阈值无依据 | A121 用「机制 vs 数值」切开：机制是 bad case 逼的，数值是为"看起来完整"拍的；A124 把 hop/path 上限并入同一根线 | **半真解释** —— 切分本身合法，但结果是同一批事实被两套说法各自解释；"为什么是 6"至今没有 |
| A20 "GraphRAG 退出条件是测量性的" | A123 主动查了协议文件头：`source: red-blue rb-2026-09-15-formal-019 / IMP-019-05`，`frozen_at: 2026-10-07` | **恶化，不是被解释。** 他最强两条 bullet 的退出条件，挂在一份**面试流程产物**上。他不但没辩护，还自己把它摆上桌 |
| A25/A28 授权与 Domain 权威靠 `reference.md` 的措辞 | A133/A190 把适用域收窄（"两边都有才叫冲突"；abstain 管不到 memory↔Domain） | **真解释（收窄）**，但裁决点仍然不在代码里 |
| A29/A30/A40/A50/A80 全落在 Target/Unknown | A134 **把 A30 的说法改了**："三个条件都不成立 → 留着"是不诚实的，正解是"我没能证明它不必要" | **真解释，且改得更不利**。这是全轮最漂亮的一次自我修正 |
| A71/A72/A73 减法实验是直觉，不是测量 | A176 **承认口径不一致**："A71 说没统计过是**不一致**的，那是'我没做'不是'做不了'" | **真解释（认账）** |
| A81/A82 两条互不连通的 `ready` 链，消费方未核对 | A185/A186 **部分确认**：产品侧链有读者；硬编 `"ready"` 的真实位置是 `platform/services/rag/handler.py:486,489`（**A81 引错了文件**）；两条链无漂移防护 | **真解释 + 引用修正** |
| A55 时间线异常（首笔改动与"重构落地"同日） | A101/A160/A162 **继续加深**：`eafeb1c2` 与 `77346758` 是同一身份谱系，所以他连"eafeb1c2 不是我这条谱系"都证明不了 | **恶化（自我加深）** |
| A41 "这一层不是我的 Ownership" vs A42–A48 细节极熟 | A146 给出机制：他是这一层的**调用方**（`simple_agent.py:1287-1330` 是 `ToolInvocationGateway` 的 composition 根） | **可信但不可验证的解释**。它同时是"ownership 缺口"的最合理开脱，我盲态分不开这两者 |
| A51 说不出一个"我亲眼看到它跑通"的入口 | A158：非文档物证**也找不到**；"3 月已存在"支撑 = 文档自述，独立可核性 = 0 | **真解释（维持 Unknown）** |
| A65–A70 Pilot 定性不是他给的、无验收文书 | A169–A175：全部确认；A170 明确"物证 = 一条汇总反馈，其余无"；A175 承认整条链**是自证** | **真解释（且更狠）** |
| A11 的 baseline MRR@10=0.90 与 A60 的修复后 1.00 互相打脸 | A113 **用一个新事实解开**：两个数属于两次不同的 run，且 **baseline 自己在 rerun 中也从 0.90 漂到 1.00**，provenance 原文禁止制造单机制收益百分比 | **真解释。** 问题问的是"哪个对"，他给的答案是"两个都不该这么用"。顺话的人会挑一个数字 |
| A6 tool 执行那一步没有 `wait_for` | A107：最坏挂到连接层 300s 或外部重启；上层 reaper **无证据** | **真解释（缺口维持）** |
| A7/A47/A96 幂等位 60s TTL + 对账无执行器 | A108/A109 补上了精确语义：行不删，`expires_at` 过后 UPDATE 分支把 generation+1、status 重置 → **重新 claim → 直接 dispatch（打第二次网络）** | **恶化但被精确化。** 洞比我描述的更实：不只是"没有支撑"，是"60 秒后默认打第二枪" |
| A42 两次授权检查之间的 TOCTOU 没有竞态测试 | A147 给出窗口的**组成**：至少一次 DB 写 + 一次 DB 读，可能再加 dispatch；并明确"若撤销发生在第二次检查之后，这次检查抓不住" | **真解释** |
| A43 生产侧没有任何代码路径会 revoke 一个 epoch | A148/A149 确认，并给出方向（在 08 补生产者，且承认很可能补不上、明年还在） | **真解释**，但这是他自己已经交过的一把刀 |
| A36 两存储无 2PC；reconciliation 无测试导入 | A140 **撤回自己的并列讲法**（outbox 覆盖 domain→事件，覆盖不到 domain→checkpoint）；A141 **升级缺口**：`reconcile_generations` 在 `src/` 里**零调用方**，A37 的"以 Domain 为准"今天**没有执行者** | **恶化 + 精确化 + 撤回** |
| A5 并发注入没做对抗测试 | A104/A106 **自己挖出更硬的洞**：`_execute_binding_tool` 传的 `user_id=self.user_id` 是**会话实例属性**，构造时冻结，不是从本次请求取的。同实例被不同用户复用就会串 | **恶化（他自己挖出来的）**。这是 Wave 2 最有价值的一条 |
| A99 多轮并发写入没有对抗测试 | A196：CAS 是真的（`PlanVersion.activate`，`task_contracts.py:476-489`），并**修正行号**（A99 引的 `:345` 是类定义，不是 CAS 点） | **真解释 + 引用修正** |
| A33/A35/A38/A47 一串"写了没接线" | A110/A137/A141/A150/A181 补齐；**A150 给出反例**：`assert_audit_durable_for_effect` **在活路径上**（`invocation_gateway.py:1499` 由 `:432` 调） | **真解释，且主动加了反例** —— 说明这份"没接线清单"不是一概而论 |
| A80 用面试验收标准当"09 该被质疑"的技术依据 | A183 **直接承认**："技术判断在前，标准在后；但我的'边界'字段有多少是按那份标准写的——**是有的**" | **真解释（自认），但这是对 Wave 1 最强信号的一阶折价** |
| A51/A52 vs A53 同一套 commit 的两种用法 | A159 **给出明确规则**：commit 只在"存在性"上算数，**永远不在"归属"上算数**；并接受这削弱 A53 | **真解释，规则清晰** |
| A60 说留第 2 条是因为"claim 和证据匹配" | A161 **当场否掉自己**："按我自己的判据，它**不满足**"；真实理由是"五条里唯一有回归测试固定住的" | **真解释（自我否证）** |
| A74 承认 guardrail 阈值层是为完整度加的，同时用它给第 2/3 条 bullet 埋雷 | A178 **重新切片**：第 2 条 = 止血（有 bad case）；无 bad case 的 guardrail 属于第 3 条 | **混合** —— 切分合法，但效果是把"架构自嗨"的自认从**被保留的那条 bullet** 上摘下来 |

### 2.2 修正的方向分布：这是判"查记录"还是"顺话"的关键

把 A101–A200 按修正的**方向**分类：

- **削减自身 claim（约 55–60 处）** —— 绝大多数。
- **维持 / 精确化（约 30 处）** —— 补机制细节，不改变结论。
- **逆 interviewer 框架的推回（7–8 处，少但都承重）**：
  - **A111** —— 我说 adapter 是壳，他补：它同时是 fail-closed 准入闸门（`MCPToolAdapterNotBound`），所以"壳的部分可以挪，注册表 + 缺失即拒这条语义不行"。
  - **A125** —— 我问"`graph_available` 停在 true 会不会带着坏图跑"，他说**这一层不成立**：它不是持久化健康位，是每轮重算的（然后才补边界）。
  - **A144** —— 我说 A39 内部有矛盾（那条测试在防什么），他说**我把他的 A39 读过头了**：那条测试防的是"过渡期残骸"（phase/cutover 命名的文件），不是"锁死方向"。
  - **A145** —— 我给的框架暗示"可行就是选择"，他不只接受，还**把自己 A40 的 hedge 升级掉**：单实例 PG 上两笔写进一个事务技术可行，所以"两个引擎"是**架构选择，不是技术限制**。
  - **A150** —— 我按"写了没接线"的口径问他审计断言，他答**它是接线的**，并主动指出这给那份清单切出一个反例。
  - **A163** —— **修正 A54 的一个错**：`multi_agent_enabled` **有** reader（`product/runtime_batch.py:428` 处一条"产品面不许变成第二个 controller"的断言）。方向是让多 Agent 残骸的故事**更强**，不是更弱。
  - **A173** —— 对"为什么材料呈现 224 而不是 FULL CI NOT RUN"，他轻微辩护："两个数同时在那两份文档里，不是藏了一个"。

**结论：以"回去查了记录"为主，不是"顺着你的话说"。** 三条理由：

1. **A113 的解矛盾方式**。问题本身是个二选一陷阱；他拒绝选，找出了第三个事实（baseline 自己漂了），而这个事实**削弱了他被保留的那条 bullet**。
2. **A150 / A163 / A145 是逆方向的**。一个按评测标准优化的人不会给出"反例"、不会把残骸讲得更严重、不会主动放弃一个可以拿来做技术挡箭牌的约束（"两个引擎，没有 2PC"）。
3. **A200 交付了红队没给的新产物**（逐段可核的替换句），A102 交付了红队没给的**hunk 级指认**。这是"手里有东西"，不是"嘴上会说"。

但**必须同时记下三条反面证据**：

1. **A138 自述了修正的时点**：`plan_version` 那个纠正，是他**准备 Wave 2 的时候**才发现的，不是早就知道。也就是说，**至少有一部分 Wave 1 的错误，是在被对抗性追问之后才消失的**。真实面试只有一波。
2. **A183 承认形态被标准塑造**。自曝的密度不能当独立证据。
3. **约 6 处实质撤回 + 4 处引用修正**发生在 Wave 2。这些在单波面试里会原封不动地留在成绩单上。

### 2.3 三处"先解释、后变糟"

这三条不是话术，相反它们是真解释——但解释完之后这个 claim 比解释之前更弱，我把它单列，因为它们是本轮最重要的增量信息：

1. **A123** —— 他解释了"GraphRAG 退出条件为什么是测量性的"，代价是这个论证的载体（`rb019-graphrag-ablation-protocol.md`）是**面试流程产物**，不是工程产物。
2. **A132 + A141** —— 他解释"`stale` / reconciliation 怎么兜底"，代价是 `stale` 没有生产者、`reconcile_generations` 零调用方，和 A43 的 epoch 是**同一个形状**（门在、锁上了、没人能转锁）。
3. **A156** —— 他纠正了负向历史 #201–#207 的出处，代价是 A48/A49/A76 的整条"演进叙事"从一份产品侧 evidence 文档，挪到了**未合并的 test-only 诊断分支产生的 fault probe** 上。

### 2.4 一句话总结这一节

**Wave 2 主要是真解释。** 唯一真正接近"话术补洞"的只有 A121 的「机制 vs 数值」与 A178 的「bullet 2 vs bullet 3」两处再切分 —— 它们都合法，但共同点是**让同一批事实同时支持两种说法，并且把不利的那一半挪离被保留的 bullet**。而真正的问题不在"他是不是在补洞"，在于：**他的准确性只有在被追问之后才到位。**

---

## 3. 五维结论

### Ownership

**结论：个人 Ownership 稳定地落在"在一个既有系统上做出的、很窄的一段"，以及"判据/阈值的定者"这个位置上；两条 headline bullet 的 Ownership 是撤退，不是建立。**

- 能建立（commit 粒度 + 测试粒度）：检索 heuristic 层（`5d9b719e`/`c7814793`/`c17f737f`/`762ffdc7`，均 2026-06-20，各自有测试）、产品侧 tool 配置注入（`77346758` 的一个可指认 hunk）、memory readback（`f3c74338`/PR #8）。
- 撤退：bullet 1 的"路由收紧/回归固定"（A200 自认只固定一半）；bullet 4 的"四维隔离"（A182 自认"照结构念的成分多于照语义讲"）；A166 **接受"局部改动的实现者"这个定位**——他说没有任何一个跨模块接口是他定的。
- 从未建立：被重构对象（子 Agent 转发层）的作者与动机；任何 blame 级归属（A59/A159）；"第一笔改动"（A52/A160）。
- 我不会把 A59 的"仓库里只有一个身份谱系"判成借口：这是对"归属不可独立验证"的一句**结构性陈述**。但它同时意味着**这一整层的可验证性是零**——不论对他有利还是不利。

标签：`OWNERSHIP_GAP`

### Implementation

**结论：他描述的"活路径"远窄于他描述的"架构"；而且这个落差是他在 Wave 2 里自己一块块量出来的。**

Wave 2 新增的"写了没接线 / 缺一半"清单（全部由他主动交出）：
`reconcile_generations`（零调用方）、`escalate_due_reconciliations`（只被测试调）、`stale`（无生产者）、`evidence_stale`（无消费方）、`memory_use_traces` / `context_pack_versions`（无 reader）、`append_plan_version`（无 caller）、`BranchResultFencer` / `DynamicStepWorker`（无 caller）、`RecoveryAction.RESEND_OUTBOX`（无执行者）、对账远端查询（未实现）、epoch revocation（未实现）。

反例（他主动指出，说明不是一概而论）：`assert_audit_durable_for_effect`（活）、abstain 路径（活）、`citation_eligibility='REJECTED'`（被 SQL 过滤，活）、memory 版本 CAS（活）、产品侧 pipeline 链（活）。

**我能判的是「他的叙述」与「他自认的落差」；我不能判这是架构问题还是实现问题。** 后者是 Blue 架构侧的权限。

标签：`NARRATIVE_GAP` + `UNVERIFIED_BY_BLIND_RED`

### Failure

**结论：失败语义的表述能力很强、覆盖面广、自曝密度高；但被陈述出来的大量失败通道，其"处置端"是空的。**

- 表述层：他稳定地区分"未执行 / 已执行结果未知 / 旧版本晚到 / 权限中途变化"，并且能落到 `DispatchCertainty`（三档）、`EffectCertainty`、`recovery_rule`（三档）、`UNKNOWN 不许降级成 FAILED` 这些具体语义上。A157 甚至给出了合并 `execution receipt` 会失去哪一个分辨力（`MAYBE_DISPATCHED`）——这是真的机制级回答。
- 实现层：A197 的收口答案是"**产生得通，处置不通**"。A152 的终态是"OPEN，停住"。A153 自认"安全守卫依赖一个人工动作"。A142 自认"人点恢复 = 不恢复"。
- **Wave 2 里他自己新发现的失败窗口**（这是我给他失败窗口层打高分的主要依据）：实例冻结的 `user_id`、TTL 到期后的重新 dispatch、`stale` 无生产者、`reconcile_generations` 无调用方、`evidence_stale` 无消费方。**五处，无一处由我供给。**

标签：`NARRATIVE_GAP`

### Evidence

**结论：这是五维里最弱的一维，而且 Wave 2 让它更弱。**

- 最强 bullet（第 2 条）的数字：**可复现性为零**（A115 自认"它就是转抄"；raw report gitignored）；样本是 5-query smoke；baseline 自己在两次 run 之间漂了 0.90→1.00（A113）；过拟合**无法排除**（A122）；唯一的界定物是 A123 披露的**面试流程协议**。
- `224 passed` = selected suite；`FULL CI: NOT RUN`（A173，两个数并列在同一批文档里，这一点我接受他的辩护）。
- 性能/规模：QPS / latency / cost / 用户量 / 法院数量 —— **一个数都没有**，且他从不给（A19/A66/A124）。
- Pilot：物证 = 一条汇总反馈；验收标准**零条**第三方；"Pilot Validation"是内部里程碑名（A169–A175）。
- 正向的一面：他从不制造数字。**"我不给这个数"这句话他说了至少六次**，而且每次都能说清为什么没有。

标签：`EVIDENCE_GAP`（重）+ `SIMULATED_RESUME_GAP`

### Fundamentals

**结论：通用语义层扎实（Wave 1 A91–A100 我基本全认），项目经验层空缺（Wave 2 A195–A199 自己暴露）。**

- 扎实的部分：GIL 与 I/O 释放、READ COMMITTED 下"语句内读"与"读-改-写拆到语句外"的区分、timeout ≠ 远端未执行、coroutine 取消 ≠ 远端终止、`create_task` 拷贝 context 而 `run_in_executor` 不继承、`CancelledError` 继承 `BaseException`、复合索引最左前缀。这七条他不是背定义，是在讲语义边界。
- 空缺的部分（A195/A196/A198/A199 自曝）：`grep finally` 在他工作过的文件里 = 0；项目内找不到一条"我亲自写的带 `finally` 的清理"；没有一次"我亲自排查过的取消/超时 bug"；没有一次 EXPLAIN；A98 的索引建议建立在错误的 WHERE 形状上（真实是四列等值，A199 自己改了）。他唯一能指的 `finally` 在 `sandbox.py`，**不是他写的**。
- 桥接的诚实度反而加分：他没有把这些八股硬包装成"我们项目里我就是这么干的"。

标签：`FUNDAMENTAL_GAP`（限"项目内不落地"这一面）

---

## 4. Resume Claim 处置

处置分布：**保留 1 / 降级改写 4 / 删除 0**。

我不替他写简历，只给处置、理由和改写方向。

| # | bullet | 处置 | 理由 | 改写方向 |
| --- | --- | --- | --- | --- |
| 1 | 重构单 Agent Tool Calling 与 Workspace 路由 | **降级改写** | "重构"预设了一个长期存在的被改造物；但 A55/A101/A160 确立：那套转发脚手架的唯一痕迹是 `77346758` diff 的 before 一侧，而仓库首 commit（`eafeb1c2`）与他的首笔改动同日、同身份谱系。A102 又把可指认的 hunk 窄化到**skill 路径**上一个函数改名，不是 tool 路径。A8/A200 确立"用回归测试固定路由边界"只固定了 direct route 准入侧，**没有任何一条断言 ReAct 回落**。A104/A106 表明"调用时注入用户配置"只对了一半：`user_id` 是实例冻结属性，不是请求级。 | 降级动词（去掉"重构"），改述为"**拆除初始快照中即存在的转发脚手架，把 MCP Tools 直绑主 Agent，并在调用点注入用户级配置**"；把"配置跨层传递"这条动因标为**推断**；回归那一句改成他自己在 A200 给出的版本（direct route 准入 + 参数抽取 + 自定义名称递归；**明写 ReAct 回落侧无断言**）。不要保留"跨层传递用户配置"的因果叙事。 |
| 2 | 定位并修复 GraphRAG 排序回退 | **保留** | 全五条里唯一有"被测量到的 bad case → 修复 → 回归测试"三段链的（A161 自认它也**不满足**"claim 与证据匹配"这个更高的判据，但它是唯一有三段链的）；A168 确认措辞没越过"bounded regression fix"的上限。措辞本身**没有**宣称 GraphRAG 有收益，这是它值得保留的原因。 | 保留为"**定位并修复**"；但附两条硬上限：(a) **任何材料里都不得出现提升/恢复 baseline 的数字或措辞** —— A113/A115 已证该数不可复现、baseline 在两次 run 之间漂移；(b) 把"发现"降为"定位到"（A11 明确不愿 claim 首发发现）。 |
| 3 | 继续优化多跳图检索 | **降级改写** | A16/A124：9 个阈值 + `graph_hop_limit` / `max_paths_per_entity` **全部无依据**，无扫参、无分布、代码无注释、`measurement_status: BLOCKED_PENDING_DATA`。A18/A122：无 holdout、过拟合无法排除。A56：方向不是他提的。A178：本 bullet 的主体（guardrail 阈值层）正是 A74 里他自认"为架构完整性加的"那一层。A123：唯一能给它设界的东西是面试流程产物。"恢复到 baseline 水平"是 5-query smoke。 | 把"优化"改成"**实现/调整**"；把三件活（seed expansion、别名归一化、path-aware ranking）与阈值层**分开陈述**，并注明阈值是经验值、效果未测量；把"5-query smoke"如实保留并**明写这不是 holdout**；删掉任何"改善/恢复"的因果断言。若只能留一句，留"实现了三个 heuristic 并有单组件回归测试，其净收益未经测量"。 |
| 4 | 构建 scoped Context / Memory V2 | **降级改写** | A24/A53/A126：所在文件已被删（`ab1222da`，2026-08-04），今天是 Historical 而非 Current；归属只能靠 commit 存在 + 自述（blame 不可切）。A22/A78/A127/A182：四维 scope 中 `agent_id` 恒定无消费方，他本人今天就愿意砍掉两维，且自认"四元组合"是照结构念多于照语义讲。A29/A30/A134：无对照实验，且他把 A30 的说法改成"我没能证明它不必要"。A128：它一次写的五张表里有两张**没有 reader**。 | "构建" → "**参与/实现**"；把"scope 约束"从"四维隔离"降为"**scope 过滤 + review/provenance 状态机**"；**明标该实现所在的文件此后被删除**；不得暗示任何收益测量。若读者的口径是"只保留今天仍在代码里的 claim"，则本条应与第 5 条**合并为一条历史性条目**，而不是两条。 |
| 5 | 收紧 Memory readback | **降级改写**（若不合并则保留为窄条） | 实质是他做的（`f3c74338`，PR #8），方向具体、可指认——这条是他最干净的实现 claim。但措辞每一段都有问题：`prepare_context()` **今天不是函数**（A24，全 `src/` 无 `def prepare_context`）；"同 scope"这道保护**没有任何负向测试**（A130：没有一条"故意传错 workspace_id → 断言读不到"）；他引的 "focused tests" 覆盖的是过滤逻辑，不是跨 scope 泄漏。 | 把 `prepare_context()` 换成"**回合前的上下文构建节点（`build_context`）**"；保留过滤条件的具体描述；把"focused tests"准确化为"**覆盖过滤逻辑的测试**"，并明写**跨 scope 泄漏无负向测试**。 |

**关于"删除"：一条都不建议删。** 理由：五条 bullet 的核心事实都有 commit 支撑，问题出在**动词强度与措辞对应的机制**上了漂，属于改写问题，不属于删除问题。真正需要删的是**材料里附带的因果叙事与数字**（"所以 GraphRAG 更有用"、"恢复到 baseline 水平"、"配置跨层传递会静默降级"），而不是 bullet 本身。

---

## 5. Findings

> 我使用我盲态下有权判断的标签：`SIMULATED_RESUME_GAP` / `NARRATIVE_GAP` / `OWNERSHIP_GAP` / `EVIDENCE_GAP` / `FUNDAMENTAL_GAP`。
> 凡涉及"Zuno 该怎么办 / 这是架构问题还是实现问题"的，一律标 `UNVERIFIED_BY_BLIND_RED` —— 那是 Blue 架构侧的权限，不是我的。

**F01｜引用精度溢价失效（`EVIDENCE_GAP` + `NARRATIVE_GAP`）**
Wave 1 的可信度结构是"全有全无、全押在 file:line"。Wave 2 里他自己修了 4 处引用位置（A156 负向历史出处整份引错；A186 硬编 `"ready"` 引错文件；A196 行号指到类定义而非 CAS 点；A199 索引建议基于错误的 WHERE 形状）。**这不是编造，但它证明 Wave 1 的引用不是逐行读着写的。** Red Wave 2 的 kill switch（"若有一处 file:line 被证明是编的 → FAIL"）**未触发**；但该条件所依赖的前提（引用是写时新读的）已被他自己的修正证伪，因此该溢价应下调，而不是维持。

**F02｜Wave 1 有约 6 处机制断言在 Wave 2 被撤回（`NARRATIVE_GAP`）**
A33"单调 plan_version 是核心信号"、A87"有一个 penalty 逻辑"、A89"引用失效 → coverage 不足"、A27"状态机在兜底"（→ A132 `stale` 无生产者）、A54"`multi_agent_enabled` 无 reader"（→ A163 有 reader）、A60"claim 与证据匹配"（→ A161 自认不满足）。**在单波面试里，这六条会原封不动进入成绩单。**

**F03｜`user_id=self.user_id`：他自己挖出的并发洞（`FUNDAMENTAL_GAP`）**
A104/A106：`_execute_binding_tool` 传的 `user_id` 是**会话实例构造时冻结**的属性，不是从本次请求取的。因此 A5 的"不会串"实际只覆盖"同实例同用户"；同实例跨用户复用会串。**A5 的"不会串"两轮都没有对抗测试支撑，而 Wave 2 给出了它可能不成立的具体机制。**

**F04｜幂等位 TTL 60 秒之后是"重新 dispatch"（`EVIDENCE_GAP`）**
A108/A109：行不删，`expires_at` 过后 UPDATE 分支重置 status/generation → 重新 claim → 直接 dispatch。叠加 A47（对账远端查询未实现、无执行器），结论是"**确定没执行才重发**"这个守卫在 60 秒之后**没有实现支撑**，默认行为是再打一次网络。

**F05｜`stale` 与 epoch 同形：门在、没人能转锁（`NARRATIVE_GAP`）**
A132：`memory_state` 的唯一写入值是 `"decayed"`，`stale` 只出现在读侧排除集合里——**读侧挂了排除，生产侧没有出产者**。这与 A43 的 epoch（只有 INSERT/JOIN/SELECT，唯一 revoke 是测试里的裸 SQL）是同一个形状。

**F06｜`reconcile_generations` 零调用方（`NARRATIVE_GAP`）**
A141：它在 `phase08.py:342` 定义、被 `agent/runtime/__init__.py:40` 再导出，但 `src/` 里**没有任何调用点**。因此 A36/A37 的"以 Domain 为准"的一致性收敛规则，今天是**被建模的规则，没有执行者**。

**F07｜900 秒升级规则没有触发者（`NARRATIVE_GAP`）**
A110：`escalate_due_reconciliations` / `timeout_due_async_jobs` 的调用方**只有测试**，`src/` 里没有 cron / worker。所以一次真实的 UNKNOWN effect 的终态是 **OPEN，停住**（A152）。"转人工"是设计默认，不是可达动作。

**F08｜两条同名不同源的 `ready`，无漂移防护（`NARRATIVE_GAP`）**
A186：`KnowledgeVersion` 的 `READY`（硬前置：两个可见索引）与 `rag/handler.py:486,489` 的 `health_status or "ready"`（默认值）是两个东西。cutover 和检索读严格知识域那条；**没有任何代码在对齐它们**。

**F09｜同系统内两种陈旧标记，一个接线一个不接（`NARRATIVE_GAP`）**
A189：`evidence_stale` 只在校验时返回，**下游没有消费方**；`citation_eligibility='REJECTED'` 会被 SQL 过滤，**有消费方**。"这条引用已经废了但没人知道"与"系统知道并挡住了"在同一个系统里并存。

**F10｜最强 bullet 的数字不可复现，且 baseline 自身漂移（`EVIDENCE_GAP`）**
A113/A115：审计那次 baseline `MRR@10=0.90`、local `0.80`；同日 rerun 里 **baseline 也变成 1.00**，local 也是 1.00 —— 即"打平"而非"超过"。raw report gitignored。provenance 原文禁止据此制造单机制收益百分比。**"修复前后"这个提法在证据上不成立。**

**F11｜GraphRAG 的退出条件挂在一份面试流程产物上（`EVIDENCE_GAP`）**
A123：`rb019-graphrag-ablation-protocol.md` 文件头写 `source: red-blue rb-2026-09-15-formal-019 / IMP-019-05`、`frozen_at: 2026-10-07`。他"靠测量决定去留"的整套论证，其载体是**评测流程产物**，且 `measurement_status: BLOCKED_PENDING_DATA`。这是本轮最尖锐的一条：**他唯一诚实的复杂度举证策略，本身没有工程侧的落点。**

**F12｜演进叙事的证据换到了未合并的 test-only 分支上（`EVIDENCE_GAP`）**
A156：A48/A49/A76 用的负向历史 #201/#203/#205/#207 **不在** `implementation-wave-001.md`；实际在 `current-test-baseline.md` 等处，且它们是**未合并的 test-only 诊断分支产生的 PostgreSQL fault probe**，使用 test-only Alembic compatibility alias。性质从"产品证据"变成了"测试探针证据"。

**F13｜`architecture.md` 是事后 Target 文档，Runtime 的 necessity 叙事失去立项依据（`NARRATIVE_GAP`）**
A136：`status: normative-target`、`architecture_state: ACCEPTED_TARGET`，git 最近改动 2026-09-16/20/24 —— 写在 Runtime 建好之后。"四种失效窗口"是**事后归纳**，不是当年的立项书。

**F14｜ADR-0005 无 approver，且实现层与其明文相悖（`UNVERIFIED_BY_BLIND_RED` + `NARRATIVE_GAP`）**
A143：文件里只有 status/date，没有 approver 字段；ADR 明确"不批准永久 dual checkpointer runtime"，而主线恰是 dual（自研桥在跑、官方 saver 只挂在无生产 caller 的 `phase08.py`）。**我能判的是"他的叙述里制度与实现分裂"这一事实；ADR 在 Zuno 的实际效力如何，是架构侧权限。**

**F15｜法院场景在代码里零支撑（`SIMULATED_RESUME_GAP`）**
A154：`src/backend/zuno` 里 `court|法院|judicial|审判|立案` **零命中**；真实对外动作是 SMTP / 物流 HTTP / Lark。简历"面向天津法院智慧平台相关场景"是**场景标签**，不是集成。他自己给出了改写方向（"面向法律文档场景、与智慧法院相关场景有关联"）。

**F16｜Pilot：零物证、零第三方标准、纯 milestone 自述（`SIMULATED_RESUME_GAP` + `EVIDENCE_GAP`）**
A169–A175：物证 = 一条汇总反馈"回答质量还需要提高"；用例与验收标准**零条**第三方输入；"Pilot Validation"是内部里程碑名；连"流程能跑通"这一点也没有独立证据。A175 自认整条链**是自证**。

**F17｜bullet 4/5 描述的文件已不存在，归属不可验证（`OWNERSHIP_GAP`）**
A126：`general_agent.py` 在 `ab1222da`（2026-08-04）被删。这两条 bullet 今天**既不可从代码验证、也不可从 blame 验证，只能靠 commit 存在 + 自述**。A159 的规则（commit 只证存在性、不证归属）使这个环**闭合不了**——他本人接受这个结论。

**F18｜"既有系统"这个前提本身没有独立历史（`OWNERSHIP_GAP`）**
A101/A158：git 首 commit `eafeb1c2` 与他的首笔改动同日（2026-04-15），而且是**同一条身份谱系**。所以"我重构了一个既有的转发层"里的"既有"，唯一凭证是那笔 diff 的 before 一侧；他连"`eafeb1c2` 不是我这条谱系的"都证明不了。3 月已存在这件事的唯一依据是 `docs/project/reference.md` 的一句话，**独立可核性 = 0**。

**F19｜没有跨模块接口是他定的（`OWNERSHIP_GAP`）**
A166：他接受"局部改动的实现者"这个定位。他给自己的唯一上调是"在检索 heuristic 那一层我是**判据的定者**"——比实现者多一点、比接口设计者少一点。这句我认，但"接口"的严格定义下是零。

**F20｜工程基础：通用层扎实，项目层空缺（`FUNDAMENTAL_GAP`）**
A195/A196/A198/A199：他工作过的文件里 `grep finally` = 0；项目内没有一条"我亲自写的 `finally` 清理"、没有一次"我亲自排查的取消/超时 bug"；没有 EXPLAIN；索引建议基于错误的 WHERE 形状（真实是 `user_id + agent_id + project_id + thread_id` 四列等值）。**他答的 `CancelledError` / GIL / READ COMMITTED 都对，但落不到"我写过并发清理"这个画像上。**

**F21｜"边界"字段的形态被面试验收标准塑造过（`EVIDENCE_GAP` + `NARRATIVE_GAP`）**
A183 自认：技术判断是真的，但"边界"字段的**形态**被他读过的 `interview-acceptance-standard.md`（"太像设计出来的项目"一节）塑造过；A80 里他甚至用那份标准当作"模块 09 该被质疑"的技术依据。
**这是对 Wave 1 最强真实性信号的一阶折价。** 我 Wave 1 的 §2.1 必须按此重读。

**F22｜反向证据：他推回我的框架，约 7–8 处，且都承重（`NO_ZUNO_CHANGE`）**
A111（adapter 同时是准入闸门）、A125（`graph_available` 是每轮重算，不是缓存位）、A144（那条测试防的是过渡残骸，不是我读成的"守护分裂"）、A145（单实例 PG 上原子写可行，所以是架构选择不是技术限制）、A150（审计断言**在活路径上**，是"没接线清单"的反例）、A163（`multi_agent_enabled` **有** reader，方向让多 Agent 残骸的故事更强）、A173（两个数并列，不是藏了一个）。
**这是"他在表演一套评测标准"这个读法的最强反证。** 我把这条记成对候选人**有利**的证据。

**F23｜一句话的行为观察（`NARRATIVE_GAP`）**
他 200 个回答里没有一次拒绝回答、没有一次空洞敷衍、没有一次编造数字。"我不给这个数"他说了至少六次。这在一个 100 题 × 2 波的批量对抗里是不常见的。**但 BATCH_DUEL 这个形态本身也在塑造他：Wave 1 的错误是在 Wave 2 被追问之后才消失的（A138）。**

---

## 6. 我仍然无法确认的部分

一个声称两轮之后什么都看透了的 Red 不值得信。以下是**我确定我不知道的**，且我拒绝用推断填平：

1. **任何一条 file:line 我都无法核实。** 我没有打开 Zuno 的仓库。因此"这段代码存在"、"这一行是什么"、"这个函数有没有 caller"，对我全部是**候选人的陈述**，不是事实。我这一整份评估的"实现层"结论，都是在**评价他说得可不可信**，不是在评价**他说得对不对**。
2. **我没有独立的方法区分"他在表演一套评测标准"和"他真的是这样的人"。** A183 提供了折价依据，F22 提供了反向依据，两者我都认。**净效果我判不出来** —— 只能给出"折价 + 保留"这个双面结论。
3. **"仓库里只有一个身份谱系"这条前提我核不了。** 这是承重的：它是他"归属不可切"整套防御的地基。如果实际能区分作者，他的大部分免责理由作废；如果确实不能，他说的就是结构事实。我无法判断。
4. **`rb019-graphrag-ablation-protocol.md` 的文件头我核不了。** F11 整条建立在他转述的 `source: red-blue rb-2026-09-15-formal-019 / IMP-019-05` 上。如果那行不是这样写的，F11 垮掉。
5. **`interview-acceptance-standard.md` 里"太像设计出来的项目"那一节我核不了。** F21 同理。
6. **A113 宣称的"baseline 自己也漂了、provenance 原文禁止制造百分比"我核不了。** 这是本轮最漂亮的一次解矛盾；如果那句原文存在，它是强证据；如果不存在，它是一次高水平的构造。**我在这两者之间没有判据。**
7. **A104/A106 的 `user_id=self.user_id` 我核不了。** 这是他自挖的最硬的一个洞，也是我"失败窗口意识强"这个结论的主要支点之一。
8. **A150/A189/A190 那三个"接线"反例我核不了。** 我依赖它们来避免把"这个系统全都没接线"讲成结论。如果它们不成立，F06–F09 那一组会显得更重。
9. **A48/A49/A76 的负向历史条目 #201–#207 的真实性质我分不清。** A156 说它们"是在 fault probe 里真的跑出来的"，也说"是被复盘整理进 Evidence 的条目"——这和 `rb019` 那份协议是**同一类问题**：我无法判断它们是工程事实，还是上一轮评测流程的产物。这个歧义压在"演进动因"整条叙事下面。
10. **我无法区分"模拟简历的候选人的编造"和"模拟设计本身的产物"。** 这份 `01_simulated_resume.md` 头部写着 `status: FROZEN` / `promoted_from: .../10_next_resume_candidate.md` —— 它本身就是从上一轮 Red/Blue 的产物提升来的。所以有些"gap"可能不是这个"人"的 gap，而是**这份模拟本身的结构**。我盲态下没有工具把这两者分开，我也不打算替它分。
11. **A129 的"简历冻结所以不能改"是真的约束还是方便的挡箭牌。** 在本轮规则里它是真的（文件确实标 FROZEN）。但"写这份简历的人"和"接受面试的人"是不是同一个立场，我判断不了。
12. **第 2 条 bullet 到底该"保留"还是"降级改写"，取决于一个我不拥有的口径**：读者是把"有 bad case + 有回归测试"当作够用的实绩，还是要求可复现的收益证据。我按前者给了"保留"，并附了两条硬上限；这个判断**可被推翻**，我把它标出来。

---

## 附录：本次实际打开的文件

按会话顺序，如实列出：

1. `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\01_simulated_resume.md`（全文，26 行）
2. `D:\projects\zuno\.agent\red-blue\attack-model.md`（全文，528 行）
3. `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\02_red_questions.md`（全文，332 行）
4. `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\04_red_wave2_review_and_questions.md`（全文，463 行）
5. `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\03_blue_answers.md`（分三次读完：1–500、500–999、1000–1424）
6. `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-07-formal-020\04_blue_wave2_answers.md`（分两次读完：1–580、580–1148）

**另有一次目录列举（需要如实披露）**：我对 workspace 目录跑过一次 `ls -la` + `wc -l`（用于确认六份输入的存在与体量）。该命令**回显了目录下所有文件的文件名、字节数与行数**，其中包括两份封存件的名字与大小（`03_blue_architecture_notes.md` 44196 字节 / 593 行；`04_blue_wave2_architecture_notes.md` 26721 字节 / 303 行）。**我没有打开、没有读取、没有检索这两份文件的任何内容**，也没有据此对任何结论做推断。列举中还出现了 `00_artifact_links.md` / `00_manifest.yaml` / `02_red_questions.part1.md` / `02_red_questions.part2.md` 四个文件名，同样未打开。

**未打开（明示）**：`03_blue_architecture_notes.md`、`04_blue_wave2_architecture_notes.md`、Zuno 的 canonical docs / `src/` / `tests/` / Evidence / `docs/governance/` / `docs/decisions/` / `docs/evidence/`，以及 `docs/red-blue/` 下的任何其他 round 目录。以上全部为盲态，未核实。

---

*Red Final Evaluation — rb-2026-10-07-formal-020 — blind*
