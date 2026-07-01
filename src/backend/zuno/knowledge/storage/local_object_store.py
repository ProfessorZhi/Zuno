from __future__ import annotations

import hashlib
from pathlib import Path

from .contracts import SourceObjectRecord


class LocalObjectStore:
    """Product V1 local object store for source files and small text fixtures."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_text(
        self,
        *,
        workspace_id: str,
        source_id: str,
        filename: str,
        mime_type: str,
        content: str,
        owner_id: str | None = None,
        acl_scope: str = "workspace",
        sensitivity_tags: list[str] | None = None,
    ) -> SourceObjectRecord:
        data = content.encode("utf-8")
        source_sha256 = hashlib.sha256(data).hexdigest()
        safe_filename = filename.replace("\\", "_").replace("/", "_") or "source.txt"
        target = self.root / "workspaces" / workspace_id / "sources" / source_id / safe_filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        storage_uri = target.resolve().as_uri()
        return SourceObjectRecord(
            source_id=source_id,
            workspace_id=workspace_id,
            owner_id=owner_id,
            source_uri=storage_uri,
            storage_uri=storage_uri,
            source_sha256=source_sha256,
            mime_type=mime_type,
            filename=filename,
            size_bytes=len(data),
            acl_scope=acl_scope,
            sensitivity_tags=list(sensitivity_tags or []),
        )


__all__ = ["LocalObjectStore"]
