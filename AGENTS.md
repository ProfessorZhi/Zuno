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

项目根目录必须保持干净，只保留稳定项目入口和配置。临时截图、浏览器截图、PDF 预览、测试产物、本地报告和缓存不得遗留在根目录；正式附件放入对应 `docs/**/assets/`，临时调试产物放入 `.local/` 或 `tmp/`。

## Architecture Documentation Governance

Zuno 的架构文档由 `docs/architecture/architecture.md`、`docs/architecture/architecture.html`、`.agent/architecture/architecture.md`、`.agent/architecture/architecture.html` 和 `.agent/references/` 共同治理。

- `docs/architecture/` 是人类可读的正式架构说明，也是 public architecture source。
- `docs/architecture/architecture.md` 是正式总架构文档，用自然语言说清当前事实、目标分层、主链路、企业私有知识库场景、文档解析、Memory、Tool、RAG / GraphRAG、安全、评测和实施落点；同一文件后半部分维护十类 Mermaid 架构视图。
- `docs/` 应少而精，保留相对稳定、面向人的正式结论；不要把高频变化的执行细节、图清单、workflow change log 或 Agent 操作规则塞进 `docs/`。
- `docs/architecture/architecture.html` 是正式架构 HTML 展示页，不是唯一事实来源；它必须由 `docs/architecture/architecture.md` 和 `tools/agent/render_architecture.py` 生成。
- `.agent/architecture/architecture.md` 是 Agent 侧总架构镜像，必须与 `docs/architecture/architecture.md` 完全一致。
- `.agent/architecture/architecture.html` 是 Agent 侧 HTML 镜像，必须与 `docs/architecture/architecture.html` 由同一个 Markdown 源生成。
- `.agent/references/` 是 Agent-facing operating memory，保存项目地图、文档治理、图清单、更新策略和 Current / Target / Future / History 规则，不替代正式文档。
- `.agent/` 可以承载更细、更常变化的 Agent 工作流、执行计划、模板、治理索引和调试 playbook；这些内容不应和 `docs/` 重复展开。
- `.agent/templates/` 是文档、图和变更记录的生成骨架，不保存项目事实。
- `.agent/programs/` 是当前执行状态和 program 生命周期入口。仓库当前不启用 `.agent/plans/`；如未来引入，必须先更新 `AGENTS.md`、`.agent/system.yaml`、verifier 和 tests。

涉及架构、Agent Runtime、RAG、GraphRAG、Memory、Tool Layer、Hooks、Trace、Eval、部署、中间件或前后端契约的改动，必须检查是否同步：

1. `docs/architecture/architecture.md`
2. `docs/architecture/architecture.html`
3. `.agent/architecture/architecture.md`
4. `.agent/architecture/architecture.html`
5. `docs/architecture/README.md`
6. `.agent/architecture/README.md`
7. `.agent/references/*`
8. `.agent/templates/*`
9. `.agent/programs/current.md`，有 active program 时还要检查对应 roadmap；no-active 时检查最近归档 program 的 roadmap
10. `README.md` 中的架构摘要

架构结论必须区分 Current、Target、Future、History。Current 只写代码、测试和可复现结果已经证明的事实；Target 是近期目标；Future 是长期方向；History 是完成、过时或被替换的方案。禁止把 Target 或 Future 写成 Current。

总架构 Markdown 内容必须比架构 HTML 更充实：Markdown 负责大段文字设计、Current / Target 边界、实施落点和 Mermaid 图源；HTML 偏图形展示和全屏查看。改任何架构正文或图源时，先改 `docs/architecture/architecture.md`，再运行 `python tools/agent/render_architecture.py --write` 同步 `.agent/architecture/architecture.md`、`docs/architecture/architecture.html` 和 `.agent/architecture/architecture.html`。

## Agent Workflow Self-Maintenance

AGENTS.md 和 `.agent/references/` 共同组成 Zuno 的 Agent 工作流系统。AGENTS.md 是 boot entry 和规则路由层，应保持精炼；`.agent/references/` 是 operating memory，保存详细工作流规则、更新策略、图清单、模板边界和长期要求。

工作流不是静态规则。当用户提出新的长期工作方式要求，例如 Agent 如何维护文档、更新架构图、同步 HTML、管理 Codex 轮次、保留证据、区分 Current / Target / Future / History，Agent 必须判断该要求是否需要写回：

