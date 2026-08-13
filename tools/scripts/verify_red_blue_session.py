"""Validate the public record contract of a Red/Blue Campaign session.

This is intentionally a lightweight Markdown/YAML conformance checker.  It
does not run an interviewer, generate questions, score answers, or mutate
canonical architecture.  Its job is to make an already-recorded session
auditable and internally consistent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SESSIONS_ROOT = REPO_ROOT / "project-reconstruction-lab" / "sessions"
REQUIRED_SESSION_FILES = (
    "manifest.yaml",
    "transcript.md",
    "scorecard.md",
    "gaps.md",
    "blue-change-set.md",
    "retest.md",
)
ALLOWED_PHASES = {"BASELINE", "RETEST", "ADVERSARIAL_ESCALATION", "FULL_REVIEW"}
ALLOWED_STATUS = {"IN_PROGRESS", "COMPLETED", "STOPPED", "REOPENED"}
ALLOWED_SYNC_STATUS = {"NOT_APPLIED", "APPLIED", "PARTIAL", "REJECTED"}
ALLOWED_USER_GATE = {"PENDING", "APPROVED", "REJECTED"}
ALLOWED_RETEST_RESULTS = {"PASS", "REOPEN", "NOT_STARTED", "WAITING_FOR_CANONICAL_SYNC"}
SPECIALIZED_PROTOCOLS = {
    "ZUNO-RED-BLUE-WORKFLOW-V3",
    "ZUNO-RED-BLUE-WORKFLOW-V3.1",
    "ZUNO-RED-BLUE-WORKFLOW-V3.1.1",
    "ZUNO-RED-BLUE-WORKFLOW-V3.1.2",
    "ZUNO-RED-BLUE-WORKFLOW-V3.1.3",
    "ZUNO-BLUE-REPAIR-V1",
    "ZUNO-EVIDENCE-CLOSURE-V1",
    "ZUNO-P0-V4-EXECUTION-V1",
    "ZUNO-GATE-REALIGNMENT-V1",
    "ZUNO-RED-BLUE-WORKFLOW-V4",
    "IMPLEMENTATION-EVIDENCE-CYCLE-001",
    "RB-CLOSURE-SEMANTIC-AUDIT-V3.1.3.1",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sections(markdown: str, prefix: str) -> list[tuple[str, str]]:
    pattern = re.compile(rf"(?m)^##\s+({re.escape(prefix)}\d+)\s*$")
    matches = list(pattern.finditer(markdown))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections.append((match.group(1), markdown[match.start() : end]))
    return sections


def _ids(value: str, pattern: str) -> set[str]:
    return set(re.findall(pattern, value))


def _field(section: str, labels: Iterable[str]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(rf"(?im)^\s*(?:{label_pattern})\s*[:\uFF1A]\s*(.*?)\s*$", section)
    if match:
        return match.group(1).strip()
    heading = re.search(
        rf"(?im)^\s*(?:#{{1,6}}\s*)?(?:{label_pattern})\s*$\r?\n\s*([^\r\n]+)",
        section,
    )
    return heading.group(1).strip() if heading else None


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _is_none_marker(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().upper() in {"", "NONE", "NULL", "N/A", "-", "无"}


def _manifest(session_dir: Path, errors: list[str]) -> dict[str, Any]:
    path = session_dir / "manifest.yaml"
    if not path.exists():
        errors.append("missing manifest.yaml")
        return {}
    try:
        value = yaml.safe_load(_text(path))
    except yaml.YAMLError as exc:
        errors.append(f"manifest.yaml is invalid YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append("manifest.yaml must contain a mapping")
        return {}
    return value


def _validate_manifest(
    manifest: dict[str, Any],
    session_dir: Path,
    errors: list[str],
) -> tuple[int, int, str]:
    required = {
        "session_id",
        "campaign_id",
        "round_id",
        "parent_session_id",
        "baseline_session_id",
        "campaign_scope",
        "campaign_phase",
        "defense_base_sha",
        "post_sync_sha",
        "question_budget",
        "actual_question_count",
        "stop_reason",
        "red_kernel_version",
        "judge_policy_version",
        "source_scope",
        "status",
    }
    missing = sorted(key for key in required if key not in manifest)
    for key in missing:
        errors.append(f"manifest.yaml missing required field: {key}")

    session_id = str(manifest.get("session_id", ""))
    phase = str(manifest.get("campaign_phase", "")).upper()
    status = str(manifest.get("status", "")).upper()
    if phase and phase not in ALLOWED_PHASES:
        errors.append(f"manifest.yaml campaign_phase is invalid: {phase}")
    if status and status not in ALLOWED_STATUS:
        errors.append(f"manifest.yaml status is invalid: {status}")
    if _is_empty(manifest.get("session_id")):
        errors.append("manifest.yaml session_id must not be empty")
    if _is_empty(manifest.get("campaign_id")):
        errors.append("manifest.yaml campaign_id must not be empty")
    if _is_empty(manifest.get("round_id")):
        errors.append("manifest.yaml round_id must not be empty")
    if _is_empty(manifest.get("baseline_session_id")):
        errors.append("manifest.yaml baseline_session_id must not be empty")
    if _is_empty(manifest.get("defense_base_sha")):
        errors.append("manifest.yaml defense_base_sha must not be empty")
    if _is_empty(manifest.get("red_kernel_version")):
        errors.append("manifest.yaml red_kernel_version must not be empty")
    if _is_empty(manifest.get("judge_policy_version")):
        errors.append("manifest.yaml judge_policy_version must not be empty")
    if _is_empty(manifest.get("source_scope")):
        errors.append("manifest.yaml source_scope must not be empty")

    parent = manifest.get("parent_session_id")
    if phase == "BASELINE" and not _is_empty(parent):
        errors.append("BASELINE session must have parent_session_id: null")
    if phase != "BASELINE" and _is_empty(parent):
        errors.append(f"{phase} session must declare parent_session_id")

    budget = manifest.get("question_budget")
    actual = manifest.get("actual_question_count")
    if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
        errors.append("manifest.yaml question_budget must be a positive integer")
        budget = 0
    if not isinstance(actual, int) or isinstance(actual, bool) or actual < 0:
        errors.append("manifest.yaml actual_question_count must be a non-negative integer")
        actual = 0
    stop_reason = manifest.get("stop_reason")
    if actual > budget and budget:
        errors.append("actual_question_count must not exceed question_budget")
    if budget and actual < budget and _is_empty(stop_reason):
        errors.append("question_count below question_budget requires stop_reason")

    if not (session_dir / "manifest.yaml").exists():
        errors.append("manifest.yaml is required")
    if status == "COMPLETED":
        for name in REQUIRED_SESSION_FILES:
            if not (session_dir / name).exists():
                errors.append(f"COMPLETED session missing required file: {name}")
    return budget, actual, session_id


def _validate_transcript(
    content: str,
    budget: int,
    errors: list[str],
) -> tuple[list[str], set[str]]:
    sections = _sections(content, "Q")
    question_ids = [identifier for identifier, _ in sections]
    if not question_ids:
        errors.append("transcript.md must contain at least one ## QNNN section")
        return [], set()
    if len(question_ids) != len(set(question_ids)):
        errors.append("transcript.md contains duplicate Question ID")
    expected = [f"Q{index:03d}" for index in range(1, len(question_ids) + 1)]
    if question_ids != expected:
        errors.append(f"transcript Question IDs must be continuous Q001..QNNN; got {question_ids}")
    if budget and len(question_ids) > budget:
        errors.append("transcript question count exceeds question_budget")

    gap_refs: set[str] = set()
    for question_id, section in sections:
        score_ref = _field(section, ("Scorecard Ref",))
        if score_ref != question_id:
            errors.append(f"{question_id} must contain Scorecard Ref: {question_id}")
        gap_value = _field(section, ("Gap Candidate Refs", "Gap Refs"))
        if gap_value is None:
            errors.append(f"{question_id} must contain Gap Candidate Refs")
        elif not _is_none_marker(gap_value):
            refs = _ids(gap_value, r"GAP-[A-Za-z0-9][A-Za-z0-9._-]*")
            if not refs:
                errors.append(f"{question_id} Gap Candidate Refs must contain GAP-* IDs or NONE")
            gap_refs.update(refs)
    return question_ids, gap_refs


def _validate_scorecard(content: str, question_ids: set[str], errors: list[str]) -> None:
    score_ids = re.findall(r"(?m)^\|\s*(Q\d+)\s*\|", content)
    if not score_ids:
        errors.append("scorecard.md must contain a Question ID table")
        score_ids = []
    if len(score_ids) != len(set(score_ids)):
        errors.append("scorecard.md contains duplicate Question ID rows")
    score_set = set(score_ids)
    missing = sorted(question_ids - score_set)
    orphan = sorted(score_set - question_ids)
    for identifier in missing:
        errors.append(f"scorecard.md missing row for {identifier}")
    for identifier in orphan:
        errors.append(f"scorecard.md references unknown Question ID: {identifier}")

    lowered = content.lower()
    for marker in (
        "## campaign quality profile",
        "question_count",
        "avg_answer_defensibility",
        "avg_architecture_project_fitness",
        "p0_count",
        "p1_count",
        "unsupported_count",
        "unsupported_rate",
        "## campaign summary",
        "coverage_status",
        "p0_total",
        "p1_total",
        "reopened_gap_count",
        "## baseline delta",
    ):
        if marker not in lowered:
            errors.append(f"scorecard.md missing Campaign Quality Profile marker: {marker}")

    profile_rows = re.findall(
        r"(?im)^\|\s*([A-Z][A-Z0-9_]+)\s*\|\s*(\d+)\s*\|",
        content,
    )
    if not profile_rows:
        errors.append("scorecard.md Campaign Quality Profile must contain Attack Area rows")
    elif sum(int(count) for _, count in profile_rows) != len(question_ids):
        errors.append("Campaign Quality Profile question_count must sum to transcript question count")


def _validate_gaps(
    content: str,
    question_ids: set[str],
    errors: list[str],
) -> tuple[set[str], set[str]]:
    sections = _sections(content, "CLUSTER-")
    cluster_ids = {identifier for identifier, _ in sections}
    if not sections:
        errors.append("gaps.md must contain at least one ## CLUSTER-NNN section")
    if len(cluster_ids) != len(sections):
        errors.append("gaps.md contains duplicate Cluster ID")

    gap_ids: set[str] = set()
    for cluster_id, section in sections:
        gap_value = _field(section, ("Gap IDs", "Gap ID"))
        if gap_value is None or _is_none_marker(gap_value):
            errors.append(f"{cluster_id} must declare Gap IDs")
        else:
            gap_ids.update(_ids(gap_value, r"GAP-[A-Za-z0-9][A-Za-z0-9._-]*"))
        question_value = _field(section, ("Questions", "Question IDs"))
        if question_value is None:
            errors.append(f"{cluster_id} must declare Questions")
        else:
            unknown = _ids(question_value, r"Q\d+") - question_ids
            for identifier in sorted(unknown):
                errors.append(f"{cluster_id} references unknown Question ID: {identifier}")
    return cluster_ids, gap_ids


def _validate_changes(
    content: str,
    cluster_ids: set[str],
    errors: list[str],
) -> tuple[set[str], dict[str, str], dict[str, set[str]]]:
    sections = _sections(content, "CHANGE-")
    change_ids = {identifier for identifier, _ in sections}
    sync_status: dict[str, str] = {}
    change_retests: dict[str, set[str]] = {}
    if not sections:
        errors.append("blue-change-set.md must contain at least one ## CHANGE-NNN section")
    if len(change_ids) != len(sections):
        errors.append("blue-change-set.md contains duplicate Change ID")

    required_fields = (
        "Source Cluster IDs",
        "User Gate",
        "Sync Status",
        "Canonical Paths",
        "Applied Commit SHA",
        "Validation Run",
        "Validation Not Run",
        "Retest IDs",
    )
    for change_id, section in sections:
        for label in required_fields:
            if _field(section, (label,)) is None:
                errors.append(f"{change_id} missing traceability field: {label}")
        source_value = _field(section, ("Source Cluster IDs",))
        if source_value and not _is_none_marker(source_value):
            for cluster_id in sorted(_ids(source_value, r"CLUSTER-\d+")):
                if cluster_id not in cluster_ids:
                    errors.append(f"{change_id} references unknown Cluster ID: {cluster_id}")
        gate = (_field(section, ("User Gate",)) or "").upper()
        if gate and gate not in ALLOWED_USER_GATE:
            errors.append(f"{change_id} has invalid User Gate: {gate}")
        status = (_field(section, ("Sync Status",)) or "").upper()
        if status not in ALLOWED_SYNC_STATUS:
            errors.append(f"{change_id} has invalid Sync Status: {status}")
        sync_status[change_id] = status
        if status == "APPLIED":
            if gate != "APPROVED":
                errors.append(f"{change_id} APPLIED requires User Gate: APPROVED")
            commit = _field(section, ("Applied Commit SHA",))
            if _is_none_marker(commit):
                errors.append(f"{change_id} APPLIED requires Applied Commit SHA")
            paths = _field(section, ("Canonical Paths",))
            if _is_none_marker(paths):
                errors.append(f"{change_id} APPLIED requires Canonical Paths")
        retest_value = _field(section, ("Retest IDs",))
        change_retests[change_id] = (
            set() if _is_none_marker(retest_value) else _ids(retest_value or "", r"RETEST-\d+")
        )
    return change_ids, sync_status, change_retests


def _validate_retests(
    content: str,
    gap_ids: set[str],
    change_ids: set[str],
    sync_status: dict[str, str],
    errors: list[str],
) -> set[str]:
    sections = _sections(content, "RETEST-")
    retest_ids = {identifier for identifier, _ in sections}
    if not sections:
        errors.append("retest.md must contain at least one ## RETEST-NNN section")
    if len(retest_ids) != len(sections):
        errors.append("retest.md contains duplicate Retest ID")

    for retest_id, section in sections:
        gap_value = _field(section, ("上一轮 Gap", "Gap IDs", "Previous Gap IDs"))
        for gap_id in sorted(_ids(gap_value or "", r"GAP-[A-Za-z0-9][A-Za-z0-9._-]*")):
            if gap_id not in gap_ids:
                errors.append(f"{retest_id} references unknown Gap ID: {gap_id}")
        change_value = _field(section, ("Change IDs", "Change ID", "Change Refs"))
        for change_id in sorted(_ids(change_value or "", r"CHANGE-\d+")):
            if change_id not in change_ids:
                errors.append(f"{retest_id} references unknown Change ID: {change_id}")
            elif sync_status.get(change_id) != "APPLIED":
                errors.append(f"{retest_id} may only use APPLIED Change: {change_id}")
        mutation = _field(section, ("Mutation Variable",))
        if _is_empty(mutation) or _is_none_marker(mutation):
            errors.append(f"{retest_id} must declare Mutation Variable")
        result = (_field(section, ("Result",)) or "").upper()
        if result not in ALLOWED_RETEST_RESULTS:
            errors.append(f"{retest_id} has invalid Result: {result}")
    return retest_ids


def verify_session(session_dir: Path, known_session_ids: set[str] | None = None) -> list[str]:
    """Return conformance errors for one session directory."""

    errors: list[str] = []
    if not session_dir.is_dir():
        return [f"session directory does not exist: {session_dir}"]
    manifest = _manifest(session_dir, errors)
    budget, declared_count, session_id = _validate_manifest(manifest, session_dir, errors)
    if known_session_ids is not None and session_id:
        parent = manifest.get("parent_session_id")
        baseline = manifest.get("baseline_session_id")
        if not _is_empty(parent) and parent not in known_session_ids:
            errors.append(f"manifest parent_session_id does not resolve: {parent}")
        if baseline and baseline not in known_session_ids and baseline != session_id:
            errors.append(f"manifest baseline_session_id does not resolve: {baseline}")

    files = {name: session_dir / name for name in REQUIRED_SESSION_FILES}
    if not files["transcript.md"].exists():
        errors.append("missing transcript.md")
        return errors
    question_ids, transcript_gap_refs = _validate_transcript(
        _text(files["transcript.md"]), budget, errors
    )
    if declared_count != len(question_ids):
        errors.append(
            f"manifest actual_question_count={declared_count} does not match transcript={len(question_ids)}"
        )

    if not files["scorecard.md"].exists():
        errors.append("missing scorecard.md")
        scorecard = ""
    else:
        scorecard = _text(files["scorecard.md"])
        _validate_scorecard(scorecard, set(question_ids), errors)
    if not files["gaps.md"].exists():
        errors.append("missing gaps.md")
        cluster_ids, gap_ids = set(), set()
    else:
        cluster_ids, gap_ids = _validate_gaps(_text(files["gaps.md"]), set(question_ids), errors)
    for gap_ref in sorted(transcript_gap_refs - gap_ids):
        errors.append(f"transcript references unknown Gap ID: {gap_ref}")

    if not files["blue-change-set.md"].exists():
        errors.append("missing blue-change-set.md")
        change_ids, sync_status, change_retests = set(), {}, {}
    else:
        change_ids, sync_status, change_retests = _validate_changes(
            _text(files["blue-change-set.md"]), cluster_ids, errors
        )
    if not files["retest.md"].exists():
        errors.append("missing retest.md")
        retest_ids = set()
    else:
        retest_ids = _validate_retests(
            _text(files["retest.md"]), gap_ids, change_ids, sync_status, errors
        )
    for change_id, refs in change_retests.items():
        for retest_id in sorted(refs - retest_ids):
            errors.append(f"{change_id} references unknown Retest ID: {retest_id}")
    try:
        display_path = session_dir.relative_to(REPO_ROOT)
    except ValueError:
        display_path = session_dir
    return [f"{display_path}: {error}" for error in errors]


def _session_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    sessions: list[Path] = []
    for path in root.iterdir():
        if not path.is_dir() or path.name == "TEMPLATE" or path.name.startswith("_"):
            continue
        if path.name == "IMPLEMENTATION-EVIDENCE-CYCLE-001":
            # The implementation evidence track has its own README/review-package contract.
            continue
        manifest_path = path / "manifest.yaml"
        if manifest_path.exists():
            try:
                manifest = yaml.safe_load(_text(manifest_path)) or {}
            except yaml.YAMLError:
                manifest = {}
            if isinstance(manifest, dict) and (
                manifest.get("protocol_version") in SPECIALIZED_PROTOCOLS
                or manifest.get("workflow_id") in SPECIALIZED_PROTOCOLS
                or manifest.get("audit_protocol") in SPECIALIZED_PROTOCOLS
            ):
                # Specialized sessions have their own verifier and contract.
                continue
        sessions.append(path)
    return sorted(sessions)


def verify_root(root: Path = SESSIONS_ROOT) -> list[str]:
    sessions = _session_dirs(root)
    if not sessions:
        return []
    known_ids: set[str] = set()
    for session_dir in sessions:
        manifest_path = session_dir / "manifest.yaml"
        if manifest_path.exists():
            try:
                value = yaml.safe_load(_text(manifest_path)) or {}
                if isinstance(value, dict) and value.get("session_id"):
                    known_ids.add(str(value["session_id"]))
            except yaml.YAMLError:
                pass
    errors: list[str] = []
    for session_dir in sessions:
        errors.extend(verify_session(session_dir, known_session_ids=known_ids))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Red/Blue Campaign session conformance")
    parser.add_argument("session", nargs="*", type=Path, help="session directory; default verifies all sessions")
    args = parser.parse_args(argv)
    if args.session:
        errors: list[str] = []
        for path in args.session:
            resolved = path if path.is_absolute() else (REPO_ROOT / path)
            errors.extend(verify_session(resolved))
    else:
        errors = verify_root()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue session conformance passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
