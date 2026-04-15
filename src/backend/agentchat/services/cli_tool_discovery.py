from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Optional

import tomllib

from agentchat.schema.tool import (
    CLIToolPreviewCommand,
    CLIToolPreviewResp,
)


_EXECUTABLE_SUFFIXES = {".exe", ".cmd", ".bat", ".ps1", ".sh"}
_READMES = ("README.md", "readme.md", "README.txt", "Readme.md")
_CLI_SCRIPT_NAMES = {
    "cli",
    "run",
    "start",
    "serve",
    "tool",
    "tools",
    "main",
    "exec",
}
_COMMON_ENTRY_FILES = ("main.py", "cli.py", "__main__.py", "app.py")


class CliToolDiscoveryService:
    @classmethod
    def preview_tool_directory(cls, tool_dir: str) -> CLIToolPreviewResp:
        cli_root = cls._get_cli_tools_root()
        resolved_path = cls._resolve_tool_dir(cli_root, tool_dir)
        exists = resolved_path.is_dir()

        readme_path, readme_text = cls._load_readme(resolved_path) if exists else (None, "")
        readme_title, readme_summary = cls._summarize_readme(readme_text)
        suggested_name = readme_title or cls._humanize_name(resolved_path.name)
        default_description = readme_summary or f"Local CLI tool: {suggested_name}"

        command_candidates = []
        if exists:
            command_candidates.extend(cls._discover_readme_candidates(readme_text, resolved_path))
            command_candidates.extend(cls._discover_executable_candidates(resolved_path))
            command_candidates.extend(cls._discover_package_json_candidates(resolved_path))
            command_candidates.extend(cls._discover_pyproject_candidates(resolved_path))

        command_candidates = cls._dedupe_candidates(command_candidates)
        command_candidates.sort(
            key=lambda item: (-item.confidence, item.command, len(item.args_template))
        )

        warnings = []
        if not exists:
            warnings.append("Tool directory does not exist.")
        elif not command_candidates:
            warnings.append("No obvious CLI entry was discovered.")

        return CLIToolPreviewResp(
            tool_dir=tool_dir,
            resolved_path=str(resolved_path),
            exists=exists,
            suggested_name=suggested_name,
            default_description=default_description,
            readme_path=str(readme_path) if readme_path else None,
            readme_summary=readme_summary or None,
            command_candidates=command_candidates,
            warnings=warnings,
        )

    @classmethod
    def _get_cli_tools_root(cls) -> Path:
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "cli_tools").exists():
                return parent / "cli_tools"
        return Path.cwd() / "cli_tools"

    @classmethod
    def _resolve_tool_dir(cls, cli_root: Path, tool_dir: str) -> Path:
        if not tool_dir or not tool_dir.strip():
            raise ValueError("tool_dir is required")

        candidate = (cli_root / Path(tool_dir)).resolve()
        if candidate != cli_root and cli_root not in candidate.parents:
            raise ValueError("tool_dir escapes cli_tools root")
        return candidate

    @classmethod
    def _load_readme(cls, tool_path: Path) -> tuple[Optional[Path], str]:
        for name in _READMES:
            candidate = tool_path / name
            if candidate.is_file():
                return candidate, candidate.read_text(encoding="utf-8", errors="replace")
        return None, ""

    @classmethod
    def _summarize_readme(cls, readme_text: str) -> tuple[str, str]:
        if not readme_text.strip():
            return "", ""

        title = ""
        summary_lines: list[str] = []
        in_code_block = False
        collecting = False

        for raw_line in readme_text.splitlines():
            line = raw_line.strip()
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            if not line:
                if collecting:
                    break
                continue
            if line.startswith("#"):
                heading = line.lstrip("#").strip()
                if not title and heading:
                    title = cls._cleanup_markdown(heading)
                if collecting:
                    break
                continue

            if not collecting:
                collecting = True

            if line.startswith(("-", "*", ">", "1.", "1)")) and not summary_lines:
                continue

            summary_lines.append(cls._cleanup_markdown(line))
            if len(" ".join(summary_lines)) >= 280:
                break

        summary = " ".join(summary_lines).strip()
        if not title and summary:
            title = cls._cleanup_markdown(summary.split(".")[0][:64]).strip()
        return title, summary

    @classmethod
    def _discover_readme_candidates(
        cls,
        readme_text: str,
        tool_path: Path,
    ) -> list[CLIToolPreviewCommand]:
        candidates: list[CLIToolPreviewCommand] = []
        if not readme_text.strip():
            return candidates

        in_code_block = False
        collect_lines = False
        for raw_line in readme_text.splitlines():
            line = raw_line.strip()
            if line.startswith("```"):
                in_code_block = not in_code_block
                collect_lines = in_code_block
                continue
            if in_code_block:
                cls._append_command_candidate_from_line(candidates, line, source="readme")
                continue

            heading_match = re.match(r"^(#{1,6})\s*(.+)$", line)
            if heading_match:
                heading = heading_match.group(2).strip().lower()
                collect_lines = bool(re.search(r"\b(usage|example|examples|command|cli|run)\b", heading))
                continue

            if re.fullmatch(r"(usage|example|examples|command|cli|run)\s*:?", line.lower()):
                collect_lines = True
                continue

            if not line:
                collect_lines = False
                continue

            if not collect_lines:
                continue

            cls._append_command_candidate_from_line(candidates, line, source="readme")

        return candidates

    @classmethod
    def _append_command_candidate_from_line(
        cls,
        candidates: list[CLIToolPreviewCommand],
        raw_line: str,
        source: str,
    ) -> None:
        line = raw_line.lstrip("$>").strip()
        if not line or any(token in line for token in ("|", "&&", "||", ";")):
            return

        tokens = shlex.split(line, posix=False)
        if not tokens:
            return

        command = tokens[0]
        if not cls._looks_like_cli_command(command):
            return

        args_template = tokens[1:]
        candidates.append(
            CLIToolPreviewCommand(
                command=command,
                args_template=args_template,
                cwd_mode="tool_dir",
                source=source,
                confidence=0.92 if len(args_template) <= 4 else 0.84,
                notes=[f"README line: {cls._cleanup_markdown(line)[:160]}"],
            )
        )

    @classmethod
    def _discover_executable_candidates(cls, tool_path: Path) -> list[CLIToolPreviewCommand]:
        candidates: list[CLIToolPreviewCommand] = []
        scan_dirs = [tool_path]
        for child_name in ("package", "bin", "dist", "scripts"):
            child_dir = tool_path / child_name
            if child_dir.is_dir():
                scan_dirs.append(child_dir)

        for scan_dir in scan_dirs:
            for file_path in scan_dir.iterdir():
                if not file_path.is_file():
                    continue

                suffix = file_path.suffix.lower()
                rel_path = file_path.relative_to(tool_path).as_posix()

                if suffix in _EXECUTABLE_SUFFIXES:
                    candidates.append(
                        CLIToolPreviewCommand(
                            command=rel_path,
                            args_template=[],
                            cwd_mode="tool_dir",
                            source="executable_file",
                            confidence=0.97 if scan_dir == tool_path else 0.88,
                            notes=[f"Executable file: {rel_path}"],
                        )
                    )
                    continue

                if suffix == ".py" and file_path.name in _COMMON_ENTRY_FILES:
                    candidates.append(
                        CLIToolPreviewCommand(
                            command="python",
                            args_template=[rel_path],
                            cwd_mode="tool_dir",
                            source="python_entry",
                            confidence=0.9,
                            notes=[f"Python entry file: {rel_path}"],
                        )
                    )

        return candidates

    @classmethod
    def _discover_package_json_candidates(cls, tool_path: Path) -> list[CLIToolPreviewCommand]:
        package_json = tool_path / "package.json"
        if not package_json.is_file():
            return []

        try:
            package_data = json.loads(package_json.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return []

        candidates: list[CLIToolPreviewCommand] = []

        bin_field = package_data.get("bin")
        if isinstance(bin_field, str):
            candidates.append(
                CLIToolPreviewCommand(
                    command="node",
                    args_template=[bin_field],
                    cwd_mode="tool_dir",
                    source="package_json_bin",
                    confidence=0.82,
                    notes=["package.json bin field"],
                )
            )
        elif isinstance(bin_field, dict):
            for name, value in bin_field.items():
                if not isinstance(value, str):
                    continue
                candidates.append(
                    CLIToolPreviewCommand(
                        command="node",
                        args_template=[value],
                        cwd_mode="tool_dir",
                        source="package_json_bin",
                        confidence=0.82,
                        notes=[f"package.json bin: {name}"],
                    )
                )

        scripts = package_data.get("scripts") or {}
        if isinstance(scripts, dict):
            for script_name, script_value in scripts.items():
                if not isinstance(script_name, str):
                    continue
                if not cls._looks_like_cli_script(script_name):
                    continue
                if not isinstance(script_value, str):
                    continue

                candidates.append(
                    CLIToolPreviewCommand(
                        command="npm",
                        args_template=["run", script_name],
                        cwd_mode="tool_dir",
                        source="package_json_script",
                        confidence=0.78,
                        notes=[f"package.json script: {script_name}"],
                    )
                )

        return candidates

    @classmethod
    def _discover_pyproject_candidates(cls, tool_path: Path) -> list[CLIToolPreviewCommand]:
        pyproject = tool_path / "pyproject.toml"
        if not pyproject.is_file():
            return []

        try:
            pyproject_data = tomllib.loads(pyproject.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return []

        candidates: list[CLIToolPreviewCommand] = []

        project_scripts = pyproject_data.get("project", {}).get("scripts", {})
        candidates.extend(cls._collect_console_scripts(project_scripts, "project.scripts"))

        poetry_scripts = pyproject_data.get("tool", {}).get("poetry", {}).get("scripts", {})
        candidates.extend(cls._collect_console_scripts(poetry_scripts, "tool.poetry.scripts"))

        return candidates

    @classmethod
    def _collect_console_scripts(cls, scripts: object, source_name: str) -> list[CLIToolPreviewCommand]:
        if not isinstance(scripts, dict):
            return []

        candidates: list[CLIToolPreviewCommand] = []
        for script_name, script_value in scripts.items():
            if not isinstance(script_name, str) or not isinstance(script_value, str):
                continue

            module_name = script_value.split(":", 1)[0].strip()
            if not module_name:
                continue

            candidates.append(
                CLIToolPreviewCommand(
                    command="python",
                    args_template=["-m", module_name],
                    cwd_mode="tool_dir",
                    source="pyproject_script",
                    confidence=0.7,
                    notes=[f"{source_name}: {script_name} -> {script_value}"],
                )
            )

        return candidates

    @classmethod
    def _looks_like_cli_command(cls, command: str) -> bool:
        lowered = command.strip().lower()
        if not lowered:
            return False

        if lowered in {"python", "python3", "node", "npm", "npx", "pnpm", "yarn", "uv", "uvx", "go", "cargo", "bash", "sh", "powershell", "pwsh", "cmd"}:
            return True
        if lowered.endswith(tuple(_EXECUTABLE_SUFFIXES)):
            return True
        if lowered.startswith(("./", ".\\", "/", "\\")):
            return True
        return False

    @classmethod
    def _looks_like_cli_script(cls, script_name: str) -> bool:
        lowered = script_name.lower()
        return any(token in lowered for token in _CLI_SCRIPT_NAMES)

    @classmethod
    def _cleanup_markdown(cls, text: str) -> str:
        text = re.sub(r"`([^`]*)`", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @classmethod
    def _humanize_name(cls, value: str) -> str:
        if not value:
            return "CLI Tool"
        if re.search(r"[\u4e00-\u9fff]", value):
            return value
        cleaned = re.sub(r"[-_.]+", " ", value).strip()
        return cleaned.title() if cleaned else "CLI Tool"

    @classmethod
    def _dedupe_candidates(
        cls,
        candidates: list[CLIToolPreviewCommand],
    ) -> list[CLIToolPreviewCommand]:
        deduped: dict[tuple[str, tuple[str, ...], str, Optional[str]], CLIToolPreviewCommand] = {}
        for candidate in candidates:
            key = (
                candidate.command,
                tuple(candidate.args_template),
                candidate.cwd_mode,
                candidate.cwd,
            )
            existing = deduped.get(key)
            if existing is None or candidate.confidence > existing.confidence:
                deduped[key] = candidate
            elif candidate.notes:
                existing.notes.extend(note for note in candidate.notes if note not in existing.notes)
        return list(deduped.values())
