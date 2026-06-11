import importlib.util
import shutil
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel, Field

from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.schemas import UnifiedResponseModel, resp_200
from zuno.settings import initialize_app_settings, resolve_app_config_path

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
        "tool_kind": "smtp_protocol",
        "display_name": "Send Email",
        "description": "Configure reusable SMTP credential profiles for the email tool.",
        "root": "tools",
        "section": "email",
        "config_type": "email_accounts",
        "fields": [],
        "note": "Use named credential slots so agents can send mail without repeating raw secrets every time.",
    },
    "get_arxiv": {
        "tool_kind": "public_data_source",
        "display_name": "Search Papers",
        "description": "Public paper search source that works without extra runtime configuration.",
        "root": None,
        "section": None,
        "config_type": "fields",
        "fields": [],
        "note": "This tool is ready by default.",
    },
    "get_weather": {
        "tool_kind": "remote_api",
        "display_name": "Weather",
        "description": "Configure the weather API key and endpoint.",
        "root": "tools",
        "section": "weather",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "API Key",
                "placeholder": "Enter the weather provider API key",
                "required": True,
                "secret": True,
            },
            {
                "key": "endpoint",
                "label": "Endpoint",
                "placeholder": "Example: https://restapi.amap.com/v3/weather/weatherInfo",
                "required": True,
                "secret": False,
            },
        ],
        "note": "This tool needs both the API key and the endpoint before it can run.",
    },
    "get_delivery": {
        "tool_kind": "remote_api",
        "display_name": "Delivery Tracking",
        "description": "Configure the logistics API AppCode and endpoint.",
        "root": "tools",
        "section": "delivery",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "AppCode",
                "placeholder": "Enter the provider AppCode",
                "required": True,
                "secret": True,
            },
            {
                "key": "endpoint",
                "label": "Endpoint",
                "placeholder": "Example: https://wuliu.market.alicloudapi.com/kdi",
                "required": True,
                "secret": False,
            },
        ],
        "note": "This tool uses the delivery provider AppCode plus a fixed endpoint.",
    },
    "tavily_search": {
        "tool_kind": "remote_api",
        "display_name": "Tavily Search",
        "description": "Configure the Tavily API key.",
        "root": "tools",
        "section": "tavily",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "API Key",
                "placeholder": "Enter the Tavily API key",
                "required": True,
                "secret": True,
            }
        ],
        "note": "This tool only needs the Tavily API key.",
    },
    "bocha_search": {
        "tool_kind": "remote_api",
        "display_name": "Bocha Search",
        "description": "Configure the Bocha API key and endpoint.",
        "root": "tools",
        "section": "bocha",
        "config_type": "fields",
        "fields": [
            {
                "key": "api_key",
                "label": "API Key",
                "placeholder": "Enter the Bocha API key",
                "required": True,
                "secret": True,
            },
            {
                "key": "endpoint",
                "label": "Endpoint",
                "placeholder": "Example: https://api.bochaai.com/v1/web-search",
                "required": True,
                "secret": False,
            },
        ],
        "note": "This tool needs both the Bocha API key and endpoint.",
    },
    "convert_to_pdf": {
        "tool_kind": "local_dependency",
        "display_name": "Convert to PDF",
        "description": "Convert documents to PDF through a local system dependency.",
        "root": None,
        "section": None,
        "config_type": "fields",
        "fields": [],
        "note": "Requires LibreOffice or soffice on the host.",
    },
    "convert_to_docx": {
        "tool_kind": "local_dependency",
        "display_name": "Convert to DOCX",
        "description": "Convert PDF files to DOCX through a Python dependency.",
        "root": None,
        "section": None,
        "config_type": "fields",
        "fields": [],
        "note": "Requires the pdf2docx Python package in the runtime.",
    },
}


TOOL_KIND_LABELS: dict[str, str] = {
    "remote_api": "API",
    "public_data_source": "CLI",
    "smtp_protocol": "CLI",
    "local_dependency": "CLI",
}


STRATEGY_LABELS: dict[str, str] = {
    "builtin_internal": "Built-in logic",
    "config_fields": "Runtime config fields",
    "profile_credentials": "Credential profiles",
    "system_dependency_command": "System command dependency",
    "python_dependency_package": "Python dependency package",
}


