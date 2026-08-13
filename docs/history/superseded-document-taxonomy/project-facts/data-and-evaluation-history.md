# Data and Evaluation History

status: canonical-history
canonical_question: 历史 QA、测试集、标准答案、评测和失败样本从哪里来？
owner: Project Facts / Evaluation History
replaces: 无；从 `delivery-and-usage.md` 的质量反馈中拆出数据与评测历史

## 已确认和待确认

| Claim | 状态 | Evidence | Strength | 边界 |
|---|---|---|---|---|
| 客户 Demo 后提出回答质量需要继续提高 | `[USER_CONFIRMED]` | E-USER-002 | E1 | 没有前后对照指标 |
| 法院侧人员参与过测试 | `[USER_CONFIRMED]` | E-USER-002 | E1 | 不能推出存在正式标注数据集 |
| 法院侧问题被整理成 QA、形成版本化测试集并持续评估 | `[UNKNOWN]` | 待 Artifact / 用户确认 | E0 | 不能由“有测试”自动推出 |
| 存在 Gold Answer、Gold Evidence 或正式 Reviewer Protocol | `[UNKNOWN]` | 待 Artifact / 用户确认 | E0 | 不能由架构 Target 补齐 |
| 与 WorkBuddy、Dify 或通用 LLM 做过公平对照 | `[UNKNOWN]` | 待 Benchmark / 记录 | E0 | A/B/C 是 Target 设计，不是历史结果 |

## 评测事实记录模板

恢复每一个历史评测批次时，至少记录：

```text
QA Source
Question / Case Scope
Curator
Gold Answer
Gold Evidence / Citation
Dataset Version
Model / Prompt / Tool Version
Evaluation Protocol
Baseline
Result
Failure Cases
Reviewer / Customer Feedback
Evidence ID
```

没有这些字段时，可以记录“做过测试”，但不能写成可复现 Benchmark。

## 公开研究边界

LawBench、LJPCheck、JIA、Fact–Article Correspondence 和 InternLM-Law 只能作为
`PUBLIC_CONTEXT`，为 Zuno 的分层评测、领域能力和功能测试提供方法论输入；它们不能证明
历史项目使用了相同数据、指标或算法，也不能证明 Zuno 质量优于任何竞品。研究证据索引见
[`project-reconstruction-lab/sources/legal-ai-capability-matrix.md`](../../../project-reconstruction-lab/sources/legal-ai-capability-matrix.md)。

## 目标与历史分离

以下是 Target 评测设计，不是历史事实：

```text
L1 Domain Capability
L2 Legal Cognition
L3 Functional Behavior
L4 Real Task Outcome
L5 Agent System
```

A/B/C WorkBuddy Generic、WorkBuddy + Zuno Capabilities、Zuno Domain-aware Runtime 也
仍是待执行的公平 Benchmark。

## Owner 边界

本文件负责历史数据和评测过程；当前可复现 Eval 证据进入 [`../../evidence/`](../../evidence/README.md)，
Target 评测 Contract 进入 [`../eval/legal-eval-and-benchmark.md`](../eval/legal-eval-and-benchmark.md)，
下一轮追问进入 [`../../../project-reconstruction-lab/01-facts/open-questions.md`](../../../project-reconstruction-lab/01-facts/open-questions.md)。
