# PHASE01：Repo Layout 审计
> 状态：active / 三线程审计已合并，等待主线程决定进入 PHASE02。

## 目标

审计根目录、`src/backend/zuno`、`docs`、`.agent`、`tools`、`tests` 的杂乱点。

本 phase 要输出全仓目录清理表，而不是直接移动 runtime。至少覆盖：

- 根目录是否只保留必要入口和一等目录。
- `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 等是否属于本地产物、生成物、示例输入、正式证据或历史档案。
- `src/backend` 顶层是否只保留必要源码根；`src/backend/zuno` 内部如何对应 `api / agent / memory / capability / knowledge / platform`。
- `docs/`、`.agent/`、`tools/`、`tests/` 是否各自承担单一职责。
- 哪些目录应该保留、移动、归档、忽略或删除。

## 可并行线程

- root/docs audit：`thread-prompts/THREAD_A_root-docs-agent-hygiene-prompt.md`
- backend layout audit：`thread-prompts/THREAD_B_backend-six-layer-audit-prompt.md`
- tools/tests/generated artifacts audit：`thread-prompts/THREAD_C_tools-tests-generated-artifacts-prompt.md`

## 验收

给出清理表和迁移风险，不直接移动 runtime。

清理表至少包含：

```text
path | current role | target role | action | risk | verifier/test
```

## 三线程合并结果

本轮 PHASE01 使用三个独立 worktree / 分支完成只读审计。三个线程均未修改文件、未删除目录、未提交、未推送；主线程只合并审计结论。

```text
thread | branch | result | next phase
Thread A | codex/program3-thread-a-root-docs-agent-hygiene | root/docs/.agent 边界整体干净，但 reports/data 策略、docs architecture 前台状态承载、goal-mode 模板瘦身需要主线程决策 | PHASE02 / PHASE05
Thread B | codex/program3-thread-b-backend-six-layer-audit | src/backend 已有六层 facade 方向，但真实实现仍大量分布在 core/services/database/schema 等旧路径；不能直接大搬家，应先做 facade-first migration plan | PHASE03 / PHASE04
Thread C | codex/program3-thread-c-verifiers-tests | tools/tests/examples/infra 职责可解释，当前 verifier 绿；缺口是 generated artifacts、data/reports 白名单、tools/tests 子目录允许集还没有完全机器化 | PHASE05
```

## 合并清理表

```text
path | current role | target role | action | risk | verifier/test
/ | 当前只保留 .agent/apps/docs/examples/infra/src/tests/tools 等一等目录和入口文件 | 根目录少而稳定 | 保持，不做根目录大搬家 | 低 | python tools/scripts/verify_repo_structure.py
.codex/ | 当前不存在；.gitignore 已忽略 | 本地 Codex 状态 | 保持忽略，不进入 repo 前台 | 中 | python .agent/scripts/verify_repo_hygiene.py
.local/ | 当前不存在；.gitignore 已忽略 | 本地配置、运行状态、secret | 保持忽略 | 高 | python .agent/scripts/verify_repo_hygiene.py + tests/repo/test_repo_hygiene.py
.test-tmp/ | 当前不存在；.gitignore 已忽略 | 临时测试目录 | 保持忽略，PHASE05 固化 forbidden tracked prefix | 低 | tests/repo/test_repo_hygiene.py
node_modules/ | 当前不存在；.gitignore 已忽略 | 依赖安装产物 | 保持忽略 | 中 | python .agent/scripts/verify_repo_hygiene.py
reports/ | 当前不存在；仅部分 reports/evals 子路径被忽略 | 生成报告默认本地产物；正式证据进 docs/evidence | PHASE02 明确白名单策略，PHASE05 机器化 | 中 | verify_repo_hygiene.py / verify_repo_structure.py
data/ | 当前不存在；仅 eval/multihop 部分路径被忽略 | 原始或生成数据默认本地产物；示例进 examples 或 tools/evals | PHASE02 明确白名单策略，PHASE05 机器化 | 中到高 | verify_repo_hygiene.py / tests/repo/test_repo_hygiene.py
docs/ | 正式人类文档真相，history 已承载 Program 1/2 | current/target/roadmap/diagrams/decisions 清楚分工 | 保持；PHASE02 瘦身过细执行状态 | 中 | python tools/scripts/verify_docs_entrypoints.py
docs/architecture/README.md | 架构入口，也含 active phase / queued program 状态 | 架构入口只保留状态摘要并指向 roadmap | PHASE02 决策是否瘦身 | 中 | verify_docs_entrypoints.py
docs/architecture/target-architecture.md | 目标架构真相，也含执行 program 段 | 目标架构只写目标和非目标，不承担执行入口 | PHASE02 将执行细节迁到 roadmap 或 .agent/programs | 中 | tests/repo/test_docs_entrypoints.py
docs/history/programs/ | Program 1/2 和旧 program 归档 | 历史 program 证据库 | 保持 | 低 | verify_agent_system.py
.agent/ | 本地 Agent Skill System | skills/program/templates/scripts/design set | 保持 | 低 | python .agent/scripts/verify_agent_system.py
.agent/programs/ | 当前只承载 Program 3 active/pending phase 和 thread-prompts | 当前唯一 active program 平铺目录 | 保持；不要混入旧 program | 低 | tests/repo/test_agent_system.py
.agent/templates/goal-mode-prompt.md | 仍可能包含固定路径和历史事实 | 只放目标模式提示骨架 | PHASE02 或 PHASE05 清理并加断言 | 中 | verify_agent_system.py / tests/repo/test_agent_system.py
src/backend/fastapi_jwt_auth | 顶层兼容包 | platform/vendor compat 兼容壳 | 保留，不直接删除 | 高 | pytest -q tests/api/test_fastapi_jwt_auth_compat.py
src/backend/zuno/api schema middleware | API 和 contract 相关路径 | api 层，保持 public contract | 先做边界守卫，不物理大搬 | 高 | tests/api / tests/frontend/test_product_wiring_v1_api_contract.py
src/backend/zuno/core/agents services/workspace services/application/context | 当前 agent runtime 实现分布处 | agent 层 | PHASE03 写 facade-first plan，PHASE04 只做低风险 re-export | 高 | tests/agent/test_general_agent* / tests/repo/test_backend_facade_layers.py
src/backend/zuno/services/memory | memory first slice 实现 | memory 层 | 扩 facade/re-export，物理迁移后置 | 中 | tests/agent/test_memory_layers.py
src/backend/zuno/services/application/capabilities services/capability_registry | ToolCard / capability registry | capability 层 | 先 facade/re-export，不一次性移动 tool runtime | 中高 | tests/agent/test_capability_* / tests/tools
src/backend/zuno/services/graphrag services/retrieval services/rag | Knowledge / GraphRAG / retrieval/fusion | knowledge 层 | 扩 facade 覆盖面，GraphRAG/retrieval 物理迁移后置 | 高 | tests/graphrag / tests/retrieval / tests/evals
src/backend/zuno/database settings.py config services/storage services/queue services/llm mcp_servers vendor | DB、配置、模型/存储/队列/vendor 底座 | platform 层 | 最后迁移，先保持旧 module names | 高 | tests/legacy_guards/test_zuno_alias_imports.py
tools/ | 维护、verify、eval、render、launcher、migration 工具 | 工具入口清楚，子目录可解释 | PHASE05 固化 tools 子目录允许集 | 中 | verify_repo_structure.py / tests/repo/test_repo_structure_consistency.py
tests/ | 测试源；tests/repo 是仓库规则测试 | 测试和 repo guardrails | PHASE05 禁止 cache/generated tracked，并固定 tests 子目录职责 | 中 | tests/repo/test_repo_hygiene.py
examples/ | 可运行示例和示例数据 | 示例输入，不放运行输出 | PHASE05 明确 examples generated 输出去向 | 低到中 | verify_repo_structure.py
infra/ | DB/Docker 基础设施 | 部署和本地 infra 配置 | PHASE05 禁止运行态 volume/cache 混入 tracked | 中 | verify_repo_hygiene.py
```

## 主线程决策

1. `docs/architecture/README.md` 是否继续承载 active phase / queued program 状态。建议只保留摘要，把执行细节收敛到 `docs/architecture/roadmap.md` 和 `.agent/programs/current.md`。
2. `docs/architecture/target-architecture.md` 是否保留执行 program 段。建议只保留目标架构和非目标，执行计划迁出。
3. `data/` 和 `reports/` 是否根级整体忽略。建议不要粗暴忽略整目录，改成白名单语义：示例输入和正式证据可 tracked，运行生成数据和临时报告必须 ignored/local。
4. `.agent/templates/goal-mode-prompt.md` 模板瘦身放在 PHASE02 还是 PHASE05。建议 PHASE02 先清理，PHASE05 再机器化。

## 后续 Phase 输入

- PHASE02 输入：Thread A 的 root/docs/.agent 结果，重点处理 docs 前台瘦身、`data/` / `reports/` 白名单语义、模板瘦身。
- PHASE03 输入：Thread B 的 backend 六层映射，重点写 facade-first migration plan，不做 runtime 大搬家。
- PHASE04 输入：只执行 PHASE02/03 证明低风险的小边界清理，例如 facade / re-export、ignore 小补丁、已确认无引用的前台历史材料归档。
- PHASE05 输入：Thread C 的 guardrail 缺口，重点把目录职责、生成物禁止 tracked、tools/tests/examples/infra 子目录允许集写进 verifier 和 repo tests。
