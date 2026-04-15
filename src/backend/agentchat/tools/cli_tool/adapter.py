import asyncio
import os
import re
import shlex
from pathlib import Path
from typing import Any, Dict


CLI_TOOLS_ROOT = Path("/app/cli_tools")


class CLIToolAdapter:
    def __init__(
        self,
        *,
        tool_id: str,
        display_name: str,
        description: str,
        cli_config: Dict[str, Any] | None = None,
    ) -> None:
        self.tool_id = tool_id
        self.display_name = display_name
        self.description = description or f"Run CLI tool {display_name}"
        self.cli_config = cli_config or {}
        self.tool_name = self._build_tool_name()
        self.tool_schema = {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": (
                                "Input text passed to the CLI tool. If the args template contains "
                                "{{input}}, it will be substituted there; otherwise it will be "
                                "appended to the end of the command."
                            ),
                        }
                    },
                    "required": ["input"],
                },
            },
        }

    def _build_tool_name(self) -> str:
        base_name = re.sub(r"[^a-zA-Z0-9_]+", "_", self.display_name.strip().lower())
        base_name = base_name.strip("_") or "cli_tool"
        return f"{base_name}_{self.tool_id[:8]}"

    @staticmethod
    def validate_cli_config(cli_config: Dict[str, Any] | None):
        if not isinstance(cli_config, dict):
            raise ValueError("CLI config must be a dictionary")

        command = (cli_config.get("command") or "").strip()
        if not command:
            raise ValueError("CLI tool requires a command")

        args_template = cli_config.get("args_template", [])
        if isinstance(args_template, str):
            args_template = shlex.split(args_template, posix=False)
        if not isinstance(args_template, list):
            raise ValueError("CLI tool args_template must be a string or an array")

        cwd_mode = cli_config.get("cwd_mode", "tool_dir")
        if cwd_mode not in {"tool_dir", "workspace", "custom"}:
            raise ValueError("CLI tool cwd_mode must be tool_dir, workspace, or custom")

        timeout_ms = cli_config.get("timeout_ms", 30000)
        if not isinstance(timeout_ms, int) or timeout_ms <= 0:
            raise ValueError("CLI tool timeout_ms must be a positive integer")

    def _resolve_tool_dir(self) -> Path:
        tool_dir = (self.cli_config.get("tool_dir") or "").strip()
        if not tool_dir:
            return CLI_TOOLS_ROOT

        resolved = (CLI_TOOLS_ROOT / tool_dir).resolve()
        cli_root = CLI_TOOLS_ROOT.resolve()
        if cli_root not in resolved.parents and resolved != cli_root:
            raise ValueError("CLI tool directory must stay under /app/cli_tools")
        return resolved

    def _resolve_cwd(self) -> Path:
        cwd_mode = self.cli_config.get("cwd_mode", "tool_dir")
        tool_dir = self._resolve_tool_dir()

        if cwd_mode == "tool_dir":
            return tool_dir

        if cwd_mode == "workspace":
            workspace_dir = (self.cli_config.get("workspace_dir") or "/app").strip()
            return Path(workspace_dir)

        custom_cwd = (self.cli_config.get("cwd") or "").strip()
        if not custom_cwd:
            raise ValueError("CLI tool requires cwd when cwd_mode is custom")

        custom_path = Path(custom_cwd)
        if not custom_path.is_absolute():
            custom_path = (tool_dir / custom_path).resolve()
        return custom_path

    def _resolve_command(self) -> str:
        command = (self.cli_config.get("command") or "").strip()
        command_path = Path(command)
        if command_path.is_absolute():
            return str(command_path)

        if any(sep in command for sep in ("/", "\\")):
            return str((self._resolve_tool_dir() / command_path).resolve())
        return command

    def _resolve_args(self, input_text: str) -> list[str]:
        args_template = self.cli_config.get("args_template", [])
        if isinstance(args_template, str):
            args_template = shlex.split(args_template, posix=False)

        resolved_args = [str(arg).replace("{{input}}", input_text) for arg in args_template]
        has_placeholder = any("{{input}}" in str(arg) for arg in args_template)
        if input_text and not has_placeholder:
            resolved_args.append(input_text)
        return resolved_args

    async def execute(self, input: str):
        command = self._resolve_command()
        args = self._resolve_args(input)
        cwd = self._resolve_cwd()
        timeout_ms = int(self.cli_config.get("timeout_ms", 30000))
        env = os.environ.copy()
        env.update(self.cli_config.get("env") or {})

        process = await asyncio.create_subprocess_exec(
            command,
            *args,
            cwd=str(cwd),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_ms / 1000,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            raise ValueError(f"CLI tool execution timed out after {timeout_ms}ms")

        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        stderr_text = stderr.decode("utf-8", errors="replace").strip()

        if process.returncode != 0:
            error_message = stderr_text or stdout_text or f"CLI tool failed with exit code {process.returncode}"
            raise ValueError(error_message)

        if stdout_text:
            return stdout_text
        if stderr_text:
            return stderr_text
        return "CLI tool executed successfully, but returned no output."
