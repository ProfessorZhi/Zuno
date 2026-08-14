# Red / Blue History Owner

本目录只保存 Red / Blue 的历史过程证据，不拥有今天的事实、Target Architecture、ADR 或实现授权。
当前历史治理已经冻结；下一轮如果重新开始，必须先由用户明确激活新的工作流。

## Current formal archive

- [Manual Round 01 — Overall Architecture](manual-round-01-overall-architecture.md)：保留完整的
  Questions、Answers、Review/Score、Red/Blue/Main Judgment 和历史元数据，不得压缩或改写正文。
- Future Manual Round 02/03：按需新增 `manual-round-NN-<theme>.md`，每轮由 ChatGPT 手工协调并完整归档。

## Legacy automated archive

- [Legacy Automated Red/Blue Program Summary](legacy-automated-rounds.md)：只保留旧自动化程序的
  可审计摘要、原始状态、基线 SHA、主要发现和最终处置，不复制旧题目、回答或评分全文。
- 被压缩的旧自动化包由 Git history 保留；当前树不再维护一组平行的旧单轮文件。

Round-006 必须保持 `ABORTED_OPERATIONAL_PILOT` / `WORKFLOW_EXECUTION_BLOCKER`，其架构分数
为 `INVALID`，不能被摘要写成已完成的架构 Round。

## Archive boundary

Manual archive = 完整对攻记录和 Main Judgment。Legacy summary = 历史程序索引和处置摘要。
两者都只是 `HISTORY`，不能反向升级为 Current Facts 或当前架构决策。正式事实回到
[`../../facts/`](../../facts/README.md)，正式 Target 回到 [`../../architecture/`](../../architecture/README.md)，
正式长期决定回到 [`../../decisions/`](../../decisions/README.md)。当前工作流见
[`../../../project-reconstruction-lab/WORKFLOW.md`](../../../project-reconstruction-lab/WORKFLOW.md)，
导航见 [`../../../project-reconstruction-lab/archive-map.md`](../../../project-reconstruction-lab/archive-map.md)。

## Future archive rule

默认采用 `manual-round-NN-<theme>.md`。除非用户明确重新启动 Automated Program，否则不再创建新的
自动化单轮归档文件。Bootstrap、Reset、Repair、Evidence Closure、P0 Execution、Gate Realignment、
Normalization、Semantic Audit 和 Workflow Test 不属于正式 Round。
