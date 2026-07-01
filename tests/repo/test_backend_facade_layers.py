from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


FACADE_ALL = {
    "zuno.api": ["Settings", "router"],
    "zuno.agent": [
        "AgentConfig",
        "AgentControlRuntime",
        "AgentRuntimeResult",
        "AgentExecutionContext",
        "ContextOrchestrator",
        "ContextPackPolicy",
        "ContextTrace",
        "ControllerRuntimeState",
        "DurableRuntimeEvent",
        "DurableRuntimeTaskSnapshot",
        "GeneralAgent",
        "InMemoryDurableRuntimeStore",
        "ModelContextPacket",
        "PlanningRequest",
        "RuntimeCheckpoint",
        "RuntimeInterrupt",
        "RuntimeNodeContract",
        "RuntimeObservation",
        "RuntimeTurnLedger",
        "SingleControllerRuntimeHarness",
        "SingleControllerDurableRuntime",
        "StrategySelector",
        "StreamAgentState",
        "build_default_strategy_selector",
        "build_single_controller_runtime_harness",
    ],
    "zuno.memory": [
        "DatabaseMemoryStore",
        "DurableMemoryStore",
        "ExternalKnowledgeRecord",
        "InMemoryLayerStore",
        "MemoryCandidate",
        "MemoryEngine",
        "MemoryGovernanceLedgerEntry",
        "MemoryLayer",
        "MemoryProcessingPolicy",
        "MemoryReviewDecision",
        "MemoryReviewStatus",
        "MemoryScope",
        "RawMemoryEvent",
        "RetentionPolicy",
        "MemoryStoreSnapshot",
        "TaskMemorySummary",
    ],
    "zuno.capability": [
        "ApprovalGate",
        "CapabilityCost",
        "CapabilityHealth",
        "CapabilityPermissions",
        "CapabilityRecord",
        "CapabilityRegistry",
        "CapabilityDecision",
        "CapabilityLayerRegistry",
        "CapabilityRouteDecision",
        "CapabilityRouteRequest",
        "CapabilityRouter",
        "CapabilitySelectionRequest",
        "CapabilitySelectionResult",
        "CapabilitySelectionTrace",
        "CapabilityType",
        "CredentialGrant",
        "DynamicCapabilitySelector",
        "ExecutorAdapterContract",
        "ExecutorRegistry",
        "InMemoryCredentialBroker",
        "MCPTrustContract",
        "NativeBM25Retriever",
        "NativeBM25SearchResult",
        "NormalizedToolResult",
        "SandboxPolicyEnforcer",
        "ToolApprovalDecision",
        "ToolApprovalPolicy",
        "ToolCard",
        "ToolCardManifest",
        "ToolCardRegistry",
        "ToolControlPlaneRuntime",
        "ToolExecutionMode",
        "ToolExecutionContext",
        "ToolResultNormalizer",
        "ToolRuntimeExecutionResult",
        "ToolRuntimeRequest",
        "ToolSandboxContext",
        "ToolSideEffectLevel",
        "ToolTrustTier",
        "build_default_capability_layer_registry",
        "build_default_tool_control_plane_runtime",
    ],
    "zuno.knowledge": [
        "AgenticGraphRAGTrace",
        "AgenticRetrievalRuntime",
        "AgenticRetrievalRuntimeRequest",
        "AgenticRetrievalRuntimeResult",
        "AgenticRetrievalRouter",
        "Citation",
        "CitationBuilder",
        "EvidenceBundle",
        "EvidenceItem",
        "EvidenceChecker",
        "EvidenceVerdict",
        "FusionStage",
        "FusionResult",
        "GraphRAGIndexPipelineContract",
        "GraphRAGExtractorConfig",
        "GraphRAGProjectContract",
        "GraphRAGProjectLoader",
        "GraphRAGProjectSnapshot",
        "GraphRAGQueryService",
        "GraphRAGSettingsValidator",
        "HookPoint",
        "IndexJobManifest",
        "IndexQueryResult",
        "KnowledgeQueryResult",
        "KnowledgeQueryService",
        "KnowledgeIndexRuntime",
        "KnowledgeSpaceManifest",
        "LoadedGraphRAGProject",
        "ProductMode",
        "ProcessedQuery",
        "ProjectReadiness",
        "QueryMethod",
        "RetrievalFusion",
        "RetrievalOrchestrator",
        "RetrievalPlan",
        "RetrievalPlanner",
        "RetrievalRequest",
        "RetrievalRouterDecision",
        "RetrievalRouterInput",
        "RetrievedDocument",
        "RuntimeTraceBuilder",
        "RuntimeTraceEvent",
        "StagedFusionPlan",
        "TraceArtifactManifest",
        "UnsupportedClaimCheck",
        "UnsupportedClaimChecker",
        "enrich_trace_metadata_with_artifacts",
        "normalize_retrieval_mode",
    ],
    "zuno.platform": [
        "ACCESS_SCOPE_DEFINITIONS",
        "EXECUTION_MODE_DEFINITIONS",
        "AccessScope",
        "BudgetPolicy",
        "BudgetVerdict",
        "EchoLLMProvider",
        "ExecutionMode",
        "EvalDatasetCase",
        "EvalMetricResult",
        "GateRequest",
        "GateResult",
        "InputSecurityGate",
        "LLMProvider",
        "LazyStorageClient",
        "LangSmithExportAdapter",
        "MinioClient",
        "MetricThreshold",
        "MockModelProvider",
        "ModelCallMetrics",
        "ModelCategory",
        "ModelGateway",
        "ModelGatewayProviderError",
        "ModelGatewayRequest",
        "ModelGatewayResult",
        "ModelGatewayTimeoutError",
        "OSSClient",
        "OutputSecurityGate",
        "RedisKeys",
        "ReleaseEvalBaseline",
        "ReleaseEvalBaselineResult",
        "RetrievalCandidate",
        "RetrievalGateResult",
        "RetrievalSecurityGate",
        "SandboxAuditEvent",
        "SandboxProfile",
        "SecurityDecision",
        "SecurityFinding",
        "SecurityGate",
        "ToolGateResult",
        "ToolSecurityGate",
        "ToolSecurityProfile",
        "ZunoSpan",
        "ZunoSpanBuilder",
        "ZunoSpanKind",
        "annotate_tool_execution_metadata",
        "build_default_model_gateway",
        "build_langchain_run_config",
        "build_langsmith_metadata",
        "configure_langsmith",
        "filter_tools_for_mode",
        "get_active_trace_id",
        "get_execution_config_payload",
        "get_tool_runtime_type",
        "normalize_access_scope",
        "normalize_execution_mode",
        "redact_sensitive_payload",
        "redact_sensitive_text",
        "storage_client",
        "validate_tools_for_mode",
    ],
}

