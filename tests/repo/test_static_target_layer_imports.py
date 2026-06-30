from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

STATIC_TARGET_SURFACES = [
    "src/backend/zuno/agent/__init__.py",
    "src/backend/zuno/agent/context.py",
    "src/backend/zuno/agent/post_turn.py",
    "src/backend/zuno/agent/runtime.py",
    "src/backend/zuno/agent/state.py",
    "src/backend/zuno/agent/streaming.py",
    "src/backend/zuno/agent/tool_bridge.py",
    "src/backend/zuno/capability/__init__.py",
    "src/backend/zuno/capability/contracts.py",
    "src/backend/zuno/capability/execution.py",
    "src/backend/zuno/capability/policy.py",
    "src/backend/zuno/capability/registry.py",
    "src/backend/zuno/capability/retrieval.py",
    "src/backend/zuno/capability/selector.py",
    "src/backend/zuno/capability/trace.py",
    "src/backend/zuno/knowledge/__init__.py",
    "src/backend/zuno/knowledge/citation.py",
    "src/backend/zuno/knowledge/contracts.py",
    "src/backend/zuno/knowledge/evidence.py",
    "src/backend/zuno/knowledge/fusion/__init__.py",
    "src/backend/zuno/knowledge/graphrag/__init__.py",
    "src/backend/zuno/knowledge/query_service.py",
    "src/backend/zuno/knowledge/retrieval/__init__.py",
    "src/backend/zuno/knowledge/trace.py",
    "src/backend/zuno/memory/__init__.py",
    "src/backend/zuno/memory/contracts.py",
    "src/backend/zuno/memory/engine.py",
    "src/backend/zuno/memory/policy.py",
    "src/backend/zuno/memory/rendering.py",
    "src/backend/zuno/memory/retrieval.py",
    "src/backend/zuno/memory/review.py",
    "src/backend/zuno/memory/store.py",
    "src/backend/zuno/platform/__init__.py",
    "src/backend/zuno/platform/model_gateway.py",
    "src/backend/zuno/platform/observability/__init__.py",
    "src/backend/zuno/platform/security/__init__.py",
    "src/backend/zuno/platform/storage/__init__.py",
]

LEGACY_IMPORT_SNIPPETS = [
    "from zuno.services",
    "import zuno.services",
    "from zuno.core",
    "import zuno.core",
    "from zuno.database",
    "import zuno.database",
    "from zuno.schema",
    "import zuno.schema",
    "from zuno.tools",
    "import zuno.tools",
    "from zuno.utils",
    "import zuno.utils",
    "from zuno.settings",
    "import zuno.settings",
]


def test_first_class_target_surfaces_use_static_physical_imports() -> None:
    violations: list[str] = []

    for relative_path in STATIC_TARGET_SURFACES:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in LEGACY_IMPORT_SNIPPETS:
            if snippet in content:
                violations.append(f"{relative_path}: {snippet}")

    assert violations == []
