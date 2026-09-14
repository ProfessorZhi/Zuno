# Red / Blue Evaluation Rules

这一文件约束 Round 后半段四种彼此不同的判断：

1. **Red Evaluation**：真实面试官会不会接受候选人在实际对话中的回答；
2. **Blue Architecture Reflection**：回答暴露的问题属于简历、叙事、证据、实现、基础还是架构；
3. **Workflow Retrospective**：Resume Builder、Red Skill、Blue Skill 和 Harness 哪一层需要修；
4. **Improvement Synthesis**：每个 finding 最终由谁负责、改什么、下一轮怎样复测。

Red 不读 Zuno docs，因此不能宣布 Architecture Truth；Blue 有文档权限，也不能替候选人洗掉一次糟糕的现场回答。

## 1. Red Evaluation

Red Evaluation 读取：

```text
01_simulated_resume.md
frozen 02_red_questions.md
03_blue_answers.md 中实际发生的 Q/A
pinned attack-model.md
```

它不读取 Zuno canonical docs。

### Interview Verdict

`STRONG_PASS`：回答具体、可信、能落到本人决策、实现、失败与证据；继续追问主要为了扩展深度。

`PASS`：主线成立，仍有少量参数 / 边界 / 量化细节可以追，但不会怀疑 Claim 本身。

`PARTIAL`：方向大体正确，但自然追问后暴露明显缺口，例如只有架构没有状态 / 数据 / test，Ownership 模糊，或说优化却没有 baseline / bad case。

`FAIL`：回答与简历冲突、核心机制无法解释、明显夸大、基础错误，或连续追问后仍无法说明本人做过什么。

Red 可以说“作为面试官我不信”，不能说“Zuno 文档事实一定错误”。

## 2. 候选人评价维度

每条真正进入深挖的 thread 按 0–4 分评价：

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Ownership | 无法区分本人 / 团队 | 能说模块 | 能说个人决策、代码和未负责部分 |
| Business Causality | 只有口号 | 有场景 | 问题自然推导设计，能解释不做后果 |
| Implementation Depth | 只有框架名 | 能讲机制 | 能讲函数 / 状态 / 数据 / 异常 / test |
| Build / Buy | 不知道替代 | 知道方案 | 能说明 Adopt / Extend / Build / Delete |
| Failure & Recovery | 只说重试 | 能列失败 | 能处理并发、副作用、恢复 authority |
| Evidence | “效果很好” | 有测试或指标 | 有 baseline、bad case、范围和限制 |
| Fundamentals | 项目与基础脱节 | 原理正确 | 能落到网络 / DB / async / IR / algorithm |
| Communication | 堆术语 | 主线可跟 | 先答结论，再按追问自然展开 |

平均分不是目标；核心维度 0/1 必须显式暴露。

## 3. Blue Architecture Reflection

Blue Reflection 读取面试产物 + Zuno canonical docs / Evidence，把高价值断点分类为：

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

Blue Reflection 必须区分两种常见情况：

```text
材料里有，Blue 没讲清楚 -> 不自动算 DOC_GAP
材料里本来就缺关键因果 / failure / implementation explanation -> DOC/NARRATIVE_GAP
```

## 4. Source Audit

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

面试里回答得漂亮但缺来源支撑，仍记录 Evidence / Resume risk。

## 5. Workflow Retrospective

### Resume Builder

评价：

- bullet 是否在写真实工程问题，而不是功能列表；
- 是否挑到了最值得追问的技术决策；
- 是否用“100% / 提升 xx%”掩盖小样本；
- Ownership 动词是否太弱或太强；
- 简历是否给面试留出深挖空间。

### Red Skill

| Dimension | 目标 |
| --- | --- |
| Resume Grounding | Seed 能从简历自然产生 |
| Listening / Adaptation | 下一问真正使用上一答 |
| One-intent | 每次只问一个主要意图 |
| Thread Depth | 高价值线索自然追 3–6 层 |
| Pivot Judgment | 信息增益下降就换 thread |
| Technical Depth | 能追实现 / failure / evidence |
| Build/Buy | 在合适时机挑战重复造轮子 |
| Fundamentals | 能自然切到底层原理 |
| Interview Realism | 不像 Reviewer checklist / AI 原子化 |

