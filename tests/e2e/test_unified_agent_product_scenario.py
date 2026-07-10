from __future__ import annotations

from zuno.agent.runtime import SQLiteAgentRunStore
from zuno.api.services.user import UserPayload
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.schema.workspace import WorkSpaceSimpleTask, WorkspaceOutputContract


def test_unified_agent_product_scenario_exposes_artifact_trace_and_runtime_recovery(tmp_path) -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    WorkspaceTaskRuntimeService.configure_unified_runtime_store_for_tests(
        SQLiteAgentRunStore(tmp_path / "product_scenario_unified_runtime.db")
    )

    snapshot = WorkspaceTaskRuntimeService.create_task(
        simple_task=WorkSpaceSimpleTask(
            query="Produce an executive brief from the selected enterprise knowledge space.",
            model_id="model-local",
            session_id="session_phase11_product",
            workspace_id="workspace_phase11_product",
            task_id="task_phase11_product",
            trace_id="trace_phase11_product",
            goal="enterprise knowledge brief",
            product_mode="enterprise_kb",
            knowledge_space_ids=["ks_enterprise"],
            uploaded_file_ids=["file_policy"],
            output_contract=WorkspaceOutputContract(
                artifact_kinds=["markdown"],
                citation_required=True,
                trace_required=True,
                format="markdown",
            ),
            plugins=[],
            mcp_servers=[],
        ),
        login_user=UserPayload(
            user_id="user_phase11_product",
            user_name="Phase11 Product User",
            role="admin",
        ),
    )

    assert snapshot["task"]["status"] == "completed"
    assert snapshot["artifact_ids"]
    assert snapshot["unified_runtime"]["task_id"] == "task_phase11_product"
    assert snapshot["unified_runtime"]["workspace_id"] == "workspace_phase11_product"
    assert snapshot["retrieval_plan"]["retrieval_profiles"]["ks_enterprise"] in {"standard", "deep"}
    assert snapshot["observability"]["trace_replay"]["source_refs"] is not None

    runtime_events = [
        event
        for event in WorkspaceTaskRuntimeService.list_task_events("task_phase11_product")
        if event["payload"].get("runtime_topology") == "unified_agent_runtime"
    ]
    assert runtime_events
    assert runtime_events[0]["type"] == "runtime_started"
    assert runtime_events[-1]["type"] == "runtime_completed"
