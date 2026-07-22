from __future__ import annotations

from pathlib import Path
import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.api.v1.workspace import router as workspace_router
from zuno.platform.security import SecurityProductActionDenied


class RecordingProductActionGuard:
    def __init__(self, *, deny_action: str | None = None) -> None:
        self.deny_action = deny_action
        self.requests = []

    def require_authorized_action(self, request) -> None:
        self.requests.append(request)
        if request.action == self.deny_action:
            raise SecurityProductActionDenied("product action denied by Security")


def _client() -> TestClient:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    app = FastAPI()
    app.include_router(workspace_router, prefix="/api/v1")
    app.dependency_overrides[get_login_user] = lambda: UserPayload(
        user_id="user_phase11",
        user_name="Phase11 User",
        role="admin",
    )
    return TestClient(app)


def _seed_index(client: TestClient, *, workspace_id: str, knowledge_space_id: str) -> None:
    file_response = client.post(
        "/api/v1/workspace/file",
        json={
            "workspace_id": workspace_id,
            "file_id": f"file_{knowledge_space_id}",
            "name": "renewal-contract.md",
            "mime_type": "text/markdown",
            "content": "Renewal notice must be sent 30 days before the contract anniversary.",
        },
    )
    assert file_response.status_code == 200

    ingest_response = client.post(
        "/api/v1/workspace/ingest",
        json={
            "workspace_id": workspace_id,
            "file_id": f"file_{knowledge_space_id}",
            "knowledge_space_id": knowledge_space_id,
        },
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["data"]["file_status"]["index_status"] == "indexed"


def test_workspace_product_schema_serializes_config_and_rejects_internal_profiles() -> None:
    from zuno.schema.workspace import (
        ChangeImpactPreview,
        KnowledgeSpaceConfig,
        WorkSpaceSimpleTask,
    )

    config = KnowledgeSpaceConfig(
        name="Contracts",
        description="Supplier contracts",
        workspace_id="workspace_phase11",
        index_capabilities={
            "basic_index": {"enabled": True, "targets": ["bm25", "vector", "citation_lineage"]},
            "graph_index": {"enabled": True, "targets": ["entity", "relation", "community"]},
            "ocr_vlm": {"enabled": False, "status": "target_blocked"},
        },
        retrieval_defaults={"default_profile": "deep", "available_profiles": ["standard", "deep"]},
    )
    dumped = config.model_dump(mode="json")
    assert dumped["retrieval_defaults"]["available_profiles"] == ["standard", "deep"]
    assert "basic" not in dumped["retrieval_defaults"]["available_profiles"]
    assert "local" not in dumped["retrieval_defaults"]["available_profiles"]
    assert "global" not in dumped["retrieval_defaults"]["available_profiles"]
    assert "drift" not in dumped["retrieval_defaults"]["available_profiles"]

    preview = ChangeImpactPreview(
        change_type="enable_graph",
        triggered_action="graph rebuild",
        affected_file_count=3,
        affected_chunk_count=18,
        requires_external_provider=False,
        may_create_blocked_state=False,
    ).model_dump(mode="json")
    assert preview["triggered_action"] == "graph rebuild"
    assert preview["affected_chunk_count"] == 18

    with pytest.raises(ValidationError):
        WorkSpaceSimpleTask(
            query="Should not expose internal GraphRAG methods",
            model_id="model-local",
            session_id="session_phase11_schema",
            workspace_id="workspace_phase11",
            knowledge_space_profiles=[
                {"knowledge_space_id": "ks_contracts", "retrieval_profile": "local"}
            ],
            plugins=[],
            mcp_servers=[],
        )


def test_workspace_task_uses_per_space_profile_and_returns_agentic_summaries() -> None:
    client = _client()
    _seed_index(client, workspace_id="workspace_phase11", knowledge_space_id="ks_phase11_contracts")

    create_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "What is the renewal notice requirement?",
            "model_id": "model-local",
            "session_id": "session_phase11",
            "workspace_id": "workspace_phase11",
            "task_id": "task_phase11_profile",
            "trace_id": "trace_phase11_profile",
            "goal": "cited renewal answer",
            "product_mode": "contract_review",
            "knowledge_space_ids": ["ks_phase11_contracts"],
            "knowledge_space_profiles": [
                {"knowledge_space_id": "ks_phase11_contracts", "retrieval_profile": "deep"}
            ],
            "uploaded_file_ids": ["file_ks_phase11_contracts"],
            "plugins": [],
            "mcp_servers": [],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["data"]
    assert created["retrieval_plan"]["retrieval_profiles"] == {"ks_phase11_contracts": "deep"}
    assert created["retrieval_plan"]["requested_profile"] == "deep"
    assert created["retrieval_plan"]["effective_profile"] in {"deep", "deep_without_graph"}
    assert created["plan_summary"]["strategy"] in {
        "direct_answer",
        "plan_execute",
        "plan_execute_with_replan",
        "reflection_enabled",
    }
    assert created["plan_summary"]["selected_skill"] == "contract_review"
    assert created["reflection_summary"]["decision"] in {"continue", "finish", "replan"}
    assert created["trace_summary"]["trace_id"] == "trace_phase11_profile"
    assert created["trace_summary"]["event_count"] >= 7
    assert created["eval_summary"]["release_eval_status"] == "pass"
    assert created["cost_summary"]["estimated_cost"] >= 0
    assert created["capability_snapshot"]["selected_skill"] == "contract_review"

    snapshot = client.get("/api/v1/workspace/task/task_phase11_profile").json()["data"]
    assert snapshot["retrieval_plan"]["retrieval_profiles"] == {"ks_phase11_contracts": "deep"}
    assert snapshot["trace_summary"]["trace_id"] == "trace_phase11_profile"


def test_workspace_artifact_response_includes_citation_refs() -> None:
    client = _client()
    _seed_index(client, workspace_id="workspace_phase11_artifact", knowledge_space_id="ks_phase11_artifact")

    created = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "What is the renewal notice requirement?",
            "model_id": "model-local",
            "session_id": "session_phase11_artifact",
            "workspace_id": "workspace_phase11_artifact",
            "task_id": "task_phase11_artifact",
            "trace_id": "trace_phase11_artifact",
            "goal": "artifact citation answer",
            "product_mode": "contract_review",
            "knowledge_space_ids": ["ks_phase11_artifact"],
            "retrieval_profiles": {"ks_phase11_artifact": "standard"},
            "uploaded_file_ids": ["file_ks_phase11_artifact"],
            "plugins": [],
            "mcp_servers": [],
        },
    ).json()["data"]
    artifact_id = created["artifact_ids"][0]

    artifact_response = client.get(f"/api/v1/workspace/artifact/{artifact_id}")
    assert artifact_response.status_code == 200
    payload = artifact_response.json()["data"]
    citation_refs = payload["citation_refs"]
    assert citation_refs
    assert citation_refs[0]["citation_id"] == "[1]"
    assert citation_refs[0]["document_id"] == "file_ks_phase11_artifact"
    assert citation_refs[0]["source_ref"].startswith("file_ks_phase11_artifact::")
    assert payload["artifact"]["citation_refs"] == citation_refs


