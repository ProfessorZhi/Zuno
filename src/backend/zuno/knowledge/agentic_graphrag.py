from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from pydantic import BaseModel, Field

from zuno.knowledge.ingestion import CanonicalDocumentIR


class ProductMode(str, Enum):
    NORMAL = "normal"
    ENHANCED = "enhanced"
    AUTO = "auto"


class QueryMethod(str, Enum):
    BASIC = "basic"
    LOCAL = "local"
    GLOBAL = "global"
    DRIFT = "drift"


class RetrievalRouterInput(BaseModel):
    query: str
    workspace_id: str
    context_pack: dict[str, Any] = Field(default_factory=dict)
    product_mode: ProductMode = ProductMode.AUTO
    budget: dict[str, Any] = Field(default_factory=dict)
    acl_scope: dict[str, Any] = Field(default_factory=dict)
    evidence_state: dict[str, Any] = Field(default_factory=dict)
    fallback_history: list[str] = Field(default_factory=list)
    trace_id: str
    task_id: str


class RetrievalRouterDecision(BaseModel):
    requested_product_mode: ProductMode
    retrieval_required: bool
    candidate_methods: list[QueryMethod] = Field(default_factory=list)
    resolved_methods: list[QueryMethod] = Field(default_factory=list)
    router_decision: str
    workspace_id: str
    trace_id: str
    task_id: str
    fallback_reason: str | None = None
    no_retrieval_reason: str | None = None
    route_trace: dict[str, Any] = Field(default_factory=dict)

    def to_trace(self) -> dict[str, Any]:
        return {
            "requested_product_mode": self.requested_product_mode.value,
            "retrieval_required": self.retrieval_required,
            "candidate_methods": [method.value for method in self.candidate_methods],
            "resolved_methods": [method.value for method in self.resolved_methods],
            "router_decision": self.router_decision,
            "fallback_reason": self.fallback_reason,
            "no_retrieval_reason": self.no_retrieval_reason,
            "workspace_id": self.workspace_id,
            "trace_id": self.trace_id,
            "task_id": self.task_id,
            "route_trace": dict(self.route_trace),
        }


