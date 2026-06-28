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

## 工作模式

Zuno 本地执行默认只有两种模式：挂机模式和多线程模式。这里的多 agent 是 Codex 执行工作流里的协作方式，不是把 Zuno runtime 改成多 Agent 架构；Zuno 近期 runtime 主线仍是 Single GeneralAgent。

线程可以常驻为“工位”，但每轮任务的隔离边界不是线程标题，而是本轮绑定或切换到的独立 worktree 和 `codex/` 分支。每轮开始都必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。主线程可以自己以目标模式/计划模式执行，也可以作为 coordinator 把粗粒度任务分给常驻线程并行执行。

### 挂机模式

- 主线程必须是真正的 Codex UI 目标模式。
- 适合单一连续任务、共享文件较多、风险需要集中控制，或用户希望主线程一路执行到底的场景。
- 主线程自己完成计划、实现、验证、提交和推送。
- 主线程可以在同一目标范围内使用多 agent / subagent 辅助审计或实现，但主线程仍负责最终判断、diff 审查和验证。

### 多线程模式

- 主线程必须是真正的 Codex UI 目标模式，并只做 coordinator：拆任务、给目标模式提示词、限定范围、分配分支、跟踪进度、审查结果、解决冲突、跑集成验证和最终合并。
- 子线程任务必须粗粒度；每个线程都要执行一大块互相独立的工作，不为很小的编辑拆线程。
- 主线程先盘点可复用 Codex 线程和 git worktree，再决定复用还是新建。
- 有合适可复用线程就复用；没有合适线程才创建新线程。复用线程必须先换到或确认本轮独立 worktree 和独立 `codex/` 分支，不能沿用上轮分支继续新任务。
- 复用或新建线程后必须改线程标题，让侧边栏能看出本轮任务、phase 和职责。
- 每个子线程必须使用独立 worktree 或独立 Codex 线程，并在独立 `codex/` 分支上工作。
- 每个子线程也必须是真正的 Codex UI 目标模式。提示词里写“目标模式”不等于 UI 目标模式。
- 如果当前工具 API 不能为新线程打开 Codex UI 目标模式，主线程不能把该线程当作目标模式线程；只能输出线程提示词，等待用户在 UI 里手动创建目标模式线程，或改为挂机模式。
- 子线程目标模式提示词默认要求线程内开启多 agent 模式；只有当任务共享文件高冲突、禁止并行或用户明确要求单线程时，才在提示词里写明禁用原因。
- 每个子线程默认允许在自己的范围内开启多 agent 模式，但只能处理互相独立的子任务，不能让多个 agent 同时改同一批文件。
- 线程内开启多 agent 模式时，必须保持同一线程的目标、范围、禁止范围和验收闸门不变。
- 多线程提示词统一放在 `.agent/programs/thread-prompts/`，不要和 `PHASE*.md` 混放。下一轮提示词更新时默认替换或清理旧提示词；只有用户明确要求归档时才归档。
- 并行线程必须有不重叠或明确可合并的写入范围；共享文件如 `AGENTS.md`、`.agent/system.yaml`、核心 verifier、README 由主线程收口。
- 每个线程完成前必须验证、提交、推送；主线程不能只信线程总结，必须读 diff、检查提交、运行集成验证后再合并。
- 多线程模式适合 docs / `.agent` / tools / tests / facade 这类可拆任务；涉及 schema、public API、数据库、runtime 主循环或同一大文件拆分时，先做只读审计再决定是否并行。

## 当前主线

已完成的 Phase 0-6 架构收口是历史完成事实，不能改写成未完成。

当前可执行 Agent 程序：

- `.agent/programs/`

当前目标：停止继续堆 runtime feature，先按短期五个 program 分批收口成熟项目封面。Program 1 和 Program 2 已完成；当前 active program 是 Program 3：`zuno-repo-layout-cleanup-v1`。

最新完成程序归档在：

- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

当前 program：

- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/current.md`
- `.agent/programs/PHASE01_repo-layout-audit.md`
- `.agent/programs/PHASE02_root-docs-hygiene.md`
- `.agent/programs/PHASE03_backend-six-layer-migration-plan.md`
- `.agent/programs/PHASE04_small-boundary-cleanups.md`
- `.agent/programs/PHASE05_hygiene-verifier-closure.md`
- `.agent/programs/closure-checklist.md`

当前 active phase 是 `PHASE01_repo-layout-audit.md`。它适合按 root/docs、backend layout、tools/tests/generated artifacts 三个线程并行审计。

后续 queued programs：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

归档 V1 / 旧清理材料：

- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

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

## Program Closure 自维护审查

每个 program 结束前必须做一次 workflow / docs self-review。它不是可选总结，而是归档、提交和推送前的收尾闸门。

必须检查：

1. `AGENTS.md` 是否需要更新。
2. `.agent/system.yaml` 的 route、docs_sync、verify 是否需要更新。
3. `.agent/references/` 是否有新的 skill、lesson、pitfall 或 debug playbook 要沉淀。
4. `.agent/templates/` 是否需要新增或修正执行骨架。
5. `.agent/programs/` 是否只保留当前 active program，或处于明确等待状态。
6. completed program 是否已归档到 `docs/history/programs/`。
7. `docs/architecture/current-architecture.md` 是否仍只写 Current。
8. `docs/architecture/target-architecture.md` 是否需要吸收新的目标边界。
9. `docs/architecture/roadmap.md` 是否反映最新状态。
10. verifier / tests 是否覆盖新规则，避免下次漂移。

如果用户提醒“以后注意”，不能只留在对话里。要判断它属于临时提醒、可复用经验、稳定规则、任务路由、全仓硬规则还是机器可检查规则，并分别沉淀到 `.agent/local/`、`.agent/references/`、`AGENTS.md`、`.agent/system.yaml` 或 verifier/test。

## 范围规则

本工作流文档不授权广泛代码修改。必须遵守任务给出的禁止路径。如果验证需要修改禁止路径，停止并返回证据，不扩大范围。
