import asyncio
import html
import json
import re
import shutil
from typing import Any, Literal, Optional
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import requests
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from agentchat.core.models.manager import ModelManager
from agentchat.utils.model_output import normalize_messages_for_model, strip_think_tags
from agentchat.schema.tool import (
    RemoteApiAssistReq,
    RemoteApiAssistResp,
    SimpleApiConfig,
    SimpleApiParamConfig,
)

DOC_FETCH_TIMEOUT_SECONDS = 10
DOC_BROWSER_RENDER_TIMEOUT_SECONDS = 12
REMOTE_API_AGENT_TIMEOUT_SECONDS = 170
MIN_DOC_TEXT_LENGTH_FOR_RULE_EXTRACTION = 500
MAX_DOC_SOURCE_COUNT = 8
MAX_AGENT_DOC_CHARS = 24000


class AgenticRemoteApiDraft(BaseModel):
    display_name: str = ""
    description: str = ""
    endpoint_url: str = ""
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "GET"
    auth_type: Literal["none", "bearer", "basic", "api_key_query", "api_key_header"] = "none"
    api_key_name: str = ""
    params: list[SimpleApiParamConfig] = Field(default_factory=list)
    probe_args: dict[str, Any] = Field(default_factory=dict)


def normalize_remote_api_auth_config(auth_config: Optional[dict]) -> dict:
    if not auth_config:
        return {}

    if auth_config.get("auth_type"):
        return auth_config

    auth_type = (auth_config.get("type") or "").strip().lower()
    token = auth_config.get("token") or ""
    key_name = (auth_config.get("key_name") or auth_config.get("name") or "").strip()
    if auth_type == "bearer":
        return {"auth_type": "Bearer", "data": token}
    if auth_type == "basic":
        return {"auth_type": "Basic", "data": token}
    if auth_type == "api_key_query":
        return {
            "auth_type": "APIKey",
            "data": token,
            "in": "query",
            "name": key_name or "api_key",
        }
    if auth_type == "api_key_header":
        return {
            "auth_type": "APIKey",
            "data": token,
            "in": "header",
            "name": key_name or "X-API-Key",
        }
    return auth_config


def build_openapi_schema_from_simple_config(simple_api_config: SimpleApiConfig) -> dict[str, Any]:
    path = simple_api_config.path.strip() or "/"
    if not path.startswith("/"):
        path = f"/{path}"

    parameters: list[dict[str, Any]] = []
    for param in simple_api_config.params:
        parameters.append(
            {
                "name": param.name,
                "in": param.location,
                "required": param.required or param.location == "path",
                "description": param.description,
                "schema": {"type": param.type},
            }
        )

    operation: dict[str, Any] = {
        "operationId": simple_api_config.operation_id,
        "summary": simple_api_config.summary or simple_api_config.operation_id,
        "description": simple_api_config.description or simple_api_config.summary or simple_api_config.operation_id,
        "parameters": parameters,
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": simple_api_config.response_schema or {"type": "object"}
                    }
                },
            }
        },
    }

    if simple_api_config.method in {"POST", "PUT", "PATCH"} and simple_api_config.body_schema:
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": simple_api_config.body_schema,
                }
            },
        }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": simple_api_config.summary or simple_api_config.operation_id,
            "description": simple_api_config.description or simple_api_config.summary or simple_api_config.operation_id,
            "version": "1.0.0",
        },
        "servers": [{"url": simple_api_config.base_url.rstrip("/")}],
        "paths": {path: {simple_api_config.method.lower(): operation}},
    }


async def build_remote_api_assist_draft_agentic(req: RemoteApiAssistReq) -> RemoteApiAssistResp:
    docs_urls = _resolve_docs_urls(req.docs_url, req.docs_urls)
    if not docs_urls:
        raise ValueError("请提供至少一个文档链接。Agent 模式需要先读取文档正文，再判断接口地址、认证方式和参数。")

    docs_analysis = _collect_docs_text_bundle(docs_urls)
    docs_text = docs_analysis.get("_source_text", "")
    if len(docs_text.strip()) < 200:
        warnings = "; ".join(docs_analysis.get("warnings", []))
        detail = f" 抓取提示：{warnings}" if warnings else ""
        raise ValueError(f"文档正文不足，Agent 无法判断接口配置。请补充更多文档链接、OpenAPI/Swagger 链接，或提供一条 curl 示例。{detail}")

    try:
        agent_draft = await asyncio.wait_for(
            _infer_remote_api_draft_with_agent(
                docs_urls=docs_urls,
                docs_text=docs_text,
                req=req,
                docs_analysis=docs_analysis,
            ),
            timeout=REMOTE_API_AGENT_TIMEOUT_SECONDS,
        )
    except TimeoutError as err:
        raise ValueError(
            f"Agent 推理超时（{REMOTE_API_AGENT_TIMEOUT_SECONDS}s）。请补充 curl 示例、接口地址，或更具体的接口文档后重试。"
        ) from err
    except Exception as err:
        raise ValueError(f"Agent 没能从当前文档判断完整表单。请补充更具体的接口文档、OpenAPI/Swagger 链接，或 curl 示例。原因：{err}") from err

    return _build_remote_api_assist_resp_from_agent_draft(req, docs_analysis, agent_draft)


