from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WAVE_VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
INFRA_VERIFIER = ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"


def main() -> None:
    text = WAVE_VERIFIER.read_text(encoding="utf-8")
    text = text.replace(
        '    "previous_status: parallel-proposal-governance",\n',
        '    "previous_status: field-frozen-pending-merge",\n',
        1,
    )
    text = text.replace(
        '''    if "accepted-target-pending-merge" not in adr or "field-frozen-pending-merge" not in registry:
        findings.append(Finding("XMOD_STATUS_INVALID", "ADR/Registry pending-merge status is inconsistent"))
''',
        '''    if "status: accepted-target" not in adr or "status: confirmed-target" not in registry:
        findings.append(Finding("XMOD_STATUS_INVALID", "ADR/Registry confirmed Target status is inconsistent"))
''',
        1,
    )
    WAVE_VERIFIER.write_text(text, encoding="utf-8", newline="\n")

    text = INFRA_VERIFIER.read_text(encoding="utf-8")
    text = text.replace(
        '    "parallel-proposal-governance",\n',
        '    "status: confirmed-target",\n    "previous_status: field-frozen-pending-merge",\n',
        1,
    )
    INFRA_VERIFIER.write_text(text, encoding="utf-8", newline="\n")
    print("Confirmed Wave 1 and Infrastructure verifier assertions fixed.")


if __name__ == "__main__":
    main()
