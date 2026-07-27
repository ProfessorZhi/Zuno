from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from zuno.memory.contracts import MemoryScope
from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.memory import (
    ContextPackInput,
    MemoryCaptureInput,
    MemoryUnitOfWork,
    MemoryUseTraceInput,
)


@dataclass(frozen=True, slots=True)
class GovernedMemoryCommitReceipt:
    capture_intent_id: str
    candidate_id: str
    memory_version_id: str
    context_pack_id: str
    memory_use_trace_id: str


class GovernedMemoryContextRuntime:
    def __init__(self, unit_of_work_factory: Callable[[], MemoryUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def commit_turn_outcome(
        self,
        *,
        scope: MemoryScope,
        event_id: str,
        run_id: str,
        step_run_id: str,
        task: str,
        response: str,
        context_trace: dict[str, Any],
        security_epoch_ref: str = "security-epoch:memory-default",
        policy_ref: str = "memory-policy:default-governed",
    ) -> GovernedMemoryCommitReceipt:
        tenant_id = scope.user_id or "tenant:default"
        workspace_id = scope.project_id or scope.agent_id or "workspace:default"
        source_ref = event_id
        payload = {
            "task": task,
            "response": response,
            "context_trace_hash": canonical_sha256(context_trace),
            "source_ref": source_ref,
        }
        stable_key = canonical_sha256(
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "source_ref": source_ref,
                "policy_ref": policy_ref,
            }
        )[:24]
        capture_intent_id = f"memory-capture:{stable_key}"
        candidate_id = f"memory-candidate:{stable_key}"
        memory_record_id = f"memory-record:{stable_key}"
        memory_version_id = f"memory-version:{stable_key}"
        context_pack_id = f"context-pack:{stable_key}"
        memory_use_trace_id = f"memory-use:{stable_key}"

        with self._unit_of_work_factory() as repo:
            repo.commit_governed_memory(
                MemoryCaptureInput(
                    capture_intent_id=capture_intent_id,
                    candidate_id=candidate_id,
                    memory_record_id=memory_record_id,
                    memory_version_id=memory_version_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    source_module="06 Agent Core / Planning & Control",
                    source_ref=source_ref,
                    trigger_type="RUN_OUTCOME",
                    memory_kind="EPISODIC",
                    content_ref=f"object://memory/{stable_key}",
                    source_refs=(source_ref,),
                    confidence=0.8,
                    evidence_strength=0.8,
                    conflict_key=f"{scope.user_id}:{scope.agent_id}:{source_ref}",
                    dedupe_key=stable_key,
                    policy_ref=policy_ref,
                    security_epoch_ref=security_epoch_ref,
                    idempotency_key=f"memory:{stable_key}",
                    payload=payload,
                )
            )
            repo.activate_memory_version(
                memory_version_id=memory_version_id,
                expected_generation=1,
                snapshot_payload={"memory_version_id": memory_version_id, "state": "ACTIVE", "source_ref": source_ref},
                serving_watermark_ref=f"memory-watermark:{stable_key}",
            )
            repo.build_context_pack(
                pack=ContextPackInput(
                    context_pack_id=context_pack_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    run_id=run_id,
                    step_run_id=step_run_id,
                    memory_version_id=memory_version_id,
                    budget_tokens=512,
                    selection_payload={
                        "source_ref": source_ref,
                        "recency": "current_turn",
                        "relevance": 1.0,
                        "sensitivity": "policy_filtered",
                    },
                    compression_payload={
                        "strategy": "F2",
                        "pre_tokens": max(1, len(response or task) // 4),
                        "post_tokens": max(1, min(512, len(response or task) // 6)),
                        "fidelity_check": "source_bound",
                    },
                    trace_payload={"context_trace": context_trace, "source_ref": source_ref},
                    state="ACTIVE",
                )
            )
            repo.record_memory_use(
                MemoryUseTraceInput(
                    memory_use_trace_id=memory_use_trace_id,
                    memory_version_id=memory_version_id,
                    context_pack_id=context_pack_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    run_id=run_id,
                    trace_payload={"adopted_by_agent_core": True, "source_ref": source_ref},
                    adopted_by_agent_core=True,
                )
            )

        return GovernedMemoryCommitReceipt(
            capture_intent_id=capture_intent_id,
            candidate_id=candidate_id,
            memory_version_id=memory_version_id,
            context_pack_id=context_pack_id,
            memory_use_trace_id=memory_use_trace_id,
        )


__all__ = ["GovernedMemoryCommitReceipt", "GovernedMemoryContextRuntime"]