- `AGENTS.md`
- `.agent/references/*`
- `.agent/templates/*`
- `.agent/programs/*`
- `docs/architecture/*`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.html`

Agent 必须区分一次性用户指令、可复用项目规则、架构治理规则、Codex 执行规则、文档模板规则和长期工作流规则。长期工作流规则必须沉淀到 `.agent/references/`；影响未来生成内容时，必须同步更新 `.agent/templates/`；能机器检查的规则必须同步 verifier 或 repo tests。

最终成品按两个层次表达：对外是五个成熟系统：Agent 工作流文档系统、元工作流自我维护系统、正式架构文档系统、架构 HTML 展示系统、干净清晰且可验证的代码结构。内部验收拆成八大交付物：Agent 工作流文档系统、元工作流自我维护系统、模板与执行计划系统、正式架构文档系统、架构 HTML 展示系统、完善的 Zuno 目标架构、清晰干净的代码和目录、一致性与验证系统。

## 必读顺序

架构、重构、新功能或工作流任务先读：

1. `docs/architecture/architecture.md`
2. `docs/architecture/architecture.html`
3. `.agent/architecture/architecture.md`
4. `.agent/architecture/architecture.html`
5. `docs/architecture/README.md`
6. `.agent/architecture/README.md`
7. `.agent/README.md`
8. `.agent/system.yaml`
9. `.agent/references/current-program.md`
10. `.agent/references/docs-map.md`
11. `.agent/references/code-map.md`
12. `.agent/references/task-routing.md`
13. `.agent/references/workflow.md`
14. `.agent/references/project-map.md`
15. `.agent/references/architecture-docs-map.md`
16. `.agent/references/documentation-governance.md`
17. `.agent/references/architecture-update-policy.md`
18. `.agent/references/diagram-inventory.md`
19. `.agent/references/current-target-future-rules.md`
20. `.agent/references/workflow-governance.md`
21. `.agent/references/workflow-update-policy.md`
22. `.agent/references/workflow-maintenance-checklist.md`

实现任务在读完相关文档后再读代码。不要只凭文档推断 runtime 行为。

## 任务路由

- 范围不清楚 -> `.agent/references/task-routing.md` 的只读审计路由。
- `docs`、`.agent`、参考资料、历史档案 -> `.agent/references/workflow.md` 的文档维护流程。
- 目录移动、删除、归档、忽略规则、生成物和本地缓存清理 -> `.agent/references/workflow.md` 的仓库卫生流程。
- `apps/web` -> `apps/web/AGENTS.md` 和 `.agent/references/code-map.md`。
- `src/backend/zuno` -> `.agent/references/code-map.md` 和 `.agent/references/runtime-call-chain.md`。
- API、DTO、请求/响应、前后端契约 -> `.agent/references/code-map.md`。
- 架构替换 -> `.agent/references/workflow.md` 的架构重构流程。
- 架构替换、目录移动、上下文/记忆、GraphRAG 边界或仓库卫生任务还必须读 `docs/architecture/architecture.md` 和 `.agent/architecture/architecture.md`，不得引用已归档旧工作集作为当前入口。
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
- 主线程必须在生成、改写或投递线程提示词之前完成线程盘点；不能先写一堆提示词再回头找线程。
- 主线程不能在主对话里直接粘贴完整子线程提示词；完整提示词必须写入 `.agent/programs/thread-prompts/`，主对话只报告线程盘点结果、提示词文件路径和下一步动作。
- 有合适可复用线程就复用；没有合适线程才创建新线程。复用线程必须先换到或确认本轮独立 worktree 和独立 `codex/` 分支，不能沿用上轮分支继续新任务。
- 复用或新建线程后必须改线程标题，让侧边栏能看出本轮任务、phase 和职责。
- 每个子线程必须使用独立 worktree 或独立 Codex 线程，并在独立 `codex/` 分支上工作。
- 每个子线程也必须是真正的 Codex UI 目标模式。提示词里写“目标模式”不等于 UI 目标模式。
- 如果当前工具 API 不能为新线程打开 Codex UI 目标模式，主线程不能把该线程当作目标模式线程；只能输出线程提示词，等待用户在 UI 里手动创建目标模式线程，或改为挂机模式。
- 子线程目标模式提示词默认要求线程内开启多 agent 模式；只有当任务共享文件高冲突、禁止并行或用户明确要求单线程时，才在提示词里写明禁用原因。
- 每个子线程默认允许在自己的范围内开启多 agent 模式，但只能处理互相独立的子任务，不能让多个 agent 同时改同一批文件。
- 线程内开启多 agent 模式时，必须保持同一线程的目标、范围、禁止范围和验收闸门不变。
- 多线程提示词统一放在 `.agent/programs/thread-prompts/`，不要和 `PHASE*.md` 混放。下一轮提示词或临时多线程执行方案更新时，默认替换或清理旧提示词和旧临时执行方案；只有用户明确要求归档时才归档。正式 completed program 的归档规则仍按 `docs/history/programs/` 执行。
- 并行线程必须有不重叠或明确可合并的写入范围；共享文件如 `AGENTS.md`、`.agent/system.yaml`、核心 verifier、README 由主线程收口。
- 每个线程完成前必须验证、提交、推送；主线程不能只信线程总结，必须读 diff、检查提交、运行集成验证后再合并。
- 多线程模式适合 docs / `.agent` / tools / tests / facade 这类可拆任务；涉及 schema、public API、数据库、runtime 主循环或同一大文件拆分时，先做只读审计再决定是否并行。

## 当前主线

已完成的 Phase 0-6 架构收口是历史完成事实，不能改写成未完成。

当前可执行 Agent 程序：

- `.agent/programs/`

当前没有 active program。最近完成并归档的 program 是 `zuno-target-architecture-runtime-full-implementation-v1`，归档位置是 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。它不是继续细化架构，也不是再做一轮 contract foundation，而是把 Zuno 从“目标架构已定义、contracts 已成型”推进到“目标架构第一版 runtime 闭环真实可跑”。核心闭环是：上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback。每个 runtime phase 只有在真实 API / runtime / UI 路径、focused tests、trace / eval 或 verifier 证明后才能关闭；只写 contract、schema 或 README 不能关闭 runtime phase。PHASE03 已完成 workspace / session / file / ingest / task / approval / event / artifact / feedback 后端 API 与 SSE runtime surface；PHASE04 已完成 Document Ingestion / Parse Gateway runtime owner surface；PHASE05 已完成本地 BM25 / vector / graph index job runtime；PHASE06 已完成 controller-node 级 durable Single Controller runtime surface；PHASE07 已完成 snapshot / SQLModel-backed memory runtime 与 GeneralAgent 接入；PHASE08 已完成本地 deterministic Tool Control Plane、工具级 approval / sandbox / credential ref / audit runtime 和最小前端审批入口；PHASE09 已完成 Agentic Retrieval / Evidence / Citation runtime 与 cited artifact 闭环；PHASE10 已完成 Security、Observability 与 release eval 在 workspace task runtime 的闭环；PHASE11 已把 Web workspace Agent 模式接入 file / ingest / task / SSE / approval / artifact / trace-eval / feedback 产品闭环；PHASE12 已完成 release gate、归档和 no-active 收口。

最近完成并归档的 program 是 `zuno-master-architecture-implementation-v1`；它已完成 PHASE01-PHASE12，覆盖项目文件夹与代码布局治理、企业知识库产品闭环、Document Ingestion、Single Controller runtime harness、Memory、Tool Control Plane、Agentic GraphRAG / Evidence / Citation、Security Governance、Eval / Observability、Architecture Markdown / HTML refresh 和 release closure。归档位置是 `docs/history/programs/zuno-master-architecture-implementation-v1/`。`zuno-architecture-detail-and-execution-plan-v1` 已完成架构文档、架构图、HTML 和执行计划细化。`zuno-eight-deliverables-full-realization-v1` 仍是八大交付物闭环的历史完成事实。Program 4 / `zuno-six-layer-internalization-v1` 已完成并归档，它不是完整 runtime architecture upgrade。

最新完成程序归档在：

- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
- `docs/history/programs/zuno-six-layer-internalization-v1/`
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`

