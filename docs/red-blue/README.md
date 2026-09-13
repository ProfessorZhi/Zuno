# Zuno Red / Blue Interview Review

`docs/red-blue/` 用来验证一件比“文档写得完整”更困难的事：**把当前 Zuno 文档压缩成一份真实简历以后，一个只看到简历的大厂面试官会怎样追问；候选人能否依靠 Zuno 文档把这些问题回答清楚；这些追问最终暴露的是架构问题、证据问题、简历问题，还是红队本身的问题。**

Red / Blue 不拥有 Project History、Target Architecture、Current Evidence 或个人 Ownership。它只产生压力、回答、评价和改进建议；正式修改仍回到各自 Canonical Owner。

## 为什么必须 Resume-first

真实面试官看不到 `docs/architecture/`，也不会提前知道 `Formal Admission`、`KnowledgeGeneration`、`Reconciliation` 这些内部术语。他看到的是简历里几行项目经历，然后根据岗位知识和工程经验决定往哪里追。

如果 Red 先读完整 Zuno 文档，再根据里面的薄弱处设计问题，得到的是 Architecture Reviewer，而不是 Interviewer。这会产生两个问题：问题过度贴合 Zuno 内部答案；Red 也容易把“文档已经告诉它哪里有 Gap”误当成自己的面试能力。

正式 Round 因此先生成一份模拟简历。Resume Builder 可以读取 Zuno docs；模拟简历冻结以后，Red 的正式业务输入只来自这份简历、岗位信息、Red Interview Skill 和通用技术知识。

## GitHub 必须处在流程中间

“每阶段最后写一份 GitHub 记录”仍然不够。如果 Red、Blue 和 Reflection 实际通过同一个聊天上下文直接交接，那么 GitHub 只是旁路日志，无法约束输入边界，也无法从中间状态恢复。

现在正式 Round 把 GitHub 作为运行时状态总线：

```text
main@固定 SHA
→ red-blue/<round-id> branch
→ Draft PR
→ 读取 branch HEAD 的阶段输入
→ 生成一个阶段产物
→ artifact + manifest + transcript 一起提交
→ 下一阶段重新读取新的 HEAD
```

阶段之间只有**已提交 artifact**能够传递。聊天里尚未归档的摘要、上一角色的临时文本和 Controller 草稿都不能直接成为下一阶段输入。

用户中途评价同样属于状态变化。只要反馈会影响当前 Round，就先写入 `07_user_feedback.md` 和 `08_session_transcript.md` 并提交，再继续执行。

这让单个 ChatGPT 对话也拥有确定的 stage boundary、可恢复状态和完整 GitHub 历史。但它解决的是**流程隔离和可审计性**，不能制造同一模型对话中不存在的物理遗忘。

## CHATGPT_AUTO 与 AGENT_AUTO 的保证不同

### CHATGPT_AUTO

一个 ChatGPT 对话可以作为 Controller 完成全部阶段，但每个阶段都必须从 Round branch 当前 HEAD 重新读取允许输入，并在 commit 后才能进入下一阶段。

该模式标记为：

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

同一聊天里 Resume Builder 如果已经看过 Zuno docs，底层对话上下文仍可能保留这些信息。所以 `CHATGPT_AUTO` 很适合快速测试简历攻击面、Red 问题质量和 Blue 文档支撑能力，但不能单独证明“Red 从未接触过项目文档”。

### AGENT_AUTO

独立 Resume Builder、Red、Blue、Red Evaluation、Blue Reflection 和 Workflow Retrospective context 继续使用完全相同的 GitHub branch / PR / commit 协议。

该模式可以在确实建立独立 Red context 时标记：

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

物理 context 隔离和 GitHub 状态总线解决两个不同问题：前者限制一个角色能知道什么，后者保证阶段之间怎样交接、怎样审计和怎样恢复。

## Round 的六个判断层

### 1. 当前文档能写出什么简历

Resume Builder 阅读当前 Project、Architecture、Modules、Evidence 和既有简历风格，形成 `01_simulated_resume.md`。

模拟简历要有竞争力，但必须守事实层级：已实现并有个人证据的，可以写实现；Target 架构只能写参与设计、复盘、边界梳理；LIPLAB 论文是团队研究背景，不自动成为本人实现；没有测量就不制造效果数字；Pilot 不写成 Production。

它是**本轮攻击界面**，不是自动覆盖真实求职简历。

`01_simulated_resume.md` 冻结并提交以后，Round 才进入 Red 阶段。

### 2. 面试官只看简历会问什么

Red 从当前 Round branch HEAD 读取模拟简历、岗位 / JD、Red Interview Skill；默认一次生成 100 个问题，但 100 不是 KPI。

问题要围绕 3–6 条高风险 Claim 形成完整攻击链，重点使用 Claim 取证、精品思维、全链路追踪、Ownership、Build / Buy / Extend / Defer、故障反例、Evidence、项目自然下钻基础、Simplification / Delete condition。

正式机器规则见 [`.agent/red-blue/attack-model.md`](../../.agent/red-blue/attack-model.md)。

### 3. Zuno 文档能否支撑候选人回答