SELECTED_EXPORTS = {
    "zuno.api": {"Settings": "zuno.api.JWT"},
    "zuno.agent": {},
    "zuno.memory": {},
    "zuno.capability": {
        "ToolCardManifest": "zuno.capability.control_plane",
        "CapabilityRecord": "zuno.services.application.capabilities",
        "CapabilityRegistry": "zuno.services.application.capabilities",
        "DynamicCapabilitySelector": "zuno.services.application.capabilities",
        "ToolCard": "zuno.services.application.capabilities",
        "ToolCardRegistry": "zuno.services.application.capabilities",
    },
    "zuno.knowledge": {
        "GraphRAGExtractorConfig": "zuno.services.graphrag.models",
        "GraphRAGProjectContract": "zuno.services.graphrag.models",
        "GraphRAGProjectLoader": "zuno.services.graphrag.project",
        "normalize_retrieval_mode": "zuno.services.graphrag.models",
    },
    "zuno.platform": {
        "AccessScope": "zuno.services.execution_policy",
        "ExecutionMode": "zuno.services.execution_policy",
        "SecurityGate": "zuno.platform.security",
        "ZunoSpanBuilder": "zuno.platform.observability",
        "normalize_execution_mode": "zuno.services.execution_policy",
    },
}

OLD_IMPORT_PATHS = [
    "zuno.api",
    "zuno.core.agents",
    "zuno.services.application.capabilities",
    "zuno.services.graphrag.models",
    "zuno.services.graphrag.project",
    "zuno.services.execution_policy",
]

HEAVY_MODULE_PREFIXES = [
    "zuno.database",
    "zuno.api.services",
    "zuno.services.rag.vector_db",
]


def test_backend_facade_packages_exist_as_current_import_surfaces() -> None:
    for module_name in FACADE_ALL:
        relative_path = Path("src/backend") / Path(*module_name.split(".")) / "__init__.py"
        assert (REPO_ROOT / relative_path).exists(), f"missing facade package: {module_name}"


def test_backend_facade_all_is_exact_and_stable() -> None:
    for module_name, expected_exports in FACADE_ALL.items():
        facade_module = importlib.import_module(module_name)
        assert facade_module.__all__ == expected_exports


def test_selected_backend_facade_exports_match_legacy_objects() -> None:
    for module_name, exports in SELECTED_EXPORTS.items():
        facade_module = importlib.import_module(module_name)

        for exported_name, legacy_module_name in exports.items():
            legacy_module = importlib.import_module(legacy_module_name)
            assert exported_name in facade_module.__all__
            assert getattr(facade_module, exported_name) is getattr(legacy_module, exported_name)


def test_old_lightweight_import_paths_still_import() -> None:
    for module_name in OLD_IMPORT_PATHS:
        module = importlib.import_module(module_name)
        assert sys.modules[module_name] is module


def test_importing_facades_in_fresh_process_does_not_load_heavy_runtime_modules() -> None:
    code = """
import importlib
import json
import sys

sys.path.insert(0, r"__BACKEND_PATH__")

for name in [
    "zuno.api",
    "zuno.agent",
    "zuno.memory",
    "zuno.capability",
    "zuno.knowledge",
    "zuno.platform",
]:
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
""".replace("__BACKEND_PATH__", str(REPO_ROOT / "src" / "backend"))
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH")
    backend_path = str(REPO_ROOT / "src" / "backend")
    env["PYTHONPATH"] = (
        backend_path
        if not existing_pythonpath
        else os.pathsep.join([backend_path, existing_pythonpath])
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        text=True,
    )

    loaded_modules = json.loads(result.stdout)
    assert loaded_modules == {prefix: [] for prefix in HEAVY_MODULE_PREFIXES}
