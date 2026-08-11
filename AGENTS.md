# Zuno Agent 入口

这是仓库唯一的 Agent 入口和工作流契约。

## 第一性原则

从当前任务和问题本质出发，不从旧 Phase 习惯或模板出发。

如果用户动机或目标不清晰，先澄清会改变工作的关键决策；目标清晰时选择最短的可靠路径。遇到问题先追根因，不打补丁。每个重要决策都要能回答“为什么”。

## 本地工作流模型

```text
AGENTS.md
  -> 唯一总入口：边界、阅读顺序、任务路由、收尾规则

.agent/
  -> Zuno Local Agent Skill System
     references/    本地项目 skills、lessons、playbooks、任务路由和已知坑
     programs/      当前执行计划、状态、Phase 和收口清单
     templates/     执行模板和报告骨架
     scripts/       过渡期验证器

project-red-blue/
  -> 项目级 Red/Blue Lab：事实采集、项目模型、红队攻击、蓝队提案和 Skill 契约；不拥有正式架构事实。

docs/
  project/          Zuno 项目知识唯一正式入口
    facts/          已知事实、未知事实和证据路由
    architecture/   总架构正文与架构图展示配对
    product/        产品架构
    domain/         法律 Domain Model 与生命周期
    agents/         Agent / Multi-Agent Runtime
    knowledge/      Knowledge / Evidence
    services/       Service Boundary
    data/           Data Ownership / Recovery
    security/       Security Architecture
    eval/           Legal Eval / Benchmark
    deployment/     Microservice Deployment
  status/          Current 与差距
  decisions/       ADR
  governance/      Ownership 和文档治理
  evidence/        可复现证据
  history/         完成、过时或被替换的历史档案
```

`AGENTS.md` 不承载所有细节，只负责把任务路由到正确的正式文档、Reference、Program 和验证入口。

`docs/project/README.md` 是项目知识入口：`facts/` 回答项目事实上发生了什么，`architecture/` 回答跨层为什么这样设计，Product/Domain/Agents/Knowledge/Services/Data/Security/Eval/Deployment 回答各 Canonical Question。事实不确定时必须保留 `UNKNOWN`，不能用 Target Architecture 代替历史事实。

## 文档语言规则

- 前台文档默认中文。
- 新增或重写的 `docs/`、`.agent/` Markdown 必须用中文说明目标、状态、边界、执行步骤和验收。
- 英文术语可以保留，但必须用中文解释其边界。
- `docs/history/` 只保存经过批准的历史摘要，可以保留原文，不为翻译而改写历史。

## 来源边界

- `docs/`：正式人类文档真相。
- `AGENTS.md`：仓库级 Agent 入口和工作流契约。
- `.agent/`：本地 Agent Skill System、Reference、Program 和模板；不保存架构或模块正文镜像。
- `project-red-blue/`：项目级红蓝实验区，维护项目事实、攻击协议、Gap 和会话摘要；不替代 `docs/` 的正式事实源。
- `docs/history/`：历史归档。

正式结论必须进入 `docs/`。只给 Agent 使用的导航、可复用提示和辅助脚本放在 `.agent/`。
`docs/history/` 保存批准的历史摘要；已完成 Program 的 raw construction materials 可以在
摘要完成、明确授权且 Git commit 可追溯时从 current tree 移除。未提交内容、未合并提交、
Migration、benchmark evidence 和用户文件不得未经明确 disposition 删除。

项目根目录必须保持干净。临时截图、PDF 预览、测试产物、本地报告和缓存不得遗留在根目录；正式附件放入对应 `docs/**/assets/`，临时调试产物放入 `.local/` 或 `tmp/`。

## Architecture Documentation Governance

### 总架构目录

以下两个目录都只能保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

```text
docs/project/architecture/
```

职责：

- `docs/project/architecture/architecture.md`：跨 Product、Domain、Logical Capability、Physical Service/Deployment 的总架构，说明 Agent 闭环、Contract、状态、失败语义和验收。
- `docs/project/architecture/architecture-views.md` 与 `docs/project/architecture/architecture.html`：不可拆分的架构图展示配对；前者提供图源，后者负责展示，二者不拥有独立架构事实。
- `docs/project/architecture/README.md`：目录边界和维护方式。
- `.agent/` 不再保存总架构或模块镜像；Agent 通过 `docs/` 唯一正式文档源读取架构事实。

禁止把模块设计、Production Readiness、ADR、Program、Ownership Matrix 或实施计划放入 architecture 目录。

### Canonical 专题设计

