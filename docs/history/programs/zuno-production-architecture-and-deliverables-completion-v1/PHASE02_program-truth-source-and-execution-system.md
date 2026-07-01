# PHASE02 Program Truth Source and Execution System

status: completed

completed_at: 2026-07-01
next_phase: PHASE03_workflow-self-maintenance-automation

## 目标

冻结 active program 真相源、phase gate、多线程执行规则、thread prompt 位置、commit/push 节奏和 verifier 期望，避免再次出现旧文档与当前 program 双轨。

## 范围

- 同步 `.agent/programs/current.md`、`.agent/programs/README.md`、`.agent/references/current-program.md`、`AGENTS.md`、`README.md`。
- 检查 `.agent/system.yaml`、workflow verifier、repo tests 对 active program 的约束。
- 如果启用多线程模式，先盘点可复用线程和 worktree，再写 `.agent/programs/thread-prompts/`。

## 禁止范围

- 不为小编辑拆线程。
- 不把提示词里的“目标模式”当成 Codex UI 目标模式。
- 不让多个线程同时大改同一目录或共享文件。

## 验收闸门

- 所有 program 状态入口一致指向本 program 和当前 phase。
- verifier / tests 能检查 active program 文件和 phase 顺序。
- 多线程提示词规则和共享文件收口 owner 明确。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py -p no:cacheprovider
```

## 需要先读取

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/system.yaml`
- `.agent/references/current-program.md`
- `AGENTS.md`
- `README.md`

## 需要修改的文件

- `.agent/programs/*`
- `.agent/references/current-program.md`
- `.agent/system.yaml`
- `AGENTS.md`
- `README.md`
- `tools/scripts/verify_repo_structure.py`
- `tools/scripts/verify_docs_entrypoints.py`
- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify-workflow.ps1`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_repo_structure_consistency.py`
- `tests/repo/test_publish_boundary.py`

## 执行拆解

1. 确认 active program、current phase、phase 文件列表和 roadmap 完全一致。
2. 确认 `.agent/programs/` 只保存当前 active program，不混入旧 program 或临时 thread prompt。
3. 更新 verifier/test 让 active program 文件集、phase section、closure checklist 成为机器检查项。
4. 明确多线程模式：主线程负责共享文件和集成验证，worker 只能改不重叠范围。
5. 为每个 phase 写明 commit/push 节奏、验证命令和 rollback/blocked 报告方式。

## 多 agent 分工

- Thread A：检查 `.agent/programs`、`.agent/references/current-program.md`、`.agent/system.yaml`。
- Thread B：检查 `README.md`、`AGENTS.md`、docs entrypoint。
- Thread C：检查 verifier 和 tests 是否覆盖 active program。
- 主线程：统一修改共享入口、运行完整 repo verification。

## 需要返回的证据

- active program 文件清单。
- verifier/test 覆盖清单。
- 多 worktree / 多 agent 执行分工。
- 每个 phase 的共享文件 owner。

## PHASE02 完成证据

本 phase 冻结 active program truth source 和 phase gate，不修改 Zuno runtime 行为。

### active program 文件清单

`.agent/programs/` 当前只保存 active program 的平铺执行文件，没有 `thread-prompts/` 临时目录或旧 active program phase 文件：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `PHASE01_production-maturity-gap-audit.md`
- `PHASE02_program-truth-source-and-execution-system.md`
- `PHASE03_workflow-self-maintenance-automation.md`
- `PHASE04_documentation-dedup-architecture-clarity.md`
- `PHASE05_repo-ownership-and-compatibility-retirement.md`
- `PHASE06_product-surface-desktop-recovery-loop.md`
- `PHASE07_production-parse-and-index-platform.md`
- `PHASE08_durable-agent-runtime-persistence.md`
- `PHASE09_memory-context-production-governance.md`
- `PHASE10_tool-sandbox-vault-network-runtime.md`
- `PHASE11_production-graphrag-evidence-citation.md`
- `PHASE12_security-trace-eval-release-closure.md`

### verifier / test 覆盖清单