def build_remote_api_assist_draft(req: RemoteApiAssistReq) -> RemoteApiAssistResp:
    docs_urls = _resolve_docs_urls(req.docs_url, req.docs_urls)
    docs_analysis = _analyze_docs_bundle(docs_urls) if docs_urls else {}
    return _build_remote_api_assist_draft_from_analysis(req, docs_urls, docs_analysis)


def _build_remote_api_assist_draft_from_analysis(
    req: RemoteApiAssistReq,
    docs_urls: list[str],
    docs_analysis: dict[str, Any],
) -> RemoteApiAssistResp:
    explicit_endpoint = (req.endpoint_url or "").strip()
    if _looks_like_docs_endpoint(explicit_endpoint, docs_urls):
        explicit_endpoint = ""

    raw_url = _extract_url(req.sample_curl) or explicit_endpoint or docs_analysis.get("endpoint_url", "")
    if not raw_url:
        raise ValueError("至少提供接口地址、文档地址或 curl 示例，智能填表才能分析。")

    method = (
        _extract_method(req.sample_curl)
        or (req.method.strip().upper() if req.method else "")
        or docs_analysis.get("method", "")
        or "GET"
    )
    parsed = urlparse(raw_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("接口地址不是合法的 http/https URL")

    warnings: list[str] = list(docs_analysis.get("warnings", []))
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/"
    display_name = req.display_name.strip() or docs_analysis.get("display_name", "") or _guess_display_name(parsed)
    operation_seed = (
        req.display_name
        or docs_analysis.get("display_name")
        or f"{method.lower()}_{path.strip('/').replace('/', '_') or 'root'}"
    )
    operation_id = _safe_operation_id(operation_seed)
    params = _merge_params(_extract_params_from_url(parsed), docs_analysis.get("params", []))

    explicit_auth_type = (req.auth_type or "").strip()
    auth_type = docs_analysis.get("auth_type", "none") if explicit_auth_type in {"", "none"} else explicit_auth_type
    auth_key_name = _pick_value(req.api_key_name, docs_analysis.get("api_key_name"))
    auth_config = normalize_remote_api_auth_config(
        {
            "type": auth_type,
            "token": req.api_key,
            "key_name": auth_key_name,
        }
    )
    if auth_config.get("auth_type") == "APIKey" and auth_config.get("in") == "query":
        key_name = auth_config.get("name")
        params = [param for param in params if not (param.location == "query" and param.name == key_name)]
    elif req.api_key and auth_type == "none":
        warnings.append("已提供 API Key，但认证方式仍是无认证；如需自动携带，请改成 API Key 查询参数或请求头。")

    description = req.description.strip() or docs_analysis.get("description", "") or f"调用 {parsed.netloc}{path}"
    simple_api_config = SimpleApiConfig(
        base_url=base_url,
        path=path,
        method=method,
        operation_id=operation_id,
        summary=display_name,
        description=description,
        params=params,
    )

    return RemoteApiAssistResp(
        display_name=display_name,
        description=description,
        simple_api_config=simple_api_config,
        auth_config=auth_config,
        openapi_schema=build_openapi_schema_from_simple_config(simple_api_config),
        warnings=warnings,
    )


def _build_remote_api_assist_resp_from_agent_draft(
    req: RemoteApiAssistReq,
    docs_analysis: dict[str, Any],
    agent_draft: dict[str, Any] | AgenticRemoteApiDraft,
) -> RemoteApiAssistResp:
    model = agent_draft if isinstance(agent_draft, AgenticRemoteApiDraft) else AgenticRemoteApiDraft(**agent_draft)
    raw_url = _extract_url(req.sample_curl) or model.endpoint_url or (req.endpoint_url or "").strip()
    if _looks_like_docs_endpoint(raw_url, _resolve_docs_urls(req.docs_url, req.docs_urls)):
        raise ValueError("Agent 返回的是文档或 OpenAPI/Swagger 规格文件地址，不是可调用的业务接口地址。请补充具体接口页、OpenAPI servers/paths 信息，或提供 curl 示例。")
    parsed = urlparse(raw_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Agent 没有返回合法的接口 URL")

    method = _extract_method(req.sample_curl) or (req.method.strip().upper() if req.method else "") or model.method or "GET"
    display_name = req.display_name.strip()
    operation_summary = model.display_name or _guess_display_name(parsed)
    provided_description = req.description.strip()
    if _is_missing_or_placeholder_description(provided_description, parsed):
        provided_description = ""
    agent_description = model.description.strip()
    if _is_missing_or_placeholder_description(agent_description, parsed):
        agent_description = ""
    if not agent_description and display_name and operation_summary and operation_summary.lower() != display_name.lower():
        agent_description = operation_summary
    description = provided_description or agent_description
    if _is_missing_or_placeholder_description(description, parsed):
        raise ValueError("Agent 没有从文档生成有效描述。请补充更具体的接口文档、OpenAPI/Swagger 链接，或 curl 示例。")
    operation_id = _safe_operation_id(display_name or operation_summary or f"{method.lower()}_{(parsed.path or '/').strip('/').replace('/', '_') or 'root'}")
    auth_config = normalize_remote_api_auth_config(
        {
            "type": model.auth_type,
            "token": req.api_key,
            "key_name": model.api_key_name,
        }
    )
    if req.api_key and model.auth_type == "none":
        raise ValueError("已拿到 API Key，但 Agent 没有识别出它应该放在 Query、Header 还是 Bearer 中。请补一个 curl 示例，或在高级设置里手动选择认证方式。")
    if req.api_key and model.auth_type in {"api_key_query", "api_key_header"} and not model.api_key_name.strip():
        raise ValueError("已识别 API Key 认证，但没有识别出字段名。请补充包含 access_key/api_key/x-api-key 的文档或 curl 示例。")
    params = _merge_params(_extract_params_from_url(parsed), model.params)
    if auth_config.get("auth_type") == "APIKey" and auth_config.get("in") == "query":
        key_name = auth_config.get("name")
        params = [param for param in params if not (param.location == "query" and param.name == key_name)]
    warnings = list(docs_analysis.get("warnings", []))
    required_param_names = [param.name for param in params if param.required and param.location in {"query", "path", "header"}]
    probe_args = _normalize_probe_args(model.probe_args, params)
    if required_param_names:
        missing_probe_args = [name for name in required_param_names if name not in probe_args]
        if missing_probe_args:
            warnings.append(
                f"Agent 已识别出必填业务参数：{', '.join(missing_probe_args)}。未找到安全测试值时，连通性检测会返回缺少测试参数，不会发起真实请求。"
            )
        else:
            warnings.append(
                f"Agent 已为必填业务参数生成测试值：{', '.join(required_param_names)}。连通性检测会使用这些示例值发起真实请求。"
            )

    simple_api_config = SimpleApiConfig(
        base_url=f"{parsed.scheme}://{parsed.netloc}",
        path=parsed.path or "/",
        method=method,
        operation_id=operation_id,
        summary=operation_summary,
        description=description,
        params=params,
    )
    return RemoteApiAssistResp(
        display_name=display_name,
        description=description,
        simple_api_config=simple_api_config,
        auth_config=auth_config,
        openapi_schema=build_openapi_schema_from_simple_config(simple_api_config),
        probe_args=probe_args,
        warnings=warnings,
    )


def _build_remote_api_agent_prompt(
    *,
    docs_urls: list[str],
    docs_text: str,
    req: RemoteApiAssistReq,
    docs_analysis: dict[str, Any],
) -> str:
    compact_docs = re.sub(r"\s+", " ", docs_text or "").strip()[:MAX_AGENT_DOC_CHARS]
    hints = {
        "docs_urls": docs_urls,
        "provided_endpoint_url": req.endpoint_url,
        "provided_sample_curl": req.sample_curl,
        "provided_method": req.method,
        "provided_display_name": req.display_name,
        "provided_description": req.description,
        "api_key_provided": bool(req.api_key),
        "api_key_name_hint": req.api_key_name,
        "auth_type_hint": req.auth_type,
    }
    output_schema = {
        "display_name": "short operation label for the API capability; the user will choose the final tool name",
        "description": "Chinese one sentence tool capability description generated from the documentation; do not just repeat the URL",
        "endpoint_url": "absolute API endpoint URL, not a docs page",
        "method": "GET|POST|PUT|PATCH|DELETE",
        "auth_type": "none|bearer|basic|api_key_query|api_key_header",
        "api_key_name": "query/header key name such as access_key, api_key, X-API-Key",
        "params": [
            {
                "name": "parameter name, excluding the API key parameter when auth_type is api_key_query",
                "in": "query|path|header",
                "required": False,
                "description": "parameter meaning",
                "type": "string|integer|number|boolean",
            }
        ],
        "probe_args": "safe sample values for required runtime parameters, for example {'symbols':'AAPL'}; omit secrets and auth fields",
    }
    return (
        "You are filling a Remote API tool form from rendered API documentation.\n"
        "Infer the best single default endpoint for a useful tool. Prefer quickstart/getting-started examples over docs navigation URLs.\n"
        "If the user did not provide a concrete endpoint or curl example, prefer a smoke-testable endpoint that can be called with only authentication over endpoints that require business identifiers such as symbols, id, or date.\n"
        "If every useful endpoint needs business input, mark those parameters as required and infer safe probe_args from docs examples, public examples, or domain-common sample values.\n"
        "For stock symbols, use a public liquid example such as AAPL unless the docs show a better example. For dates, prefer a stable historical date or omit optional dates.\n"
        "The user chooses the final tool name. You generate the capability description and operation metadata.\n"
        "The description field is required. Write it in Chinese, based on the documentation, explaining what the tool can do.\n"
        "Do not use generic descriptions like 'call this URL' or '调用 api.example.com/path'.\n"
        "Do not use OpenAPI/Swagger spec file URLs, docs pages, SwaggerHub API URLs, or documentation navigation URLs as endpoint_url.\n"
        "If the docs link to an OpenAPI spec, use its servers + paths to infer the real business API endpoint.\n"
        "Never include the secret API key value in your output. If authentication uses a query or header API key, output only the key name.\n"
        "Return only valid JSON matching this schema:\n"
        f"{json.dumps(output_schema, ensure_ascii=False)}\n\n"
        f"Inputs:\n{json.dumps(hints, ensure_ascii=False)}\n\n"
        f"Rendered documentation text:\n{compact_docs}"
    )


def _is_missing_or_placeholder_description(description: str, parsed_url) -> bool:
    cleaned = (description or "").strip()
    if not cleaned:
        return True
    lowered = cleaned.lower()
    host = (parsed_url.netloc or "").lower()
    path = (parsed_url.path or "").lower()
    if host and host in lowered and len(cleaned) <= len(host) + len(path or "") + 30:
        return True
    if host and host in lowered and any(token in lowered for token in ["调用", "call"]):
        return True
    if path and path != "/" and path in lowered and len(cleaned) < len(host) + len(path) + 20:
        return True
    generic_phrases = [
        "remote api tool",
        "call api",
        "调用 api",
        "调用接口",
        "通过远程接口提供能力",
    ]
    return any(phrase in lowered for phrase in generic_phrases)


async def _infer_remote_api_draft_with_agent(
    *,
    docs_urls: list[str],
    docs_text: str,
    req: RemoteApiAssistReq,
    docs_analysis: dict[str, Any],
) -> dict[str, Any]:
    model = ModelManager.get_tool_invocation_model()
    messages = [
        SystemMessage(content="You extract API integration configuration and return strict JSON only."),
        HumanMessage(
            content=_build_remote_api_agent_prompt(
                docs_urls=docs_urls,
                docs_text=docs_text,
                req=req,
                docs_analysis=docs_analysis,
            )
        ),
    ]
    normalized_messages = normalize_messages_for_model(messages, model=model)
    response = await model.ainvoke(normalized_messages)
    content = strip_think_tags(str(getattr(response, "content", "") or "")).strip()
    data = _extract_json_object(content)
    return AgenticRemoteApiDraft(**data).model_dump(by_alias=True)


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start:end + 1])