class AgenticRetrievalRouter:
    def decide(self, request: RetrievalRouterInput) -> RetrievalRouterDecision:
        product_mode = ProductMode(request.product_mode)
        if product_mode is ProductMode.NORMAL:
            return self._decision(
                request=request,
                retrieval_required=True,
                candidate_methods=[QueryMethod.BASIC],
                resolved_methods=[QueryMethod.BASIC],
                router_decision="normal_basic",
                route_trace={"mode_policy": "normal_forces_basic"},
            )

        if product_mode is ProductMode.ENHANCED:
            methods, decision, trace = self._select_methods(request.query, request.fallback_history)
            return self._decision(
                request=request,
                retrieval_required=True,
                candidate_methods=methods,
                resolved_methods=methods,
                router_decision=f"enhanced_{decision}",
                route_trace={"mode_policy": "enhanced_requires_retrieval", **trace},
            )

        if not self._needs_retrieval(request):
            return self._decision(
                request=request,
                retrieval_required=False,
                candidate_methods=[],
                resolved_methods=[],
                router_decision="auto_no_retrieval",
                no_retrieval_reason="query_can_be_answered_from_context",
                route_trace={"mode_policy": "auto_decides_retrieval_need_first"},
            )

        methods, decision, trace = self._select_methods(request.query, request.fallback_history)
        return self._decision(
            request=request,
            retrieval_required=True,
            candidate_methods=methods,
            resolved_methods=methods,
            router_decision=f"auto_{decision}",
            fallback_reason=self._fallback_reason(request.fallback_history),
            route_trace={"mode_policy": "auto_selected_internal_methods", **trace},
        )

    def _decision(
        self,
        *,
        request: RetrievalRouterInput,
        retrieval_required: bool,
        candidate_methods: list[QueryMethod],
        resolved_methods: list[QueryMethod],
        router_decision: str,
        fallback_reason: str | None = None,
        no_retrieval_reason: str | None = None,
        route_trace: dict[str, Any] | None = None,
    ) -> RetrievalRouterDecision:
        max_methods = request.budget.get("max_methods")
        if isinstance(max_methods, int) and max_methods > 0:
            candidate_methods = candidate_methods[:max_methods]
            resolved_methods = resolved_methods[:max_methods]
        return RetrievalRouterDecision(
            requested_product_mode=ProductMode(request.product_mode),
            retrieval_required=retrieval_required,
            candidate_methods=candidate_methods,
            resolved_methods=resolved_methods,
            router_decision=router_decision,
            workspace_id=request.workspace_id,
            trace_id=request.trace_id,
            task_id=request.task_id,
            fallback_reason=fallback_reason,
            no_retrieval_reason=no_retrieval_reason,
            route_trace=route_trace or {},
        )

    def _select_methods(
        self, query: str, fallback_history: Iterable[str]
    ) -> tuple[list[QueryMethod], str, dict[str, Any]]:
        normalized = query.lower()
        fallback_text = " ".join(fallback_history).lower()
        if self._looks_like_drift(normalized, fallback_text):
            return (
                [QueryMethod.DRIFT, QueryMethod.LOCAL, QueryMethod.BASIC],
                "drift_research",
                {"drift_required": True, "chunk_backfill_required": True},
            )
        if self._looks_like_global(normalized):
            return (
                [QueryMethod.GLOBAL, QueryMethod.LOCAL, QueryMethod.BASIC],
                "global_staged",
                {"community_prior_required": True, "chunk_backfill_required": True},
            )
        if self._looks_like_entity_question(normalized):
            return (
                [QueryMethod.LOCAL, QueryMethod.BASIC],
                "local",
                {"local_graph_required": True, "baseline_backfill_required": True},
            )
        return (
            [QueryMethod.BASIC, QueryMethod.LOCAL],
            "exact_lookup",
            {"baseline_required": True, "local_optional": True},
        )

    def _needs_retrieval(self, request: RetrievalRouterInput) -> bool:
        if request.context_pack.get("draft_only") is True:
            return False
        if request.evidence_state.get("coverage") == 1.0 and not request.fallback_history:
            return False
        normalized = request.query.lower()
        retrieval_keywords = {
            "what",
            "why",
            "which",
            "where",
            "who",
            "contract",
            "policy",
            "evidence",
            "citation",
            "source",
            "research",
            "compare",
            "global",
            "relationship",
            "renewal",
            "drift",
            "changed",
        }
        return any(keyword in normalized for keyword in retrieval_keywords)

    def _looks_like_global(self, normalized_query: str) -> bool:
        global_markers = ("global", "theme", "themes", "across all", "compare", "summarize all")
        return any(marker in normalized_query for marker in global_markers)

    def _looks_like_entity_question(self, normalized_query: str) -> bool:
        entity_markers = ("relationship", "related", "entity", "obligation", "notice", "clause")
        return any(marker in normalized_query for marker in entity_markers)

    def _looks_like_drift(self, normalized_query: str, fallback_text: str) -> bool:
        drift_markers = ("drift", "changed", "between old and new", "version", "versions")
        return any(marker in normalized_query for marker in drift_markers) or "low_coverage" in fallback_text

    def _fallback_reason(self, fallback_history: list[str]) -> str | None:
        return fallback_history[-1] if fallback_history else None


class FusionStage(BaseModel):
    name: str
    methods: list[QueryMethod]
    purpose: str


