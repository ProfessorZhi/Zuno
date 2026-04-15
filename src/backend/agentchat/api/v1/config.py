import importlib.util
import shutil
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel, Field

from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.schema.schemas import UnifiedResponseModel, resp_200
from agentchat.settings import initialize_app_settings

router = APIRouter(tags=["Config"])


class EmailPresetItem(BaseModel):
    slot_name: str = ""
    provider: str = "qq"
    sender_email: str = ""
    auth_code: str = ""
    smtp_host: str = ""
    smtp_port: int = 465
    use_ssl: bool = True
    display_name: str = ""


class SystemToolConfigUpdateReq(BaseModel):
    values: dict[str, Any] = Field(default_factory=dict)
    accounts: list[EmailPresetItem] = Field(default_factory=list)


SYSTEM_TOOL_CONFIG_META: dict[str, dict[str, Any]] = {
    "send_email": {
        "display_name": "发送邮件",
        "description": "配置多个发件邮箱槽位，支持多个 QQ 邮箱，也支持其他 SMTP 邮箱。",
        "root": "tools",
        "section": "email",
        "config_type": "email_accounts",
        "fields": [],
        "note": "建议把常用邮箱都存成预设槽位。Agent 调用时优先用槽位名，不必每次重复输入邮箱地址和授权码。",
    },
    "get_arxiv": {
        "display_name": "论文检索",
        "description": "当前通过公开论文源检索，不依赖额外全局配置。",
        "root": None,
        "section": None,
        "config_type": "fields",
        "fields": [],
        "note": "这个工具当前可直接使用，无需额外配置。",
    },
    "get_weather": {
        "display_name": "天气预报",
        "description": "配置高德天气查询所需的 API Key 和接口地址。",
        "root": "tools",
        "section": "weather",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "高德 API Key",
                "placeholder": "请输入高德开放平台的 Web 服务 API Key",
                "required": True,
                "secret": True,
            },
            {
                "key": "endpoint",
                "label": "高德天气接口地址",
                "placeholder": "例如 https://restapi.amap.com/v3/weather/weatherInfo",
                "required": True,
                "secret": False,
            },
        ],
        "note": "这是高德天气接口配置。你需要在高德开放平台创建 Web 服务 Key，然后填写 Key 和 weatherInfo 接口地址。",
    },
    "get_delivery": {
        "display_name": "快递物流查询",
        "description": "配置阿里云市场“全国快递物流查询-快递查询接口”的 APPCODE 和接口地址。",
        "root": "tools",
        "section": "delivery",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "阿里云 APPCODE",
                "placeholder": "请输入这款阿里云物流商品的 AppCode（APPCODE）",
                "required": True,
                "secret": True,
            },
            {
                "key": "endpoint",
                "label": "阿里云物流接口地址",
                "placeholder": "固定填写 https://wuliu.market.alicloudapi.com/kdi",
                "required": True,
                "secret": False,
            },
        ],
        "note": "这是你当前购买的阿里云物流商品专用配置。鉴权方式用 APPCODE，请填写商品详情页里的 AppCode；接口地址固定为 https://wuliu.market.alicloudapi.com/kdi。查询时默认自动识别快递公司，识别失败时可补充公司代码，如 zto、yto、sfexpress。",
    },
    "tavily_search": {
        "display_name": "联网搜索",
        "description": "配置 Tavily 搜索 API Key。",
        "root": "tools",
        "section": "tavily",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "API Key",
                "placeholder": "请输入 Tavily API Key",
                "required": True,
                "secret": True,
            }
        ],
    },
    "bocha_search": {
        "display_name": "博查搜索",
        "description": "配置博查搜索的 API Key 和接口地址。",
        "root": "tools",
        "section": "bocha",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "API Key",
                "placeholder": "请输入 Bocha API Key",
                "required": True,
                "secret": True,
            },
            {
                "key": "endpoint",
                "label": "接口地址",
                "placeholder": "例如 https://api.bochaai.com/v1/web-search",
                "required": True,
                "secret": False,
            },
        ],
    },
    "convert_to_pdf": {
        "display_name": "文件格式转换 (Docx -> PDF)",
        "description": "当前通过系统依赖完成转换，无需额外全局配置。",
        "root": None,
        "section": None,
        "config_type": "fields",
        "fields": [],
        "note": "如果状态显示缺依赖，请先安装 LibreOffice。",
    },
    "convert_to_docx": {
        "display_name": "文件格式转换 (PDF -> Docx)",
        "description": "当前通过系统依赖完成转换，无需额外全局配置。",
        "root": None,
        "section": None,
        "config_type": "fields",
        "fields": [],
        "note": "如果状态显示缺依赖，请先安装 pdf2docx。",
    },
}


