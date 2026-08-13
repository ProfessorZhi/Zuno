"""Verify that V3 AUTO_APPLY deltas have a traceable Canonical documentation diff."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V3-ROUND-002"
EXPECTED_DELTAS = [f"D{i:03d}" for i in range(1, 12)]
SYNC_ROW_RE = re.compile(r"^\|\s*(D\d{3})\s*\|.*?\|\s*(docs/project/[^|]+?)\s*\|\s*(AUTO_APPLY|ADR_ESCALATION|USER_GATE_ESCALATION)\s*\|", re.MULTILINE)
IMPLEMENTATION_EVIDENCE_COMMIT_MARKER = "feat: implement domain mutation and citation provenance guards"
CANONICAL_OWNER_ALIASES = {
    "docs/project/architecture/": "docs/architecture/",
    "docs/project/product/": "docs/history/superseded-document-taxonomy/project-topics/product/",
    "docs/project/domain/": "docs/history/superseded-document-taxonomy/project-topics/domain/",
    "docs/project/agents/": "docs/history/superseded-document-taxonomy/project-topics/agents/",
    "docs/project/knowledge/": "docs/history/superseded-document-taxonomy/project-topics/knowledge/",
    "docs/project/services/": "docs/history/superseded-document-taxonomy/project-topics/services/",
    "docs/project/data/": "docs/history/superseded-document-taxonomy/project-topics/data/",
    "docs/project/security/": "docs/history/superseded-document-taxonomy/project-topics/security/",
    "docs/project/eval/": "docs/history/superseded-document-taxonomy/project-topics/eval/",
    "docs/project/deployment/": "docs/history/superseded-document-taxonomy/project-topics/deployment/",
    "docs/project/modules/": "docs/history/superseded-document-taxonomy/project-modules/",
}


def canonical_path(owner: str) -> Path:
    direct = ROOT / owner
    if direct.exists():
        return direct
    for old_prefix, new_prefix in CANONICAL_OWNER_ALIASES.items():
        if owner.startswith(old_prefix):
            return ROOT / (new_prefix + owner[len(old_prefix):])
    return direct


def changed_files(baseline: str) -> set[str]:
    paths: set[str] = set()
    for args in (("diff", "--name-only", baseline), ("diff", "--cached", "--name-only", baseline)):
        result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            paths.update(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())
    return paths


def authorized_post_round_files() -> set[str]:
    """Return files owned by the separately recorded Wave-001 implementation commit.

    V3's original scope check predates the independent Implementation Evidence
    track.  Keep the old Canonical Diff check useful by excluding only the
    explicitly identified Wave-001 commit; any other later runtime change
    remains a V3 scope violation.
    """
    log = subprocess.run(
        ["git", "log", "--format=%H%x09%s", "--all"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    allowed: set[str] = set()
    for line in log.stdout.splitlines():
        commit, _, subject = line.partition("\t")
        if IMPLEMENTATION_EVIDENCE_COMMIT_MARKER not in subject:
            continue
        files = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        allowed.update(item.strip().replace("\\", "/") for item in files.stdout.splitlines() if item.strip())
    return allowed


def verify_canonical_diff(session: Path) -> list[str]:
    errors: list[str] = []
    manifest = yaml.safe_load((session / "manifest.yaml").read_text(encoding="utf-8"))
    baseline = str(manifest.get("baseline_sha", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", baseline):
        errors.append("manifest baseline_sha must be a full commit SHA")
    sync = (session / "canonical-sync-record.md").read_text(encoding="utf-8")
    if "Status: APPLIED" not in sync:
        errors.append("Canonical Sync must be APPLIED")
    rows = SYNC_ROW_RE.findall(sync)
    if [row[0] for row in rows] != EXPECTED_DELTAS:
        errors.append("Canonical Sync must map D001..D011 in order")
    diff = changed_files(baseline)
    implementation_evidence_files = authorized_post_round_files()
    forbidden_prefixes = ("src/", "apps/", "infra/", "migrations/", "migration/")
    allowed_documentation_guidance_files = {"apps/web/AGENTS.md"}
    forbidden_names = {"pyproject.toml", "poetry.lock", "requirements.txt", "package-lock.json", "pnpm-lock.yaml"}
    for path in sorted(diff):
        if (path.startswith(forbidden_prefixes) or path in forbidden_names) and path not in implementation_evidence_files and path not in allowed_documentation_guidance_files:
            errors.append(f"V3 scope forbids runtime/schema/infra/dependency change: {path}")
    all_mapped: set[str] = set()
    for delta_id, raw_docs, mode in rows:
        docs = [item.strip() for item in raw_docs.split(";") if item.strip()]
        if mode != "AUTO_APPLY":
            continue
        if not docs:
            errors.append(f"{delta_id} AUTO_APPLY has no Canonical Doc")
        for doc in docs:
            all_mapped.add(doc)
            doc_path = canonical_path(doc)
            if not doc_path.exists():
                errors.append(f"{delta_id} Canonical Doc does not exist: {doc}")
            else:
                doc_text = doc_path.read_text(encoding="utf-8")
                legacy_marker = "Round-002" in doc_text
                v31_structure = (
                    "## Part A — Architecture Narrative" in doc_text
                    and "## Part B — Detailed Architecture Specification" in doc_text
                )
                if not legacy_marker and not v31_structure:
                    errors.append(
                        f"{delta_id} Canonical Doc lacks a legacy Round-002 marker or V3.1 Part A/Part B structure: {doc}"
                    )
            if doc not in diff and str(doc_path.relative_to(ROOT)).replace("\\", "/") not in diff:
                errors.append(f"{delta_id} AUTO_APPLY Canonical Doc not changed from baseline: {doc}")
    if not all_mapped:
        errors.append("no AUTO_APPLY Canonical Docs were mapped")
    if "Facts changed: NONE" not in (session / "round-report.md").read_text(encoding="utf-8"):
        errors.append("round-report must keep facts unchanged")
    if "runtime_changed: NONE" not in (session / "manifest.yaml").read_text(encoding="utf-8"):
        errors.append("manifest must keep runtime_changed: NONE")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify V3 Canonical Diff trace")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_canonical_diff(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("canonical V3 diff verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
