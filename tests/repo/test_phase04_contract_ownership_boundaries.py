from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_contract_ownership_boundaries.py"
)


def _module():
    spec = spec_from_file_location(
        "verify_phase04_contract_ownership_boundaries", VERIFIER
    )
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_contract_ownership_boundaries() -> None:
    module = _module()

    assert module.verify_phase04_contract_ownership_boundaries() == []


def test_prepared_tool_action_owner_is_distinct_from_agent_security_and_infra() -> None:
    module = _module()

    prepared_owner = module._entry("PreparedToolActionV1").owner_module

    assert prepared_owner == "Tool Runtime"
    assert prepared_owner != module._entry("ActionProposalV1").owner_module
    assert prepared_owner != module._entry("SecurityApprovalDecisionV1").owner_module
    assert prepared_owner != module._entry("AuditPersistenceReceiptV1").owner_module