def test_workspace_artifact_citation_refs_reauthorize_through_security_guard() -> None:
    client = _client()
    _seed_index(client, workspace_id="workspace_phase05_citation", knowledge_space_id="ks_phase05_citation")

    created = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "What is the renewal notice requirement?",
            "model_id": "model-local",
            "session_id": "session_phase05_citation",
            "workspace_id": "workspace_phase05_citation",
            "task_id": "task_phase05_citation",
            "trace_id": "trace_phase05_citation",
            "goal": "citation reauthorization answer",
            "product_mode": "contract_review",
            "knowledge_space_ids": ["ks_phase05_citation"],
            "retrieval_profiles": {"ks_phase05_citation": "standard"},
            "uploaded_file_ids": ["file_ks_phase05_citation"],
            "plugins": [],
            "mcp_servers": [],
        },
    ).json()["data"]
    artifact_id = created["artifact_ids"][0]
    guard = RecordingProductActionGuard()
    WorkspaceTaskRuntimeService.configure_security_product_action_guard(guard)

    try:
        artifact_response = client.get(f"/api/v1/workspace/artifact/{artifact_id}")
    finally:
        WorkspaceTaskRuntimeService.configure_security_product_action_guard(None)

    assert artifact_response.status_code == 200
    assert [request.action for request in guard.requests] == ["artifact.read", "citation.read"]
    assert guard.requests[1].principal_id == "user_phase11"
    assert guard.requests[1].resource_ref == f"workspace-artifact:{artifact_id}:citations"


