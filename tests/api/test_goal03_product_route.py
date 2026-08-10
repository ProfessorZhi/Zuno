from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.router import router as api_router
from zuno.api.services import user as user_service
from zuno.api.services.product import (
    ProductActionConsumeResult,
    ProductAgentCatalogEntryResult,
    ProductAgentDefinitionResult,
    ProductAgentDraftResult,
    ProductAgentEditorSnapshotResult,
    ProductAgentInstallationResult,
    ProductAgentPublicationResult,
    ProductAgentVersionResult,
    ProductAvailableActionResult,
    ProductProjectionResult,
    ProductRuntimeRequestResult,
    ProductService,
    ProductStreamEventResult,
)


class _LoginUser:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


def test_goal03_product_runtime_request_route_is_exposed_and_returns_receipt(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    monkeypatch.setattr(
        ProductService,
        "submit_runtime_request",
        staticmethod(
            lambda **kwargs: ProductRuntimeRequestResult(
                command_id="command:client:1",
                receipt_id="command:client:1:receipt:1",
                status="ACCEPTED",
                projection=ProductProjectionResult(
                    projection_event_id="projection:command:client:1:accepted",
                    stream_cursor_id="cursor:command:client:1:1",
                    stream_sequence_no=1,
                    freshness="current",
                    redaction_decision_ref="redaction:command:client:1:server",
                ),
                available_actions=(
                    ProductAvailableActionResult(
                        action="CANCEL",
                        action_token_id="action-token:command:client:1:cancel",
                        target_ref="runtime-request:1",
                        effective_security_epoch_ref="security-epoch:product:default",
                        projection_version=1,
                        expires_at="2026-07-26T00:00:00+00:00",
                    ),
                ),
            )
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/product/runtime-requests",
        json={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "conversation_id": "conversation-a",
            "client_request_id": "client:1",
            "runtime_request_ref": "runtime-request:1",
            "raw_intent_ref": "intent:1",
            "command_kind": "SUBMIT_USER_GOAL",
            "active_agent_version_id": "agent-version:1",
            "payload": {"query": "renewal", "cutover_mode": "new_default"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert body["data"]["receipt_id"] == "command:client:1:receipt:1"
    assert body["data"]["status"] == "ACCEPTED"
    assert body["data"]["projection"] == {
        "projection_event_id": "projection:command:client:1:accepted",
        "stream_cursor_id": "cursor:command:client:1:1",
        "stream_sequence_no": 1,
        "freshness": "current",
        "redaction_decision_ref": "redaction:command:client:1:server",
    }
    assert body["data"]["available_actions"][0]["action"] == "CANCEL"
    assert body["data"]["available_actions"][0]["action_token_id"] == "action-token:command:client:1:cancel"
    assert body["data"]["available_actions"][0]["effective_security_epoch_ref"] == "security-epoch:product:default"
    assert body["data"]["available_actions"][0]["projection_version"] == 1


def test_goal03_product_runtime_request_route_rejects_rollback_before_service(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    def should_not_submit(**kwargs):
        raise AssertionError("rollback request reached ProductService.submit_runtime_request")

    monkeypatch.setattr(ProductService, "submit_runtime_request", staticmethod(should_not_submit))

    client = TestClient(app)
    response = client.post(
        "/api/v1/product/runtime-requests",
        json={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "conversation_id": "conversation-a",
            "client_request_id": "client:rollback",
            "runtime_request_ref": "runtime-request:rollback",
            "raw_intent_ref": "intent:rollback",
            "command_kind": "SUBMIT_USER_GOAL",
            "active_agent_version_id": "agent-version:1",
            "payload": {
                "query": "rollback must not submit",
                "cutover_mode": "rollback",
                "rollback_reason": "product_runtime_cutover_rollback",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 500
    assert "Product runtime rollback mode is active" in body["status_message"]
    assert "ProductService.submit_runtime_request" not in body["status_message"]


def test_goal03_product_service_rejects_rollback_before_database_write() -> None:
    try:
        ProductService.submit_runtime_request(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            conversation_id="conversation-a",
            principal_id="principal-a",
            active_agent_version_id="agent-version:1",
            client_request_id="client:rollback:service",
            runtime_request_ref="runtime-request:rollback:service",
            raw_intent_ref="intent:rollback:service",
            command_kind="SUBMIT_USER_GOAL",
            payload={
                "goal": "rollback must not write",
                "cutover_mode": "rollback",
                "rollback_reason": "product_runtime_cutover_rollback",
            },
        )
    except ValueError as exc:
        assert "Product runtime rollback mode is active" in str(exc)
    else:
        raise AssertionError("rollback request was accepted by ProductService")


def test_goal03_product_runtime_request_route_rejects_cutover_command_mismatch_before_service(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    def should_not_submit(**kwargs):
        raise AssertionError("cutover mismatch reached ProductService.submit_runtime_request")

    monkeypatch.setattr(ProductService, "submit_runtime_request", staticmethod(should_not_submit))

    client = TestClient(app)
    response = client.post(
        "/api/v1/product/runtime-requests",
        json={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "conversation_id": "conversation-a",
            "client_request_id": "client:canary:mismatch",
            "runtime_request_ref": "runtime-request:canary:mismatch",
            "raw_intent_ref": "intent:canary:mismatch",
            "command_kind": "SUBMIT_USER_GOAL",
            "active_agent_version_id": "agent-version:1",
            "payload": {
                "goal": "canary must use canary command kind",
                "cutover_mode": "canary",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 500
    assert "Product runtime cutover command mismatch" in body["status_message"]
    assert "ProductService.submit_runtime_request" not in body["status_message"]


def test_goal03_product_service_rejects_cutover_mismatch_and_unknown_mode_before_database_write() -> None:
    cases = [
        ("shadow", "SUBMIT_USER_GOAL", "Product runtime cutover command mismatch"),
        ("canary", "SUBMIT_USER_GOAL", "Product runtime cutover command mismatch"),
        ("new_default", "CANARY_SUBMIT_USER_GOAL", "Product runtime cutover command mismatch"),
        ("sidecar", "SUBMIT_USER_GOAL", "unsupported Product runtime cutover mode"),
    ]

    for cutover_mode, command_kind, expected_message in cases:
        try:
            ProductService.submit_runtime_request(
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                conversation_id="conversation-a",
                principal_id="principal-a",
                active_agent_version_id="agent-version:1",
                client_request_id=f"client:{cutover_mode}:mismatch",
                runtime_request_ref=f"runtime-request:{cutover_mode}:mismatch",
                raw_intent_ref=f"intent:{cutover_mode}:mismatch",
                command_kind=command_kind,
                payload={
                    "goal": "cutover mode must match command kind",
                    "cutover_mode": cutover_mode,
                },
            )
        except ValueError as exc:
            assert expected_message in str(exc)
        else:
            raise AssertionError(f"{cutover_mode}:{command_kind} was accepted by ProductService")


def test_goal03_product_service_builds_cutover_owner_context_for_agent_core_handoff() -> None:
    context = ProductService.build_runtime_cutover_owner_context(
        active_agent_version_id="agent-version:1",
        command_id="command:canary:1",
        command_kind="CANARY_SUBMIT_USER_GOAL",
        payload={"cutover_mode": "canary", "goal": "preserve cutover into Agent Core"},
    )

    assert context["active_agent_version_id"] == "agent-version:1"
    assert context["command_id"] == "command:canary:1"
    assert context["command_kind"] == "CANARY_SUBMIT_USER_GOAL"
    assert context["cutover_mode"] == "canary"
    assert context["constraints_hash"] == ProductService.build_runtime_cutover_owner_context(
        active_agent_version_id="agent-version:1",
        command_id="command:canary:1",
        command_kind="CANARY_SUBMIT_USER_GOAL",
        payload={"cutover_mode": "canary", "goal": "different hash-irrelevant value"},
    )["constraints_hash"]
    assert context["constraints_hash"] != ProductService.build_runtime_cutover_owner_context(
        active_agent_version_id="agent-version:1",
        command_id="command:shadow:1",
        command_kind="SHADOW_SUBMIT_USER_GOAL",
        payload={"cutover_mode": "shadow", "goal": "preserve cutover into Agent Core"},
    )["constraints_hash"]


def test_goal03_product_stream_events_route_uses_last_event_id(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    captured = {}

    def fake_events(**kwargs):
        captured.update(kwargs)
        return (
            ProductStreamEventResult(
                event_id="projection:1",
                event_type="DELTA",
                sequence_no=2,
                redaction_decision_ref="redaction:1",
                resync_required=False,
            ),
        )

    monkeypatch.setattr(ProductService, "list_stream_events", staticmethod(fake_events))

    client = TestClient(app)
    response = client.get(
        "/api/v1/product/stream-events?tenant_id=tenant-a&workspace_id=workspace-a",
        headers={"Last-Event-ID": "cursor:previous"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert captured == {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "principal_id": "principal-a",
        "last_event_id": "cursor:previous",
    }
    assert body["data"]["events"][0]["event_id"] == "projection:1"
    assert body["data"]["events"][0]["event_type"] == "DELTA"


def test_goal03_product_action_consume_route_uses_login_principal(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    captured = {}

    def fake_consume(**kwargs):
        captured.update(kwargs)
        return ProductActionConsumeResult(
            action_token_id="action-token:command:client:1:cancel",
            command_id="command:client:1:cancel",
            receipt_id="command:client:1:cancel:receipt:1",
            status="ACCEPTED",
            target_ref="runtime-request:1",
            used_at="2026-07-26T00:00:00+00:00",
        )

    monkeypatch.setattr(ProductService, "consume_action_token", staticmethod(fake_consume))

    client = TestClient(app)
    response = client.post(
        "/api/v1/product/actions/consume",
        json={
            "tenant_id": "tenant-a",
            "action_token_id": "action-token:command:client:1:cancel",
            "client_request_id": "client:1:cancel",
            "raw_intent_ref": "intent:client:1:cancel",
            "payload": {"reason": "user_cancel"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert captured == {
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "action_token_id": "action-token:command:client:1:cancel",
        "client_request_id": "client:1:cancel",
        "raw_intent_ref": "intent:client:1:cancel",
        "payload": {"reason": "user_cancel"},
    }
    assert body["data"] == {
        "action_token_id": "action-token:command:client:1:cancel",
        "command_id": "command:client:1:cancel",
        "receipt_id": "command:client:1:cancel:receipt:1",
        "status": "ACCEPTED",
        "target_ref": "runtime-request:1",
        "used_at": "2026-07-26T00:00:00+00:00",
    }


def test_goal03_product_action_consume_route_fail_closes_replay(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    def replay(**kwargs):
        raise RuntimeError("action token replay detected")

    monkeypatch.setattr(ProductService, "consume_action_token", staticmethod(replay))

    client = TestClient(app)
    response = client.post(
        "/api/v1/product/actions/consume",
        json={
            "tenant_id": "tenant-a",
            "action_token_id": "action-token:command:client:1:cancel",
            "client_request_id": "client:1:cancel",
            "raw_intent_ref": "intent:client:1:cancel",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 500
    assert "action token replay detected" in body["status_message"]
    assert body.get("data") in (None, {})


def test_goal03_product_agent_studio_catalog_routes_use_product_service(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")
    captured = {}

    def fake_draft(**kwargs):
        captured["draft"] = kwargs
        return (
            ProductAgentDefinitionResult(
                agent_definition_id="agent-definition:client-draft",
                tenant_id=kwargs["tenant_id"],
                workspace_id=kwargs["workspace_id"],
                owner_principal_ref=f"principal:{kwargs['principal_id']}",
                display_name=kwargs["display_name"],
                description=kwargs["description"],
                status="DRAFT",
            ),
            ProductAgentDraftResult(
                agent_draft_id="agent-draft:client-draft",
                agent_definition_id="agent-definition:client-draft",
                draft_version=1,
                editor_principal_ref=f"principal:{kwargs['principal_id']}",
                configuration_hash="a" * 64,
                status="DRAFT",
            ),
        )

    def fake_publish(**kwargs):
        captured["publish"] = kwargs
        return (
            ProductAgentPublicationResult(
                publication_id="agent-publication:client-publish",
                agent_version_id=kwargs["agent_version_id"],
                scope=kwargs["publication_scope"],
                status="PUBLISHED",
            ),
            ProductAgentCatalogEntryResult(
                catalog_entry_id="agent-catalog:client-publish",
                agent_version_id=kwargs["agent_version_id"],
                publication_ref="agent-publication:client-publish",
                agent_definition_id=kwargs["agent_definition_id"],
                display_name="Draft Agent",
                description="draft desc",
                definition_status="ACTIVE",
                authorized=True,
                visibility_scope=kwargs["publication_scope"],
                effective_permission_preview_ref="permission-preview:client-publish",
            ),
        )

    def fake_install(**kwargs):
        captured["install"] = kwargs
        return ProductAgentInstallationResult(
            installation_id="agent-installation:client-install",
            agent_version_id=kwargs["agent_version_id"],
            workspace_id=kwargs["workspace_id"],
            principal_ref=f"principal:{kwargs['principal_id']}",
            status="INSTALLED",
        )

    def fake_catalog(**kwargs):
        captured["catalog"] = kwargs
        return (
            ProductAgentCatalogEntryResult(
                catalog_entry_id="agent-catalog:client-publish",
                agent_version_id="agent-version:client-publish",
                publication_ref="agent-publication:client-publish",
                agent_definition_id="agent-definition:client-draft",
                display_name="Draft Agent",
                description="draft desc",
                definition_status="ACTIVE",
                authorized=True,
                visibility_scope="WORKSPACE",
                effective_permission_preview_ref="permission-preview:client-publish",
            ),
        )

    monkeypatch.setattr(ProductService, "create_agent_draft", staticmethod(fake_draft))
    monkeypatch.setattr(ProductService, "publish_agent_version", staticmethod(fake_publish))
    monkeypatch.setattr(ProductService, "install_agent_version", staticmethod(fake_install))
    monkeypatch.setattr(ProductService, "list_agent_catalog", staticmethod(fake_catalog))

    client = TestClient(app)
    draft_response = client.post(
        "/api/v1/product/agent-drafts",
        json={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "client_request_id": "client-draft",
            "display_name": "Draft Agent",
            "description": "draft desc",
            "configuration": {"tools": []},
        },
    )
    publish_response = client.post(
        "/api/v1/product/agent-publications",
        json={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "client_request_id": "client-publish",
            "agent_definition_id": "agent-definition:client-draft",
            "agent_version_id": "agent-version:client-publish",
            "publication_scope": "WORKSPACE",
            "configuration": {"tools": []},
        },
    )
    install_response = client.post(
        "/api/v1/product/agent-installations",
        json={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "client_request_id": "client-install",
            "agent_version_id": "agent-version:client-publish",
            "installation_scope": "USER",
        },
    )
    catalog_response = client.get("/api/v1/product/agent-catalog?tenant_id=tenant-a&workspace_id=workspace-a")

    assert draft_response.status_code == 200
    assert draft_response.json()["data"]["agent_definition"]["agent_definition_id"] == "agent-definition:client-draft"
    assert draft_response.json()["data"]["agent_draft"]["configuration_hash"] == "a" * 64
    assert publish_response.json()["data"]["agent_publication"]["status"] == "PUBLISHED"
    assert publish_response.json()["data"]["agent_catalog_entry"]["authorized"] is True
    assert publish_response.json()["data"]["agent_catalog_entry"]["publication_ref"] == "agent-publication:client-publish"
    assert install_response.json()["data"]["agent_installation"]["principal_ref"] == "principal:principal-a"
    assert catalog_response.json()["data"]["agent_catalog_entries"][0]["catalog_entry_id"] == "agent-catalog:client-publish"
    assert catalog_response.json()["data"]["agent_catalog_entries"][0]["publication_ref"] == "agent-publication:client-publish"
    assert catalog_response.json()["data"]["agent_catalog_entries"][0]["agent_definition_id"] == "agent-definition:client-draft"
    assert catalog_response.json()["data"]["agent_catalog_entries"][0]["display_name"] == "Draft Agent"
    assert catalog_response.json()["data"]["agent_catalog_entries"][0]["description"] == "draft desc"
    assert captured["draft"]["principal_id"] == "principal-a"
    assert captured["install"]["principal_id"] == "principal-a"
    assert captured["catalog"] == {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "principal_id": "principal-a",
    }


def test_goal03_product_agent_studio_snapshot_route_uses_product_service(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    captured = {}

    def fake_snapshot(**kwargs):
        captured.update(kwargs)
        return ProductAgentEditorSnapshotResult(
            agent_definition=ProductAgentDefinitionResult(
                agent_definition_id=kwargs["agent_definition_id"],
                tenant_id=kwargs["tenant_id"],
                workspace_id=kwargs["workspace_id"],
                owner_principal_ref="principal:principal-a",
                display_name="Draft Agent",
                description="draft desc",
                status="ACTIVE",
            ),
            agent_draft=ProductAgentDraftResult(
                agent_draft_id="agent-draft:snapshot",
                agent_definition_id=kwargs["agent_definition_id"],
                draft_version=1,
                editor_principal_ref="principal:principal-a",
                configuration_hash="a" * 64,
                status="DRAFT",
            ),
            agent_version=ProductAgentVersionResult(
                agent_version_id="agent-version:snapshot",
                agent_definition_id=kwargs["agent_definition_id"],
                version_no=1,
                configuration_hash="b" * 64,
                primary_agent_core_profile_ref="agent-core-profile:product:default",
                status="PUBLISHED",
            ),
            agent_catalog_entry=ProductAgentCatalogEntryResult(
                catalog_entry_id="agent-catalog:snapshot",
                agent_version_id="agent-version:snapshot",
                publication_ref="agent-publication:snapshot",
                agent_definition_id=kwargs["agent_definition_id"],
                display_name="Draft Agent",
                description="draft desc",
                definition_status="ACTIVE",
                authorized=True,
                visibility_scope="WORKSPACE",
                effective_permission_preview_ref="permission-preview:snapshot",
            ),
            configuration={
                "name": "Draft Agent",
                "description": "draft desc",
                "tool_ids": ["tool-1"],
                "llm_id": "llm-1",
                "mcp_ids": ["mcp-1"],
                "system_prompt": "Be helpful",
                "knowledge_ids": ["knowledge-1"],
                "agent_skill_ids": ["skill-1"],
                "enable_memory": True,
            },
        )

    monkeypatch.setattr(ProductService, "load_agent_studio_snapshot", staticmethod(fake_snapshot))

    client = TestClient(app)
    response = client.get(
        "/api/v1/product/agent-studio/agent-definition:snapshot?tenant_id=tenant-a&workspace_id=workspace-a"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert body["data"]["agent_definition"]["agent_definition_id"] == "agent-definition:snapshot"
    assert body["data"]["agent_draft"]["agent_draft_id"] == "agent-draft:snapshot"
    assert body["data"]["agent_version"]["agent_version_id"] == "agent-version:snapshot"
    assert body["data"]["agent_catalog_entry"]["catalog_entry_id"] == "agent-catalog:snapshot"
    assert body["data"]["configuration"]["llm_id"] == "llm-1"
    assert captured == {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "principal_id": "principal-a",
        "agent_definition_id": "agent-definition:snapshot",
    }


def test_goal03_product_agent_revoke_routes_use_product_service(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")
    captured = {}

    def fake_revoke_install(**kwargs):
        captured["installation"] = kwargs
        return ProductAgentInstallationResult(
            installation_id=kwargs["installation_id"],
            agent_version_id="",
            workspace_id=kwargs["workspace_id"],
            principal_ref=f"principal:{kwargs['principal_id']}",
            status="REVOKED",
        )

    def fake_revoke_publication(**kwargs):
        captured["publication"] = kwargs
        return ProductAgentPublicationResult(
            publication_id=kwargs["publication_id"],
            agent_version_id="",
            scope="",
            status="REVOKED",
        )

    monkeypatch.setattr(ProductService, "revoke_agent_installation", staticmethod(fake_revoke_install))
    monkeypatch.setattr(ProductService, "revoke_agent_publication", staticmethod(fake_revoke_publication))

    client = TestClient(app)
    install_response = client.delete(
        "/api/v1/product/agent-installations/agent-installation-1?tenant_id=tenant-a&workspace_id=workspace-a"
    )
    publication_response = client.delete(
        "/api/v1/product/agent-publications/agent-publication-1?tenant_id=tenant-a&workspace_id=workspace-a"
    )

    assert install_response.status_code == 200
    assert install_response.json()["data"]["agent_installation"]["status"] == "REVOKED"
    assert publication_response.status_code == 200
    assert publication_response.json()["data"]["agent_publication"]["status"] == "REVOKED"
    assert captured["installation"]["principal_id"] == "principal-a"
    assert captured["publication"]["publication_id"] == "agent-publication-1"


def test_goal03_product_artifact_routes_reauthorize_through_product_surface(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")
    captured = {}

    def fake_get(artifact_id: str, *, principal_id: str = ""):
        captured["get"] = {"artifact_id": artifact_id, "principal_id": principal_id}
        return {
            "artifact": {"artifact_id": artifact_id, "download_policy": "AUTHORIZED"},
            "content": "# artifact",
            "citation_refs": [{"citation_ref": "citation:1"}],
            "download": {
                "url": f"/api/v1/product/artifacts/{artifact_id}/download",
                "filename": f"{artifact_id}.md",
                "media_type": "text/markdown; charset=utf-8",
                "policy": "AUTHORIZED",
            },
        }

    def fake_download(artifact_id: str, *, principal_id: str = ""):
        captured["download"] = {"artifact_id": artifact_id, "principal_id": principal_id}
        return {
            "content": "# artifact",
            "filename": f"{artifact_id}.md",
            "media_type": "text/markdown; charset=utf-8",
        }

    monkeypatch.setattr(ProductService, "get_artifact", staticmethod(fake_get))
    monkeypatch.setattr(ProductService, "download_artifact", staticmethod(fake_download))

    client = TestClient(app)
    read_response = client.get("/api/v1/product/artifacts/artifact-1")
    download_response = client.get("/api/v1/product/artifacts/artifact-1/download")

    assert read_response.status_code == 200
    assert read_response.json()["data"]["download"]["url"] == "/api/v1/product/artifacts/artifact-1/download"
    assert read_response.json()["data"]["product_artifact"] == {
        "artifact_ref": "artifact-1",
        "publication_ref": "publication:artifact-1",
        "projection_version": 0,
        "downloadable": True,
        "citation_refs": ["citation:1"],
        "citation_count": 1,
        "citation_authorized": True,
        "download_policy": "AUTHORIZED",
    }
    assert read_response.json()["data"]["product_quality"]["status"] == "RUNTIME_OBSERVED"
    assert read_response.json()["data"]["product_quality"]["metrics"] == {"citation_count": 1}
    assert download_response.status_code == 200
    assert download_response.text == "# artifact"
    assert download_response.headers["cache-control"] == "no-store"
    assert 'filename="artifact-1.md"' in download_response.headers["content-disposition"]
    assert captured == {
        "get": {"artifact_id": "artifact-1", "principal_id": "principal-a"},
        "download": {"artifact_id": "artifact-1", "principal_id": "principal-a"},
    }


def test_goal03_product_feedback_route_records_delivery_feedback(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")
    captured = {}

    def fake_feedback(**kwargs):
        captured.update(kwargs)
        return {
            "feedback_id": "feedback-product-1",
            "task_id": kwargs["task_id"],
            "rating": kwargs["rating"],
            "label": kwargs["label"],
            "comment": kwargs["comment"],
            "dataset_candidate": kwargs["dataset_candidate"],
        }

    monkeypatch.setattr(ProductService, "record_feedback", staticmethod(fake_feedback))

    client = TestClient(app)
    response = client.post(
        "/api/v1/product/feedback",
        json={
            "task_id": "task-1",
            "rating": 5,
            "label": "helpful",
            "comment": "useful",
            "dataset_candidate": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["feedback_id"] == "feedback-product-1"
    assert captured == {
        "task_id": "task-1",
        "rating": 5,
        "label": "helpful",
        "comment": "useful",
        "dataset_candidate": False,
    }


def test_goal03_product_stream_route_returns_sse_projection_events(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    captured = {}

    def fake_events(**kwargs):
        captured.update(kwargs)
        return (
            ProductStreamEventResult(
                event_id="projection:1",
                event_type="RESYNC_REQUIRED",
                sequence_no=2,
                redaction_decision_ref="redaction:resync-required",
                resync_required=True,
            ),
        )

    monkeypatch.setattr(ProductService, "list_stream_events", staticmethod(fake_events))

    client = TestClient(app)
    response = client.get(
        "/api/v1/product/stream?tenant_id=tenant-a&workspace_id=workspace-a",
        headers={"Last-Event-ID": "cursor:expired"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["connection"] == "keep-alive"
    assert response.headers["x-accel-buffering"] == "no"
    assert captured["last_event_id"] == "cursor:expired"
    assert "retry: 1000" in response.text
    assert "id: projection:1" in response.text
    assert "event: RESYNC_REQUIRED" in response.text
    assert '"resync_required": true' in response.text
    assert "event: HEARTBEAT" in response.text
    assert '"event_id":"heartbeat"' in response.text
    assert '"event_type":"HEARTBEAT"' in response.text
    assert '"sequence_no":0' in response.text
    assert '"redaction_decision_ref":"redaction:heartbeat"' in response.text


def test_goal03_product_router_is_registered_in_main_api_router() -> None:
    router_text = (
        __import__("pathlib").Path("src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    )
    assert "product," in router_text
    assert "router.include_router(product.router)" in router_text
