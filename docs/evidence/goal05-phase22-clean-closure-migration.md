# Goal05 PHASE22 Clean Closure Migration Evidence

status: in_progress
phase: PHASE22
source_sha_at_generation: dfb9981995f4193488ca022ee5ec15eeff6a6349
origin_main_sha_at_generation: dfb9981995f4193488ca022ee5ec15eeff6a6349

## 目的

文档化旧 PR #97 (codex/phase22-final-closure, head `8b73d5d9`) 的“clean closure”迁移内容：仅迁移经审查的有效最终状态，不继承其提交历史与任何 DROP 类别内容。新分支基于最新 `origin/main` (`dfb99819`) 创建，不重写或合并旧 PR。

## ACCEPT（已迁移）

- `tools/evals/zuno/rag_eval/measurement_gate.py` — `MeasurementTruthGate` 增加 `_is_blank` 判定，空白 snapshot_ref / trace_id / budget_settlement_ref / artifact_receipt_ref / run_outcome_ref 一律 fail-closed。
- `tests/evals/test_canonical_profile_runners.py` — 新增两条空白 ref 回归测试（`test_21e_standard_rag_blank_receipt_refs_are_missing_not_observed`、`test_21f_agentic_graphrag_blank_run_outcome_is_missing`）。
- `.agent/scripts/dispatch_claude_worker.ps1` — Worker Dispatcher：完整 Task Card 读取、SHA-256、长度 800 字符下限；worktree clean / branch / 非 main 门禁；provider launcher (`claude-minimax` / `claude-deepseek`) 选择 + `claude.cmd` 兜底；execution 与 quota snapshot 分离（`NOT_QUERIED != CONFIG_REQUIRED`）；真实 JSON Schema 校验（type / required / additionalProperties / if-then / enum / pattern / minLength / minItems / maxItems / allOf / items）；task_id 匹配；`BLOCKED_*` 永不得升级 `COMPLETED`；raw `SUMMARY_PATH` 先读取、持久化时再脱敏；`COMPLETION_CANDIDATE` 由 Controller 审查后决定是否升级；distinct exit codes（0/2/3/10/20/30）；active/stale lock 检测与恢复；路径、Prompt、密钥、邮箱脱敏。
- `.agent/programs/worker-result.schema.json` — Worker Result JSON Schema；strict `if-then` 区分 `COMPLETED` vs `BLOCKED_*`。
- `tests/repo/test_dispatch_claude_worker.py` — 30 条 dispatcher 测试（fake runner / 隔离 PATH / 全程不依赖网络）。
- `tests/evals/test_*.py`（12 文件）+ `tests/repo/test_phase4_knowledge_config_v2_and_local_eval.py` — `from zuno.evals.rag_eval.X` 改为 `from tools.evals.zuno.rag_eval.X`。
- `.agent/programs/codex-medium-runbook.md` — 增补 Provider Worker 调度协议小节（执行 / 额度分离、三种完成结果、`CONFIG_REQUIRED` 不得阻止执行）。
- `.agent/scripts/verify-workflow.ps1` — 增加 `.agent/programs/thread-prompts` 路径要求。
- `.agent/references/{command-catalog,known-pitfalls,workflow,workflow-change-log}.md` — 工作树、嵌套 shell、PATH 隔离、结构化输入文件化等长期命令线安全规则。

## REWORK

无。ACCEPT 列出的所有变更以最终状态直接迁移；未对任何 ACCEPT 文件做方向性改写。

## DROP（不迁移）

- `tools/scripts/verify_agent_commit_attribution.py` 的 allowlist 加宽（`Claude Code` / `implementation`）—— 违反“不得修改或放宽 verifier”规则。
- `Agent: Claude Code` / `Agent-Mode: implementation` 这类 Trailer 枚举 —— 不在最新 main 合法枚举内（合法枚举见 `tools/scripts/verify_agent_commit_attribution.py::ALLOWED_AGENTS` / `ALLOWED_MODES`）。
- 旧 head 追逐（`approximate, will refresh`、`integration_head_sha` 等自引用 SHA） —— 改用 `source_sha_at_generation` / `origin_main_sha_at_generation` 等稳定字段。
- 任何 `zuno.evals.*` 全局 alias / shim —— 直接迁移到 `tools.evals.zuno.*`，不引入兼容 shim。
- 把 MiniMax metrics-wrapper 探针声明为 dispatcher live E2E（`docs/evidence/goal05-phase22-minimax-live-run.md`） —— 旧 PR 自降级为 `provider_wrapper_smoke_observed`，本轮也不再迁移。
- 旧 PR #97 重复的 final report / controller report / chatgpt review fix round / stop-hook resolution / pr97 body snapshot / wave1 controller plan 等文档（`docs/evidence/goal05-phase22-final-controller-report.md`、`*-chatgpt-review-fix-report.md`、`*-final-verification-run.md`、`*-stop-hook-resolution.md`、`*-pr97-body-snapshot.md`、`*-wave1-controller-plan.md`、`*-reviewer-pack-controller-handoff.md`、`*-commit-attribution-blocked.md`、`*-import-fix-deltas.md`、`*-benchmark-runtime-worker-ds1.md`、`*-worker-dispatch-protocol.md`、`*-agent-metrics-summary.md`、`*.json`、`*-canonical-tree-controller-review.md`、`*.md` 共 16 文件）—— self-referencing SHA、duplicate final reports、仅为旧 PR 历史服务。
- `.agent/programs/thread-prompts/phase22-final-closure/*.md`（5 文件）—— 旧 PR #97 专用 worker thread prompt，与 Provider/MiniMax live probe overclaim 绑定。

## 冻结事实（迁移未触动）

- PHASE22: `in_progress`
- Program: `active`
- Fixed Benchmark: `blocked_not_measured`，`actual_case_count=0`
- Reviewer Approval: `REVIEW_REQUIRED`，`reviewer_approved_count=0`，`benchmark_eligible_count=0`
- Production Readiness: `not established`
- Token / Cost / Session: `NOT_AVAILABLE_INTERACTIVE_SESSION`

## Metrics

- Main Session: `NOT_AVAILABLE_INTERACTIVE_SESSION`
- Provider / Model: Claude-Code / MiniMax-M3（main interactive session，未启动 live dispatcher E2E）
- Final Reviewer: ChatGPT / pending exact-head review

## 验证命令

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_current_program.py
python tools/scripts/verify_phase22_completion_blockers.py
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_agent_commit_attribution.py --base origin/main --allow-human-only
python -m pytest -q tests/repo/test_dispatch_claude_worker.py tests/evals/test_canonical_profile_runners.py -p no:cacheprovider
```

## Boundary

- 本证据不声明 PHASE22 完成，不声明 Fixed Benchmark 测量，不声明 Production Ready。
- `source_sha_at_generation` / `origin_main_sha_at_generation` 记录生成本文件时的源 SHA；承载本文件的提交 SHA 可能更新。
- 新 Draft PR 仅迁移 ACCEPT 内容；旧 PR #97 未合并，将在本轮结束时由其旧 worktree 安全清理流程关闭。
- 任何后续 chatgpt exact-head review 必须基于本证据记录的迁移后 head。