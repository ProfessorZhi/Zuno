from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = ROOT / ".agent/modules/06-agent-core-planning-control.md"
VERIFIER = ROOT / "tools/scripts/verify_agent_core_target_protocols.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def main() -> None:
    document = FORMAL.read_text(encoding="utf-8")
    document = replace_once(
        document,
        "├── agent_activation_conditions\n└── agent_step_acceptance_criteria",
        "├── agent_activation_conditions\n├── agent_step_acceptance_criteria\n├── agent_step_feasibility_decisions\n└── agent_graph_bundles",
        "Plan Definition target tables",
    )
    FORMAL.write_text(document, encoding="utf-8", newline="\n")
    MIRROR.write_text(document, encoding="utf-8", newline="\n")

    verifier = VERIFIER.read_text(encoding="utf-8")
    verifier = replace_once(
        verifier,
        '    "PlanVersion Transition Matrix",\n',
        '    "完整子状态机 Transition Matrix",\n',
        "transition matrix required term",
    )
    VERIFIER.write_text(verifier, encoding="utf-8", newline="\n")
    print("focused Agent Core P0/P1 validation fixes applied")


if __name__ == "__main__":
    main()
