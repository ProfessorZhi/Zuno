from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zuno.platform.contracts import canonical_sha256


CAPABILITY_EXPOSURE_CONFORMANCE_VERSION = "capability-exposure-conformance-v1.phase21"

FORBIDDEN_PLANNER_EXPOSURE_FIELDS = (
    "api_key",
    "access_token",
    "bearer ",
    "client_secret",
    "credential_policy",
    "dependency_probe",
    "private_key",
    "raw_instruction",
    "required_roles",
    "secret",
)

PROMPT_INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "developer message",
    "system prompt",
    "reveal secret",
    "bypass approval",
    "disable policy",
)


class CapabilityExposureConformanceError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CapabilityExposureConformanceReport:
    policy_version: str
    exposure_ref: str
    status: str
    checked_capability_ids: tuple[str, ...]
    blocked_capability_ids: tuple[str, ...]
    attack_findings: tuple[str, ...] = field(default_factory=tuple)
    sanitized_fields_absent: tuple[str, ...] = field(default_factory=tuple)
    audit_ref: str = ""
    report_hash: str = ""

    def __post_init__(self) -> None:
        payload = {
            "policy_version": self.policy_version,
            "exposure_ref": self.exposure_ref,
            "status": self.status,
            "checked_capability_ids": list(self.checked_capability_ids),
            "blocked_capability_ids": list(self.blocked_capability_ids),
            "attack_findings": list(self.attack_findings),
            "sanitized_fields_absent": list(self.sanitized_fields_absent),
        }
        object.__setattr__(self, "audit_ref", f"capability-exposure-audit:{canonical_sha256(payload)[:24]}")
        object.__setattr__(self, "report_hash", canonical_sha256({**payload, "audit_ref": self.audit_ref}))

    def as_trace(self) -> dict[str, Any]:
        return {
            "policy_version": self.policy_version,
            "exposure_ref": self.exposure_ref,
            "status": self.status,
            "checked_capability_ids": list(self.checked_capability_ids),
            "blocked_capability_ids": list(self.blocked_capability_ids),
            "attack_findings": list(self.attack_findings),
            "sanitized_fields_absent": list(self.sanitized_fields_absent),
            "audit_ref": self.audit_ref,
            "report_hash": self.report_hash,
        }


def validate_planner_exposure_conformance(
    *,
    task_goal: str,
    requested_capability_ids: tuple[str, ...],
    allowed_capability_ids: tuple[str, ...],
    blocked_capability_reasons: dict[str, str],
    planner_exposure: dict[str, Any],
    serialized_exposure: str,
) -> CapabilityExposureConformanceReport:
    exposure_ref = str(planner_exposure.get("exposure_ref") or "")
    exposed_ids = tuple(
        str(entry.get("capability_id"))
        for entry in planner_exposure.get("capabilities", [])
        if isinstance(entry, dict)
    )
    allowed_set = set(allowed_capability_ids)
    blocked_ids = tuple(sorted(blocked_capability_reasons))
    findings: list[str] = []

    if planner_exposure.get("visibility") != "planner_authorized_summary_schema_only":
        findings.append("invalid_visibility_boundary")
    if any(capability_id not in allowed_set for capability_id in exposed_ids):
        findings.append("unauthorized_capability_exposed")
    if any(capability_id in serialized_exposure for capability_id in blocked_ids):
        findings.append("blocked_capability_identifier_leaked")
    if any(capability_id in exposed_ids for capability_id in blocked_ids):
        findings.append("blocked_capability_exposed")
    if set(exposed_ids) - set(requested_capability_ids):
        findings.append("unrequested_capability_exposed")

    sanitized = tuple(
        marker
        for marker in FORBIDDEN_PLANNER_EXPOSURE_FIELDS
        if marker not in serialized_exposure.lower()
    )
    leaked_fields = sorted(set(FORBIDDEN_PLANNER_EXPOSURE_FIELDS) - set(sanitized))
    if leaked_fields:
        findings.append("sensitive_policy_field_leaked:" + ",".join(leaked_fields))

    lowered_goal = task_goal.lower()
    if any(marker in lowered_goal for marker in PROMPT_INJECTION_MARKERS):
        findings.append("prompt_injection_marker_ignored")

    blocking = tuple(
        finding
        for finding in findings
        if finding
        not in {
            "prompt_injection_marker_ignored",
        }
    )
    report = CapabilityExposureConformanceReport(
        policy_version=CAPABILITY_EXPOSURE_CONFORMANCE_VERSION,
        exposure_ref=exposure_ref,
        status="passed" if not blocking else "failed",
        checked_capability_ids=exposed_ids,
        blocked_capability_ids=blocked_ids,
        attack_findings=tuple(findings),
        sanitized_fields_absent=sanitized,
    )
    if blocking:
        raise CapabilityExposureConformanceError(
            "capability planner exposure conformance failed: " + ",".join(blocking)
        )
    return report


__all__ = [
    "CAPABILITY_EXPOSURE_CONFORMANCE_VERSION",
    "CapabilityExposureConformanceError",
    "CapabilityExposureConformanceReport",
    "validate_planner_exposure_conformance",
]