def _build_install_requirement(tool_name: str, meta: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "convert_to_pdf":
        return {
            "code": "system_command",
            "label": "System command",
            "required": True,
            "subject": "libreoffice",
            "detail": "The host runtime must provide LibreOffice or the soffice command.",
        }

    if tool_name == "convert_to_docx":
        return {
            "code": "python_package",
            "label": "Python package",
            "required": True,
            "subject": "pdf2docx",
            "detail": "The backend runtime must install the pdf2docx package.",
        }

    detail = (
        "Uses built-in SMTP logic and does not require extra local binaries."
        if meta.get("config_type") == "email_accounts"
        else "No extra installation is required."
    )
    return {
        "code": "none",
        "label": "No extra install",
        "required": False,
        "subject": None,
        "detail": detail,
    }


def _build_config_requirement(meta: dict[str, Any]) -> dict[str, Any]:
    if meta.get("config_type") == "email_accounts":
        return {
            "code": "credential_profiles",
            "label": "Credential profiles",
            "required": True,
            "detail": "The runtime must store one or more reusable SMTP credential profiles.",
        }

    if meta.get("fields"):
        return {
            "code": "fields",
            "label": "Config fields",
            "required": True,
            "detail": "The required runtime config fields must be filled before the tool can run.",
        }

    return {
        "code": "none",
        "label": "No extra config",
        "required": False,
        "detail": "No extra runtime config is required.",
    }


def _build_tool_strategy(tool_name: str, meta: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "convert_to_pdf":
        strategy_code = "system_dependency_command"
        summary = "Runs through a host-level system command."
    elif tool_name == "convert_to_docx":
        strategy_code = "python_dependency_package"
        summary = "Runs through a Python package already installed in the backend runtime."
    elif meta.get("config_type") == "email_accounts":
        strategy_code = "profile_credentials"
        summary = "Uses named credential profiles instead of repeating raw secrets on each call."
    elif meta.get("fields"):
        strategy_code = "config_fields"
        summary = "Depends on runtime config fields stored in the project config file."
    else:
        strategy_code = "builtin_internal"
        summary = "Uses built-in backend logic without extra installation or config."

    return {
        "code": strategy_code,
        "label": STRATEGY_LABELS[strategy_code],
        "summary": summary,
        "install_requirement": _build_install_requirement(tool_name, meta),
        "config_requirement": _build_config_requirement(meta),
    }


def _build_system_tool_meta_payload(tool_name: str, meta: dict[str, Any]) -> dict[str, Any]:
    strategy = _build_tool_strategy(tool_name, meta)
    return {
        "tool_name": tool_name,
        "display_name": meta["display_name"],
        "description": meta["description"],
        "tool_kind": _get_tool_kind(meta),
        "tool_kind_label": _get_tool_kind_label(meta),
        "strategy_code": strategy["code"],
        "strategy_label": strategy["label"],
        "strategy_summary": strategy["summary"],
        "install_requirement": strategy["install_requirement"],
        "config_requirement": strategy["config_requirement"],
        "strategy": strategy,
    }


def _get_tool_kind(meta: dict[str, Any]) -> str:
    return str(meta.get("tool_kind") or "remote_api")


def _get_tool_kind_label(meta: dict[str, Any]) -> str:
    return TOOL_KIND_LABELS.get(_get_tool_kind(meta), "API")


def _get_runtime_config_path() -> Path:
    path = resolve_app_config_path(writable=True)
    if path.exists():
        return path

    example_path = resolve_app_config_path()
    if example_path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        return path
    raise FileNotFoundError("Runtime config file not found")


def _load_runtime_config() -> tuple[Path, dict[str, Any]]:
    path = _get_runtime_config_path()
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError("runtime config must contain a YAML object")
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
        **_build_system_tool_meta_payload(tool_name, meta),
        "root": root,
        "section": section,
        "config_type": meta.get("config_type", "fields"),
        "fields": meta["fields"],
        "values": scoped_values,
        "note": meta.get("note", ""),
        "status": _build_system_tool_status(tool_name, meta, config_data),
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
        "label": "Ready" if ready else "Needs config",
        "detail": (
            f"{len(ready_accounts)} email profile(s) are ready"
            if ready
            else "No usable email credential profile is configured yet"
        ),
        "configurable": True,
    }


def _build_system_tool_status(tool_name: str, meta: dict[str, Any], config_data: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "send_email":
        return _email_status(config_data)

    if meta.get("fields"):
        ready = _has_required_values(meta, config_data)
        return {
            "code": "ready" if ready else "needs_config",
            "label": "Ready" if ready else "Needs config",
            "detail": "Required runtime config is complete" if ready else "Required runtime config fields are missing",
            "configurable": True,
        }

    if tool_name == "convert_to_pdf":
        installed = shutil.which("libreoffice") is not None or shutil.which("soffice") is not None
        return {
            "code": "ready" if installed else "missing_dependency",
            "label": "Ready" if installed else "Missing dependency",
            "detail": "LibreOffice/soffice was detected" if installed else "LibreOffice/soffice command was not detected",
            "configurable": False,
        }

    if tool_name == "convert_to_docx":
        installed = importlib.util.find_spec("pdf2docx") is not None
        return {
            "code": "ready" if installed else "missing_dependency",
            "label": "Ready" if installed else "Missing dependency",
            "detail": "pdf2docx dependency was detected" if installed else "pdf2docx Python dependency was not detected",
            "configurable": False,
        }

    return {
        "code": "ready",
        "label": "Ready",
        "detail": "This tool is ready to use",
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
            raise ValueError("Every email profile must define a slot name")
        if not item["sender_email"]:
            raise ValueError(f"Profile {item['slot_name']} is missing sender_email")
        if not item["auth_code"]:
            raise ValueError(f"Profile {item['slot_name']} is missing auth_code")
        if not item["smtp_host"]:
            raise ValueError(f"Profile {item['slot_name']} is missing smtp_host")
        normalized_accounts.append(item)

    email_section["accounts"] = normalized_accounts


@router.get("/config", response_model=UnifiedResponseModel)
async def get_runtime_config(login_user: UserPayload = Depends(get_login_user)):
    _ = login_user
    _, data = _load_runtime_config()
    return resp_200(
        data={
            "content": yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            "system_tools": [
                {
                    **_build_system_tool_meta_payload(tool_name, meta),
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
            raise ValueError("config payload must be a YAML object")
        path = await _persist_runtime_config(parsed)
        return resp_200(data=f"Runtime config reloaded from: {path}")
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


@router.get("/config/system-tool/{tool_name}/status", response_model=UnifiedResponseModel)
async def get_system_tool_status(
    tool_name: str,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    try:
        _, data = _load_runtime_config()
        meta = SYSTEM_TOOL_CONFIG_META[tool_name]
        return resp_200(
            data={
                "tool_name": tool_name,
                "tool_kind": _get_tool_kind(meta),
                "tool_kind_label": _get_tool_kind_label(meta),
                "status": _build_system_tool_status(tool_name, meta, data),
            }
        )
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
                    "message": f"{meta['display_name']} profiles were saved",
                    "config_path": str(path),
                }
            )

        root = meta.get("root")
        section = meta.get("section")
        if not root or not section:
            return resp_200(
                data={
                    "message": f"{meta['display_name']} does not expose writable global config fields",
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
            raise ValueError(f"Missing required fields: {', '.join(missing_required)}")

        for key, value in req.values.items():
            if key in allowed_keys:
                section_values[key] = value

        await _persist_runtime_config(data)
        return resp_200(
            data={
                "message": f"{meta['display_name']} config was saved",
                "config_path": str(path),
            }
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Unsupported system tool")
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


__all__ = [
    "EmailPresetItem",
    "STRATEGY_LABELS",
    "SYSTEM_TOOL_CONFIG_META",
    "SystemToolConfigUpdateReq",
    "TOOL_KIND_LABELS",
    "_build_config_requirement",
    "_build_install_requirement",
    "_build_system_tool_meta_payload",
    "_build_system_tool_payload",
    "_build_system_tool_status",
    "_build_tool_strategy",
    "_email_status",
    "_get_runtime_config_path",
    "_get_tool_kind",
    "_get_tool_kind_label",
    "_has_required_values",
    "_load_runtime_config",
    "_normalize_email_accounts",
    "_persist_runtime_config",
    "_save_email_accounts",
    "get_runtime_config",
    "get_system_tool_config",
    "get_system_tool_status",
    "router",
    "update_runtime_config",
    "update_system_tool_config",
]
