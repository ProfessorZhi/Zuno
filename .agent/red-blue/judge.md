# Red / Blue Evaluation Rules

这一文件约束 Round 后半段三个不同判断：

1. **Red Evaluation**：真实面试官会不会接受候选人在实际对话中的回答；
2. **Blue Architecture Reflection**：回答暴露的问题属于简历、叙事、证据、实现、基础还是架构；
3. **Workflow Retrospective**：Red 本身是否像一个会听回答、会临场追问的真实面试官。

Red 不读 Zuno docs，因此不能宣布 Architecture Truth；Blue 有文档权限，也不能替候选人洗掉一次糟糕的面试回答。

## 1. Red Evaluation

Red Evaluation 读取：

```text
01_simulated_resume.md
frozen 02_red_questions.md interview plan
actual observable question / answer exchanges
03_blue_answers.md
attack-model.md
```

100 问 Pressure Suite 没有被现场逐题执行，不构成“漏答”。评价对象是实际发生的 thread。

### Interview Verdict

#### STRONG_PASS

回答具体、可信、能落到本人工作。核心 Claim 在自然追问中经得住实现、失败、替代方案和 Evidence 检查；继续追问主要为了扩展深度。

#### PASS

主线成立，仍有少量参数 / 边界 / 量化细节可以继续问，但不会让面试官怀疑 Claim 本身。

#### PARTIAL

方向大体正确，但实际 follow-up 暴露明显缺口，例如只有架构没有函数/状态/数据、说“我们”但 Ownership 不清、说优化却没有 baseline/bad case、只会 Retry、或回答明显像背材料。

#### FAIL

回答与简历直接冲突、核心机制无法解释、明显夸大、基础原理错误，或连续自然追问后仍无法说明本人做过什么。

Red 可以说“我作为面试官不信”，不能说“Zuno 文档事实一定错误”。

## 2. 候选人评价维度

每条真正进入深挖的主 Thread 按 0–4 分评价：

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Ownership | 无法区分本人 / 团队 | 能说模块 | 能说个人决策、代码和未负责部分 |
| Business Causality | 只有产品口号 | 有场景但弱因果 | 约束自然推导设计，能解释不做后果 |
| Implementation Depth | 只有框架名 | 能讲机制 | 能讲函数 / 状态 / 数据 / 异常 / test |
| Build / Buy | 不知道替代 | 知道但比较弱 | 能说明 Adopt / Extend / Build / Delete |
| Failure & Recovery | 只说重试 | 能列失败 | 能处理并发、副作用、恢复 authority |
| Evidence | “效果很好” | 有测试或指标 | 有 baseline、bad case、范围和限制 |
| Fundamentals | 项目与基础脱节 | 原理正确 | 能从项目或岗位场景落到底层机制 |
| Communication | 堆术语 | 主线可跟 | 能根据追问层次自然展开和收束 |

平均分不是目标；核心维度 0/1 必须显式暴露。

## 3. Blue Architecture Reflection

Blue Reflection 读取面试产物 + Zuno canonical docs / Evidence，把高价值断点分类为：

- `SIMULATED_RESUME_GAP`：简历 Claim 太强、太弱、太模糊或混淆团队/Target/个人成果；
- `NARRATIVE_GAP`：事实与设计存在，但文档不能让候选人自然讲清；
- `DOC_GAP`：缺调用链、示例、故障、术语解释或入口；
- `ARCHITECTURE_GAP`：Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身不成立；
- `IMPLEMENTATION_GAP`：Target 清楚但 Current 没实现或违反 Target；
- `EVIDENCE_GAP`：历史或实现可能存在，但缺 test/trace/benchmark/Pilot material；
- `OWNERSHIP_GAP`：无法支持本人实现范围；
- `FUNDAMENTAL_GAP`：候选人基础训练问题；
- `NO_ZUNO_CHANGE`：回答已经足够，或 Red 本身的问题不应驱动 Zuno 修改。

只有 `ARCHITECTURE_GAP` 才直接建议 Architecture Revision。

## 4. Source Audit

Blue Reflection 重新核对强 Claim 的来源层：

```text
resume-only
project history
architecture target
module target
current evidence
personal provenance
unknown
```

面试里回答得漂亮但缺 Zuno 来源支撑，仍记录 Evidence / Resume risk。

## 5. Workflow Retrospective：专门审 Red

新版 Retrospective 不只看“题目本身对不对”，还检查对话行为：

| Dimension | 目标 |
| --- | --- |
| Resume Grounding | Seed 能从简历自然产生 |
| Listening / Adaptation | 下一问真正使用上一答的信息 |
| One-intent Questions | 表面问题简洁，不把 rubric 拼成复合问 |
| Thread Depth | 同一有价值线索可以自然连续追 3–6 轮 |
| Pivot Judgment | 信息增益下降时及时换线程 |
| Technical Depth | 追到实现 / 故障 / Evidence，而非只问 Why |
| Build/Buy Skepticism | 在合适时机攻击重复造轮子 |
| Failure Pressure | 故障注入与当前 thread 有因果关系 |
| Fundamentals | 能自然切到底层或岗位基础 |
| Interview Realism | 像真人交流，不像 Reviewer checklist / AI 原子化 |
| User Alignment | 用户是否认可这一轮 Red |

Pressure Suite 的覆盖度单独评价，不与 Live Interview realism 混为一谈。

用户反馈优先级最高。用户说“问题不够人味”时，不能通过把每题改成口语词来解决；必须检查 conversation policy、follow-up selection、thread switching 和问题粒度。

## 6. Red 自身的失败模式

以下行为直接降低 Interview Realism：

- 候选人还没回答，就把一条完整攻击树一次性写进问题；
- 每题都要求背景 + 机制 + test + metric + trade-off；
- 上一答出现了一个值得追的异常点，但 Red 无视它继续按预写题号走；
- 连续拆原子细节却没有新的判断价值；
- 为了覆盖 Resume bullet 平均分配现场时间；
- 现场把 Claim label、risk、Kill Switch、rubric 念给候选人；
- 候选人明确不是 Owner 后仍继续十几道源码题；
- 把 Pressure Suite 的完整度误当成真人面试质量。

## 7. 禁止行为

- Red 读取 Zuno docs 后按答案出题；
- Blue 根据 Red 评分修改同一批回答再让 Red 重判；
- Red Evaluation 使用 hidden Zuno source support；
- Blue Reflection 把所有面试断点升级成 Architecture Gap；
- Workflow Retrospective 只评价 Blue、不评价 Red；
- 因一轮得分高宣布 Skill 已验证；
- 在同一 Round 中修改 canonical Zuno Truth 后继续宣称同一版本通过。

## 8. Round 结束标准

正常完成的 Round 是：

```text
模拟简历冻结
→ Red Interview Plan / Pressure Suite
→ USER_RED_REVIEW（若 REQUIRED）
→ Live answer-driven interview / Blue answers
→ Red Evaluation based on actual exchanges
→ Blue Architecture Reflection
→ Workflow Retrospective
→ User Feedback / Archive
```

如果用户在 `USER_RED_REVIEW` 发现 Red Skill 本身存在结构性缺陷，该 Round 可以 `SUPERSEDED`。先独立修改 Skill，再用新 Skill 开新 Round；失败版本保留为校准证据。
