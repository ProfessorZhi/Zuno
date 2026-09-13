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

Red / Blue 进一步把 GitHub 作为**运行时状态总线**：阶段之间不能靠聊天记忆直接交接，只消费已经提交到 Round branch 的 artifact。

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
→ docs/research/ 或对应 workflow evidence 记录 lineage / baseline / hypothesis
→ 判断 Writing Gap / Architecture Gap / Evidence Gap / Workflow Gap
→ 成熟结论进入对应 canonical owner
→ Current claim 仍需 evidence/
```

面经研究属于 Red Skill 的上游行为证据，不是 Zuno Product Truth，也不直接进入每轮 Red 上下文。

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

长期位置：

```text
docs/red-blue/             长期方法、行为证据与说明
docs/red-blue/workspace/   active Round
docs/red-blue/rounds/      closed Round archive
.agent/red-blue/            machine protocol + active state + Red Skill
```

正式执行只保留 `CHATGPT_AUTO` 和 `AGENT_AUTO`。

### GitHub-mediated lifecycle

每轮从固定 `main` SHA 创建 `red-blue/<round-id>` branch + Draft PR，所有阶段执行：

```text
read Round branch HEAD
→ read declared stage inputs
→ produce one stage output
→ update artifact + manifest + transcript
→ commit
→ next stage re-read new HEAD
```

用户评价也先进入 `07_user_feedback.md` / `08_session_transcript.md` 并提交。

### Resume-first sequence

```text
current Zuno docs / Evidence + prior resume style
→ Resume Builder 生成模拟简历
→ commit 冻结模拟简历
→ Red 只消费模拟简历 + JD + Red Skill + 通用知识
→ Red 生成 Interview Plan + Pressure Suite
→ USER_RED_REVIEW（校准期 REQUIRED）
→ APPROVE 后冻结 Red plan
→ Live answer-driven interview / Blue answers
→ Red 根据实际问答给 interviewer verdict
→ Blue 根据 docs 判断 Gap 类型
→ Workflow Retrospective 审 Red / Harness
→ archive / CI / merge / reread main
```

Red 不得把 `docs/project/`、`docs/architecture/`、`docs/modules/`、`docs/evidence/` 当作正式出题输入。

### Pressure Suite 不等于现场面试

保留 100 问 Pressure Suite，用于离线压力覆盖和 retrospective；现场不再预写固定 30 问 Primary Path。

Live Interview 使用少量 Seed + 动态追问：

```text
6–10 个 Seed
→ 听候选人回答
→ 抓刚出现的关键词 / 数字 / 选择 / 困难 / Ownership / bad case
→ 只选一个高信息增益 handle
→ 问一个主要意图
→ 继续或换 thread
```

深度来自连续短问。一个有价值 thread 可以持续多轮；一个 Claim 很快失去可信度就自然切走。Kill Switch 属于 Controller state，不作为口头问题展示。

真实面试也允许从项目直接切到网络、数据库、并发或算法基础，不需要把每一道基础题都强行包装成 Resume Claim 延伸。

### USER_RED_REVIEW

校准期用户主要检查：

- Seed 是否像真人会问；
- Branch Example 的下一问是否真的依赖上一答；
- 是否仍把 Reviewer rubric 拼成复合长问；
- 是否无信息增益地原子化；
- 是否有合理的 thread 深挖和 pivot。

用户可 `APPROVE / REQUEST_REVISION / ABORT`。只有 APPROVE 后 Blue 才能运行。

如果用户判断 Red Skill 本身需要结构性修改，当前 Round 可以 `SUPERSEDED`，失败题单保留，再独立修 Skill、开新 Round。

### 两种模式的边界

`CHATGPT_AUTO` 只拥有 `LOGICAL_GITHUB_MEDIATED` 隔离；同一聊天无法证明模型物理遗忘。`AGENT_AUTO` 只有在 Red 使用独立 context 时才可声明 `PHYSICAL_CONTEXT_ISOLATION` / strict blind Red。

Round 产生的是面试压力、回答、评价、Blue Reflection 和 Workflow Retrospective，不是自动修改授权。Architecture / Evidence / Ownership Finding 必须另开 bounded task 进入对应 Canonical Owner。

## 可导出的 Skills

稳定以后可以抽方法为 Skill，但 Skill 不携带与仓库竞争的 Zuno Truth。

Red Skill 应沉淀的是 interviewer behavior：先听、再追；Claim 取证；Ownership；Build/Buy；故障反例；Evidence；基础下钻；Simplification；以及何时停止一个 thread。它不应该打包 Zuno 当前 Architecture 正文，也不应该把历史 Blue 答案变成隐藏题库。

Skill 更新作为独立任务，从用户真实面试、公开面经和 Round retrospective 中提炼规律；更新后必须新 Round 验证。

## Current / Target 铁律

不得把：

- 设计文档 → 已实现；
- Demo / Pilot → Production；
- 团队/导师成果 → 个人实现；
- Framework capability → Zuno 自研；
- “应该可以” → “已经验证”。

需要时明确写 `Current / Target / Evidence / Unknown / Measurement Needed`。
