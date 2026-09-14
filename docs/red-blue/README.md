# Zuno Red / Blue Interview Review

`docs/red-blue/` 用来持续验证四件事：当前 Zuno 能否压缩成可信简历；只看到简历的面试官会怎样攻击；候选人的回答能否经住实现、失败和证据检查；这些压力最终应该推动 Resume、Skill、文档、架构、实现还是基础训练中的哪一层变化。

Red / Blue 不拥有 Project History、Target Architecture、Current Evidence 或 Personal Ownership。它负责制造压力、暴露断点、正确归因，再把改进送回真正的 Owner。

## 一轮不是终点，而是下一轮的输入

```text
main@固定 SHA
→ Build / Review / Freeze Resume
→ Build / Review / Freeze Red Plan
→ Red / Blue 对攻
→ Red Evaluation
→ Blue Architecture Reflection
→ Resume / Red / Blue / Harness Retrospective
→ Improvement Ledger
→ User Improvement Gate
→ NEXT_ROUND_ONLY changes
→ Next Resume Candidate
→ archive / merge
→ 新 main HEAD
→ 下一轮
```

高分不是唯一成功标准。一次 FAIL 如果能被准确归因、形成真实改进并在下一轮复测，比为了全 PASS 修改答案更有价值。

## Resume-first

真实面试官先看到简历。每轮由 Resume Builder 从固定 `zuno_base_sha` 的 Project、Architecture、Modules、Evidence、selected provenance 与既有简历风格生成 `01_simulated_resume.md`。

一条 Resume bullet 优先压缩一个真实工程故事：

```text
系统哪里会错
→ 我做了什么技术决策
→ 关键机制是什么
→ 有什么可信结果 / 证据
```

轮末 `10_next_resume_candidate.md` 只是下一轮候选稿。下一轮仍从新 main HEAD 重新校验，未实现 Target、未补 Evidence 或未证明 Ownership 的内容不能因为上一轮讨论过就升级成事实。

## 自动 Round 默认 Batch Duel

`CHATGPT_AUTO` 的自动校准默认使用 `BATCH_DUEL`。用户不逐题扮演候选人，Red 和 Blue 自己在 GitHub 上完成两波批量对攻：

```text
Frozen Resume + Frozen Red Plan
→ Red Wave 1 批量攻击
→ commit
→ Blue Wave 1 批量回答
→ commit
→ Red Wave 2 读取整批回答，针对薄弱点追杀
→ commit
→ Blue Wave 2 批量回答
→ commit
→ Red Evaluation
```

适应性没有消失，只是发生在 Wave 边界。Wave 2 Red 必须在 Blue Wave 1 提交以后生成；禁止把两波问题预写好再假装 answer-driven。

100-question `Pressure Suite` 仍然保留，但只做离线 coverage audit。正式 Batch Wave 1 默认只选约 20–40 个高信息量问题，Wave 2 再追约 10–30 个真实缺口，不把 100 问机械当成必答卷。

`02_red_questions.md` 保存 Red Interview Plan、`PRESSURE_SUITE` 与实际 Red waves；`03_blue_answers.md` 保存 Blue Wave 1 / Wave 2 batch answers。

## Live Interview 仍然保留，但不再是自动默认

当用户明确要求逐题真人面试时，使用 `LIVE_INTERVIEW`：

```text
SPOKEN_SEEDS
→ Red question commit
→ Blue answer commit
→ DYNAMIC FOLLOWUP
→ Red question commit
→ Blue answer commit
→ ...
```

Live 模式仍要求 one-question-one-intent、实时 listening 和信息增益驱动的 pivot。Batch Duel 的出现不降低真人面试模式的质量要求。

## Red Interview Skill 与 Blue Skill 分开

Red Interview Skill 由 `.agent/red-blue/attack-model.md` 约束。它负责攻击 Ownership、implementation、failure、evidence、Build/Buy 和 fundamentals，但不读取 Zuno docs 当隐藏答案。

