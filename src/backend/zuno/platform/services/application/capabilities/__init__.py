from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable


class CapabilityType(StrEnum):
    KNOWLEDGE = "Knowledge"
    ACTION_TOOL = "ActionTool"
    MCP_TOOL = "MCPTool"
    MCP_RESOURCE = "MCPResource"
    MCP_PROMPT = "MCPPrompt"
    SKILL = "Skill"


class CapabilityHealth(StrEnum):
    READY = "ready"
    DEGRADED = "degraded"
    NEEDS_CONFIG = "needs_config"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class CapabilityPermissions:
    scopes: tuple[str, ...] = ()
    side_effects: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scopes": list(self.scopes),
            "side_effects": self.side_effects,
        }


@dataclass(frozen=True, slots=True)
class CapabilityCost:
    token_estimate: int = 0
    latency_ms: int | None = None
    unit_cost: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "token_estimate": self.token_estimate,
            "latency_ms": self.latency_ms,
            "unit_cost": self.unit_cost,
        }


@dataclass(frozen=True, slots=True)
class CapabilityRecord:
    name: str
    type: CapabilityType
    description: str
    schema: dict[str, Any]
    permissions: CapabilityPermissions
    cost: CapabilityCost
    health: CapabilityHealth
    source: str
    owner: str
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "schema": dict(self.schema),
            "permissions": self.permissions.to_dict(),
            "cost": self.cost.to_dict(),
            "health": self.health.value,
            "source": self.source,
            "owner": self.owner,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ToolCard:
    id: str
    name: str
    aliases: tuple[str, ...]
    type: CapabilityType
    description: str
    input_schema_summary: str
    output_schema_summary: str
    permissions: CapabilityPermissions
    cost_hint: CapabilityCost
    health: CapabilityHealth
    owner_module: str
    source: str
    tags: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def side_effects(self) -> bool:
        return self.permissions.side_effects

    @classmethod
    def from_capability_record(cls, record: CapabilityRecord) -> ToolCard:
        aliases = _string_tuple(record.metadata.get("aliases", ()))
        examples = _string_tuple(record.metadata.get("examples", ()))
        return cls(
            id=str(record.metadata.get("tool_card_id") or f"{record.type.value}:{record.name}"),
            name=record.name,
            aliases=aliases,
            type=record.type,
            description=record.description,
            input_schema_summary=_summarize_schema(record.schema),
            output_schema_summary=str(record.metadata.get("output_schema_summary") or ""),
            permissions=record.permissions,
            cost_hint=record.cost,
            health=record.health,
            owner_module=record.owner,
            source=record.source,
            tags=tuple(record.tags),
            examples=examples,
            metadata=dict(record.metadata),
        )

    def searchable_text(self) -> str:
        return " ".join(
            [
                self.id,
                self.name,
                " ".join(self.aliases),
                self.type.value,
                self.description,
                self.input_schema_summary,
                self.output_schema_summary,
                self.owner_module,
                self.source,
                " ".join(self.tags),
                " ".join(self.examples),
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "aliases": list(self.aliases),
            "type": self.type.value,
            "description": self.description,
            "input_schema_summary": self.input_schema_summary,
            "output_schema_summary": self.output_schema_summary,
            "permissions": self.permissions.to_dict(),
            "side_effects": self.side_effects,
            "cost_hint": self.cost_hint.to_dict(),
            "latency_hint": self.cost_hint.latency_ms,
            "health": self.health.value,
            "examples": list(self.examples),
            "owner_module": self.owner_module,
            "source": self.source,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }


class CapabilityRegistry:
    def __init__(self, capabilities: Iterable[CapabilityRecord] = ()) -> None:
        self._records: dict[str, CapabilityRecord] = {}
        for capability in capabilities:
            self.register(capability)

    def register(self, capability: CapabilityRecord) -> None:
        self._records[capability.name] = capability

    def list(self) -> tuple[CapabilityRecord, ...]:
        return tuple(self._records.values())


class ToolCardRegistry:
    def __init__(self, cards: Iterable[ToolCard] = ()) -> None:
        self._cards: dict[str, ToolCard] = {}
        for card in cards:
            self.register(card)

    @classmethod
    def from_capability_records(cls, capabilities: Iterable[CapabilityRecord]) -> ToolCardRegistry:
        return cls(ToolCard.from_capability_record(capability) for capability in capabilities)

    def register(self, card: ToolCard) -> None:
        self._cards[card.id] = card

    def get(self, card_id: str) -> ToolCard | None:
        return self._cards.get(card_id)

    def list(self) -> tuple[ToolCard, ...]:
        return tuple(self._cards.values())


@dataclass(frozen=True, slots=True)
class CapabilitySelectionRequest:
    task: str
    allowed_types: tuple[CapabilityType, ...] = tuple(CapabilityType)
    max_capabilities: int = 8
    required_permissions: tuple[str, ...] = ()
    allow_side_effects: bool = True
    max_token_cost: int | None = None


@dataclass(frozen=True, slots=True)
class NativeBM25SearchResult:
    tool_card_id: str
    score: float
    matched_terms: tuple[str, ...]
    explanation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_card_id": self.tool_card_id,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "explanation": dict(self.explanation),
        }


