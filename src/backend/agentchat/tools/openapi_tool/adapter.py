import os
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urlunparse

import httpx


class OpenAPIToolAdapter:
    """
    OpenAPI → LLM Tool Adapter (OpenAPI 3.x)
    """

    def __init__(
        self,
        openapi_schema: Dict[str, Any],
        auth_config: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        self.schema = openapi_schema
        self.timeout = timeout
        self.auth_config = auth_config or {}

        # 自动提取 base URL
        self.base_url = self._extract_base_url()

        # tool 执行元数据
        self._tool_meta: Dict[str, Dict] = {}

        # 生成 tools
        self.tools = self._generate_tools()

    # 提取 base_url（OpenAPI 3.x）
    def _extract_base_url(self) -> str:
        servers = self.schema.get("servers")
        if not servers:
            raise ValueError("OpenAPI schema missing 'servers'")

        server = servers[0]
        url = server["url"]

        # 解析变量模板
        variables = server.get("variables", {})
        for k, v in variables.items():
            url = url.replace(f"{{{k}}}", v.get("default", ""))

        return self._normalize_localhost_url(url.rstrip("/"))

    def _normalize_localhost_url(self, url: str) -> str:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname not in {"127.0.0.1", "localhost"}:
            return url

        if not os.path.exists("/.dockerenv"):
            return url

        netloc = parsed.netloc
        if hostname == "localhost":
            netloc = netloc.replace("localhost", "host.docker.internal", 1)
        else:
            netloc = netloc.replace("127.0.0.1", "host.docker.internal", 1)
        return urlunparse(parsed._replace(netloc=netloc))


    def _generate_tools(self) -> List[Dict[str, Any]]:
        """
        生成符合 OpenAI Tool Calling 规范的 tools
        """
        tools = []
        seen_names = set()

        for path, methods in self.schema.get("paths", {}).items():
            for method, spec in methods.items():

                operation_id = spec.get("operationId")
                if not operation_id:
                    continue

                operation_id = operation_id.strip()
                if not operation_id:
                    continue

                # 清理非法字符，避免 LLM 报错
                import re
                operation_id = re.sub(r"[^a-zA-Z0-9_]", "_", operation_id)

                if operation_id in seen_names:
                    raise ValueError(f"Duplicate operationId: {operation_id}")

                seen_names.add(operation_id)

                parameters_schema = self._build_parameters_schema(spec)

                tool_schema = {
                    "type": "function",
                    "function": {
                        "name": operation_id,
                        "description": (
                                spec.get("summary")
                                or spec.get("description")
                                or f"{method.upper()} {path}"
                        ),
                        "parameters": parameters_schema,
                    },
                }

                tools.append(tool_schema)

                # 保存执行元数据
                self._tool_meta[operation_id] = {
                    "path": path,
                    "method": method.upper(),
                    "spec": spec,
                }

        return tools

    def get_primary_operation_id(self) -> Optional[str]:
        if not self.tools:
            return None
        return self.tools[0].get("function", {}).get("name")

    def get_tool_parameters_schema(self, tool_name: str) -> Dict[str, Any]:
        for tool in self.tools:
            function_schema = tool.get("function", {})
            if function_schema.get("name") == tool_name:
                return function_schema.get("parameters", {}) or {}
        return {}

    def _build_parameters_schema(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        将 OpenAPI 参数转换为 OpenAI 可用 JSON Schema
        """
        properties = {}
        required = []

        # ===== path/query/header 参数 =====
        for param in spec.get("parameters", []):
            name = param.get("name")
            if not name:
                continue

            schema = param.get("schema", {"type": "string"})
            cleaned = self._clean_schema(schema)

            # 添加描述，增强模型理解
            if param.get("description") and "description" not in cleaned:
                cleaned["description"] = param["description"]

            properties[name] = cleaned

            if param.get("required"):
                required.append(name)

        # ===== requestBody =====
        body = spec.get("requestBody", {})
        content = body.get("content", {})

        json_schema = content.get("application/json", {}).get("schema")

        if json_schema:
            cleaned = self._clean_schema(json_schema)

            # 如果 body 是 object
            if cleaned.get("type") == "object":
                properties.update(cleaned.get("properties", {}))
                required.extend(cleaned.get("required", []))
            else:
                # 非 object body（极少见）
                properties["body"] = cleaned
                if body.get("required"):
                    required.append("body")

        return {
            "type": "object",
            "properties": properties,
            "required": list(set(required)),
        }

    def _clean_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗 OpenAPI schema → 标准 JSON Schema（OpenAI 兼容）
        """
        if not isinstance(schema, dict):
            return {"type": "string"}

        allowed_keys = {
            "type",
            "properties",
            "items",
            "required",
            "description",
            "enum",
            "format",
        }

        cleaned = {}

        for key, value in schema.items():
            if key not in allowed_keys:
                continue

            if key == "properties":
                cleaned[key] = {
                    k: self._clean_schema(v)
                    for k, v in value.items()
                }

            elif key == "items":
                cleaned[key] = self._clean_schema(value)

            else:
                cleaned[key] = value

        # 如果没有 type，默认 string
        if "type" not in cleaned:
            cleaned["type"] = "string"

        return cleaned

    # 构造鉴权 Header
    def _build_auth_headers(self) -> Dict[str, str]:
        if not self.auth_config:
            return {}

        auth_type = self.auth_config.get("auth_type")
        data = self.auth_config.get("data")

        if auth_type == "Bearer":
            return {"Authorization": f"Bearer {data}"}

        if auth_type == "Basic":
            return {"Authorization": f"Basic {data}"}

        if auth_type == "APIKey" and (self.auth_config.get("in") or "header").strip().lower() != "query":
            key_name = (self.auth_config.get("name") or "X-API-Key").strip() or "X-API-Key"
            return {key_name: data}

        if auth_type == "Header":
            # data 应该是 dict
            return data

        return {}

    def _apply_auth(self, query_params: Dict[str, Any], headers: Dict[str, str]) -> None:
        if not self.auth_config:
            return

        auth_type = self.auth_config.get("auth_type")
        data = self.auth_config.get("data")
        if auth_type == "APIKey" and data:
            location = (self.auth_config.get("in") or "header").strip().lower()
            key_name = (self.auth_config.get("name") or "X-API-Key").strip() or "X-API-Key"
            if location == "query":
                query_params[key_name] = data
                return

        headers.update(self._build_auth_headers())

    # 执行 tool
    async def execute(self, **kwargs) -> Any:
        """
        执行 OpenAPI 工具调用
        LangChain 会将参数展开为 kwargs
        """

        # tool 名称由 LangChain 注入
        tool_name = kwargs.pop("_tool_name", None)

        if not tool_name:
            raise ValueError("Tool name not provided")

        if tool_name not in self._tool_meta:
            raise ValueError(f"Unknown tool: {tool_name}")

        meta = self._tool_meta[tool_name]

        path = meta["path"]
        method = meta["method"]

        path_params = {}
        query_params = {}
        json_body = {}

        # 替换 path 参数
        for key, value in kwargs.items():
            if f"{{{key}}}" in path:
                path = path.replace(f"{{{key}}}", str(value))
                path_params[key] = value
            else:
                query_params[key] = value

        url = f"{self.base_url}{path}"

        # body 支持（POST/PUT/PATCH）
        if method in ["POST", "PUT", "PATCH"]:
            json_body = kwargs

        import httpx

        headers = {}
        self._apply_auth(query_params, headers)

        # auth 处理
        if self.auth_config:
            if self.auth_config.get("auth_type") == "Bearer":
                headers["Authorization"] = f"Bearer {self.auth_config['data']}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method,
                url,
                params=query_params or None,
                json=json_body or None,
                headers=headers,
            )

        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        if "json" in content_type:
            return response.json()
        text = response.text.strip()
        return text or {"status_code": response.status_code}

    async def test_connectivity(
        self,
        test_args: Optional[Dict[str, Any]] = None,
        *,
        operation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        operation_id = operation_id or self.get_primary_operation_id()
        if not operation_id:
            raise ValueError("OpenAPI schema does not contain any callable operation")

        parameters_schema = self.get_tool_parameters_schema(operation_id)
        required = list(parameters_schema.get("required") or [])
        provided_args = dict(test_args or {})
        missing_required = [name for name in required if name not in provided_args]

        meta = self._tool_meta.get(operation_id) or {}
        path = meta.get("path") or ""
        tested_url = f"{self.base_url}{path}"

        if missing_required:
            return {
                "ok": False,
                "runtime_type": "remote_api",
                "summary": "缺少必填测试参数，暂时无法发起真实请求",
                "details": [f"默认测试接口：{operation_id}", f"目标地址：{tested_url}"],
                "warnings": [f"还缺少这些必填参数：{', '.join(missing_required)}"],
                "executed": False,
                "operation_id": operation_id,
                "tested_url": tested_url,
            }

        try:
            result = await self.execute(_tool_name=operation_id, **provided_args)
        except Exception as err:
            return {
                "ok": False,
                "runtime_type": "remote_api",
                "summary": "API real request failed",
                "details": [f"operation: {operation_id}", f"target: {tested_url}", str(err)],
                "warnings": [str(err)],
                "executed": True,
                "operation_id": operation_id,
                "tested_url": tested_url,
            }
        result_type = type(result).__name__
        result_hint = ""
        if isinstance(result, dict):
            preview_keys = ", ".join(list(result.keys())[:5])
            result_hint = f"返回对象字段：{preview_keys}" if preview_keys else "返回对象为空"
        elif isinstance(result, list):
            result_hint = f"返回数组长度：{len(result)}"
        else:
            result_hint = f"返回类型：{result_type}"

        return {
            "ok": True,
            "runtime_type": "remote_api",
            "summary": "接口真实请求成功，连通性正常",
            "details": [f"已测试接口：{operation_id}", f"目标地址：{tested_url}", result_hint],
            "warnings": [],
            "executed": True,
            "operation_id": operation_id,
            "tested_url": tested_url,
        }

    @staticmethod
    def validate_openapi_schema(openapi_schema):
        """
        验证 OpenAPI schema 是否满足工具生成要求。
        不通过将抛出 ValueError。
        """

        if not isinstance(openapi_schema, dict):
            raise ValueError("OpenAPI schema must be a dictionary")

        version = openapi_schema.get("openapi")
        if not version:
            raise ValueError("Missing 'openapi' field (expected OpenAPI 3.x)")

        if not version.startswith("3."):
            raise ValueError(f"Unsupported OpenAPI version: {version}")

        # 检查 servers
        servers = openapi_schema.get("servers")
        if not servers or not isinstance(servers, list):
            raise ValueError("OpenAPI schema must contain at least one server")

        if "url" not in servers[0]:
            raise ValueError("Server entry missing 'url'")

        # 检查 paths
        paths = openapi_schema.get("paths")
        if not paths:
            raise ValueError("OpenAPI schema missing 'paths'")

        operation_ids = set()

        for path, methods in paths.items():
            if not path.startswith("/"):
                raise ValueError(f"Invalid path: {path}")

            if not isinstance(methods, dict):
                raise ValueError(f"Invalid methods for path: {path}")

            for method, spec in methods.items():

                if method.lower() not in {
                    "get", "post", "put", "patch", "delete", "options", "head"
                }:
                    raise ValueError(f"Invalid HTTP method '{method}' in {path}")

                if not isinstance(spec, dict):
                    raise ValueError(f"Invalid spec for {method.upper()} {path}")

                # operationId 必须存在
                operation_id = spec.get("operationId")
                if not operation_id:
                    raise ValueError(
                        f"Missing operationId for {method.upper()} {path}"
                    )

                # operationId 必须唯一
                if operation_id in operation_ids:
                    raise ValueError(f"Duplicate operationId: {operation_id}")

                operation_ids.add(operation_id)

                # 校验 parameters
                for param in spec.get("parameters", []):
                    if "name" not in param or "in" not in param:
                        raise ValueError(
                            f"Invalid parameter in {operation_id}"
                        )

                    if param["in"] not in {"path", "query", "header", "cookie"}:
                        raise ValueError(
                            f"Invalid parameter location in {operation_id}"
                        )

                # 校验 requestBody
                if "requestBody" in spec:
                    content = spec["requestBody"].get("content", {})
                    if not content:
                        raise ValueError(
                            f"requestBody missing content in {operation_id}"
                        )

                    if "application/json" not in content:
                        raise ValueError(
                            f"{operation_id} only supports application/json body"
                        )