def _resolve_docs_urls(primary: str, others: list[str] | None) -> list[str]:
    candidates = [*(others or []), primary]
    resolved: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        for url in re.findall(r"https?://[^\s'\"<>]+", candidate or ""):
            normalized = _sanitize_docs_url(url.rstrip(".,);"))
            if normalized and normalized not in seen:
                seen.add(normalized)
                resolved.append(normalized)
    return resolved[:MAX_DOC_SOURCE_COUNT]


def _sanitize_docs_url(url: str) -> str:
    parsed = urlparse(url)
    kept_query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if not key.lower().startswith("utm_")]
    return urlunparse(parsed._replace(query=urlencode(kept_query), fragment=""))


def _looks_like_docs_endpoint(endpoint_url: str, docs_urls: list[str]) -> bool:
    candidate = (endpoint_url or "").strip()
    if not candidate:
        return False
    lowered = candidate.lower()
    if any(token in lowered for token in ["/documentation", "/docs", "/swagger", "/openapi", "postman"]):
        return True
    return candidate in set(docs_urls or [])


def _extract_url(sample_curl: str) -> str:
    if not sample_curl:
        return ""
    match = re.search(r"https?://[^\s'\"\\]+", sample_curl)
    return match.group(0).rstrip(".,);") if match else ""


