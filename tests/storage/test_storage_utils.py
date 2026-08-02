from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api" / "src"))


def test_extract_object_key_from_public_minio_url():
    from zuno.platform.common.file_utils import get_object_key_from_public_url

    object_key = get_object_key_from_public_url(
        "http://127.0.0.1:9000/zuno/files/2026-4-17/txt/demo.txt",
        bucket_name="zuno",
    )

    assert object_key == "files/2026-4-17/txt/demo.txt"


def test_extract_object_key_keeps_plain_relative_path():
    from zuno.platform.common.file_utils import get_object_key_from_public_url

    object_key = get_object_key_from_public_url(
        "files/2026-4-17/txt/demo.txt",
        bucket_name="zuno",
    )

    assert object_key == "files/2026-4-17/txt/demo.txt"


def test_parse_gateway_file_uri_does_not_delete_source_file(tmp_path):
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    source = tmp_path / "demo.txt"
    source.write_text("hello\nworld", encoding="utf-8")

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_storage_utils",
            workspace_id="workspace_storage_utils",
            source_uri=source.as_uri(),
            mime_type="text/plain",
        )
    )

    assert result.status == "succeeded"
    assert result.document is not None
    assert [block.text for block in result.document.blocks] == ["hello", "world"]
    assert source.exists()
