from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


EXPECTED_EXPORTS = {
    "zuno.capability.contracts": [
        "CapabilityCost",
        "CapabilityHealth",
        "CapabilityPermissions",
        "CapabilityRecord",
        "CapabilityType",
        "ToolCard",
    ],
    "zuno.capability.control_plane": [
        "ApprovalGate",
        "ExecutorAdapterContract",
        "ExecutorRegistry",
        "MCPTrustContract",
        "NormalizedToolResult",
        "SIDE_EFFECT_RISK_MATRIX",
        "ToolApprovalDecision",
        "ToolApprovalPolicy",
        "ToolCardManifest",
        "ToolExecutionMode",
        "ToolResultNormalizer",
        "ToolSideEffectLevel",
        "ToolTrustTier",
    ],
    "zuno.capability.registry": [
        "CapabilityRecord",
        "CapabilityRegistry",
        "ToolCardRegistry",
    ],
    "zuno.capability.selector": [
        "CapabilitySelectionRequest",
        "CapabilitySelectionResult",
        "CapabilitySelectionTrace",
        "DynamicCapabilitySelector",
    ],
    "zuno.capability.policy": [
        "CapabilityPolicyDecision",
        "CapabilityCost",
        "CapabilityHealth",
        "CapabilityPermissions",
    ],
    "zuno.capability.layer": [
        "CapabilityDecision",
        "CapabilityLayerRegistry",
        "CapabilityRouteDecision",
        "CapabilityRouteRequest",
        "CapabilityRouter",
        "build_default_capability_layer_registry",
    ],
    "zuno.capability.execution": [
        "CapabilityRecord",
        "CapabilitySelectionResult",
        "CapabilityType",
    ],
    "zuno.capability.runtime": [
        "CredentialGrant",
        "InMemoryCredentialBroker",
        "NetworkPolicyDecision",
        "SandboxPolicyEnforcer",
        "ToolControlPlaneRuntime",
        "ToolExecutionContext",
        "ToolRuntimeExecutionResult",
        "ToolRuntimeRequest",
        "ToolSandboxContext",
        "build_default_tool_control_plane_runtime",
    ],
    "zuno.capability.runtime_batch": [
        "CapabilityAvailabilityEntry",
        "CapabilityAvailabilitySnapshot",
        "CapabilityAvailabilityStatus",
        "CapabilityAuditBoundary",
        "CapabilityBoundaryDecision",
        "CapabilityConceptTaxonomy",
        "CapabilityConnectorPolicy",
        "CapabilityConstraintRecord",
        "CapabilityCurrentEvidenceGate",
        "CapabilityDecisionStatus",
        "CapabilityDefinitionRecord",
        "CapabilityEnvelope",
        "CapabilityFallbackVerdict",
        "CapabilityInventoryChange",
        "CapabilityOutboxRecord",
        "CapabilityPersistenceBoundary",
        "CapabilityPinnedVersionSet",
        "CapabilityProviderBindingRecord",
        "CapabilityRecoveryPlan",
        "CapabilityResultValidity",
        "CapabilityReuseVerdict",
        "CapabilityRuntimeBatch",
        "CapabilitySecurityBoundary",
        "CapabilitySelectionRecord",
        "CapabilityTraceEvent",
        "CapabilityTransactionRecord",
        "CapabilityTransitionRecord",
        "CapabilityUnknownContractVerdict",
        "CapabilityVersionRecord",
        "ConnectorPackSplit",
        "ProviderConformanceRecord",
        "ProviderFailureDomain",
        "SkillDiscoveryResult",
        "SkillLoadResult",
        "SkillPolicyVerdict",
        "SkillResourceClassification",
        "SkillVersionRecord",
    ],
    "zuno.capability.tool_runtime": [
        "AdapterFamily",
        "DispatchCertainty",
        "EffectCertainty",
        "EffectLevel",
        "PreparedActionStatus",
        "ReconciliationConclusion",
        "ToolAttemptStatus",
        "ToolRuntimeBatch",
    ],
    "zuno.capability.trace": [
        "CapabilitySelectionTrace",
    ],
    "zuno.capability.retrieval": [
        "NativeBM25Retriever",
        "NativeBM25SearchResult",
        "ToolCard",
        "ToolCardRegistry",
    ],
}


