from __future__ import annotations

import asyncio
from pathlib import Path

from zuno.api.dto.workspace import WorkspaceAttachment
from zuno.platform.services.workspace import attachment_service


def test_workspace_document_attachment_uses_canonical_ir_without_chunk_projection(
    monkeypatch,
    tmp_path,
) -> None:
    source = tmp_path / "policy.md"
    source.write_text("# Policy\nRenewal notice is required.", encoding="utf-8")
    attachment = WorkspaceAttachment(
        name="policy.md",
        url="https://storage.example.test/policy.md",
        mime_type="text/markdown",
    )
    monkeypatch.setattr(attachment_service, "_download_attachment", lambda _: str(source))

    kind, content = asyncio.run(
        attachment_service._extract_attachment_text(
            attachment,
            session_id="session_policy",
        )
    )

    assert kind == "document"
    assert "Renewal notice is required." in content


def test_workspace_attachment_service_does_not_import_chunk_projection_adapter() -> None:
    source = "src/backend/zuno/platform/services/workspace/attachment_service.py"
    content = Path(source).read_text(encoding="utf-8")

    assert "parse_file_into_chunk_model_projection" not in content
    assert "chunk_projection_adapter" not in content
    assert "from zuno.api.dto.chunk import ChunkModel" not in content
