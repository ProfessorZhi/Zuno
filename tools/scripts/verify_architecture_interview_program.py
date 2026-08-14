"""Validate the lightweight architecture interview lab contract."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "project-reconstruction-lab"
ARCHIVE = ROOT / "docs/history/red-blue"
SKILLS = {
    "red-team-interviewer",
    "architecture-red-blue-loop",
    "jd-enterprise-project",
}
SKILL_MARKERS = {
    "red-team-interviewer": ("ACTIVATION: EXPLICIT_ONLY", "MODES: QUESTION | REVIEW", "DEFAULT_OUTPUT: QUESTIONS_ONLY"),
    "architecture-red-blue-loop": ("DEFAULT ACTIVATION: EXPLICIT_ONLY", "MANUAL_MAIN", "AUTOMATED_MAIN", "PROPOSED_MAIN_JUDGMENT"),
    "jd-enterprise-project": ("ACTIVATION: EXPLICIT_ONLY", "COMPOSITION: EXPLICIT_ONLY", "CURRENT", "TARGET", "GAP", "EVIDENCE_REQUIRED"),
}
ARCHIVE_FIELDS = {
    "series",
    "round_id",
    "execution_mode",
    "status",
    "base_sha",
    "archive_commit",
    "architecture_revision_commit",
}
OLD_LAB_PATH = re.compile(
    r"project-reconstruction-lab/(?:00-charter|01-facts|02-history|03-current|04-product|"
    r"05-red-blue|06-architecture|07-interview-red-team|08-decisions|09-implementation|"
    r"10-reports|legacy|sources|workflows|sessions)(?:/|$)"
)


def _metadata(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines()[:20]:
        if ":" not in line or line.startswith("<!--"):
            continue
        key, value = line.split(":", 1)
        if key.strip() in ARCHIVE_FIELDS:
            result[key.strip()] = value.strip().strip("`")
    return result


def verify(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    lab = root / "project-reconstruction-lab"
    expected_lab = {"README.md", "WORKFLOW.md", "archive-map.md", "skills"}
    actual_lab = {path.name for path in lab.iterdir()}
    if actual_lab != expected_lab:
        errors.append(f"Lab top-level mismatch: expected {sorted(expected_lab)}, got {sorted(actual_lab)}")

    skills = lab / "skills"
    actual_skills = {path.name for path in skills.iterdir()}
    expected_skills_root = SKILLS | {"README.md"}
    if actual_skills != expected_skills_root:
        errors.append(f"Skill directory mismatch: expected {sorted(expected_skills_root)}, got {sorted(actual_skills)}")
    for name in SKILLS:
        skill_dir = skills / name
        files = {path.name for path in skill_dir.iterdir()}
        if files != {"SKILL.md"}:
            errors.append(f"{name} must contain only SKILL.md, got {sorted(files)}")
        else:
            content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            if not content.startswith("---\n") or "name:" not in content or "description:" not in content:
                errors.append(f"{name}/SKILL.md has invalid frontmatter")
            for section in ("## Purpose", "## Inputs", "## Workflow", "## Outputs", "## Boundaries", "## Failure / Stop Conditions", "## Evidence Rules", "## Example Invocation"):
                if section not in content:
                    errors.append(f"{name}/SKILL.md missing {section}")

    system_yaml = root / ".agent/system.yaml"
    if system_yaml.exists():
        system_content = system_yaml.read_text(encoding="utf-8")
        if "mode: \"REPOSITORY_LOCAL_EXPLICIT_ONLY\"" not in system_content:
            errors.append("system.yaml must declare repository-local explicit-only Skill mode")
        if "discovery: \"EXPLICIT_ONLY\"" not in system_content:
            errors.append("system.yaml must declare EXPLICIT_ONLY Skill discovery")
        if "PATH_TRIGGERED" in system_content:
            errors.append("system.yaml must not contain PATH_TRIGGERED")
        for name in SKILLS:
            expected = f"project-reconstruction-lab/skills/{name}/SKILL.md"
            if expected not in system_content:
                errors.append(f"system.yaml missing local Skill registration: {name}")

    workflow = lab / "WORKFLOW.md"
    workflow_content = workflow.read_text(encoding="utf-8") if workflow.exists() else ""
    for marker in ("DEFAULT_MODE: MANUAL_CHATGPT", "## Actor Ownership", "### ChatGPT Main Coordinator", "### ChatGPT Red", "### ChatGPT Blue", "### Codex", "Architecture Decision Owner", "Codex 不负责"):
        if marker not in workflow_content:
            errors.append(f"WORKFLOW.md missing ownership marker: {marker}")

    skills_readme = skills / "README.md"
    skills_readme_content = skills_readme.read_text(encoding="utf-8") if skills_readme.exists() else ""
    for marker in ("REPOSITORY LOCAL", "EXPLICIT INVOCATION", "NOT CANONICAL", "NOT AUTO-EXECUTED"):
        if marker not in skills_readme_content:
            errors.append(f"skills/README.md missing local Skill marker: {marker}")
    for name, markers in SKILL_MARKERS.items():
        skill_path = skills / name / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
        for marker in markers:
            if marker not in content:
                errors.append(f"{name}/SKILL.md missing governance marker: {marker}")

    archive = root / "docs/history/red-blue"
    archive_files = sorted(path for path in archive.glob("*.md"))
    if not (archive / "README.md").exists():
        errors.append("missing docs/history/red-blue/README.md")
    if not (archive / "legacy-automated-rounds.md").exists():
        errors.append("missing docs/history/red-blue/legacy-automated-rounds.md")

    allowed = {"README.md", "legacy-automated-rounds.md"}
    manual_files: list[Path] = []
    for path in archive_files:
        if path.name.startswith("manual-round-") and path.suffix == ".md":
            manual_files.append(path)
            allowed.add(path.name)
        elif path.name not in allowed:
            errors.append(f"unexpected Red/Blue archive file: {path.relative_to(root)}")

    if not manual_files:
        errors.append("missing manual Red/Blue Round archive")

    for path in manual_files:
        metadata = _metadata(path)
        missing = ARCHIVE_FIELDS - metadata.keys()
        if missing:
            errors.append(f"{path.relative_to(root)} missing metadata: {sorted(missing)}")
        if metadata.get("execution_mode") != "MANUAL":
            errors.append(f"{path.relative_to(root)} must have execution_mode: MANUAL")
        if not metadata.get("base_sha"):
            errors.append(f"{path.relative_to(root)} has empty base_sha")

    legacy_summary = archive / "legacy-automated-rounds.md"
    if legacy_summary.exists():
        legacy_content = legacy_summary.read_text(encoding="utf-8")
        if "ABORTED_OPERATIONAL_PILOT" not in legacy_content or "architecture_score: INVALID" not in legacy_content:
            errors.append("legacy summary must preserve Round-006 aborted and invalid-score semantics")
        if "score_validity: INVALID" not in legacy_content:
            errors.append("legacy summary must declare Round-006 score_validity: INVALID")

    active_routes = [
        root / "AGENTS.md",
        root / ".agent/system.yaml",
        root / ".agent/references/current-program.md",
        root / ".agent/references/docs-map.md",
        root / ".agent/references/task-routing.md",
        root / ".agent/references/workflow.md",
        root / ".agent/references/verification-map.md",
       lab / "README.md",
       lab / "WORKFLOW.md",
       lab / "archive-map.md",
        lab / "skills/README.md",
       archive / "README.md",
    ]
    for path in active_routes:
        if not path.exists():
            errors.append(f"missing active route: {path.relative_to(root)}")
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if OLD_LAB_PATH.search(line):
                errors.append(f"active old Lab path at {path.relative_to(root)}:{line_number}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        print("ARCHITECTURE_INTERVIEW_PROGRAM_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ARCHITECTURE_INTERVIEW_PROGRAM_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
