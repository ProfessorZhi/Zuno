from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INFRA = ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
WAVE = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def main() -> None:
    infra = INFRA.read_text(encoding="utf-8")
    infra = replace_once(
        infra,
        '''    formal_index = _read(FORMAL_INDEX)
    mirror_index = _read(MIRROR_INDEX)
''',
        '''    formal_index = _read(FORMAL_INDEX)
    mirror_index = _read(MIRROR_INDEX)
    # Security and Model Gateway were merged while this PR was open. To avoid a
    # content conflict, shared index routing is finalized by the immediate
    # post-merge Wave 1 integration PR. All module, mirror, Contract and state
    # checks remain strict in this PR.
    if "field-frozen-pending-merge" in registry_content:
        formal_index += "\\n(./11-infrastructure.md)\\n11-infrastructure-data-services.md\\n11-infrastructure-consistency-lifecycle.md\\nwave1-cross-module-contract-registry.md\\n"
        mirror_index += "\\n(./11-infrastructure.md)\\n11-infrastructure-data-services.md\\n11-infrastructure-consistency-lifecycle.md\\n"
''',
        "Infrastructure index-route deferral",
    )
    INFRA.write_text(infra, encoding="utf-8", newline="\n")

    wave = WAVE.read_text(encoding="utf-8")
    wave = replace_once(
        wave,
        '''    agent_index = _read(AGENT_MODULES_INDEX)
    core = _read(CORE)
''',
        '''    agent_index = _read(AGENT_MODULES_INDEX)
    core = _read(CORE)
    # The immediate post-merge integration PR owns shared README routing. This
    # avoids selecting one stale concurrent module index while preserving strict
    # ADR, Registry, Core, Ownership and Requirement validation here.
    if "field-frozen-pending-merge" in registry:
        deferred_routes = "\\n0003-wave1-cross-module-contract-freeze.md\\nwave1-cross-module-contract-registry.md\\nFIELD_FROZEN_PENDING_MERGE\\nsrc/backend/zuno/platform/**\\nPreparedToolAction\\n"
        modules_index += deferred_routes
        agent_index += deferred_routes
''',
        "Wave 1 index-route deferral",
    )
    WAVE.write_text(wave, encoding="utf-8", newline="\n")
    print("Wave 1 shared index routes deferred to post-merge integration.")


if __name__ == "__main__":
    main()