当前 `.agent/programs/` 处于 no-active 等待态，只保留：

- `.agent/programs/current.md`
- `.agent/programs/README.md`

最近完成的 `zuno-target-architecture-runtime-full-implementation-v1` 已归档。本轮 PHASE01-PHASE12 已完成，当前 `.agent/programs/` 处于 no-active 等待态。

Program 3 final alias surface closure 已完成：`src/backend/` 顶层只保留 `zuno/`；`src/backend/zuno` 顶层目录只保留 `api / agent / memory / capability / knowledge / platform`；根级零碎 `.py` alias 文件退休；旧 public import path 通过 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。

Program 4 已完成的边界：六层内部已有第一批无副作用薄入口、README、focused tests 和 verifier guard。它不表示 GeneralAgent 主循环、DB schema、API 行为、eval baseline、production memory、dynamic capability orchestration、retrieval fusion 或 model gateway runtime 已完成。

以下 queued programs 已被 `zuno-eight-deliverables-full-realization-v1` 吸收为近期实现参考；它们仍保留为未来参考输入，不再是当前执行入口：


归档 V1 / 旧清理材料：

- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

目标架构设计工作集：

- `.agent/architecture/architecture.md`

不要把 Java、微服务、事件驱动 worker 或多 Agent 模式当作近期实现工作，除非用户明确打开未来方向实现程序。

