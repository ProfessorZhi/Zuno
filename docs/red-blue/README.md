# Zuno Red / Blue Interview Review

`docs/red-blue/` 用来验证一件比“文档写得完整”更困难的事：**把当前 Zuno 文档压缩成一份真实简历以后，一个只看到简历的大厂面试官会怎样追问；候选人能否只依靠 Zuno 文档把这些问题回答清楚；这些追问最终暴露的是架构问题、证据问题、简历问题，还是红队本身的问题。**

Red / Blue 不拥有 Project History、Target Architecture、Current Evidence 或个人 Ownership。它只产生压力、回答、评价和改进建议；正式修改仍回到各自 Canonical Owner。

## 为什么必须 Resume-first

真实面试官看不到 `docs/architecture/`，也不会提前知道 `Formal Admission`、`KnowledgeGeneration`、`Reconciliation` 这些内部术语。他看到的是简历里几行项目经历，然后根据岗位知识和工程经验决定往哪里追。

如果 Red 先读完整 Zuno 文档，再根据里面的薄弱处设计问题，得到的是 Architecture Reviewer，而不是 Interviewer。这会产生两个问题：

- 问题过度贴合 Zuno 内部答案，含金量看似很高，实际不符合真实面试入口；
- Red 很容易把“文档已经告诉它哪里有 Gap”误当成自己的面试能力。

新的正式 Round 因此先生成一份模拟简历。只有 Resume Builder 可以读取 Zuno docs；模拟简历冻结以后，Red 只能看这份简历。

## Round 的六个判断层

一轮不再只是 Red 问、Blue 答、Judge 判分。它依次回答六个问题。

### 1. 当前文档能写出什么简历

Controller / Resume Builder 阅读当前 Project、Architecture、Modules、Evidence 和既有简历风格，形成 `01_simulated_resume.md`。

模拟简历要有竞争力，但必须守事实层级：

- 已实现并有个人证据的，可以写实现；
- Target 架构只能写参与设计、复盘、边界梳理；
- LIPLAB 论文是团队研究背景，不自动成为本人实现；
- 没有测量就不制造效果数字；
- Pilot 不写成 Production。

它是**本轮攻击界面**，不是自动覆盖真实求职简历。

### 2. 面试官只看简历会问什么

Red 读取模拟简历、岗位 / JD、Red Interview Skill 和模型通用知识。

它看不到 Zuno docs、源码、Evidence、Blue source trace，也看不到模拟简历的构建来源。

默认一次生成 100 个问题，但 100 不是 KPI。问题要围绕 3–6 条高风险 Claim 形成完整攻击链，重点使用：

- Claim 取证；
- 精品思维；
- 全链路追踪；
- Ownership；
- Build / Buy / Extend / Defer；
- 故障与反例；
- Evidence；
- 项目自然下钻基础；
- Simplification / Delete condition。

正式机器规则见 [`.agent/red-blue/attack-model.md`](../../.agent/red-blue/attack-model.md)。

### 3. Zuno 文档能否支撑候选人回答

Blue 看到模拟简历、Red 题单和允许的 Zuno canonical docs。它逐题回答，关键 Claim 留 source trace。

Blue 可以明确回答 Unknown，也可以说简单方案足够、某机制应删除、某项只是 Target。它不需要替现有架构辩护。

### 4. 真实面试官是否接受这些回答

Red Evaluation 再次只看简历、题目和 Blue 答案，不看 Zuno docs。

它判断的是：

- 这像不像真正做过；
- 是否能落到实现；
- Ownership 是否可信；
- 是否理解替代方案；
- 故障和基础原理是否经得住；
- 有没有“背文档感”；
- 30 秒 / 90 秒 / 3 分钟能不能讲。

Red 可以判回答不可信，但不能宣布 Zuno Architecture Truth。

### 5. 面试暴露的到底是什么问题

