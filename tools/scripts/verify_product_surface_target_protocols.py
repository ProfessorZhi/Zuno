from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/01-product-surface.md"
MIRROR = REPO_ROOT / ".agent/modules/01-product-surface.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
DOCS_MAP = REPO_ROOT / ".agent/references/docs-map.md"
WEB_AGENTS = REPO_ROOT / "apps/web/AGENTS.md"

REQUIRED_PARTS = [
    "# Part I：定位与概念架构",
    "# Part II：产品机制与完整运行流程",
    "# Part III：状态、Projection、恢复与一致性概览",
    "# Part IV：目标实现表面与规范索引",
    "# Part V：领域模型、状态转换与显示闭环",
    "# Part VI：Command、Query、Stream 与交付控制协议",
    "# Part VII：安全、生命周期与一致性协议",
    "# Part VIII：验证与完成证据",
]

REQUIRED_TERMS = [
    "统一北向产品边界",
    "Product Surface 不得成为第二套 Controller",
    "ConversationThread",
    "UserSubmission",
    "UserMessage",
    "ProductCommand",
    "RuntimeRequest",
    "CommandReceipt",
    "ProductProjectionSnapshot",
    "ProductProjectionEventV1",
    "SourceWatermark",
    "AuthorizedView",
    "AvailableAction",
    "ProductDisplayStatus",
    "ProjectionFreshness",
    "ConnectionStatus",
    "ChannelDelivery",
    "ClientRenderReceipt",
    "UserReadReceipt",
    "FeedbackSubmission",
    "Snapshot + Delta",
    "Resume Cursor",
    "RESYNC_REQUIRED",
    "REAUTHORIZATION_REQUIRED",
    "Provisional Content",
    "Tool Effect UNKNOWN",
    "CrossModuleEnvelopeV1",
    "Requirement Enforcement Matrix",
    "Requirement Control Registry",
    "ProductTransitionRecord",
    "Failure Decision Matrix",
    "PostgreSQL Target Tables",
    "Target Test Matrix",
    "唯一的正式 Target 架构文档",
    ".agent/programs/",
]

REQUIRED_TABLES = [
    "product_conversation_threads",
    "product_user_submissions",
    "product_messages",
    "product_commands",
    "product_command_receipts",
    "product_runtime_requests",
    "product_channel_deliveries",
    "product_delivery_attempts",
    "product_client_render_receipts",
    "product_user_read_receipts",
    "product_feedback_submissions",
    "product_transition_records",
    "product_failures",
    "product_outbox_events",
    "product_reconciliation_records",
    "product_conversation_projections",
    "product_run_projections",
    "product_interrupt_projections",
    "product_ingestion_projections",
    "product_artifact_projections",
    "product_quality_projections",
    "product_projection_events",
    "product_projection_source_watermarks",
    "product_projection_rebuilds",
    "product_stream_cursors",
]

REQUIRED_MATRICES = [
    "### 39.1 Conversation Transition Matrix",
    "### 40.1 UserSubmission Transition Matrix",
    "### 41.1 Receipt Transition Matrix",
    "### 42.1 Projection Transition Matrix",
    "### 44.1 ChannelDelivery Transition Matrix",
    "## 45. FeedbackSubmission State Machine",
    "## 46. StreamSession Contract",
    "## 47. Display Mapping Matrix",
]

REQUIRED_API_PATHS = [
    "POST /api/v1/product/conversations",
    "POST /api/v1/product/conversations/{conversation_id}/submissions",
    "POST /api/v1/product/runs/{run_id}/signals",
    "POST /api/v1/product/approvals/{approval_id}/decisions",
    "POST /api/v1/product/runs/{run_id}/cancel",
    "POST /api/v1/product/artifacts/{artifact_id}/download-sessions",
    "GET /api/v1/product/runs/{run_id}/snapshot",
    "GET /api/v1/product/runs/{run_id}/events",
]

FORBIDDEN_TERMS = [
    "status: target-boundary-foundation",
    "boundary foundation available",
    "第二轮待冻结 Contract",
    "Product Surface 的第二轮实施级设计",
    "pendingToolApproval",
    "HTTP 200 即任务成功",
    "SSE 结束即成功",
    "src/backend/zuno/product/",
]

SPLIT_NAMES = [
    "01-product-surface-api.md",
    "01-product-surface-projection.md",
    "01-product-surface-streaming.md",
    "01-product-surface-contracts.md",
    "01-product-surface-security.md",
    "01-product-surface-operations.md",
]

