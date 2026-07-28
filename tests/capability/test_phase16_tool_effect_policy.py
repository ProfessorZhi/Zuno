from __future__ import annotations

from zuno.capability.tool_runtime.effect_policy import (
    TOOL_EFFECT_POLICY_VERSION,
    ToolEffectClass,
    classify_tool_effect,
)


def test_phase16_effect_policy_classifies_read_write_async_and_targets() -> None:
    read_policy = classify_tool_effect(
        tool_name="filesystem.read",
        args={"path": "docs/architecture/README.md"},
        side_effect_level="read",
        adapter_kind="LOCAL_FUNCTION",
    )
    write_policy = classify_tool_effect(
        tool_name="mail.send",
        args={"to": "review@example.com", "target": "mailto:review@example.com"},
        side_effect_level="write_external",
        adapter_kind="API",
    )
    async_policy = classify_tool_effect(
        tool_name="export.start",
        args={"resource": "s3://bucket/export"},
        side_effect_level="async_external",
        adapter_kind="ASYNC_JOB",
    )

    assert read_policy.policy_version == TOOL_EFFECT_POLICY_VERSION
    assert read_policy.effect_class is ToolEffectClass.READ
    assert read_policy.provider_dispatch_allowed is True
    assert read_policy.target_resource_set.conflict_keys == ("docs/architecture/readme.md",)
    assert write_policy.effect_class is ToolEffectClass.IRREVERSIBLE_WRITE
    assert write_policy.provider_dispatch_allowed is False
    assert write_policy.approval_required is True
    assert "mailto:review@example.com" in write_policy.target_resource_set.resource_refs
    assert async_policy.effect_class is ToolEffectClass.ASYNC_EXTERNAL
    assert async_policy.audit_required is True
