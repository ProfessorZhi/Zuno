# THREAD B - Tool / Sandbox

## UI Mode

本线程必须在 Codex UI 目标模式执行。提示词中的“目标模式”不能替代真实 UI 模式。

## Goal

执行 Program 2 的 Tool / Sandbox 子任务：强化 Tool Control Plane、tool registry、policy、approval、execution/result normalization、redacted approval ledger、credential-ref-only broker、network deny / deny_by_default 和 sandbox audit context。

## Safety Gate

先执行并报告：

```powershell
git fetch --prune
git status --short --branch
git log --oneline -5 --decorate
```

必须切到独立 worktree 和分支：

- Branch: `codex/zuno-p2-tool-sandbox`
- Suggested worktree: `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-tool-sandbox`

如果无法确认独立 worktree / branch，停止并返回证据。

## Program 1 Shared Facts

- Document IR, ingestion and retrieval evidence can carry ACL, sensitivity, parser diagnostics and `citation_lineage`.
- Tool execution must not leak raw credentials, sensitive document content, parser diagnostics, source hashes or approval secrets into logs / traces.
- OCR / VLM and external parser adapters are target-blocked; do not add real credentials or service calls.
- Current sandbox may record `real_isolation=False`; do not claim rootless / gVisor / Firecracker Current.

Tool / Sandbox must protect Program 1 lineage: approval, network and sandbox traces can reference lineage ids, but must not expose private document payloads or credentials.

## Allowed Paths

- `src/backend/zuno/capability/**`
- `src/backend/zuno/platform/security/**`
- `tests/agent/test_capability_system.py`
- `tests/agent/test_capability_registry.py`
- `tests/security/**`
- `tests/tools/**`

## Forbidden Paths

- `AGENTS.md`
- `README.md`
- `docs/**`
- `.agent/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/agent/context.py`
- shared verifier / workflow scripts

If a fix requires forbidden paths, stop and report the exact reason.

## Required Work

1. Write failing tests for high side-effect tool approval, decision id, tool request id and result id continuity.
2. Prove credential-ref-only behavior and redacted approval ledger.
3. Prove network deny / deny_by_default behavior in policy tests.
4. Make sandbox audit context explicit, including `real_isolation=False` when appropriate.
5. Use internal subagents only for independent, non-overlapping work.

## Focused Tests

```powershell
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_registry.py tests/security tests/tools -p no:cacheprovider
git diff --check
```

## Stop Conditions

- Requires real external vault, OAuth broker, network proxy or production sandbox.
- Requires modifying Knowledge / Memory ownership.
- Requires storing raw credentials or sensitive source text.

## Closure

Before finishing, run focused tests, review diff, commit, and push.

Report:

- Branch
- Commit hash
- Push status
- Files changed
- Tests run and results
- Any blocked / forbidden-path evidence
