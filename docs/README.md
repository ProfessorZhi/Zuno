# Zuno 项目文档

`docs/` 是 Zuno 的正式知识入口。一级目录现在分成两个 plane：前四个帮助人理解 **Zuno 是什么、从哪里来、为什么这样设计**；后四个负责 **这些事实怎样被决定、证明、治理和维护**。

```text
docs/
├── README.md
│
│   # Zuno Knowledge Plane
├── project/                    真实项目来源、发展、团队/个人 Ownership 与项目级叙事
├── research/                   葛季栋/LIPLAB 研究谱系、Research→Engineering、平台基线与写作研究
├── architecture/               唯一总体 Target Architecture（固定四文件）
├── modules/                    九个 Target 责任域：Human Part A + Engineering Part B/C
│
│   # Zuno Control & Maintenance Plane
├── decisions/                  仍有长期约束力的 ADR
├── evidence/                   Current Code/Test/Trace/Eval/Runtime Evidence
├── governance/                 Provenance、Ownership、Contract、文档与验收规则
├── maintenance/                Operations、Agent workflow 与历史审查资料
│   ├── operations/
│   ├── agent-workflow/
│   └── history/red-blue/
│
└── terminology.md
```

这不是严格流水线。最重要的边界是：`research/` 可以解释和挑战 Project / Architecture，但不能覆盖 Canonical Truth；`maintenance/` 可以解释怎样运行和维护仓库，但不拥有 Project、Architecture 或 Current Evidence。

## 推荐阅读顺序

第一次理解项目或准备技术面试：

1. [Project 主文档](./project/project.md)：这个项目从哪里来、为什么值得做、团队和个人做了什么、Current / Target / Unknown 到哪里。
2. [Research Knowledge Base](./research/README.md)：葛季栋/LIPLAB 研究谱系怎样形成 Research Artifacts，通用 Agent 平台已经解决什么，以及这些研究怎样进入 Engineering Capability。
3. [总体架构](./architecture/architecture.md)：基于这些约束，为什么会逐步出现不同 Authority / Ownership 边界。
4. [模块架构](./modules/README.md)：从总体故事进入九个责任域；先读 Part A，需要工程精度时再读 Part B / Part C / B14.1–B14.8。
5. [有效 ADR](./decisions/README.md)：哪些长期设计选择被正式接受以及为什么。
6. [Current Evidence](./evidence/README.md)：代码、Migration、Test、Trace、Eval 和运行到底证明了什么。
7. [Governance](./governance/)：事实来源、文档标准、Owner 与跨模块 Contract 规则。
8. [Maintenance](./maintenance/README.md)：Runbook、Agent/GitHub 工作流和 Red / Blue 历史。
9. [术语表](./terminology.md)：跨文档统一术语。

`docs/project/README.md` 只是导航。项目事实来源、允许表述和 Unknown 由 [`governance/project-fact-provenance.md`](./governance/project-fact-provenance.md) 管理。

## 一套回答问题的方法

```text
这个真实项目为什么存在、谁参与？          → project/
葛季栋/LIPLAB 哪些研究与 Zuno 有什么关系？ → research/
为什么不是普通 RAG / WorkBuddy + Tools？   → project/ + research/ + architecture/
为什么今天按这些责任边界设计？            → architecture/
每个责任域内部怎样工作和恢复？            → modules/
字段、Guard、事务、Crash/Migration？       → 对应 module B14.1–B14.8
长期决策为什么被接受？                    → decisions/
现在到底实现和验证到了什么程度？          → evidence/
事实和文档如何被治理？                    → governance/
仓库怎样运行、修改、审查和追溯？          → maintenance/
```

一个完整技术回答应覆盖“现实问题、简单 baseline、失败、设计原因、替代方案、恢复、当前证据和仍未证明的部分”，而不是只背技术栈或数据库表。

## Research 的特殊边界

`research/` 新增的是上游研究知识，不是第二套 Project / Architecture：

- 论文提出 ≠ Zuno 已实现；
- 导师/课题组成果 ≠ 用户本人实现；
- Research Artifact ≠ Engineering Capability；
- Capability ≠ Provider；
- Provider 可调用 ≠ Provider Qualified；
- Provider 成功 ≠ Formal Business Fact；
- 外部平台 Feature Matrix 会过期，必须带 `last_verified` 并重新核验。

成熟研究结论进入 Zuno 正文时，仍需修改对应 Canonical Owner；Current claim 仍只能由 `evidence/` 支持。

## 当前文档状态

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
quality_proven: NO
production_readiness: NOT_ESTABLISHED
```

九篇模块都已经有 Human-first Part A、B1–B14 Engineering Reference、Part C Cross-Module Consistency，并进一步拥有 B14.1–B14.8 Detail Freeze Candidate。这仍然不等于最终 enum、数据库 Schema、Migration、API 或服务拓扑被冻结，更不等于代码已经实现。

## 八个一级目录的 Owner 边界

- `project/`：项目级 Human-first Truth；当前只保留 `README.md` + `project.md`。
- `research/`：经核验的研究谱系、外部平台 baseline 与研究→工程推导；不拥有 Current/Target。
- `architecture/`：唯一总体 Target Architecture，固定四文件。
- `modules/`：九个冻结逻辑责任域及其 Deep / Detail Candidate。
- `decisions/`：仍有长期约束力的 ADR。
- `evidence/`：只记录 Current 代码、Migration、Test、Trace、Eval 和运行证据。
- `governance/`：事实来源、Owner、兼容 Contract、Human-first 与验收规则。
- `maintenance/`：当前 Runbook、Agent/GitHub 工作流与历史审查；不拥有当前架构真相。
  - Red / Blue archive route: `maintenance/history/red-blue/`。

`Current`、`Target`、`Future`、`History` 和 `Unknown` 必须区分。文档写得完整不证明实现可用；Current 只能由代码、Migration、Test、Trace、Eval 或真实运行结果证明。
