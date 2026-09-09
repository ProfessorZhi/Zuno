# Zuno Agent / Repository Workflow

本文件解释人和 Agent 怎样维护 Zuno。它是 Human-readable process contract，不是机器路由，也不是 Product Runtime 设计。

机器执行入口仍然是：

```text
AGENTS.md
.agent/system.yaml
.agent/references/
.agent/programs/
.agent/red-blue/
.agent/templates/
.agent/scripts/
```

不要把这里的说明复制成第二套 `.agent` 配置。

## 角色分工

### ChatGPT

主要负责读取最新 canonical state、研究公开资料、判断 Narrative / Architecture / Evidence / Ownership Gap、审查文档与 PR、运行 Red / Blue，以及在 merge 后重新读取 `main`。

### Claude Code / 本地工程执行者

主要负责读取完整本地代码和 Git history、修改代码/文档/Migration/Test、执行本地验证并返回 Commit SHA、测试结果和未解决问题。

### GitHub

GitHub 是跨 Agent 的同步事实面。任何“已经完成”的结论最终都必须落到可读取的 Commit / PR / CI / main HEAD。

## 标准 GitHub 修改闭环

```text
read latest main
→ define one bounded objective
→ create branch
→ edit only target scope
→ run focused validation
→ inspect diff
→ open PR
→ run required CI
→ fix failures without weakening semantic gates
→ merge
→ reread exact main HEAD
```

CI 失败时先判断是迁移遗漏、真实 Gap 还是 validator 仍绑定旧路径/旧表述。不要通过降低质量阈值、删除关键 validator 或把 Target 冒充 Current 来“修绿”。

## Research → Documentation

外部研究不能直接覆盖 Canonical Truth。

```text
Research / interview / platform / paper
→ source verification
→ docs/research/ 记录 lineage / baseline / hypothesis
→ 判断 Writing Gap / Architecture Gap / Evidence Gap
→ 成熟结论进入 project / architecture / modules / decisions
→ Current claim 仍需 evidence/
```

研究关系至少区分 `DIRECT_LINEAGE`、`CAPABILITY_LINEAGE`、`CONCEPTUAL_LINEAGE`、`BACKGROUND_ONLY`、`UNVERIFIED`。平台 baseline 需要核验日期，因为 WorkBuddy、Dify、Coze、LangGraph 等能力会变化。

## Architecture / Documentation Review

审查顺序优先是：

```text
真实问题
→ 最简单方案
→ 哪个具体场景让它失效
→ 谁拥有事实
→ Crash / timeout / late result / 权限变化时信谁
→ 什么应该复用成熟平台
→ Current / Target / Unknown
→ 什么条件下删除复杂度
```

Part A 由因果连续性、场景、失败、替代方案和 Trade-off 判断，不由标题数量或术语密度判断。

## Red / Blue

Red / Blue 有两层：

```text
docs/red-blue/       长期方法、正式说明、Round archive
.agent/red-blue/      machine protocol + temporary active state
```

正式执行只保留 `CHATGPT_AUTO` 和 `AGENT_AUTO`。用户可以中途 intervention，但没有第三个 human-candidate mode。

Red / Blue 产生的是 Findings，不是自动修改授权。重大 Architecture / Evidence / Ownership Finding 必须另开 bounded task，进入对应 Canonical Owner，merge 后再用不同场景或不同问法 Retest。

完整方法见 [`../../red-blue/README.md`](../../red-blue/README.md)。旧手工 Round 只保留在 [`../../red-blue/archive/legacy/`](../../red-blue/archive/legacy/) 复盘，不作为当前标准答案。

## 可导出的 Skills

稳定以后可以抽方法为 Skill，但 Skill 不携带与仓库竞争的 Zuno Truth。

优先级：

1. Red/Blue Architecture Review Harness；
2. Research → Architecture Traceability；
3. GitHub Architecture Review Closure；
4. Human-first Architecture Documentation Review。

Skill 运行时重新读取目标仓库、精确简历快照和当前 Evidence。不要把历史 Round、`.agent/red-blue/current.md` 或当前 Zuno Architecture 正文打包成通用 Skill。

## Current / Target 铁律

不得把：

- 设计文档 → 已实现；
- Demo / Pilot → Production；
- 团队/导师成果 → 个人实现；
- Framework capability → Zuno 自研；
- “应该可以” → “已经验证”。

需要时明确写 `Current / Target / Evidence / Unknown / Measurement Needed`。