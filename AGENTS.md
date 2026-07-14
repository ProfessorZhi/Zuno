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
     architecture/  总架构四个 canonical 镜像文件
     modules/       逻辑模块实施级设计镜像
     programs/      当前执行计划、状态、Phase 和收口清单
     templates/     执行模板和报告骨架
     scripts/       过渡期验证器

docs/
  architecture/    总架构四个 canonical 文件
  modules/         十一个逻辑模块设计
  status/          Current 与差距
  decisions/       ADR
  governance/      Ownership 和文档治理
  evidence/        可复现证据
  history/         完成、过时或被替换的历史档案
```

`AGENTS.md` 不承载所有细节，只负责把任务路由到正确的正式文档、Reference、Program 和验证入口。

## 文档语言规则

- 前台文档默认中文。
- 新增或重写的 `docs/`、`.agent/` Markdown 必须用中文说明目标、状态、边界、执行步骤和验收。
- 英文术语可以保留，但必须用中文解释其边界。
- `docs/history/` 是历史证据库，可以保留原文，不为翻译而改写历史。

## 来源边界

- `docs/`：正式人类文档真相。
- `AGENTS.md`：仓库级 Agent 入口和工作流契约。
- `.agent/`：本地 Agent Skill System、镜像、Reference、Program 和模板。
- `docs/history/`：历史归档。

正式结论必须进入 `docs/`。只给 Agent 使用的导航、可复用提示和辅助脚本放在 `.agent/`。历史材料移动到 `docs/history/`，不要因为不再当前有效就删除。

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
docs/architecture/
.agent/architecture/
```

职责：

- `docs/architecture/architecture.md`：重文字目标总架构，说明“轻量实现、成熟设计”、十一逻辑模块、六个物理运行域、Agent 闭环、Contract、状态、失败语义和验收。
- `docs/architecture/architecture-views.md`：十类 canonical views 的 Mermaid 规范图源。
- `docs/architecture/architecture.html`：读取独立图源的原生 Mermaid Architecture Atlas。
- `docs/architecture/README.md`：目录边界和维护方式。
- `.agent/architecture/`：上述正式总架构的 Agent 镜像，不是独立事实源。

禁止把模块设计、Production Readiness、ADR、Program、Ownership Matrix 或实施计划放入 architecture 目录。

### 模块设计

- `docs/modules/README.md`：十一个逻辑模块入口。
- `docs/modules/<number>-<module>.md`：单个模块实施级设计。
- `.agent/modules/`：需要被 Agent System 高频读取的模块镜像。
- Agent Core 唯一正式 Target 文档：`docs/modules/06-agent-core-planning-control.md`。
- Agent Core 唯一镜像：`.agent/modules/06-agent-core-planning-control.md`。
- Tool Runtime 唯一正式 Target 文档：`docs/modules/08-tool-runtime.md`。
- Tool Runtime 唯一镜像：`.agent/modules/08-tool-runtime.md`。

Agent Core 规范优先级：全局架构原则 → 单一模块 Target 架构文档 → Program → 代码与 Migration。

Tool Runtime 规范优先级：全局架构原则 → ADR 0003 / Wave 1 Registry → `docs/modules/08-tool-runtime.md` → Program → 代码与 Migration。第 08 模块不得新增第二份 `08-*` 设计文档。

模块文档可以很详细，但必须服从总架构的 Owner 边界，不得把 Target 冒充为 Current。Agent Core 和 Tool Runtime Target 文档不承载 Current Baseline、实现 Phase、Cutover 或具体迁移计划；这些内容必须进入 `.agent/programs/`。

### 状态、决策和治理

- `docs/status/production-readiness.md`：Current、Gap、Measurement Blocked、Completed、Future Optional。
- `docs/decisions/`：正式 ADR。
- `docs/governance/`：Repository Ownership、文档治理和工程边界。
- `docs/evidence/`：代码、测试、Trace、Eval 和可复现运行证据。

### 架构同步

设计含义变化时：

1. 更新 `docs/architecture/architecture.md`；
2. 图形关系变化时更新 `architecture-views.md`；
3. 运行 `python tools/agent/render_architecture.py --write`；
4. 运行 `python tools/agent/render_architecture.py --check`；
5. 运行 `python tools/scripts/verify_docs_entrypoints.py`。

模块变化时：

1. 更新对应 `docs/modules/<module>.md`；
2. 若存在 `.agent/modules` 镜像，同步全部镜像；
3. 更新 `docs/status/production-readiness.md` 只能写已经由实现和证据证明的 Current 变化；
4. 更新测试和验证器；
5. Agent Core 变更运行 `python tools/scripts/verify_agent_core_target_protocols.py`；
6. Tool Runtime 变更运行 `python tools/scripts/verify_tool_runtime_target_protocols.py`。

