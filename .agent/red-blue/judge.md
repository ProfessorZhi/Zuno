# Red / Blue Evaluation Rules

这一文件约束一轮中五种彼此不同的判断：

1. **Red Wave 2 Blind Review**：第一轮 100 答暴露了什么，下一批 100 题为什么这样追；
2. **Red Final Evaluation**：两轮 200 题以后，真实面试官会不会接受候选人；
3. **Blue Architecture Reflection**：回答压力对应的 Resume / Docs / Architecture / Implementation / Evidence 缺口是什么；
4. **Workflow Retrospective**：Resume Builder、Red 思维框架、Blue 思维框架、Harness 哪一层需要修；
5. **Improvement Synthesis**：每个 finding 由谁负责、改什么、下一轮怎样复测。

Red 不读 Zuno docs，因此不能宣布 Architecture Truth。Blue 有文档权限，也不能利用架构诊断替候选人重写已经发生的回答。

## 1. Red Wave 2 Blind Review

输入：

```text
Frozen Resume
Red Wave 1 100 questions
Blue Wave 1 100 answers
pinned attack-model.md
```

禁止读取：

```text
Blue architecture notes
Zuno docs / source / Evidence
hidden source trace
```

输出在 `04_red_wave2_review_and_questions.md` 的前半部分。

Blind Review 必须回答：

- 哪些 Claim 已经可信；
- 哪些回答只到名词 / 框架层；
- 哪些 Ownership 仍模糊；
- 哪些 precise number / Pilot / benchmark 值得怀疑；
- 哪些 failure / concurrency / state / authority 被 Blue 自己暴露；
- 哪些第一波问题前提有误；
- 哪些 Thread 应降低权重；
- 下一批为什么要追这些 handle。

这不是最终 verdict。后半部分必须生成新的 **恰好 100 个** targeted follow-ups。

## 2. Red Final Evaluation

Red Final Evaluation 读取：

```text
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
pinned attack-model.md
```

仍然不读取 canonical docs 或任何 Blue architecture notes。

### Interview Verdict

`STRONG_PASS`：两轮都能落到本人决策、实现、失败、证据与底层原理；第二轮主要扩展设计深度。

`PASS`：主线成立，仍有少量参数 / Evidence /边界问题，但不会怀疑主要 Claim。

`PARTIAL`：Blue 1 暴露明显缺口，Blue 2 只部分补足；或者只有设计概念，没有状态 / 数据 / test / Ownership。

`FAIL`：回答与简历冲突、核心机制无法解释、明显夸大、基础错误，或第二轮仍无法说明本人做过什么。

### 两轮特有检查

Red Final 必须比较 Blue 1 与 Blue 2：

- Blue 2 是否真正回答了 Red 2 的追问；
- 是否只是换了更漂亮的话术；
- 是否突然出现第一轮完全没有依据的新实现细节；
- 是否承认并保留 Unknown；
- 是否能把开放设计题与历史事实分开。

Red 可以说“作为面试官我仍不信”，不能说“Zuno 架构事实一定错误”。

## 3. 候选人评价维度

每条真正进入深挖的 thread 按 0–4 分评价：

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Ownership | 无法区分本人 / 团队 | 能说模块 | 能说个人决策、代码和未负责部分 |
| Business Causality | 只有口号 | 有场景 | 问题自然推导设计，能解释不做后果 |
| Implementation Depth | 只有框架名 | 能讲机制 | 能讲函数 / 状态 / 数据 /异常 / test |
| Build / Buy | 不知道替代 | 知道方案 | 能说明 Adopt / Extend / Build / Delete |
| Failure & Recovery | 只说重试 | 能列失败 | 能处理并发、副作用、版本、恢复 authority |
| Evidence | “效果很好” | 有测试或指标 | 有 baseline、bad case、范围和限制 |
| Fundamentals | 项目与基础脱节 | 原理正确 | 能落到 network / DB / async / IR / algorithm |
| Communication | 堆术语 | 主线可跟 | 先答结论，再自然展开 |

平均分不是目标；核心维度 0/1 必须显式暴露。

## 4. Blue Architecture Reflection

Blue Architecture Reflection 分两层。

### Provisional Architecture Notes

Blue Wave 1 和 Wave 2 各自生成封存 notes：