### Blue Skill

| Dimension | 目标 |
| --- | --- |
| Directness | 先回答当前问题，不先念背景 |
| Ownership Clarity | 主动区分本人 / 团队 / 未负责 |
| Mechanism Depth | 技术名词能落到状态、数据、调用链、test |
| Problem Framing | 能说清原问题和为什么这样改 |
| Evidence Discipline | 数字有样本 / 指标 / scope；不制造完美结果 |
| Boundary Honesty | Pilot / Target / Unknown 不说大 |
| Failure Reasoning | 不把所有失败都归结为 retry |
| Conversational Quality | 像面试回答，不像文档摘要 |
| Follow-up Resilience | Red 再追一层还有真实细节 |

### Harness

检查：

- Red / Blue 是否真按 turn 交替；
- 每个问题提交后 Blue 才回答；
- Blue 回答提交后 Red 才看到；
- Red 是否泄漏 Zuno docs；
- Blue 是否提前看到 Red Evaluation；
- Pressure Suite 是否被误当现场脚本；
- 用户 Gate 是否只放在真正需要判断的位置。

## 6. Improvement Classification

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

- Red 问法机械、没听回答：`RED_SKILL_GAP`
- Red / Blue turn 顺序或 firewall 有问题：`HARNESS_GAP`
- Blue 有材料但表达失败：`BLUE_SKILL_GAP`
- Resume claim 选择或措辞有问题：`RESUME_GAP`
- 文档已有事实但缺连续故事：`NARRATIVE_GAP`
- 缺调用链 / failure / example / contract explanation：`DOC_GAP`
- 设计责任本身错误：`ARCHITECTURE_GAP`
- Target 正确但代码没落：`IMPLEMENTATION_GAP`
- 缺 test / trace / benchmark：`EVIDENCE_GAP`
- 个人归属无法证明：`OWNERSHIP_GAP`
- 候选人底层知识薄弱：`FUNDAMENTAL_GAP`

## 7. Improvement Apply Rule

只有用户批准的 ledger item 才能执行。

轮末修改 `.agent/red-blue/attack-model.md`、`defense-model.md`、协议、文档或架构时，必须标记 `NEXT_ROUND_ONLY`。这些变更不能反向改变本轮 Red Evaluation / Blue Reflection，不能回头重算当前轮 verdict。

Architecture change 继续遵守 Owner / ADR；Implementation gap 不能靠改文档伪装解决；Evidence gap 不能靠改简历变成“已验证”。

## 8. 下一轮 Resume Candidate

`10_next_resume_candidate.md` 根据已批准且已落地的改进生成。

它不是自动冻结简历。下一 Round 从新 main HEAD 重建 / 校验后，仍需 USER_RESUME_REVIEW。

未解决的 Implementation / Evidence / Ownership gap 必须使相应 Claim 保持原边界或降级，不能因为这一轮已经讨论过就升级。

## 9. 禁止行为

- Red 读取 Zuno docs 后按答案出题；
- Red 一次预写完整现场 follow-up 链，然后假装 answer-driven；
- Blue 在 Red question 尚未提交前预答；
- Blue 根据 Red Evaluation 重写同一轮回答；
- Workflow Retrospective 只审 Red 不审 Blue；
- Red 问崩了就改 Architecture；
- Blue 答崩了就删 Resume Claim；
- 一轮发现直接覆盖 canonical truth；
- 轮末改 Skill 后回头宣布本轮已通过新 Skill；
- 用下一版 Resume Candidate 替换本轮 Frozen Resume。

## 10. Round 结束标准

正常完成：

```text
Frozen Resume
→ Frozen Red Plan
→ Red ↔ Blue committed live turns
→ Red Evaluation
→ Blue Architecture Reflection
→ Resume/Red/Blue/Harness Retrospective
→ Improvement Ledger
→ USER_IMPROVEMENT_REVIEW
→ approved changes applied or explicitly deferred
→ Next Resume Candidate
→ archive / CI / merge
```

Round 成功不等于全部 PASS。一个高价值 FAIL 只要能被正确归因、形成真实改进并在下一轮复测，也属于有效进展。