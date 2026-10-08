# Workflow Retrospective — rb-2026-10-08-formal-021

```text
round: rb-2026-10-08-formal-021
author: Controller（本轮工作流产物作者本人）
scope: 只审 workflow，不审系统架构（系统判决见 05_blue_architecture_reflection.md）
base_sha: cdd2063b341e6919fafaa1395d1f3bdc837329f6
head_observed: 297257da
audit_targets: Resume Builder / Red Thinking Framework / Blue Candidate Framework /
               Blue Architecture Framework / Harness
branch_commits:
  d8f8d7a8 ROUND_INIT
  eb8163fb record round PR number (282)
  bcd00a61 freeze simulated resume after independent fact-check (Resume Gate, delegated)
  97bdd0db red wave 1 — 100 blind questions
  28e4661e blue wave 1 — 100 answers + sealed architecture notes
  718c8524 red wave 2 — blind evaluation + 100 follow-ups
  957e8114 blue wave 2 answers — A101–A200 complete
  60cd92c9 record wave-2 controller verifications; fix manifest YAML
  b95e00fc blue wave 2 sealed architecture re-diagnosis
  c18be857 checkpoint blue wave 2 — sealed notes registered
  4fce22a7 mark sealed wave-2 notes complete in artifact links
  e7bd469b correct the record on Blue's A8/A56 citation defect
  144ba412 red final evaluation
  297257da checkpoint red evaluation — advance to blue reflection
```

**本文的立场**：这份复盘由 Controller（也就是本轮 Resume Gate、状态总线与产物收口的执行者）写自己。
凡涉及 Controller 自身失误的条目，**不写成「流程问题」而写成「我的问题」**。

---

## 1. Resume Builder Reflection

### 1.1 本轮最重要的一条：Controller 自己在 Resume Gate 改错了一个方向

`01_simulated_resume.md` 第 1 条现写「**复杂请求进入 ReAct 路径**」。**这句是错的**，而且是本 Controller
在 Resume Gate 上亲手改出来的。

- **来源**：round 020 的 `10_next_resume_candidate.md` 原文写的是「复杂或**参数不完整**任务回落 ReAct」。
  我在冻结前逐条取证，判定「参数不完整」`NOT_SUPPORTED`（参数不全的工具体走产品侧
  `_plan_tool_creation_flow` 的 `mode="ask"` 补参流程，不是回落 ReAct），于是删掉「参数不完整」，
  改成了「复杂请求进入 ReAct 路径」。
- **错在哪**：我的核验只证到 `_plan_kind_for` 会返回 `simple` / `complex` 这个**分类**存在，
  **没有继续查这个分类在产品装配下被谁消费**。核验停在了「机制存在」，没走到「机制被这样使用」。
- **实际是什么**：`main.py:113` 产品装配处 `dynamic_dag_planner=None`；`single_controller_runtime.py:737-739`
  `complex_unbound` 命中后 `:814-818` 置 `DYNAMIC_PLAN_RUNTIME_NOT_BOUND`，`:825` 走 `_blocked_request`。
  在该组合下复杂请求是在**准入处 fail closed 被拦下**，**不进入 ReAct**。
- **谁发现的**：不是外部。Blue Wave 1 的 **A56** 自己答出了「complex 需要一个注入的 DAG planner」，
  Controller 把它追到代码才确认。**这是一次自我发现**。
- **处置**：**不回写 frozen resume**（verdict immutable）。该条进入 `09_improvement_ledger.md`，
  并必须在 `10_next_resume_candidate.md` 改成可复核措辞。

### 1.2 因此暴露的核验清单缺陷（Resume Builder 的方法问题）

原核验清单能回答「这条 claim 有没有 commit / 测试 / 台账支撑」，**不能**回答：

```text
这个机制在产品装配（shipped composition）下真的被这样使用吗？
```

本轮 4 处措辞修正里，有 3 处是「措辞强度」问题（方向没错），只有这 1 处是**方向错**——
而它恰好是核验清单唯一没覆盖的那一类。⇒ Resume Gate 的核验清单必须新增一项
「**装配侧确认**」：任何关于运行行为的 claim，必须追到组装点（`main.py` / composition），
不能停在类定义或单元测试。

