from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools/scripts/verify_product_surface_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/01-product-surface.md"
MIRROR = REPO_ROOT / ".agent/modules/01-product-surface.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_product_surface_target_protocols", VERIFIER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Product Surface target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_product_surface_target_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_only_one_product_surface_target_document_exists() -> None:
    assert FORMAL.exists()
    assert MIRROR.exists()
    assert sorted(p.name for p in FORMAL.parent.glob("01-product-surface*.md")) == [
        "01-product-surface.md"
    ]
    assert sorted(p.name for p in MIRROR.parent.glob("01-product-surface*.md")) == [
        "01-product-surface.md"
    ]


def test_product_surface_mirror_is_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


def test_document_has_eight_ordered_parts() -> None:
    content = _content()
    parts = [
        "# Part I：定位与概念架构",
        "# Part II：产品机制与完整运行流程",
        "# Part III：状态、Projection、恢复与一致性概览",
        "# Part IV：目标实现表面与规范索引",
        "# Part V：领域模型、状态转换与显示闭环",
        "# Part VI：Command、Query、Stream 与交付控制协议",
        "# Part VII：安全、生命周期与一致性协议",
        "# Part VIII：验证与完成证据",
    ]
    positions = [content.index(part) for part in parts]
    assert positions == sorted(positions)
    assert all(content.count(part) == 1 for part in parts)


def test_requirements_controls_and_invariants_are_contiguous() -> None:
    content = _content()
    assert sorted(int(v) for v in re.findall(r"ARCH-PRODUCT-(\d{3})", content)) == list(
        range(1, 81)
    )
    assert sorted(int(v) for v in re.findall(r"RC-PRODUCT-(\d{3})", content)) == list(
        range(1, 81)
    )
    assert sorted(int(v) for v in re.findall(r"INV-PRODUCT-(\d{3})", content)) == list(
        range(1, 31)
    )


def test_target_only_status_and_program_boundary() -> None:
    content = _content()
    assert "status: normative-target-module-architecture" in content
    assert "唯一的正式 Target 架构文档" in content
    assert ".agent/programs/" in content
    assert "# Current Baseline" not in content
    assert "status: target-boundary-foundation" not in content


def test_product_does_not_become_second_controller() -> None:
    content = _content()
    assert "Product Surface 不得成为第二套 Controller" in content
    assert "Product 不创建 Plan、不推进 Step、不决定 Retry/Replan、不写 RunOutcome" in content
    assert "Agent Core" in content
    assert "Security" in content
    assert "Tool Runtime" in content


def test_projection_and_stream_contracts_are_complete() -> None:
    content = _content()
    for term in [
        "Base Product Projection",
        "AuthorizedView",
        "AvailableAction",
        "SourceWatermark",
        "AggregateVersion",
        "ProjectionVersion",
        "StreamSequence",
        "Snapshot + Delta",
        "Resume Cursor",
        "RESYNC_REQUIRED",
        "REAUTHORIZATION_REQUIRED",
        "Backpressure",
    ]:
        assert term in content


def test_product_state_matrices_exist() -> None:
    content = _content()
    for heading in [
        "### 39.1 Conversation Transition Matrix",
        "### 40.1 UserSubmission Transition Matrix",
        "### 41.1 Receipt Transition Matrix",
        "### 42.1 Projection Transition Matrix",
        "### 44.1 ChannelDelivery Transition Matrix",
        "## 45. FeedbackSubmission State Machine",
        "## 46. StreamSession Contract",
        "## 47. Display Mapping Matrix",
    ]:
        assert heading in content


def test_outcome_and_side_effect_semantics_are_not_flattened() -> None:
    content = _content()
    for term in [
        "PARTIAL",
        "ABSTAINED",
        "REFUSED",
        "BLOCKED",
        "Tool Effect UNKNOWN",
        "UNKNOWN 禁止盲目重试",
        "Cancel Accepted、Run CANCELLING",
        "Artifact、Publication、Delivery、Render、Read 分离",
    ]:
        assert term in content


def test_storage_and_physical_layout_respect_repository_contract() -> None:
    content = _content()
    for path in [
        "src/backend/zuno/api/product/",
        "src/backend/zuno/api/services/product/",
        "src/backend/zuno/platform/database/product/",
        "apps/web/src/product/",
        "apps/desktop/src/product/",
    ]:
        assert path in content
    assert "src/backend/zuno/product/" not in content
    for table in [
        "product_conversation_threads",
        "product_commands",
        "product_projection_events",
        "product_stream_cursors",
        "product_channel_deliveries",
    ]:
        assert table in content


def test_security_rendering_and_lifecycle_are_covered() -> None:
    content = _content()
    for term in [
        "EffectiveSecurityEpoch",
        "Action Token",
        "Citation Metadata 不等于内容可访问",
        "Artifact Preview 使用独立 Sandbox",
        "Anti-enumeration",
        "Legal Hold",
        "Correction 与撤回",
        "Product Reconciler Contract",
    ]:
        assert term in content
