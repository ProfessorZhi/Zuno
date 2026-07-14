from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_product_surface_boundary_design.py"
FORMAL = REPO_ROOT / "docs/modules/01-product-surface.md"
MIRROR = REPO_ROOT / ".agent/modules/01-product-surface.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_product_surface_boundary_design", VERIFIER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Product Surface boundary verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_product_surface_boundary_verifier() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_product_surface_mirror_is_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


def test_first_round_parts_are_complete_and_ordered() -> None:
    content = _content()
    parts = [
        "# Part I：定位、问题与边界",
        "# Part II：核心产品场景与端到端语义",
        "# Part III：产品对象、Projection 与真实状态",
        "# Part IV：Command、Query、Stream 与安全边界",
        "# Part V：第一轮架构不变量",
        "# Part VI：第一轮冻结项与第二轮待设计项",
        "# Part VII：Requirement、测试与完成证据",
    ]
    positions = [content.index(part) for part in parts]
    assert positions == sorted(positions)
    assert all(content.count(part) == 1 for part in parts)


def test_first_round_requirements_are_contiguous() -> None:
    requirement_ids = [int(value) for value in re.findall(r"ARCH-PRODUCT-(\d{3})", _content())]
    assert sorted(requirement_ids) == list(range(1, 33))


def test_boundary_does_not_claim_implementation_completion() -> None:
    content = _content()
    assert "status: target-boundary-foundation" in content
    assert "boundary foundation available" in content
    assert "status: normative-target-module-architecture" not in content
    assert "不能声明" in content
    assert "implementation available" in content
    assert "production ready" in content


def test_product_does_not_own_domain_truth() -> None:
    content = _content()
    for phrase in [
        "Product Surface 不建立第二套 Task Controller",
        "Projection 不得反向修改源领域事实",
        "Approval 不由 Product Surface 决定",
        "Tool UNKNOWN 禁止普通 Retry",
        "Upload Accepted 不等于 Searchable",
        "Artifact、Publication、Delivery、Render 和 Read 分离",
    ]:
        assert phrase in content


def test_second_round_surfaces_are_explicitly_deferred() -> None:
    content = _content()
    for phrase in [
        "RuntimeRequest 完整字段",
        "Product Projection Version 与 Source Watermark 结构",
        "SSE Event Schema、Cursor 编码、Retention 和 Backpressure",
        "Product 数据库表、索引、事务和 Migration",
        "REST Path、API Version 和兼容适配器退役计划",
    ]:
        assert phrase in content
