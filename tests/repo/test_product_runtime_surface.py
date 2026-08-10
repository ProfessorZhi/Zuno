from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_product_runtime_has_one_canonical_backend_owner() -> None:
    runtime = _read("src/backend/zuno/api/services/product/runtime_engine.py")
    product_api = _read("src/backend/zuno/api/v1/product.py")

    assert "class ProductRuntimeMechanics:" in runtime
    assert "ProductIngestionService" in product_api
    assert "ProductObservabilityService" in product_api
    assert "WorkspaceTaskRuntimeService" not in runtime
    assert "workspace_task_runtime" not in runtime
    assert "import tempfile" not in runtime
    assert "SQLiteAgentRunStore(Path(tempfile.gettempdir())" not in runtime
    assert "/workspace/task" not in product_api


def test_product_api_owns_runtime_and_ingestion_routes() -> None:
    product_api = _read("src/backend/zuno/api/v1/product.py")
    workspace_api = _read("src/backend/zuno/api/v1/workspace.py")

    for route in (
        'router.post("/runtime-requests"',
        'router.post("/files"',
        'router.post("/ingestions"',
        'router.get("/observability/retrieval"',
        'router.get("/artifacts/{artifact_id}"',
    ):
        assert route in product_api
    assert 'router.get("/runtime/{task_id}"' not in product_api
    assert 'router.post("/runtime/{task_id}/approve"' not in product_api

    for route in ("/file", "/ingest", "/task", "/artifact", "/feedback"):
        assert route not in workspace_api


def test_runtime_command_protocol_has_no_cutover_modes() -> None:
    command_service = _read("src/backend/zuno/api/services/product/command_service.py")
    completion_service = _read("src/backend/zuno/api/services/completion.py")
    frontend_runtime = _read("apps/web/src/product/runtime.ts")

    assert 'PRODUCT_RUNTIME_COMMAND_KIND = "SUBMIT_USER_GOAL"' in command_service
    for content in (command_service, completion_service, frontend_runtime):
        assert "cutover_mode" not in content
        assert "SHADOW_SUBMIT_USER_GOAL" not in content
        assert "CANARY_SUBMIT_USER_GOAL" not in content
        assert "rollback_reason" not in content


def test_frontend_ingestion_calls_product_surface() -> None:
    workspace_client = _read("apps/web/src/apis/workspace.ts")

    assert "url: '/api/v1/product/files'" in workspace_client
    assert "url: '/api/v1/product/ingestions'" in workspace_client
    assert "url: '/api/v1/product/observability/retrieval'" in workspace_client