`02_red_questions.md` 提交以后，Blue 从新的 GitHub HEAD 读取冻结简历和题单，再按本轮固定 `zuno_base_sha` 读取允许的 Zuno canonical docs。

Blue 可以明确回答 Unknown，也可以说简单方案足够、某机制应删除、某项只是 Target。它不需要替现有架构辩护。

### 4. 真实面试官是否接受这些回答

`03_blue_answers.md` 提交以后，Red Evaluation 再从 GitHub 读取简历、题目和 Blue 答案，不把 Zuno docs 作为评价输入。

它判断回答像不像真正做过，是否能落到实现，Ownership 是否可信，是否理解替代方案，故障和基础原理是否经得住，以及 30 秒 / 90 秒 / 3 分钟能不能讲。

Red 可以判回答不可信，但不能宣布 Zuno Architecture Truth。

### 5. 面试暴露的到底是什么问题

`04_red_evaluation.md` 提交以后，Blue Architecture Reflection 再结合固定 Zuno docs，把问题重新分类：

```text
SIMULATED_RESUME_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_ZUNO_CHANGE
```

面试官问到了一个历史字段，而仓库没有恢复，并不意味着需要新增架构对象。只有设计因果、Authority、State、Recovery、Security、Contract 或 Build/Buy 本身不成立，才进入 Architecture Revision。

### 6. Red 本身问得好不好

`06_workflow_retrospective.md` 不评价“Blue 有没有赢”，而评价问题是否真正从简历产生、有没有技术深度、是否完整追踪业务→实现→故障→证据→基础、有没有大量重复、有没有攻击重复造轮子，以及是否像真实大厂面试。

用户明确评价“红队不合格”“问题没含金量”时，这个反馈拥有最高优先级。不能拿 PASS 率替 Red 辩护。

## Red Interview Skill 的来源

当前 Red Skill 吸收了用户本人真实面试和公开面经中反复出现的行为模式：先验证 Claim，再谈设计；强制 Ownership；强制 Build / Buy / Extend / Defer；从项目追到函数、状态、Schema、并发、网络、数据库和测试；用 timeout、duplicate、权限撤销、版本变化等反例验证可靠性；追 Baseline、Dataset、Metric、Ablation、Bad Case；严格分 Current / Target / Production；用反事实测试能否删除复杂度。

原始面经只用于**独立的 Skill 更新任务**。每个正式 Round 的 Red 默认不再读取大批原始面经，以免一轮问题受具体题库污染。

## 一轮一个 GitHub branch / PR

活动 Round 位于自己的 branch：

```text
red-blue/<round-id>
```

该 branch 上有：

```text
docs/red-blue/workspace/<round-id>/
```

固定九份文件：

```text
00_manifest.yaml
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md
07_user_feedback.md
08_session_transcript.md
```

每个阶段完成立即 commit 到同一个 Draft PR。Round 完成后，在 branch 上把 workspace 整体移动到：

```text
docs/red-blue/rounds/<round-id>/
```

然后 Draft PR 转 ready，跑 required CI，merge，最后重新读取精确 `main` HEAD。

不创建“漂亮版”替换原始历史。坏问题、弱回答和用户批评都应该留下。

## 一轮为什么只做一次 Red batch

默认 100 问已经足以对一版模拟简历形成广度和深度压力。若 Blue 修复了架构、文档或简历，再用同一文件夹继续问，会混淆“哪一版文档对应哪一版简历”。

因此 retest 创建新 Round：

```text
Docs version N
→ Simulated Resume N
→ Red N
→ Blue N
→ Evaluation / Reflection / Workflow Retrospective

独立修复

Docs version N+1
→ Simulated Resume N+1
→ New Red Round
```

## 防止两个 AI 自嗨

正式 Round 依靠七个约束：

1. **Resume-first**：攻击入口先压缩成简历。
2. **GitHub state bus**：阶段之间只能通过已提交 artifact 交接。
3. **Claim-grounded questions**：每个高价值问题来自简历 Claim。
4. **Blue source trace**：项目事实回到固定 Zuno sources。
5. **Red interviewer verdict**：评价回答是否像真正做过，而不是文档是否自洽。
6. **Blue architecture reflection**：避免把所有面试断点都误改成架构。
7. **Workflow retrospective + user feedback**：Red 自己也必须被审计。

若需要严格证明 blind Red，再增加 `AGENT_AUTO` 的独立 context 隔离。

Round 的成功标准不是 Red 问得多、Blue PASS 多，而是这套流程能持续提高三件事：**简历 Claim 的可信度、Zuno 文档的工程解释力、红队问题本身的质量。**

## 历史 Round

`docs/red-blue/rounds/` 中早期 Round 按当时协议保留。方法变更后不重写历史结论。

尤其 `rb-2026-09-13-zuno-interview-batch-013` 使用了“Red 可读取 Zuno 项目材料”的旧边界，已经被当前 resume-first + GitHub-mediated protocol 取代。它可以用于观察旧方法为什么会产生 Reviewer-style 问题，但不再作为合格 Interview Red Team 的验收基准。

更早的 manual / early automated 资料继续保存在 `archive/legacy/`。