def _extract_method(sample_curl: str) -> str:
    if not sample_curl:
        return ""
    match = re.search(r"(?:^|\s)-X\s+([A-Za-z]+)", sample_curl)
    return match.group(1).upper() if match else ""


def _extract_params_from_url(parsed_url) -> list[SimpleApiParamConfig]:
    params: list[SimpleApiParamConfig] = []
    path_seen = set()
    for token in re.findall(r"{([^{}]+)}", parsed_url.path or ""):
        name = token.strip()
        if not name or name in path_seen:
            continue
        path_seen.add(name)
        params.append(
            SimpleApiParamConfig(
                name=name,
                location="path",
                required=True,
                description=f"Path parameter: {name}",
                type="string",
            )
        )

    for key, _ in parse_qsl(parsed_url.query or "", keep_blank_values=True):
        if not key:
            continue
        params.append(
            SimpleApiParamConfig(
                name=key,
                location="query",
                required=False,
                description=f"Query parameter: {key}",
                type="string",
            )
        )
    return params


def _guess_display_name(parsed_url) -> str:
    host = parsed_url.netloc.replace("api.", "").split(":")[0]
    endpoint = parsed_url.path.strip("/").split("/")[-1] if parsed_url.path else "api"
    return f"{host} {endpoint}".strip()