class StagedFusionPlan(BaseModel):
    requested_product_mode: ProductMode
    stages: list[FusionStage] = Field(default_factory=list)

    @classmethod
    def from_decision(cls, decision: RetrievalRouterDecision) -> "StagedFusionPlan":
        methods = decision.resolved_methods
        if QueryMethod.GLOBAL in methods:
            return cls(
                requested_product_mode=decision.requested_product_mode,
                stages=[
                    FusionStage(
                        name="community_prior",
                        methods=[QueryMethod.GLOBAL],
                        purpose="derive community-level themes and subquestions",
                    ),
                    FusionStage(
                        name="chunk_evidence_backfill",
                        methods=[
                            method
                            for method in [QueryMethod.LOCAL, QueryMethod.BASIC]
                            if method in methods
                        ],
                        purpose="ground global prior in cited chunks",
                    ),
                ],
            )
        if QueryMethod.DRIFT in methods:
            return cls(
                requested_product_mode=decision.requested_product_mode,
                stages=[
                    FusionStage(
                        name="drift_scan",
                        methods=[QueryMethod.DRIFT],
                        purpose="detect temporal or policy drift",
                    ),
                    FusionStage(
                        name="drift_evidence_backfill",
                        methods=[
                            method
                            for method in [QueryMethod.LOCAL, QueryMethod.BASIC]
                            if method in methods
                        ],
                        purpose="ground drift findings in local and baseline evidence",
                    ),
                ],
            )
        return cls(
            requested_product_mode=decision.requested_product_mode,
            stages=[
                FusionStage(
                    name="direct_evidence",
                    methods=methods,
                    purpose="retrieve chunk-level evidence directly",
                )
            ],
        )

    def to_trace(self) -> dict[str, Any]:
        return {
            "requested_product_mode": self.requested_product_mode.value,
            "global_is_prior_not_chunk_ranker": any(
                stage.name == "community_prior" for stage in self.stages
            ),
            "stages": [
                {
                    "name": stage.name,
                    "methods": [method.value for method in stage.methods],
                    "purpose": stage.purpose,
                }
                for stage in self.stages
            ],
        }


class EvidenceItem(BaseModel):
    evidence_id: str
    document_id: str
    block_id: str
    retrieval_method: QueryMethod
    score: float
    source_span: dict[str, Any] = Field(default_factory=dict)
    citation_label: str
    trust_label: str
    acl_scope: str = "workspace"
    text: str = ""


class EvidenceBundle(BaseModel):
    items: list[EvidenceItem] = Field(default_factory=list)
    dropped_evidence_ids: list[str] = Field(default_factory=list)
    coverage: float = 0.0

    @classmethod
    def from_candidates(
        cls, candidates: Iterable[EvidenceItem], allowed_acl_scopes: set[str]
    ) -> "EvidenceBundle":
        items: list[EvidenceItem] = []
        dropped: list[str] = []
        for candidate in candidates:
            if candidate.acl_scope in allowed_acl_scopes:
                items.append(candidate)
            else:
                dropped.append(candidate.evidence_id)
        coverage = cls._coverage(items)
        return cls(items=items, dropped_evidence_ids=dropped, coverage=coverage)

    @staticmethod
    def _coverage(items: list[EvidenceItem]) -> float:
        if not items:
            return 0.0
        covered = sum(1 for item in items if item.citation_label and item.source_span)
        return covered / len(items)


class Citation(BaseModel):
    label: str
    evidence_id: str
    document_id: str
    block_id: str
    source_span: dict[str, Any] = Field(default_factory=dict)
    trust_label: str


class CitationBuilder:
    def build(self, evidence_bundle: EvidenceBundle) -> list[Citation]:
        return [
            Citation(
                label=item.citation_label,
                evidence_id=item.evidence_id,
                document_id=item.document_id,
                block_id=item.block_id,
                source_span=dict(item.source_span),
                trust_label=item.trust_label,
            )
            for item in evidence_bundle.items
            if item.citation_label and item.source_span
        ]


class UnsupportedClaimCheck(BaseModel):
    unsupported_claims: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)


