from __future__ import annotations

import importlib.util
import shutil
import smtplib
import ssl
from typing import Any

import httpx

from agentchat.database.models.tool import ToolTable
from agentchat.schema.tool import ToolConnectivityReq, ToolConnectivityResp
from agentchat.services.simple_api_tool import normalize_remote_api_auth_config
from agentchat.services.tool_creation_service import ToolCreationService
from agentchat.services.user_defined_tool_runtime import get_cli_config_from_auth_config, get_user_defined_runtime_type
from agentchat.tools.cli_tool.adapter import CLIToolAdapter
from agentchat.tools.openapi_tool.adapter import OpenAPIToolAdapter


class ToolConnectivityService:
    @staticmethod
    async def test_system_tool(tool_name: str) -> ToolConnectivityResp:
        from agentchat.api.v1.config import SYSTEM_TOOL_CONFIG_META, _load_runtime_config, _normalize_email_accounts

        meta = SYSTEM_TOOL_CONFIG_META.get(tool_name)
        if not meta:
            raise ValueError("Unsupported system tool")

        _, config_data = _load_runtime_config()
        tool_kind = str(meta.get("tool_kind") or "remote_api")
        values = ToolConnectivityService._system_tool_values(meta, config_data)

        if tool_kind == "smtp_protocol":
            return await ToolConnectivityService._test_system_smtp(config_data, _normalize_email_accounts)
        if tool_kind == "local_dependency":
            return ToolConnectivityService._test_system_local_dependency(tool_name)
        if tool_kind == "public_data_source":
            return await ToolConnectivityService._test_system_public_source(tool_name)
        if tool_kind == "remote_api":
            return await ToolConnectivityService._test_system_remote_api(tool_name, meta, values)

        return ToolConnectivityResp(ok=False, runtime_type="cli", summary=f"Unsupported system tool kind: {tool_kind}", warnings=[tool_kind])

    @staticmethod
    def _system_tool_values(meta: dict[str, Any], config_data: dict[str, Any]) -> dict[str, Any]:
        root = meta.get("root")
        section = meta.get("section")
        if root and section:
            return dict((config_data.get(root) or {}).get(section) or {})
        if root:
            return dict(config_data.get(root) or {})
        return dict(config_data)

    @staticmethod
    def _missing_required_system_fields(meta: dict[str, Any], values: dict[str, Any]) -> list[str]:
        return [
            str(field.get("key"))
            for field in meta.get("fields", [])
            if field.get("required") and not str(values.get(str(field.get("key")), "")).strip()
        ]

    @staticmethod
    async def _test_system_remote_api(tool_name: str, meta: dict[str, Any], values: dict[str, Any]) -> ToolConnectivityResp:
        missing = ToolConnectivityService._missing_required_system_fields(meta, values)
        if missing:
            return ToolConnectivityResp(
                ok=False,
                runtime_type="remote_api",
                summary="系统 API 工具缺少必填配置，未执行真实请求",
                warnings=[f"缺少配置：{', '.join(missing)}"],
                executed=False,
            )

        endpoint = str(values.get("endpoint") or "").strip()
        api_key = str(values.get("api_key") or "").strip()
        method = "GET"
        headers: dict[str, str] = {}
        params: dict[str, Any] = {}

        if tool_name == "get_weather":
            params = {"key": api_key, "city": "110101", "extensions": "base"}
        elif tool_name == "get_delivery":
            headers = {"Authorization": f"APPCODE {api_key}"}
            params = {"no": "test"}
        elif tool_name == "bocha_search":
            method = "POST"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        elif tool_name == "tavily_search":
            endpoint = endpoint or "https://api.tavily.com/search"
            method = "POST"
        elif api_key:
            params = {"key": api_key}

        if not endpoint:
            return ToolConnectivityResp(ok=False, runtime_type="remote_api", summary="系统 API 工具缺少 endpoint，未执行真实请求", warnings=["缺少 endpoint"])

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                if tool_name == "bocha_search":
                    response = await client.post(endpoint, headers=headers, json={"query": "test", "count": 1})
                elif tool_name == "tavily_search":
                    response = await client.post(endpoint, json={"api_key": api_key, "query": "test", "max_results": 1})
                else:
                    response = await client.request(method, endpoint, params=params or None, headers=headers or None)
            response.raise_for_status()
        except Exception as err:
            return ToolConnectivityResp(
                ok=False,
                runtime_type="remote_api",
                summary="系统 API 工具真实请求失败",
                details=[f"endpoint: {endpoint}", str(err)],
                warnings=[str(err)],
                executed=True,
                tested_url=endpoint,
            )

        return ToolConnectivityResp(
            ok=True,
            runtime_type="remote_api",
            summary="系统 API 工具真实请求成功",
            details=[f"endpoint: {endpoint}", f"status: {response.status_code}"],
            executed=True,
            tested_url=endpoint,
        )

    @staticmethod
    async def _test_system_smtp(config_data: dict[str, Any], normalize_accounts) -> ToolConnectivityResp:
        accounts = [
            item for item in normalize_accounts(config_data)
            if item["slot_name"] and item["sender_email"] and item["auth_code"] and item["smtp_host"]
        ]
        if not accounts:
            return ToolConnectivityResp(ok=False, runtime_type="cli", summary="邮件工具缺少可用邮箱槽位，未执行 SMTP 检测", warnings=["请先配置邮箱槽位"])

        account = accounts[0]
        try:
            if account.get("use_ssl", True):
                with smtplib.SMTP_SSL(account["smtp_host"], int(account["smtp_port"]), timeout=12, context=ssl.create_default_context()) as smtp:
                    smtp.login(account["sender_email"], account["auth_code"])
            else:
                with smtplib.SMTP(account["smtp_host"], int(account["smtp_port"]), timeout=12) as smtp:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.login(account["sender_email"], account["auth_code"])
        except Exception as err:
            return ToolConnectivityResp(ok=False, runtime_type="cli", summary="SMTP 登录/握手检测失败", details=[f"slot: {account['slot_name']}", str(err)], warnings=[str(err)], executed=True)

        return ToolConnectivityResp(ok=True, runtime_type="cli", summary="SMTP 登录/握手检测成功", details=[f"slot: {account['slot_name']}", account["smtp_host"]], executed=True)

    @staticmethod
    def _test_system_local_dependency(tool_name: str) -> ToolConnectivityResp:
        if tool_name == "convert_to_pdf":
            found = shutil.which("libreoffice") or shutil.which("soffice")
            subject = "LibreOffice/soffice"
        else:
            found = "pdf2docx" if importlib.util.find_spec("pdf2docx") else ""
            subject = "pdf2docx"
        return ToolConnectivityResp(
            ok=bool(found),
            runtime_type="cli",
            summary=f"{subject} 依赖检测{'成功' if found else '失败'}",
            details=[str(found)] if found else [],
            warnings=[] if found else [f"未检测到 {subject}"],
            executed=True,
            command=str(found or subject),
        )

    @staticmethod
    async def _test_system_public_source(tool_name: str) -> ToolConnectivityResp:
        if tool_name != "get_arxiv":
            return ToolConnectivityResp(ok=False, runtime_type="cli", summary="未知公开数据源工具", warnings=[tool_name])
        try:
            import arxiv

            client = arxiv.Client(page_size=1, delay_seconds=0, num_retries=1)
            results = list(client.results(arxiv.Search(query="test", max_results=1)))
            if not results:
                raise ValueError("arxiv returned no results")
        except Exception as err:
            return ToolConnectivityResp(ok=False, runtime_type="cli", summary="公开数据源 smoke test 失败", details=[str(err)], warnings=[str(err)], executed=True)
        return ToolConnectivityResp(ok=True, runtime_type="cli", summary="公开数据源 smoke test 成功", details=["arxiv returned at least one result"], executed=True)

    @staticmethod
    async def test(req: ToolConnectivityReq) -> ToolConnectivityResp:
        runtime_type, resolved_schema, _stored_auth = ToolCreationService.validate_and_resolve(
            runtime_type=req.runtime_type,
            auth_config=req.auth_config,
            cli_config=req.cli_config,
            openapi_schema=req.openapi_schema,
            simple_api_config=req.simple_api_config,
            source_metadata=None,
        )

        if runtime_type == "cli":
            cli_adapter = CLIToolAdapter(
                tool_id="connectivity_check",
                display_name="Connectivity Check",
                description="Test CLI connectivity",
                cli_config=req.cli_config,
            )
            result = await cli_adapter.test_connectivity()
            return ToolConnectivityResp(**result)

        adapter = OpenAPIToolAdapter(
            openapi_schema=resolved_schema,
            auth_config=normalize_remote_api_auth_config(req.auth_config),
        )
        result = await adapter.test_connectivity(
            dict(req.probe_args or {}),
            operation_id=req.probe_operation_id.strip() or None,
        )
        return ToolConnectivityResp(**result)

    @staticmethod
    async def test_saved_tool(tool: ToolTable | dict[str, Any]) -> ToolConnectivityResp:
        runtime_type = get_user_defined_runtime_type(tool if isinstance(tool, ToolTable) else ToolTable(**tool))
        auth_config = tool.auth_config if isinstance(tool, ToolTable) else tool.get("auth_config") or {}

        if runtime_type == "cli":
            cli_adapter = CLIToolAdapter(
                tool_id=tool.tool_id,
                display_name=tool.display_name,
                description=tool.description,
                cli_config=get_cli_config_from_auth_config(auth_config),
            )
            result = await cli_adapter.test_connectivity()
            return ToolConnectivityResp(**result)

        probe_args = {}
        source_metadata = auth_config.get("source_metadata") if isinstance(auth_config, dict) else {}
        if isinstance(source_metadata, dict):
            probe_args = source_metadata.get("probe_args") or {}
        adapter = OpenAPIToolAdapter(
            openapi_schema=tool.openapi_schema,
            auth_config=normalize_remote_api_auth_config(auth_config),
        )
        result = await adapter.test_connectivity(dict(probe_args or {}))
        return ToolConnectivityResp(**result)

    @staticmethod
    def to_runtime_status(result: ToolConnectivityResp) -> dict[str, Any]:
        detail = result.summary
        if result.executed and result.ok:
            return {
                "code": "ready",
                "label": "已就绪",
                "detail": detail or "连通性测试成功",
                "configurable": True,
            }

        warnings = [item.lower() for item in (result.warnings or [])]
        details = [item.lower() for item in (result.details or [])]
        text = " ".join([detail.lower(), *warnings, *details])
        if "healthcheck command is missing" in text or "未配置健康检查" in text:
            return {
                "code": "runtime_input",
                "label": "待配置健康检查",
                "detail": detail or "需要配置 healthcheck_command 后才能真实检测 CLI",
                "configurable": True,
            }

        if "missing required" in text or "缺少必填" in text or "path 参数" in text or "query 参数" in text:
            return {
                "code": "runtime_input",
                "label": "待补测试参数",
                "detail": detail or "需要补充运行时参数后再检测",
                "configurable": True,
            }

        if "not found" in text or "找不到命令" in text or "healthcheck" in text or "依赖" in text:
            return {
                "code": "missing_dependency",
                "label": "缺依赖",
                "detail": detail or "当前环境缺少可执行依赖或健康检查命令不可用",
                "configurable": True,
            }

        if not result.ok:
            return {
                "code": "needs_config",
                "label": "需配置",
                "detail": detail or "当前配置未通过连通性检测",
                "configurable": True,
            }

        return {
            "code": "runtime_input",
            "label": "待补健康检查",
            "detail": detail or "基础校验通过，但还没有执行真实检测",
            "configurable": True,
        }