PHASE02 处理了 PHASE01 暴露的 verifier truth-source gap：

- `.agent/system.yaml` 的 docs-agent route verify list 已纳入 `python tools/scripts/verify_docs_entrypoints.py`。
- PHASE02 验证命令已纳入 `python tools/scripts/verify_docs_entrypoints.py`，因为该 verifier 是 production-readiness summary boundary 和 retired front-path 的关键 guard。
- `verify_agent_system.py` 与 `verify_repo_structure.py` 不再硬编码单个 `current_phase`，改为读取 `.agent/programs/current.md`，检查 current phase 属于 PHASE01-PHASE12，并检查 phase status 顺序：已过 phase 必须 `completed`，当前 phase 必须 `active`，后续 phase 必须 `pending`。
- `verify_docs_entrypoints.py` 与 repo tests 不再把 architecture current phase 固定为某个 phase 名，而是读取 `.agent/programs/current.md` 的 current phase。
- `verify-workflow.ps1` 继续检查 active program 名和 `current_phase: PHASE##_*` 形状；详细 phase order 由 Python verifiers 负责。

### 执行分工

本轮按用户目标文件要求使用单线程挂机模式：

- 不创建新 Codex UI 线程。
- 不创建新 worktree。
- 不写 `.agent/programs/thread-prompts/`。
- 主线程负责所有文件修改、diff 审查、验证、commit 和 push。
- 内部 subagent 仅作为当前线程内 read-only sidecar 审计：docs/workflow、backend ownership、product loop、runtime target。它们不写文件；晚到发现作为后续 phase 输入处理。

### 共享文件 owner

| shared surface | PHASE02 owner | 规则 |
| --- | --- | --- |
| `AGENTS.md`、`README.md` | 主线程 | 只保留当前状态摘要和入口，不展开 Production Target 细节。 |
| `.agent/system.yaml` | 主线程 | 路由、docs_sync 和 verify 必须同步。 |
| `.agent/programs/*` | 主线程 | current phase、phase status、closure checklist 和 roadmap 必须一起更新。 |
| `.agent/references/current-program.md` | 主线程 | 只记录 program 状态、归档位置和执行规则，不替代 production-readiness。 |
| `docs/architecture/*`、`.agent/architecture/*` | 主线程 | 改 `docs/architecture/architecture.md` 后必须运行 renderer 同步 mirror 和 HTML。 |
| verifier / repo tests | 主线程 | 规则能机器检查时同步脚本和 tests。 |

### 后续 phase 输入

来自 read-only sidecar 的非 PHASE02 发现已归入后续 phase：

- PHASE05：`src/backend/zuno/api/README.md` 和 `.agent/references/runtime-call-chain.md` 有 stale physical path；`BACKEND_LAYER_INTERNAL_SURFACES` 可补 pin 已存在 target surfaces。
- PHASE06：Desktop 仍是 API/bridge 复用，缺少 production recovery/download/e2e evidence；workspace task ownership / cross-user tests 需要补。
- PHASE07-PHASE12：parser/index/GraphRAG/memory/tool/security/eval 的 external service、credential、real sandbox、online eval 仍为 Target，需要 adapter、local fallback 或 blocked evidence。

### 验证结果

| Command | Result |
| --- | --- |
| `git diff --check` | pass；仅报告 Windows LF/CRLF working-copy warning。 |
| `python tools/agent/render_architecture.py --check` | pass；architecture Markdown mirror 和两个 HTML 输出与 `docs/architecture/architecture.md` 同步。 |
| `python tools/scripts/verify_docs_entrypoints.py` | pass。 |
| `python tools/scripts/verify_repo_structure.py` | pass。 |
| `python .agent/scripts/verify_agent_system.py` | pass。 |
| `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1` | pass。 |
| `pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_docs_entrypoints.py tests/repo/test_publish_boundary.py -p no:cacheprovider` | `63 passed in 2.01s`。 |

## 停止条件

- 当前分支或 worktree 有未解释的用户改动。
- verifier 需要禁止路径变更才能通过。
- 需要把旧 program 重新变成 active 才能满足测试。