Blue Candidate Skill 由 `.agent/red-blue/defense-model.md` 约束。它负责先回答问题，再按追问展开；区分本人和团队、Historical / Current / Target / Unknown；把技术名词落到机制，不把回答说成 README 或 Evidence memo。

两套 Skill 在 Round Init pin version。轮末可以修，但全部 `NEXT_ROUND_ONLY`，不能回头重算当前轮 verdict。

## Agent topology 不是架构身份

Red / Blue 可以挑战 Single Agent、Subgraph、parallel worker、Specialist Agent、Supervisor 或 Persistent Multi-Agent。流程不预设 Multi-Agent 更高级，也不保护当前 topology。

更合理的压力顺序是：

```text
最简单 Tool / Workflow
→ Subgraph
→ parallel worker
→ Specialist Agent
→ Persistent Multi-Agent
```

复杂度必须由独立 context / tool policy、并行任务、专业角色隔离、权限、恢复或可测质量收益推导。Domain、Knowledge、Memory、Effects、Security 等业务 Authority 不应随着 Agent topology 复制出第二套 truth。

如果 Generic Agent Host 已经能提供 workflow、MCP、checkpoint、generic memory/RAG 和 tracing，Zuno 应优先复用，并只保留法律材料/证据版本、专业 Capability 资格、Formal Domain admission、必要的 Effect/Security correctness 与法律 Evaluation。

## Red Evaluation 与 Blue Architecture Reflection 解决不同问题

Red Evaluation 只看到 Frozen Resume、实际 batch/live answers 与 Red Skill。它可以说“作为面试官我不信”，不能利用隐藏 Zuno 文档宣布 Architecture Truth。

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

Red 问到一个字段而 Blue 没答上，不等于 Architecture 缺对象。只有 Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身不成立，才进入 Architecture Revision。

## Workflow Retrospective 同时审四层

### Resume Builder

检查是否把功能清单当贡献、是否包装小样本数字、是否挑错技术故事。

### Red Skill

Batch 模式检查 Wave 1 是否选高信息量问题、Wave 2 是否真的从 Blue Wave 1 长出来；Live 模式检查 listening、one-intent、thread depth 和 pivot。

### Blue Skill

检查 Ownership、Historical / Current / Target mode switch、机制深度、Evidence boundary，以及 spoken answer 是否像候选人口语而不是 source report。

### Harness

检查 GitHub commit barrier、firewall、Batch/Live execution choice、Pressure Suite 是否被误当现场脚本，以及用户是否被错误要求逐题扮演候选人。

## Improvement Ledger：不允许发现问题却不知道改哪

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

每条还必须有 Owner、proposed change、evidence needed、risk、status 和 next-round retest。

常见路由：Red 问得差先改 Red/Harness；Blue 有材料但讲不清先改 Blue/Narrative；Target 正确但代码没落是 Implementation；有实现但缺 test/trace/benchmark 是 Evidence；只有责任和真值语义本身不成立才改 Architecture。

## Improvement Gate 与下一轮

默认 `USER_IMPROVEMENT_REVIEW=REQUIRED`。面试断点不能未经判断直接改 canonical Zuno Truth。

用户明确批准的 Skill / Harness / Docs / Architecture 改动可以在 Round 后半段落到 branch，但全部标记 `NEXT_ROUND_ONLY`。本轮 Red verdict 和 Blue Reflection 永远引用原 base SHA 与 pinned Skill，不重新计算。

## GitHub State Bus 与隔离模式

每个 stage、batch wave 或 live turn：

```text
read live Round branch HEAD
→ run only declared actor
→ write observable artifact
→ commit
→ next actor re-read
```

`CHATGPT_AUTO` 只能声明 `LOGICAL_GITHUB_MEDIATED`；严格 blind Red 使用独立 context 的 `AGENT_AUTO / PHYSICAL_CONTEXT_ISOLATION`。两种隔离模式都可运行 Batch Duel 或 Live Interview。

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

Round 的长期目标是逐轮收敛：**简历越来越像真实工程经历，Red 越来越能找到高价值断点，Blue 越来越能把历史贡献与当前架构讲清，文档与架构只在真正有缺陷时被修改。**
