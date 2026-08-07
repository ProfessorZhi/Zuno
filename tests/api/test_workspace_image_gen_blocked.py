"""PHASE22 runtime cutover: image generation must not bypass the gateway.

The workspace product surface must fail closed with
``IMAGE_TOOL_RUNTIME_NOT_BOUND`` before any ``_text_to_image`` call can
resolve. The dev-test-profile entry point that called
``_text_to_image`` directly is deleted in this slice.
"""

from __future__ import annotations

import re


def test_workspace_product_surface_has_no_text_to_image_import() -> None:
    import ast

    tree = ast.parse(
        open(
            "src/backend/zuno/api/services/workspace.py", encoding="utf-8"
        ).read()
    )
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.append(f"{node.module}.{alias.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.append(alias.name)
    assert not any("_text_to_image" in name for name in imported), (
        "Workspace product surface must not import _text_to_image; the "
        "only image path goes through ToolInvocationGateway as a "
        "registered executor adapter. Imports: " + str(imported)
    )


def test_workspace_product_surface_blocks_image_generation() -> None:
    src = open(
        "src/backend/zuno/api/services/workspace.py", encoding="utf-8"
    ).read()
    assert "IMAGE_TOOL_RUNTIME_NOT_BOUND" in src
    assert re.search(r"if\s+cls\.should_run_direct_image_generation", src)


def test_build_direct_image_response_is_deleted() -> None:
    import ast

    tree = ast.parse(
        open(
            "src/backend/zuno/api/services/workspace.py", encoding="utf-8"
        ).read()
    )
    defined = {
        node.name
        for node in ast.walk(tree)
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        )
    }
    assert "build_direct_image_response" not in defined, (
        "build_direct_image_response was the dev-test-profile-only "
        "direct _text_to_image caller; it must be removed in this slice."
    )