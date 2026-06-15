from __future__ import annotations

from typing import NotRequired, TypedDict


class DomainQAState(TypedDict):
    user_id: str
    agent_id: str
    dialog_id: str
    query: str
    domain_pack_id: str | None
    knowledge_ids: list[str]
    runtime_settings: NotRequired[dict | None]
    domain_pack: NotRequired[dict | None]
    intent: NotRequired[str | None]
    rewritten_queries: NotRequired[list[str]]
    processed_query: NotRequired[dict | None]
    retrieval_plan: NotRequired[dict | None]
    retrieval_rounds: NotRequired[list[dict]]
    retriever_runs: NotRequired[list[dict]]
    documents_by_source: NotRequired[dict[str, list[dict]]]
    retrieval_result: NotRequired[dict | None]
    vector_contexts: NotRequired[list[dict]]
    graph_paths: NotRequired[list[dict]]
    graph_path_strings: NotRequired[list[str]]
    tool_results: NotRequired[list[dict]]
    evidence_bundle: NotRequired[dict]
    evidence_quality: NotRequired[dict]
    fallback_decision: NotRequired[dict | None]
    support_verdict: NotRequired[dict]
    draft_answer: NotRequired[str | None]
    report_markdown: NotRequired[str | None]
    citations: NotRequired[list[dict]]
    final_answer: NotRequired[str | None]
    trace_metadata: NotRequired[dict]
    cost_metadata: NotRequired[dict]
    status: NotRequired[str]
    failure_metadata: NotRequired[dict | None]


class MultiAgentSupervisorState(TypedDict):
    user_id: str
    agent_id: str
    dialog_id: str
    query: str
    domain_pack_id: str | None
    knowledge_ids: list[str]
    runtime_settings: NotRequired[dict | None]
    domain_pack: NotRequired[dict | None]
    planned_agents: NotRequired[list[str]]
    specialist_outputs: NotRequired[list[dict]]
    vector_contexts: NotRequired[list[dict]]
    graph_paths: NotRequired[list[dict]]
    citations: NotRequired[list[dict]]
    evidence_bundle: NotRequired[dict]
    support_verdict: NotRequired[dict]
    draft_answer: NotRequired[str | None]
    report_markdown: NotRequired[str | None]
    final_answer: NotRequired[str | None]
    trace_metadata: NotRequired[dict]
    cost_metadata: NotRequired[dict]
    status: NotRequired[str]
    failure_metadata: NotRequired[dict | None]
