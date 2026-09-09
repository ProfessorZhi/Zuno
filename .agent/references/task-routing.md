# 任务路由

本文只决定先读什么、走哪条 Owner 路径和何时停止。

| 任务 | 先读 | 主要 Owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| 项目背景、历史事实、立项逻辑 | `docs/project/project.md`、`docs/governance/project-fact-provenance.md` | Project |
| 葛季栋/LIPLAB 研究谱系、论文/能力 lineage | `docs/research/README.md` + 对应 research 文件 | Research reference；不得覆盖 Project/Target/Current |
| WorkBuddy / Dify / Coze / LangGraph 比较、Build/Buy | `docs/research/agent-platform-baseline.md` + 当前官方资料 | Research + Architecture |
| 文档故事化 / Part A Rewrite | `docs/research/documentation-narrative-blueprint.md` + Project/Architecture/目标 Module | Documentation；先区分 Writing Gap 与 Architecture Gap |
| 技术面试 / 架构 Reviewer 连续追问 | Project 主线，再按问题进入 Architecture / Module / Evidence | 对应事实 Owner |
| Red / Blue 对攻与压力测试 | `docs/red-blue/README.md` + `.agent/red-blue/` | Red/Blue Review；Blue Closed-book |
| 个人贡献 | `docs/project/project.md` + provenance + 历史任务级证据 | Project；不得由 Target 或导师成果反推 |
| 文档结构、README、Agent 路由 | `docs/governance/documentation-architecture.md`、`docs/governance/workflows/agent-workflow.md`、`docs-map.md` | Governance |
| 阅读总体架构、理解系统 | Project → Architecture Part A → Modules README | Architecture |
| 总体架构或跨层设计 | Architecture Part A+B、有效 ADR、Evidence、Governance；Research 仅作上游依据 | Architecture |
| 阅读模块、理解责任域 | `docs/modules/README.md`、对应 Module Part A | Module Design |
| Module Deep Design / Review | 总体架构 Part A+B、目标模块 Part A+B+C、ADR、Evidence、Governance | Module Design |
| 字段、DB / Manifest / Checkpoint / Registry、并发、Migration、Failure Injection | 目标模块 Part B/C + 当前代码 / Migration；先确认实现授权 | Architecture + Implementation |
| 架构为什么发生变化 | 当前架构 + 对应 ADR；历史 Red/Blue 仅作辅助考古 | Architecture / Decisions |
| 当前运行、部署、生产准备度 | `docs/evidence/`、`docs/governance/operations/`、代码和测试 | Evidence / Operations |
| 人和 Agent 怎样完成 GitHub 改动 | `docs/governance/workflows/agent-workflow.md` + `.agent/references/workflow.md` | Governance / Agent workflow |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client |
| `src/backend/zuno` | `code-map.md`、`debugging.md`、总体架构 + 对应模块 | Runtime Owner |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md`、Evidence、Evaluation 模块 | Eval Owner |

## 停止条件

- 目标会改变业务 API、数据库 Schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证。
- Research 发现新论文/平台能力时，不直接改 Architecture；先确认 lineage、来源和真实业务需求。
- Red / Blue Finding 不自动修改简历、Architecture、Runtime 或 Evidence；先开独立修复任务。
- 如果局部修改需要新增/删除责任域、改变总体 Owner、Admission、Invalidation、Lifecycle、Security、Effect 或 Recovery，升级 Architecture Revision。
- 没有真实约束时，不因为“更高级”增加服务、状态机、GraphRAG、Reflection、Multi-Agent 或 Native Runtime。
- 发现未提交资产、未进入 main 的 Commit 或未归属文件时默认保留，不用磁盘占用作为删除理由。

## 基本流程

```text
read project / current truth
  → read research only when lineage / platform context matters
  → distinguish History / Target / Decision / Current / Unknown
  → define owner and boundary
  → read overall architecture
  → read target module
  → read adjacent owners and Evidence
  → stop if a cross-module architecture gap appears
  → implement only after explicit authorization
  → focused verify / CI
  → PR + merge
  → reread exact main HEAD
```

Red / Blue 独立流程：

```text
Part A readable first
  → pin Zuno SHA + exact resume snapshot + role/JD + scenario scope
  → CHATGPT_AUTO or AGENT_AUTO
  → Red scenario / claim attack
  → Blue closed-book answer
  → source / decision-impact verification
  → findings
  → independent fix
  → retest with different wording/scenario
```
