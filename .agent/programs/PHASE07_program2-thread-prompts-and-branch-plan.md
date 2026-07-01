# PHASE07 Program 2 Thread Prompts 与 Branch Plan

status: planned
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
3. 为每个线程写 safety gate：`git fetch --prune`、`git status --short --branch`、`git log --oneline -5 --decorate`。
4. 为每个线程写 focused tests。
5. 写主线程合并顺序：GraphRAG / Index、Memory / Context、Tool / Sandbox、Security / Governance，最后统一 docs / verifier。
6. 明确如果无法创建真实 UI 目标模式线程，则只报告提示词路径，等待用户手动打开。
7. 运行 docs / workflow verifier。

## 多 agent 分工

- 可用 subagent 只读检查每个 prompt 是否范围互斥。
- 主线程负责最终 prompt 文件、合并计划和 verifier/test。

## 需要返回的证据

- 四个 thread prompt 路径。
- 每个线程 branch / allowed paths / focused tests 表。
- 主线程合并计划。
- workflow verifier 输出。

## 停止条件

- 当前工具无法创建真实 UI 目标模式线程，且用户要求立即自动开线程。
- Program 2 计划仍有共享文件冲突，无法拆成四个粗粒度线程。
- thread prompt 需要包含凭据、私有资料原文或不可公开路径。