总架构 Markdown 必须比 HTML 更充实；HTML 偏图形展示。禁止把三十张详细图重新堆回 `architecture.md`。

## Current / Target / Future / History

- Current：代码、测试、Trace/Eval 或 Verifier 已证明的事实。
- Target：近期准备实现的目标。
- Future：长期可选方向，不是短期 Blocker。
- History：完成、过时或被替换的材料。

不得把类名、目录、Docker 声明、Mock Test 或目标文档当作生产完成证据。

## 必读顺序

架构、重构、新功能或工作流任务先读：

1. `docs/architecture/architecture.md`
2. `docs/architecture/architecture-views.md`
3. `docs/architecture/architecture.html`
4. `docs/modules/README.md`
5. 与任务对应的 `docs/modules/<module>.md`
6. `docs/status/production-readiness.md`
7. `.agent/architecture/architecture.md`
8. `.agent/modules/README.md`
9. `.agent/README.md`
10. `.agent/system.yaml`
11. `.agent/references/current-program.md`
12. `.agent/references/docs-map.md`
13. `.agent/references/code-map.md`
14. `.agent/references/task-routing.md`
15. `.agent/references/workflow.md`
16. `.agent/references/project-map.md`
17. `.agent/references/architecture-docs-map.md`
18. `.agent/references/documentation-governance.md`
19. `.agent/references/architecture-update-policy.md`
20. `.agent/references/diagram-inventory.md`
21. `.agent/references/current-target-future-rules.md`
22. `.agent/references/verification-map.md`

Agent Core 任务必须读取唯一正式 Target 文档 `docs/modules/06-agent-core-planning-control.md`。

Tool、CLI、OpenAPI、HTTP API、Provider SDK、MCP Tool、Browser、代码执行、异步 Job、Tool Attempt、Effect、Reconciliation 或工具旁路任务必须读取唯一正式 Target 文档 `docs/modules/08-tool-runtime.md`，以及 ADR 0003 和 Wave 1 Registry。

实现任务在读完相关文档后再读代码。不要只凭文档推断 Runtime 行为。

## 任务路由

- 范围不清楚 → `.agent/references/task-routing.md` 的只读审计路由。
- 文档、`.agent`、History、README → `.agent/references/workflow.md` 的文档维护流程。
- 目录移动、删除、归档、忽略规则和缓存清理 → 仓库卫生流程。
- `apps/web` → `apps/web/AGENTS.md` 和 `.agent/references/code-map.md`。
- `src/backend/zuno/agent/**` → Agent Core 单一模块 Target 文档、Runtime Call Chain 和 Code Map。
- `src/backend/zuno/knowledge/**` → Knowledge 模块文档和 Retrieval Reference。
- `src/backend/zuno/memory/**` → Memory 模块文档。
- `src/backend/zuno/capability/**` → 先区分 07 Capability / Skill 与 08 Tool Runtime；Tool 定义、执行、Adapter、Attempt、Effect 和 Reconciliation 读取 `docs/modules/08-tool-runtime.md`。
- `src/backend/zuno/platform/services/mcp/**`、`mcp_openai/**`、用户定义 CLI/OpenAPI 执行路径 → Tool Runtime Target 和迁移旁路清单。
- API、DTO、请求/响应、前后端契约 → Code Map 和 Product Surface 边界。
- Eval 工具、数据集、指标和报告 → `tools/evals/zuno/AGENTS.md` 和 Verification Map。

## 工作模式

Zuno 本地执行只有两类主模式：挂机模式和多线程模式。这里的多 Agent 是 Codex 执行工作流协作方式，不改变 Zuno Runtime 的 Single Controller 主线。

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
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_agent_core_target_protocols.py
python tools/scripts/verify_tool_runtime_target_protocols.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_agent_core_target_protocols.py tests/repo/test_tool_runtime_target_protocols.py -p no:cacheprovider
```

## Agent Workflow Self-Maintenance

长期工作方式要求必须判断是否写回：

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/*`
- `.agent/templates/*`
- `.agent/programs/*`
- `docs/architecture/*`
- `docs/modules/*`
- `docs/status/*`
- 对应 Verifier 和 Tests

一次性用户指令不必沉淀；可复用规则、架构治理规则、Codex 执行规则和文档模板规则必须进入相应事实源。

## 禁止

- 不恢复 `docs/architecture/` 或 `.agent/architecture/` 的第五个文件。
- 不把模块专题放回 Architecture 目录。
- 不为 Module 08 新增第二份正式或镜像设计文档。
- 不把 Product Runtime 改成默认自治 Multi-Agent。
- 不把隐藏思维链保存进 Trace、Memory 或数据库。
- 不绕过 Security、Approval、Budget 或 Idempotency。
- 不把 Target 或 Future 写成 Current。
- 不删除历史证据来制造“目录干净”。
