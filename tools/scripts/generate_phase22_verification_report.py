from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-verification-report.md"
PROGRAM = REPO_ROOT / ".agent" / "programs" / "PHASE22_fixed-benchmark-production-readiness-and-closure.md"
CLOSURE_SUMMARY = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-closure-summary.md"
COMPLETION_BLOCKERS = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-completion-blockers.md"
REVIEWED_SUMMARY = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-public-benchmark-review-pack" / "reviewed" / "review_summary.json"
FEATURE_FLAG_REPORT = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-feature-flag-runtime-cutover" / "verifier_report.json"
LEGACY_AUDIT_REPORT = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-final-legacy-audit-v3" / "audit_report.json"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def build_phase22_verification_report() -> str:
    program_text = _read_text(PROGRAM)
    closure_text = _read_text(CLOSURE_SUMMARY)
    blockers_text = _read_text(COMPLETION_BLOCKERS)
    reviewed_summary = _read_json(REVIEWED_SUMMARY)
    approved_count = reviewed_summary.get("reviewer_approved_count", 0)
    eligible_count = reviewed_summary.get("benchmark_eligible_count", 0)
    total_cases = reviewed_summary.get("total_cases", 0)
    feature_findings = _read_json(FEATURE_FLAG_REPORT).get("finding_count", 0)
    legacy_findings = _read_json(LEGACY_AUDIT_REPORT).get("finding_count", 0)

    return "\n".join(
        [
            "# PHASE22 Verification Report",
            "",
            "status: in_progress",
            "report_kind: verification_snapshot",
            "",
            "## Verified Current Facts",
            "",
            "- PHASE22 remains `in_progress`.",
            "- Fixed benchmark remains `BLOCKED / blocked_not_measured`.",
            f"- Public benchmark review pack is `PASS` with `{approved_count}/{total_cases}` approved and `{eligible_count}/{total_cases}` eligible cases.",
            "- Program remains `active`.",
            "- No archive / no-active reset has been performed.",
            "",
            "## Evidence Sources",
            "",
            f"- `{CLOSURE_SUMMARY.relative_to(REPO_ROOT).as_posix()}`",
            f"- `{COMPLETION_BLOCKERS.relative_to(REPO_ROOT).as_posix()}`",
            f"- `{PROGRAM.relative_to(REPO_ROOT).as_posix()}`",
            "",
            "## Completion Boundary",
            "",
            f"- program boundary phrase: {'PHASE22 remains `in_progress`' if 'PHASE22 remains `in_progress`' in program_text else 'missing'}",
            f"- closure boundary phrase: {'Program archive and no-active reset are still pending.' if 'Program archive and no-active reset are still pending.' in closure_text else 'missing'}",
            f"- blocker boundary phrase: {'PHASE22 当前不能关闭为 `completed`' if 'PHASE22 当前不能关闭为 `completed`' in blockers_text else 'missing'}",
            "",
            "## Verification Commands",
            "",
            "```bash",
            "python tools/scripts/verify_current_program.py",
            "python tools/scripts/verify_phase22_completion_blockers.py",
            "python tools/scripts/verify_docs_entrypoints.py",
            "python -m pytest -q tests/repo/test_phase22_closure_summary.py tests/platform/test_langsmith_trace_adapter.py tests/platform/test_langsmith_adapter_factory.py tests/evals/test_canonical_profile_runners.py::test_09f_standard_adapter_trace_delivery_failure_fails_closed -p no:cacheprovider --tb=short",
            "```",
            "",
            "## 2026-08-10 Verification Run",
            "",
            "本轮验证没有把局部通过扩大解释成 Full final verification 通过：",
            "",
            "- 通过：Phase22 cleanup boundary、repo structure、current program、completion blocker gate、docs entrypoints、Agent System、doc boundaries；四 Profile canonical/contract 回归为 `237 passed, 30 subtests passed`。",
            "- 通过：全量 pytest collection 已恢复，收集 `2750 tests`；Phase22 focused regression（candidate/review/dataset/closure/formal/measurement/cleanup）为 `114 passed`，backend semantic ownership focused regression 为 `5 passed`，product baseline/regression summary 为 `3 passed`，workspace task 关键回归为 `3 passed`，统一产品 E2E 为 `1 passed`。完整 pytest、`-k phase22` 和 workspace runtime 全文件运行均在 5 分钟执行上限内 timeout，未产生全量汇总，不能宣称全量通过。",
            "- 通过：`verify_phase22_backend_semantic_legacy.py --scope repository` 返回 `BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED`、0 findings；最终 legacy 审计的 MCP 规则已从子串匹配收敛为执行形状匹配。",
            f"- 仍失败：feature-flag runtime cutover verifier 仍有 `{feature_findings}` 条 findings；final legacy cutover verifier 仍有 `{legacy_findings}` 条 findings，包含真实 `/api/v1/mcp_chat` → `MCPChatAgent` → `mcp_openai.MCPManager` 旧生产执行链，以及其他未完成 legacy/runtime 收口。",
            "",
            "因此 Full final verification 仍是 `incomplete`，Production Readiness 仍不能判定；本报告不声明 `PHASE22_COMPLETED`、`BENCHMARK_PASSED` 或 `PRODUCTION_READY`。",
            "",
            "## Known Remaining Blockers",
            "",
            "- formal four-profile runtime, credentials, and runtime/measurement attestation",
            "- full final verification",
            "- program archive / no-active reset",
            "- clean Git worktree：`.claude/worktrees` 下有 10 个已登记工作树，其中含未跟踪内容；另有未登记目录，所有者/是否废弃尚未确认",
            "",
            "## Archive Boundary",
            "",
            "Program archive 和 `.agent/programs/` 的 no-active reset 本轮未执行。已登记工作树必须由其所有者确认后，才能针对精确路径执行 `git worktree remove`；本轮没有进行删除、移动或忽略规则变更。",
            "",
            "## Boundary",
            "",
            "- This report does not claim PHASE22 completed.",
            "- It is a reproducible snapshot of the current verification boundary.",
            "",
        ]
    )


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_phase22_verification_report(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
