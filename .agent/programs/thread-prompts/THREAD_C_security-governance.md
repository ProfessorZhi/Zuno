# THREAD C - Security / Governance

## UI Mode

本线程必须在 Codex UI 目标模式执行。提示词中的“目标模式”不能替代真实 UI 模式。

## Goal

执行 Program 2 的 Security / Governance 子任务：把 input / retrieval / tool / output 四道 gate 样例化，覆盖 prompt injection、cross-workspace leakage、secret / PII redaction、unsupported claim policy、policy decision trace 和 blocked / allowed / redacted evidence。

## Safety Gate

先执行并报告：

```powershell
git fetch --prune
git status --short --branch
git log --oneline -5 --decorate
```

必须切到独立 worktree 和分支：

- Branch: `codex/zuno-p2-security-governance`
- Suggested worktree: `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-security-governance`

如果无法确认独立 worktree / branch，停止并返回证据。

## Program 1 Shared Facts

- Document IR, index manifest and retrieval chunks carry ACL scopes, sensitivity tags, source hash, document version and `citation_lineage`.
- Security gates must treat ACL / sensitivity / citation lineage as enforceable runtime metadata, not as documentation-only fields.
- Retrieval gate and output DLP are distinct; one cannot replace the other.
- OCR / VLM is target-blocked derived enrichment and must not become source truth.

Security / Governance must protect Program 1 lineage from prompt injection, cross-workspace leakage and unsafe output.

## Allowed Paths

- `src/backend/zuno/platform/security/**`
- `src/backend/zuno/platform/observability/**`
- `tests/security/**`
- `tests/evals/**`
- `tools/evals/zuno/**` only for lightweight security metric configuration

## Forbidden Paths

- `AGENTS.md`
- `README.md`
- `docs/**`
- `.agent/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/capability/**` unless a failing security test proves the smallest necessary policy hook
- `src/backend/zuno/knowledge/**`
- shared verifier / workflow scripts

If a fix requires forbidden paths, stop and report the exact reason.

## Required Work

1. Write failing tests for prompt injection and cross-workspace leakage using ACL / sensitivity metadata.
2. Prove input, retrieval, tool and output gates each emit traceable policy decisions.
3. Prove secret / PII redaction in trace and governance ledger.
4. Prove unsupported claim policy cannot be bypassed by uncited high-confidence wording.
5. Use internal subagents only for independent, non-overlapping work.

## Focused Tests

```powershell
pytest -q tests/security tests/evals -p no:cacheprovider
git diff --check
```

## Stop Conditions

- Requires production DLP provider, real external trace sink or private dataset.
- Requires modifying Tool / Knowledge / Memory ownership beyond a minimal tested hook.
- Cannot prove redaction or policy decision trace with local tests.

## Closure

Before finishing, run focused tests, review diff, commit, and push.

Report:

- Branch
- Commit hash
- Push status
- Files changed
- Tests run and results
- Any blocked / forbidden-path evidence