def _safe_operation_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_")
    if not cleaned:
        cleaned = "call_api"
    if cleaned[0].isdigit():
        cleaned = f"api_{cleaned}"
    return cleaned


def _pick_value(primary: Optional[str], secondary: Optional[str], fallback: str = "") -> str:
    if primary and str(primary).strip():
        return str(primary).strip()
    if secondary and str(secondary).strip():
        return str(secondary).strip()
    return fallback


def _merge_params(primary: list[SimpleApiParamConfig], secondary: list[SimpleApiParamConfig]) -> list[SimpleApiParamConfig]:
    merged: list[SimpleApiParamConfig] = []
    seen: set[tuple[str, str]] = set()
    for param in [*primary, *secondary]:
        key = (param.location, param.name)
        if not param.name or key in seen:
            continue
        merged.append(param)
        seen.add(key)
    return merged


def _normalize_probe_args(probe_args: dict[str, Any] | None, params: list[SimpleApiParamConfig]) -> dict[str, Any]:
    if not isinstance(probe_args, dict):
        return {}
    param_names = {param.name for param in params if param.name}
    normalized: dict[str, Any] = {}
    for key, value in probe_args.items():
        name = str(key).strip()
        if not name or name not in param_names:
            continue
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        normalized[name] = value
    return normalized


