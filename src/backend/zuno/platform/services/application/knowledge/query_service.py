from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from zuno.services.graphrag.models import GraphRAGExtractorConfig
from zuno.services.graphrag.project.loader import GraphRAGProjectLoader
from zuno.services.graphrag.prompts.registry import GraphRAGPromptRegistry
from zuno.services.graphrag.query_service import (
    GraphRAGProjectSnapshot,
    GraphRAGQueryService,
    KnowledgeQueryResult,
)
from zuno.knowledge.agentic.contracts import (
    CorrectiveAction,
    EvidenceCoverageSummary,
    EvidenceFrontier,
    KnowledgeControlProposal,
    KnowledgeControlProposalType,
    KnowledgeRetrievalGraphNode,
    KnowledgeRetrievalGraphTrace,
    KnowledgeRetrievalProfile,
    RetrieverKind,
)


ConfigLoader = Callable[[str], Awaitable[dict[str, Any]]]


async def _default_config_loader(knowledge_id: str) -> dict[str, Any]:
    from zuno.api.services.knowledge import KnowledgeService

    return await KnowledgeService.get_knowledge_config(knowledge_id)


class KnowledgeQueryService:
    def __init__(
        self,
        *,
        config_loader: ConfigLoader | None = None,
        project_loader: GraphRAGProjectLoader | None = None,
        query_service: GraphRAGQueryService | None = None,
    ):
        self.config_loader = config_loader or _default_config_loader
        self.project_loader = project_loader or GraphRAGProjectLoader()
        self.query_service = query_service or GraphRAGQueryService()

    async def query(
        self,
        *,
        user_id: str,
        knowledge_ids: list[str],
        query: str,
        product_mode: str | None = None,
        query_method: str | None = None,
        top_k: int | None = None,
    ) -> KnowledgeQueryResult:
        if not knowledge_ids:
            raise ValueError("knowledge_ids is required")
        snapshot = await self.build_project_snapshot(
            user_id=user_id,
            knowledge_id=knowledge_ids[0],
        )
        result = await self.query_service.query(
            query=query,
            knowledge_ids=knowledge_ids,
            snapshot=snapshot,
            product_mode=product_mode,
            query_method=query_method,
            top_k=top_k,
        )
        return _with_phase18_application_trace(
            result=result,
            snapshot=snapshot,
            user_id=user_id,
            knowledge_ids=knowledge_ids,
            query=query,
            product_mode=product_mode,
            query_method=query_method,
        )

    async def build_project_snapshot(
        self,
        *,
        user_id: str,
        knowledge_id: str,
    ) -> GraphRAGProjectSnapshot:
        del user_id
        config = dict(await self.config_loader(knowledge_id) or {})
        project_config = dict(config.get("graphrag_project") or {})
        project_id = config.get("graphrag_project_id") or project_config.get("graphrag_project_id")
        project = self.project_loader.load(project_id) if project_id else None

        contract = dict(project.contract.model_dump() if project else project_config)
        readiness = dict(project.readiness.to_dict() if project else {})
        prompt_categories: list[str] = []
        query_policy: dict[str, Any] = {}
        settings: dict[str, Any] = {}
        if project:
            prompt_registry = GraphRAGPromptRegistry.from_project(project)
            prompt_categories = prompt_registry.categories()
            settings = dict(project.settings)
            query_policy = dict(settings.get("query_policy") or settings.get("retrieval_policy") or {})

        retrieval_settings = dict(config.get("retrieval_settings") or {})
        index_settings = dict(config.get("index_settings") or {})
        graph_settings = dict(config.get("graph_index_settings") or {})
        model_refs = dict(config.get("model_refs") or {})
        prompt_refs = dict(config.get("prompt_refs") or {})
        schema_refs = dict(config.get("schema_refs") or {})
        policy_refs = dict(config.get("policy_refs") or {})
        eval_refs = dict(config.get("eval_refs") or {})
        if project:
            for name, path in project.prompt_paths.items():
                prompt_refs.setdefault(name, path)
        if config.get("eval_profile_id"):
            eval_refs.setdefault("entity_extraction_eval_profile", config.get("eval_profile_id"))
        extractor_config = GraphRAGExtractorConfig.from_knowledge_config(
            graph_index_settings=graph_settings,
            model_refs=model_refs,
            prompt_refs=prompt_refs,
            schema_refs=schema_refs,
            policy_refs=policy_refs,
            eval_refs=eval_refs,
        )
        community_status = (
            graph_settings.get("community_report_status")
            or graph_settings.get("community_detection_status")
            or "not_built"
        )
        prompt_version = contract.get("prompt_version") or project_config.get("prompt_version") or "default"
        query_prompt_version = contract.get("query_prompt_version") or project_config.get("query_prompt_version") or "default"
        community_version = (
            contract.get("community_version")
            or graph_settings.get("community_version")
            or project_config.get("community_version")
            or "v0"
        )

        return GraphRAGProjectSnapshot(
            graphrag_project_id=str(project_id) if project_id else None,
            contract=contract,
            extractor_config=extractor_config.to_trace(),
            readiness=readiness,
            prompt_categories=prompt_categories,
            retrieval_settings=retrieval_settings,
            index_version={
                "vector": str(index_settings.get("index_version") or "v1"),
                "graph": str(graph_settings.get("index_version") or "v1"),
                "community": str(community_version),
                "prompt": str(prompt_version),
                "query_prompt": str(query_prompt_version),
            },
            index_health={
                "vector": str(index_settings.get("health_status") or "ready"),
                "graph": str(graph_settings.get("health_status") or "ready"),
                "community": str(community_status),
            },
            knowledge_capability=str(config.get("index_capability") or "rag"),
            query_policy=query_policy,
            settings=settings,
        )


