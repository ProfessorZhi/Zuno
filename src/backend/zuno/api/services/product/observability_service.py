from __future__ import annotations

from zuno.api.services.product.runtime_engine import ProductRuntimeMechanics


class ProductObservabilityService:
    """Application owner for Product runtime and retrieval projections."""

    @staticmethod
    def retrieval_observability_summary(*, limit: int = 20) -> dict:
        return ProductRuntimeMechanics.retrieval_observability_summary(limit=limit)


__all__ = ["ProductObservabilityService"]