def test_workspace_task_snapshot_citation_refs_return_403_when_security_guard_denies() -> None:
    client = _client()
    _seed_index(client, workspace_id="workspace_phase05_citation_deny", knowledge_space_id="ks_phase05_citation_deny")

    created = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "What is the renewal notice requirement?",
            "model_id": "model-local",
            "session_id": "session_phase05_citation_deny",
            "workspace_id": "workspace_phase05_citation_deny",
            "task_id": "task_phase05_citation_deny",
            "trace_id": "trace_phase05_citation_deny",
            "goal": "denied citation reauthorization answer",
            "product_mode": "contract_review",
            "knowledge_space_ids": ["ks_phase05_citation_deny"],
            "retrieval_profiles": {"ks_phase05_citation_deny": "standard"},
            "uploaded_file_ids": ["file_ks_phase05_citation_deny"],
            "plugins": [],
            "mcp_servers": [],
        },
    ).json()["data"]
    task_id = created["task"]["task_id"]
    guard = RecordingProductActionGuard(deny_action="citation.read")
    WorkspaceTaskRuntimeService.configure_security_product_action_guard(guard)

    try:
        task_response = client.get(f"/api/v1/workspace/task/{task_id}")
    finally:
        WorkspaceTaskRuntimeService.configure_security_product_action_guard(None)

    assert task_response.status_code == 403
    assert task_response.json()["detail"] == "product action denied by Security"
    assert [request.action for request in guard.requests] == ["citation.read"]


def test_frontend_workspace_api_types_expose_product_contract_without_internal_user_modes() -> None:
    source = (Path(__file__).resolve().parents[2] / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    profile_match = re.search(r"export type WorkspaceRetrievalProfile\s*=\s*([^\n]+)", source)
    assert profile_match is not None
    profile_definition = profile_match.group(1)
    assert "'standard'" in profile_definition
    assert "'deep'" in profile_definition
    for internal_mode in ("'basic'", "'local'", "'global'", "'drift'"):
        assert internal_mode not in profile_definition

    assert "KnowledgeSpaceConfig" in source
    assert "KnowledgeSpaceRetrievalSelection" in source
    assert "WorkspaceFileStatus" in source
    assert "ChangeImpactPreview" in source
    assert "knowledge_space_profiles?: KnowledgeSpaceRetrievalSelection[]" in source
    assert "retrieval_profiles?: Record<string, WorkspaceRetrievalProfile>" in source
    assert "citation_refs: WorkspaceCitationRef[]" in source


def test_frontend_agentchat_sends_explicit_product_profiles_from_selected_knowledge() -> None:
    root = Path(__file__).resolve().parents[2]
    workspace_page = (root / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(
        encoding="utf-8"
    )
    create_page = (root / "apps/web/src/pages/knowledge/knowledge-create.vue").read_text(
        encoding="utf-8"
    )
    config_utils = (root / "apps/web/src/utils/knowledge-config.ts").read_text(encoding="utf-8")

    assert "toWorkspaceRetrievalProfile" in config_utils
    assert "buildKnowledgeSpaceProfileSelections" in workspace_page
    assert "knowledge_space_ids:" in workspace_page
    assert "knowledge_space_profiles:" in workspace_page
    assert "retrieval_profiles:" in workspace_page
    assert "KnowledgeProductMode = 'standard' | 'deep'" in config_utils
    assert "value: 'enhanced'" not in create_page