def _analyze_docs_bundle(docs_urls: list[str]) -> dict[str, Any]:
    docs_bundle = _collect_docs_text_bundle(docs_urls)
    source_text = docs_bundle.get("_source_text", "")
    if not source_text:
        warnings = docs_bundle.get("warnings", [])
        return {"warnings": warnings} if warnings else {}

    text = docs_bundle.get("_plain_text", source_text)
    warnings: list[str] = list(docs_bundle.get("warnings", []))
    endpoint = _extract_doc_endpoint(source_text)
    auth_type, api_key_name = _extract_doc_auth(source_text)
    method = _extract_doc_method(source_text)
    params = _extract_doc_params(source_text)
    description = _extract_doc_description(text or source_text)
    display_name = _extract_doc_display_name(text or source_text, endpoint)
    if endpoint and endpoint.startswith("http://") and "https://" not in source_text:
        warnings.append("文档示例使用的是 HTTP；如果服务支持 HTTPS，建议优先改成 HTTPS。")

    return {
        "endpoint_url": endpoint,
        "auth_type": auth_type,
        "api_key_name": api_key_name,
        "method": method,
        "params": params,
        "description": description,
        "display_name": display_name,
        "warnings": warnings,
        "_source_text": source_text,
    }


def _collect_docs_text_bundle(docs_urls: list[str]) -> dict[str, Any]:
    combined_parts: list[str] = []
    combined_raw_parts: list[str] = []
    warnings: list[str] = []
    visited: set[str] = set()
    queue = list(docs_urls)

    while queue and len(visited) < MAX_DOC_SOURCE_COUNT:
        current_url = queue.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)
        try:
            html_text, text = _fetch_docs_page(current_url)
        except Exception as err:
            warnings.append(f"文档抓取失败：{current_url} ({err})")
            continue
        if html_text:
            combined_raw_parts.append(html_text)
        if text:
            combined_parts.append(text)
        for related_url in _extract_related_doc_links(html_text, current_url):
            if related_url not in visited and related_url not in queue and len(visited) + len(queue) < MAX_DOC_SOURCE_COUNT:
                queue.append(related_url)

    text = " ".join(part for part in combined_parts if part).strip()
    raw_text = " ".join(part for part in combined_raw_parts if part).strip()
    source_text = " ".join(part for part in [text, raw_text] if part).strip()
    if not source_text:
        return {"warnings": warnings} if warnings else {}
    return {
        "warnings": warnings,
        "_source_text": source_text,
        "_plain_text": text,
    }

    endpoint = _extract_doc_endpoint(source_text)
    auth_type, api_key_name = _extract_doc_auth(source_text)
    method = _extract_doc_method(source_text)
    params = _extract_doc_params(source_text)
    description = _extract_doc_description(text or source_text)
    display_name = _extract_doc_display_name(text or source_text, endpoint)
    if endpoint and endpoint.startswith("http://") and "https://" not in source_text:
        warnings.append("文档示例使用的是 HTTP；如果服务支持 HTTPS，建议优先改成 HTTPS。")

    return {
        "endpoint_url": endpoint,
        "auth_type": auth_type,
        "api_key_name": api_key_name,
        "method": method,
        "params": params,
        "description": description,
        "display_name": display_name,
        "warnings": warnings,
        "_source_text": source_text,
    }


def _fetch_docs_page(docs_url: str) -> tuple[str, str]:
    request_error: Exception | None = None
    try:
        response = requests.get(
            docs_url,
            timeout=DOC_FETCH_TIMEOUT_SECONDS,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ZunoRemoteApiAssist/1.0",
                "Accept": "text/html,application/xhtml+xml,application/json,text/plain;q=0.9,*/*;q=0.8",
            },
        )
        response.raise_for_status()
        normalized_html, normalized_text = _normalize_docs_html(response.text)
        if _should_render_docs_with_browser(normalized_html, normalized_text):
            try:
                rendered_html, rendered_text = _fetch_docs_page_with_browser(docs_url)
                if len(rendered_text) > len(normalized_text):
                    return rendered_html, rendered_text
            except Exception:
                return normalized_html, normalized_text
        return normalized_html, normalized_text
    except Exception as err:
        request_error = err

    try:
        return _fetch_docs_page_with_browser(docs_url)
    except Exception as browser_error:
        raise RuntimeError(f"{request_error}; browser render fallback failed: {browser_error}") from browser_error


def _normalize_docs_html(raw_html: str) -> tuple[str, str]:
    normalized_html = html.unescape(raw_html or "")
    normalized_text = re.sub(r"<script[\s\S]*?</script>", " ", normalized_html, flags=re.IGNORECASE)
    normalized_text = re.sub(r"<style[\s\S]*?</style>", " ", normalized_text, flags=re.IGNORECASE)
    normalized_text = re.sub(r"<[^>]+>", " ", normalized_text)
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()
    return normalized_html, normalized_text