Blue Architecture Reflection 读取 Red 的评价和 Zuno docs，把问题重新分类：

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

这是正式 Round 必须有的一层。

`06_workflow_retrospective.md` 不评价“Blue 有没有赢”，而评价：

- 问题是否真正从简历产生；
- 有没有技术深度；
- 是否完整追踪业务→实现→故障→证据→基础；
- 有没有大量重复；
- 有没有攻击重复造轮子；
- 是否像真实大厂面试，而不是 Reviewer checklist；
- 用户对问题质量的评价是什么；
- Red Skill / Persona / question budget 是否需要修改。

用户明确评价“红队不合格”“问题没含金量”时，这个反馈拥有最高优先级。不能拿 PASS 率替 Red 辩护。

## Red Interview Skill 的来源

当前 Red Skill 不是凭空生成的题库。它吸收了用户本人真实面试和公开面经中反复出现的行为模式，例如：

- 先验证 Claim，再谈设计；
- 为什么先于怎么做；
- 强制 Ownership；
- 强制 Build / Buy / Extend / Defer；
- 从项目一路追到函数、状态、Schema、并发、网络、数据库和测试；
- 用 timeout、duplicate、权限撤销、版本变化等反例验证可靠性；
- 追 Baseline、Dataset、Metric、Ablation、Bad Case；
- Current / Target / Production 分层；
- 反事实删复杂度。

原始面经只用于**独立的 Skill 更新任务**。每个正式 Round 的 Red 默认不再读取大批原始面经，以免一轮问题受具体题库污染。

## 两种执行模式

### CHATGPT_AUTO

一个 ChatGPT 对话内程序性隔离各阶段。Resume Builder 可以先读取 Zuno docs；切换到 Red 阶段以后，Red 的允许输入缩到模拟简历 + Skill + 岗位信息。

每个阶段完成立即归档到 GitHub。不能等一轮结束后凭摘要重建。

### AGENT_AUTO

Controller 为 Resume Builder、Red、Blue、Red Evaluation、Blue Reflection、Workflow Retrospective 建立独立 context。

独立 Agent 的主要价值是更强的 context firewall；它不改变 Round 文件结构，也不允许只保留最终 report。

两个模式都只保存可观察 I/O 和控制事件，不保存或伪造模型私有 chain-of-thought。

## 工作区

正在执行的 Round 位于 [`workspace/`](./workspace/README.md)：

```text
docs/red-blue/workspace/<round-id>/
```

一轮固定九个文件：

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

Round 结束后整个文件夹原样移动到：

```text
docs/red-blue/rounds/<round-id>/
```

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

这样每轮都能比较文档演进是否真的改善了可面试性。

## 防止两个 AI 自嗨

正式 Round 至少依靠六个约束：

1. **Resume-first firewall**：Red 看不到 Zuno docs。
2. **Claim-grounded questions**：每个高价值问题来自简历 Claim。
3. **Blue source trace**：项目事实必须回到允许来源。
4. **Red interviewer verdict**：评价回答是否像真正做过，而不是文档是否自洽。
5. **Blue architecture reflection**：避免把所有面试断点都误改成架构。
6. **Workflow retrospective + user feedback**：Red 自己也必须被审计。

Round 的成功标准不是 Red 问得多、Blue PASS 多，而是这套流程能持续提高三件事：**简历 Claim 的可信度、Zuno 文档的工程解释力、红队问题本身的质量。**

## 历史 Round

`docs/red-blue/rounds/` 中早期 Round 按当时协议保留。方法变更后不重写历史结论。

尤其 `rb-2026-09-13-zuno-interview-batch-013` 使用了“Red 可读取 Zuno 项目材料”的旧边界，已经被本 resume-first protocol 取代。它可以用于观察旧方法为什么会产生 Reviewer-style 问题，但不再作为合格 Interview Red Team 的验收基准。

更早的 manual / early automated 资料继续保存在 `archive/legacy/`。