class NativeBM25Retriever:
    def __init__(self, cards: Iterable[ToolCard], *, k1: float = 1.2, b: float = 0.75) -> None:
        self._cards = tuple(cards)
        self._k1 = k1
        self._b = b
        self._documents = {
            card.id: self._tokens(card.searchable_text())
            for card in self._cards
        }
        self._doc_lengths = {
            card_id: len(tokens) or 1
            for card_id, tokens in self._documents.items()
        }
        self._avg_doc_len = (
            sum(self._doc_lengths.values()) / len(self._doc_lengths)
            if self._doc_lengths
            else 1.0
        )
        self._document_frequency = self._build_document_frequency()

    def search(self, query: str, *, top_k: int = 8) -> tuple[NativeBM25SearchResult, ...]:
        query_terms = self._tokens(query)
        if not query_terms:
            return ()
        results = [
            self._score_card(card_id=card.id, query_terms=query_terms)
            for card in self._cards
        ]
        scored = [result for result in results if result.score > 0]
        scored.sort(key=lambda result: (result.score, result.tool_card_id), reverse=True)
        return tuple(scored[: max(1, top_k)])

    def _score_card(self, *, card_id: str, query_terms: tuple[str, ...]) -> NativeBM25SearchResult:
        doc_terms = self._documents.get(card_id, ())
        doc_len = self._doc_lengths.get(card_id, 1)
        matched_terms: list[str] = []
        term_scores: dict[str, float] = {}
        total = 0.0
        for term in query_terms:
            term_frequency = doc_terms.count(term)
            if term_frequency == 0:
                continue
            matched_terms.append(term)
            idf = self._idf(term)
            numerator = term_frequency * (self._k1 + 1)
            denominator = term_frequency + self._k1 * (
                1 - self._b + self._b * doc_len / self._avg_doc_len
            )
            term_score = idf * numerator / denominator
            term_scores[term] = term_score
            total += term_score
        return NativeBM25SearchResult(
            tool_card_id=card_id,
            score=round(total, 6),
            matched_terms=tuple(dict.fromkeys(matched_terms)),
            explanation={
                "algorithm": "native_bm25",
                "k1": self._k1,
                "b": self._b,
                "doc_len": doc_len,
                "avg_doc_len": self._avg_doc_len,
                "term_scores": term_scores,
            },
        )

    def _build_document_frequency(self) -> dict[str, int]:
        document_frequency: dict[str, int] = {}
        for terms in self._documents.values():
            for term in set(terms):
                document_frequency[term] = document_frequency.get(term, 0) + 1
        return document_frequency

    def _idf(self, term: str) -> float:
        document_count = len(self._documents) or 1
        frequency = self._document_frequency.get(term, 0)
        return math.log((document_count - frequency + 0.5) / (frequency + 0.5) + 1)

    @classmethod
    def _tokens(cls, text: str) -> tuple[str, ...]:
        lowered = (text or "").lower()
        raw_tokens = [
            token
            for token in re.split(r"[^0-9a-zA-Z_\u4e00-\u9fff]+", lowered)
            if token
        ]
        tokens: list[str] = []
        for token in raw_tokens:
            tokens.append(token)
            if re.search(r"[\u4e00-\u9fff]", token):
                tokens.extend(token[index:index + 2] for index in range(max(0, len(token) - 1)))
        return tuple(dict.fromkeys(token for token in tokens if len(token) > 1))