def _should_render_docs_with_browser(html_text: str, plain_text: str) -> bool:
    lowered = (html_text or "").lower()
    if len(plain_text or "") < MIN_DOC_TEXT_LENGTH_FOR_RULE_EXTRACTION:
        return True
    js_app_tokens = [
        'id="root"',
        'id="app"',
        "__next_data__",
        "swagger-ui",
        "redoc",
        "portal.swaggerhub.com",
    ]
    return any(token in lowered for token in js_app_tokens) and "access_key" not in (plain_text or "").lower()


def _fetch_docs_page_with_browser(docs_url: str) -> tuple[str, str]:
    try:
        return _fetch_docs_page_with_playwright(docs_url)
    except Exception as playwright_error:
        try:
            return _fetch_docs_page_with_selenium(docs_url)
        except Exception as selenium_error:
            raise RuntimeError(
                f"playwright render failed: {playwright_error}; selenium fallback failed: {selenium_error}"
            ) from selenium_error


def _fetch_docs_page_with_playwright(docs_url: str) -> tuple[str, str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as err:
        raise RuntimeError("playwright is not available") from err

    with sync_playwright() as p:
        chrome_path = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
        launch_kwargs = {"headless": True}
        if chrome_path:
            launch_kwargs["executable_path"] = chrome_path
        browser = p.chromium.launch(**launch_kwargs)
        try:
            page = browser.new_page(
                viewport={"width": 1440, "height": 1200},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ZunoRemoteApiAssist/1.0",
            )
            page.goto(docs_url, wait_until="domcontentloaded", timeout=DOC_BROWSER_RENDER_TIMEOUT_SECONDS * 1000)
            page.wait_for_function(
                "() => document.body && document.body.innerText && document.body.innerText.trim().length > 80",
                timeout=DOC_BROWSER_RENDER_TIMEOUT_SECONDS * 1000,
            )
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                pass
            inner_text = page.locator("body").inner_text(timeout=3000)
            page_source = page.content()
            normalized_html = html.unescape(page_source)
            normalized_text = re.sub(r"\s+", " ", str(inner_text)).strip()
            return normalized_html, normalized_text
        finally:
            browser.close()


def _fetch_docs_page_with_selenium(docs_url: str) -> tuple[str, str]:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
    except Exception as err:
        raise RuntimeError("selenium is not available") from err

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1200")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ZunoRemoteApiAssist/1.0")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_page_load_timeout(DOC_BROWSER_RENDER_TIMEOUT_SECONDS)
        driver.get(docs_url)
        WebDriverWait(driver, DOC_BROWSER_RENDER_TIMEOUT_SECONDS).until(
            lambda browser: browser.execute_script(
                "return document.body && document.body.innerText && document.body.innerText.trim().length > 80"
            )
        )
        inner_text = driver.execute_script("return document.body ? document.body.innerText : ''") or ""
        page_source = driver.page_source or ""
        normalized_html = html.unescape(page_source)
        normalized_text = re.sub(r"\s+", " ", str(inner_text)).strip()
        return normalized_html, normalized_text
    finally:
        driver.quit()


def _extract_related_doc_links(html_text: str, current_url: str) -> list[str]:
    parsed_current = urlparse(current_url)
    current_host = parsed_current.netloc.lower()
    current_parts = [part for part in parsed_current.path.split("/") if part]
    current_root = "/" + "/".join(current_parts[:2]) if len(current_parts) >= 2 else parsed_current.path.rsplit("/", 1)[0]
    links: list[str] = []
    seen: set[str] = set()
    for href in re.findall(r'href=["\']([^"\']+)["\']', html_text, flags=re.IGNORECASE):
        candidate = urljoin(current_url, href)
        parsed = urlparse(candidate)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != current_host:
            continue
        lowered = candidate.lower()
        same_doc_tree = bool(current_root and parsed.path.startswith(current_root))
        has_doc_signal = any(
            token in lowered
            for token in ["getting-started", "quickstart", "openapi", "swagger", "api-v-", "documentation", "reference", "endpoint", "docs"]
        )
        if not (same_doc_tree or has_doc_signal):
            continue
        normalized = candidate.split("#", 1)[0]
        if normalized not in seen and normalized != current_url:
            seen.add(normalized)
            links.append(normalized)
    return links[:5]


def _extract_doc_endpoint(text: str) -> str:
    urls = [item.rstrip(".,);") for item in re.findall(r"https?://[^\s'\"<>]+", text)]
    if urls:
        scored = sorted(urls, key=_score_doc_url, reverse=True)
        return scored[0]

    base_match = re.search(r"Base URL[:\s]+(https?://[^\s'\"<>]+)", text, re.IGNORECASE)
    if base_match:
        return base_match.group(1).rstrip(".,);")

    return ""