OBJECT_TABLE_PAIRS = {
    "ConversationThread": "product_conversation_threads",
    "UserSubmission": "product_user_submissions",
    "UserMessage": "product_messages",
    "ProductCommand": "product_commands",
    "CommandReceipt": "product_command_receipts",
    "RuntimeRequest": "product_runtime_requests",
    "ChannelDelivery": "product_channel_deliveries",
    "DeliveryAttempt": "product_delivery_attempts",
    "ClientRenderReceipt": "product_client_render_receipts",
    "UserReadReceipt": "product_user_read_receipts",
    "FeedbackSubmission": "product_feedback_submissions",
    "ProductProjectionEvent": "product_projection_events",
    "SourceWatermark": "product_projection_source_watermarks",
    "ProjectionRebuildRecord": "product_projection_rebuilds",
    "StreamCursorRecord": "product_stream_cursors",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX, DOCS_MAP, WEB_AGENTS]:
        if not path.exists():
            errors.append(f"missing Product Surface path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Product Surface formal document and mirror must be byte-identical")
    if "status: normative-target-module-architecture" not in formal:
        errors.append("Product Surface document must declare normative-target-module-architecture")

    formal_variants = sorted(p.name for p in FORMAL.parent.glob("01-product-surface*.md"))
    mirror_variants = sorted(p.name for p in MIRROR.parent.glob("01-product-surface*.md"))
    if formal_variants != ["01-product-surface.md"]:
        errors.append(f"Product Surface must have one formal document; got {formal_variants}")
    if mirror_variants != ["01-product-surface.md"]:
        errors.append(f"Product Surface must have one Agent mirror; got {mirror_variants}")
    for name in SPLIT_NAMES:
        if (FORMAL.parent / name).exists() or (MIRROR.parent / name).exists():
            errors.append(f"split Product Surface document is forbidden: {name}")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Product Surface document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Product Surface parts are not ordered I through VIII")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Product Surface document missing required term: {term}")
    for table in REQUIRED_TABLES:
        if table not in formal:
            errors.append(f"Product Surface document missing target table: {table}")
    for matrix in REQUIRED_MATRICES:
        if matrix not in formal:
            errors.append(f"Product Surface document missing state matrix: {matrix}")
    for path in REQUIRED_API_PATHS:
        if path not in formal:
            errors.append(f"Product Surface document missing target API path: {path}")
    for term in FORBIDDEN_TERMS:
        if term in formal:
            errors.append(f"Product Surface document contains forbidden term: {term}")

    for object_name, table_name in OBJECT_TABLE_PAIRS.items():
        if object_name not in formal or table_name not in formal:
            errors.append(f"object/storage mapping incomplete: {object_name} -> {table_name}")

    requirement_ids = [int(v) for v in re.findall(r"ARCH-PRODUCT-(\d{3})", formal)]
    control_ids = [int(v) for v in re.findall(r"RC-PRODUCT-(\d{3})", formal)]
    invariant_ids = [int(v) for v in re.findall(r"INV-PRODUCT-(\d{3})", formal)]
    if sorted(requirement_ids) != list(range(1, 81)):
        errors.append("ARCH-PRODUCT-001 through ARCH-PRODUCT-080 must exist exactly once")
    if sorted(control_ids) != list(range(1, 81)):
        errors.append("RC-PRODUCT-001 through RC-PRODUCT-080 must exist exactly once")
    if sorted(invariant_ids) != list(range(1, 31)):
        errors.append("INV-PRODUCT-001 through INV-PRODUCT-030 must exist exactly once")

    docs_index = _read(DOCS_INDEX)
    agent_index = _read(AGENT_INDEX)
    docs_map = _read(DOCS_MAP)
    web_agents = _read(WEB_AGENTS)
    for text in ["01-product-surface.md", "单一完整 Target 架构", "verify_product_surface_target_protocols.py"]:
        if text not in docs_index:
            errors.append(f"docs/modules/README.md missing Product route: {text}")
    for text in [".agent/modules/01-product-surface.md", "docs/modules/01-product-surface.md", "verify_product_surface_target_protocols.py"]:
        if text not in agent_index:
            errors.append(f".agent/modules/README.md missing Product route: {text}")
    for text in ["docs/modules/01-product-surface.md", ".agent/modules/01-product-surface.md", "verify_product_surface_target_protocols.py"]:
        if text not in docs_map:
            errors.append(f".agent/references/docs-map.md missing Product route: {text}")
    for text in ["docs/modules/01-product-surface.md", "AvailableAction", "Product Projection"]:
        if text not in web_agents:
            errors.append(f"apps/web/AGENTS.md missing Product rule: {text}")

    for path in [
        "src/backend/zuno/api/product/",
        "src/backend/zuno/api/services/product/",
        "src/backend/zuno/platform/database/product/",
        "apps/web/src/product/",
        "apps/desktop/src/product/",
    ]:
        if path not in formal:
            errors.append(f"Product target code layout missing: {path}")

    if "# Current Baseline" in formal or "# Current 实现" in formal:
        errors.append("Product Target document must not embed Current baseline sections")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Product Surface target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
