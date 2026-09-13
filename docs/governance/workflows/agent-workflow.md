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

Red / Blue 有三块长期位置：

```text
docs/red-blue/             长期方法与说明
docs/red-blue/workspace/   active Round，一轮一个文件夹
docs/red-blue/rounds/      closed Round archive
.agent/red-blue/            machine protocol + temporary active state
```

正式执行只保留 `CHATGPT_AUTO` 和 `AGENT_AUTO`。用户可以中途 intervention，但没有第三个 human-candidate mode。

当前正式协议是 **resume-first**：

```text
current Zuno docs / Evidence + prior resume style
→ Resume Builder 生成本轮模拟简历
→ 冻结模拟简历
→ Red 只看模拟简历 + JD + Red Interview Skill + 模型通用知识
→ Blue 才读取 Zuno docs 回答
→ Red 只根据简历与回答给 interviewer verdict
→ Blue 根据文档判断 Resume / Narrative / Architecture / Evidence / Ownership / Fundamental Gap
→ Workflow Retrospective 反过来审 Red 问题质量和 Harness
→ 用户反馈归档
→ Round close
```

Red 不得读取 `docs/project/`、`docs/architecture/`、`docs/modules/`、`docs/evidence/` 后再按答案出题。真实面试官通常只看到简历；让 Red 预读 Zuno docs 会把模拟变成 Architecture Review。

每轮默认可以批量生成 100 问，但一轮只产生这一批。修复或复测必须新建 Round，并重新生成与当时文档对应的模拟简历。

Round 产生的是面试压力、回答、评价、Blue Reflection 和 Workflow Retrospective，不是自动修改授权。重大 Architecture / Evidence / Ownership Finding 必须另开 bounded task，进入对应 Canonical Owner，merge 后再开新 Round Retest。

用户对 Red 题目质量的评价属于正式输入。用户明确认为“问题没含金量、太像 Reviewer、重复、没全链路”时，后续 `06_workflow_retrospective.md` 必须优先分析 Red Skill / Persona / question budget / context firewall，而不是只归因于 Blue。

完整方法见 [`../../red-blue/README.md`](../../red-blue/README.md)，Active Workspace 见 [`../../red-blue/workspace/README.md`](../../red-blue/workspace/README.md)。旧手工 Round 只保留在 [`../../red-blue/archive/legacy/`](../../red-blue/archive/legacy/) 复盘，不作为当前标准答案。

## 可导出的 Skills

稳定以后可以抽方法为 Skill，但 Skill 不携带与仓库竞争的 Zuno Truth。

优先级：

1. Resume-first Red Interview Skill；
2. Research → Architecture Traceability；
3. GitHub Architecture Review Closure；
4. Human-first Architecture Documentation Review。

Red Skill 应沉淀的是 interviewer behavior：Claim 取证、精品思维、全链路追踪、Ownership、Build/Buy、故障反例、Evidence、基础下钻和 Simplification。它不应该打包 Zuno 当前 Architecture 正文，也不应该把历史 Blue 答案变成出题模板。

Skill 更新应作为独立任务，从用户真实面试、公开面经和 Round workflow retrospective 中提炼规律；更新完成后用新 Round 验证。

## Current / Target 铁律

不得把：

- 设计文档 → 已实现；
- Demo / Pilot → Production；
- 团队/导师成果 → 个人实现；
- Framework capability → Zuno 自研；
- “应该可以” → “已经验证”。

需要时明确写 `Current / Target / Evidence / Unknown / Measurement Needed`。