### 1.3 独立取证核验的产出（有效部分）

Resume 冻结前由一个隔离 subagent 在 base `cdd2063b` 上对 5 条 bullet 与 3 条边界主张逐条回溯。
结论：**5 条 bullet 全部有支撑，但 3 处措辞证不到**，当场改掉 4 处（明细见 `00_artifact_links.md`）。
其中**一处是 round 020 的 candidate 自身携带的 `NOT_SUPPORTED`**（「参数不完整回落 ReAct」）——
说明上一轮的 Resume Candidate 并未自带核验，本轮 Gate 起到了它该起的作用。

另有两处「反向收窄」值得记：原文「上述改动在 5-query smoke 上验证」**说得比事实窄**
（每个机制另有单元测试）；`ContextOrchestrator` 被从「轻量运行时装配器」降为 **typed contract 层**
（`prepare` 在 `src/` 内无生产调用点）。

### 1.4 `IMP-020-09` 的处置

本轮 frozen resume 直接采用 round 020 的 candidate 正文，逐字未改，五条处置：
**保留 1 条**（第 2 条，附两条硬上限：不得声称「效果提升」、不得制造 run-to-run 百分比）、
**降级改写 4 条**（第 1/3/4/5 条，漂的是动词强度不是事实）、**删除 0 条**。
处置记录**不进入** `01_simulated_resume.md` —— 告诉 Red「这些 bullet 是刻意弱化过的」等于发路标。

---

## 2. Red Thinking Framework Reflection

### 2.1 判得准的部分

Red Wave 1 自报的三个最高风险 handle 里，**第一个就命中了本轮的实质**：
「GraphRAG『同日 rerun 不再低于 baseline』被判为最高真实性风险（样本 5 条、metric 未写明）」。
这条在 Wave 2 被 Q113 追成「审计与 rerun 是否同模型」的归因攻击，是本轮最有价值的一问。
⇒ Attack Model 的「Evidence Escalation」动作在本轮是有效的。

### 2.2 结构性问题：三个 Top follow-up 里两个建立在**假前提**上

Red Wave 2 的三个 Top follow-up（Q113 / Q117 / Q107）在 Wave 2 的终判是：

| 问 | 前提 | 终判 |
| --- | --- | --- |
| Q113 | audit 用 `qwen-plus`、rerun 用 `deepseek-v4-flash`，故「修复有效」被换模型污染 | **前提被证伪**：`a25c95a2`（2026-06-20）把 profile 的 `conversation_model` 改为 `deepseek-v4-flash`，且它是 audit `7928df50` 与 rerun `3da5d742` 的**共同祖先** ⇒ 两者同模型 |
| Q107 | `salt` 是随机的，retry 时 key 变化导致幂等失效 | **前提被证伪**：`mcp_tool_executor_adapter.py:70-73` 的 `salt: str = ""` 默认空串，key 是 `{run_id}:{step_run_id}:{tool_name}:{salt}` |
| Q117 | guardrail 硬替换 top 与 baseline-preserving 不变量互斥 | **命中**：A117/A118 承认为真矛盾（`fusion.py:922` 故意覆盖下限） |

**这是 Attack Model 的一个真实特征，不是缺陷**：它从 resume 的措辞反推一个「应该会出问题」的机制，再打。
前提是从文本**推**出来的，所以天然会有打空的时候。

**但框架必须能区分两件事**，本轮的终判已经做到了、框架文本却没有写：

```text
claim 被证伪  ≠  premise 被证伪
```

「攻击的前提不成立」**不能**当作「候选人弱」的证据，**也不能**当作「候选人强」的证据——
它只说明攻方对系统的建模有一次失准。本轮 Red Final 处理得对（F3 明写「该题不是补洞，是反击」），
但这是**执行者的自觉**，不是框架的规则。⇒ 建议写进 Attack Model。

### 2.3 模板合规

Red Wave 2 由 subagent 生成，把 `Part A` / `Part B` 写成了 h1（round 020 是 h2）。
Controller 机械规范为 h2，**未改任何文字**，并在 commit message 与 manifest 里记录。
⇒ 这是**模板合规**问题（Harness 侧），不是内容问题。

