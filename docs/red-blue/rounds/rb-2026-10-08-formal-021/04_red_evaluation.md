# Red Final Evaluation — rb-2026-10-08-formal-021

```text
blind: true
seen: 01_simulated_resume.md, 02_red_questions.md, 03_blue_answers.md,
      04_red_wave2_review_and_questions.md, 04_blue_wave2_answers.md,
      .agent/red-blue/attack-model.md
not_seen: 03_blue_architecture_notes.md, 04_blue_wave2_architecture_notes.md,
          canonical docs (docs/architecture, docs/modules, docs/governance,
          docs/decisions, docs/evidence), src, tests, Evidence,
          00_manifest.yaml, 00_artifact_links.md, docs/red-blue/rounds/**,
          任何其他 docs/red-blue/ 文件
```

**泄漏自查（必填）。** 本次为完成本文件，我**没有**对 `docs/` 或仓库执行任何跨目录 `grep` / `find` / `glob`；全部输入来自上列 6 个允许文件，逐个用 Read 打开，未运行 Bash，未列目录。因此**没有**发生「搜索顺带带回封存文件路径/内容」的越界。

唯一需要如实声明的相邻情形：**允许文件自身的内容里出现了被封存文件的文件名**——`04_red_wave2_review_and_questions.md` 末尾的「本次实际打开的文件」表，以及 `03_blue_answers.md` 里的若干 `not_seen` 陈述，都**字面列出了** `03_blue_architecture_notes.md` / `04_blue_wave2_architecture_notes.md` / `04_red_evaluation.md` 等被封存文件的**名字**（无内容片段）。这来自被允许文件的正文，不是我的检索产物；我**未**据此去打开、引用或推断任何被封存文件的内容。除此之外无越界。

**方法声明。** 我是盲的。下面对 `文件:行`、commit SHA、run id、测试名、常数的一切判断，评价的是**引用结构是否自洽、跨答是否一致、两波之间是否漂移**，**不是**引用是否指向它声称的东西。我无法核实任何一条引用。按盲态判据，我区分 **NOT_ESTABLISHED（我不信他能证明）** 与 **FALSIFIED（已证伪）**：作为盲面试官我**只能**说前者；本文件中出现的「不成立 / 收回 / 矛盾」均指**候选人自述层面的不成立**（他两波的表述互斥、或他自认描述错误），**不是**我对真实历史的断言。我不写任何收益数字、run-to-run 百分比，也不写 Production / 规模 / QPS / Latency / Cost 的任何数值。

---

## 1. 总判断

**整轮判定：PARTIAL。**

不是 FAIL：本轮里**没有任何一条强 Claim** 是「只有形容词、落不到任何一档」的。简历第 1–5 条的每一个机制，都能被追到**代码 `file:line` + 一条 commit/fix 链 + 一个明确的失败窗口或显式 Unknown**；第 6 条（Pilot）则一致地停在 Unknown，且候选人两波都没有把它升格成 Production。攻方在 Wave 2 提出的每一处高价值缺口，都被候选用**更窄的表述**接手，而不是用更响的措辞盖过去。没有任何一处出现「一边削一边偷偷升级」。

不是 PASS：本轮**没有建立任何一条收益性 Claim**，而且「最可信的一段」与「他拥有的三段」在结构上是错位的（Part A §3 已指出，Wave 2 的 A152 / A116 / A135 把它坐实了）。简历里被描述为「复杂度」的四层（GraphRAG、Memory V2 / ContextOrchestrator、Native Runtime、MCP 准入），其保留理由统一退化为「有单测、有设计、协议未跑」——这正是 Attack Model §4「『已经实现』不能成为继续保留的理由」的反面样本。**复杂度正当性一层，我没有给到 PASS 的依据。**

分层结论：

| 层 | 结论 | 依据（只落到 Q/A 文本） |
|---|---|---|
| **Resume authenticity** | 可信（受限） | 两波之间义务边界不漂移；Wave 2 的修正绝大多数**朝收窄方向**（见 §2.2）；三条「简历已写明没有」的核查全部维持（§2.1 末） |
| **Ownership** | 仅建立到「受限提交切片」 | A1/A52/A54/A58/A157 的切片口径两波一致；A152/A116/A135 主动把最可信的模块划出个人范围 |
| **Implementation** | 机制级 PASS，产物级 PARTIAL | 每个机制可落到代码；但 ContextOrchestrator、phase08 saver、escalate、manual-assessment、delete-restore 等**命名组件不在任何 live path 上**，候选人自述 |
| **Complexity justification** | **未建立（FAIL-as-justified）** | GraphRAG：A68/A122/A86 举不出受益 query；Memory V2：A35/A137 无 A/B、无使用痕迹；Runtime：A43/A177 必要性 `not established`；准入：A111 约「一件半」在跑 |
| **Failure / Evidence** | 机制级成立、收益级不成立 | 唯一「已验证」的失败窗口簇（A44–A50 / A146–A151 / A194）位于**他不拥有**的 06/08 控制面；他拥有的模块里，失败语义多为「delegate 给 06 / Unknown」 |
| **Fundamentals** | 异步与 DB 语义强、IR 与评测弱 | A92/A93/A106/A107、A94/A195/A197、A6/A90/A190/A191 自洽且能纠错；A99/A187（ANN 未测）、A120/A121（打分手定）、A192（顺序检索）、A199（**仓内有 RRF 未用**）暴露 IR/评测基础薄弱 |

