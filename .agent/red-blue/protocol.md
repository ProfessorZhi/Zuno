# Red / Blue Execution Protocol

本协议定义 Red、Blue、Judge 和 Controller 如何运行。它适用于 ChatGPT 对攻、候选人真人模拟，以及多个 Agent 自主运行。

## 目标

Red / Blue 不是为了把答案“训练到看起来很完整”，而是验证：

> 候选人简历上的 Claim，是否能够仅依赖允许的项目文档和本人真实经历，经受真实大厂面试的连续追问。

如果 Blue 失败，首先记录 Gap。只有在 Round 结束后，才进入独立的 Documentation / Architecture / Evidence / Resume 修复任务。

## 四个角色

### Controller

Controller 只负责：

- 固定 Round manifest；
- 创建角色隔离上下文；
- 控制轮次顺序；
- 保存 transcript / judgment；
- 判断是否达到停止条件；
- Round 结束后归档。

Controller 不替 Red 想答案，也不替 Blue 搜资料。

### Red

Red 是 skeptical interviewer，不是老师。它的任务是：

1. 从精确简历快照抽取 3–5 条高风险 Claim；
2. 结合目标岗位和面试轮次选择 interviewer persona；
3. 使用 `attack-model.md` 连续下钻；
4. 必要时用真实面经语料校准“真实面试官会怎么追”，但不机械复述题库；
5. 发现矛盾时停留在同一条攻击链，直到 Claim 被澄清、证伪或信息耗尽。

Red 对候选人一次只展示一个主问题。内部 attack intent、expected evidence、counterexample 和 next drill 不向 Blue / 人类候选人展示。

### Blue

Blue 模拟候选人。它必须遵守 Closed-book：

- 使用与 Red 相同的精确简历快照；
- 只能读取 Round manifest 允许的 Zuno canonical docs；
- 回答项目 / 架构问题时优先使用 Project / Architecture / Module **Part A 的自然故事**；
- 当 Red 深挖 Contract、State、Concurrency、Recovery、Security、Persistence、Evidence 时，才继续使用 Part B / Part C / ADR / Evidence；
- 不读取面经、八股、外部标准答案、用户过去 QA 或 Red hidden context。

Blue 如果不知道，应明确说 Current / Target / Unknown 或“文档不足以支持”。禁止靠模型常识把 Zuno 未记录的事实补齐。

### Judge

Judge 不参与答题，只做审计：

- 判断 Blue 是否回答了 Red 真正验证的风险；
- 检查回答是否由简历和允许的 canonical docs 支持；
- 判断是表达问题、文档问题还是架构 / 证据问题；
- 决定 Red 应继续同链、换角度、还是结束该 Claim；
- 输出 Gap，但不生成“正确答案”给 Blue。

详细标准见 `judge.md`。

## Context Firewall

正式模式必须维护以下逻辑隔离：

```text
RED CONTEXT
  exact resume snapshot
  target role / JD / stage
  attack-model.md
  selected interview calibration material
  public/platform research when the attack explicitly tests Build/Buy

BLUE CONTEXT
  exact same resume snapshot
  AGENTS.md
  docs/project/
  docs/architecture/
  docs/modules/
  docs/decisions/
  docs/evidence/
  docs/governance/project-fact-provenance.md

JUDGE CONTEXT
  exact resume snapshot
  Red question + hidden attack intent
  Blue answer + source trace
  same allowed canonical docs as Blue
  judge.md
```

禁止信息流：

```text
Red interview corpus ─X→ Blue
Red hidden intent     ─X→ Blue
Judge diagnosis       ─X→ Blue during the same chain
Blue external search  ─X→ answer
Historical ideal QA   ─X→ Blue
```

单个 ChatGPT 对话无法提供密码学级上下文隔离，所以 `chatgpt-duel` 依赖程序性角色隔离；正式验收优先使用不同子 Agent / context window。

## Round 启动

Round 开始前必须固定：

1. Zuno base SHA；
2. 精确 resume snapshot：repository + commit SHA + path；
3. Target role / JD；
4. Interview stage；
5. Mode；
6. Red calibration mode；
7. Blue allowlist；
8. 预期时长或最大 Turn；
9. 主面试官画像和交叉画像。

