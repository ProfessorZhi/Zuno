# Red / Blue Judge

Judge 的职责是把“答得不好”分解成真正可修复的 Gap，而不是给 Blue 写标准答案。

## Verdict

每个 Turn 至少给一个 verdict：

### PASS

Blue 回答了当前问题的核心风险，且关键 Claim 能由 resume + allowed canonical docs / evidence 支持。允许表达风格不完美，但不能靠猜测补关键事实。

### PARTIAL

方向正确，但存在一个会被真实面试官继续追穿的缺口，例如：

- 只给机制，没有 why / alternative；
- 能说 Owner，但说不清 crash / recovery；
- Part A 可以回答主问题，但下一层工程细节需要 Part B；
- Current / Target 基本清楚，但 Evidence 不完整；
- 个人 Ownership 只说到“参与”，无法界定具体设计 / 实现 / Review。

### FAIL

Blue 没回答问题、核心逻辑矛盾、Owner / State / Recovery 不成立，或只能依赖 Closed-book 之外的信息才能继续。

### UNSUPPORTED_CLAIM

简历本身做出了强 Claim，但 Zuno Canonical Docs / Evidence / Ownership 来源无法支撑。此时不能把问题只归为“Blue 不会答”；必须回到简历或事实来源修正。

## Gap Taxonomy

Judge 必须尽量选择最小根因，不用一个模糊的“回答不好”覆盖全部。

### `NARRATIVE_GAP`

架构本身大体合理，资料也存在，但 Part A / Project Story 无法让 Blue 自然讲清：

- 问题是什么；
- 为什么简单方案失败；
- 为什么这个边界自然出现；
- 为什么不是现成平台；
- trade-off / delete condition。

优先 Narrative Fix，不升级 Architecture Round。

### `DOC_GAP`

已有设计语义成立，但文档缺少某个必要事实、例子、故障链、术语解释或跨文档入口。

### `ARCHITECTURE_GAP`

只有出现 Owner 冲突、状态语义冲突、Recovery 无法闭环、Security Authority 不清、Contract 不成立、Build/Buy 无合理边界、关键反例无法处理等，才判 Architecture Gap。

### `TRADEOFF_GAP`

能说“怎么做”，但不能解释：

- 为什么不是更简单方案；
- 为什么不 Buy / Adopt；
- 增加什么复杂度；
- 什么条件下删除 / 合并。

### `EVIDENCE_GAP`

Claim 需要代码、Test、Trace、Eval、Migration、Benchmark、运行数据等证明，但当前 Evidence 不足。

### `IMPLEMENTATION_GAP`

Target 设计明确，但 Current Code / Test 尚未实现或实现与文档不一致。

### `OWNERSHIP_GAP`

无法严格区分：

- 用户本人；
- 导师 / 课题组；
- 团队成员；
- Framework；
- Codex / Claude Code / Agent 辅助。

### `MEASUREMENT_GAP`

知道要测什么，但当前没有可接受的 baseline、dataset、metric、sample、SLO、ablation、成本或统计方案。

### `PROJECT_REALITY_GAP`

项目来源、用户场景、阶段、Pilot / Production、真实使用方式等项目事实本身不清楚。

### `RESUME_CLAIM_RISK`

简历措辞比项目事实 / Evidence 更强，例如把 Target 写成已实现、把团队成果写成本人、把 Pilot 写成 Production、把平台能力写成自研。

## Judge 的判定顺序

不要因为 Blue 没说到某个术语就判错。按顺序判断：

1. **Did it answer the question?**
2. **Is the causal reasoning coherent?**
3. **Is the claim source-supported?**
4. **Does it preserve Current / Target / Unknown?**
5. **Does it preserve personal / team / advisor / framework ownership?**
6. **If Red injected a failure, is recovery closed?**
7. **If Red challenged Build/Buy, was the alternative treated fairly?**
8. **Would a real interviewer have a meaningful next drill?**

## Source support

Judge 应记录 Blue 的关键句由什么支持：

```text
resume claim
project Part A
architecture Part A
module Part A
module Part B/C
ADR
evidence
unsupported inference
```

如果一个回答“行业上通常正确”但 Zuno 文档没有这个事实，应标为 unsupported inference，而不是因为模型知道正确答案就 PASS。

## Part A 的专项验收

Project / Architecture / Module Part A 的目标不是覆盖所有字段，而是让 Blue 在不翻 RFC 的情况下先完成面试主叙事。

Judge 要分别判断：

### 30 秒

是否能说清：

```text
问题
+ 核心选择
+ 为什么
```

### 90 秒

是否还能自然补上：

```text
机制
+ 一个典型异常
+ 恢复
```

### 3 分钟

是否还能继续补上：

```text
alternative
trade-off
scale / cost
Current / Target
Evidence
personal ownership（如适用）
```

如果 30 秒回答必须先读 B14，优先判 Narrative / Doc Gap；如果 3 分钟问题要求精确 Crash Window 而 Part B 能回答，不应因为 Part A 没有字段表而判失败。

## Attack Chain 判断

Judge 每 Turn 给 Red 一个内部 `next_action`：

### `CONTINUE_SAME_CHAIN`

当前回答暴露更深风险，继续追同一 Claim。

### `REFRAME_SAME_RISK`

Blue 可能只是没听懂问题。换现实场景 / 反例问一次，但不要泄露标准答案。

### `NEXT_ATTACK_ANGLE`

当前风险已稳定，通过另一个角度交叉验证同一 Claim。

### `NEXT_CLAIM`

该 Claim 已足够通过或失败已经稳定。

### `CLOSE_ROUND`

达到 Round 停止条件。

## Severity

建议：

- `S0`：简历真实性 / Ownership / Current-Target 重大风险，可能直接伤害可信度；
- `S1`：核心架构无法解释或关键 recovery / authority 不成立；
- `S2`：重要 Trade-off、Evidence、Scale、Security 追问无法支撑；
- `S3`：表达、术语时机、例子不足，不改变核心判断。

Severity 不是分数游戏；它用于确定修复优先级。

## Judge 禁止行为

Judge 不得：

- 把外部面经标准答案写给 Blue 后再让 Blue 重答；
- 因为文档没有覆盖一道冷门八股就强行判 Architecture Gap；
- 为了提高通过率替候选人改写个人 Ownership；
- 将导师 / 课题组论文能力视为用户本人实现；
- 将 Target / Mock / Demo / Test 当 Production Evidence；
- 因为某个 Framework 流行就判 Zuno 必须采用；
- 在同一 Round 中直接修改 canonical docs。

## Round Summary

结束后至少输出：

```text
Round identity / mode / base SHA / resume snapshot
Interviewer persona
Claims tested
Attack chains
Verdicts
Top 3 gaps + severity + gap type
Unsupported resume claims, if any
30s / 90s / 3m extractability
Part A coverage gaps
Evidence / ownership gaps
Recommended independent fix order
Retest angles using different wording
```

Judge 的报告进入历史；只有独立修复 PR 被接受后，改变才进入 canonical owners。