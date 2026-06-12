import asyncio
from types import SimpleNamespace


def test_normalize_image_input_converts_local_storage_url_to_data_uri(monkeypatch):
    from agentchat.services.rag import vl_embedding

    captured = {}
    monkeypatch.setattr(
        vl_embedding.app_settings,
        "storage",
        SimpleNamespace(active=SimpleNamespace(base_url="http://127.0.0.1:9000/agentchat", bucket_name="agentchat")),
    )
    def fake_get_file_bytes(object_name):
        captured["object_name"] = object_name
        return b"fake-image-bytes"

    monkeypatch.setattr(vl_embedding.storage_client, "get_file_bytes", fake_get_file_bytes, raising=False)

    result = asyncio.run(vl_embedding._normalize_image_input("http://127.0.0.1:9000/files/2026-4-22/png/test.png"))

    assert captured["object_name"] == "files/2026-4-22/png/test.png"
    assert result.startswith("data:image/png;base64,")
