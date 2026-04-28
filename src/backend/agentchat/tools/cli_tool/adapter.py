import asyncio
import os
import re
import shlex
import shutil
from pathlib import Path
from typing import Any, Dict


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
    def _get_cli_tools_root() -> Path:
        env_root = (os.environ.get("ZUNO_CLI_TOOLS_ROOT") or "").strip()
        if env_root:
            return Path(env_root).resolve()

        cwd_candidate = (Path.cwd() / "cli_tools").resolve()
        if cwd_candidate.exists():
            return cwd_candidate

        app_root = Path("/app/cli_tools")
        if app_root.exists():
            return app_root.resolve()

        current = Path(__file__).resolve()
        for parent in current.parents:
            candidate = parent / "cli_tools"
            if candidate.exists():
                return candidate.resolve()

        return cwd_candidate

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
        cli_root = self._get_cli_tools_root()
        tool_dir = (self.cli_config.get("tool_dir") or "").strip()
        local_path = (self.cli_config.get("local_path") or "").strip()
        raw_path = tool_dir or local_path
        if not raw_path:
            return cli_root

        candidate = Path(raw_path)
        if candidate.is_absolute():
            resolved = candidate.resolve()
            if not resolved.exists():
                raise ValueError(f"CLI tool directory does not exist: {resolved}")
            return resolved

        resolved = (cli_root / candidate).resolve()
        if cli_root not in resolved.parents and resolved != cli_root:
            raise ValueError(f"CLI tool directory must stay under {cli_root}")
        if not resolved.exists():
            raise ValueError(f"CLI tool directory does not exist: {resolved}")
        return resolved

    def _resolve_cwd(self) -> Path:
        cwd_mode = self.cli_config.get("cwd_mode", "tool_dir")
        tool_dir = self._resolve_tool_dir()

        if cwd_mode == "tool_dir":
            return tool_dir

        if cwd_mode == "workspace":
            default_workspace = Path.cwd() if not Path("/app").exists() else Path("/app")
            workspace_dir = str(self.cli_config.get("workspace_dir") or default_workspace).strip()
            return Path(workspace_dir)

        custom_cwd = (self.cli_config.get("cwd") or "").strip()
        if not custom_cwd:
            raise ValueError("CLI tool requires cwd when cwd_mode is custom")

        custom_path = Path(custom_cwd)
        if not custom_path.is_absolute():
            custom_path = (tool_dir / custom_path).resolve()
        return custom_path

    def _resolve_command_parts(self) -> list[str]:
        command = (self.cli_config.get("command") or "").strip()
        if not command:
            raise ValueError("CLI tool requires a command")

        parts = shlex.split(command, posix=False)
        if not parts:
            raise ValueError("CLI tool requires a valid command")

        executable = parts[0]
        executable_path = Path(executable)
        if executable_path.is_absolute():
            parts[0] = str(executable_path)
            return parts

        if any(sep in executable for sep in ("/", "\\")):
            parts[0] = str((self._resolve_tool_dir() / executable_path).resolve())
        return parts

    def _resolve_args(self, input_text: str) -> list[str]:
        args_template = self.cli_config.get("args_template", [])
        if isinstance(args_template, str):
            args_template = shlex.split(args_template, posix=False)

        resolved_args = [str(arg).replace("{{input}}", input_text) for arg in args_template]
        has_placeholder = any("{{input}}" in str(arg) for arg in args_template)
        if input_text and not has_placeholder:
            resolved_args.append(input_text)
        return resolved_args

    def _build_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(self.cli_config.get("env") or {})
        return env

    async def _run_command(
        self,
        command_parts: list[str],
        *,
        cwd: Path,
        timeout_ms: int,
        env: dict[str, str],
    ) -> tuple[str, str]:
        process = await asyncio.create_subprocess_exec(
            *command_parts,
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

        return stdout_text, stderr_text

    def _resolve_healthcheck_parts(self) -> list[str]:
        healthcheck_command = (self.cli_config.get("healthcheck_command") or "").strip()
        if not healthcheck_command:
            return []

        parts = shlex.split(healthcheck_command, posix=False)
        if not parts:
            raise ValueError("CLI healthcheck command is invalid")

        executable = parts[0]
        executable_path = Path(executable)
        if executable_path.is_absolute():
            parts[0] = str(executable_path)
            return parts

        if any(sep in executable for sep in ("/", "\\")):
            parts[0] = str((self._resolve_tool_dir() / executable_path).resolve())
        return parts

    async def execute(self, input: str):
        command_parts = self._resolve_command_parts()
        args = self._resolve_args(input)
        cwd = self._resolve_cwd()
        timeout_ms = int(self.cli_config.get("timeout_ms", 30000))
        env = self._build_env()

        stdout_text, stderr_text = await self._run_command(
            [*command_parts, *args],
            cwd=cwd,
            timeout_ms=timeout_ms,
            env=env,
        )

        if stdout_text:
            return stdout_text
        if stderr_text:
            return stderr_text
        return "CLI tool executed successfully, but returned no output."

    async def test_connectivity(self) -> dict[str, Any]:
        self.validate_cli_config(self.cli_config)

        tool_dir = self._resolve_tool_dir()
        cwd = self._resolve_cwd()
        timeout_ms = int(self.cli_config.get("timeout_ms", 30000))
        env = self._build_env()
        command_parts = self._resolve_command_parts()

        executable = command_parts[0]
        executable_display = " ".join(command_parts)
        if not Path(executable).is_absolute():
            resolved_executable = shutil.which(executable, path=env.get("PATH"))
            if not resolved_executable and any(sep in executable for sep in ("/", "\\")):
                resolved_executable = str(Path(executable).resolve()) if Path(executable).exists() else ""
            if not resolved_executable:
                raise ValueError(f"找不到 CLI 命令：{executable}")

        healthcheck_parts = self._resolve_healthcheck_parts()
        if not healthcheck_parts:
            return {
                "ok": False,
                "runtime_type": "cli",
                "summary": "CLI healthcheck command is missing",
                "details": [
                    f"工具目录：{tool_dir}",
                    f"工作目录：{cwd}",
                    f"启动命令：{executable_display}",
                ],
                "warnings": ["未配置健康检查命令，本次只完成了目录与命令可达校验。"],
                "executed": False,
                "command": executable_display,
            }

        try:
            stdout_text, stderr_text = await self._run_command(
                healthcheck_parts,
                cwd=cwd,
                timeout_ms=timeout_ms,
                env=env,
            )
        except Exception as err:
            return {
                "ok": False,
                "runtime_type": "cli",
                "summary": "CLI healthcheck failed",
                "details": [
                    f"healthcheck: {' '.join(healthcheck_parts)}",
                    str(err),
                ],
                "warnings": [str(err)],
                "executed": True,
                "command": " ".join(healthcheck_parts),
            }
        details = [
            f"工具目录：{tool_dir}",
            f"工作目录：{cwd}",
            f"健康检查：{' '.join(healthcheck_parts)}",
        ]
        if stdout_text:
            details.append(f"stdout：{stdout_text[:240]}")
        elif stderr_text:
            details.append(f"stderr：{stderr_text[:240]}")

        return {
            "ok": True,
            "runtime_type": "cli",
            "summary": "CLI 健康检查成功，连通性正常",
            "details": details,
            "warnings": [],
            "executed": True,
            "command": " ".join(healthcheck_parts),
        }