```text
03_blue_architecture_notes.md
04_blue_wave2_architecture_notes.md
```

它们对 Red 不可见，只用于记录当波压力暴露的可能系统问题，防止两轮结束后丢失上下文。

### Final Architecture Reflection

Red Final Evaluation 之后，Blue 读取两份 provisional notes + 全部面试产物 + canonical Zuno docs / Evidence，生成 `05_blue_architecture_reflection.md`。

分类：

- `SIMULATED_RESUME_GAP`
- `NARRATIVE_GAP`
- `DOC_GAP`
- `ARCHITECTURE_GAP`
- `IMPLEMENTATION_GAP`
- `EVIDENCE_GAP`
- `OWNERSHIP_GAP`
- `FUNDAMENTAL_GAP`
- `NO_ZUNO_CHANGE`

只有 Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身不成立，才直接建议 Architecture Revision。

Blue Reflection 必须区分：

```text
材料里有，Blue 没讲清楚
→ BLUE_SKILL_GAP / NARRATIVE_GAP

材料本来就缺 test / benchmark
→ EVIDENCE_GAP

Target 正确但 code 未落
→ IMPLEMENTATION_GAP

设计责任 / Authority 本身错
→ ARCHITECTURE_GAP
```

## 5. Architecture Revision 的评审框架

任何 Architecture change 必须回答：

```text
现实问题是什么？
最简单方案是什么？
简单方案哪里失效？
当前设计哪里失效？
候选新设计解决什么？
增加什么成本？
Build / Buy / Extend / Defer 如何选择？
Current / Target / Evidence / Unknown 各是什么？
什么测量结果出现时应该删除这个复杂度？
下一轮如何复测？
```

Multi-Agent、GraphRAG、Reflection、Native Runtime、独立 Service 都必须遵守这套规则。

## 6. Source Audit

强 Claim 重新核对来源层：

```text
resume-only
project history
architecture target
module target
current evidence
personal provenance
unknown
```

面试回答很漂亮但没有来源支撑，仍记录 Evidence / Resume risk。

## 7. Workflow Retrospective

`06_workflow_retrospective.md` 是 Controller 对整个模拟系统的元审查。

### Resume Builder

评价：

- bullet 是否在写真实工程问题，而不是功能列表；
- 是否挑到了最值得连续追问的技术决策；
- 是否用漂亮数字掩盖小样本；
- Ownership 动词是否太弱或太强；
- 简历是否给两轮 100 题留下真实深度。

### Red Thinking Framework

| Dimension | 目标 |
| --- | --- |
| Resume Grounding | Red 1 的问题从简历自然产生 |
| Blindness | 没用 canonical Zuno 隐藏答案 |
| Thread Depth | 100 题围绕高价值 Thread 深挖，而非平均扫点 |
| One-intent | 每题一个主要意图 |
| Blue-1 Evaluation | Red 2 先公平评价第一批回答 |
| Adaptation | Red 2 的 100 题真正从 Blue 1 handle 产生 |
| Technical Depth | 能追实现 / failure / evidence / fundamentals |
| Build/Buy | 能挑战重复造轮子和删除条件 |
| Architecture Neutrality | 不把 Multi-Agent 等当默认正确答案 |
| Realism | 像高级工程面试官，不像 Reviewer checklist |

必须审“Red 是怎么想的”，不只数题目质量。

### Blue Thinking Framework

分两部分。

#### Candidate Answer Framework

- Directness；
- Ownership Clarity；
- Historical / Current / Target / Open Design / Fundamental 模式选择；
- Mechanism Depth；
- Evidence Discipline；
- Boundary Honesty；
- Failure Reasoning；
- Follow-up Resilience。

#### Architecture Diagnosis Framework

- 是否从现实 failure 推导；
- 是否尊重最简单方案；
- 是否把回答缺口误判为 Architecture Gap；
- 是否清楚 Owner / Authority；
- 是否给复杂度成本与退出条件；
- 是否允许删除已实现复杂度；
- 是否把 framework capability 与 Zuno Authority 分开。

### Harness

检查：

- Red Wave 1 是否恰好 100 题；
- Blue Wave 1 是否恰好 100 答；
- Red Wave 2 是否先评价 Blue 1 再生成恰好 100 题；
- Blue Wave 2 是否恰好 100 答；
- Red 2 / Red Final 是否看不到 Blue architecture notes；
- Blue 2 是否没有用 Wave 1 architecture notes 给 Candidate answer coaching；
- 每个 stage 是否 commit-then-reread；
- Batch Checkpoint 是否只给用户链接，不要求用户逐题作答；
- 用户 Gate 是否只放在真正的决策点。

