from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from agentchat.utils.runtime_observability import (  # noqa: E402
    RedisKeys,
    build_langchain_run_config,
)


def test_redis_keys_use_namespaced_layout():
    assert RedisKeys.auth_session("u_123") == "auth:user:u_123:session"
    assert RedisKeys.captcha("abc") == "captcha:abc"
    assert RedisKeys.rsa_private_key() == "security:rsa:private_key"
    assert RedisKeys.stream_latest("s_456") == "stream:s_456:latest"


def test_langchain_run_config_includes_langsmith_metadata():
    config = build_langchain_run_config(
        callbacks=["usage-callback"],
        run_name="workspace_simple_chat",
        tags=["workspace", "simple-agent"],
        metadata={
            "trace_id": "trace-1",
            "user_id": "user-1",
            "session_id": "session-1",
            "knowledge_ids": ["kb-1", "kb-2"],
            "agent_name": "Simple-Agent",
        },
    )

    assert config["callbacks"] == ["usage-callback"]
    assert config["run_name"] == "workspace_simple_chat"
    assert config["tags"] == ["workspace", "simple-agent"]
    assert config["metadata"]["trace_id"] == "trace-1"
    assert config["metadata"]["user_id"] == "user-1"
    assert config["metadata"]["session_id"] == "session-1"
    assert config["metadata"]["knowledge_ids"] == ["kb-1", "kb-2"]
    assert config["metadata"]["agent_name"] == "Simple-Agent"