**对 Part A 的总回应：** Part A 的核心结论（「诚实、边界感强、但对复杂度是否值得几乎没有测量能力」）在两波之后**没有被推翻**，但有三处被 Wave 2 **实质性更新**：(1) Part A §4 的最高价值缺口（换模型混淆）被 A112/A113 **关掉一半**（排除换模型、并主动放弃单因归因）；(2) Part A §6 第 1 条（guardrail 硬替换 vs 不变量）被 A117/A118 承认为**真矛盾**并收窄；(3) Part A §6 第 2 条（salt 幂等）被 A106/A107 用**纠正攻方前提**的方式**证伪了攻方的假设**，同时交出一个更硬的新 handle。这三处都让**信任上升**，而不是下降。

---

## 2. Blue 1 → Blue 2：真解释还是话术补洞

### 2.1 逐条点名 Wave 1 缺口在 Wave 2 的处理

Part A 点名的高价值缺口，逐条在 Wave 2 的落点：

1. **简历「复杂请求进入 ReAct 路径」 vs A8「complex fail closed」**（Part A §7、Q101/Q102）→ **A101**：两句都成立但指两个时间点——简历写的是**4 月设计意图**，A8 说的是**今天**；产品装配下 `dynamic_dag_planner=None`，complex 在**准入处被挡掉**，走不到 ReAct。A101 并**主动修正 Wave 1 两处硬错**（`single_controller_runtime.py` 的真实路径；`:497-501` 是 `return None` 而非抛异常）。→ **处理方式：收窄 + 自纠。判定：真解释。**
2. **A8 vs A10 的内部矛盾**（Q102）→ **A102**：承认 A10 **选错了测试对象**——该测的是「准入把 complex 挡住」（确定性、无需模型），不是 ReAct 行为（需要假模型 fixture）。→ **真解释。**
3. **A97/A98 硬替换 vs A17 不变量**（Q117/Q118）→ **A117/A118**：**承认是真矛盾**，并给出一个语义自洽的代码细节——`_apply_genealogy_guardrail` 做 `selected[weakest_index]=candidate`，返回 `final_top5_floor_preserved=(promoted is None)`，**恰好**在晋升时 `floor_preserved=False`。→ **真解释（且是新读出来的实证）。**
4. **A12/A93 的 `{salt}` 幂等**（Q106/Q107）→ **A106/A107**：**纠正攻方前提**——salt 是**确定性的**（`salt=str(binding.name or resolved_tool_id)`，默认空串），攻方假设的「随机 salt 破坏幂等」**不成立**；真正的幂等边界在 key 的 `run_id`/`step_run_id` 分量上（同 step 撞 key 过度收敛；跨 run 重发不命中旧 receipt）。→ **处理方式：证伪攻方 + 交出新 handle。判定：真解释（且方向与「顺话」相反）。**
5. **A19/A84 vs A20/A85 的模型混淆**（Q112–Q114）→ **A112/A113/A114**：用 commit 元数据重建——profile 对齐提交是 audit 与 rerun 的**共同祖先**，两轮输入来自对齐之后的产物，故 audit→rerun **同模型**；A19 的「换过模型」指**更早**一次 smoke。A113 据此**排除换模型**，但同时**拒绝**把 local 的恢复归给 fusion（baseline 自身数字也在动 ⇒ 运行间方差，无 leave-one-out ⇒ 不可分离）。→ **真解释。**
6. **A21「未执行→跑不了」的口径移动**（Q116）→ **A116**：**收回**，明确是「**没做**」不是「做不了」；把 `BLOCKED_PENDING_DATA` 归属为一个**更晚的治理产物**（来源另一次 round、非他写、不描述他当时的处境）。→ **真解释（自我不利方向）。**
7. **A23 vs A73/A74 把机制拆成两个预算**（Q172/Q173）→ **A172/A173**：**同意**别名归一化是 seed expansion 的**输入预处理**，二者是**一根链的两个环节**，按两个预算会重复计算收益；收回「独立可删」的框架。→ **真解释。**
8. **A49 的 escalate 阈值无驱动**（Q147）→ **A147**：承认 `escalate_due_reconciliations` 在生产里**没有调用方**（只有测试调）。→ **真解释。**
9. **A48 的 `WAITING_RECONCILIATION` 只在 Target**（Q149）→ **A149**：修正为**工具层 BLOCK**（`status=gateway_status`、`SecurityDecision.BLOCK`），Run 级状态机**不存在**。→ **真解释。**
10. **A55/A71 vs A28 的读路径**（Q127/Q128）→ **A127/A128**：承认 A28 的**对象命名错**——`GeneralAgent.prepare_context` 不是 live 方法；真路径是 `core.py` 的 `build_context` → `build_context_pack`，`prepare_context` 只是**节点名**。A181 进一步给出**成因**（台账本身也用文档词）。→ **真解释。**
11. **A38 同题内 `ACTIVATED` vs `ACTIVE`**（Q138）→ **A138**：**收回** `ACTIVATED`；承认它只出现在文档、不在任一代码枚举；并指出**两个代码枚举互相不一致**（一个用 `REJECTED`、一个用 `VALIDATING`）。→ **真解释。**
12. **A78 接受了假前提（`KnowledgeGeneration` 不在简历里）**（Q179）→ **A179**：**认漏纠**，并明确正确做法应是先纠正前提。→ **真解释。**
13. **A99 ANN 未测**（Q187）→ **A187**：**维持**缺口；明确「ANN 抖动 != 只来自图」这一替代解释**未被排除**。→ **维持（未补洞，如实保留）。**
14. **A29/A70 `agent_id` 硬编码**（Q130）→ **A130**：**维持**；只说「agent 轴被塌成常量」，不报未审计的精确维数。→ **维持。**
15. **A35 无 A/B / kill test 归属**（Q135/Q136）→ **A135/A136**：**维持**；并**不认领** ADR 里 kill-test 的作者身份；把 PR 数字归为「PR 描述里记的，不是我重跑」。→ **维持 + 边界收紧。**
16. **Part A §3 结构错位（最可信的簇不归他）**（Q152）→ **A152**：**坐实**——九模块 authority 划分是**团队 ADR**（晚于他做 effect 的时间），他只做了「authorization 判定回到持久化 decision/epoch」这条**局部实现约束**。→ **维持且强化。**

