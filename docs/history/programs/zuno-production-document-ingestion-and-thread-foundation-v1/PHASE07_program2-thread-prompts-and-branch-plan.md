# PHASE07 Program 2 Thread Prompts 与 Branch Plan

status: completed
completed_at: 2026-07-01
program: zuno-production-document-ingestion-and-thread-foundation-v1

## 目标

为 Program 2 的多线程施工准备完整可投递提示词、分支、worktree、允许范围、禁止范围、验证命令和合并规则。PHASE07 不执行 Program 2，只准备它。

## 范围

- 创建或刷新 `.agent/programs/thread-prompts/`。
- 生成四个子线程提示词：
  - Memory / Context
  - Tool / Sandbox
  - Security / Governance
  - GraphRAG / Index
- 写清每个线程的 branch、worktree、allowed paths、forbidden paths、verification gates、commit / push 要求。
- 每个提示词都必须把 Program 1 的 ingestion lineage 作为共享输入事实：Document IR、document version、ACL / sensitivity、parse job、index manifest 和 citation provenance。
- 写清主线程 coordinator 的合并顺序和冲突处理规则。

## 禁止范围

- 不直接创建或控制真实 Codex UI 目标模式线程。
- 不让多个线程改同一个共享文件。
- 不把线程提示词贴到主对话作为完整执行文本。
- 不把 Program 2 子线程写成 Zuno 产品 runtime 多 Agent。

## 验收闸门

- 每个 thread prompt 都能独立交给目标模式线程执行。
- 每个 prompt 都声明 worktree / branch safety gate。
- 每个 prompt 都包含 allowed paths、forbidden paths、focused tests、stop conditions、commit / push evidence。
- Memory / Tool / Security / GraphRAG 四个 prompt 都必须说明自己如何消费或保护 Program 1 的 Document IR / index manifest / ACL / citation lineage。
- 主线程合并计划能说明共享文件由谁收口。

## 验证命令

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 需要先读取

- `.agent/references/workflow.md`
- `.agent/system.yaml`
- `.agent/templates/target-mode-prompt.md`
- `docs/architecture/document-ingestion-foundation.md`
- `.agent/programs/queued-programs/PROGRAM02_runtime-subsystems-parallel.md`
- PHASE01-PHASE06 closure evidence

## 需要修改的文件

- `.agent/programs/thread-prompts/THREAD_A_memory-context.md`
- `.agent/programs/thread-prompts/THREAD_B_tool-sandbox.md`
- `.agent/programs/thread-prompts/THREAD_C_security-governance.md`
- `.agent/programs/thread-prompts/THREAD_D_graphrag-index.md`
- `.agent/programs/PHASE07_program2-thread-prompts-and-branch-plan.md`
- verifier / tests，如需要保护 thread prompt 命名和边界

## 执行拆解

1. 读取 Program 2 queued plan。
2. 为每个线程写目标、背景、allowed paths、forbidden paths。
3. 把 Program 1 的 Document IR / parse lineage / index manifest / ACL / citation provenance 写成每个线程的输入约束。
4. 为每个线程写 safety gate：`git fetch --prune`、`git status --short --branch`、`git log --oneline -5 --decorate`。
5. 为每个线程写 focused tests。
6. 写主线程合并顺序：GraphRAG / Index、Memory / Context、Tool / Sandbox、Security / Governance，最后统一 docs / verifier。
7. 明确如果无法创建真实 UI 目标模式线程，则只报告提示词路径，等待用户手动打开。
8. 运行 docs / workflow verifier。

## 多 agent 分工

- 可用 subagent 只读检查每个 prompt 是否范围互斥。
- 主线程负责最终 prompt 文件、合并计划和 verifier/test。

## 需要返回的证据

- 四个 thread prompt 路径。
- 每个线程 branch / allowed paths / focused tests 表。
- 主线程合并计划。
- workflow verifier 输出。

## 关闭证据

PHASE07 只准备 Program 2 多线程施工资产，不直接创建或控制真实 Codex UI 目标模式线程。当前工具不能证明新线程处于 Codex UI 目标模式，因此本阶段交付可投递提示词文件；真实线程启动需要用户在 UI 中手动确认，或下一轮明确改为挂机模式。

四个 thread prompt 路径：

