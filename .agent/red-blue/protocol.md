# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法见 `docs/red-blue/README.md`。

## 目标

Red / Blue 是持续收敛的工程闭环：

```text
当前 Zuno Truth
→ Resume Builder
→ Resume Review / Freeze
→ Red Plan / PRESSURE_SUITE
→ Red / Blue 对攻
→ Red Evaluation
→ BLUE_ARCHITECTURE_REFLECTION
→ Resume / Red Skill / Blue Skill / Harness Retrospective
→ Improvement Ledger
→ 用户批准改进
→ NEXT_ROUND_ONLY changes
→ Next Resume Candidate
→ merge
→ 下一轮
```

Round 的目的不是让 Blue “答赢”，而是让 Resume、Red、Blue、文档、架构、实现和 Evidence 在压力下逐轮变得更可信。

Red / Blue 产物不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或 Personal Ownership。正式事实始终回到 canonical owner。

## GitHub 是运行时状态总线

每个 stage / wave / live turn 都遵守：

```text
read Round branch HEAD
→ verify stage + allowlist
→ read declared inputs
→ run one actor
→ write artifact + manifest + transcript
→ commit
→ next actor re-read new HEAD
```

GitHub commit 是 handoff barrier。聊天摘要、角色临时文本和未提交草稿不能跨阶段成为正式输入。

正式 Round 从固定 `main@zuno_base_sha` 创建独立 branch + Draft PR：

```text
red-blue/<round-id>
docs/red-blue/workspace/<round-id>/
```

当前 Round 的评价只针对冻结时的 Resume、pinned Skill 与 `zuno_base_sha`。轮末修改 Skill / Docs / Architecture 只对下一轮生效，不能回头重算当前 verdict。

## 两种 execution mode

Round 的 `mode` 仍然是隔离模式：

```text
CHATGPT_AUTO
AGENT_AUTO
```

面试执行方式单独由 `execution_mode` 表示：

```text
BATCH_DUEL
LIVE_INTERVIEW
```

### BATCH_DUEL — 自动 Round 默认

用于自动化架构压力测试、Resume 迭代和 Skill 校准。用户不逐题扮演候选人。

```text
Frozen Resume + Frozen Red Plan
→ RED_WAVE_1 batch
→ commit
→ BLUE_WAVE_1 batch
→ commit
→ RED_WAVE_2 reads BLUE_WAVE_1
→ targeted follow-up batch
→ commit
→ BLUE_WAVE_2 batch
→ commit
→ RED_EVALUATION
```

关键不变量：

- Wave 2 Red **必须在 Blue Wave 1 commit 以后生成**；禁止预写两波再假装 adaptive；
- Red Wave 1 默认从 Resume / Spoken Seeds / Pressure Suite 中选择约 20–40 个高信息量问题；
- Red Wave 2 默认只追 Blue Wave 1 暴露的约 10–30 个高价值 gap；
- 100-question `PRESSURE_SUITE` 继续做离线 coverage audit，不要求 Blue 每轮机械回答 100 题；
- Blue 每个 Wave 批量回答并直接写 GitHub，用户只审阶段结果和 Gate；
- `02_red_questions.md` 保存 Plan + Red Wave 1 + Red Wave 2；`03_blue_answers.md` 保存 Blue Wave 1 + Blue Wave 2。必要时执行中的临时分片在 close 前收敛回固定 artifact。

### LIVE_INTERVIEW — 显式真人模拟时使用

只有用户明确要求逐题真人面试时使用。

```text
LIVE_INTERVIEW_SEEDS
→ RED_TURN commit
→ BLUE_TURN commit
→ DYNAMIC_FOLLOWUP
→ RED_TURN commit
→ BLUE_TURN commit
→ ...
```

每个 spoken question 仍遵循 one-question-one-intent。LIVE_INTERVIEW 不因 BATCH_DUEL 的存在而降级。

## 生命周期

