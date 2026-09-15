# Zuno Red / Blue Interview Review

`docs/red-blue/` 用来持续验证五件事：当前 Zuno 能否压缩成可信简历；盲测面试官会怎样攻击；候选人的回答能否经住两轮深挖；这些压力是否暴露真实架构缺陷；Red / Blue / Harness 自己的思维框架是否也需要修改。

Red / Blue 不拥有 Project History、Target Architecture、Current Evidence 或 Personal Ownership。它制造压力、暴露断点、正确归因，再把改进送回真正的 Owner。

## 正式 Round 的主线

自动校准 Round 默认使用：

```text
main@固定 SHA
→ Build / Review / Freeze Resume
→ Red Wave 1：100 题
→ Blue Wave 1：100 答 + 封存架构初诊
→ Red Wave 2：评价 Blue 1 + 100 个针对性追问
→ Blue Wave 2：100 答 + 封存架构复诊
→ Red Final Evaluation
→ Blue Final Architecture Reflection
→ Controller Workflow Retrospective
→ Improvement Ledger + Round Report
→ User Improvement Gate
→ Apply approved architecture / docs / skill / implementation changes
→ Next Resume Candidate
→ archive / merge
→ 新 main HEAD
→ 下一轮
```

一轮高分不是目标。更重要的是把“候选人不会讲”“证据不够”“文档没解释”“实现没落”“架构责任本身错了”分开。

## Resume-first

每轮开始由 Resume Builder 从固定 `zuno_base_sha` 的 Project、Architecture、Modules、Evidence、selected provenance 与既有简历风格生成 `01_simulated_resume.md`。

好的 Resume bullet 压缩一个真实工程故事：

```text
系统哪里会错
→ 我做了什么技术决策
→ 关键机制是什么
→ 有什么可信结果 / 证据
```

Resume Freeze 后，本轮所有攻击都针对同一版本。

## Red Wave 1：100 题

第一波 Red 只看到简历、岗位和 Attack Skill。它不知道 Zuno 文档里的“标准答案”。

100 题不是为了覆盖 100 个知识点，而是为了对少数高价值 Claim 做纵深压力：Ownership、实现、状态、失败、Evidence、Build/Buy、Fundamentals 和架构替代方案。

完成后默认只把 `02_red_questions.md` 链接发给用户。

## Blue Wave 1：回答与架构初诊分开

Blue 对这 100 题逐题回答，写入 `03_blue_answers.md`。

同一阶段还会写 `03_blue_architecture_notes.md`，记录：

- 哪些问题可能只是回答没讲清；
- 哪些是 Docs / Evidence / Implementation gap；
- 哪些可能真的是 Architecture gap；
- 当前方案是否应该保留、简化、替换或删除。

但这个架构初诊 **Red 看不到**。

如果 Red 2 看到它，就会拿 canonical knowledge 追问，盲测失效。

完成后默认只把 `03_blue_answers.md` 链接发给用户。

## Red Wave 2：评价 Blue 1，再追 100 题

第二波 Red 只读取第一波可观察 Q/A。

它先写一段 Blue 1 blind evaluation：哪些已经可信、哪些还薄、哪些问题第一波问偏了、哪些回答自己暴露了更深风险。

然后再生成新的 100 题。

例如：

```text
Blue 1：MCP user config 是 call-time lookup
→ Red 2：并发隔离？ConfigVersion？retry 用哪版？

Blue 1：GraphRAG baseline-preserving
→ Red 2：threshold 为什么是 6？tie-break？ablation？latency？kill gate？

Blue 1：Memory 只读 APPROVED
→ Red 2：谁有 approval authority？能不能 bypass？撤销后怎么办？

Blue 1：Multi-Agent 是可选
→ Red 2：Tool / Subgraph / Specialist 的边界？shared state？late result？谁写 Domain？
```

完成后默认只把 `04_red_wave2_review_and_questions.md` 链接发给用户。

## Blue Wave 2：再答 100 题

Blue 2 读取 Red 2 的公开评价和追问，再逐题回答 100 题。

