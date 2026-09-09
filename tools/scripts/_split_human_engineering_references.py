from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ARCH_PART_B = "## Part B — Engineering / Agent Reference（工程 / Agent 参考）"
MODULE_PART_B = "## Part B — Engineering / Agent Reference"

MODULES = (
    "application",
    "domain",
    "knowledge",
    "runtime",
    "capability",
    "effects",
    "model-gateway",
    "security",
    "evaluation",
)


def split_once(text: str, marker: str, label: str) -> tuple[str, str]:
    if text.count(marker) != 1:
        raise RuntimeError(f"{label}: expected exactly one split marker {marker!r}")
    before, after = text.split(marker, 1)
    return before.rstrip() + "\n", marker + after


def split_architecture() -> None:
    readme = ROOT / "docs/architecture/README.md"
    human, engineering = split_once(readme.read_text(encoding="utf-8"), ARCH_PART_B, "architecture")
    human += "\n---\n\n工程 / Agent 精确参考见 [`reference.md`](reference.md)。\n"
    reference = (
        "# Overall Architecture Engineering Reference\n\n"
        "status: canonical-architecture-engineering-reference\n"
        "owner: Cross-cutting Architecture Owner\n"
        "human_source: docs/architecture/README.md\n"
        "module_router: docs/modules/reference.md\n"
        "decision_source: docs/decisions/\n"
        "evidence_source: docs/evidence/\n\n"
        + engineering
    )
    readme.write_text(human, encoding="utf-8")
    (ROOT / "docs/architecture/reference.md").write_text(reference, encoding="utf-8")


def split_module(name: str) -> None:
    root = ROOT / "docs/modules" / name
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    human, engineering = split_once(text, MODULE_PART_B, name)
    title = text.splitlines()[0].removeprefix("# ").strip()
    human += "\n---\n\n工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。\n"
    reference = (
        f"# {title} — Engineering Reference\n\n"
        "human_source: README.md\n"
        "overall_architecture: ../../architecture/reference.md\n"
        "current_evidence: ../../evidence/\n\n"
        + engineering
    )
    readme.write_text(human, encoding="utf-8")
    (root / "reference.md").write_text(reference, encoding="utf-8")


def verify_split() -> None:
    architecture = (ROOT / "docs/architecture/README.md").read_text(encoding="utf-8")
    architecture_ref = (ROOT / "docs/architecture/reference.md").read_text(encoding="utf-8")
    if ARCH_PART_B in architecture or ARCH_PART_B not in architecture_ref:
        raise RuntimeError("architecture split invariant failed")
    for name in MODULES:
        human = (ROOT / "docs/modules" / name / "README.md").read_text(encoding="utf-8")
        reference = (ROOT / "docs/modules" / name / "reference.md").read_text(encoding="utf-8")
        if MODULE_PART_B in human or MODULE_PART_B not in reference:
            raise RuntimeError(f"{name}: split invariant failed")
        if "## Part C — Cross-Module Consistency" not in reference:
            raise RuntimeError(f"{name}: Part C missing from reference")


def main() -> None:
    split_architecture()
    for name in MODULES:
        split_module(name)
    verify_split()


if __name__ == "__main__":
    main()