不要用“最新简历”这种漂移引用。简历索引里标记为“待核验包装稿”的版本不得自动成为 Round 基线。

## Mode A — Human Candidate

```text
Red Agent → 用户本人回答 → Red follow-up
                         ↘ Judge（复盘时）
```

模拟中默认不展示评分、标准答案或攻击意图。用户说“结束 / 复盘”后 Judge 才输出报告。

## Mode B — ChatGPT Duel

```text
Controller
  → Red asks one question
  → Blue answers closed-book
  → Judge evaluates silently
  → Controller gives Judge decision only to Red
  → Red asks next follow-up
  → repeat
```

用户可以选择实时看到 Blue 答案，也可以只在 Round 结束后查看完整 transcript。Red 不应因为 Blue 第一次答到关键词就切题；要验证这个答案是否能承受下一层约束。

## Mode C — Autonomous Agent

至少维护三个独立角色上下文：Red、Blue、Judge。建议 Controller 使用状态机：

```text
INIT
→ CLAIM_MINING
→ SELECT_ATTACK
→ RED_ASK
→ BLUE_ANSWER
→ JUDGE
→ CONTINUE_CHAIN | NEXT_CLAIM | CLOSE
→ ARCHIVE
```

Autonomous 模式允许 Red 在开始前检索批准的 interview corpus，并生成一个**私有的 pressure model**；这个中间物不得暴露给 Blue。

Autonomous 模式不得自行：

- 修改 Zuno Architecture；
- 修改简历；
- 创建实现 PR；
- 用外部材料补齐 Blue；
- 把 Round Verdict 写成 Current Evidence。

## 一次 Turn

每个 Turn 内部至少记录：

```text
turn_id
claim_under_test
attack_angle
red_question
red_hidden_intent
expected_evidence
blue_answer
blue_source_trace
judge_verdict
judge_gap_type
next_action
```

对候选人只展示 `red_question`；是否展示 `blue_answer` 取决于 mode。

## 连续追问原则

Red 问完后先检查 Blue 的**回答形状**：

- 只有名词，没有机制 → 追输入 / 状态 / Owner / 接口；
- 有方案，没有原因 → 追约束 / baseline / alternative / cost；
- 说“我们” → 追个人 Ownership；
- 说“自研” → 追 Build / Buy / Extend / Defer；
- 说“支持恢复” → 注入 crash / timeout / duplicate / late result；
- 说“高并发 / 高性能” → 追负载模型、瓶颈、数据和测量；
- 说“效果更好” → 追 baseline、dataset、metric、ablation、置信区间或失败样本；
- 说“权限控制” → 追长期任务权限变化和 TOCTOU；
- 说“重试” → 追幂等、重复副作用和 Unknown outcome；
- Current / Target 混淆 → 要求重新分层。

具体攻击图见 `attack-model.md`。

## 停止条件

单个 Claim 在以下任一条件满足时结束：

- Blue 能稳定回答事实、原因、机制、故障、Trade-off、Evidence 和 Ownership；
- 已出现足够明确的 Gap，继续追问只会重复同一缺口；
- 允许文档本身没有更多信息；
- 问题已经越出目标岗位 / Round 范围。

整个 Round 在达到目标 Turn、时间预算、Claim 覆盖或连续两条高严重度 Gap 后可以结束。

## Round 结束

Round 结束后 Judge 输出：

- 面试官 persona；
- 被攻击的简历 Claim；
- 每条攻击链；
- PASS / PARTIAL / FAIL / UNSUPPORTED_CLAIM；
- 最危险 Gap；
- 30 秒 / 90 秒 / 3 分钟 interview extractability；
- 哪些 Gap 属于 Resume、Narrative、Docs、Architecture、Evidence、Ownership 或 Measurement；
- Retest 应使用的不同问法。

然后：

```text
raw Round → docs/maintenance/history/red-blue/
accepted Gap → independent fix task
fix merged → reread main
Red Retest with different wording
```

历史 Round 本身不拥有 Architecture Truth。