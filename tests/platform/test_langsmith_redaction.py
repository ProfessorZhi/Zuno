from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel
import pytest

from zuno.platform.observability.trace_adapter import redact_sensitive_data, sanitize_secret_values


class SamplePydanticModel(BaseModel):
    api_key: str = "sk-pydantic-secret"
    normal_field: str = "public_data"


@dataclass
class SampleDataclass:
    password: str = "pass123"
    username: str = "alice"


def test_redact_sensitive_data_keys() -> None:
    data = {
        "api_key": "sk-123456",
        "password": "my_password",
        "secret": "topsecret",
        "authorization": "Bearer token123",
        "token": "tok_xyz",
        "access_token": "acc_tok",
        "refresh_token": "ref_tok",
        "id_token": "id_tok",
        "session_token": "sess_tok",
        "access_key": "acc_key",
        "private_key": "-----BEGIN PRIVATE KEY-----",
        "connection_string": "postgres://user:pass@localhost",
        "cookie": "session=abc",
        "set_cookie": "session=def",
        "database_url": "mysql://root:secret@localhost",
        "bearer": "token_val",
        "normal_key": "hello",
    }
    redacted = redact_sensitive_data(data)
    for key in [
        "api_key",
        "password",
        "secret",
        "authorization",
        "token",
        "access_token",
        "refresh_token",
        "id_token",
        "session_token",
        "access_key",
        "private_key",
        "connection_string",
        "cookie",
        "set_cookie",
        "database_url",
        "bearer",
    ]:
        assert redacted[key] == "[REDACTED_SECRET]"
    assert redacted["normal_key"] == "hello"


def test_value_level_secret_sanitization() -> None:
    error_msg = "Error connecting to postgresql+psycopg://postgres:secret123@localhost:5432/zuno with Bearer sk-live-998877665544332211"
    sanitized = sanitize_secret_values(error_msg)
    assert "secret123" not in sanitized
    assert "sk-live-998877665544332211" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized

    exc = RuntimeError("Failed with api_key=sk-1234567890 password=supersecret")
    redacted_exc = redact_sensitive_data(exc)
    assert "sk-1234567890" not in redacted_exc
    assert "supersecret" not in redacted_exc


def test_content_switches_independent() -> None:
    data = {
        "prompt_content": "Sensitive prompt",
        "raw_document": "Doc body",
        "document_content": "Doc content",
        "tool_result": "Tool output",
        "normal_field": "Normal value",
    }

    # All content switches off (default): metadata_only=False does NOT bypass them!
    res1 = redact_sensitive_data(data, redact_content=False, include_prompt_content=False, include_document_content=False, include_tool_content=False)
    assert res1["prompt_content"] == "[REDACTED_CONTENT]"
    assert res1["raw_document"] == "[REDACTED_CONTENT]"
    assert res1["document_content"] == "[REDACTED_CONTENT]"
    assert res1["tool_result"] == "[REDACTED_CONTENT]"
    assert res1["normal_field"] == "Normal value"

    # Only include_prompt_content=True
    res2 = redact_sensitive_data(data, redact_content=False, include_prompt_content=True)
    assert res2["prompt_content"] == "Sensitive prompt"
    assert res2["raw_document"] == "[REDACTED_CONTENT]"

    # Only include_document_content=True
    res3 = redact_sensitive_data(data, redact_content=False, include_document_content=True)
    assert res3["document_content"] == "Doc content"
    assert res3["prompt_content"] == "[REDACTED_CONTENT]"

    # Only include_tool_content=True
    res4 = redact_sensitive_data(data, redact_content=False, include_tool_content=True)
    assert res4["tool_result"] == "Tool output"
    assert res4["prompt_content"] == "[REDACTED_CONTENT]"
