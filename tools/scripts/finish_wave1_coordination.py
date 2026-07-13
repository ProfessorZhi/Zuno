from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
DIAGNOSTIC = ROOT / "validation-logs/wave1-coordinate.log"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = VERIFIER.read_text(encoding="utf-8")

    text = replace_once(
        text,
        'AGENT_MODULES_INDEX = REPO_ROOT / ".agent/modules/README.md"\n',
        'AGENT_MODULES_INDEX = REPO_ROOT / ".agent/modules/README.md"\nCORE = REPO_ROOT / "docs/modules/06-agent-core-planning-control.md"\nCORE_MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md"\n',
        "core path constants",
    )

    text = replace_once(
        text,
        'ADR_TERMS = [\n    "status: accepted-target-pending-merge",\n    "CrossModuleEnvelopeV1",\n',
        'ADR_TERMS = [\n    "status: accepted-target-pending-merge",\n    "CrossModuleEnvelopeV1",\n    "服务端权威产品边界",\n    "contract_bundle_version",\n    "consumer_module",\n    "payload_schema_hash",\n',
        "ADR required terms",
    )

    text = replace_once(
        text,
        'REGISTRY_TERMS = [\n    "status: field-frozen-pending-merge",\n    "previous_status: parallel-proposal-governance",\n    "CrossModuleEnvelopeV1",\n',
        'REGISTRY_TERMS = [\n    "status: field-frozen-pending-merge",\n    "previous_status: parallel-proposal-governance",\n    "CrossModuleEnvelopeV1",\n    "产品部署边界",\n    "contract_bundle_version",\n    "consumer_module",\n    "payload_schema_hash",\n',
        "Registry required terms",
    )

    text = replace_once(
        text,
        '        (AGENT_MODULES_INDEX, "XMOD_AGENT_INDEX_MISSING"),\n',
        '        (AGENT_MODULES_INDEX, "XMOD_AGENT_INDEX_MISSING"),\n        (CORE, "XMOD_CORE_MISSING"),\n        (CORE_MIRROR, "XMOD_CORE_MIRROR_MISSING"),\n',
        "core required paths",
    )

    text = replace_once(
        text,
        '    agent_index = _read(AGENT_MODULES_INDEX)\n',
        '    agent_index = _read(AGENT_MODULES_INDEX)\n    core = _read(CORE)\n',
        "core read",
    )

    checks = '''    if CORE.read_bytes() != CORE_MIRROR.read_bytes():
        findings.append(Finding("XMOD_CORE_MIRROR_DRIFT", "Agent Core formal document and mirror differ"))
    for term in [
        "ActionProposal",
        "ActionExecutionBinding",
        "PreparedToolAction",
        "agent_action_proposals",
        "agent_action_execution_bindings",
        "contract_bundle_version",
        "consumer_module",
        "effective_security_epoch_ref",
        "payload_schema_hash",
    ]:
        _require(core, term, "XMOD_CORE_ALIGNMENT", findings)
    for forbidden in [
        "`PreparedAction`、`ArtifactVersion`",
        "agent_prepared_actions",
    ]:
        if forbidden in core:
            findings.append(Finding("XMOD_CORE_LEGACY_OWNERSHIP", f"legacy Agent Core ownership remains: {forbidden}"))

'''
    if "XMOD_CORE_MIRROR_DRIFT" not in text:
        anchor = '''    core = _read(CORE)

    for content, label in [(adr, "ADR"), (registry, "REGISTRY")]:
'''
        replacement = '''    core = _read(CORE)

''' + checks + '''    for content, label in [(adr, "ADR"), (registry, "REGISTRY")]:
'''
        text = replace_once(text, anchor, replacement, "core alignment checks")

    VERIFIER.write_text(text, encoding="utf-8", newline="\n")
    if DIAGNOSTIC.exists():
        DIAGNOSTIC.unlink()
    print("Wave 1 verifier alignment completed.")


if __name__ == "__main__":
    main()
