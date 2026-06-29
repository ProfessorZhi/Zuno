from __future__ import annotations

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


class CapabilityRegistry:
    def __init__(self, capabilities: Iterable[CapabilityRecord] = ()) -> None:
        self._records: dict[str, CapabilityRecord] = {}
        for capability in capabilities:
            self.register(capability)

    def register(self, capability: CapabilityRecord) -> None:
        self._records[capability.name] = capability

    def list(self) -> tuple[CapabilityRecord, ...]:
        return tuple(self._records.values())


@dataclass(frozen=True, slots=True)
class CapabilitySelectionRequest:
    task: str
    allowed_types: tuple[CapabilityType, ...] = tuple(CapabilityType)
    max_capabilities: int = 8
    required_permissions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CapabilitySelectionTrace:
    selected_names: tuple[str, ...]
    dropped_names: tuple[str, ...]
    selection_reasons: dict[str, str]
    scores: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_names": list(self.selected_names),
            "dropped_names": list(self.dropped_names),
            "selection_reasons": dict(self.selection_reasons),
            "scores": dict(self.scores),
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
        allowed_types = set(request.allowed_types)
        required_permissions = set(request.required_permissions)
        scored: list[tuple[float, CapabilityRecord]] = []
        dropped: list[str] = []
        reasons: dict[str, str] = {}
        scores: dict[str, float] = {}

        for capability in self._registry.list():
            score = self._score(request.task, capability)
            scores[capability.name] = score
            if capability.type not in allowed_types:
                dropped.append(capability.name)
                reasons[capability.name] = "type_not_allowed"
                continue
            if capability.health is CapabilityHealth.DISABLED:
                dropped.append(capability.name)
                reasons[capability.name] = "disabled"
                continue
            if not required_permissions.issubset(set(capability.permissions.scopes)):
                dropped.append(capability.name)
                reasons[capability.name] = "permission_not_allowed"
                continue
            if score <= 0:
                dropped.append(capability.name)
                reasons[capability.name] = "no_task_match"
                continue
            scored.append((score, capability))
            reasons[capability.name] = "task_match"

        scored.sort(
            key=lambda item: (
                item[0],
                -item[1].cost.token_estimate,
                item[1].name,
            ),
            reverse=True,
        )
        selected = tuple(item[1] for item in scored[: max(1, request.max_capabilities)])
        selected_names = {item.name for item in selected}
        for _, capability in scored:
            if capability.name not in selected_names:
                dropped.append(capability.name)
                reasons[capability.name] = "selection_limit"

        return CapabilitySelectionResult(
            capabilities=selected,
            trace=CapabilitySelectionTrace(
                selected_names=tuple(capability.name for capability in selected),
                dropped_names=tuple(dict.fromkeys(dropped)),
                selection_reasons=reasons,
                scores=scores,
            ),
        )

    @classmethod
    def _score(cls, task: str, capability: CapabilityRecord) -> float:
        query_tokens = cls._tokens(task)
        haystack = " ".join(
            [
                capability.name,
                capability.description,
                capability.type.value,
                capability.source,
                capability.owner,
                " ".join(capability.tags),
            ]
        ).lower()
        if not query_tokens:
            return 0
        score = 0.0
        for token in query_tokens:
            if token in haystack:
                score += 10 + min(len(token), 12)
        return score

    @staticmethod
    def _tokens(text: str) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                token
                for token in re.split(r"[^0-9a-zA-Z_\u4e00-\u9fff]+", text.lower())
                if len(token) > 1
            )
        )


__all__ = [
    "CapabilityCost",
    "CapabilityHealth",
    "CapabilityPermissions",
    "CapabilityRecord",
    "CapabilityRegistry",
    "CapabilitySelectionRequest",
    "CapabilitySelectionResult",
    "CapabilitySelectionTrace",
    "CapabilityType",
    "DynamicCapabilitySelector",
]