- `.agent/programs/thread-prompts/THREAD_A_memory-context.md`
- `.agent/programs/thread-prompts/THREAD_B_tool-sandbox.md`
- `.agent/programs/thread-prompts/THREAD_C_security-governance.md`
- `.agent/programs/thread-prompts/THREAD_D_graphrag-index.md`

线程边界：

| Thread | Branch | Suggested worktree | Allowed roots | Focused tests |
| --- | --- | --- | --- | --- |
| Memory / Context | `codex/zuno-p2-memory-context` | `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-memory-context` | `src/backend/zuno/memory/**`, `src/backend/zuno/agent/context.py`, `src/backend/zuno/agent/post_turn.py` | `tests/agent/test_context_contracts.py`, `tests/agent/test_context_orchestrator.py`, `tests/agent/test_memory_layers.py`, `tests/agent/test_memory_layer_surfaces.py`, `tests/agent/test_generalagent_context_memory_runtime.py` |
| Tool / Sandbox | `codex/zuno-p2-tool-sandbox` | `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-tool-sandbox` | `src/backend/zuno/capability/**`, `src/backend/zuno/platform/security/**` | `tests/agent/test_capability_system.py`, `tests/agent/test_capability_registry.py`, `tests/security/**`, `tests/tools/**` |
| Security / Governance | `codex/zuno-p2-security-governance` | `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-security-governance` | `src/backend/zuno/platform/security/**`, `src/backend/zuno/platform/observability/**`, `tools/evals/zuno/**` 轻量安全指标配置 | `tests/security/**`, `tests/evals/**` |
| GraphRAG / Index | `codex/zuno-p2-graphrag-index` | `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-graphrag-index` | `src/backend/zuno/knowledge/**` | `tests/agent/test_knowledge_graphrag_runtime_contracts.py`, `tests/agent/test_agentic_retrieval_runtime.py`, `tests/graphrag/**`, `tests/retrieval/**` |

主线程合并计划：

1. 先审查 GraphRAG / Index，因为它消费 Program 1 的 index manifest、`citation_lineage` 和 evidence provenance，后续 Memory / Security 都依赖这些字段稳定。
2. 再审查 Memory / Context，确保上下文压缩、memory write、semantic fallback、privacy delete 和 sensitive exclusion 不丢失 ACL、sensitivity、source lineage 和 dropped reason。
3. 再审查 Tool / Sandbox，确认 approval、network、credential-ref-only 和 sandbox audit 不泄露 Program 1 文档 payload、source hash 或 parser diagnostics。
4. 最后审查 Security / Governance，用 input / retrieval / tool / output gate 统一验证 ACL、sensitivity、prompt injection、cross-workspace leakage、redaction 和 unsupported claim policy。
5. 共享文件 `AGENTS.md`、README、`docs/**`、`.agent/**`、verifier、workflow scripts 和跨线程架构结论由主线程统一收口；子线程如果必须修改这些路径，必须停止并返回证据。

机器守门：

- 新增 `tests/repo/test_agent_system.py::test_program2_thread_prompts_are_target_mode_ready_and_guarded`，检查四个 prompt 的文件名、目标模式声明、safety gate、Program 1 shared facts、allowed / forbidden paths、focused tests、stop conditions、commit / push evidence。
- 新增 `.agent/scripts/verify_agent_system.py::verify_program_thread_prompts`，把同一规则纳入 Agent system verifier。

验证结果：

- `pytest -q tests/repo/test_agent_system.py::test_program2_thread_prompts_are_target_mode_ready_and_guarded -p no:cacheprovider`：先失败于 verifier 未纳入 `THREAD_PROMPT_FILES`，补 verifier 后通过，证明测试能抓住缺失守门。
- `git diff --check`：通过；仅报告 Windows line ending warning。
- `python .agent/scripts/verify_agent_system.py`：`Agent system verification passed.`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`：`Workflow verification passed.`
- `pytest -q tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider`：`16 passed`。

## 停止条件

- 当前工具无法创建真实 UI 目标模式线程，且用户要求立即自动开线程。
- Program 2 计划仍有共享文件冲突，无法拆成四个粗粒度线程。
- thread prompt 需要包含凭据、私有资料原文或不可公开路径。