- `docs/project/README.md`：Product/Domain/Agents/Knowledge/Services/Data/Security/Eval/Deployment 入口。
- `docs/project/<topic>/*.md`：每份文档声明 Canonical Question、Owner、依赖、替代关系和状态边界。
- `docs/project/modules/`：上一阶段 11 模块的 Superseded 迁移材料，不再是新 Target 事实源。

专题规范优先级：全局原则 → 对应专题 Owner 文档 → ADR/共享 Contract → Program → 代码与 Migration。

### 项目事实

- `docs/project/README.md`：项目知识总入口和事实、架构、模块的路由规则。
- `docs/project/facts/README.md`：事实文档写作、状态标签和证据边界。
- `docs/project/facts/`：项目背景、团队与 Ownership、开发演进、交付使用、技术现实；未知信息必须明确标记，不得由红蓝工作区的候选假设直接升级为正式事实。

模块文档可以很详细，但必须服从总架构的 Owner 边界，不得把 Target 冒充为 Current。Agent Core Target 文档不承载 Current Baseline、实现 Phase、Cutover 或具体迁移计划；这些内容必须进入 `.agent/programs/`。

### 状态、决策和治理

- `docs/status/production-readiness.md`：Current、Gap、Measurement Blocked、Completed、Future Optional。
- `docs/decisions/`：正式 ADR。
- `docs/governance/`：Repository Ownership、文档治理和工程边界。
- `docs/evidence/`：代码、测试、Trace、Eval 和可复现运行证据。

### 架构同步

架构文档的统一信息架构和写作规则见 `docs/governance/architecture-document-writing-standard.md`。它是文档治理规范，不是新的架构事实源；总架构和专题正文分别由 `docs/project/architecture/` 与 `docs/project/<topic>/` 持有。

设计含义变化时：

1. 更新 `docs/project/architecture/architecture.md`；
2. 图形关系变化时，把 `architecture-views.md` 与 `architecture.html` 作为一个展示配对同步更新；
3. 运行 `python tools/agent/render_architecture.py --write`；
4. 运行 `python tools/agent/render_architecture.py --check`；
5. 运行 `python tools/scripts/verify_docs_entrypoints.py`。
6. 运行 `python tools/scripts/verify_markdown_internal_links.py`。
7. 运行 `python tools/scripts/verify_architecture_writing_standard.py`。
8. 运行 `python tools/scripts/verify_architecture_human_readability.py`。

专题变化时：

1. 更新对应 `docs/project/<topic>/<document>.md`；
2. `docs/` 是架构和模块的唯一正式事实源，不维护 `.agent` 镜像；
3. 更新 `docs/status/production-readiness.md` 只能写已经由实现和证据证明的 Current 变化；
4. 更新测试和验证器；
5. Agent Core 变更运行 `python tools/scripts/verify_agent_core_target_protocols.py`。

总架构 Markdown 必须比展示配对更充实；展示配对只用于图形理解。图数量由读者问题决定，不以旧模块数量或固定图数证明完整性。

阅读路由：用户问“为什么这样设计”时优先读总体架构和对应专题；用户要求实现、修改或验证时，必须继续读取 Owner 专题、ADR/共享 Contract、Current Status 和当前 Program。每份专题只维护自己的 Canonical Question，不创建跨文档重复状态机。

## Current / Target / Future / History

- Current：代码、测试、Trace/Eval 或 Verifier 已证明的事实。
- Target：近期准备实现的目标。
- Future：长期可选方向，不是短期 Blocker。
- History：完成、过时或被替换的材料。

不得把类名、目录、Docker 声明、Mock Test 或目标文档当作生产完成证据。

## 必读顺序

架构、重构、新功能或工作流任务先读：

1. `docs/project/README.md`
2. 与任务对应的 `docs/project/facts/*.md`
3. `docs/project/architecture/architecture.md`
4. `docs/project/architecture/architecture-views.md`
5. `docs/project/architecture/architecture.html`
6. `docs/project/README.md` 的 Canonical Taxonomy（例如 `docs/project/product/product-architecture.md`）
7. 与任务对应的 `docs/project/<topic>/<document>.md`
8. `docs/status/production-readiness.md`
9. `.agent/README.md`
10. `.agent/system.yaml`
11. `.agent/references/current-program.md`
12. `.agent/references/docs-map.md`
13. `.agent/references/code-map.md`
14. `.agent/references/task-routing.md`
15. `.agent/references/workflow.md`
16. `.agent/references/debugging.md`
17. `.agent/references/known-pitfalls.md`
18. `.agent/references/verification-map.md`

`architecture-views.md` 与 `architecture.html` 只在需要查看或维护架构图时作为一个整体打开；它们不是必读的文字事实源。