```text
ROUND_INIT
→ BUILD_SIMULATED_RESUME
→ USER_RESUME_REVIEW
   ├─ APPROVE → FREEZE_RESUME
   ├─ REQUEST_REVISION → RESUME_REVISION → USER_RESUME_REVIEW
   └─ ABORT → CLOSE / SUPERSEDE
→ RED_QUESTIONS
→ USER_RED_REVIEW
   ├─ APPROVE → FREEZE_RED_QUESTIONS
   ├─ REQUEST_REVISION → RED_REVISION → USER_RED_REVIEW
   └─ ABORT → CLOSE / SUPERSEDE
→ INTERVIEW_EXECUTION
   ├─ BATCH_DUEL → RED_WAVE_1 → BLUE_WAVE_1 → RED_WAVE_2 → BLUE_WAVE_2
   └─ LIVE_INTERVIEW → RED_TURN ↔ BLUE_TURN
→ RED_EVALUATION
→ BLUE_ARCHITECTURE_REFLECTION
→ WORKFLOW_RETROSPECTIVE
→ IMPROVEMENT_SYNTHESIS
→ USER_IMPROVEMENT_REVIEW
   ├─ APPROVE / PARTIAL_APPROVE → APPLY_IMPROVEMENTS
   ├─ REQUEST_REVISION → IMPROVEMENT_REVISION
   └─ DEFER → record reason
→ BUILD_NEXT_RESUME_CANDIDATE
→ USER_FEEDBACK_CAPTURE
→ CLOSE_AND_ARCHIVE
→ merge Round PR
→ next Round from new main HEAD
```

默认校准 Round 要求 Resume、Red Plan、Improvement 三个用户 Gate。`USER_RED_REVIEW` 防止坏攻击器污染后续；`USER_IMPROVEMENT_REVIEW` 防止一次面试误判直接改坏 canonical Truth。

## Resume Builder

Resume Builder 从固定 base SHA 读取 Project、Architecture、Modules、Evidence、selected provenance 和用户简历风格，生成 `01_simulated_resume.md`。

模拟简历必须像真实投递材料，不像 Evidence memo。默认 1 行项目简介、1 行技术栈、约 4–6 条高价值贡献。一条 bullet 优先压缩：

```text
真实问题 → 本人动作 / 技术决策 → 机制 → 可验证结果
```

事实边界强制：Pilot ≠ Production；团队工作 ≠ Personal Ownership；Target ≠ Current；small smoke ≠ formal benchmark。

冻结 Resume 正文一旦修改，已有 Red Plan 自动 `INVALIDATED_BY_RESUME_CHANGE`。

## Red Plan 与 PRESSURE_SUITE

Red 正式输入只有：

```text
frozen 01_simulated_resume.md
target role / JD / stage
pinned .agent/red-blue/attack-model.md
model general knowledge
```

### Red 禁止输入

```text
docs/project/
docs/architecture/
docs/modules/
docs/evidence/
docs/governance/
Zuno 源码 / PR / commit diff
Blue hidden answer key
```

Red 不拥有隐藏答案。

`02_red_questions.md` 保存 Interview Threads、6–10 个 Spoken Seeds、Follow-up Policy、Branch Examples 和 100-question `PRESSURE_SUITE`。Pressure Suite 是覆盖库，不是 BATCH_DUEL 或 LIVE_INTERVIEW 的固定现场脚本。

### BATCH_DUEL Red selection

Red Wave 1 从 Resume claims 中选高信息量覆盖，不要求平均照顾每条 bullet。Blue Wave 1 提交后，Red 提取具体数字、技术选择、Unknown、Ownership、failure、未证明状态等 handles，再生成 Wave 2。

Wave 2 必须在 artifact 中记录它攻击的是哪些 **observable answer gaps**，但不保存模型私有 chain-of-thought。

## Blue Candidate Skill / BLUE_ANSWERS

Blue 回答行为由 pinned `.agent/red-blue/defense-model.md` 约束。canonical docs / Evidence 负责“什么事实可以说”，Defense Skill 负责“怎样像真实候选人说”。

Blue 正式 allowlist：

```text
frozen Resume
current committed Red questions / wave
prior observable exchanges / prior waves
pinned defense-model.md
AGENTS.md
docs/project/ @ zuno_base_sha
docs/architecture/ @ zuno_base_sha
docs/modules/ @ zuno_base_sha
docs/decisions/ @ zuno_base_sha
docs/evidence/ @ zuno_base_sha
selected provenance @ zuno_base_sha
```

