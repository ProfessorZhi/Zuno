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
    "zuno.capability.execution": [
        "CapabilityRecord",
        "CapabilitySelectionResult",
        "CapabilityType",
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
    from zuno.capability.contracts import CapabilityRecord
    from zuno.capability.registry import CapabilityRegistry
    from zuno.capability.selector import DynamicCapabilitySelector

    assert capability.CapabilityRecord is CapabilityRecord
    assert capability.CapabilityRegistry is CapabilityRegistry
    assert capability.DynamicCapabilitySelector is DynamicCapabilitySelector


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
