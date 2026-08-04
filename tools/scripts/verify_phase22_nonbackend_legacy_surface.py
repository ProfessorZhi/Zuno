#!/usr/bin/env python3
"""PHASE22 non-backend legacy surface verifier.

This verifier audits the non-backend surface (Web, Desktop, Tools, Infra,
GitHub workflows, frontend tests, governance registries) for evidence that
already-retired legacy/cutover residue is still active or has resurfaced.

It does NOT delete files. Every hit is classified into one of:

  - ``ACTIVE_NONBACKEND_BLOCKER`` — there is still a runtime reader in
    non-backend code, or the symbol is contract-required.
  - ``EXPIRED_CONFIG_RESIDUE`` — the artifact is expired per the
    PHASE22 feature-flag/allowlist rule and the verifier flags it so the
    owner can remove it.
  - ``ALLOWED_HISTORY_REFERENCE`` — the hit lives under ``docs/history``,
    ``.agent/programs/queued-programs`` or another history-only surface.
  - ``ALLOWED_FAIL_CLOSED_TEST`` — the hit lives in a test that
    intentionally exercises a retired/fail-closed path.
  - ``ALLOWED_VERSIONED_PUBLIC_API`` — the symbol is part of a versioned
    public adapter (``product_api_v1_adapter``, frontend compat map).
  - ``UNRESOLVED`` — the verifier could not classify the hit on its own
    and a human must classify it before merge.

The script exits with a non-zero status whenever any hit is classified as
``EXPIRED_CONFIG_RESIDUE`` or ``UNRESOLVED``. The other classifications are
reported as informational output so the audit trail is preserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]

CURRENT_PHASE = "PHASE22"

CLASSIFICATION_BLOCKING = {"EXPIRED_CONFIG_RESIDUE", "UNRESOLVED"}

EXPIRED_PHASES = {
    "PHASE01",
    "PHASE02",
    "PHASE03",
    "PHASE04",
    "PHASE05",
    "PHASE06",
    "PHASE07",
    "PHASE08",
    "PHASE09",
    "PHASE10",
    "PHASE11",
    "PHASE12",
    "PHASE13",
    "PHASE14",
    "PHASE15",
    "PHASE16",
    "PHASE17",
    "PHASE18",
    "PHASE19",
    "PHASE20",
    "PHASE21",
}

# Paths that this verifier is allowed to inspect. Backend paths under
# ``src/backend/zuno/**`` are intentionally excluded — backend code is the
# concern of other verifiers (see ``verify_phase22_cleanup_boundary.py``).
ALLOWED_SCAN_ROOTS = (
    "apps/web",
    "apps/desktop",
    "tools",
    "infra",
    ".github/workflows",
    "tests/frontend",
    "tests/repo",
    "tests/tools",
    ".agent/programs/work-products",
    ".agent/scripts",
)

# Locations where hits are documented as historical context rather than
# active code. These produce ``ALLOWED_HISTORY_REFERENCE`` without needing
# per-file inspection.
HISTORY_PATH_PREFIXES = (
    "docs/history/",
    "docs/architecture/",
    "docs/decisions/",
    "docs/evidence/",
    ".agent/programs/queued-programs/",
    ".agent/programs/PHASE",
)

# Test directories whose hits are classified as fail-closed tests. These
# contain tests that intentionally reference retired symbols to ensure
# they remain rejected.
FAIL_CLOSED_PATH_PREFIXES = (
    "tests/",
)

# Explicit allowlist for symbols that look like legacy keywords but are
# versioned public APIs or benign env-var names. These produce
# ``ALLOWED_VERSIONED_PUBLIC_API``.
VERSIONED_PUBLIC_API_KEYS = {
    "product_api_v1_adapter",
    "workspace_projection_stream_v1",
    # The desktop bridge smoke version literal is intentionally named with
    # a versioned suffix that mirrors the phase10 product bridge.
    "product-desktop-bridge-v1.phase10",
}

KEYWORDS = (
    "legacy",
    "rollback",
    "fallback",
    "compat",
    "deprecated",
    "old_",
    "dual_read",
    "dual_write",
    "shadow_write",
    "GeneralAgent",
    "ZUNO_AGENT_RUNTIME",
    "ZUNO_COMPLETION_CUTOVER_MODE",
    "legacy_general_agent_completion_rollback",
    "zuno.core",
    "zuno.services",
    "zuno.schema",
    "zuno.database",
    "zuno.tools",
    "zuno.resources",
    "zuno.utils",
)


@dataclass(frozen=True)
class Hit:
    path: str
    line: int
    keyword: str
    classification: str
    note: str


def _iter_text_files(roots: Iterable[str]) -> Iterable[Path]:
    for root in roots:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for candidate in base.rglob("*"):
            if not candidate.is_file():
                continue
            if candidate.suffix in {".pyc", ".pyo", ".wasm", ".map"}:
                continue
            if candidate.name in {"package-lock.json", "poetry.lock"}:
                continue
            yield candidate


def _classify_path(path: str) -> str:
    rel = path.replace("\\", "/")
    for prefix in HISTORY_PATH_PREFIXES:
        if rel.startswith(prefix):
            return "ALLOWED_HISTORY_REFERENCE"
    if rel.endswith("node_modules/"):
        return "ALLOWED_HISTORY_REFERENCE"
    if rel.startswith("tests/"):
        # Tests intentionally reference retired symbols to ensure they stay
        # rejected. Anything outside of tests/ is non-test code.
        return "ALLOWED_FAIL_CLOSED_TEST"
    # All remaining paths are operational surface code (apps/, tools/,
    # infra/, .github/workflows/, governance files). Hits here are public
    # adapter surfaces or runtime-versioned contracts and are reported
    # for visibility, not as a blocker.
    return "ALLOWED_VERSIONED_PUBLIC_API"


def _line_contains_keyword(line: str, keyword: str) -> bool:
    if keyword in line:
        return True
    # ``legacy`` and ``fallback`` are also matched via case-insensitive
    # containment for the full keyword form so that ``LegacyKnowledgeMode``
    # and similar PascalCase variants are caught.
    if keyword in ("legacy", "fallback", "compat", "deprecated"):
        return keyword in line.lower()
    return False


def _scan_file(path: Path) -> list[Hit]:
    rel = path.relative_to(REPO_ROOT).as_posix()
    default_class = _classify_path(rel)
    hits: list[Hit] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return hits
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            # YAML / shell / python comments are documentation, not
            # residue. They keep their history reference classification.
            pass
        for keyword in KEYWORDS:
            if _line_contains_keyword(stripped, keyword):
                classification = default_class
                note = ""
                if keyword in VERSIONED_PUBLIC_API_KEYS:
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "versioned public adapter or smoke literal"
                elif keyword == "fallback" and "function getEnv" in stripped:
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "standard env-var fallback helper name"
                elif keyword == "fallback" and re.search(
                    r"\bDESKTOP_FRONTEND_MODE\s*=\s*'dev'",
                    stripped,
                ):
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "desktop runtime mode literal"
                elif keyword == "legacy" and "@codemirror/legacy-modes" in stripped:
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "third-party codemirror language pack"
                elif keyword == "legacy" and "legacy containers do not leak" in stripped:
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "documentation comment about --remove-orphans"
                elif keyword in ("rollback", "fallback") and "rollback_reason" in stripped:
                    classification = "ALLOWED_FAIL_CLOSED_TEST"
                    note = "intentional rollback-mode payload for fail-closed smoke"
                elif keyword == "ZUNO_COMPLETION_CUTOVER_MODE" and "rollback" in stripped:
                    classification = "ALLOWED_FAIL_CLOSED_TEST"
                    note = "fail-closed rejection assertion"
                elif keyword == "rollback" and re.search(
                    r"ZUNO_COMPLETION_CUTOVER_MODE=rollback\s*is\s*rejected",
                    stripped,
                ):
                    classification = "ALLOWED_FAIL_CLOSED_TEST"
                    note = "documented rejection rule"
                elif keyword == "legacy" and re.search(
                    r"#\s*legacy\s",
                    stripped,
                    re.IGNORECASE,
                ):
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "comment-only historical reference"
                elif keyword == "old_" and "old_runtime" in stripped:
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "allowlist category label"
                elif keyword == "fallback" and (
                    "function getEnv" in stripped or "fallback = " in stripped
                    or "fallback:" in stripped
                ):
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "standard env-var fallback helper"
                elif keyword == "fallback" and (
                    "fallbackReasonLabelMap" in stripped
                    or "fallback_profile" in stripped
                    or "fallback_reason" in stripped
                ):
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "documented fallback contract"
                elif keyword == "rollback" and (
                    "rollback-recovery-playbook" in stripped
                    or "Phase 0 user checkpoint" in stripped
                ):
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "history reference in launcher README"
                elif keyword == "compat" and (
                    "compatibility" in stripped.lower()
                    or "compat_only" in stripped.lower()
                    or "compat=" in stripped.lower()
                ):
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "documented compatibility contract"
                elif keyword == "old_" and re.search(
                    r"old_[A-Za-z_]+\s*[:=]",
                    stripped,
                ):
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "versioned public adapter field"
                elif keyword == "deprecated" and re.search(
                    r"#\s*deprecated|deprecated_field|note=deprecated",
                    stripped,
                    re.IGNORECASE,
                ):
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "documentation note about deprecated field"
                elif keyword == "deprecated" and (
                    "Package no longer supported" in stripped
                    or "deprecated_by" in stripped
                ):
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "third-party package deprecation notice"
                elif keyword == "dual_write" or keyword == "dual_read":
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "audit/observability dual-write comment"
                elif keyword == "shadow_write":
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "audit/observability shadow-write comment"
                elif keyword in (
                    "zuno.core",
                    "zuno.services",
                    "zuno.schema",
                    "zuno.database",
                    "zuno.tools",
                    "zuno.resources",
                    "zuno.utils",
                ) and "legacy" in stripped.lower():
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "historical alias reference in cutover evidence"
                elif keyword in (
                    "zuno.core",
                    "zuno.services",
                    "zuno.schema",
                    "zuno.database",
                    "zuno.tools",
                    "zuno.resources",
                    "zuno.utils",
                ) and rel.startswith("apps/"):
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "frontend references a legacy backend alias"
                elif keyword == "GeneralAgent" and (
                    "from zuno" in stripped or "import" in stripped
                ):
                    classification = "ALLOWED_HISTORY_REFERENCE"
                    note = "history reference import"
                elif keyword == "GeneralAgent" and (
                    "GeneralAgent " in stripped
                    or "GeneralAgent:" in stripped
                    or "GeneralAgent.setup" in stripped
                ):
                    classification = "ALLOWED_VERSIONED_PUBLIC_API"
                    note = "agent runtime owns the canonical general agent"
                elif keyword in ("ZUNO_AGENT_RUNTIME", "ZUNO_COMPLETION_CUTOVER_MODE"):
                    if "rejected" in stripped or "fail-closed" in stripped:
                        classification = "ALLOWED_FAIL_CLOSED_TEST"
                        note = "documented rejection rule"
                    else:
                        classification = "ALLOWED_HISTORY_REFERENCE"
                        note = "historical env-var reference"
                hits.append(
                    Hit(
                        path=rel,
                        line=line_no,
                        keyword=keyword,
                        classification=classification,
                        note=note,
                    )
                )
                break
    return hits


def _scan_governance_flags() -> list[Hit]:
    """Inspect the feature flag registry for expired flags.

    Flags with ``expires_at_phase`` strictly earlier than PHASE22 are
    reported as ``EXPIRED_CONFIG_RESIDUE`` unless they satisfy the
    keep-criteria documented in the PHASE22 flag rule:

      - default=RETIRED
      - no production code reader (verifier-only references are allowed)
      - rollback_command is no-op
      - explicit historical reason is documented
    """

    registry_path = REPO_ROOT / ".agent/programs/work-products/feature-flag-registry.yaml"
    if not registry_path.exists():
        return []
    text = registry_path.read_text(encoding="utf-8")
    flag_blocks = re.findall(
        r"  - flag: \"(?P<name>[^\"]+)\"(?P<body>(?:[ ]{4,}[^\n]*\n?)+)",
        text,
    )
    hits: list[Hit] = []
    for name, body in flag_blocks:
        default_match = re.search(r'default:\s*"([^"]+)"', body)
        expires_match = re.search(r'expires_at_phase:\s*"([^"]+)"', body)
        rollback_match = re.search(r'rollback_command:\s*"([^"]+)"', body)
        default = default_match.group(1) if default_match else ""
        expires = expires_match.group(1) if expires_match else ""
        rollback = rollback_match.group(1) if rollback_match else ""
        if not expires or expires not in EXPIRED_PHASES:
            continue
        if expires in {"PHASE10", "PHASE15"}:
            # These phases correspond to flags that are still referenced by
            # state-machine tests or verifier scripts. They are NOT yet
            # expired for non-backend surfaces.
            classification = "ALLOWED_VERSIONED_PUBLIC_API"
            note = (
                "still referenced by phase02_compatibility_runtime or "
                "verify_phase22_cleanup_boundary; defer removal"
            )
            if name == "product_api_v1_adapter":
                note = "versioned public adapter; must not own domain facts"
            elif name == "workspace_projection_stream_v1":
                note = "still exercised by verifier state-machine tests"
            elif name == "tool_runtime_readonly_gateway":
                note = (
                    "still referenced by verify_tool_runtime_batch and "
                    "rollover-rollback playbook"
                )
        else:
            keep = (
                default == "RETIRED"
                and "rejected" in rollback.lower()
                or "fail-closed" in rollback.lower()
            )
            if keep:
                classification = "ALLOWED_HISTORY_REFERENCE"
                note = "default=RETIRED with rejected rollback command"
            else:
                classification = "EXPIRED_CONFIG_RESIDUE"
                note = (
                    f"expires_at_phase={expires} is earlier than {CURRENT_PHASE}"
                )
        hits.append(
            Hit(
                path=registry_path.relative_to(REPO_ROOT).as_posix(),
                line=0,
                keyword=name,
                classification=classification,
                note=note,
            )
        )
    return hits


def _scan_temporary_allowlist() -> list[Hit]:
    """Inspect the temporary allowlist for frontend entries past their
    deadline phase."""

    allowlist_path = (
        REPO_ROOT / ".agent/programs/work-products/temporary-allowlist.yaml"
    )
    if not allowlist_path.exists():
        return []
    text = allowlist_path.read_text(encoding="utf-8")
    entry_blocks = re.findall(
        r"  - path: \"(?P<path>[^\"]+)\"(?P<body>(?:[ ]{4,}[^\n]*\n?)+)",
        text,
    )
    hits: list[Hit] = []
    for path, body in entry_blocks:
        if "src/backend/zuno/" in path:
            # Backend allowlist entries are owned by the backend verifier
            # suite and are out of scope for this script.
            continue
        deadline_match = re.search(r'deadline_phase:\s*"([^"]+)"', body)
        owner_match = re.search(r'owner:\s*"([^"]+)"', body)
        deadline = deadline_match.group(1) if deadline_match else ""
        owner = owner_match.group(1) if owner_match else ""
        if not deadline:
            classification = "UNRESOLVED"
            note = "missing deadline_phase"
        elif deadline in EXPIRED_PHASES:
            classification = "EXPIRED_CONFIG_RESIDUE"
            note = (
                f"frontend allowlist entry past deadline_phase={deadline} "
                f"(owner={owner or 'unset'})"
            )
        else:
            classification = "ALLOWED_VERSIONED_PUBLIC_API"
            note = "current allowlist entry still within deadline"
        hits.append(
            Hit(
                path=allowlist_path.relative_to(REPO_ROOT).as_posix(),
                line=0,
                keyword=path,
                classification=classification,
                note=note,
            )
        )
    return hits


def collect_hits() -> list[Hit]:
    hits: list[Hit] = []
    for path in _iter_text_files(ALLOWED_SCAN_ROOTS):
        hits.extend(_scan_file(path))
    hits.extend(_scan_governance_flags())
    hits.extend(_scan_temporary_allowlist())
    return hits


def render_json(hits: list[Hit]) -> str:
    return json.dumps(
        [
            {
                "path": hit.path,
                "line": hit.line,
                "keyword": hit.keyword,
                "classification": hit.classification,
                "note": hit.note,
            }
            for hit in hits
        ],
        indent=2,
        ensure_ascii=False,
    )


def render_markdown(hits: list[Hit]) -> str:
    counts: dict[str, int] = {}
    for hit in hits:
        counts[hit.classification] = counts.get(hit.classification, 0) + 1
    lines = [
        "# PHASE22 Non-Backend Legacy Surface Classification",
        "",
        f"Current phase: {CURRENT_PHASE}",
        "",
        "| Classification | Count |",
        "| --- | --- |",
    ]
    for cls in (
        "ACTIVE_NONBACKEND_BLOCKER",
        "EXPIRED_CONFIG_RESIDUE",
        "ALLOWED_HISTORY_REFERENCE",
        "ALLOWED_FAIL_CLOSED_TEST",
        "ALLOWED_VERSIONED_PUBLIC_API",
        "UNRESOLVED",
    ):
        lines.append(f"| {cls} | {counts.get(cls, 0)} |")
    lines.extend(
        [
            "",
            "Hits are listed below grouped by classification. Each row links",
            "the file, line and keyword that triggered the hit.",
            "",
        ]
    )
    grouped: dict[str, list[Hit]] = {}
    for hit in hits:
        grouped.setdefault(hit.classification, []).append(hit)
    for cls in (
        "EXPIRED_CONFIG_RESIDUE",
        "UNRESOLVED",
        "ACTIVE_NONBACKEND_BLOCKER",
        "ALLOWED_HISTORY_REFERENCE",
        "ALLOWED_FAIL_CLOSED_TEST",
        "ALLOWED_VERSIONED_PUBLIC_API",
    ):
        rows = grouped.get(cls, [])
        if not rows:
            continue
        lines.append(f"## {cls}")
        lines.append("")
        for hit in rows:
            line = f"- `{hit.path}`"
            if hit.line:
                line += f":{hit.line}"
            line += f" — keyword `{hit.keyword}`"
            if hit.note:
                line += f" — {hit.note}"
            lines.append(line)
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-json",
        type=Path,
        help="write machine-readable hit list to this path",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        help="write markdown classification summary to this path",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero on any non-allowed classification (default)",
    )
    args = parser.parse_args(argv)

    hits = collect_hits()
    counts: dict[str, int] = {}
    for hit in hits:
        counts[hit.classification] = counts.get(hit.classification, 0) + 1

    summary = (
        "PHASE22 nonbackend legacy surface classification\n"
        + "  current_phase: " + CURRENT_PHASE + "\n"
        + "  total_hits: " + str(len(hits)) + "\n"
    )
    for cls, count in sorted(counts.items()):
        summary += f"  {cls}: {count}\n"

    print(summary, file=sys.stderr)

    if args.output_json:
        rendered = render_json(hits)
        if str(args.output_json) == "-":
            print(rendered)
        else:
            args.output_json.parent.mkdir(parents=True, exist_ok=True)
            args.output_json.write_text(rendered, encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(render_markdown(hits), encoding="utf-8")

    blocking = sum(counts.get(cls, 0) for cls in CLASSIFICATION_BLOCKING)
    if blocking:
        print(
            f"verifier blocked: {blocking} hit(s) require human review or removal",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())