def _score_doc_url(value: str) -> tuple[int, int]:
    score = 0
    lowered = value.lower()
    if "api." in lowered:
        score += 5
    if "access_key=" in lowered:
        score += 4
    if "/check" in lowered:
        score += 3
    if "?" in lowered:
        score += 2
    if any(token in lowered for token in ["documentation", "getting-started", "quickstart", "docs/"]):
        score -= 10
    return score, -len(value)


def _extract_doc_auth(text: str) -> tuple[str, str]:
    lowered = text.lower()
    if "access_key" in lowered:
        return "api_key_query", "access_key"
    if "x-api-key" in lowered:
        return "api_key_header", "x-api-key"
    if "authorization: bearer" in lowered or "bearer token" in lowered:
        return "bearer", ""
    if "basic auth" in lowered or "authorization: basic" in lowered:
        return "basic", ""
    return "none", ""


def _extract_doc_method(text: str) -> str:
    match = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\b", text)
    return match.group(1).upper() if match else ""


IGNORED_DOC_PARAM_NAMES = {
    "orgid",
    "response_type",
    "client_id",
    "redirect_uri",
    "identity_provider",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "action",
    "scope",
    "state",
    "nonce",
    "code",
    "code_challenge",
    "code_challenge_method",
    "prompt",
    "method",
    "summary",
    "operationid",
    "servers",
    "documentations",
    "paths",
    "components",
    "version",
    "info",
    "title",
    "sections",
    "currentproductrole",
    "productslug",
    "currentproduct",
    "orgname",
    "name",
    "description",
}


def _extract_doc_params(text: str) -> list[SimpleApiParamConfig]:
    params: list[SimpleApiParamConfig] = []
    seen: set[str] = set()
    candidates: list[str] = []
    candidates.extend(re.findall(r"(?:\?|&)([a-zA-Z_][a-zA-Z0-9_]*)=", text))

    for key, description in re.findall(r'"([a-z_][a-z0-9_]*)","([^"]{5,160})"', text, flags=re.IGNORECASE):
        lowered_description = description.lower()
        if any(
            token in lowered_description
            for token in [
                "parameter",
                "authenticate",
                "request",
                "response",
                "include",
                "output",
                "language",
                "hostname",
                "security",
                "lookup",
                "comma-separated",
            ]
        ):
            candidates.append(key)

    for key in candidates:
        normalized = key.strip()
        lowered = normalized.lower()
        if not normalized or lowered in seen or lowered in IGNORED_DOC_PARAM_NAMES or lowered == "access_key":
            continue
        params.append(
            SimpleApiParamConfig(
                name=normalized,
                location="query",
                required=False,
                description=f"Query parameter: {normalized}",
                type="string",
            )
        )
        seen.add(lowered)
    return params


def _extract_doc_description(text: str) -> str:
    patterns = [
        r"(?:[A-Za-z0-9_-]+\s+API|API)\s+offers\s+(.*?)(?:Quickstart Guide|Getting Started|API Access Key)",
        r"(?:used to|is used to)\s+(.*?)(?:\.| Step \d+ | Quickstart Guide)",
        r"(Quickstart Guide .*?)(?: Step \d+ | Support & Resources | Example )",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        description = match.group(1).strip()
        description = re.sub(r"\s+", " ", description).strip(" .")
        if description:
            return description[:180]
    return ""


def _extract_doc_display_name(text: str, endpoint_url: str) -> str:
    title_match = re.search(r"\b([A-Z][A-Za-z0-9_-]{2,})\b(?: API| Quickstart Guide| Documentation)", text)
    if title_match:
        candidate = title_match.group(1).strip()
        if candidate.lower() not in {"api", "documentation", "quickstart", "guide"}:
            return candidate
    host_match = re.search(r"Base URL[:\s]+https?://(?:api\.)?([A-Za-z0-9-]+)", text, re.IGNORECASE)
    if host_match:
        return host_match.group(1)
    if endpoint_url:
        parsed = urlparse(endpoint_url)
        host = parsed.netloc.replace("api.", "").split(":")[0]
        if host:
            return host.split(".")[0]
        return _guess_display_name(parsed)
    return "远程 API 工具"