**三处「简历已写明没有」的核查（Part A §7）在 Wave 2 的终态：** (1) ReAct 侧无回归断言——A10 维持，A102 进一步承认**连该测的准入 block 也没写成断言**（比 Wave 1 更不利，不是更好）；(2) holdout/ablation 未执行——A116 把「跑不了」收回为「**没做**」，A170 说明权重 0 的臂**从未跑过**；(3) 只到 Pilot——A59–A66 全维持，A162 自认该行**可验证信息量很薄**。**三处都没有被升格。**

### 2.2 修正的方向分布——判「查记录」还是「顺话」的关键

把 A101–A200 相对 A1–A100 的实质修正按**方向**归类：

- **朝收窄 / 自我不利（占绝大多数）**：A101（ReAct 是意图非现状）、A109（skill 读文件能力**随删除消失**、无等价承接）、A110/A111（「单 Agent Tool Calling」是 4 月形态；三件 delta 约「一件半」在跑）、A116（缺口→**收回**阻塞口径）、A123/A124/A125（目标域**零验证**、词汇按英文建、迁移是**假设**）、A126（拒绝给生产量级）、A129（ContextOrchestrator **该删**）、A137（structured memory **无任何使用痕迹**）、A142/A143/A144/A145（约束未落地 / 恢复顺序未实现 / 通用 Host **从未对照** / 必要性 case 是**构造示例**）、A147/A148/A149（无驱动 / 无 caller / 工具层停）、A160（该 run **不 certify** 4 月路径）、A166/A167（离 Pilot 的距离**无法定位**）、A174（**注参大部分塌成 commodity**）、A178（自曝 `==30` 是**自指、不保护任何东西**）、A180（**无原子切换**，只有引用侧校验）、A183（删除生命周期**生产走 0 步**）、A190（**无缓存**——隔离靠「不存在缓存」）、A195/A197（CAS 不防不可重复读漂移；SQL 下沉**不充分**）、A198（自曝 `fusion_score` 是 **trace-only、不决策**）、A200（**无** Owner 冲突实例）。
- **朝事实/归属纠错（中性偏收窄）**：A101(b)、A112（限定模型变更范围）、A114（补范围）、A127（对象错）、A138（文档词当代码枚举背）、A146（A46 **漏列**第一次 reauth 调用）、A151（fault seam 细节）、A181（命名漂移）、**A199（收回 A97「全仓没有 RRF」——RRF 在仓里存在）**。
- **朝辩护（极少，且仅一处真正「站住」）**：A106/A107（纠正攻方**假**前提：salt 确定）；A120（**同意** `_graph_signal` 等权相加是弱点，属收窄而非辩护）；A161（「作者字段区分不出」是**仓库书面口径**，非他自编——这是对「为免责而自编」这一指控的合理抗辩）；A191（显式参数优先，但同时自曝**无一处断言两者一致**）。

**结论：修正的方向分布压倒性地指向「查记录」，而不是「顺话」。** 判据有三：

