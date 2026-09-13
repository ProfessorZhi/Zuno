# Red / Blue Evaluation Rules

这一文件约束 Round 后半段的两个不同判断：

1. **Red Evaluation**：真实面试官会不会接受候选人的回答；
2. **Blue Architecture Reflection**：回答暴露的问题究竟属于简历、叙事、证据、实现、基础知识还是架构本身。

两者不能合并。Red 不读 Zuno docs，因此它不能宣布 Architecture Truth；Blue 有文档权限，但不能因为知道“正确答案”就替候选人洗掉一次糟糕的面试回答。

## 1. Red Evaluation

Red 只读取：

```text
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
attack-model.md
```

### Interview Verdict

#### STRONG_PASS

回答具体、可信、能落到本人工作，核心 Claim 经得住实现、失败、替代方案和 Evidence 追问；继续追问主要是扩展深度。

#### PASS

主线成立，仍有少量参数 / 边界 / 量化细节可继续问，但不会让面试官怀疑 Claim 本身。

#### PARTIAL

方向大体正确，但真实面试官会继续追穿，例如：

- 只有架构，没有函数 / 状态 / 数据；
- 只有实现，没有业务原因；
- 说“我们”但个人 Ownership 不清；
- 说“优化”却无 baseline / bad case；
- 说“恢复”但只会 Retry；
- 对 Build/Buy 没调查；
- 回答明显像背文档，缺少做过事情的细节。

#### FAIL

回答与简历直接冲突、核心机制无法解释、明显夸大、基础原理错误，或者多次追问后仍无法说明自己做过什么。

Red 可以说“我作为面试官不信”，但不能说“Zuno 文档事实一定错误”。

## 2. Red 评价维度

每条主 Claim 按 0–4 分评价：

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Ownership | 无法区分本人 / 团队 | 能说模块 | 能说个人决策、代码和未负责部分 |
| Business Causality | 只有产品口号 | 有场景但弱因果 | 约束自然推导设计，能解释不做后果 |
| Implementation Depth | 只有框架名 | 能讲机制 | 能讲函数 / 状态 / 数据 / 异常 / test |
| Build / Buy | 不知道替代 | 知道但比较弱 | 能说明 Adopt / Extend / Build / Delete |
| Failure & Recovery | 只说重试 | 能列失败 | 能处理版本、并发、副作用、恢复 authority |
| Evidence | “效果很好” | 有测试或指标 | 有 baseline、bad case、范围和限制 |
| Fundamentals | 项目与基础脱节 | 原理正确 | 能从项目自然下钻到底层并回到设计 |
| Communication | 堆术语 | 主线可跟 | 30s/90s/3m 都能根据深度组织 |

平均分不是目标；任何核心维度 0/1 都应该在 `04_red_evaluation.md` 中显式暴露。

## 3. Blue Architecture Reflection

Blue Reflection 读取所有面试产物 + Zuno canonical docs / Evidence，然后给每个高价值断点分类。

### `SIMULATED_RESUME_GAP`

模拟简历本身写得太强、太弱、太模糊或错误组合了团队 / Target / 个人成果。

### `NARRATIVE_GAP`

架构和证据存在，但 Project / Architecture / Module Part A 不能让候选人自然回答。

### `DOC_GAP`

设计存在，但缺少必要的调用链、示例、故障、术语解释或入口。

### `ARCHITECTURE_GAP`

Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身不成立。只有这种情况才建议改架构。

### `IMPLEMENTATION_GAP`

Target 清楚，但 Current 没实现或行为违反 Target。

### `EVIDENCE_GAP`

实现 / 历史可能存在，但当前没有代码、test、trace、benchmark、Pilot material 等足够证据。

### `OWNERSHIP_GAP`

无法支持“这是本人做的”或无法分清导师、团队、Framework 与个人。

### `FUNDAMENTAL_GAP`

这是候选人基础知识训练问题，不应为了面试修 Zuno 架构。

### `NO_ZUNO_CHANGE`

问题合理，Blue 回答本身已经足够；或者 Red 问题质量差，不应驱动项目修改。

## 4. Source Audit

Blue Reflection 必须重新核对回答中的强 Claim：

```text
resume-only
project history
architecture target
module target
current evidence
personal provenance
unknown
```

如果回答在面试中很漂亮，但只能靠模型常识而非 Zuno 来源支持，应记录 Evidence / Resume risk；不要因为 Red 没权限发现就忽略。

## 5. Workflow Retrospective：专门审 Red

Round 结束后必须给 Red 本身打分，至少包括：

| Dimension | 目标 |
| --- | --- |
| Resume Grounding | 问题能从简历自然产生 |
| Technical Depth | 不停留在 Why / 名词 |
| Full-chain Coverage | 业务→实现→失败→证据→基础形成完整链 |
| Non-duplication | 100 问不是同义改写 |
| Build/Buy Skepticism | 真正攻击重复造轮子 |
| Failure Pressure | 有真实 crash / timeout / concurrency / security 反例 |
| Fundamentals Drilldown | 能从项目自然追到底层 |
| Interview Realism | 像真实一二三面，不像架构 Reviewer checklist |
| Information Gain | 每个问题都有新的判别价值 |
| User Alignment | 用户评价是否认可问题质量 |

用户反馈优先级最高。

如果用户明确评价“这批问题没含金量”，Workflow Retrospective 不能用高 PASS 率为 Red 辩护；必须找出是 Resume 输入、Skill、问题预算、Persona 还是角色泄漏导致的问题。

## 6. 禁止行为

- Red 读取 Zuno docs 后按答案出题；
- Blue 根据 Red 的评分修改同一批回答再让 Red 重判；
- Red Evaluation 使用 hidden Zuno source support；
- Blue Reflection 把所有面试断点都升级成 Architecture Gap；
- Workflow Retrospective 只评价 Blue、不评价 Red；
- 因为一轮得分高就宣布 Skill 已验证；
- 在同一 Round 中直接修 canonical docs / Resume / Skill 后再宣布通过。

## 7. Round 结束标准

一轮固定完成：

```text
模拟简历冻结
→ Red 100 问
→ Blue 100 答
→ Red Evaluation
→ Blue Architecture Reflection
→ Workflow Retrospective
→ User Feedback 归档
```

之后关闭。任何修复和 retest 都创建新 Round。