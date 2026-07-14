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

REQUIRED_PARTS = [
    "# Part I：定位、问题与边界",
    "# Part II：核心产品场景与端到端语义",
    "# Part III：产品对象、Projection 与真实状态",
    "# Part IV：Command、Query、Stream 与安全边界",
    "# Part V：第一轮架构不变量",
    "# Part VI：第一轮冻结项与第二轮待设计项",
    "# Part VII：Requirement、测试与完成证据",
]

REQUIRED_TERMS = [
    "status: target-boundary-foundation",
    "北向产品边界",
    "Product Surface 不是 Agent Core",
    "Cross-module Ownership",
    "Trust Boundary",
    "统一产品主路径",
    "Strict Grounded Answer",
    "Tool Effect UNKNOWN",
    "Projection 不是事实源",
    "AvailableAction 原则",
    "Command API 语义",
    "Query API 语义",
    "SSE Product Projection Stream",
    "Provisional Content",
    "Authorization Checkpoints",
    "Invariant Registry",
    "第二轮待冻结 Contract",
    "boundary foundation available",
    ".agent/programs/",
]

REQUIRED_INVARIANTS = [f"INV-PRODUCT-{number:03d}" for number in range(1, 25)]

FORBIDDEN_ASSERTIONS = [
    "status: normative-target-module-architecture",
    "contract-complete\nimplementation-spec-complete",
    "Product Surface owns AgentRun",
    "Product Surface owns Approval",
    "Product Surface owns ToolAttempt",
    "SSE 关闭表示任务完成",
    "HTTP 200 表示 Run 成功",
    "Queue ACK 表示任务完成",
]

DEFERRED_TERMS = [
    "RuntimeRequest 完整字段",
    "Product Projection Version 与 Source Watermark 结构",
    "SSE Event Schema、Cursor 编码、Retention 和 Backpressure",
    "Product 数据库表、索引、事务和 Migration",
    "REST Path、API Version 和兼容适配器退役计划",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []

    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX, DOCS_MAP]:
        if not path.exists():
            errors.append(f"missing Product Surface boundary path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Product Surface formal document and mirror must be byte-identical")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Product Surface document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Product Surface document parts are not in canonical order")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Product Surface boundary document missing required term: {term}")

    for invariant in REQUIRED_INVARIANTS:
        if formal.count(invariant) != 1:
            errors.append(f"Product Surface invariant must appear exactly once: {invariant}")

    requirement_ids = [int(value) for value in re.findall(r"ARCH-PRODUCT-(\d{3})", formal)]
    if sorted(requirement_ids) != list(range(1, 33)):
        errors.append("Product Surface document must define ARCH-PRODUCT-001 through ARCH-PRODUCT-032 exactly once")

    for assertion in FORBIDDEN_ASSERTIONS:
        if assertion in formal:
            errors.append(f"Product Surface boundary document contains forbidden assertion: {assertion}")

    for term in DEFERRED_TERMS:
        if term not in formal:
            errors.append(f"Product Surface boundary document must explicitly defer: {term}")

    docs_index = _read(DOCS_INDEX)
    agent_index = _read(AGENT_INDEX)
    docs_map = _read(DOCS_MAP)
    if "[01-product-surface.md](./01-product-surface.md)" not in docs_index:
        errors.append("docs/modules/README.md must link the Product Surface boundary document")
    if "[01-product-surface.md](./01-product-surface.md)" not in agent_index:
        errors.append(".agent/modules/README.md must link the Product Surface mirror")
    if "第一轮边界设计" not in docs_index or "第一轮边界设计" not in agent_index:
        errors.append("module indexes must label Product Surface as first-round boundary design")
    if "docs/modules/01-product-surface.md" not in docs_map:
        errors.append("docs map must route Product Surface work to the formal boundary document")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Product Surface first-round boundary design verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
