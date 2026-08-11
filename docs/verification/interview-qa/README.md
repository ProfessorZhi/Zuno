# Zuno Architecture Interview Verification Corpus

本目录不是面试 FAQ，也不是第二套架构。它用真实面试追问、合理派生追问和 Zuno Target Architecture 压力题，验证一个没有聊天上下文的人能否仅阅读正式架构文档回答工程问题。

## Canonical Truth

正式事实源：docs/architecture/、docs/modules/、docs/decisions/、docs/governance/。

QA 与正式架构冲突时，正式架构优先。QA 中的 Expected Answer 只允许复述或压缩 canonical docs，不得创造新的 Runtime、Current、Benchmark 或 Production 事实。

本次双层文档重构只改变同一份 Markdown 的阅读入口，不改变架构语义、QA 题目或 Canonical Reference。人类问题优先由 Part A 回答，实现和审查问题继续落到 Part B；QA 仍然是消费者，不是第三套架构事实。

本轮架构文档写作重组保留了既有 canonical section anchors，以避免无语义变化的标题改名破坏外部引用；因此本轮 `section_ref` 更新数量为 `0`。若未来语义迁移导致 anchor 消失，必须先修复 canonical 文档，再更新覆盖矩阵和 QA metadata。

## 题库范围

当前冻结 Q001–Q267，分布为：

| Domain | 题数 |
| --- | ---: |
| Agentic GraphRAG / Evidence | 65 |
| Tool / MCP / Permission / Effect Safety | 58 |
| Memory & Context | 44 |
| Memory & Information Extraction | 35 |
| Agent Core / Planning & Control | 45 |
| Cross-module / System Design | 20 |
| 合计 | 267 |

每题标记 source_type：REAL（真实问题）、DERIVED（从真实问题合理延伸）、ARCHITECTURE_STRESS（根据 Zuno Target 设计构造）。

## 三种使用模式

### 模式 A：候选人复习

随机打开一个 QID，先不看答案，只根据 canonical architecture 回答，再对照 30 秒回答、深挖回答和 Follow-up。

### 模式 B：Architecture Audit

只打开 docs/architecture/、对应 docs/modules/、docs/decisions/ 和 docs/governance/，检查能否独立回答；coverage_status=FULL 只代表文档覆盖，不代表 Runtime 已实现。

### 模式 C：未来代码审查

实现完成后，把每道题继续映射到 code、Migration、test、Trace 和 Eval，回答“设计在哪里被代码证明”。这不是本轮的完成条件。

## 覆盖闸门

Architecture Interview Coverage = PASS 仅表示：267/267 有 canonical references，267/267 final coverage=FULL，且没有 conflicting canonical definition 和 QA-only architecture fact。

本轮复核基线与结果：

| 阶段 | FULL | PARTIAL | MISSING | 说明 |
| --- | ---: | ---: | ---: | --- |
| 双层重构前 | 267 | 0 | 0 | 既有 QA metadata 的最终覆盖状态 |
| 双层重构后 | 267 | 0 | 0 | 保留稳定章节锚点后重新运行结构与引用校验 |

这不是 Runtime 质量证明；如果未来 Part A 暴露真正的架构 Gap，应记录到 Gap / ADR，而不是为了让 QA 变成 FULL 虚构实现证据。

它不表示 implementation available、quality proven 或 production ready。Current / Target / Future 状态仍以 docs/status/production-readiness.md 为准。

验证命令：

    python tools/scripts/verify_architecture_interview_qa.py
    pytest -q tests/repo/test_architecture_interview_qa.py -p no:cacheprovider
