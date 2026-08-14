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

    archive = root / "docs/history/red-blue"
    archive_files = sorted(archive.glob("*.md"))
    if not (archive / "README.md").exists():
        errors.append("missing docs/history/red-blue/README.md")
    if len(archive_files) < 10:
        errors.append(f"expected at least 10 formal Round archives, got {len(archive_files)}")
    for path in archive_files:
        if path.name == "README.md":
            continue
        metadata = _metadata(path)
        missing = ARCHIVE_FIELDS - metadata.keys()
        if missing:
            errors.append(f"{path.relative_to(root)} missing metadata: {sorted(missing)}")
        if metadata.get("execution_mode") not in {"MANUAL", "AUTOMATED"}:
            errors.append(f"{path.relative_to(root)} has invalid execution_mode")
        if not metadata.get("base_sha"):
            errors.append(f"{path.relative_to(root)} has empty base_sha")

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