def _get_runtime_config_path() -> Path:
    candidates = [
        Path("/app/agentchat/config.yaml"),
        Path(__file__).resolve().parents[2] / "config.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Runtime config.yaml not found")


def _load_runtime_config() -> tuple[Path, dict[str, Any]]:
    path = _get_runtime_config_path()
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError("config.yaml must contain a YAML object")
    return path, data


async def _persist_runtime_config(data: dict[str, Any]) -> Path:
    path = _get_runtime_config_path()
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)
    await initialize_app_settings(str(path))
    return path


def _normalize_email_accounts(config_data: dict[str, Any]) -> list[dict[str, Any]]:
    accounts = (((config_data.get("tools") or {}).get("email") or {}).get("accounts") or [])
    if not isinstance(accounts, list):
        return []

    normalized: list[dict[str, Any]] = []
    for account in accounts:
        if not isinstance(account, dict):
            continue
        normalized.append(
            {
                "slot_name": str(account.get("slot_name", "")).strip(),
                "provider": str(account.get("provider", "qq")).strip() or "qq",
                "sender_email": str(account.get("sender_email", "")).strip(),
                "auth_code": str(account.get("auth_code", "")).strip(),
                "smtp_host": str(account.get("smtp_host", "")).strip(),
                "smtp_port": int(account.get("smtp_port") or 465),
                "use_ssl": bool(account.get("use_ssl", True)),
                "display_name": str(account.get("display_name", "")).strip(),
            }
        )
    return normalized


def _build_system_tool_payload(tool_name: str, config_data: dict[str, Any]) -> dict[str, Any]:
    meta = SYSTEM_TOOL_CONFIG_META.get(tool_name)
    if not meta:
        raise KeyError(tool_name)

    root = meta.get("root")
    section = meta.get("section")
    scoped_values: dict[str, Any] = {}
    if root and section and meta.get("config_type") == "fields":
        scoped_values = ((config_data.get(root) or {}).get(section) or {}).copy()

    payload = {
        "tool_name": tool_name,
        "display_name": meta["display_name"],
        "description": meta["description"],
        "root": root,
        "section": section,
        "config_type": meta.get("config_type", "fields"),
        "fields": meta["fields"],
        "values": scoped_values,
        "note": meta.get("note", ""),
    }

    if meta.get("config_type") == "email_accounts":
        payload["accounts"] = _normalize_email_accounts(config_data)

    return payload


def _has_required_values(meta: dict[str, Any], config_data: dict[str, Any]) -> bool:
    root = meta.get("root")
    section = meta.get("section")
    if not root or not section:
        return True

    values = ((config_data.get(root) or {}).get(section) or {})
    for field in meta.get("fields", []):
        if field.get("required") and not str(values.get(field["key"], "")).strip():
            return False
    return True


def _email_status(config_data: dict[str, Any]) -> dict[str, Any]:
    accounts = _normalize_email_accounts(config_data)
    ready_accounts = [
        item
        for item in accounts
        if item["slot_name"] and item["sender_email"] and item["auth_code"] and item["smtp_host"]
    ]
    ready = len(ready_accounts) > 0
    return {
        "code": "ready" if ready else "needs_config",
        "label": "已就绪" if ready else "需配置",
        "detail": f"已配置 {len(ready_accounts)} 个可用发件箱槽位" if ready else "还没有可用的发件箱预设",
        "configurable": True,
    }


