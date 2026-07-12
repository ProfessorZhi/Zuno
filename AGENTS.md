# Zuno Agent 入口

这是仓库唯一的 Agent 入口和工作流契约。

## 第一性原则

从当前问题和目标本质出发，不从旧 Phase、旧实现或模板出发。重要决策必须回答：为什么、谁拥有事实、失败如何传播、如何恢复、如何验证。

## 本地工作流模型

```text
AGENTS.md
  -> 唯一总入口：边界、阅读顺序、任务路由、收尾规则

.agent/
  references/    本地 skills、lessons、playbooks 和路由
  architecture/  总架构四个 canonical 镜像文件
  modules/       逻辑模块 Target 镜像
  programs/      实现和迁移 Program
  templates/     执行模板
  scripts/       文档和边界验证器

docs/
  architecture/  总架构四个 canonical 文件
  modules/       十一个逻辑模块 Target 设计
  status/        Current、Gap 和 Measurement
  decisions/     ADR
  governance/    Ownership 和文档治理
  evidence/      可复现证据
  history/       完成、过时或被替换的历史档案
```

`AGENTS.md` 只负责路由，不承载全部设计细节。

## 文档语言与来源边界

- 前台文档默认中文；英文术语首次出现时说明边界。
- `docs/` 是正式人类文档真相。
- `.agent/` 是 Agent Skill System、镜像、Reference、Program 和模板。
- `docs/history/` 保存历史证据，不因过时而删除。
- 临时产物不得遗留在仓库根目录。

## Architecture Documentation Governance

### 总架构目录

以下两个目录只能包含四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

```text
docs/architecture/
.agent/architecture/
```

职责：

- `architecture.md`：总架构文字事实源；
- `architecture-views.md`：canonical Mermaid 图源；
- `architecture.html`：图形化 Architecture Atlas；
- `README.md`：目录边界和维护规则；
- `.agent/architecture/`：正式总架构的字节级镜像。

禁止把模块专题、Current、ADR、Program、Ownership Matrix 或实施计划放入 architecture 目录。

### 模块设计

- `docs/modules/README.md`：十一个逻辑模块入口；
- `docs/modules/<number>-<module>.md`：模块 Target 设计；
- `.agent/modules/`：Agent System 高频读取的模块镜像。

Agent Core Target 由三份正式文档共同构成：

```text
docs/modules/06-agent-core-planning-control.md
docs/modules/06-agent-core-control-protocols.md
docs/modules/06-agent-core-consistency-lifecycle-protocols.md
```

对应镜像：

```text
.agent/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-control-protocols.md
.agent/modules/06-agent-core-consistency-lifecycle-protocols.md
```

规范优先级：

```text
全局架构原则
→ Agent Core 规范性协议
→ Agent Core 主设计实施规格
→ Program 与代码
```

Agent Core 文档必须保持 Target-only，不得混入 Current Baseline 或具体迁移计划。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```

### 状态、决策和治理

- `docs/status/production-readiness.md`：Current、Gap、Measurement Blocked、Completed、Future Optional；
- `docs/decisions/`：正式 ADR；
- `docs/governance/`：Ownership 和文档治理；
- `docs/evidence/`：代码、测试、Trace、Eval 和可复现运行证据。

### 同步规则

设计含义变化时：

1. 更新正式文档；
2. 同步所有 `.agent` 镜像；
3. 图形关系变化时更新 architecture views 和 HTML；
4. 更新入口、验证器和测试；
5. 搜索旧路径和失效 Contract；
6. 报告实际验证和未运行验证。

模块变化时不得直接把 Target 写入状态文档。只有工程证据证明的 Current 变化才能进入 `docs/status/production-readiness.md`。

## Current / Target / Future / History

- Current：代码、Migration、测试、Trace、Eval 或运行证据证明的事实；
- Target：已确认但未必实现的目标；
- Future：长期可选方向；
- History：完成、过时或被替换的材料。

不得把类名、目录、Docker 声明、Mock、目标表结构或设计文档当作实现完成证据。

## 必读顺序

架构、重构、新功能或工作流任务先读：

1. `docs/architecture/architecture.md`
2. `docs/architecture/architecture-views.md`
3. `docs/modules/README.md`
4. 与任务相关的模块正式文档
5. `docs/status/production-readiness.md`
6. 对应 `.agent/modules/` 镜像
7. `.agent/system.yaml`
8. `.agent/references/docs-map.md`
9. `.agent/references/code-map.md`
10. `.agent/references/task-routing.md`
11. `.agent/references/workflow.md`
12. `.agent/references/verification-map.md`

Agent Core 任务必须同时读取三份 Agent Core Target 文档，不能只读取主设计。

实现任务在读完 Target 和 Current 后再读代码，不得只凭文档推断 Runtime 行为。

## 任务路由

- 文档、`.agent`、History、README → 文档维护流程；
- `src/backend/zuno/agent/**` → Agent Core 三份 Target 文档、Runtime Call Chain 和 Code Map；
- `src/backend/zuno/knowledge/**` → Knowledge 模块和 Retrieval Reference；
- `src/backend/zuno/memory/**` → Memory 模块；
- `src/backend/zuno/capability/**` → Capability / Skill 模块；
- API 和前后端 DTO → Product Surface 与 Code Map；
- Eval、数据集、指标和报告 → Eval AGENTS 和 Verification Map。

## Agent Core 固定原则

```text
Zuno 是 Agent，Graph 是控制系统
Single Controller Agent Runtime
所有任务都有 Plan
固定 AgentRunGraph + 动态 Plan DAG + 固定 StepExecutionGraph
模型只产生 Proposal
Retry 与 Replan 分离
PlanVersion 激活后不可变
并行 Worker 只返回 BranchResultRef
多 Interrupt 与 Signal
副作用 Prepare / Approve / Claim / Execute / Reconcile
FinalCandidate / ArtifactVersion / Publication / RunOutcome 分离
PostgreSQL 保存领域事实，Checkpointer 保存图控制状态
```

任何实现不得绕过 Plan、Trace、Budget、Security、Approval、AnswerPolicy、Final Gate 或 Publication。

## 工作模式

本地执行可使用挂机模式或多线程模式；这里的多 Agent 是 Codex 工程协作方式，不改变 Zuno Runtime 的 Single Controller 主线。

- 主线程负责架构、集成审查和最终验证；
- 子线程使用独立 Worktree 和 Branch；
- 子任务必须说明允许和禁止范围、Contract、状态、失败、恢复和验收；
- 子线程完成后 Commit 和 Push；
- 主线程审查 Diff、合并冲突和运行集成验证。

## 修改与验证规则

- 修改前读取最新 `main`、目标文件 SHA、入口、镜像和活跃引用；
- 不覆盖并发修改；
- 只修改确认范围；
- 修改后同步镜像、入口、验证器和测试；
- 未运行完整 CI 时不得声称 CI 通过；
- 验证失败必须如实报告。

常用验证：

```text
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_agent_core_target_protocols.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```

## 禁止

- 不恢复 architecture 目录的第五个文件；
- 不把模块专题放回 architecture 目录；
- 不把 Product Runtime 改为默认自治 Multi-Agent；
- 不保存隐藏思维链；
- 不绕过 Security、Approval、Budget、Idempotency 或 Publication；
- 不把 Target 或 Future 写成 Current；
- 不删除历史证据来制造目录干净。