Blue 不读取未来 Red Wave、Red Evaluation 或尚未产生的 retrospective。

BATCH_DUEL 中，`03_blue_answers.md` 按 Wave 保存 batch answers；artifact 可以附 `source_support / boundary` 供后续 Reflection 使用，但 spoken answer 不把这些 source trace 念给面试官。

LIVE_INTERVIEW 中，`03_blue_answers.md` 保存实际 Q/A exchange ledger。

## Red Evaluation

执行结束后，Red Evaluation 读取 Frozen Resume、Frozen Red Plan、实际 batch waves / live exchanges 与 pinned attack-model，不读取 Zuno canonical docs。

它评价 Ownership、Business Causality、Implementation Depth、Build/Buy、Failure/Recovery、Evidence、Fundamentals 和 Communication。Red 可以说“作为面试官我不信”，不能宣布 Zuno Architecture Truth。

## BLUE_ARCHITECTURE_REFLECTION

Blue Reflection 再把 Red 信号放回 canonical sources，分类：

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

只有 Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身不成立，才建议 Architecture Revision。Red 问到某个细节、Blue 一时没答上，不自动产生新 Architecture Object。

## WORKFLOW_RETROSPECTIVE

`06_workflow_retrospective.md` 必须分别评价：

### Resume Builder
- 是否选了真实工程问题；
- 是否包装数字；
- 是否把个人贡献写弱或写强。

### Red Skill
- Wave / Follow-up 是否真依赖上一答；
- 是否追到实现、failure、evidence；
- 是否像 Reviewer checklist；
- BATCH_DUEL 是否把 Pressure Suite 错当 100 题必答卷。

### Blue Skill
- 是否先回答再展开；
- Ownership 与时间层是否清楚；
- 是否区分 Historical / Current / Target / Unknown；
- 是否能从项目切到底层机制；
- spoken answer 是否像真人而不是 source report。

### Harness
- commit handoff / firewall 是否正确；
- BATCH_DUEL Wave 2 是否真的消费 Wave 1；
- LIVE_INTERVIEW turn ordering 是否正确；
- Gate 是否产生无意义摩擦。

Retrospective 不能修改本轮答案或 verdict。

## Improvement Ledger

`09_improvement_ledger.md` 为每条 finding 指定 primary owner：

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

每条至少记录 signal、root_cause、owner、proposed_change、evidence_needed、risk、status、next_round_retest。

归因原则：Red 差先改 Red/Harness；Blue 有材料却讲不清先改 Blue/Narrative；Target 没实现是 Implementation；有实现缺证据是 Evidence；只有 Architecture Authority 本身有问题才改 Architecture。

## USER_IMPROVEMENT_REVIEW 与 Apply

默认用户批准后才修改 canonical Skill、Harness、Docs 或 Architecture。用户在当前对话中对某个具体 workflow correction 给出明确指令时，可以把该 item 记录为已批准并在 Round 后半段应用。

Architecture 修改仍满足 Owner / ADR；Implementation Gap 不能靠改文档伪装解决。

所有 post-round changes：

```text
change_effective_scope: NEXT_ROUND_ONLY
current_round_verdict_recomputed: false
```

## 下一版简历与下一轮

批准的改进应用后，Resume Builder 从 post-improvement HEAD 生成 `10_next_resume_candidate.md`。未解决的 Implementation / Evidence / Ownership gap 不得因本轮讨论过就升级为 Resume fact。

下一 Round 从新的 exact main HEAD 重新验证候选简历并经过 `USER_RESUME_REVIEW`。

## Context Firewall

### CHATGPT_AUTO

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

同一 ChatGPT 对话不能证明物理遗忘。严格 blind Red 验收使用独立 context 的 AGENT_AUTO。

### AGENT_AUTO

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

AGENT_AUTO 也可以使用 BATCH_DUEL 或 LIVE_INTERVIEW。

## 固定 Round Artifacts

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

执行中为了迁移旧 Round 临时产生的 wave 分片必须在 close 前收敛回固定 artifact 或明确作为 compatibility artifact 归档。

所有 artifact 只保存 observable role I/O、GitHub refs、classification、decision 和用户 intervention；不保存或伪造模型私有 chain-of-thought。
