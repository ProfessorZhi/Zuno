# Zuno Agent 入口

这是仓库唯一的 Agent 工作入口。先从问题本质和当前证据出发，不从旧目录、惯例或架构模板倒推答案；事实不清时保留 `UNKNOWN`，不要用 Target 设计填空。

## 正式文档 Owner

```text
docs/project/                         人类可读的项目故事入口（README、背景、团队、开发过程）
docs/architecture/                    总体 Target Architecture，固定四文件
docs/modules/                         九个冻结 Target 责任域的模块设计入口；仍需逐个建立正文
docs/decisions/                       仍然有效的长期 ADR
docs/evidence/                        当前代码、测试、Trace、Eval 和运行证据
docs/governance/project-fact-provenance.md  项目事实来源与表述边界
docs/governance/human-first-documentation-standard.md  Human-first 文档写作与分工规则
docs/history/red-blue/                Red / Blue 架构审查过程记录，不是事实或架构源
docs/operations/                      当前仍需执行的运维 Runbook / recovery profile
docs/terminology.md                   跨文档术语
.agent/                               Agent 路由、规则、Program 和验证入口
```

Git history 是普通文件演进和已删除工作区材料的考古来源。当前树不维护 `facts`、旧模块专题、旧 Program 垃圾场或第二套项目故事。

## 文档边界

- `docs/project/README.md` 是第一次进入项目故事时的简短导航。
- `docs/project/project-background.md` 回答项目为什么存在、研究与法院背景、用户问题、产品故事和仍未恢复的事实。
- `docs/project/team-and-contributions.md` 回答团队规模、用户何时加入、实际参与方向和个人职责边界。
- `docs/project/development-process.md` 回答项目如何从已有代码发展到 Agent、Memory/Context、Tool Calling、Demo、法院测试和 Pilot。
- `docs/governance/project-fact-provenance.md` 保存给 Reviewer / Agent 使用的项目事实来源边界；它不替代 Project 故事。
- `docs/architecture/architecture.md` 是唯一总体架构正文；`architecture-views.md` 与 `architecture.html` 是展示配对，不能拥有第二套架构事实。
- Red / Blue Archive 记录为什么质疑和怎样判断，不等于 Architecture Truth、Current Evidence、ADR 或实施授权。接受的结果必须写回 `docs/architecture/` 或 `docs/decisions/`。
- `Current` 由代码、测试和 Evidence 证明；`Target` 是设计；`Future` 是可选方向；`History` 只解释过去。`Pilot` 不等于 `Production`。

## 必读顺序

一般项目、架构或文档任务：

1. `docs/README.md`
2. `docs/project/README.md`
3. `docs/project/project-background.md`
4. `docs/project/team-and-contributions.md`
5. `docs/project/development-process.md`
6. `docs/architecture/architecture.md`：理解系统时先读 Part A；实现、测试、Migration、Recovery、Contract 或 Security 时再读 Part B。
7. 需要看图时同时读 `architecture-views.md` 与 `architecture.html`
8. `docs/modules/README.md`、相关 ADR、`docs/evidence/README.md` 和 `docs/governance/human-first-documentation-standard.md`
9. `.agent/README.md`、`.agent/system.yaml`、`.agent/references/`

只有任务明确询问架构为什么这样演进、历史攻击或上一轮判断时，才读取 `docs/history/red-blue/` 的指定 Round，不默认加载全部原始记录。

实现任务必须在读完 Part A、Part B、相关 ADR、Evidence 和 Governance 规则后再读代码。不要把类名、目录、依赖、Mock、目标文档或测试存在当成生产证据；不能只依据 Part A 实施工程细节。

## 架构文档治理

`docs/architecture/` 只能有：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

跨层含义变化时修改 `architecture.md`；图形变化时同步图源和 HTML，再运行 `python tools/agent/render_architecture.py --write`、`--check` 以及文档验证。不要创建 `.agent/architecture/` 或模块镜像。

Round 02 已冻结九个 Target 责任域并打开 Module Decomposition Gate。可以在独立 Module Design 任务中逐个创建模块正文，但不要因为 Gate Open 就自动实现全部模块，也不要把逻辑模块直接当作服务或数据库。

## Red / Blue 规则

Red / Blue 是人工协调的 Architecture Stress Test。它可以讨论 Multi-Agent、Runtime、Knowledge 等复杂边界，但不把工程协作多线程写成 Zuno Runtime 事实。每轮应保留 Scope、Baseline SHA、Red Questions、Blue Answers、Red Review、Main Judgment、开放问题和（如有）架构修订 Commit SHA。原始记录进入 `docs/history/red-blue/`；它只解释“为什么改”，不回答“现在是什么”。

FACT GAP 要回到用户确认和 `docs/project/`；Architecture Gap 才能进入架构修订。不得将 Red Concern、Blue Proposal 或 Round 内容自动实现。

## 修改、验证和提交

- 不修改业务代码、数据库、Migration、依赖或安全边界，除非用户明确授权。
- 不覆盖用户已有未提交修改；提交前检查 `git status --short`，只暂存本任务范围。
- 文档修改完成后至少运行 `git diff --check`、文档入口、内部链接、结构、Agent 路由和边界验证；按风险运行 focused tests。
- 真实修改任务必须验证、Commit、Push，除非明确阻塞；只读审计不提交。
- 不声称 `FULL CI PASSED`，除非完整 CI 确实执行并通过。

常用命令：

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

更多路由见 `.agent/references/task-routing.md` 和 `.agent/references/workflow.md`。
当前 Program 状态见 `.agent/references/current-program.md`；验证地图见 `.agent/references/verification-map.md`；机器路由见 `.agent/system.yaml`。