1. **净方向是负的。** 如果他是在「演给评测器看」，最优策略是**保留** Part A 指出的换模型混淆（作为归因借口）**并**宣称 fusion 修好了回退；实际做法相反——A113 把两条**都**拿掉，只留「不可分离」。同理 A116 把自己唯一可用的**外部**借口（环境阻塞）**收回**成「这是我的缺口」。
2. **存在「证伪攻方」的实例。** A106/A107 是**纠正攻方的前提**，并给出一个**字面代码事实**（salt 取 binding 名、默认空串）来取消攻方假设；A199 是**收回自己此前的一句「全仓 grep 无命中」**。这两类动作只有「回去查了」才会产生，顺着话讲产生不了——顺话者不会说「你这个问题前提错了」，也不会主动撤回一条对自己有利的「仓里没有 RRF」。
3. **修正几乎都落在「机制级、可复核粒度」**（`fusion.py` 的返回变量名、key 模板分量、枚举差异、调用点行号），而不是落在「态度级」的泛泛认错。

**但有一个必须写进总判的限定（来自 Part A §7 的元警告，我予以维持）：** 这 100 答的**形态**高度模板化（每题「第二层」+ `事实层/证据/边界` 三段 + 封闭枚举取值），这套 metadata **不是临场能自带的**，是策略生成的。因此**「每处都削」这一形态本身不能作证**；它为 claim 提供的担保只有「口径被约束住」，不是「他主动坦白了」。本文件对 Blue 的加分，只来自**内容层的外部一致性**（跨答重复的机制细节、A106/A107 这类证伪攻方、A199 这类自撤回），**不来自**自我削弱的密度。

### 2.3 「先解释、后变糟」的地方

Wave 2 有几处**解释本身制造了更差的处境**（不是补洞，是补洞把洞挖大）：

- **A101/A102 之于简历第 1 条。** 「两句都对、分指两个时间点」这个解释，一旦成立，就把简历那句「复杂请求进入 ReAct 路径」从**现状描述**降级为**历史意图**；紧接着 A102 承认连「准入 block」这条**确定性、可测**的断言都没写，使「ReAct 侧暂无断言是 fixture 难题」这条 Wave 1 说辞**失去对象**（该测的那段根本不需要模型）。解释把一个措辞问题升级成**两个**问题（措辞失真 + 测试对象选错）。
- **A190 之于 A5/A89 的隔离论证。** Wave 1 的「不串」靠「`call_args` 是局部对象」；A190 为排除缓存风险，交代**根本不存在缓存**（每次调用当场查 DAO）。隔离结论反而更硬，但代价被带入：**每个 tool 调用一次 DB 读**。解释守住了正确性，却把「隔离」的成本显式化——这是一处净增信息、净减分数的解释。
- **A199 之于 A97/A98 的「自研融合」。** A97/A98 用「gate 与 RRF 数学不相容」为自制方案辩护；A199 回去查后**收回「仓内无 RRF」**，并指出**同一仓库的另一条路径已经在用 RRF**。于是「我们刻意不用 RRF」变成「知识检索这条路上选了自制、而 RRF 就在隔壁」。这是本轮**最典型的「先解释、后变糟」**：辩护动作直接暴露了「重新发明」的实证。
- **A128 之于简历第 4 条。** A127/A128 把集成点从 `GeneralAgent.prepare_context` 修回 `core.py` 的节点链。行为方向对，但**Wave 1 点名点错**这件事已被记录在案；第 4 条的「接入 Agent 调用前读取与回合后写入」在 Wave 1 里是靠一个**不存在的对象**支撑的。

### 2.4 一句话总结

**Wave 2 不是「话术补洞」，而是「回访记录后的收口」——它把 Wave 1 的每一处高价值缺口都朝更窄处收敛（含一次证伪攻方、一次自撤回），代价是同时把简历第 1 条的现状措辞、GraphRAG 的「不变量」表述、以及 ContextOrchestrator 作为集成点的地位一并否掉。**

---

## 3. 五维结论

### 3.1 Ownership

**已建立：受限提交切片 ownership。** 两波口径完全一致：Tool/MCP（`77346758` 单主题重构 + `0b5fb350` 的可安全提取子集）、GraphRAG fix chain（audit → fusion → seed → alias → path → rerun）、Context/Memory V2 链（typed contract → scoped foundation → 集成 → readback hardening，含独立 PR）。三段的措辞统一停在「这是我能自证的一笔」（A1/A52/A157/A161）。

**已明确划出个人范围（且 Wave 2 强化）：** 总体 Target Architecture、九模块、平台 DB schema（A54）、Tool Control Plane（A14/A75）、九模块 authority 划分所依据的 ADR（A152：**团队**、晚于他做 effect 的时间）、ADR 里的 memory kill-test（A135：**不认领**）、ablation 协议（A116/A170：**更晚的治理产物**）、PF 台账（A164：**没提交过我能指认的条目**）、连「作者字段区分不出」这句边界口径本身也**不认领作者**（A161）。