class UnsupportedClaimChecker:
    def check(self, claims: Iterable[str], evidence_bundle: EvidenceBundle) -> UnsupportedClaimCheck:
        evidence_text = "\n".join(item.text for item in evidence_bundle.items).lower()
        unsupported = [
            claim
            for claim in claims
            if claim.lower().strip() and claim.lower().strip() not in evidence_text
        ]
        return UnsupportedClaimCheck(
            unsupported_claims=unsupported,
            recommended_actions=(
                [
                    "rewrite",
                    "retrieve_more",
                    "evidence_limited_answer",
                    "block_high_risk_confident_wording",
                ]
                if unsupported
                else []
            ),
        )


class AgenticRetrievalRuntimeRequest(BaseModel):
    query: str
    workspace_id: str
    knowledge_space_ids: list[str] = Field(default_factory=list)
    product_mode: ProductMode = ProductMode.AUTO
    context_pack: dict[str, Any] = Field(default_factory=dict)
    budget: dict[str, Any] = Field(default_factory=dict)
    allowed_acl_scopes: set[str] = Field(default_factory=lambda: {"workspace"})
    evidence_state: dict[str, Any] = Field(default_factory=dict)
    fallback_history: list[str] = Field(default_factory=list)
    claims: list[str] = Field(default_factory=list)
    trace_id: str
    task_id: str


class AgenticRetrievalRuntimeResult(BaseModel):
    answer: str
    decision: RetrievalRouterDecision
    fusion_plan: StagedFusionPlan
    evidence_bundle: EvidenceBundle
    citations: list[Citation] = Field(default_factory=list)
    unsupported_claim_check: UnsupportedClaimCheck
    trace: AgenticGraphRAGTrace
    index_payloads: list[dict[str, Any]] = Field(default_factory=list)
    trace_metadata: dict[str, Any] = Field(default_factory=dict)

    def to_task_event(self) -> dict[str, Any]:
        trace = self.trace.to_dict()
        runtime_trace_events = [
            dict(event)
            for event in self.trace_metadata.get("runtime_trace_events", [])
            if isinstance(event, dict)
        ]
        return {
            "type": "retrieval",
            "status": "completed" if self.decision.retrieval_required else "skipped",
            "payload": {
                "status": "completed" if self.decision.retrieval_required else "skipped",
                "message": "Retrieved cited evidence." if self.decision.retrieval_required else "No retrieval required.",
                "resolved_methods": [method.value for method in self.decision.resolved_methods],
                "candidate_methods": [method.value for method in self.decision.candidate_methods],
                "router_decision": self.decision.router_decision,
                "fallback_reason": self.decision.fallback_reason or self.trace_metadata.get("fallback_reason"),
                "no_retrieval_reason": self.decision.no_retrieval_reason,
                "evidence_coverage": trace["evidence_coverage"],
                "citation_coverage": trace["citation_coverage"],
                "citation_ids": [citation.label for citation in self.citations],
                "unsupported_claims": list(self.unsupported_claim_check.unsupported_claims),
                "dropped_evidence_ids": list(self.evidence_bundle.dropped_evidence_ids),
                "evidence_verdict": dict(self.trace_metadata.get("evidence_verdict") or {}),
                "artifact_manifest": dict(self.trace_metadata.get("artifact_manifest") or {}),
                "runtime_trace_event_ids": [
                    str(event.get("event_id"))
                    for event in runtime_trace_events
                    if event.get("event_id")
                ],
                "retrievers_used": sorted(
                    {
                        retriever
                        for payload in self.index_payloads
                        for retriever in payload.get("retrievers_used", [])
                    }
                ),
            },
        }