def _build_system_tool_status(tool_name: str, meta: dict[str, Any], config_data: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "send_email":
        return _email_status(config_data)

    if meta.get("fields"):
        ready = _has_required_values(meta, config_data)
        return {
            "code": "ready" if ready else "needs_config",
            "label": "已就绪" if ready else "需配置",
            "detail": "全局配置已完整" if ready else "缺少必要的全局配置项",
            "configurable": True,
        }

    if tool_name == "convert_to_pdf":
        installed = shutil.which("libreoffice") is not None or shutil.which("soffice") is not None
        return {
            "code": "ready" if installed else "missing_dependency",
            "label": "已就绪" if installed else "缺依赖",
            "detail": "已检测到 LibreOffice/soffice" if installed else "未检测到 LibreOffice/soffice 命令",
            "configurable": False,
        }

    if tool_name == "convert_to_docx":
        installed = importlib.util.find_spec("pdf2docx") is not None
        return {
            "code": "ready" if installed else "missing_dependency",
            "label": "已就绪" if installed else "缺依赖",
            "detail": "已检测到 pdf2docx 依赖" if installed else "未检测到 pdf2docx Python 依赖",
            "configurable": False,
        }

    return {
        "code": "ready",
        "label": "已就绪",
        "detail": "当前工具可直接使用",
        "configurable": False,
    }


def _save_email_accounts(config_data: dict[str, Any], accounts: list[EmailPresetItem]) -> None:
    tools = config_data.setdefault("tools", {})
    email_section = tools.setdefault("email", {})

    normalized_accounts: list[dict[str, Any]] = []
    for account in accounts:
        item = account.model_dump()
        item["slot_name"] = item["slot_name"].strip()
        item["sender_email"] = item["sender_email"].strip()
        item["auth_code"] = item["auth_code"].strip()
        item["smtp_host"] = item["smtp_host"].strip()
        item["display_name"] = item["display_name"].strip()
        item["provider"] = item["provider"].strip() or "qq"
        if not any(item.values()):
            continue
        if not item["slot_name"]:
            raise ValueError("每个邮箱槽位都必须填写槽位名")
        if not item["sender_email"]:
            raise ValueError(f"槽位 {item['slot_name']} 缺少发件邮箱")
        if not item["auth_code"]:
            raise ValueError(f"槽位 {item['slot_name']} 缺少授权码")
        if not item["smtp_host"]:
            raise ValueError(f"槽位 {item['slot_name']} 缺少 SMTP 主机")
        normalized_accounts.append(item)

    email_section["accounts"] = normalized_accounts


@router.get("/config", response_model=UnifiedResponseModel)
async def get_runtime_config(
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    _, data = _load_runtime_config()
    return resp_200(
        data={
            "content": yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            "system_tools": [
                {
                    "tool_name": tool_name,
                    "display_name": meta["display_name"],
                    "description": meta["description"],
                    "has_fields": bool(meta.get("fields")) or meta.get("config_type") == "email_accounts",
                    "status": _build_system_tool_status(tool_name, meta, data),
                }
                for tool_name, meta in SYSTEM_TOOL_CONFIG_META.items()
            ],
        }
    )


@router.post("/config", response_model=UnifiedResponseModel)
async def update_runtime_config(
    data: str = Form(...),
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    try:
        parsed = yaml.safe_load(data) or {}
        if not isinstance(parsed, dict):
            raise ValueError("配置内容必须是对象")
        path = await _persist_runtime_config(parsed)
        return resp_200(data=f"配置已更新并重新加载: {path}")
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/config/system-tool/{tool_name}", response_model=UnifiedResponseModel)
async def get_system_tool_config(
    tool_name: str,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    try:
        _, data = _load_runtime_config()
        return resp_200(data=_build_system_tool_payload(tool_name, data))
    except KeyError:
        raise HTTPException(status_code=404, detail="Unsupported system tool")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/config/system-tool/{tool_name}", response_model=UnifiedResponseModel)
async def update_system_tool_config(
    tool_name: str,
    req: SystemToolConfigUpdateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    try:
        meta = SYSTEM_TOOL_CONFIG_META.get(tool_name)
        if not meta:
            raise KeyError(tool_name)

        path, data = _load_runtime_config()
        config_type = meta.get("config_type", "fields")
        if config_type == "email_accounts":
            _save_email_accounts(data, req.accounts)
            await _persist_runtime_config(data)
            return resp_200(
                data={
                    "message": f"{meta['display_name']} 预设已保存",
                    "config_path": str(path),
                }
            )

        root = meta.get("root")
        section = meta.get("section")
        if not root or not section:
            return resp_200(
                data={
                    "message": f"{meta['display_name']} 当前没有可保存的全局配置项",
                    "config_path": str(path),
                }
            )

        root_values = data.setdefault(root, {})
        section_values = root_values.setdefault(section, {})

        allowed_keys = {field["key"] for field in meta["fields"]}
        missing_required = [
            field["label"]
            for field in meta["fields"]
            if field.get("required") and not str(req.values.get(field["key"], "")).strip()
        ]
        if missing_required:
            raise ValueError(f"缺少必填项: {', '.join(missing_required)}")

        for key, value in req.values.items():
            if key in allowed_keys:
                section_values[key] = value

        await _persist_runtime_config(data)
        return resp_200(
            data={
                "message": f"{meta['display_name']} 配置已保存",
                "config_path": str(path),
            }
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Unsupported system tool")
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