def _with_phase18_application_trace(
    *,
    result: KnowledgeQueryResult,
    snapshot: GraphRAGProjectSnapshot,
    user_id: str,
    knowledge_ids: list[str],
    query: str,
    product_mode: str | None,
    query_method: str | None,
) -> KnowledgeQueryResult:
    metadata = dict(result.trace_metadata)
    if metadata.get("phase18_application_query_path"):
        return result
    frontier = _phase18_frontier(result)
    final_action = CorrectiveAction.CONTINUE if not frontier.stop_reasons else CorrectiveAction.ABSTAIN
    proposal_type = (
        KnowledgeControlProposalType.ACCEPT_EVIDENCE
        if final_action is CorrectiveAction.CONTINUE
        else KnowledgeControlProposalType.ABSTAIN
    )
    graph_trace = KnowledgeRetrievalGraphTrace(
        profile=_phase18_profile(result),
        requested_profile=str(query_method or result.requested_query_method or snapshot.default_query_method()),
        snapshot_id=snapshot.graphrag_project_id,
    )
    retrievers = _phase18_retrievers(result)
    graph_trace.add(
        KnowledgeRetrievalGraphNode.VALIDATE,
        status="completed" if query.strip() and knowledge_ids else "blocked",
        payload={"query_present": bool(query.strip()), "knowledge_scope_present": bool(knowledge_ids)},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.PIN_SNAPSHOT,
        status="pinned" if snapshot.graphrag_project_id else "deferred_to_repository",
        payload={"graphrag_project_id": snapshot.graphrag_project_id},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.SCOPE,
        payload={
            "user_id": user_id,
            "knowledge_space_ids": list(knowledge_ids),
            "product_mode": product_mode,
        },
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.INTERPRET,
        payload={"query_method_contract": dict(metadata.get("query_method_contract") or {})},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.SELECT_PROFILE,
        payload={"resolved_query_method": result.resolved_query_method, "selected_profile": graph_trace.profile.value},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.PLAN_ROUND,
        round=1,
        payload={"retrievers": retrievers, "top_k": snapshot.retrieval_settings.get("top_k")},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.ADMIT,
        round=1,
        status="admitted" if knowledge_ids else "blocked",
        payload={"admitted": bool(knowledge_ids), "admission_reason": "admitted" if knowledge_ids else "knowledge_scope_empty"},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.DISPATCH,
        round=1,
        payload={"retrievers": retrievers, "parallel_group": f"application-query:{snapshot.graphrag_project_id or 'default'}"},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.NORMALIZE,
        round=1,
        payload={"document_count": len(result.documents), "citation_count": len(result.citations)},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.FUSE_RERANK,
        round=1,
        payload=dict(metadata.get("retrieval_fusion_contract") or {}),
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.EVIDENCE_LEDGER,
        round=1,
        payload={"frontier": frontier.model_dump(mode="json"), "evidence": dict(result.evidence)},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.EVALUATE,
        round=1,
        payload={
            "verdict": "relevant" if result.documents else "irrelevant",
            "frontier_stop_reasons": list(frontier.stop_reasons),
        },
    )
    graph_trace.proposal = KnowledgeControlProposal(
        proposal_type=proposal_type,
        final_action=final_action,
        reason="application knowledge query produced PHASE18 trace metadata",
        payload={"frontier": frontier.model_dump(mode="json")},
    )
    graph_trace.add(
        KnowledgeRetrievalGraphNode.CORRECTIVE_DECISION,
        round=1,
        payload={
            "corrective_action": final_action.value,
            "proposal_type": proposal_type.value,
            "frontier_stop_reasons": list(frontier.stop_reasons),
        },
    )
    metadata.update(
        {
            "phase18_application_query_path": True,
            "knowledge_retrieval_graph": graph_trace.model_dump(mode="json"),
            "knowledge_control_proposal": graph_trace.proposal.model_dump(mode="json"),
            "evidence_frontier": frontier.model_dump(mode="json"),
        }
    )
    result.trace_metadata = metadata
    return result


