# Zuno Agent 入口

这是仓库唯一的 Agent 入口和工作流契约。

## 第一性原则

从当前任务和问题本质出发，不从旧 phase 习惯或模板出发。

如果用户动机或目标不清晰，先澄清会改变工作的关键决策。如果目标清晰但路径更长，直接指出并选择更短路径。遇到问题先追根因，不打补丁。每个决策都要能回答“为什么”。

## 本地工作流模型

```text
AGENTS.md
  -> 唯一总入口：边界、阅读顺序、任务路由、收尾规则

.agent/
  -> Zuno Local Agent Skill System
     references/    本地项目 skills、lessons、playbooks、任务路由和已知坑
     architecture/  目标架构设计工作集
     programs/      当前平铺执行计划、当前状态、各 phase 文件和收口清单
     templates/     skill 执行模板和报告骨架
     scripts/       过渡期保留的验证器；长期自动化目标位置是 tools/agent 与 tools/verify

docs/
  -> 面向人的正式文档真相

docs/history/
  -> 完成、过时或被替换的历史档案
```

`AGENTS.md` 不承载所有细节。它只负责把任务路由到 `.agent/references/`、`.agent/architecture/` 和 `.agent/programs/` 中正确的位置。

## 文档语言规则

- 前台文档默认中文。
- 新增或重写的 `docs/`、`.agent/` Markdown 必须用中文说明目标、状态、边界、执行步骤和验收。
- 英文术语可以保留，但必须用中文解释其边界。
- `docs/history/` 是历史证据库，可以保留原文，不为了翻译而改写历史。

## 来源边界

- `docs/`：正式人类文档真相。
- `AGENTS.md`：仓库级 Agent 入口和工作流契约。
- `.agent/`：Zuno 本地 Agent Skill System，保存项目级 skills、执行计划、目标设计和模板。
- `docs/history/`：过时计划、旧程序、退休迁移说明和被替换设计的归档。

正式结论必须进入 `docs/`。只给 Agent 使用的导航、可复用提示和辅助脚本放在 `.agent/`。历史材料移动到 `docs/history/`，不要因为它不再当前有效就删除。

## 必读顺序

架构、重构、新功能或工作流任务先读：

1. `docs/architecture/README.md`
2. `docs/architecture/current-architecture.md`
3. `docs/architecture/target-architecture.md`
4. `docs/architecture/roadmap.md`
5. `.agent/README.md`
6. `.agent/system.yaml`
7. `.agent/references/current-program.md`
8. `.agent/references/docs-map.md`
9. `.agent/references/code-map.md`
10. `.agent/references/task-routing.md`
11. `.agent/references/workflow.md`
12. `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
13. `.agent/architecture/near-term/01-target-runtime-architecture.md`
14. `.agent/architecture/near-term/02-context-memory-architecture.md`
15. `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
16. `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
17. `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`

实现任务在读完相关文档后再读代码。不要只凭文档推断 runtime 行为。

## 任务路由

- 范围不清楚 -> `.agent/references/task-routing.md` 的只读审计路由。
- `docs`、`.agent`、参考资料、历史档案 -> `.agent/references/workflow.md` 的文档维护流程。
- 目录移动、删除、归档、忽略规则、生成物和本地缓存清理 -> `.agent/references/workflow.md` 的仓库卫生流程。
- `apps/web` -> `apps/web/AGENTS.md` 和 `.agent/references/code-map.md`。
- `src/backend/zuno` -> `src/backend/zuno/AGENTS.md` 和 `.agent/references/runtime-call-chain.md`。
- API、DTO、请求/响应、前后端契约 -> `.agent/references/code-map.md`。
- 架构替换 -> `.agent/references/workflow.md` 的架构重构流程。
- 架构替换、目录移动、上下文/记忆、GraphRAG 边界或仓库卫生任务还必须读 `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`。
- Eval 工具、数据集、指标、配置档和报告 -> `tools/evals/zuno/AGENTS.md` 和 `.agent/references/verification-map.md`。

## 当前主线

已完成的 Phase 0-6 架构收口是历史完成事实，不能改写成未完成。

当前可执行 Agent 程序：

- `.agent/programs/`

当前目标：停止继续堆 runtime feature，先完成成熟项目封面化、分层目录计划、本地 Agent Skill System、tools/tests 防回归和架构图展示收口。

最新完成程序归档在：

- `docs/history/programs/zuno-target-architecture-migration-v1/`

当前 program：

- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/current.md`
- `.agent/programs/PHASE01_public-architecture-surface.md`
- `.agent/programs/PHASE02_local-agent-skill-system.md`
- `.agent/programs/PHASE03_tools-tests-guardrails.md`
- `.agent/programs/PHASE04_backend-facade-layers.md`
- `.agent/programs/PHASE05_large-file-light-split.md`
- `.agent/programs/PHASE06_architecture-diagrams-html.md`
- `.agent/programs/closure-checklist.md`

归档 V1 / 旧清理材料：

- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
- `docs/history/programs/zuno-target-runtime-v2/`

目标架构设计工作集：

- `.agent/architecture/near-term/`
- `.agent/architecture/future/`
- `.agent/architecture/decisions/`

不要把 Java、微服务、事件驱动 worker 或多 Agent 模式当作近期实现工作，除非用户明确打开未来方向实现程序。

## 自维护规则

每次新需求、新功能、重构或架构替换，都判断是否需要同步：

1. `.agent/programs/`
2. 平铺 phase 文档；每个新 program 从 `PHASE01` 开始，旧 active phase 文件从当前前台移除
3. 规格、ADR 或审计
4. `docs/history/`
5. `docs/architecture/README.md`
6. `docs/architecture/current-architecture.md`
7. `docs/architecture/target-architecture.md`
8. `AGENTS.md`
9. `.agent/references/current-program.md`
10. `.agent/references/docs-map.md`
11. `.agent/references/task-routing.md` 或 `.agent/references/workflow.md`
12. `.agent/programs/`
13. `.agent/system.yaml`、`.agent/references/` skill 文件或 `.agent/templates/`
14. `.gitignore`
15. 如果产生修改，运行验证、提交、推送

如果旧设计被替换，把旧材料归档到 `docs/history/`，不要留在前台路径里，也不要静默删除。

## 任务收尾规则

- 只读侦察不提交、不推送。
- 修改任务必须运行最小有效验证。
- 修改任务结束时提交并推送，除非验证或推送被阻塞。
- 不要强制推送、带租约强制推送或修改旧提交，除非用户明确要求。
- 不要保留旧的小写或点号形式 Agent 入口与 `AGENTS.md` 并行。
- 只有根入口路由到的模块才允许有模块级 `AGENTS.md`。

## 范围规则

本工作流文档不授权广泛代码修改。必须遵守任务给出的禁止路径。如果验证需要修改禁止路径，停止并返回证据，不扩大范围。
