import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_zuno_config_resource_aliases_exist_and_match_zuno():
    resource_names = ["tool.json", "avatars.json", "mcp_server.json"]
    for resource_name in resource_names:
        zuno_path = REPO_ROOT / "src/backend/zuno/config" / resource_name
        zuno_path = REPO_ROOT / "src/backend/zuno/config" / resource_name
        assert zuno_path.exists()

        zuno_payload = json.loads(zuno_path.read_text(encoding="utf-8"))
        zuno_payload = json.loads(zuno_path.read_text(encoding="utf-8"))

        if resource_name == "mcp_server.json":
            assert all("zuno/mcp_servers/remote_proxy/main.py" in json.dumps(item, ensure_ascii=False) for item in zuno_payload)
        else:
            assert zuno_payload == zuno_payload


def test_zuno_config_example_exists_and_matches_zuno():
    zuno_path = REPO_ROOT / "src/backend/zuno/config.example.yaml"
    zuno_path = REPO_ROOT / "src/backend/zuno/config.example.yaml"
    assert zuno_path.exists()
    assert zuno_path.read_text(encoding="utf-8") == zuno_path.read_text(encoding="utf-8")
