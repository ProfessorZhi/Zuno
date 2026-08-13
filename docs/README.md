# Zuno 文档入口

前台文档默认使用中文，承载当前正式结论。`docs/project/` 是项目知识入口；`docs/history/` 保存批准的历史摘要和 Superseded 原稿；`project-reconstruction-lab/` 是调查、恢复和 Red/Blue 工作区，不替代正式事实源。

## 首读路径

- [Zuno 项目知识入口](./project/README.md)
- [历史项目入口](./project/history/README.md)：回答历史背景、团队、演进、交付和未知事实。
- [Current Repository Reality](./project/status/current-reality.md)：回答当前仓库有什么证据。
- [Target Status](./project/status/target-status.md)：回答 Target、Hypothesis、Future 和 reversal boundary。
- [总体 Target 架构](./project/architecture/architecture.md)：回答 Product、Domain、Logical Capability、Physical Service/Deployment 如何形成跨层闭环。
- [架构图展示配对](./project/architecture/architecture-views.md)：与 `architecture.html` 配套，只负责展示，不拥有独立架构事实。
- [Production Readiness](./project/status/production-readiness.md)：当前生产状态事实源，当前仍为 `NOT_ESTABLISHED`。
- [架构决策](./decisions/README.md)
- [工程治理](./governance/repo-ownership-matrix.md)
- [当前证据](./evidence/README.md)
- [架构面试验证语料](./verification/interview-qa/README.md)：非规范性攻击语料。
- [历史归档](./history/README.md)

## Canonical 文档层次

```text
docs/project/
  README.md
  history/       What actually happened? + UNKNOWN
  status/        What is proven now, what is Target, is Production proven?
  architecture/  How do Product, Domain, Capability, Service and Deployment fit?

docs/decisions/  Why was a decision accepted or reversed?
docs/governance/ Who owns the document and boundary?
docs/evidence/   What can be reproduced from code, test, trace or eval?
docs/history/    Approved summaries and Superseded raw document material
```

`docs/project/architecture/` 仍严格只有四个文件。旧 `facts/`、专题目录和 `modules/` 已迁入历史归档，不再是 active Canonical taxonomy；它们的原始内容不因迁移而变成 Current 或 Target。

## Current / Target / History

```text
Current
    由代码、Migration、Test、Trace、Eval 或真实运行证据证明。

Target
    由已接受 ADR、总体架构和共享治理边界定义；不证明实现。

Hypothesis
    必须由 Benchmark、Spike、Security Evidence 或 User Validation 关闭。

History
    保留发生过的项目事实、未知事实和被替换的文档组织方式。
```

本轮文档重构不修改 Facts、ADR、Runtime、UI、Schema、Migration、Dependencies、Production Infra，也不启动 Round-007。Round-006 immutable evidence 继续保持不变。

## 两条阅读路径

```text
历史/项目读者：history → current-reality → architecture → target-status → evidence
工程/架构读者：architecture → decisions/governance → status → evidence → current Program
```

## 三条必须分开的项目故事

```text
HISTORY
    智慧司法背景 → 已有产品 → 用户加入 → Agent / Memory / OpenViking / Tool Calling
    → Demo → 回答质量反馈 → 法院侧测试 → Pilot → 尚未 Production。

CURRENT
    当前 main 真正被代码、Migration、Test、Config、Trace 或 Eval 证明的内容。

TARGET
    Evidence-driven Legal Agent Platform；五层责任视图、A/B/C Kill Test 和最终服务数量
    都不把目标能力伪装成历史事实或已测量收益。
```

WorkBuddy / Dify 的比较是 `TARGET PRODUCT THESIS` 和 Benchmark 假设，不是营销结论；公开论文和研究成果是 `PUBLIC_CONTEXT` / `RESEARCH_TRANSFER`，不能倒灌为历史 Zuno 实现。

项目事实不确定时保留 `UNKNOWN`、`USER_PARTIAL_RECALL` 或候选状态；Target 架构不能替代历史事实。