class AgenticRetrievalRuntime:
    """PHASE09 runtime bridge from Agentic Router to local index jobs."""

    def __init__(self, *, index_runtime: Any) -> None:
        self.index_runtime = index_runtime
        self.router = AgenticRetrievalRouter()
        self.citation_builder = CitationBuilder()
        self.claim_checker = UnsupportedClaimChecker()

    def answer(self, request: AgenticRetrievalRuntimeRequest) -> AgenticRetrievalRuntimeResult:
        decision = self.router.decide(
            RetrievalRouterInput(
                query=request.query,
                workspace_id=request.workspace_id,
                context_pack=request.context_pack,
                product_mode=request.product_mode,
                budget=request.budget,
                acl_scope={"workspace_id": request.workspace_id},
                evidence_state=request.evidence_state,
                fallback_history=request.fallback_history,
                trace_id=request.trace_id,
                task_id=request.task_id,
            )
        )
        fusion_plan = StagedFusionPlan.from_decision(decision)
        if not decision.retrieval_required:
            empty_bundle = EvidenceBundle()
            unsupported = UnsupportedClaimCheck()
            trace = AgenticGraphRAGTrace.from_decision(
                decision=decision,
                evidence_bundle=empty_bundle,
                citations=[],
                unsupported_claims=[],
            )
            return AgenticRetrievalRuntimeResult(
                answer="No retrieval was required for this request.",
                decision=decision,
                fusion_plan=fusion_plan,
                evidence_bundle=empty_bundle,
                citations=[],
                unsupported_claim_check=unsupported,
                trace=trace,
                index_payloads=[],
                trace_metadata=self._trace_metadata(
                    request=request,
                    decision=decision,
                    evidence_bundle=empty_bundle,
                    citations=[],
                    answer="No retrieval was required for this request.",
                    index_payloads=[],
                ),
            )

        index_payloads = [
            self.index_runtime.to_retrieval_payload(knowledge_space_id, request.query)
            for knowledge_space_id in request.knowledge_space_ids
        ]
        candidates = self._evidence_candidates(
            decision=decision,
            index_payloads=index_payloads,
        )
        bundle = EvidenceBundle.from_candidates(candidates, request.allowed_acl_scopes)
        citations = self.citation_builder.build(bundle)
        unsupported = self.claim_checker.check(request.claims, bundle)
        trace = AgenticGraphRAGTrace.from_decision(
            decision=decision,
            evidence_bundle=bundle,
            citations=citations,
            unsupported_claims=unsupported.unsupported_claims,
        )
        answer = self._answer_from_evidence(bundle, citations)
        return AgenticRetrievalRuntimeResult(
            answer=answer,
            decision=decision,
            fusion_plan=fusion_plan,
            evidence_bundle=bundle,
            citations=citations,
            unsupported_claim_check=unsupported,
            trace=trace,
            index_payloads=index_payloads,
            trace_metadata=self._trace_metadata(
                request=request,
                decision=decision,
                evidence_bundle=bundle,
                citations=citations,
                answer=answer,
                index_payloads=index_payloads,
            ),
        )

    def _evidence_candidates(
        self,
        *,
        decision: RetrievalRouterDecision,
        index_payloads: list[dict[str, Any]],
    ) -> list[EvidenceItem]:
        candidates: list[EvidenceItem] = []
        seen_chunks: set[str] = set()
        citation_index = 1
        for method in decision.resolved_methods:
            for payload in index_payloads:
                for source_name in self._sources_for_method(method):
                    for document in payload.get("documents_by_source", {}).get(source_name, []):
                        chunk_id = str(document.get("chunk_id") or "")
                        if not chunk_id or chunk_id in seen_chunks:
                            continue
                        if float(document.get("score") or 0.0) <= 0:
                            continue
                        metadata = dict(document.get("metadata") or {})
                        seen_chunks.add(chunk_id)
                        candidates.append(
                            EvidenceItem(
                                evidence_id=f"ev:{method.value}:{chunk_id}",
                                document_id=str(document.get("document_id") or metadata.get("document_id") or ""),
                                block_id=chunk_id.split("::", 1)[-1],
                                retrieval_method=method,
                                score=float(document.get("score") or 0.0),
                                source_span=dict(metadata.get("source_span") or {}),
                                citation_label=f"[{citation_index}]",
                                trust_label=str(metadata.get("trust_label") or "indexed"),
                                acl_scope=str(metadata.get("acl_scope") or "workspace"),
                                text=str(document.get("content") or ""),
                            )
                        )
                        citation_index += 1
        return candidates

    @staticmethod
    def _sources_for_method(method: QueryMethod) -> tuple[str, ...]:
        if method is QueryMethod.BASIC:
            return ("bm25",)
        if method is QueryMethod.LOCAL:
            return ("graph", "vector")
        if method is QueryMethod.GLOBAL:
            return ("graph",)
        if method is QueryMethod.DRIFT:
            return ("bm25", "graph")
        return ("bm25",)

    def _trace_metadata(
        self,
        *,
        request: AgenticRetrievalRuntimeRequest,
        decision: RetrievalRouterDecision,
        evidence_bundle: EvidenceBundle,
        citations: list[Citation],
        answer: str,
        index_payloads: list[dict[str, Any]],
    ) -> dict[str, Any]:
        from zuno.knowledge.trace import enrich_trace_metadata_with_artifacts

        evidence_refs = [_evidence_ref(item) for item in evidence_bundle.items]
        citation_refs = [_citation_ref(citation) for citation in citations]
        metadata = {
            **decision.to_trace(),
            "requested_product_mode": decision.requested_product_mode.value,
            "resolved_product_mode": decision.requested_product_mode.value,
            "requested_query_method": ",".join(method.value for method in decision.candidate_methods),
            "resolved_query_method": ",".join(method.value for method in decision.resolved_methods),
            "retrievers_used": sorted(
                {
                    retriever
                    for payload in index_payloads
                    for retriever in payload.get("retrievers_used", [])
                }
            ),
            "evidence_bundle": {
                "document_count": len(evidence_bundle.items),
                "chunk_ids": evidence_refs,
                "citation_chunks": citation_refs,
                "citation_coverage": (
                    len(citation_refs) / len(evidence_bundle.items)
                    if evidence_bundle.items
                    else 0.0
                ),
                "dropped_evidence_ids": list(evidence_bundle.dropped_evidence_ids),
            },
            "citation_chunks": citation_refs,
            "pipeline_trace": {
                "steps": [
                    {
                        "name": "agentic_retrieval",
                        "status": "completed" if decision.retrieval_required else "skipped",
                        "detail": {
                            "router_decision": decision.router_decision,
                            "resolved_methods": [method.value for method in decision.resolved_methods],
                        },
                    }
                ]
            },
        }
        return enrich_trace_metadata_with_artifacts(
            trace_metadata=metadata,
            query=request.query,
            answer=answer,
            documents=[
                {
                    "chunk_id": ref,
                    "document_id": item.document_id,
                    "block_id": item.block_id,
                    "source_type": item.retrieval_method.value,
                }
                for item, ref in zip(evidence_bundle.items, evidence_refs)
            ],
            evidence_bundle=metadata["evidence_bundle"],
            citations=citation_refs,
            fallback_reason=decision.fallback_reason,
        )

    @staticmethod
    def _answer_from_evidence(bundle: EvidenceBundle, citations: list[Citation]) -> str:
        if not bundle.items:
            return "No indexed evidence matched this request."
        citation_by_evidence = {citation.evidence_id: citation.label for citation in citations}
        lines = [
            f"{item.text} {citation_by_evidence.get(item.evidence_id, item.citation_label)}"
            for item in bundle.items
        ]
        return "\n".join(lines)