### 2.4 Red Final 的自限边界（诚实，但要记）

Red Final（`04_red_evaluation.md:262`）自述：

> 本报告对 `文件:行`、commit SHA、run id、测试名、常数的全部判断都是**结构判断**，不是核实。……

这意味着 **Red Final 的「实现层」结论不能当事实用**。它判得对的地方（如 F2 guardrail、F7 命名组件无调用方、
F9 仓内 RRF 未用、F14 准入无 ADR）都是**与结构一致的推断**，恰好被 Blue 的复诊独立确认；
但它同样会**判错**——见 `05_blue_architecture_reflection.md §9.3`（Reflection 独立回源码核出的清单）。
⇒ 流程含义：Red Final 之后**必须**有一道回源码的核对，本轮由 Blue Reflection 承担；这一步不能省。

---

## 3. Blue Thinking Framework Reflection

### 3.1 候选人回答框架

**表现好的地方（有实证，不是印象）**

- **Wave 2 的 18 处撤回 / 修正**是**实质的**。Controller 抽验了其中 5 处（A183、A190、A169/A68、A172、A107），
  **全部成立**；其中 A168「`resolve_alias` 的 `allow_fuzzy` 分支是死代码」是一个真的死分支
  （该循环只做 `normalized_candidate == normalized_known`，而该相等已在上面返回）。
- **主动拒绝归因**：A113 排除「换模型」后**拒绝**把 local 恢复归因给 fusion 修复（baseline 自身数字同日漂移，
  `MRR@10` 0.90→1.00）。这与本轮边界声明一致，是**减法**，不是加法。

**框架风险：形式可能盖过内容**

Red Wave 2 的盲评（Part A）明确提出：「每题『第二层』+ `事实层/证据/边界` 的模板
**可能是策略化模板而非临场自削**」，因此**不为强 claim 加分**。Red Final 的 F12 重复了这一点。

⇒ 框架含义：**三段式格式本身不构成证据**。加分只能来自**内容层的对外一致性**
（与其他答案、与 resume、与失败窗口自洽）。若框架文本里有任何「自削密度高 = 诚实」的隐含奖励，应当删掉。

**框架的真问题：自我修正本身也会错**

Blue-2a 在 `04_blue_wave2_answers.md:21` 自述「A8/A56 把 `single_controller_runtime.py`
写成在 `agent/runtime/execution/` 下——错」。Controller 逐行核对：

- A8（`03_blue_answers.md:121`/`:125`）与 A56（`:798`）**根本没写目录**，只写 `single_controller_runtime.py:497-501`。
- `agent/runtime/execution/` 在该文件里只出现在 `:122`，指的是**另一个文件** `react_runner.py`。

⇒ **Blue 误述了自己 Wave 1 的错误**。真正成立的错是**动作错**：`:497-501` 是 `build_workspace_plan_steps`
的 `return None`（全文件无 `raise DYNAMIC_PLAN_RUNTIME_NOT_BOUND`），Wave 1 说它「抛」。

框架含义：**自我修正不能当已核实的事实采信**。一条「我错了」和一条「我这样改」都需要回源码核。
本轮这条「关于错误的错误」差点被我当成 Arch §14 的转述写进记录 —— 见 §4.4。

### 3.2 架构诊断框架

**（定稿：依 `05_blue_architecture_reflection.md` 的最终结果补全）**

**结论：这是本轮五个审查对象里表现最好的一个。**

- **差分复诊是有效的，且真的会回退。** Wave 2 复诊把 Wave 1 自己的 `F-06`（conditional
  `ARCHITECTURE_GAP`）主动**降级**为 EVIDENCE / GOVERNANCE，条件性 `ARCHITECTURE_GAP` 集合清零；
  `F-04` 的 salt 契约被撤回（salt 的随机性后来被源码排除：`simple_agent.py:216-218`
  以 `salt=str(getattr(binding,"name","") or resolved_tool_id)` 传入，由动作身份决定）。
  一个只会加固自己结论的诊断框架不会做这件事。
