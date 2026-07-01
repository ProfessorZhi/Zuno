from __future__ import annotations

import hashlib
from contextlib import AbstractContextManager
from mimetypes import guess_type
from pathlib import Path
from urllib.parse import unquote, urlparse

from zuno.agent.contracts import ObjectStoreRef, ObjectStoreResult

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
        return self.save_bytes(
            workspace_id=workspace_id,
            source_id=source_id,
            filename=filename,
            mime_type=mime_type,
            content=content.encode("utf-8"),
            owner_id=owner_id,
            acl_scope=acl_scope,
            sensitivity_tags=sensitivity_tags,
        )

    def save_bytes(
        self,
        *,
        workspace_id: str,
        source_id: str,
        filename: str,
        mime_type: str | None,
        content: bytes,
        owner_id: str | None = None,
        acl_scope: str = "workspace",
        sensitivity_tags: list[str] | None = None,
    ) -> SourceObjectRecord:
        data = bytes(content)
        source_sha256 = hashlib.sha256(data).hexdigest()
        safe_filename = filename.replace("\\", "_").replace("/", "_") or "source.txt"
        target = self.root / "workspaces" / workspace_id / "sources" / source_id / safe_filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        storage_uri = target.resolve().as_uri()
        content_type = mime_type or guess_type(safe_filename)[0] or "application/octet-stream"
        return SourceObjectRecord(
            source_id=source_id,
            workspace_id=workspace_id,
            owner_id=owner_id,
            source_uri=storage_uri,
            storage_uri=storage_uri,
            source_sha256=source_sha256,
            mime_type=content_type,
            filename=filename,
            size_bytes=len(data),
            acl_scope=acl_scope,
            sensitivity_tags=list(sensitivity_tags or []),
        )

    def read_bytes(self, source: SourceObjectRecord | str) -> bytes:
        return self._path_from_source(source).read_bytes()

    def open_stream(self, source: SourceObjectRecord | str) -> AbstractContextManager[object]:
        return self._path_from_source(source).open("rb")

    def verify_sha256(self, source: SourceObjectRecord | str, expected_sha256: str | None = None) -> bool:
        expected = expected_sha256 or getattr(source, "source_sha256", None)
        if not expected:
            return False
        try:
            actual = hashlib.sha256(self.read_bytes(source)).hexdigest()
        except FileNotFoundError:
            return False
        return actual == expected

    def diagnose_object(self, source: SourceObjectRecord | str) -> ObjectStoreResult:
        storage_uri = source.storage_uri if isinstance(source, SourceObjectRecord) else source
        path = self._path_from_uri(storage_uri)
        if not path.exists():
            return ObjectStoreResult(
                ok=False,
                diagnostics=[
                    {
                        "code": "object_missing",
                        "storage_uri": storage_uri,
                        "message": "Object store reference does not exist on local disk.",
                    }
                ],
            )
        data = path.read_bytes()
        source_sha256 = hashlib.sha256(data).hexdigest()
        content_type = getattr(source, "mime_type", None) or guess_type(path.name)[0] or "application/octet-stream"
        return ObjectStoreResult(
            ok=True,
            object_ref=ObjectStoreRef(
                storage_uri=path.resolve().as_uri(),
                source_sha256=source_sha256,
                content_type=content_type,
                size_bytes=len(data),
            ),
        )

    def _path_from_source(self, source: SourceObjectRecord | str) -> Path:
        storage_uri = source.storage_uri if isinstance(source, SourceObjectRecord) else source
        return self._path_from_uri(storage_uri)

    @staticmethod
    def _path_from_uri(storage_uri: str) -> Path:
        parsed = urlparse(storage_uri)
        if parsed.scheme != "file":
            raise FileNotFoundError(f"unsupported local object uri: {storage_uri}")
        path_text = unquote(parsed.path)
        if path_text.startswith("/") and len(path_text) > 3 and path_text[2] == ":":
            path_text = path_text[1:]
        return Path(path_text)


__all__ = ["LocalObjectStore"]
