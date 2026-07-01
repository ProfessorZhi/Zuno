# THREAD A - Memory / Context

## UI Mode

本线程必须在 Codex UI 目标模式执行。提示词中的“目标模式”不能替代真实 UI 模式。

## Goal

执行 Program 2 的 Memory / Context 子任务：强化 working / episodic / semantic / procedural / preference / governance memory 边界、Context Pack include / exclude / compressed / dropped reasons、semantic fallback、privacy delete、sensitive source exclusion 和 memory eval baseline。

## Safety Gate

先执行并报告：

```powershell
git fetch --prune
git status --short --branch
git log --oneline -5 --decorate
```

必须切到独立 worktree 和分支：

- Branch: `codex/zuno-p2-memory-context`
- Suggested worktree: `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-memory-context`

如果无法确认独立 worktree / branch，停止并返回证据。

## Program 1 Shared Facts

- Document IR 已有 `document_version_id`、`source_sha256`、`parser_config_hash`、`ir_schema_version`、ACL 和 sensitivity tags。
- Parse job snapshot 已有 `parse_job_id`、`parse_attempt_id`、diagnostics、retry / blocked / failed / cancelled / dead_letter 语义。
- Index manifest 已承接 parse lineage、`diagnostics_digest`、block/table/figure count、ACL scopes 和 sensitivity tags。
- Retrieval chunk metadata 已有 `citation_lineage`，Evidence / Citation provenance 可回追 source hash、document version、parse job 和 parse attempt。
- 外部 parser / OCR / VLM 仍是 target-blocked；不要把它写成 Current。

Memory / Context 必须消费这些事实：上下文压缩、记忆写入和语义召回不得丢失 ACL、sensitivity、source lineage 和 dropped reason。

## Allowed Paths

- `src/backend/zuno/memory/**`
- `src/backend/zuno/agent/context.py`
- `src/backend/zuno/agent/post_turn.py`
- `tests/agent/test_context_contracts.py`
- `tests/agent/test_context_orchestrator.py`
- `tests/agent/test_memory_layers.py`
- `tests/agent/test_memory_layer_surfaces.py`
- `tests/agent/test_generalagent_context_memory_runtime.py`

## Forbidden Paths

- `AGENTS.md`
- `README.md`
- `docs/**`
- `.agent/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/platform/security/**`
- `src/backend/zuno/knowledge/**`
- shared verifier / workflow scripts

If a fix requires forbidden paths, stop and report the exact reason.

## Required Work

1. Write failing tests for Context Pack include / exclude / compressed / dropped reason behavior.
2. Preserve citation lineage, ACL and sensitivity metadata when memory/context consumes retrieved evidence.
3. Strengthen semantic fallback, privacy delete and sensitive source exclusion with focused tests.
4. Keep product runtime as Single Controller / Single GeneralAgent; this thread is engineering parallelism, not a Zuno multi-agent runtime change.
5. Use internal subagents only for independent read-only audits or non-overlapping implementation slices.

## Focused Tests

```powershell
pytest -q tests/agent/test_context_contracts.py tests/agent/test_context_orchestrator.py tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
git diff --check
```

## Stop Conditions

- Needed changes cross into Knowledge / Tool / Security ownership.
- Memory changes require DB migration or production external vector memory.
- Sensitive source exclusion cannot be proven with tests.

## Closure

Before finishing, run focused tests, review diff, commit, and push.

Report:

- Branch
- Commit hash
- Push status
- Files changed
- Tests run and results
- Any blocked / forbidden-path evidence
