# Architecture Interview / Red-Blue Workflow

这是 `project-reconstruction-lab/` 唯一当前工作流。它用于在正式架构清晰后进行一次可收口的
架构面试和 Red/Blue 审查；它不负责生成事实、不直接修改 Runtime，也不把一轮问题自动变成十个
新组件。

## Actor Ownership

本 Lab 的默认执行模式是：

```text
DEFAULT_MODE: MANUAL_CHATGPT
```

默认链路由 ChatGPT Main Coordinator 驱动：

```text
ChatGPT Main Round Brief
  → ChatGPT Red Questions
  → ChatGPT Blue Answers
  → ChatGPT Red Review
  → ChatGPT Main Quick Judgment
  → Codex Archive
  → Archive Commit
  → ChatGPT Main Architecture Review
  → Optional Codex Architecture Revision
  → Revision Commit
  → ChatGPT Review
  → Next Round
```

### ChatGPT Main Coordinator

ChatGPT Main 是 Architecture Decision Owner，负责读取 latest main、选择 Round Theme、判断
是否继续 Overall Architecture 或进入 Module、形成 Round Brief、审查 Red/Blue/Review、分类
ANSWER ISSUE、FACT GAP、PART A GAP、PART B / MODULE GAP、ARCHITECTURE GAP、MEASUREMENT、
NO CHANGE，并作出 ACCEPT、REJECT、DEFER、MEASURE 或 NO_CHANGE。Main 还负责形成 Architecture
Revision Specification 和 Codex Task，并审查 Codex 结果是否与 Architecture 一致。

### ChatGPT Red

ChatGPT Red 负责提问、Counter Attack、必要性、Alternative / Build-Buy、Failure / Recovery、
Ownership、Evidence 和 Complexity Kill Test。Red 不拥有 Architecture Decision。

### ChatGPT Blue

ChatGPT Blue 作为候选人回答，基于允许的事实源解释设计，并明确 Current / Target / History /
Unknown，暴露无法回答的问题。Blue 不修改 Canonical Architecture。

### Codex

Codex 只执行上层已明确裁决的任务：

- Archive Executor：读取 latest main，保存完整 Q/A/Review 和 Main Summary，更新 History 导航，
  验证、Commit、Push；
- Architecture / Engineering Executor：严格按已冻结 Scope 修改文档或代码，更新必要入口、
  verifier 和测试，Commit、Push 并报告证据。

Codex 不负责自己生成 Red Questions、扮演 Blue、进行 Main Judgment、因 Red Finding 自行修改
Architecture、改变冻结原则或自动启动下一 Round。三个本地 Skill 不参与这条默认手动链路，只有
用户或上层 Coordinator 明确指定名称时才读取。

## 一轮怎么走

```text
Main Round Brief
  → Red Questions
  → Blue Answers
  → Red Review
  → Main Quick Judgment
  → Archive First
  → Archive Commit
  → Main Architecture Review
  → Optional Architecture Revision Commit
  → Next Round
```

每一步的含义：

1. Main 先固定本轮主题、基线和阅读范围；
2. Red 选择最强的必要性、边界、失败、恢复、安全、成本或替代方案攻击；
3. Blue 只能基于基线事实、正式架构、ADR 和通用工程知识回答，并明确未知；
4. Red Review 记录回答暴露的缺口，不替 Blue 写推荐答案；
5. Main 判断是 `ACCEPT`、`REJECT`、`DEFER`、`MEASUREMENT`、`FACT_GAP` 还是 `NO_CHANGE`；
6. 先把问题、回答和判断归档，确保“发生了什么”不会被后续架构编辑覆盖；
7. 只有 Main 明确授权，才单独创建 Architecture Revision Commit。

## 必须追问的内容

每个被保留的复杂度至少要回答：

- 为什么存在，真实问题是什么；
- 为什么普通 Library、Worker、模块化单体或成熟 OSS 不够；
- 谁拥有状态和最终决定；
- 失败、重试、重复执行和恢复怎样处理；
- 权限、审计、观测和验证怎样成立；
- 代价是什么，什么证据会触发删除、简化或外部化。

Red 可以给出反例和更简单替代，但只作为攻击。Blue 必须先用普通工程语言解释，再补精确
术语。不能把“企业级”“最佳实践”“未来扩展”当作证明。

## 决策原则

```text
DELETE → SIMPLIFY → REUSE → EXTERNALIZE → MEASURE → BUILD
```

Red Finding 不等于 Architecture Gap；Blue 回答差也不等于需要新增机制。若事实缺口阻止判断，
返回 `FACT_GAP`；若收益没有证据，返回 `MEASUREMENT`；若已有工具足够，返回 `REUSE` 或
`EXTERNALIZE`。

连续 Overall Architecture 稳定后，才可以单独讨论模块或服务拆分。不要预设 11 个模块、固定
题量、固定服务数、GraphRAG、Multi-Agent、微服务或某个 Provider 必须存在。

## 状态边界

```text
CURRENT    由代码、Test、Trace、Eval 或真实运行证据支持
HISTORY    已发生并被归档的 Round 或项目材料
TARGET     已接受但尚未实现的目标设计
HYPOTHESIS 等待 Benchmark、Spike、用户或安全验证
UNKNOWN    当前没有足够证据
```

Round Archive 只保存历史记录，不拥有今天的 Facts 或 Target。Architecture Revision 必须回到
`docs/architecture/`、ADR 或正确的治理 Owner；本 Workflow 不创建第二套 Canonical 文档。

## 停止条件

在以下任一情况停止本轮并报告原因：

- 无法证明当前基线或阅读范围；
- Red 需要读取不在允许范围内的业务代码或私有材料；
- Blue 只能靠猜测补历史事实；
- 问题已经没有新的 Architecture Information；
- 需要修改 API、Schema、Dependency、安全边界或生产系统；
- 用户尚未授权进入 Architecture Revision 或新的 Round。

Interview Ready 不等于 Production Ready。生产结论仍需要真实运行、负载、故障、安全、恢复和
外部验收证据。

## 归档契约

正式 Round 归档在 `docs/history/red-blue/`。Manual Round 使用完整归档，并至少标明：

```text
series
round_id
execution_mode: MANUAL | AUTOMATED
status
base_sha
archive_commit
architecture_revision_commit
```

旧 Automated Program 不再逐轮保留当前树文件，而由唯一 Legacy Summary 保存来源、原始状态、
基线和处置；其完整原始包通过 Git history 追溯。中止的 Round 保留真实中止状态，不补造不存在的
后半轮。除非用户明确重新启动 Automated Program，未来默认使用 `manual-round-NN-<theme>.md`。
旧 Protocol、Bootstrap、Reset 和 Workflow Engineering 的演进不在当前 Lab 重新建立历史目录。
