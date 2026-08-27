# 任务路由

本文只决定先读什么、走哪条 Owner 路径和何时停止。

| 任务 | 先读 | 主要 Owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| 项目背景、历史事实、立项逻辑 | `docs/project/project.md`、`project-fact-provenance.md` | Project Documentation |
| 葛季栋/LIPLAB 研究谱系、论文/能力 lineage | `docs/research/README.md`、`jidong-ge-liplab-lineage.md`、`research-to-engineering-traceability.md` | Research reference；不得覆盖 canonical truth |
| WorkBuddy / Dify / Coze / LangGraph 比较、Build/Buy | `docs/research/agent-platform-baseline.md` + 当前官方资料 | Research + Architecture；平台 baseline 需重新核验 |
| 文档故事化 / Part A Rewrite | `docs/research/documentation-narrative-blueprint.md` + Project/Architecture/目标 Module | Documentation；先判断 Writing Gap vs Architecture Gap |
| 技术面试 / 架构 Reviewer 连续追问 | Project 主线，再按问题进入 Research / Architecture / Module / Evidence | 对应事实 Owner |
| Red / Blue 面试对攻与压力测试 | `.agent/red-blue/README.md`、`protocol.md`、`attack-model.md`、`judge.md`、`docs/maintenance/red-blue/README.md` | Red/Blue Harness；Blue Closed-book |
| 个人贡献 | `docs/project/project.md`、project fact provenance、历史任务级证据 | Project Documentation；不得由 Target 或导师成果反推 |
| 文档结构、README、Agent 路由 | `docs/maintenance/agent-workflow/README.md`、`workflow.md`、`docs-map.md`、验证地图 | Documentation |
| 阅读总体架构、理解系统 | `docs/project/project.md`、必要 Research、`docs/architecture/README.md`、Architecture Part A | Architecture |
| 总体架构或跨层设计 | Architecture Part A+B、有效 ADR、Evidence、Governance；Research 仅作上游依据 | Architecture |
| 阅读模块、理解责任域 | `docs/modules/README.md`、对应 `docs/modules/0X-*.md` Part A | Module Design |
| Module Deep Design / Review | 总体架构 Part A+B、目标模块 Part A+B+C、ADR、Evidence、Governance | Module Design；不自动授权实现 |
| Module Detail Freeze Review | 上述全部 + 目标模块 B14.1–B14.8 + 相邻模块 Candidate + ADR / Evidence | Module Design；当前仅 Detail Candidate |
| 字段、DB / Manifest / Checkpoint / Registry、并发、Migration、Failure Injection 实现任务 | 对应模块 B14.1–B14.8 + 当前代码 / Migration；先确认 Detail Freeze 与 Implementation Authorization | Architecture + Codex |
| 实现、测试、Migration、Recovery、Contract、Security | 总体架构 + 对应模块 + ADR + Evidence + Governance | Architecture / Runtime |
| 架构为什么发生变化 | 当前架构 + `docs/maintenance/history/red-blue/` 指定 Round | Architecture Review |
| 当前运行、部署、生产准备度 | `docs/evidence/`、`docs/maintenance/operations/`、代码和测试 | Evidence / Operations |
| 人和 Agent 怎样完成 GitHub 改动 | `docs/maintenance/agent-workflow/README.md` + `.agent/references/workflow.md` | Maintenance / Agent workflow |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client |
| `src/backend/zuno` | `code-map.md`、`debugging.md`、总体架构 + 对应模块 | Runtime Owner |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md`、Evidence、09 模块 | Eval Owner |

## 停止条件

- 目标会改变业务 API、数据库 Schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证。
- Research 发现新论文/平台能力时，不直接改 Architecture；先确定 lineage、来源可靠性以及它是否只是 Writing / Evidence Gap。
- Red / Blue 发现 Gap 时先停在 Judgment / Report；不得在同一 Round 用外部标准答案补 Blue，也不得自动修改简历、Architecture 或 Runtime。
- Project 如果发现必须新增 / 删除九个逻辑模块、扩大 Canonical Legal Kernel 或改变跨模块 Owner，必须升级 Architecture Gap。
- 模块 Deep Design / Detail Candidate / Freeze Review 如果需要改变总体 Owner、扩大 Canonical Kernel 或修改 Admission / Invalidation / Lifecycle / Security / Effect 等跨模块不变量，停止局部设计并升级 Architecture Gap。
- 九个模块 B14.1–B14.8 都只是冻结前候选。没有 Module Detail Freeze 和明确 Implementation Authorization 时，不创建大规模业务表、Migration 或 Runtime 实现。
- 不允许把某个模块的字段模板机械复制到另一个模块；每个 Owner 的 identity、事务和恢复锚点必须按自身语义设计。
- 发现未提交资产、未进入 main 的 Commit 或未归属文件时默认保留，不用磁盘占用作为删除理由。
- 未经明确授权，不根据 Research Snapshot、Red / Blue Proposal 或 Candidate 直接实施业务代码。

## 基本流程

```text
read project / current truth
  → read research only when lineage / platform / narrative context matters
  → distinguish Research / History / Target / Current / Unknown
  → define owner and boundary
  → read overall architecture
  → read target module Deep Design V2 + Part C
  → for field-level questions, read B14.1–B14.8 Detail Candidate
  → read adjacent Owner candidates and Evidence
  → stop if a cross-module architecture gap appears
  → run Module Detail Freeze Review
  → obtain explicit Implementation Authorization
  → implement canonical path
  → focused verify / CI as required
  → PR + merge
  → reread exact main HEAD
```

Red / Blue 任务走独立流程：

```text
pin Zuno SHA + exact resume snapshot + target role
  → .agent/red-blue/
  → Red claim mining / optional calibration
  → Blue closed-book Part A-first answer
  → Judge / Gap
  → archive
  → independent fix / retest if requested
```
