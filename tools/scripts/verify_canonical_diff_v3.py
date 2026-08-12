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


def changed_files(baseline: str) -> set[str]:
    paths: set[str] = set()
    for args in (("diff", "--name-only", baseline), ("diff", "--cached", "--name-only", baseline)):
        result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            paths.update(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())
    return paths


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
    forbidden_prefixes = ("src/", "apps/", "infra/", "migrations/", "migration/")
    forbidden_names = {"pyproject.toml", "poetry.lock", "requirements.txt", "package-lock.json", "pnpm-lock.yaml"}
    for path in sorted(diff):
        if path.startswith(forbidden_prefixes) or path in forbidden_names:
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
            doc_path = ROOT / doc
            if not doc_path.exists():
                errors.append(f"{delta_id} Canonical Doc does not exist: {doc}")
            elif "Round-002" not in doc_path.read_text(encoding="utf-8"):
                errors.append(f"{delta_id} Canonical Doc lacks the Round-002 sync marker: {doc}")
            if doc not in diff:
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
