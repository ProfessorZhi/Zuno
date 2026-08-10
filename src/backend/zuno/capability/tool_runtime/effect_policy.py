from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from zuno.platform.contracts import canonical_sha256


TOOL_EFFECT_POLICY_VERSION = "tool-effect-policy-v1.phase16"


class ToolEffectClass(StrEnum):
    NONE = "NONE"
    READ = "READ"
    REVERSIBLE_WRITE = "REVERSIBLE_WRITE"
    IRREVERSIBLE_WRITE = "IRREVERSIBLE_WRITE"
    ASYNC_EXTERNAL = "ASYNC_EXTERNAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class TargetResourceSet:
    resource_set_ref: str
    resource_refs: tuple[str, ...]
    conflict_keys: tuple[str, ...]

    @property
    def hash(self) -> str:
        return canonical_sha256(
            {
                "resource_set_ref": self.resource_set_ref,
                "resource_refs": list(self.resource_refs),
                "conflict_keys": list(self.conflict_keys),
            }
        )


@dataclass(frozen=True, slots=True)
class ToolEffectPolicy:
    policy_version: str
    effect_class: ToolEffectClass
    effect_level: str
    target_resource_set: TargetResourceSet
    approval_required: bool
    audit_required: bool
    provider_dispatch_allowed: bool
    blocked_reason: str = ""

    @property
    def policy_hash(self) -> str:
        return canonical_sha256(
            {
                "policy_version": self.policy_version,
                "effect_class": self.effect_class.value,
                "effect_level": self.effect_level,
                "target_resource_set_hash": self.target_resource_set.hash,
                "approval_required": self.approval_required,
                "audit_required": self.audit_required,
                "provider_dispatch_allowed": self.provider_dispatch_allowed,
                "blocked_reason": self.blocked_reason,
            }
        )


def classify_tool_effect(
    *,
    tool_name: str,
    args: dict[str, Any],
    readonly: bool | None = None,
    side_effect_level: str | None = None,
    adapter_kind: str = "",
) -> ToolEffectPolicy:
    normalized_level = _normalize_side_effect_level(side_effect_level, readonly=readonly)
    resources = target_resource_set(tool_name=tool_name, args=args, adapter_kind=adapter_kind)
    effect_class = _effect_class(normalized_level=normalized_level, adapter_kind=adapter_kind)
    provider_dispatch_allowed = effect_class in {ToolEffectClass.NONE, ToolEffectClass.READ}
    return ToolEffectPolicy(
        policy_version=TOOL_EFFECT_POLICY_VERSION,
        effect_class=effect_class,
        effect_level=effect_class.value,
        target_resource_set=resources,
        approval_required=effect_class not in {ToolEffectClass.NONE, ToolEffectClass.READ},
        audit_required=effect_class is not ToolEffectClass.NONE,
        provider_dispatch_allowed=provider_dispatch_allowed,
        blocked_reason="" if provider_dispatch_allowed else "TOOL_EFFECT_POLICY_REQUIRED",
    )


def target_resource_set(*, tool_name: str, args: dict[str, Any], adapter_kind: str = "") -> TargetResourceSet:
    refs: list[str] = []
    for key in ("url", "path", "endpoint", "resource", "target", "query", "to"):
        value = args.get(key)
        if value:
            refs.append(str(value))
    if not refs:
        refs.append(f"tool://{tool_name}")
    resource_refs = tuple(dict.fromkeys(refs))
    conflict_keys = tuple(sorted(_conflict_key(value) for value in resource_refs))
    resource_set_ref = f"target-resource-set:{canonical_sha256({'tool_name': tool_name, 'adapter_kind': adapter_kind, 'resources': list(resource_refs)})[:24]}"
    return TargetResourceSet(
        resource_set_ref=resource_set_ref,
        resource_refs=resource_refs,
        conflict_keys=conflict_keys,
    )


def _normalize_side_effect_level(side_effect_level: str | None, *, readonly: bool | None) -> str:
    if side_effect_level:
        return side_effect_level.lower()
    if readonly is True:
        return "read"
    if readonly is False:
        return "write_external"
    return "unknown"


def _effect_class(*, normalized_level: str, adapter_kind: str) -> ToolEffectClass:
    if normalized_level == "none":
        return ToolEffectClass.NONE
    if normalized_level in {"read", "read_only", "readonly"}:
        return ToolEffectClass.READ
    if normalized_level in {"write_local", "workspace_write"}:
        return ToolEffectClass.REVERSIBLE_WRITE
    if normalized_level in {"destructive", "delete", "irreversible_write"}:
        return ToolEffectClass.IRREVERSIBLE_WRITE
    if normalized_level in {"async_external", "async_job"} or adapter_kind.upper() in {"ASYNC_JOB", "WEBHOOK_CALLBACK"}:
        return ToolEffectClass.ASYNC_EXTERNAL
    if normalized_level in {"write_external", "external_write"}:
        return ToolEffectClass.IRREVERSIBLE_WRITE
    return ToolEffectClass.UNKNOWN


def _conflict_key(resource_ref: str) -> str:
    lowered = resource_ref.lower()
    for separator in ("?", "#"):
        lowered = lowered.split(separator, 1)[0]
    return lowered.rstrip("/")


__all__ = [
    "TOOL_EFFECT_POLICY_VERSION",
    "TargetResourceSet",
    "ToolEffectClass",
    "ToolEffectPolicy",
    "classify_tool_effect",
    "target_resource_set",
]
