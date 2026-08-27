# Zuno Agent / Repository Workflow

本目录解释**人和 Agent 怎样维护 Zuno**。它是 Human-readable process contract，不是机器路由，也不是 Product Runtime 设计。

机器执行层仍然只有：

```text
AGENTS.md
.agent/system.yaml
.agent/references/
.agent/programs/
.agent/templates/
.agent/scripts/
```

不要把这里的说明复制成第二套 `.agent` 配置。

## 角色分工

### ChatGPT

主要负责：

- 从 GitHub 读取最新 canonical state；
- 研究真实面试、论文、平台和工程资料；
- 判断 Narrative / Architecture / Evidence / Ownership Gap；
- 审查文档、架构与 PR；
- 必要时运行 Red Team；
- 给本地执行者形成边界明确的修改任务；
- merge 后重新读取 `main`，不根据旧上下文宣布完成。

### Claude Code / 本地工程执行者

主要负责：

- 读取本地完整代码、测试和 Git history；
- 修改代码 / 文档 / Migration / Test；
- 执行本地验证；
- 返回 Commit SHA、修改清单、测试和未解决问题。

### GitHub

GitHub 是跨 Agent 的同步事实面。任何“已经完成”的结论都必须最终落到可读取的 Commit / PR / CI / main HEAD。

## 标准 GitHub 修改闭环

```text
read latest main
  → define one bounded objective
  → create branch
  → edit only target scope
  → run focused validation
  → inspect diff
  → open PR
  → wait for required CI
  → fix failures without weakening semantic gates
  → merge (normally squash)
  → reread exact main HEAD
  → run post-merge consistency review
```

如果 PR CI 失败，不通过降低质量阈值、删除关键 validator 或把 Target 冒充 Current 来“修绿”。先判断失败暴露的是迁移遗漏、真实文档 Gap，还是 validator 本身仍绑定旧目录/旧表述。

## Research → Documentation

外部研究不能直接覆盖 Canonical Truth。

```text
Research / interview / platform / paper
  → source verification
  → research/ 中记录 lineage / baseline / hypothesis
  → 判断 Writing Gap 还是 Architecture Gap
  → 成熟结论进入 project / architecture / modules / ADR
  → Current claim 仍需 evidence/
```

研究论文与 Zuno 的关系至少区分：`DIRECT_LINEAGE`、`CAPABILITY_LINEAGE`、`CONCEPTUAL_LINEAGE`、`BACKGROUND_ONLY`、`UNVERIFIED`。平台能力基线必须带核验日期，因为 WorkBuddy、Dify、Coze、LangGraph 等能力会快速变化。

## Architecture / Documentation Review

先问：

1. 真实问题是什么？
2. 最简单方案是什么？
3. 它在哪个具体场景失败？
4. 谁真正拥有这个事实？
5. Crash / timeout / late result / 权限变化时先相信谁？
6. 哪些能力应该 Buy / Adopt / Extend，而不是自研？
7. 哪些是 Current，哪些只是 Target / Hypothesis？
8. 什么条件下应该删除这层复杂度？

Part A 的质量由因果连续性、场景、失败、替代方案和 Trade-off 判断，不由标题数量或术语密度判断。

## Red / Blue

Red / Blue 是 Architecture Stress Test，不是默认开发流程。Red 可以读取真实面试和外部资料；正式 Closed-book Blue 只读允许的 Zuno canonical docs。Blue 答不出来应记录 Gap，不临时用外部答案补齐。

### 工作空间分层

Red / Blue 不使用一个永久的“万能工作目录”。当前约定分四层：

```text
.agent/programs/                           运行态 workspace；只有明确启动 Round 时才激活
.agent/system.yaml + .agent/references/    机器路由、读取顺序和执行约束
docs/maintenance/agent-workflow/          人类可读的工作流与维护说明
docs/maintenance/history/red-blue/        Round 结束后的原始历史归档
```

当前 `.agent/programs/current.md` 的状态是 `no-active`，因此现在没有正在运行的 Red / Blue Round，也不应为了“预留空间”自动创建新的 Session / Question Set / Candidate Branch。

一次正式 Red / Blue 的推荐闭环是：

```text
explicit user activation
  → read latest main + canonical Project / Architecture / Modules
  → Red may read approved external interview/research sources
  → Blue closed-book reads only allowed canonical Zuno docs
  → ask one primary question at a time
  → record answer + counterexample + judgment
  → classify gaps: DOC / NARRATIVE / ARCHITECTURE / TRADEOFF / EVIDENCE /
                  IMPLEMENTATION / OWNERSHIP / MEASUREMENT
  → do not repair answers from external sources during Blue
  → close the Round
  → archive raw record in docs/maintenance/history/red-blue/
  → accepted design changes enter Architecture / Module / ADR in a separate change
  → Current claims still require Evidence
```

原始历史进入 `docs/maintenance/history/red-blue/`；被接受的结论必须单独进入 Architecture / Module / ADR，历史 Round 本身永远不是实施授权。

## 后续可导出的 Skills

这些流程可以在规则稳定以后抽成 Skill，但 Skill 只能封装**方法和执行流程**，不能携带一份与仓库竞争的 Zuno Canonical Truth。

优先级建议：

1. **Red/Blue Architecture Interview Harness**：最适合优先导出。封装 interviewer persona、单问题连续追问、反例注入、Closed-book Blue、Gap taxonomy、Round closure；仓库内容仍在运行时读取。
2. **Research → Architecture Traceability**：封装作者/论文身份核验、lineage 分类、Research → Capability → Provider → Qualification → Canonical decision 的证据链，以及 Writing Gap / Architecture Gap / Evidence Gap 判断。
3. **GitHub Architecture Review Closure**：封装 latest `main` → bounded branch → validator / CI → PR → merge → reread exact `main` HEAD 的闭环，适合文档治理和 Architecture Review PR。
4. **Human-first Architecture Documentation Review**：封装 Part A 的因果叙事检查、术语密度告警、Current / Target 边界和“复杂度什么时候应该删除”的人工 Review checklist。

不建议把 `docs/maintenance/history/red-blue/` 直接导出为 Skill；那是项目历史数据，不是可复用方法。也不建议把 `.agent/programs/current.md` 打包进 Skill；它是当前仓库的运行态指针。

## Current / Target 铁律

不得把：

- 设计文档 → 已实现；
- Demo / Pilot → Production；
- 团队/导师成果 → 个人实现；
- Framework capability → Zuno 自研；
- “应该可以” → “已经验证”。

需要时明确写 `Current / Target / Evidence / Unknown / Measurement Needed`。
