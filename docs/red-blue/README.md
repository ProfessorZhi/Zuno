# Zuno Red / Blue Interview Review

`docs/red-blue/` 用来验证三件彼此不同的事：当前 Zuno 文档能否压缩成可信简历；一个只看到简历的大厂面试官会怎样追问；候选人的回答最终暴露的是项目事实、实现证据、简历、架构，还是 Red 自己的问题。

Red / Blue 不拥有 Project History、Target Architecture、Current Evidence 或个人 Ownership。它只产生压力、回答、评价和改进建议，正式事实仍回到各自 Canonical Owner。

## Resume-first

真实面试官先看到简历，而不是 `docs/architecture/`。如果 Red 先读完整 Zuno 文档再反推问题，它会逐渐变成 Architecture Reviewer：问题高度贴合内部术语，也会因为提前知道 Gap 而显得“很会问”。

正式 Round 因此先由 Resume Builder 读取固定 `zuno_base_sha` 的 Project、Architecture、Modules、Evidence、选定 provenance 和已有简历风格，生成 `01_simulated_resume.md`。模拟简历冻结以后，Red 的正式输入只剩模拟简历、岗位 / JD、Red Interview Skill 和模型通用知识。

## GitHub 在流程中间

每个正式 Round 都在独立 branch / Draft PR 中执行：

```text
main@固定 SHA
→ red-blue/<round-id>
→ docs/red-blue/workspace/<round-id>/
→ stage 读取 live branch HEAD
→ stage artifact + manifest + transcript
→ commit
→ 下一 stage 重新读取新 HEAD
```

GitHub commit 是阶段边界。聊天里未提交的摘要、上一角色临时输出和 Controller 草稿不能直接跨阶段成为正式输入。

Transcript 为每个 stage 记录 `input_head_sha`。Manifest 使用 `last_consumed_head_sha` 表示最近完成阶段实际读取的输入 HEAD；当前 branch HEAD 永远从 GitHub live ref 获取，避免把“上一步输入”误写成“当前状态”。

Round 启动前已经知道的用户约束必须在第一笔 Round transaction 中进入 `07_user_feedback.md` 和 transcript。中途的新反馈同样先提交，再影响后续阶段。

## CHATGPT_AUTO 与 AGENT_AUTO

`CHATGPT_AUTO` 在单个 ChatGPT 对话中执行，但每个 handoff 仍经过 GitHub：

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

它适合快速迭代简历、Red Skill 和文档支撑能力，但不能证明模型物理遗忘了 Resume Builder 曾看过的项目资料。

`AGENT_AUTO` 在 Red 确实使用独立 context 时可以声明：

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

两种模式使用同一 GitHub state machine；物理 context 隔离与 GitHub 状态交接承担不同责任。

## Red 的产物分成 Pressure Suite 和 Primary Path

Round 可以生成 100 个高质量问题，但 100 只是**压力集容量**，不能伪装成一场真实 45–60 分钟面试会逐题问完。

默认结构：

```text
PRIMARY_PATH: 30（允许 25–40）
RESERVE_FOLLOWUP: 70
```

Primary Path 代表真实技术一面主路径。它应该尽快验证最高风险的 2–3 条实现 Claim，而不是先花大量时间平均覆盖所有架构主题。

Reserve 只有在 Primary 回答触发时才进入，用于继续下钻并发、网络、数据库、算法、测试、Evidence 或 Build/Buy；没有触发条件的同义问题不应保留。

### Ownership Kill Switch

简历如果直接写了函数、算法、Schema、test artifact 或精确指标，Red 必须早期验证：

```text
你具体改了什么实现对象？
→ 改前/改后的数据流是什么？
→ 给一个真实规则、参数或 assertion
```

如果候选人连续无法回答这些最小 Ownership probe，该 Claim 触发 Kill Switch。Red 记录 credibility break，切到下一条 Claim，而不是用十几道同义问题继续消耗面试时间。

Ownership 成立以后，再继续追算法、状态、并发、故障、成本和测量。

## USER_RED_REVIEW：先审 Red，再运行 Blue

工作流处于校准期时，Round manifest 默认：

```text
red_review_gate: REQUIRED
```

Red 第一次提交 `02_red_questions.md` 后，状态进入 `USER_RED_REVIEW`，自动流程停止。用户直接检查 Primary Path 和完整压力集。

用户只有三种结果：

```text
APPROVE
REQUEST_REVISION
ABORT
```

`APPROVE` 后，Controller 提交一次状态转换，把 `red_questions_status` 改成 `FROZEN`，Blue 才能执行。

`REQUEST_REVISION` 时，用户反馈先进入 `07_user_feedback.md` 和 transcript。Red Revision 仍只能读取原 Red allowlist、当前题单和这条已提交的质量反馈；它不能因为用户要求改题而偷看 Zuno docs。更新后的 `02_red_questions.md` 再次进入 `USER_RED_REVIEW`。前一版本由 Git history 保留。

这一步的目的很明确：Red Skill 还没有校准稳定以前，不能让 Red 自己生成问题、自己做 retrospective、然后宣布自己已经合格。

## 一轮的后续阶段

用户批准 Red questions 后才继续：

```text
FROZEN Red Questions
→ Blue 根据固定 Zuno docs 回答
→ Red Evaluation 只按简历 / questions / answers 做面试官 verdict
→ Blue Reflection 结合项目资料判断真正 Gap
→ Workflow Retrospective 审判 Red / Harness
→ Archive / CI / Merge
```

Blue 可以明确回答 Unknown。诚实边界本身是加分，但如果简历明确写“我实现某算法”，候选人却讲不出算法、字段、调用链或测试，Red 仍然可以判 implementation ownership 不成立。

## 面试断点怎样路由

Blue Reflection 把问题分成：

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

面试官追到了历史实现细节，而 Project documentation 没恢复，不意味着需要给 Target Architecture 再加一个对象。只有 Owner、Authority、State、Recovery、Security、Contract 或 Build/Buy 因果本身不成立，才进入 Architecture Revision。

## Red Interview Skill

Red Skill 强制以下行为：Claim 取证、Personal Ownership、Build / Buy / Extend / Defer、真实实现对象、故障反例、Eval / metric / baseline / bad case、项目自然下钻 Python / network / DB / Agent/RAG 基础，以及复杂度删除条件。

基础题从项目长出来。例如 Tool timeout 可以自然下钻到 HTTP/TCP、async cancellation、idempotency 和 remote side effect；Memory scope 可以下钻到 request-local state、DB isolation 和 stale cache。它不通过随机八股假装“技术深度”。

## 固定九份 artifact

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

活动 Round 位于 `docs/red-blue/workspace/<round-id>/`。关闭前在同一 branch 上原样移动到 `docs/red-blue/rounds/<round-id>/`，Draft PR 转 ready，required CI 通过后 merge，再读取 exact `main` HEAD。

坏问题、弱回答、用户批评和 Red Revision 不做“漂亮化重写”。这些历史本身就是 Harness 迭代证据。

## Retest

新的项目文档、简历 Claim 或 Red Skill 需要复测时创建新 Round，不在已完成 Round 中继续追加第二批问题：

```text
Docs N → Resume N → Red N → User Red Review → Blue / Evaluation
→ 独立修复
Docs N+1 → Resume N+1 → New Round
```

Round 的成功标准不是题量或 PASS 率，而是持续提高：**简历 Claim 的可信度、项目文档对个人实现的工程解释力、以及 Red 本身的问题质量。**