Agent Runtime 任务必须读取 `docs/project/agents/agent-platform.md`、`docs/project/agents/multi-agent-runtime.md`、`docs/project/domain/`、`docs/project/services/` 和 `docs/project/data/` 的相关文档。

实现任务在读完相关文档后再读代码。不要只凭文档推断 Runtime 行为。

## 任务路由

- 范围不清楚 → `.agent/references/task-routing.md` 的只读审计路由。
- 文档、`.agent`、History、README → `.agent/references/workflow.md` 的文档维护流程。
- 项目红蓝队、项目事实、落地真实性或个人贡献 → `project-red-blue/README.md` 的项目红蓝工作流。
- 目录移动、删除、归档、忽略规则和缓存清理 → 仓库卫生流程。
- `apps/web` → `apps/web/AGENTS.md` 和 `.agent/references/code-map.md`。
- `src/backend/zuno/agent/**` → `docs/project/agents/`、Domain、Services、Data。
- `src/backend/zuno/knowledge/**` → `docs/project/knowledge/`、Domain、Eval。
- `src/backend/zuno/memory/**` → `docs/project/agents/agent-platform.md` 与 Domain boundary。
- `src/backend/zuno/capability/**` → `docs/project/agents/agent-platform.md`、Services、Security。
- API、DTO、请求/响应、前后端契约 → Code Map 和 Product Surface 边界。
- Eval 工具、数据集、指标和报告 → `tools/evals/zuno/AGENTS.md` 和 Verification Map。

## 工作模式

Zuno 本地执行只有两类主模式：挂机模式和多线程模式。Codex 的多 Agent 协作不等于 Zuno Product Runtime；Zuno Target 允许 Composable Multi-Agent，但 Agent profiles 不自动形成独立服务，当前代码仍按 Current Evidence 表述。

### 挂机模式

适用于共享文件多、风险集中、需要连续端到端收口的任务：

- 主线程作为真正的 Codex UI 目标模式执行到底；
- 主线程可以在线程内使用多 Agent；
- 主线程负责实现、验证、提交和推送。

### 多线程模式

适用于可按写入范围安全并行的粗粒度任务：

- 主线程是 Coordinator；
- 子线程必须由用户在 UI 中创建真正的目标模式线程；
- 提示词里写“目标模式”不等于 UI 目标模式；
- 优先复用已有线程槽和 Worktree，没有合适槽位才新建；
- 子任务必须写清目标、范围、禁止范围、验收闸门和验证命令；
- 子线程默认允许内部多 Agent 协作；
- 子线程必须使用独立 Worktree 和 Branch；
- 子线程完成后 Commit 并 Push；
- 主线程负责审查 Diff、合并冲突、跑集成验证和最终提交。

完整子线程提示词写入 `.agent/programs/thread-prompts/`，下一轮计划默认替换或清理旧提示词。

## 修改与验证规则

- 修改任务必须验证、Commit、Push，除非被明确阻塞。
- 只读侦察不 Commit、不 Push。
- 不允许仅凭“看起来正确”宣称完成。
- 数据库、公开 API、依赖升级和安全边界变化属于 Stop Condition，需要明确确认。
- 外部副作用必须有审批、幂等和审计。
- 大型重构优先采用 Expand / Migrate / Verify / Contract，而不是一次性 Bulk Move。

常用验证：

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_deep_dive_architecture.py
python tools/scripts/verify_architecture_interview_qa.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_agent_core_target_protocols.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```

## Agent Workflow Self-Maintenance

长期工作方式要求必须判断是否写回：

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/*`
- `.agent/templates/*`
- `.agent/programs/*`
- `docs/project/architecture/*`
- `docs/project/product/*`, `domain/*`, `agents/*`, `knowledge/*`, `services/*`, `data/*`, `security/*`, `eval/*`, `deployment/*`
- `docs/status/*`
- 对应 Verifier 和 Tests

一次性用户指令不必沉淀；可复用规则、架构治理规则、Codex 执行规则和文档模板规则必须进入相应事实源。

## 禁止

- 不在 `docs/project/architecture/` 增加第五个文件，也不重新创建 `.agent/architecture/` 或 `.agent/modules/` 镜像目录。
- 不把模块专题放回 Architecture 目录。
- 不把 Product Runtime 改成无治理的自治 Agent Society；Multi-Agent 必须服从 Domain、Security、Budget、Review 和 Eval Contract。
- 不把隐藏思维链保存进 Trace、Memory 或数据库。
- 不绕过 Security、Approval、Budget 或 Idempotency。
- 不把 Target 或 Future 写成 Current。
- 不以“目录干净”为理由删除历史证据；只有完成摘要、明确授权且可由 Git commit 追溯的
  raw construction materials 才能退出 current tree。