- **§13 高门槛守住了。** 两波下来最终只剩 **1 条** `ARCHITECTURE_GAP`（`F-01`，Owner + Contract），
  且由 Reflection 逐行独立复现全链；`F-11` / `F-14` / `F-15` 明确**不升级**。
  `F-01` 的契约锚点经 Controller 复核成立：`docs/modules/reference.md:237`
  「Native Runtime entrant 一定有 Plan：简单单步，复杂 Dynamic DAG」——
  而被拦下的复杂请求产出的正是一个**无 Plan 的 entrant**。
- **复诊不只是确认，还新增了。** 产出 `N-01`..`N-05`（孤儿组件模式 / Target 词漂移 /
  仓内 RRF 未用于知识路径 / 冻结协议消融单位缺陷 / delta 塌缩后收敛到「准入」）。
- **它没有拿反思去争取更多架构。** `Multi-Agent` 的结论是**不值得（今天）**：当前失败是「准入无 owner」，
  不是「单 Agent 做不动」，且零 measured constraint；正解是先补归属（`F-01`）与先跑测量（M6/M7/M8），
  不是升层。这是**减法方向**的判决，不是扩张方向。

**交叉验证（本节最值得记的一项）**：Reflection 的 §9.3 独立回源码核了 Red Final，核出
**2 处过强表述**（`RF-01` 把 `prepare_context` 说成「不存在的对象」——它作为符号确实存在，
`agent/harness.py:9`/`:269`；`RF-02` 说 A8/A56「两处硬错」——实际只有**动作**一处错，
「目录」只是欠指定），并闭合了 Red Final 主动保留的 2 个未知（salt 确定性、
`final_top5_floor_preserved` 存在性），**两处都指向 Blue 正确**。

其中 `RF-02` 与 **Controller 在 `00_artifact_links.md` 的独立结论一致**（见 §3.1）——
即两个互不可见的执行者从同一源码得出同一判定。Reflection 自己也指出：
Red Final 的偏差集中在「把归属错误说成存在错误」「接受候选人不准的自述」这两类**过度精确**上，
**几乎没有凭空错误**。这既是对 Red Thinking Framework 的正面评价，也说明
「盲评之后必须有回源码核对」（§2.4、§4.3）不是形式主义。


---

## 4. Harness Reflection

### 4.1 隔离的真实边界（每轮都要说，因为每轮都在变）

subagent 的**上下文隔离是物理的**（独立 context、无共享记忆）；**文件系统是共享的**。
允许读哪些文件靠**指令约束 + 事后自报审计**，**不是沙箱**。
本轮所有隔离声明都是**自我申报**，无一是沙箱验证。

### 4.2 本轮观测到的泄漏向量（三次，全部自报）

1. **Wave 1 Arch 实例**：为定位 `ContextOrchestrator` / direct-route / ReAct 在 canonical 文档中的落点，
   对 `docs/` 做了一次跨目录 grep，输出顺带带回 `docs/red-blue/rounds/**` 与本轮 workspace 内其他文件的片段。
   声明未用作 finding 证据。
2. **Wave 2 Arch 实例**：同源操作（定位 `KnowledgeGeneration` / `ServingPointer`），输出带回
   **两个归档轮次 transcript 的路径名**（未打开、未读内容）及本轮 `00_manifest.yaml` 路径名。
3. **（新形态）允许文件正文里字面列出封存件的文件名**：`04_red_wave2_review_and_questions.md` 的附录
   与 `03_blue_answers.md` 的 `not_seen` 陈述里，**字面**写了 `03_blue_architecture_notes.md` 等文件名。
   Red Final 如实声明了这一相邻情形且未据此打开任何文件。

⇒ 第 1、2 条是 `IMP-020-14` 记录的向量在本轮的**两次复现**；第 3 条是**新形态**：
泄漏不一定来自检索，也可能来自**产物自身的元数据**。建议 `IMP-020-14` 的修法直接覆盖第 3 条
（封存文件名不应出现在 Red 可见文件的正文里）。

### 4.3 盲测认证不到的东西

`strict_blind_red_certification: true` 认证的是**流程**（谁在什么阶段读了什么），不是**结论的正确性**。
本轮最清楚的一例：Red Final 全部 `file:line` 判断都是**结构判断**、未核源码（它自己这么写的）。
⇒ 「盲」≠「已核实」。任何要用 Red Final 的实现层结论的地方，必须先有回源码的核对。

