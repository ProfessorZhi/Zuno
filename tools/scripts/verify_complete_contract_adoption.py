from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "contracts"
FIXTURE_ROOT = REPO_ROOT / "tests" / "contracts" / "fixtures"

CANONICAL_MODULES = {
    "Product Surface",
    "Input / Document Ingestion",
    "Knowledge",
    "Model Gateway",
    "Memory",
    "Agent Core",
    "Capability",
    "Tool Runtime",
    "Security",
    "Observability",
    "Infrastructure",
}

REPRESENTATIVE_FIXTURES = {
    "CrossModuleEnvelopeV1",
    "FailureCodeV1",
    "ProductCommandV1",
    "SourceObjectRefV1",
    "CapabilityInvocationRefV1",
    "InfrastructureLeaseRefV1",
}


def _expand_module(value: str) -> set[str]:
    if value == "ALL":
        return set(CANONICAL_MODULES)
    if value == "Knowledge/Memory":
        return {"Knowledge", "Memory"}
    if value in CANONICAL_MODULES:
        return {value}
    return set()


def _contract_class_names() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for path in CONTRACT_ROOT.glob("*.py"):
        if path.name == "__init__.py":
            continue
        text = path.read_text(encoding="utf-8")
        for name in re.findall(r"(?m)^class\s+([A-Za-z0-9_]+V1)\b", text):
            result.setdefault(name, []).append(path.name)
    return result


def verify_complete_contract_adoption() -> list[str]:
    errors: list[str] = []
    try:
        contracts = importlib.import_module("zuno.platform.contracts")
        shared = importlib.import_module("zuno.platform.contracts.shared")
        manifest = contracts.build_wave1_contract_registry().manifest()
    except Exception as exc:  # pragma: no cover - reported as verifier error
        return [f"cannot load contract adoption registry: {exc}"]

    adopted_modules: set[str] = set()
    names: set[str] = set()
    for entry in manifest.entries:
        names.add(entry.contract_name)
        adopted_modules.update(_expand_module(entry.owner_module))
        for producer in entry.producer_modules:
            adopted_modules.update(_expand_module(producer))
        for consumer in entry.consumer_modules:
            adopted_modules.update(_expand_module(consumer))
        if not entry.schema_hash:
            errors.append(f"contract missing schema_hash: {entry.contract_name}")
        if not entry.producer_modules:
            errors.append(f"contract missing producer_modules: {entry.contract_name}")
        if not entry.consumer_modules:
            errors.append(f"contract missing consumer_modules: {entry.contract_name}")
        if entry.compatibility not in {"CURRENT_MAJOR", "READ_MINOR", "ADAPTER_REQUIRED", "REJECT"}:
            errors.append(f"contract has invalid compatibility policy: {entry.contract_name}")

    missing_modules = sorted(CANONICAL_MODULES - adopted_modules)
    if missing_modules:
        errors.append(f"contract adoption missing canonical modules: {missing_modules}")

    definitions = _contract_class_names()
    for name, files in sorted(definitions.items()):
        if len(files) > 1:
            errors.append(f"duplicate contract class definition: {name} in {files}")
    for name in names:
        if name not in definitions:
            errors.append(f"registry contract has no class definition: {name}")
    for name in definitions:
        if name.endswith("V1") and name not in names and name not in {"ContractRef"}:
            errors.append(f"contract class missing from registry: {name}")

    for fixture_name in REPRESENTATIVE_FIXTURES:
        fixture_path = FIXTURE_ROOT / f"{fixture_name}.json"
        if not fixture_path.exists():
            errors.append(f"missing representative contract fixture: {fixture_name}.json")
            continue
        model = getattr(shared, fixture_name)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        try:
            model.model_validate(payload)
        except Exception as exc:  # pragma: no cover - reported as verifier error
            errors.append(f"invalid representative fixture {fixture_name}.json: {exc}")
    return errors


def main() -> int:
    errors = verify_complete_contract_adoption()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE03 complete contract adoption verification failed.")
        return 1
    print("PHASE03 complete contract adoption verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
