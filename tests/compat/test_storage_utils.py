import asyncio
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "backend"))


def test_extract_object_key_from_public_minio_url():
    from agentchat.utils.file_utils import get_object_key_from_public_url

    object_key = get_object_key_from_public_url(
        "http://127.0.0.1:9000/agentchat/files/2026-4-17/txt/demo.txt",
        bucket_name="agentchat",
    )

    assert object_key == "files/2026-4-17/txt/demo.txt"


def test_extract_object_key_keeps_plain_relative_path():
    from agentchat.utils.file_utils import get_object_key_from_public_url

    object_key = get_object_key_from_public_url(
        "files/2026-4-17/txt/demo.txt",
        bucket_name="agentchat",
    )

    assert object_key == "files/2026-4-17/txt/demo.txt"


def test_text_parser_does_not_delete_source_file(tmp_path):
    from agentchat.services.rag.doc_parser.text import text_parser

    source = tmp_path / "demo.txt"
    source.write_text("hello\nworld", encoding="utf-8")

    text = asyncio.run(text_parser.parse_file(str(source)))

    assert text == "hello\nworld"
    assert source.exists()
