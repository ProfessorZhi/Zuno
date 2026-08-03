"""In-memory fake object store used as a test double.

The PHASE22-OBJECT-STORE-OWNER-GATE must treat this file as a Test Double
and exclude it from the production owner count.  It intentionally mirrors
the surface area of :class:`MinioObjectStore` so it can be substituted in
unit tests without affecting the production binding proof.
"""

from __future__ import annotations

from typing import Any, Dict, List


class FakeObjectStore:
    """Drop-in replacement for tests only; never used in production."""

    def __init__(self) -> None:
        self.buckets: Dict[str, List[Any]] = {}

    def ensure_bucket(self, bucket: str, *, object_lock: bool = False) -> None:
        self.buckets.setdefault(bucket, [])

    def stage_object(self, *, bucket: str, object_name: str, content: bytes) -> Dict[str, Any]:
        self.buckets.setdefault(bucket, []).append({"name": object_name, "size": len(content)})
        return {
            "bucket": bucket,
            "object_name": object_name,
            "content_hash": "fake-hash",
            "size_bytes": len(content),
            "visibility": "staged",
        }


__all__ = ["FakeObjectStore"]