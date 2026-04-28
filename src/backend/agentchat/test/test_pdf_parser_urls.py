import asyncio
from types import SimpleNamespace


def test_upload_file_to_oss_keeps_bucket_prefix(monkeypatch, tmp_path):
    from agentchat.services.rag.doc_parser.pdf import PDFParser

    sample = tmp_path / "sample.png"
    sample.write_bytes(b"png-bytes")

    upload_calls = {}

    monkeypatch.setattr(
        "agentchat.services.rag.doc_parser.pdf.app_settings",
        SimpleNamespace(storage=SimpleNamespace(active=SimpleNamespace(base_url="http://127.0.0.1:9000/agentchat"))),
    )
    monkeypatch.setattr("agentchat.services.rag.doc_parser.pdf.storage_client.sign_url_for_get", lambda *_args, **_kwargs: None, raising=False)

    def fake_upload_file(object_name, file_content):
        upload_calls["object_name"] = object_name
        upload_calls["file_content"] = file_content

    monkeypatch.setattr("agentchat.services.rag.doc_parser.pdf.storage_client.upload_file", fake_upload_file, raising=False)

    sign_url = asyncio.run(PDFParser().upload_file_to_oss(str(sample)))

    assert upload_calls["object_name"] in sign_url
    assert sign_url.startswith("http://127.0.0.1:9000/agentchat/files/")
