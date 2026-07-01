from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


EXPECTED_EXPORTS = {
    "zuno.platform.security": [
        "AccessScope",
        "ExecutionMode",
        "GateRequest",
        "GateResult",
        "InputSecurityGate",
        "OutputSecurityGate",
        "RetrievalCandidate",
        "RetrievalGateResult",
        "RetrievalSecurityGate",
        "SandboxAuditEvent",
        "SandboxProfile",
        "SecurityDecision",
        "SecurityFinding",
        "SecurityGate",
        "SecurityTraceSummary",
        "ToolGateResult",
        "ToolSecurityGate",
        "ToolSecurityProfile",
        "build_security_trace_summary",
        "normalize_access_scope",
        "normalize_execution_mode",
        "redact_sensitive_payload",
        "redact_sensitive_text",
        "validate_tools_for_mode",
    ],
    "zuno.platform.security.governance": [
        "GateRequest",
        "GateResult",
        "InputSecurityGate",
        "OutputSecurityGate",
        "RetrievalCandidate",
        "RetrievalGateResult",
        "RetrievalSecurityGate",
        "SandboxAuditEvent",
        "SandboxProfile",
        "SecurityDecision",
        "SecurityFinding",
        "SecurityGate",
        "SecurityTraceSummary",
        "ToolGateResult",
        "ToolSecurityGate",
        "ToolSecurityProfile",
        "build_security_trace_summary",
        "redact_sensitive_payload",
        "redact_sensitive_text",
    ],
    "zuno.platform.observability": [
        "EvalDatasetCase",
        "EvalMetricResult",
        "LangSmithExportAdapter",
        "MetricThreshold",
        "RedisKeys",
        "ReleaseEvalBaseline",
        "ReleaseEvalBaselineResult",
        "ZunoSpan",
        "ZunoSpanBuilder",
        "ZunoSpanKind",
        "build_langchain_run_config",
        "build_langsmith_metadata",
        "configure_langsmith",
        "get_active_trace_id",
    ],
    "zuno.platform.observability.trace_eval": [
        "EvalDatasetCase",
        "EvalMetricResult",
        "LangSmithExportAdapter",
        "MetricThreshold",
        "ReleaseEvalBaseline",
        "ReleaseEvalBaselineResult",
        "ZunoSpan",
        "ZunoSpanBuilder",
        "ZunoSpanKind",
    ],
    "zuno.platform.storage": [
        "LazyStorageClient",
        "MinioClient",
        "OSSClient",
        "storage_client",
    ],
    "zuno.platform.model_gateway": [
        "EchoLLMProvider",
        "LLMProvider",
    ],
}


def test_platform_layer_modules_expose_target_boundaries() -> None:
    for module_name, expected_exports in EXPECTED_EXPORTS.items():
        module = importlib.import_module(module_name)
        assert module.__all__ == expected_exports


def test_platform_layer_modules_reuse_legacy_foundation_objects() -> None:
    from zuno.platform.model_gateway import LLMProvider
    from zuno.platform.observability import get_active_trace_id
    from zuno.platform.security import AccessScope
    from zuno.platform.storage import storage_client
    from zuno.services.execution_policy import AccessScope as LegacyAccessScope
    from zuno.services.llm.providers import LLMProvider as LegacyLLMProvider
    from zuno.services.storage import storage_client as LegacyStorageClient
    from zuno.utils.runtime_observability import get_active_trace_id as LegacyTraceId

    assert AccessScope is LegacyAccessScope
    assert get_active_trace_id is LegacyTraceId
    assert storage_client is LegacyStorageClient
    assert LLMProvider is LegacyLLMProvider


def test_platform_package_facade_points_at_target_modules() -> None:
    import zuno.platform as platform
    from zuno.platform.model_gateway import LLMProvider
    from zuno.platform.observability import ZunoSpanBuilder
    from zuno.platform.security import AccessScope, SecurityGate

    assert platform.AccessScope is AccessScope
    assert platform.SecurityGate is SecurityGate
    assert platform.LLMProvider is LLMProvider
    assert platform.ZunoSpanBuilder is ZunoSpanBuilder


def test_importing_platform_surfaces_does_not_load_database_or_vector_runtime() -> None:
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
