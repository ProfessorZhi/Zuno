from __future__ import annotations


def test_workspace_product_object_contracts_cover_phase03_fields() -> None:
    from zuno.schema import workspace

    expected_models = {
        "WorkspaceContract": {
            "workspace_id",
            "owner",
            "members",
            "policy_scope",
            "retention_policy",
            "status",
            "created_at",
            "updated_at",
        },
        "KnowledgeSpaceContract": {
            "knowledge_space_id",
            "workspace_id",
            "graph_project_id",
            "index_version",
            "acl_policy",
            "status",
            "created_at",
            "updated_at",
        },
        "WorkspaceSessionContract": {
            "session_id",
            "workspace_id",
            "user_id",
            "thread_id",
            "active_task_id",
            "status",
            "created_at",
            "updated_at",
        },
        "WorkspaceTaskContract": {
            "task_id",
            "session_id",
            "workspace_id",
            "goal",
            "product_mode",
            "status",
            "budget",
            "trace_id",
            "created_at",
            "updated_at",
        },
        "UploadedFileContract": {
            "file_id",
            "workspace_id",
            "mime_type",
            "hash",
            "security_label",
            "parse_status",
            "created_at",
            "updated_at",
        },
        "ArtifactContract": {
            "artifact_id",
            "task_id",
            "kind",
            "uri",
            "hash",
            "download_policy",
            "created_at",
            "updated_at",
        },
        "TraceEventContract": {
            "event_id",
            "task_id",
            "trace_id",
            "type",
            "timestamp",
            "payload",
        },
        "CitationContract": {
            "citation_id",
            "evidence_id",
            "document_id",
            "block_id",
            "source_span",
            "created_at",
        },
        "FeedbackContract": {
            "feedback_id",
            "task_id",
            "rating",
            "label",
            "comment",
            "dataset_candidate",
            "created_at",
        },
    }

    for model_name, expected_fields in expected_models.items():
        model = getattr(workspace, model_name)
        assert expected_fields.issubset(set(model.model_fields)), model_name


def test_workspace_task_state_machine_and_request_envelope_are_pinned() -> None:
    from zuno.schema.workspace import (
        WORKSPACE_TASK_STATUS_FLOW,
        WorkSpaceSimpleTask,
        WorkspaceOutputContract,
        WorkspaceTaskBudget,
    )

    assert WORKSPACE_TASK_STATUS_FLOW == [
        "created",
        "context_building",
        "planning",
        "running",
        "approval_waiting",
        "resuming",
        "finalizing",
        "completed",
        "failed",
        "cancelled",
    ]

    task = WorkSpaceSimpleTask(
        query="Summarize the new supplier contract",
        model_id="model-local",
        session_id="session_1",
        workspace_id="workspace_1",
        user_id="user_1",
        goal="contract_review",
        product_mode="contract_review",
        knowledge_space_ids=["ks_contracts"],
        uploaded_file_ids=["file_contract"],
        approval_mode="required_for_risky_tools",
        budget=WorkspaceTaskBudget(max_steps=8, max_tokens=24000, timeout_seconds=180),
        output_contract=WorkspaceOutputContract(
            artifact_kinds=["markdown", "citation_bundle"],
            citation_required=True,
            trace_required=True,
        ),
        plugins=[],
        mcp_servers=[],
    )

    dumped = task.model_dump()
    assert dumped["workspace_id"] == "workspace_1"
    assert dumped["knowledge_space_ids"] == ["ks_contracts"]
    assert dumped["uploaded_file_ids"] == ["file_contract"]
    assert dumped["budget"]["max_steps"] == 8
    assert dumped["output_contract"]["citation_required"] is True


def test_workspace_product_stream_event_contract_is_traceable() -> None:
    from zuno.schema.workspace import WorkspaceProductStreamEvent

    event = WorkspaceProductStreamEvent(
        event_id="event_1",
        task_id="task_1",
        trace_id="trace_1",
        type="artifact.ready",
        status="running",
        timestamp=123.0,
        payload={"artifact_id": "artifact_1"},
    )

    dumped = event.model_dump()
    assert dumped["event_id"] == "event_1"
    assert dumped["task_id"] == "task_1"
    assert dumped["trace_id"] == "trace_1"
    assert dumped["type"] == "artifact.ready"
    assert dumped["payload"]["artifact_id"] == "artifact_1"