为了防止自己给自己 coaching，Blue 2 的 Candidate answer generation 不读取 Wave 1 的封存 architecture notes。

回答完成以后再生成第二份封存架构复诊。

完成后默认只把 `04_blue_wave2_answers.md` 链接发给用户。

## Red Final 与 Blue Final 做不同的事

Red Final 继续 blind。它只看简历和两轮可观察 Q/A，判断候选人是否可信、Blue 2 是真正解释还是话术补洞，以及哪些 Resume Claim 应保留、降级或删除。

Blue Final Architecture Reflection 才重新读取 canonical docs / Evidence 和两份架构初诊，判断：

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

Architecture Gap 的门槛很高：Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身有问题才算。

## 架构可以被推翻

当前九模块、Single Controller、单 Agent、Native Runtime、GraphRAG、Memory、Persistent Multi-Agent 都不是不可变答案。

真正的架构反思要从现实失败出发：

```text
问题是什么
→ 最简单方案是什么
→ 简单方案哪里失败
→ 当前方案哪里失败
→ 新方案解决什么
→ 增加什么成本
→ 什么测量结果出现时应该删掉它
```

如果 Tool 足够，就不拆 Agent；如果 Subgraph 足够，就不做 Persistent Multi-Agent；如果 Generic Host + Zuno Backend 已经够，就不为了架构图保留自研 Runtime。

## Controller 还要审 Red / Blue 自己

Blue Final 后不会直接改架构。Controller 先完成 `06_workflow_retrospective.md`。

它审五层：

### Resume Builder

技术故事选得对不对；数字是否包装；Ownership 是否准确。

### Red Thinking Framework

Red 1 的 100 题有没有纵深；Red 2 是否真的理解 Blue 1；blind evaluation 是否公平；是否把 Multi-Agent 当默认高级答案；是否出现 Reviewer checklist 式机械攻击。

### Blue Candidate Framework

是否正确区分 Historical Ownership / Current System / Target Design / Open Design / Fundamental；有材料是否讲清；没材料是否乱补；是否只会用 Unknown 防守。

### Blue Architecture Framework

是否从 failure 推导；是否尊重简单方案；是否把回答缺口误判成架构缺陷；是否说明成本、退出条件和 Measurement Needed。

### Harness

是否真正保持 100/100/100/100；架构 notes 是否对 Red 封存；commit barrier、base SHA、Skill pinning 和 Batch Checkpoint 是否正确。

## Improvement Ledger 与 Round Report

`09_improvement_ledger.md` 给每条 finding 一个 primary owner。

`09_round_report.md` 则是给用户看的完整总结：

```text
Red 1 打出了什么
Blue 1 暴露了什么
Red 2 怎么追杀
Blue 2 有没有顶住
候选人最终评价
真正的架构缺陷
Red / Blue 思维框架缺陷
Harness 缺陷
应该改什么
不应该改什么
下一轮复测什么
```

用户批准后才真正修改 canonical Architecture、Docs、Skill 或 Implementation plan。

## 改完架构以后再生成下一轮简历

批准的改动落地并验证以后生成 `10_next_resume_candidate.md`。

未实现的 Target、未补的 Evidence、未恢复的 Personal Ownership 不能因为“我们讨论过”就升级到简历。

下一 Round 从新的 exact main HEAD 重新开始，并重新经过 USER_RESUME_REVIEW。

## GitHub State Bus

每个 stage：

```text
read live Round branch HEAD
→ run only declared actor
→ write observable artifact
→ commit
→ next actor re-read
```

`CHATGPT_AUTO` 只能声明 `LOGICAL_GITHUB_MEDIATED`；严格 blind Red 要使用独立 context 的 `AGENT_AUTO / PHYSICAL_CONTEXT_ISOLATION`。

## Core Round Artifacts

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

BATCH_DUEL 额外保存：

```text
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
09_round_report.md
```

Round 的长期目标是：**简历越来越可信，Red 越来越会攻，Blue 越来越会答也越来越会审架构，Harness 越来越少制造假信号，而 Zuno 架构只在真实约束与证据支持时增加复杂度。**