### 4.4 本轮实测出的方法论陷阱（4 条，3 条新）

**(a) 状态总线产物可能在多个阶段里一直是坏的，且没人校验 —— 新，且严重**

`00_manifest.yaml` 从 `red_wave_1` 那条 `red_wave_1_commit_ref` 写进去起，**一直是非法 YAML**：
未加引号的 `git log --grep "^rb-021: ..."` 含 `: `，YAML 把它当映射值。Controller 在 Wave 2 收口时
顺手 `yaml.safe_load` 才发现。已核实 `718c8524` 与 `957e8114` 两个提交上的 manifest **都解析失败**
（同一行 157）。

⇒ 这是**状态总线完整性**问题：manifest 是本流程的接线板，接线板坏了没人知道。
**必须**在每个 stage commit 上加一道 validator（`yaml.safe_load` + 必需键检查）。
这条建议进 ledger。

**(b) subagent 的 cwd 传递缺陷 —— 已有，本轮复现**

Resume Gate 的核验 subagent 报告「base `cdd2063b` 在本仓库不存在、`git rev-parse` 返回 unknown revision」。
Controller 复核：`git cat-file -t cdd2063b341e…` → `commit`，且它同时等于 `origin/main`
与本 round 分支的 merge-base。**base 有效**。根因：subagent 的 git 命令在**非仓库 cwd** 下执行。

⇒ 派发带 git 操作的 subagent 时必须**显式给绝对仓库路径**并在指令里要求 `git -C <repo>`。

**(c) 模板合规需要机械校验 —— 新**

Red Wave 2 的 h1/h2 偏差（§2.3）与各产物文件头字段（`blind` / `seen` / `not_seen` / `sealed`）
目前全靠执行者自觉。本轮靠人工比对 round 020 才发现。
⇒ 建议把「产物形态」做成可校验清单（标题层级、必需头部键、章节名）。

**(d) 占位符会被误当产物 —— 新，小但会浪费时间**

每个产物路径在 HEAD 上有一个**小占位 blob**（`04_blue_wave2_answers.md` 336 字节、
`04_red_evaluation.md` 341 字节）。Controller 的首次等待循环以「文件存在」为条件，
**立刻命中了占位符**，白等一轮。
⇒ 等待条件必须带**尺寸阈值 + mtime**，不能只看存在性。

### 4.5 本轮**没有**复现的缺陷（记录为正向）

round 020 的 `NO_ZUNO_CHANGE` F-20 记录：Red Final 与 Blue Reflection **并行**完成，
导致 Reflection 先按 Part A 判、产物到位后重写。本轮**顺序被强制**：
Red Final 先冻结提交（`144ba412`），Blue Reflection 才开工。**该缺陷本轮未复现。**

---

## 5. 本轮流程层面的改动建议（进入 `09_improvement_ledger.md`）

| 建议 | Owner | 触发 |
| --- | --- | --- |
| Resume Gate 核验清单新增「装配侧确认」项 | Resume Builder / Skill | §1.1、§1.2 |
| Attack Model 写入「claim 被证伪 ≠ premise 被证伪」规则 | Red Skill | §2.2 |
| 「自我修正」不得直接采信，需回源码核 | Blue Skill | §3.1 |
| 禁止三段式格式作为加分依据（若现有文本隐含奖励则删） | Blue Skill | §3.1 |
| stage commit 增加 manifest validator（`yaml.safe_load` + 必需键） | Harness / Protocol | §4.4(a) |
| 派发带 git 的 subagent 必须给绝对路径并要求 `git -C` | Harness | §4.4(b) |
| 产物形态可校验清单（标题层级 / 头部键 / 章节名） | Harness / Templates | §4.4(c) |
| 等待条件须带尺寸阈值 + mtime | Harness | §4.4(d) |
| `IMP-020-14` 修法扩展到「封存文件名不得出现在 Red 可见文件正文」 | Harness / Protocol | §4.2 第 3 条 |
| Red Final 之后必须有回源码核对（本轮由 Blue Reflection 承担） | Protocol | §2.4 |

> 以上均为**提案**，`improvement_review_gate: REQUIRED` 未过，本轮不自动应用。