**未建立：** 任何强 Claim 到「我设计了这个机制」这一层。他对机制的贡献统一退到「我在现有代码里做了这一笔」（A53/A58/A157）。**结构性错位坐实：** 讲得最可复核的一簇（06/08 控制面）他不拥有（A152/A75/A14）；他拥有的三段，收益全部未证明。

**残余不清：** 个人切片与平台 schema 在 memory 路径上的交界。A130/A156 确认 DB 是「看过/调过数据、不拥有 schema」，A156 另列四条「参与过但材料不足」项（其中至少两条当时就是参与级而非 owner）。这条交界**两波都没有给出可复核的边界标准**（A157 只给了「有前后差异 + 有回归测试的路径」这一条提取标准，给不出比例，且明确「给百分比就是编数字」）。

**判定：Ownership 一致性 PASS；Ownership 强度 FAIL（这是设计使然，不是候选人失分）。**

### 3.2 Implementation

**机制级 PASS。** 每个被点名的机制都能落到 `file:line`，且 Wave 2 的**纠错**本身是「真的去读了」的证据（A101 路径/行号、A127 对象、A138 枚举、A146 漏列调用、A199 RRF）。

**产物级 PARTIAL，且有明确的「不在 live path」清单**（候选人自述）：`ContextOrchestrator`（A55/A158/A175：无生产调用点，诞生自 Target 设计、无具体 caller）、`phase08` 的官方 `PostgresSaver`（A141：未接线）、`escalate_due_reconciliations`（A147：无调用方）、`record_manual_effect_assessment`（A148：无 caller）、delete/restore 生命周期（A183：生产**零步**）、`KnowledgeGeneration` / ServingPointer（A78/A180：`src` 零命中）。

**Wave 2 新增的不利实现事实：** 多路检索是**顺序执行**、无 `gather`（A192）；`fusion_score` 是 **trace-only**（A198）；无缓存、每调用一次 DB 读（A190）；`KnowledgeReadinessEvidence` 的 `==30` 是**自指检查**（A178）。

**判定：实现真实存在，但「命名组件 ≠ 在跑的组件」这一落差是本轮最普遍的结构特征。**

### 3.3 Failure

**最好的一段失败语义在**他不拥有**的 06/08 控制面**：A44/A151（send 前撤销 epoch → executor 零调用）、A46（mandatory audit before effect）、A47（AUD-L1 verified / AUD-L2 not proven）、A48/A149（unknown effect → 工具层 BLOCK）、A194（身份同一 ≠ 写入与发送原子）——**这些都不计入他的个人层**（A152/A75）。

**他拥有的模块里的失败处理，多为「delegate 给 06 / Unknown」：** timeout 语义给 06 Target（A11/A92）；幂等只保证**同 step 内**（A107，跨 run 未审计）；stale memory 状态不刷新就**挡不住**（A33/A131）；无 TOCTOU 护栏（A96）；两条冲突 memory **不仲裁**、各自独立 APPROVED（A34/A133）；无 A/B（A35）。

**Wave 2 自产的最硬失败发现：** 跨 run 重发因 key 含 `run_id` 而不命中旧 receipt（A107）；guardrail **故意**破坏 baseline 下限（A117/A118）。

**Authority 归属**：候选人把「谁拥有最终判断」**一致地划给自己以外**（02 Domain / 08 Security / 06 Effect），且不把 Target 说成已实现（A31/A41/A45/A100/A143）。**判定：失败语义的 authority 划分讲得清楚，但在他自己的链路上覆盖稀薄。**

### 3.4 Evidence

**每个强 Claim 的证据是「代码 + commit 链 + PF 台账」，无一例外；但证据粒度停在机制级。** 最强的一条证据 artifact 是 audit（逐题 top5 位移、点名被挤出的实体），Wave 2 把它**限定**为「机制级归因可追溯」而非「幅度可归因」（A187）。

**数字：仍无一个可追溯来源**（Part A 已计九个零来源；Wave 2 不增来源，反而**收回**若干——A113 拒绝对归因、A126 拒绝给生产量级、A116 收回阻塞口径、A199 收回 grep 结论）。这四处都是**主动放弃**而非补证。

**Wave 2 的证据来源自限**：A160 明确该 selected main run **不 certify 4 月路径**；A136 明确 PR 数字**不是他重跑**；A178 明确 `==30` 是自指、**不构成保护**。

**判定：Evidence Sufficiency——机制级 yes；收益级 no；且候选人主动拒绝了一切收益叙述。**

### 3.5 Fundamentals

**强（自洽且能纠错）：**
- timeout / idempotency（A11/A12/A92/A93/A106/A107）：能区分「本地未拿到响应」与「远端是否执行」，能**纠正攻方的假前提**并把风险**重新定位**到 key 的其他分量。
- DB 并发（A94/A195/A197）：正确区分「同一行的 lost update（CAS/FOR UPDATE 可防）」与「基于别处读到的快照做决定的并发漂移（READ COMMITTED 防不住）」，并指出 SQL 谓词下沉**不充分**、需「条件写 / 同行锁定 / 同事务判定」。
- 并发身份（A6/A90/A190/A191）：正确把 ContextVar 定位为 **tracing 通道**、坚持显式参数承担有后果的动作，并自曝**无一处断言两者一致**。
- cancel 语义（A91/A193）：正确区分「本地 cancel 意图」与「远端终止」，并承认 CXL-B（cancel 编排）**未实现**。
- 事务反模式（A95/A196）：识别「拿 DB 锁等模型返回」，并指出**没有静态检查**能拦住它。