def _evidence_ref(item: EvidenceItem) -> str:
    return f"{item.document_id}::{item.block_id}"


def _citation_ref(citation: Citation) -> str:
    return f"{citation.document_id}::{citation.block_id}"


class GraphRAGIndexPipelineContract(BaseModel):
    input_document_id: str
    workspace_id: str
    text_units: list[dict[str, Any]] = Field(default_factory=list)
    pipeline_steps: list[str] = Field(default_factory=list)
    index_manifest: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_document_ir(cls, document: CanonicalDocumentIR) -> "GraphRAGIndexPipelineContract":
        text_units = [
            {
                "text_unit_id": f"{document.metadata.document_id}::{block.block_id}",
                "document_id": document.metadata.document_id,
                "block_id": block.block_id,
                "text": block.text,
                "source_span": block.source_span.model_dump(),
                "acl_scope": block.acl_scope,
                "sensitivity_tags": list(block.sensitivity_tags),
            }
            for block in document.blocks
        ]
        steps = [
            "document_ir",
            "text_unit",
            "entity_relation_extraction",
            "entity_resolution",
            "graph_upsert",
            "community_detection",
            "community_report",
            "embeddings_search_index",
            "index_manifest",
        ]
        return cls(
            input_document_id=document.metadata.document_id,
            workspace_id=document.metadata.workspace_id,
            text_units=text_units,
            pipeline_steps=steps,
            index_manifest={
                "document_id": document.metadata.document_id,
                "workspace_id": document.metadata.workspace_id,
                "text_unit_count": len(text_units),
                "requires_source_spans": True,
                "pipeline_steps": steps,
            },
        )


