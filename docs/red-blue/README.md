# Zuno Red / Blue Interview Review

`docs/red-blue/` 用来持续验证四件事：当前 Zuno 能否压缩成可信简历；只看到简历的真实面试官会怎样追问；候选人的回答能否经住实现、失败和证据检查；这些压力最终应该推动 Resume、Skill、文档、架构、实现还是基础训练中的哪一层变化。

Red / Blue 不拥有 Project History、Target Architecture、Current Evidence 或 Personal Ownership。它的作用是制造压力、暴露断点、正确归因，再把改进送回真正的 Owner。

## 一轮不是终点，而是下一轮的输入

目标循环：

```text
main@固定 SHA
→ Build / Review / Freeze Resume
→ Build / Review / Freeze Red Plan
→ Red ↔ Blue 逐轮真实对攻
→ Red Evaluation
→ Blue Architecture Reflection
→ Resume / Red / Blue / Harness Retrospective
→ Improvement Ledger
→ User Improvement Gate
→ Apply approved changes
→ Next Resume Candidate
→ archive / merge
→ 新 main HEAD
→ 下一轮
```

高分不是唯一成功标准。一轮把某个 Resume Claim 打穿，但最终能确认问题属于 Evidence、Blue Skill 或 Architecture，并形成下一轮可验证修复，比“全 PASS”更有价值。

## Resume-first，但 Resume 也会被每轮重新审判

真实面试官先看到简历。每轮开始由 Resume Builder 从固定 `zuno_base_sha` 的 Project、Architecture、Modules、Evidence、selected provenance 与既有简历风格生成 `01_simulated_resume.md`。

一条好的 Resume bullet 不是“用了 LangGraph / MCP / GraphRAG”，而是压缩一个真实工程故事：

```text
系统哪里会错
→ 我做了什么技术决策
→ 关键机制是什么
→ 有什么可信结果 / 证据
```

轮末 `10_next_resume_candidate.md` 不是当前轮 Resume 的覆盖版本，而是吸收已批准改进后的下一轮候选稿。下一轮仍从新 main HEAD 校验，不允许把未实现 Target 或未补 Evidence 的内容因为“上一轮讨论过”就升级成事实。

## Live Interview 真正交替执行

`02_red_questions.md` 只保存 Interview Plan + Pressure Suite。现场不是 Red 一口气生成全部问题再让 Blue 批量回答。

实际顺序是：

```text
Red 问一个问题
→ commit
→ Blue 读取这个问题并回答
→ commit
→ Red 读取刚才回答，选一个最高信息增益 handle 追问
→ commit
→ Blue 回答
→ ...
```

`03_blue_answers.md` 因而是 Live Interview Exchange Ledger。它记录真正发生的 question / answer，而不是预写对话。

这种 commit-per-turn 设计同时解决两件事：Red 的 follow-up 真正依赖上一答；Blue 不可能提前知道下一问。

## Red Skill 与 Blue Skill 分开

Red 由 `.agent/red-blue/attack-model.md` 约束。它负责：听回答、选攻击 handle、追 Ownership / implementation / failure / evidence / Build-Buy / fundamentals，并在信息增益下降时换 thread。

Blue 由 `.agent/red-blue/defense-model.md` 约束。它负责：先直接回答，再按追问展开；区分本人和团队；把技术名词落到机制；诚实处理 small-sample、Pilot、Unknown 和 Target-only；不把回答说成 README 或 Evidence memo。

两套 Skill 都在 Round Init pin version。轮末可以修，但只能影响下一轮，不能回头重新评价本轮。

## Red Evaluation 与 Blue Reflection解决不同问题

Red Evaluation 模拟真实面试官，只看到 Resume、实际 Q/A 和 Red Skill。它可以判断“我不信这个 Claim”，但不能利用隐藏 Zuno 文档宣布事实真假。

Blue Architecture Reflection 再把这些信号放回 canonical docs / Evidence，区分：

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

Red 追到一个字段而 Blue 没答上，不等于 Architecture 缺对象。Architecture Gap 只用于 Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身有问题。

## Workflow Retrospective 不再只审 Red

一轮结束后必须分四部分复盘：

### Resume Builder

有没有把功能清单当贡献；有没有用漂亮但可疑的数字包装小样本；有没有选错技术故事。

### Red Skill

有没有听上一答；追问是否自然；能否连续进入代码 / 状态 / test / failure；有没有 AI interviewer / Reviewer checklist 味。

### Blue Skill

有没有先回答再展开；Ownership 是否主动说清；能否解释真实工程矛盾；有没有过度防御、照文档念、制造参数或把 Unknown 说满。

### Harness

Red / Blue 是否真正 turn-by-turn；firewall 有没有破；Gate 是否有必要；Pressure Suite 有没有被误当现场题单。

## Improvement Ledger：不允许“发现问题但不知道改哪”

`09_improvement_ledger.md` 给每条 finding 一个 primary class：

```text
RESUME_GAP
RED_SKILL_GAP
BLUE_SKILL_GAP
HARNESS_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_CHANGE
```

常见判断：

- Red 没听回答：改 Red Skill，不改架构；
- Blue 有材料但讲不清：先看 Blue Skill / Narrative；
- Resume claim 写错强度：改 Resume；
- 文档没解释已有 failure / call chain：改 Docs；
- 设计责任本身错：才进 Architecture；
- 代码没实现：Implementation；
- 没有 test / trace / benchmark：Evidence；
- 本人归属不清：Ownership；
- 纯基础没学会：Fundamentals。

每条还必须有 Owner、proposed change、evidence needed、risk、status 和 next-round retest。

## Improvement Gate 与下一轮

默认 `USER_IMPROVEMENT_REVIEW=REQUIRED`。面试断点不能未经判断直接改 canonical Zuno Truth。

批准的 Skill / Harness / Docs / Architecture 改动可以在 Round 后半段落到 branch，但全部标记 `NEXT_ROUND_ONLY`。本轮 Red verdict 和 Blue Reflection 永远引用原 base SHA 与 pinned Skill，不重新计算。

改动完成后生成 `10_next_resume_candidate.md`；Round archive + merge 后，下一 Round 从新的 exact main HEAD 开始，再校验这份候选简历。

## GitHub State Bus

每个 stage 和 live turn：

```text
read live Round branch HEAD
→ run only declared actor
→ write observable artifact
→ commit
→ next actor re-read
```

`CHATGPT_AUTO` 只能声明 `LOGICAL_GITHUB_MEDIATED`；严格 blind Red 要使用独立 context 的 `AGENT_AUTO / PHYSICAL_CONTEXT_ISOLATION`。

## Round Artifacts

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
09_improvement_ledger.md
10_next_resume_candidate.md
```

Round 的长期目标是让系统逐轮收敛：**简历越来越像真实工程经历，Red 越来越像真人面试官，Blue 越来越能把做过的东西讲清，文档与架构只在真正有缺陷时被修改。**