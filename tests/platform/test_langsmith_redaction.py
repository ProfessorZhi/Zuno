from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel
import pytest

from zuno.platform.observability.trace_adapter import redact_sensitive_data


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


def test_redact_content_keys() -> None:
    data = {
        "raw_document": "Sensitive doc body",
        "document_content": "Sensitive doc content",
        "prompt_content": "Sensitive prompt",
        "tool_result": "Sensitive tool result",
        "authorization_header": "Bearer xxx",
        "full_database_row": "Row data",
        "secret_lease": "Lease 123",
        "approval_token": "Appr token",
        "desktop_token": "Desk token",
        "other_info": "Public info",
    }
    redacted = redact_sensitive_data(data, redact_content=True)
    for key in [
        "raw_document",
        "document_content",
        "prompt_content",
        "tool_result",
        "authorization_header",
        "full_database_row",
        "secret_lease",
        "approval_token",
        "desktop_token",
    ]:
        assert redacted[key] in ("[REDACTED_CONTENT]", "[REDACTED_SECRET]")
    assert redacted["other_info"] == "Public info"


def test_redact_nested_structures() -> None:
    nested = {
        "user": {
            "api_key": "sk-secret",
            "profile": {
                "password": "pass",
                "auth_items": ["tok1", {"secret": "inner_secret"}],
            },
        },
        "tuple_data": ("normal", {"access_key": "in_tuple"}),
    }
    redacted = redact_sensitive_data(nested, redact_content=True)
    assert redacted["user"]["api_key"] == "[REDACTED_SECRET]"
    assert redacted["user"]["profile"]["password"] == "[REDACTED_SECRET]"
    assert redacted["user"]["profile"]["auth_items"][1]["secret"] == "[REDACTED_SECRET]"
    assert redacted["tuple_data"][1]["access_key"] == "[REDACTED_SECRET]"


def test_redact_pydantic_and_dataclass() -> None:
    p_model = SamplePydanticModel()
    d_model = SampleDataclass()

    red_p = redact_sensitive_data({"pydantic": p_model, "dataclass": d_model})
    assert red_p["pydantic"]["api_key"] == "[REDACTED_SECRET]"
    assert red_p["pydantic"]["normal_field"] == "public_data"
    assert red_p["dataclass"]["password"] == "[REDACTED_SECRET]"
    assert red_p["dataclass"]["username"] == "alice"


def test_redact_truncation_and_unserializable() -> None:
    long_str = "a" * 1000
    redacted_str = redact_sensitive_data(long_str, max_chars=10)
    assert redacted_str == "aaaaaaaaaa...[TRUNCATED]"

    class CustomObj:
        def __str__(self) -> str:
            return "CustomObjRepresented"

    redacted_obj = redact_sensitive_data(CustomObj(), max_chars=10)
    assert redacted_obj == "CustomObjR...[TRUNCATED]"


def test_redact_exception() -> None:
    exc = ValueError("Invalid operation")
    redacted_exc = redact_sensitive_data(exc)
    assert redacted_exc == "ValueError: Invalid operation"