**弱（且恰好是决定 GraphRAG 收益的那两块）：**
- ANN vs 精确 KNN：无 recall 对照、无不同 K 的召回曲线（A99/A187）——这直接使「被挤出 top5 = 图位移」的**替代解释（ANN 抖动 + 小样本）未被排除**。
- IR 融合：自研「分组 + 层级 + 基线下限」，**未对照 RRF**（A97/A98）；A199 进一步暴露**仓内已有 RRF 未用在知识检索路上**——这是「重新发明轮子」的实证，不是知识空白。
- 打分可信度：`_graph_signal` 四个语义不同的计数器**等权相加**（A120）；`_score_path` 六元权重**手定、跑数据集前无任何人工对齐**（A121）。

**判定：Fundamentals 在「异步 / DB 语义」轴向上明显强于「IR / 评测」轴向；而弱的那一块，正是他不做消融就保住 GraphRAG 的原因。**

---

## 4. Resume Claim 处置

逐条对 `01_simulated_resume.md` 给出最终处置。

### 第 1 条 — 重构单 Agent Tool Calling 与 Workspace 路由

- **可保留的部分**：direct route 的准入与工具参数抽取边界（含自定义 MCP 名称递归修复）、「ReAct 一侧暂无回归断言」的自述。
- **需改 / 需删的部分**：「**复杂请求进入 ReAct 路径**」这一子句。
- **对「复杂请求进入 ReAct 路径」这一 claim 的点名判定：NOT_ESTABLISHED as current state — 应改写或删除。** 依据（只落到 Q/A 文本）：A8/A56 说分流判据是**规则**、`complex` 需要注入的 DAG planner、而产品装配里是 `None`，故复杂请求**在准入层 fail closed**；A101 明说「『进入 ReAct 路径』作为今天的现状**不准确**」，只承认为 4 月的**设计意图**；A110/A111 进一步说今天 Runtime 是「Single Controller + 受管工具绑定」、不再是自由 ReAct 遍历，4 月那三件 delta 约「一件半」在跑。作为盲面试官我不主张「真实历史不是这样」——我只主张：**按候选人自己的 Wave 2 回答，这句话不能作为现状描述成立**。若保留，必须挂时间范围（「4 月版本的设计意图」）并去掉「进入 ReAct 路径」这一可达性暗示。
- **附带**：A102 承认「**该测的准入 block 从未写成断言**」，使 Wave 1 对 ReAct 断言缺口的解释（fixture 成本）失去主要对象。
- **处置：需改（子句级）＋ 保留（direct route 与测试部分）。**

### 第 2 条 — 定位并修复 GraphRAG 排序回退

- **可保留**：ranking **displacement** 的失败形态、被挤出实体与逐题记录、baseline-preserving 融合的**机制**（排序键以 `baseline_rank = min(vector_rank, bm25_rank)` 为主）。
- **需改**：「baseline-preserving」**不能作为全局不变量**讲。A117/A118/A169 承认 comparison/bridge/genealogy 三类 query 上有 guardrail **故意**硬替换、返回「floor preserved = False」，最终输出**可以**劣于 baseline。原文「保留 Vector/BM25 原始 rank」在**排序阶段**成立，读者会误读为**输出**保证，须补例外。
- **需改（措辞）**：「同日 rerun 在该 5-query 样本上不再低于 baseline」字面成立，但 (i) 是**非劣**而非收益；(ii) A113 已明确 baseline 自身数字也在动，**fusion vs 运行方差不可分离**。建议写成「在该小样本 rerun 上不再低于 baseline（未做消融，不可归因到单一机制）」。
- **处置：可保留但需改（补 guardrail 例外 + 归因免责）。**

### 第 3 条 — 继续完善多跳图检索

- **可保留**：三个机制存在且有单测（行为级）。
- **需改（结构）**：A172/A173 认定**别名归一化是 seed expansion 的输入预处理**，二者是**一根链的两个环节**，不应作为两个独立机制并列陈述；把它们拆成「三个机制」会**系统性高估各自边际收益**。
- **需改（证据）**：A86 明确单测「只证明 behavior、不证明对指标的边际贡献」；holdout / leave-one-out **未执行**，且 A116 把它从「跑不了」**收回为「没做」**。
- **需改（域适配）**：A123/A124/A125 明确整套关系词表按**英文**建、目标域（中文法律）**零验证**、迁移是**假设**；A24/A168 指明别名归一化在中文法律主体上有**已知误合并风险**且 fuzzy 分支实际退化为 no-op。
- **处置：需改（合并机制叙述 + 明确收益未测 + 域未验证）；不建议删（有行为级单测支撑其存在）。**

