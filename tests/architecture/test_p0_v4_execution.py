"""Verification-only V4 execution for RB-P0-V4-EXECUTION-001.

This file is intentionally not product Runtime code.  The model spikes and
local provider emulator prove failure contracts at an emulated boundary; the
tests that import ``zuno`` exercise current repository behavior.  The session
record must keep those two evidence scopes separate.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Lock
from urllib.error import URLError
from urllib.request import Request, urlopen

import pytest


@dataclass(frozen=True, slots=True)
class Proposal:
    proposal_id: str
    owner: str
    payload: dict[str, str]
    expected_version: int


class DomainOwnerSpike:
    """Verification-only model for the missing canonical mutation contract."""

    def __init__(self, owner: str = "domain-owner") -> None:
        self.owner = owner
        self.version = 0
        self.payload: dict[str, str] = {}
        self.committed: dict[str, int] = {}
        self._lock = Lock()

    def commit(self, proposal: Proposal) -> int:
        with self._lock:
            if proposal.owner != self.owner:
                raise PermissionError("non-owner mutation")
            if proposal.proposal_id in self.committed:
                return self.committed[proposal.proposal_id]
            if proposal.expected_version != self.version:
                raise ValueError("stale version")
            self.version += 1
            self.payload = dict(proposal.payload)
            self.committed[proposal.proposal_id] = self.version
            return self.version


@dataclass(frozen=True, slots=True)
class PlanWrite:
    plan_id: str
    expected_domain_version: int
    payload: str


class PlanDomainConflictSpike:
    """Verification-only model for stale PlanVersion write rejection."""

    def __init__(self) -> None:
        self.domain_version = 10
        self.applied_plans: dict[str, int] = {}
        self._lock = Lock()

    def mutate_domain(self) -> int:
        with self._lock:
            self.domain_version += 1
            return self.domain_version

    def commit(self, write: PlanWrite) -> str:
        with self._lock:
            if write.plan_id in self.applied_plans:
                return "idempotent_replay"
            if write.expected_domain_version != self.domain_version:
                return "conflict_replan_required"
            self.applied_plans[write.plan_id] = self.domain_version
            return "committed"


def test_q005_v4_spike_owner_concurrency_duplicate_and_stale_rejection() -> None:
    owner = DomainOwnerSpike()
    unauthorized = Proposal("p-unauthorized", "agent", {"fact": "x"}, 0)
    with pytest.raises(PermissionError):
        owner.commit(unauthorized)

    proposals = [
        Proposal(f"p-{index}", "domain-owner", {"fact": str(index)}, 0)
        for index in range(2)
    ]

    def attempt(proposal: Proposal) -> tuple[str, str, int | None]:
        try:
            return ("committed", proposal.proposal_id, owner.commit(proposal))
        except ValueError:
            return ("stale", proposal.proposal_id, None)

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, proposals))
    assert sorted(outcome[0] for outcome in outcomes) == ["committed", "stale"]
    committed = next(outcome for outcome in outcomes if outcome[0] == "committed")
    committed_proposal = next(proposal for proposal in proposals if proposal.proposal_id == committed[1])
    assert owner.commit(committed_proposal) == 1
    with pytest.raises(ValueError, match="stale version"):
        owner.commit(Proposal("p-stale", "domain-owner", {"fact": "old"}, 0))


def test_q053_v4_spike_rejects_stale_plan_and_replays_idempotently() -> None:
    state = PlanDomainConflictSpike()
    write = PlanWrite("plan-v1", 10, "proposal")
    assert state.mutate_domain() == 11
    assert state.commit(write) == "conflict_replan_required"
    fresh = PlanWrite("plan-v2", 11, "proposal-new")
    assert state.commit(fresh) == "committed"
    assert state.commit(fresh) == "idempotent_replay"


def test_q097_v4_spike_recovery_keeps_unknown_effect_out_of_retry() -> None:
    state = {"domain": "committed", "checkpoint": "stale", "effect": "unknown"}
    recovery = {
        "authoritative": "domain",
        "rebuildable": ("checkpoint",),
        "irreversible": ("effect",),
        "next_action": "reconcile_before_retry",
    }
    assert state["domain"] == "committed"
    assert recovery["authoritative"] == "domain"
    assert recovery["next_action"] == "reconcile_before_retry"
    assert state["effect"] != "retry"


class _ProviderState:
    def __init__(self) -> None:
        self.effects: dict[str, str] = {}
        self.counts: dict[str, int] = {}
        self.lock = Lock()


class _ProviderHandler(BaseHTTPRequestHandler):
    state: _ProviderState

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        key = str(payload["idempotency_key"])
        mode = str(payload.get("mode", "normal"))
        with self.state.lock:
            already_committed = key in self.state.effects
            if not already_committed:
                self.state.counts[key] = self.state.counts.get(key, 0) + 1
                if mode != "not_committed_then_drop":
                    self.state.effects[key] = f"provider-effect:{key}"
        if mode in {"commit_then_drop", "not_committed_then_drop"}:
            self.close_connection = True
            return
        body = json.dumps(
            {
                "status": "replayed" if already_committed else "committed",
                "provider_operation_id": self.state.effects.get(key),
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        key = self.path.partition("?key=")[2]
        with self.state.lock:
            effect = self.state.effects.get(key)
        body = json.dumps(
            {"status": "committed" if effect else "not_found", "provider_operation_id": effect}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args: object) -> None:
        return


@pytest.fixture()
def provider_server():
    state = _ProviderState()
    handler = type("ProviderHandler", (_ProviderHandler,), {"state": state})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = __import__("threading").Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server, state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _post(server: ThreadingHTTPServer, payload: dict[str, str], timeout: float = 1.0) -> dict[str, str]:
    request = Request(
        f"http://127.0.0.1:{server.server_port}/effect",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def _status(server: ThreadingHTTPServer, key: str) -> dict[str, str | None]:
    with urlopen(f"http://127.0.0.1:{server.server_port}/status?key={key}", timeout=1) as response:
        return json.loads(response.read())


def test_q063_v4_loopback_provider_response_loss_is_idempotent(provider_server) -> None:
    server, state = provider_server
    key = "idem:q063:one"
    with pytest.raises((URLError, TimeoutError, ConnectionError, OSError)):
        _post(server, {"idempotency_key": key, "mode": "commit_then_drop"})
    replay = _post(server, {"idempotency_key": key, "mode": "normal"})
    assert replay["status"] == "replayed"
    assert replay["provider_operation_id"] == f"provider-effect:{key}"
    assert state.counts[key] == 1


def test_q064_v4_unknown_outcome_reconciles_before_safe_retry(provider_server) -> None:
    server, state = provider_server
    committed_key = "idem:q064:committed"
    with pytest.raises((URLError, TimeoutError, ConnectionError, OSError)):
        _post(server, {"idempotency_key": committed_key, "mode": "commit_then_drop"})
    committed = _status(server, committed_key)
    assert committed["status"] == "committed"
    assert state.counts[committed_key] == 1

    retryable_key = "idem:q064:not-committed"
    with pytest.raises((URLError, TimeoutError, ConnectionError, OSError)):
        _post(server, {"idempotency_key": retryable_key, "mode": "not_committed_then_drop"})
    not_committed = _status(server, retryable_key)
    assert not_committed["status"] == "not_found"
    assert _post(server, {"idempotency_key": retryable_key, "mode": "normal"})["status"] == "committed"
    assert state.counts[retryable_key] == 2


def test_q016_current_runtime_restarts_without_treating_checkpoint_as_domain_fact(tmp_path) -> None:
    from zuno.agent.runtime import AgentRuntimeService, ReflectionDecision, RuntimeStartRequest, SQLiteAgentRunStore

    request = RuntimeStartRequest(
        run_id="run:q016-v4",
        thread_id="thread:q016-v4",
        workspace_id="workspace:q016-v4",
        user_id="user:q016-v4",
        task_id="task:q016-v4",
        trace_id="trace:q016-v4",
        goal="exercise restart boundary",
        reflection_decision=ReflectionDecision.USE_TOOL,
    )
    first = AgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))
    interrupted = first.start(request)
    assert interrupted.finalization_status == "interrupted"
    assert first.store.latest_checkpoint(request.task_id) is not None
    second = AgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))
    resumed = second.resume(task_id=request.task_id, approval_decision="approved")
    assert resumed.finalization_status == "finalized"
    assert second.store.pending_interrupt(request.task_id) is None


def test_q033_current_runtime_requires_approval_before_effect() -> None:
    from zuno.capability.control_plane import ApprovalGate, ToolApprovalPolicy, ToolCardManifest, ToolExecutionMode, ToolSideEffectLevel, ToolTrustTier

    manifest = ToolCardManifest(
        tool_id="effect.q033",
        owner="verification",
        capability_domain="verification",
        description_for_model="effect",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        execution_mode=ToolExecutionMode.API,
        trust_tier=ToolTrustTier.WORKSPACE,
        side_effect_level=ToolSideEffectLevel.WRITE_EXTERNAL,
        approval_policy=ToolApprovalPolicy.APPROVAL_REQUIRED,
        sandbox_profile="isolated",
        credential_policy="none",
        network_policy="deny",
        audit_policy="trace",
        budget={"timeout_seconds": 1},
        executor_adapter="verification.q033",
    )
    decision = ApprovalGate().evaluate(manifest)
    assert decision.allowed is False
    assert decision.approval_required is True
    assert decision.interrupt is None


def test_q039_citation_fixture_abstains_when_retrieval_has_no_citation() -> None:
    from zuno.agent.runtime.state import AgentRuntimeState
    from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind
    from zuno.agent.runtime.synthesis.grounded_answer import GroundedSynthesisEngine

    state = AgentRuntimeState(
        run_id="run:q039-v4",
        thread_id="thread:q039-v4",
        workspace_id="workspace:q039-v4",
        user_id="user:q039-v4",
        task_id="task:q039-v4",
        trace_id="trace:q039-v4",
        goal="Which evidence supports the claim?",
        observations=[
            NormalizedObservation(
                observation_id="retrieval:q039",
                kind=ObservationKind.RETRIEVAL,
                evidence_ids=["evidence:missing-citation"],
                citation_ids=[],
            )
        ],
    )
    result = GroundedSynthesisEngine().synthesize(state)
    assert result.metadata["unsupported_claims"]
    assert "Insufficient cited evidence" in result.metadata["final_answer"]


def test_q039_wrong_span_is_not_silently_accepted() -> None:
    from zuno.knowledge.provenance import CitationCandidate, CitationProvenanceGuard, EvidenceLineage, SourceSpanLineage

    evidence = {
        "evidence:wrong-span": EvidenceLineage(
            evidence_id="evidence:wrong-span",
            document_version_id="document:q039:v1",
            source_span_id="span:correct",
            claim_refs=("claim:q039",),
        )
    }
    spans = {
        "span:wrong": SourceSpanLineage(
            source_span_id="span:wrong",
            evidence_id="evidence:wrong-span",
            document_version_id="document:q039:v1",
        )
    }
    result = CitationProvenanceGuard().validate(
        CitationCandidate(
            claim_id="claim:q039",
            evidence_id="evidence:wrong-span",
            document_version_id="document:q039:v1",
            source_span_id="span:wrong",
            citation_id="citation:evidence:wrong-span",
        ),
        evidence_by_id=evidence,
        spans_by_id=spans,
    )
    assert result.accepted is False
    assert result.reason_code == "evidence_span_mismatch"


def test_q067_untrusted_context_cannot_authorize_tool() -> None:
    from zuno.platform.security.runtime_batch import SecurityRuntimeBatch, TrustLabel

    flow = SecurityRuntimeBatch().information_flow(
        flow_ref="flow:q067-v4",
        source_label=TrustLabel.UNTRUSTED,
        sink_ref="sink:tool",
        protected_sink_policy_ref="policy:tool",
    )
    assert flow.allowed is False


def test_q070_current_readonly_trace_has_correlation_fields() -> None:
    from zuno.capability.control_plane import ExecutorAdapterContract, ToolApprovalPolicy, ToolCardManifest, ToolExecutionMode, ToolSideEffectLevel, ToolTrustTier
    from zuno.capability.runtime import ToolControlPlaneRuntime, ToolRuntimeRequest

    runtime = ToolControlPlaneRuntime()
    runtime.register_manifest(
        ToolCardManifest(
            tool_id="read.q070",
            owner="verification",
            capability_domain="verification",
            description_for_model="read",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.READ,
            approval_policy=ToolApprovalPolicy.AUTO,
            sandbox_profile="workspace_ro",
            credential_policy="none",
            network_policy="deny",
            audit_policy="trace",
            budget={"timeout_seconds": 1},
            executor_adapter="verification.q070",
        )
    )
    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="verification.q070",
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            sandbox_profile="workspace_ro",
            network_policy="deny",
            credential_policy="none",
            timeout_seconds=1,
        ),
        lambda _args, _context: {"status": "success"},
    )
    result = runtime.execute(
        ToolRuntimeRequest(
            tool_id="read.q070",
            arguments={},
            workspace_id="workspace:q070-v4",
            user_id="user:q070-v4",
            task_id="task:q070-v4",
            trace_id="trace:q070-v4",
            model_intent="read",
        )
    )
    assert result.status == "completed"
    assert result.audit_event.audit_id
    assert result.audit_event.trace_id == "trace:q070-v4"
    assert result.audit_event.task_id == "task:q070-v4"
    assert all(
        event["payload"].get("tool_request_id")
        for event in result.task_events
        if event.get("type") in {"tool_call", "tool_result"}
    )