def _phase18_profile(result: KnowledgeQueryResult) -> KnowledgeRetrievalProfile:
    resolved = result.resolved_query_method.lower().strip()
    if resolved == "local":
        return KnowledgeRetrievalProfile.LOCAL
    if resolved == "global":
        return KnowledgeRetrievalProfile.GLOBAL
    if resolved == "drift":
        return KnowledgeRetrievalProfile.DRIFT
    if "community" in result.retrievers_used:
        return KnowledgeRetrievalProfile.GLOBAL
    return KnowledgeRetrievalProfile.STANDARD


def _phase18_retrievers(result: KnowledgeQueryResult) -> list[str]:
    mapped: list[str] = []
    for retriever in result.retrievers_used:
        normalized = str(retriever).lower().strip()
        if normalized == "graph":
            normalized = RetrieverKind.RELATION.value
        if normalized in {kind.value for kind in RetrieverKind} and normalized not in mapped:
            mapped.append(normalized)
    return mapped or [RetrieverKind.BM25.value, RetrieverKind.VECTOR.value]


def _phase18_frontier(result: KnowledgeQueryResult) -> EvidenceFrontier:
    document_count = len(result.documents)
    citation_count = len(result.citations)
    stop_reasons: list[str] = []
    if document_count <= 0:
        stop_reasons.append("no_evidence")
    elif citation_count <= 0:
        stop_reasons.append("strict_citation_missing")
    coverage_ratio = 1.0 if document_count and citation_count else 0.0
    return EvidenceFrontier(
        total_records=document_count,
        newest_round=1 if document_count else 0,
        novelty=1.0 if document_count else 0.0,
        missing_strict_citation_ids=[] if citation_count else [str(item.get("chunk_id") or idx) for idx, item in enumerate(result.documents, start=1)],
        stop_reasons=stop_reasons,
        coverage=EvidenceCoverageSummary(
            claim_count=0,
            covered_claim_count=0,
            strict_citation_count=citation_count,
            coverage_ratio=coverage_ratio,
            strict_citation_ratio=coverage_ratio,
        ),
    )


__all__ = ["KnowledgeQueryService"]