class AgenticGraphRAGTrace(BaseModel):
    requested_product_mode: ProductMode
    router_decision: str
    candidate_methods: list[QueryMethod] = Field(default_factory=list)
    resolved_methods: list[QueryMethod] = Field(default_factory=list)
    fallback_reason: str | None = None
    evidence_coverage: float = 0.0
    citation_coverage: float = 0.0
    unsupported_claims: list[str] = Field(default_factory=list)
    trace_id: str
    task_id: str

    @classmethod
    def from_decision(
        cls,
        *,
        decision: RetrievalRouterDecision,
        evidence_bundle: EvidenceBundle,
        citations: list[Citation],
        unsupported_claims: list[str] | None = None,
    ) -> "AgenticGraphRAGTrace":
        citation_coverage = len(citations) / len(evidence_bundle.items) if evidence_bundle.items else 0.0
        return cls(
            requested_product_mode=decision.requested_product_mode,
            router_decision=decision.router_decision,
            candidate_methods=decision.candidate_methods,
            resolved_methods=decision.resolved_methods,
            fallback_reason=decision.fallback_reason,
            evidence_coverage=evidence_bundle.coverage,
            citation_coverage=citation_coverage,
            unsupported_claims=unsupported_claims or [],
            trace_id=decision.trace_id,
            task_id=decision.task_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_product_mode": self.requested_product_mode.value,
            "router_decision": self.router_decision,
            "candidate_methods": [method.value for method in self.candidate_methods],
            "resolved_methods": [method.value for method in self.resolved_methods],
            "fallback_reason": self.fallback_reason,
            "evidence_coverage": self.evidence_coverage,
            "citation_coverage": self.citation_coverage,
            "unsupported_claims": list(self.unsupported_claims),
            "trace_id": self.trace_id,
            "task_id": self.task_id,
        }


__all__ = [
    "AgenticGraphRAGTrace",
    "AgenticRetrievalRuntime",
    "AgenticRetrievalRuntimeRequest",
    "AgenticRetrievalRuntimeResult",
    "AgenticRetrievalRouter",
    "Citation",
    "CitationBuilder",
    "EvidenceBundle",
    "EvidenceItem",
    "FusionStage",
    "GraphRAGIndexPipelineContract",
    "ProductMode",
    "QueryMethod",
    "RetrievalRouterDecision",
    "RetrievalRouterInput",
    "StagedFusionPlan",
    "UnsupportedClaimCheck",
    "UnsupportedClaimChecker",
]