@dataclass(frozen=True, slots=True)
class CapabilityPolicyDecision:
    tool_card_id: str
    allowed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_card_id": self.tool_card_id,
            "allowed": self.allowed,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class CapabilitySelectionTrace:
    selected_names: tuple[str, ...]
    dropped_names: tuple[str, ...]
    selection_reasons: dict[str, str]
    scores: dict[str, float]
    candidate_tool_card_ids: tuple[str, ...] = ()
    retrieval_scores: dict[str, float] = field(default_factory=dict)
    filters_applied: tuple[str, ...] = ()
    selected_tool_card_ids: tuple[str, ...] = ()
    rejected_tool_card_ids: dict[str, str] = field(default_factory=dict)
    injected_schema_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_names": list(self.selected_names),
            "dropped_names": list(self.dropped_names),
            "selection_reasons": dict(self.selection_reasons),
            "scores": dict(self.scores),
            "candidate_tool_card_ids": list(self.candidate_tool_card_ids),
            "retrieval_scores": dict(self.retrieval_scores),
            "filters_applied": list(self.filters_applied),
            "selected_tool_card_ids": list(self.selected_tool_card_ids),
            "rejected_tool_card_ids": dict(self.rejected_tool_card_ids),
            "injected_schema_ids": list(self.injected_schema_ids),
        }


@dataclass(frozen=True, slots=True)
class CapabilitySelectionResult:
    capabilities: tuple[CapabilityRecord, ...]
    trace: CapabilitySelectionTrace

    def tool_schemas(self) -> dict[str, dict[str, Any]]:
        return {
            capability.name: dict(capability.schema)
            for capability in self.capabilities
            if capability.type in {
                CapabilityType.ACTION_TOOL,
                CapabilityType.MCP_TOOL,
                CapabilityType.SKILL,
            }
        }