def test_capability_layer_modules_expose_target_boundaries() -> None:
    for module_name, expected_exports in EXPECTED_EXPORTS.items():
        module = importlib.import_module(module_name)
        assert module.__all__ == expected_exports


def test_capability_layer_modules_reuse_legacy_foundation_objects() -> None:
    from zuno.capability.contracts import CapabilityRecord, CapabilityType
    from zuno.capability.registry import CapabilityRegistry, ToolCardRegistry
    from zuno.capability.retrieval import NativeBM25Retriever, ToolCard
    from zuno.capability.selector import DynamicCapabilitySelector
    from zuno.capability.trace import CapabilitySelectionTrace
    from zuno.services.application import capabilities as legacy

    assert CapabilityRecord is legacy.CapabilityRecord
    assert CapabilityType is legacy.CapabilityType
    assert ToolCard is legacy.ToolCard
    assert CapabilityRegistry is legacy.CapabilityRegistry
    assert ToolCardRegistry is legacy.ToolCardRegistry
    assert NativeBM25Retriever is legacy.NativeBM25Retriever
    assert DynamicCapabilitySelector is legacy.DynamicCapabilitySelector
    assert CapabilitySelectionTrace is legacy.CapabilitySelectionTrace


def test_capability_package_facade_points_at_layer_modules() -> None:
    import zuno.capability as capability
    from zuno.capability.control_plane import ToolCardManifest
    from zuno.capability.contracts import CapabilityRecord
    from zuno.capability.layer import CapabilityRouter
    from zuno.capability.registry import CapabilityRegistry
    from zuno.capability.runtime import ToolControlPlaneRuntime
    from zuno.capability.runtime_batch import CapabilityRuntimeBatch
    from zuno.capability.selector import DynamicCapabilitySelector
    from zuno.capability.tool_runtime import ToolRuntimeBatch

    assert capability.CapabilityRecord is CapabilityRecord
    assert capability.CapabilityRegistry is CapabilityRegistry
    assert capability.CapabilityRouter is CapabilityRouter
    assert capability.DynamicCapabilitySelector is DynamicCapabilitySelector
    assert capability.ToolCardManifest is ToolCardManifest
    assert capability.ToolControlPlaneRuntime is ToolControlPlaneRuntime
    assert capability.CapabilityRuntimeBatch is CapabilityRuntimeBatch
    assert capability.ToolRuntimeBatch is ToolRuntimeBatch


def test_importing_capability_surfaces_does_not_load_heavy_runtime_modules() -> None:
    code = """
import importlib
import json
import sys

sys.path.insert(0, r"__BACKEND_PATH__")

for name in __MODULES__:
    importlib.import_module(name)

prefixes = [
    "zuno.database",
    "zuno.api.services",
    "zuno.services.rag.vector_db",
]
print(json.dumps({
    prefix: sorted(name for name in sys.modules if name == prefix or name.startswith(prefix + "."))
    for prefix in prefixes
}, sort_keys=True))
"""
    env = dict(os.environ)
    backend_path = str(REPO_ROOT / "src" / "backend")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        backend_path
        if not existing_pythonpath
        else os.pathsep.join([backend_path, existing_pythonpath])
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            code.replace("__BACKEND_PATH__", backend_path).replace(
                "__MODULES__", repr(sorted(EXPECTED_EXPORTS))
            ),
        ],
        check=True,
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        text=True,
    )

    loaded_modules = json.loads(result.stdout)
    assert loaded_modules == {prefix: [] for prefix in loaded_modules}