### 第 4 条 — 构建 scoped Context / Memory V2

- **可保留**：typed contracts 与 scope 语义的存在；调用前读取、回合后写入的**行为**（在节点层真实存在）。
- **需删 / 需改**：**不要用 `ContextOrchestrator` 作为集成点。** A55/A158/A175 明确它**无生产调用点**、诞生自 Target 设计而非某个具体 caller，A129 甚至给出「重做会删掉它」。A127/A128 承认 Wave 1 点名的 `GeneralAgent.prepare_context` **对象命名错**，真路径是 `core.py` 的 `build_context` / `post_turn_commit` 节点。
- **需改（口径）**：A29/A70/A130 明确 `agent_id` 在 runtime 侧**硬编码**为常量，声称的四维 scope 实际生效维度更少。
- **处置：需改（改集成点命名、去掉把 ContextOrchestrator 当运行时入口的暗示）。**

### 第 5 条 — 收紧 Memory readback

- **可保留**：`_memory_exclusion_reason` 的排除逻辑、仅 APPROVED 的过滤、source trace 与 review/provenance 约束、focused tests 的**行为级**覆盖。
- **需改（证据粒度）**：A136 明确 PR 记的 focused/repo/legacy 数字**不是他重跑**、只证明行为类别；A35 明确**无 A/B**；A137 明确 structured memory **无任何人工使用痕迹**。
- **需改（authority 口径）**：A31/A100/A134 明确 recall eligibility **属 08 但未接上**，今天生效的是 scope + APPROVED 过滤；「审核通过」是**一列**（A96）、**无 TOCTOU 护栏**、无后台刷新（A33/A131）。凡涉及「谁能召回」的表述须标 Target。
- **处置：可保留但需改（把收益/authority 口径限定到行为级与 Current）。**

### 第 6 条 — 项目简介（内部 Demo / 法院侧测试 / Pilot Validation）

- A59–A66 全 Unknown；A162 自认该行**只提供阶段信息、不提供结果信息**；A62 把边界定性为**取证边界**而非人为决策；A163 拆出「措辞是我选的、边界是事实层的」。
- **处置：需改（近零信息行）。** 不必然删除（阶段本身是弱信号），但**不含任何可验证结果**；两波都未把它升格为 Production 或「法院在用」，这一点**干净**。

---

## 5. Findings

- **F1（现状措辞失真 · 高）** 简历第 1 条「复杂请求进入 ReAct 路径」与候选人自己的现状描述（complex 在准入层 fail closed，planner 未装配）互斥；A101 已自认「作为今天的现状不准确」。**处置：改/删子句。**
- **F2（自造不变量被自己推翻 · 高）** 「baseline-preserving」作为**全局**不变量不成立：guardrail 在三类 query 上**故意**覆盖 baseline 下限（A117/A118/A169）。**这是本轮最干净的一条「两答互斥 → Wave 2 收窄」的闭合。**
- **F3（攻方假设被证伪 · 高，方向对候选人有利）** `{salt}` 非随机（A106）；攻方的幂等失效假设不成立。候选人**主动**交出新 handle（key 含 `run_id`，跨 run 不命中旧 receipt）。**该题不是补洞，是反击。**
- **F4（最高价值归因缺口被关掉一半 · 高）** audit 与 rerun **同模型**（A112，commit 图重建）；「换模型」被排除；但 local 恢复**不可归因**到 fusion（A113，baseline 自身波动 + 无消融）。**结论：排除一条、拒绝一条，两条都不利于自己。**
- **F5（口径从「阻塞」收回为「未做」 · 高）** A116 把自己唯一的外部借口收回，并划清协议是**更晚的治理产物**、非他写。
- **F6（结构错位坐实 · 高）** 最可复核的一簇（06/08 控制面）**不归他**（A152：团队 ADR、时间晚于他做 effect）；他拥有的三段收益全未证明。
- **F7（大面积「命名组件不在 live path」· 高）** ContextOrchestrator、phase08 saver、escalate、manual-assessment、delete/restore 均**无生产调用方**（A55/A141/A147/A148/A183）；`KnowledgeGeneration`、`ServingPointer` 在 `src` 零命中（A78/A180）。
- **F8（机制被过度拆分 · 中高）** 别名归一化与 seed expansion 是**一根链**（A172/A173）；拆成两个机制会重复计收益，且与 A74「留 seed 删 alias」的取舍自相矛盾。
- **F9（IR 基础薄弱且落在关键路径 · 中高）** ANN recall 从未测（A99/A187）；打分等权相加 / 手定无对齐（A120/A121）；多路检索**顺序执行**（A192）；**仓内已有 RRF 但未用在知识检索路**（A199，且撤回 A97 的「全仓无 RRF」）。
- **F10（测试对象选错 · 中）** A102 承认该测的确定性准入 block 未写成断言，Wave 1 的 fixture 说辞失去对象。
- **F11（收益级证据为零，且候选人主动拒给 · 中）** GraphRAG 唯一已记录收益是「非劣」（A122），而「图权重 0」这一平凡配置也能拿到；Memory V2 无 A/B、无使用痕迹（A35/A137）；Runtime 必要性 `not established`（A43/A177）；4 月准入存活约「一件半」（A111）。
- **F12（形态可策略生成，不能作证 · 元）** 每题「第二层」+ `事实层/证据/边界` 的模板是策略产物。**本轮对 Blue 的加分只来自内容层外部一致性，不来自自削密度。**
- **F13（时间线空窗 · 中）** A51/A153/A154：公开根提交与他第一笔可自证改动**同日**，3 月至该日之间**无任何可复核 artifact**；OpenViking 等只剩「参与」回忆（PF-011 artifact 未恢复）。**NOT_ESTABLISHED，不判 FALSIFIED。**
- **F14（决策治理缺口 · 中）** 影响所有请求分流的准入规则**无 ADR、owner 为 Unknown**（A56/A159）；`plan_kind` 关键词表是**固定清单**、新接 server 会静默落到空（A104/A105）。
- **F15（并发/一致性护栏稀疏 · 中）** memory 模块仅一处 `FOR UPDATE`、UoW 无显式隔离级别（A94/A195）；无 TOCTOU 护栏（A96/A197）；无后台 reaper（A33/A131）；无静态检查拦「事务内等模型」（A196）。

