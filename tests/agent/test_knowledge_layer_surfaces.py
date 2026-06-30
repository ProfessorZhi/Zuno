from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


EXPECTED_EXPORTS = {
    "zuno.knowledge.agentic_graphrag": [
        "AgenticGraphRAGTrace",
        "AgenticRetrievalRouter",
        "Citation",
        "CitationBuilder",
        "EvidenceBundle",
        "EvidenceItem",
        "FusionStage",
        "GraphRAGIndexPipelineContract",
        "ProductMode",
        "QueryMethod",
        "RetrievalRouterDecision",
        "RetrievalRouterInput",
        "StagedFusionPlan",
        "UnsupportedClaimCheck",
        "UnsupportedClaimChecker",
    ],
    "zuno.knowledge.contracts": [
        "GraphRAGProjectContract",
        "GraphRAGExtractorConfig",
        "GraphRAGProjectLoader",
        "GraphRAGSettingsValidator",
        "LoadedGraphRAGProject",
        "ProjectReadiness",
        "normalize_retrieval_mode",
    ],
    "zuno.knowledge.query_service": [
        "GraphRAGProjectSnapshot",
        "GraphRAGQueryService",
        "KnowledgeQueryResult",
        "KnowledgeQueryService",
    ],
    "zuno.knowledge.evidence": [
        "FusionResult",
        "KnowledgeQueryResult",
        "RetrievedDocument",
    ],
    "zuno.knowledge.citation": [
        "KnowledgeQueryResult",
        "RetrievedDocument",
    ],
    "zuno.knowledge.trace": [
        "EvidenceChecker",
        "EvidenceVerdict",
        "GraphRAGProjectSnapshot",
        "HookPoint",
        "KnowledgeQueryResult",
        "ProcessedQuery",
        "RetrievalPlan",
        "RuntimeTraceBuilder",
        "RuntimeTraceEvent",
        "TraceArtifactManifest",
        "enrich_trace_metadata_with_artifacts",
    ],
    "zuno.knowledge.retrieval": [
        "ProcessedQuery",
        "PRODUCT_MODES",
        "QUERY_METHODS",
        "QUERY_METHOD_ROUTER",
        "RetrievalOrchestrator",
        "RetrievalPlan",
        "RetrievalPlanner",
        "RetrievalRequest",
        "RetrievedDocument",
        "normalize_product_mode",
    ],
    "zuno.knowledge.fusion": [
        "FusionResult",
        "RetrievalFusion",
        "RetrievedDocument",
    ],
    "zuno.knowledge.graphrag": [
        "GraphRAGExtractorConfig",
        "GraphRAGProjectContract",
        "GraphRAGProjectLoader",
        "GraphRAGProjectSnapshot",
        "GraphRAGQueryService",
        "GraphRAGSettingsValidator",
        "LoadedGraphRAGProject",
        "ProjectReadiness",
        "normalize_retrieval_mode",
    ],
}


def test_knowledge_layer_modules_expose_target_boundaries() -> None:
    for module_name, expected_exports in EXPECTED_EXPORTS.items():
        module = importlib.import_module(module_name)
        assert module.__all__ == expected_exports


def test_knowledge_layer_modules_reuse_legacy_foundation_objects() -> None:
    from zuno.knowledge.contracts import GraphRAGExtractorConfig, GraphRAGProjectContract
    from zuno.knowledge.fusion import RetrievalFusion
    from zuno.knowledge.query_service import KnowledgeQueryService
    from zuno.knowledge.retrieval import RetrievalPlanner
    from zuno.services.application.knowledge import KnowledgeQueryService as LegacyKnowledgeQueryService
    from zuno.services.graphrag.models import GraphRAGExtractorConfig as LegacyExtractorConfig
    from zuno.services.graphrag.models import GraphRAGProjectContract as LegacyContract
    from zuno.services.retrieval.fusion import RetrievalFusion as LegacyFusion
    from zuno.services.retrieval.planner import RetrievalPlanner as LegacyPlanner

    assert GraphRAGProjectContract is LegacyContract
    assert GraphRAGExtractorConfig is LegacyExtractorConfig
    assert KnowledgeQueryService is LegacyKnowledgeQueryService
    assert RetrievalFusion is LegacyFusion
    assert RetrievalPlanner is LegacyPlanner


def test_knowledge_package_facade_points_at_layer_modules() -> None:
    import zuno.knowledge as knowledge
    from zuno.knowledge.agentic_graphrag import AgenticRetrievalRouter, ProductMode
    from zuno.knowledge.contracts import GraphRAGExtractorConfig, GraphRAGProjectContract
    from zuno.knowledge.query_service import KnowledgeQueryService
    from zuno.knowledge.retrieval import RetrievalPlanner

    assert knowledge.AgenticRetrievalRouter is AgenticRetrievalRouter
    assert knowledge.ProductMode is ProductMode
    assert knowledge.GraphRAGProjectContract is GraphRAGProjectContract
    assert knowledge.GraphRAGExtractorConfig is GraphRAGExtractorConfig
    assert knowledge.KnowledgeQueryService is KnowledgeQueryService
    assert knowledge.RetrievalPlanner is RetrievalPlanner


def test_importing_knowledge_surfaces_does_not_load_heavy_runtime_modules() -> None:
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
    "zuno.services.rag.handler",
    "zuno.services.retrieval.retrievers",
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