## 自维护规则

每次新需求、新功能、重构或架构替换，都判断是否需要同步：

1. `.agent/programs/`
2. 平铺 phase 文档；每个新 program 从 `PHASE01` 开始，旧 active phase 文件从当前前台移除
3. 规格、ADR 或审计
4. `docs/history/`
5. `docs/architecture/README.md`
6. `docs/architecture/architecture.md`
7. `docs/architecture/architecture.html`
8. `.agent/architecture/architecture.md`
9. `.agent/architecture/architecture.html`
10. `AGENTS.md`
11. `.agent/references/current-program.md`
12. `.agent/references/docs-map.md`
13. `.agent/references/task-routing.md` 或 `.agent/references/workflow.md`
14. `.agent/programs/`
15. `.agent/system.yaml`、`.agent/references/` skill 文件或 `.agent/templates/`
16. `.gitignore`
17. 如果产生修改，运行验证、提交、推送

如果旧设计被替换，把旧材料归档到 `docs/history/`，不要留在前台路径里，也不要静默删除。

## 任务收尾规则

- 只读侦察不提交、不推送。
- 修改任务必须运行最小有效验证。
- 修改任务结束时提交并推送，除非验证或推送被阻塞。
- 不要强制推送、带租约强制推送或修改旧提交，除非用户明确要求。
- 不要保留旧的小写或点号形式 Agent 入口与 `AGENTS.md` 并行。
- 模块级 `AGENTS.md` 只保留在确实需要局部规则且不会污染目标目录表达的位置。

## Program Closure 自维护审查

每个 program 结束前必须做一次 workflow / docs self-review。它不是可选总结，而是归档、提交和推送前的收尾闸门。

必须检查：

1. `AGENTS.md` 是否需要更新。
2. `.agent/system.yaml` 的 route、docs_sync、verify 是否需要更新。
3. `.agent/references/` 是否有新的 skill、lesson、pitfall 或 debug playbook 要沉淀。
4. `.agent/templates/` 是否需要新增或修正执行骨架。
5. `.agent/programs/` 是否只保留当前 active program，或处于明确等待状态。
6. completed program 是否已归档到 `docs/history/programs/`。
7. `docs/architecture/architecture.md` 的 Current / Target / Future / History 是否仍严格区分。
8. `.agent/architecture/architecture.md` 是否与 `docs/architecture/architecture.md` 完全一致。
9. 两个 `architecture.html` 是否由同一个 Markdown 源生成且可通过渲染校验。
10. verifier / tests 是否覆盖新规则，避免下次漂移。

如果用户提醒“以后注意”，不能只留在对话里。要判断它属于临时提醒、可复用经验、稳定规则、任务路由、全仓硬规则还是机器可检查规则，并分别沉淀到 `.agent/local/`、`.agent/references/`、`AGENTS.md`、`.agent/system.yaml` 或 verifier/test。

## 范围规则

本工作流文档不授权广泛代码修改。必须遵守任务给出的禁止路径。如果验证需要修改禁止路径，停止并返回证据，不扩大范围。
