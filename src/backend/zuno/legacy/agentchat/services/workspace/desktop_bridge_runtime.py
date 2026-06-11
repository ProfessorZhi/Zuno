from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from urllib import error, request

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class DesktopBridgeConfig(BaseModel):
    url: str
    token: str


class ListDirectoryArgs(BaseModel):
    path: str = Field(default=".", description="要列出的目录路径。相对路径默认基于工作区。")


class ReadFileArgs(BaseModel):
    path: str = Field(description="要读取的文件路径。相对路径默认基于工作区。")


class WriteFileArgs(BaseModel):
    path: str = Field(description="要写入的文件路径。相对路径默认基于工作区。")
    content: str = Field(description="要写入的完整文本内容。")
    append: bool = Field(default=False, description="是否采用追加写入。")


class SearchFilesArgs(BaseModel):
    query: str = Field(description="要搜索的文件名或文本关键字。")
    path: str = Field(default=".", description="搜索根目录。相对路径默认基于工作区。")
    limit: int = Field(default=20, description="最多返回多少条结果。")


class RunCommandArgs(BaseModel):
    command: str = Field(description="要执行的 PowerShell 命令。")
    cwd: str = Field(default=".", description="命令执行目录。相对路径默认基于工作区。")
    timeout_ms: int = Field(default=20000, description="命令超时时间，单位毫秒。")


class DesktopBridgeClient:
    def __init__(self, bridge_config: DesktopBridgeConfig, access_scope: str):
        self.bridge_config = bridge_config
        self.access_scope = access_scope

    async def invoke(self, action: str, args: dict[str, Any]) -> str:
        payload = json.dumps(
            {
                "action": action,
                "args": args,
                "access_scope": self.access_scope,
            },
            ensure_ascii=False,
        ).encode("utf-8")

        def _do_request():
            http_request = request.Request(
                f"{self.bridge_config.url.rstrip('/')}/execute",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Zuno-Desktop-Token": self.bridge_config.token,
                },
                method="POST",
            )
            try:
                with request.urlopen(http_request, timeout=60) as response:
                    return json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                try:
                    parsed = json.loads(detail)
                    raise RuntimeError(parsed.get("error") or detail) from exc
                except json.JSONDecodeError:
                    raise RuntimeError(detail or str(exc)) from exc
            except error.URLError as exc:
                raise RuntimeError(f"无法连接桌面 bridge: {exc.reason}") from exc

        result = await asyncio.to_thread(_do_request)
        return json.dumps(result, ensure_ascii=False, indent=2)


def build_terminal_langchain_tools(
    *,
    bridge_config: DesktopBridgeConfig,
    access_scope: str,
) -> tuple[list[StructuredTool], dict[str, dict[str, str]]]:
    client = DesktopBridgeClient(bridge_config, access_scope)

    tools: list[StructuredTool] = [
        StructuredTool(
            name="list_directory",
            description="列出目录内容。用于查看当前项目或指定路径下有哪些文件和文件夹。",
            coroutine=lambda path=".": client.invoke("list_directory", {"path": path}),
            args_schema=ListDirectoryArgs,
        ),
        StructuredTool(
            name="read_file",
            description="读取本地文本文件内容。回答文件相关问题前，优先先读文件，不要猜测。",
            coroutine=lambda path: client.invoke("read_file", {"path": path}),
            args_schema=ReadFileArgs,
        ),
        StructuredTool(
            name="write_file",
            description="写入或追加本地文本文件。修改文件时必须通过这个工具，不要只在回答里声称已经修改。",
            coroutine=lambda path, content, append=False: client.invoke(
                "write_file",
                {"path": path, "content": content, "append": append},
            ),
            args_schema=WriteFileArgs,
        ),
        StructuredTool(
            name="search_files",
            description="在本地文件中搜索文件名或文本关键字。适合先定位相关文件，再继续读取。",
            coroutine=lambda query, path=".", limit=20: client.invoke(
                "search_files",
                {"query": query, "path": path, "limit": limit},
            ),
            args_schema=SearchFilesArgs,
        ),
    ]

    if access_scope == "unrestricted":
        tools.append(
            StructuredTool(
                name="run_command",
                description=(
                    "执行 PowerShell 本地命令。仅在确实需要终端时使用；优先先用更窄的文件工具。"
                ),
                coroutine=lambda command, cwd=".", timeout_ms=20000: client.invoke(
                    "run_command",
                    {"command": command, "cwd": cwd, "timeout_ms": timeout_ms},
                ),
                args_schema=RunCommandArgs,
            )
        )

    metadata = {
        tool.name: {
            "name": tool.name,
            "type": "终端工具",
        }
        for tool in tools
    }
    return tools, metadata