class DynamicCapabilitySelector:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    def select(self, request: CapabilitySelectionRequest) -> CapabilitySelectionResult:
        capabilities = self._registry.list()
        cards_by_name = {
            capability.name: ToolCard.from_capability_record(capability)
            for capability in capabilities
        }
        cards_by_id = {card.id: card for card in cards_by_name.values()}
        search_results = NativeBM25Retriever(cards_by_id.values()).search(
            request.task,
            top_k=max(1, len(cards_by_id)),
        )
        search_score_by_id = {
            result.tool_card_id: result.score
            for result in search_results
        }
        ordered_card_ids = [
            *[result.tool_card_id for result in search_results],
            *[
                card.id
                for card in cards_by_name.values()
                if card.id not in search_score_by_id
            ],
        ]
        capability_by_card_id = {
            cards_by_name[capability.name].id: capability
            for capability in capabilities
        }

        allowed_types = set(request.allowed_types)
        required_permissions = set(request.required_permissions)
        scored: list[tuple[float, CapabilityRecord, ToolCard]] = []
        dropped: list[str] = []
        reasons: dict[str, str] = {}
        scores: dict[str, float] = {}
        rejected_tool_card_ids: dict[str, str] = {}
        filters_applied = (
            "type",
            "health",
            "permission",
            "side_effect",
            "cost",
            "task_relevance",
        )

        for card_id in ordered_card_ids:
            capability = capability_by_card_id[card_id]
            card = cards_by_id[card_id]
            score = search_score_by_id.get(card_id, 0.0)
            scores[capability.name] = score
            if capability.type not in allowed_types:
                self._drop(
                    capability=capability,
                    card=card,
                    reason="type_not_allowed",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )
                continue
            if capability.health is CapabilityHealth.DISABLED:
                self._drop(
                    capability=capability,
                    card=card,
                    reason="disabled",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )
                continue
            if capability.health is CapabilityHealth.NEEDS_CONFIG:
                self._drop(
                    capability=capability,
                    card=card,
                    reason="needs_config",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )
                continue
            if not required_permissions.issubset(set(capability.permissions.scopes)):
                self._drop(
                    capability=capability,
                    card=card,
                    reason="permission_not_allowed",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )
                continue
            if capability.permissions.side_effects and not request.allow_side_effects:
                self._drop(
                    capability=capability,
                    card=card,
                    reason="side_effect_not_allowed",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )
                continue
            if request.max_token_cost is not None and capability.cost.token_estimate > request.max_token_cost:
                self._drop(
                    capability=capability,
                    card=card,
                    reason="cost_exceeds_budget",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )
                continue
            if score <= 0:
                self._drop(
                    capability=capability,
                    card=card,
                    reason="no_task_match",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )
                continue
            scored.append((score, capability, card))
            reasons[capability.name] = "task_match"

        scored.sort(
            key=lambda item: (
                item[0],
                -item[1].cost.token_estimate,
                item[1].name,
            ),
            reverse=True,
        )
        selected_entries = tuple(scored[: max(1, request.max_capabilities)])
        selected = tuple(item[1] for item in selected_entries)
        selected_names = {item.name for item in selected}
        for _, capability, card in scored:
            if capability.name not in selected_names:
                self._drop(
                    capability=capability,
                    card=card,
                    reason="selection_limit",
                    dropped=dropped,
                    reasons=reasons,
                    rejected_tool_card_ids=rejected_tool_card_ids,
                )

        return CapabilitySelectionResult(
            capabilities=selected,
            trace=CapabilitySelectionTrace(
                selected_names=tuple(capability.name for capability in selected),
                dropped_names=tuple(dict.fromkeys(dropped)),
                selection_reasons=reasons,
                scores=scores,
                candidate_tool_card_ids=tuple(ordered_card_ids),
                retrieval_scores={
                    card_id: search_score_by_id.get(card_id, 0.0)
                    for card_id in ordered_card_ids
                },
                filters_applied=filters_applied,
                selected_tool_card_ids=tuple(item[2].id for item in selected_entries),
                rejected_tool_card_ids=rejected_tool_card_ids,
                injected_schema_ids=tuple(
                    capability.name
                    for capability in selected
                    if capability.type in {
                        CapabilityType.ACTION_TOOL,
                        CapabilityType.MCP_TOOL,
                        CapabilityType.SKILL,
                    }
                ),
            ),
        )

    @staticmethod
    def _drop(
        *,
        capability: CapabilityRecord,
        card: ToolCard,
        reason: str,
        dropped: list[str],
        reasons: dict[str, str],
        rejected_tool_card_ids: dict[str, str],
    ) -> None:
        dropped.append(capability.name)
        reasons[capability.name] = reason
        rejected_tool_card_ids[card.id] = reason


__all__ = [
    "CapabilityCost",
    "CapabilityHealth",
    "CapabilityPermissions",
    "CapabilityPolicyDecision",
    "CapabilityRecord",
    "CapabilityRegistry",
    "CapabilitySelectionRequest",
    "CapabilitySelectionResult",
    "CapabilitySelectionTrace",
    "CapabilityType",
    "DynamicCapabilitySelector",
    "NativeBM25Retriever",
    "NativeBM25SearchResult",
    "ToolCard",
    "ToolCardRegistry",
]


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value if str(item))
    return ()


def _summarize_schema(schema: dict[str, Any]) -> str:
    if not schema:
        return ""
    schema_type = str(schema.get("type") or "")
    properties = schema.get("properties")
    if isinstance(properties, dict) and properties:
        names = ", ".join(str(name) for name in sorted(properties))
        return f"{schema_type or 'object'}: {names}"
    if schema_type:
        return schema_type
    return ", ".join(str(key) for key in sorted(schema))