Workflow Retrospective 不能修改本轮答案或本轮 verdict。

## 8. Improvement Classification

`09_improvement_ledger.md` 使用以下 primary class：

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

不要用一个问题同时逃避 Owner。每条 finding 必须有 primary owner；可以记录 secondary effect。

### 常见路由

- Red 1/2 问法机械：`RED_SKILL_GAP`
- batch / firewall / commit 顺序错误：`HARNESS_GAP`
- Blue 有材料但表达失败：`BLUE_SKILL_GAP`
- Resume claim 选择或措辞有问题：`RESUME_GAP`
- 文档已有事实但缺连续故事：`NARRATIVE_GAP`
- 缺调用链 / failure / contract explanation：`DOC_GAP`
- 设计责任本身错误：`ARCHITECTURE_GAP`
- Target 正确但 code 未落：`IMPLEMENTATION_GAP`
- 缺 test / trace / benchmark：`EVIDENCE_GAP`
- 个人归属无法证明：`OWNERSHIP_GAP`
- 候选人底层知识薄弱：`FUNDAMENTAL_GAP`

## 9. Round Report

在用户 Improvement Gate 前生成 `09_round_report.md`。

它必须用人能连续阅读的方式汇报：

```text
Red 1 打了什么
Blue 1 暴露什么
Red 2 怎么针对追杀
Blue 2 是否顶住
最终候选人评价
真正的架构缺陷
Red/Blue 思维框架缺陷
Harness 缺陷
建议改什么
不建议改什么
下一轮复测什么
```

## 10. Improvement Apply Rule

只有用户批准的 ledger item 才能执行。

轮末修改 `.agent/red-blue/attack-model.md`、`defense-model.md`、协议、文档、架构或实现计划时，必须标记 `NEXT_ROUND_ONLY`。这些变更不能反向改变本轮 Red Evaluation / Blue Reflection，不能回头重算当前轮 verdict。

Architecture change 继续遵守 Owner / ADR；Implementation gap 不能靠改文档伪装解决；Evidence gap 不能靠改简历变成“已验证”。

## 11. 下一轮 Resume Candidate

`10_next_resume_candidate.md` 根据已批准且已落地的改进生成。

它不是自动冻结简历。下一 Round 从新 main HEAD 重建 / 校验后，仍需 USER_RESUME_REVIEW。

未解决的 Implementation / Evidence / Ownership gap 必须使相应 Claim 保持原边界或降级。

## 12. 禁止行为

- Red 读取 Zuno docs 后按答案出题；
- Red 2 读取 Blue architecture notes；
- Red Final 读取 canonical docs；
- Red 2 不评价 Blue 1 就直接套第二份题库；
- Blue 跳过 100 题中的部分问题；
- Blue 2 读取 Wave 1 architecture notes 给自己 coaching；
- Blue 根据 Red Final Evaluation 重写已经发生的回答；
- Workflow Retrospective 只审 Red 不审 Blue；
- Red 问崩了就改 Architecture；
- Blue 答崩了就删 Resume Claim；
- 一轮 finding 直接覆盖 canonical truth；
- 轮末改 Skill 后回头宣布本轮已通过新 Skill；
- 用下一版 Resume Candidate 替换本轮 Frozen Resume。

## 13. Round 结束标准

正常完成：

```text
Frozen Resume
→ Red Wave 1: 100
→ Blue Wave 1: 100 + sealed architecture notes
→ Red Wave 2: Blue-1 blind evaluation + 100
→ Blue Wave 2: 100 + sealed architecture notes
→ Red Final Evaluation
→ Blue Final Architecture Reflection
→ Resume / Red / Blue / Harness Retrospective
→ Improvement Ledger + Round Report
→ USER_IMPROVEMENT_REVIEW
→ approved changes applied or explicitly deferred
→ Next Resume Candidate
→ archive / CI / merge
```

Round 成功不等于全部 PASS。一个高价值 FAIL 只要能被正确归因、形成真实架构或工程改进并在下一轮复测，也属于有效进展。