---

## 6. 我仍然无法确认的部分

作为盲面试官，以下我**无法**在两波材料内部解决，且**不会**用任何封存笔记或 canonical 源去补：

1. **所有引用本身。** commit SHA、`file:line`、run id、测试名、常数——我全部只做了**结构判断**（自洽性、跨答一致性、两波漂移）。它们的真假我无从核实。
2. **A106「salt 确定性」是否正确。** 这是本轮**方向最关键**的一次证伪攻方；若 `simple_agent.py:215-218` 的 `salt` 取值另有随机来源，则 A106/A107 的性质会从「反击」变成「辩护」。我无法核实。
3. **A112 的模型重建是否正确。** 它依赖 commit 图的祖先关系与产物出处；我无法核实 profile 对齐提交、两轮输入产物、以及「audit 与 rerun 同模型」。
4. **A117 的 `final_top5_floor_preserved` 是否真存在且语义如述。** 若该返回表达式不存在，「真矛盾」的判定虽由**两波口径互斥**支撑（不依赖代码），但矛盾会在**代码层**失去落点。
5. **A199 的 RRF「已在仓内」是否成立。** 它使「重新发明」成为实证；反之则退回 A97 的原判。
6. **个人切片与团队切片的真实交界**（尤其在 memory 路径上）。两波都未给出可复核的边界标准。
7. **「第二层」细节是「照记录复述」还是「按模板生成」**——形态上它更可能是后者（F12），但个别题（A106/A107/A112/A117/A199）呈现出只有「回去查了」才产生的**纠错形状**。我**不能**在前二者之间给出最终裁定，也不会把模板形态当成诚实或不诚实的证据。
8. **Pilot / 法院的一切**（A59–A66）：我无法在前述「全 Unknown」之外获得任何可判断的信息。

---

## 附录：本次实际打开的文件

| # | 文件 | 状态 |
|---|---|---|
| 1 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\01_simulated_resume.md` | 允许（冻结简历） |
| 2 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\02_red_questions.md` | 允许（Red Wave 1 的 100 题） |
| 3 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\03_blue_answers.md` | 允许（Blue Wave 1，A1–A100；分段读满 1423 行） |
| 4 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\04_red_wave2_review_and_questions.md` | 允许（Red Wave 2：Part A 盲评 + Q101–Q200） |
| 5 | `D:\projects\zuno\docs\red-blue\workspace\rb-2026-10-08-formal-021\04_blue_wave2_answers.md` | 允许（Blue Wave 2，A101–A200；分段读满 1263 行） |
| 6 | `D:\projects\zuno\.agent\red-blue\attack-model.md` | 允许（Red Skill，完整读） |

**越界打开：无。**
**跨目录 `grep` / `find` / `glob`：未执行（本文件全程未调用 Bash）。**
**唯一需声明的相邻情形：** 上表第 4 份（允许文件）的正文里字面列示了被封存文件的**文件名**（`03_blue_architecture_notes.md` 等），无内容片段；未据此打开或引用任何被封存文件。详见文件头「泄漏自查」。

**自我申报的诚实边界：** 本报告对 `文件:行`、commit SHA、run id、测试名、常数的全部判断都是**结构判断**，不是核实。我未打开任何源码、封存笔记或 Evidence，因此无法确认 A1–A200 中任何一条引用是否指向它声称的东西；亦不能据此宣布任何一条 Claim 在真实历史中为假——本文件中的「不成立 / 收回 / 矛盾」一律指**候选人自述层面**的成立状态。
