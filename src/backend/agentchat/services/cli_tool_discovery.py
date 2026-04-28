from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path
from typing import Optional

import tomllib

from agentchat.schema.tool import (
    CLIToolCredentialModeSuggestion,
    CLIToolPreviewCommand,
    CLIToolPreviewReq,
    CLIToolPreviewResp,
    CLIToolStructuredSuggestion,
)


_EXECUTABLE_SUFFIXES = {".exe", ".cmd", ".bat", ".ps1", ".sh"}
_README_NAMES = ("README.md", "readme.md", "README.txt", "Readme.md")
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
_ENV_VAR_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
_URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


class CliToolDiscoveryService:
    @classmethod
    def preview_tool_directory(cls, tool_dir: str) -> CLIToolPreviewResp:
        return cls.preview(CLIToolPreviewReq(tool_dir=tool_dir))

    @classmethod
    def preview_tool(cls, req: CLIToolPreviewReq) -> CLIToolPreviewResp:
        return cls.preview(req)

    @classmethod
    def preview(cls, req: CLIToolPreviewReq) -> CLIToolPreviewResp:
        source_type = req.source_type or "local_directory"
        if source_type == "github_repo" and not (req.install_source or "").strip() and (req.github_url or "").strip():
            req = req.model_copy(update={"install_source": req.github_url.strip()})
        if not (req.doc_url or "").strip() and (req.docs_url or "").strip():
            req = req.model_copy(update={"doc_url": req.docs_url.strip()})
        local_path, resolved_path, exists = cls._resolve_subject(req)
        subject_dir = cls._subject_directory(local_path, source_type)
        normalized_doc_url = (req.doc_url or req.docs_url or "").strip()
        normalized_github_url = (req.github_url or "").strip()

        readme_path, readme_text = cls._load_readme(subject_dir) if subject_dir else (None, "")
        readme_title, readme_summary = cls._summarize_readme(readme_text)
        detected_files = cls._detect_files(local_path, subject_dir)

        suggested_name = readme_title or cls._default_name(req, local_path, resolved_path)
        default_description = readme_summary or cls._default_description(source_type, suggested_name)

        run_suggestions = cls._build_run_suggestions(req, local_path, subject_dir, readme_text)
        install_suggestions = cls._build_install_suggestions(req, exists)
        healthcheck_suggestions = cls._build_healthcheck_suggestions(run_suggestions)
        credential_mode_suggestions = cls._build_credential_mode_suggestions(
            req,
            subject_dir,
            readme_text,
        )

        warnings = cls._build_warnings(req, source_type, exists, subject_dir, run_suggestions)
        recommended = run_suggestions[0] if run_suggestions else None
        structured_suggestions = cls._build_structured_suggestions(
            req=req,
            suggested_name=suggested_name,
            readme_summary=readme_summary,
            detected_files=detected_files,
            install_suggestions=install_suggestions,
            run_suggestions=run_suggestions,
            healthcheck_suggestions=healthcheck_suggestions,
            credential_mode_suggestions=credential_mode_suggestions,
            warnings=warnings,
        )
        assist_sources = [item for item in [normalized_github_url, normalized_doc_url, str(local_path) if local_path else ""] if item]
        assist_summary = cls._build_assist_summary(
            req=req,
            suggested_name=suggested_name,
            readme_summary=readme_summary,
            exists=exists,
            warnings=warnings,
            recommended=recommended,
        )

        return CLIToolPreviewResp(
            tool_dir=req.tool_dir,
            source_type=source_type,
            install_source=req.install_source,
            doc_url=normalized_doc_url,
            docs_url=normalized_doc_url,
            github_url=normalized_github_url,
            local_path=str(local_path) if local_path else req.local_path,
            resolved_path=str(resolved_path),
            exists=exists,
            suggested_name=suggested_name,
            default_description=default_description,
            readme_path=str(readme_path) if readme_path else None,
            readme_summary=readme_summary or None,
            command_candidates=run_suggestions,
            recommended=recommended,
            candidates=run_suggestions,
            install_suggestions=install_suggestions,
            run_suggestions=run_suggestions,
            healthcheck_suggestions=healthcheck_suggestions,
            credential_mode_suggestions=credential_mode_suggestions,
            display_name=suggested_name,
            description=default_description,
            readme_excerpt=readme_summary or None,
            detected_files=detected_files,
            suggested_install_command=cls._format_shell_command(install_suggestions[0]) if install_suggestions else None,
            suggested_healthcheck_command=healthcheck_suggestions[0].healthcheck_command if healthcheck_suggestions else None,
            assist_summary=assist_summary,
            assist_sources=assist_sources,
            structured_suggestions=structured_suggestions,
            warnings=warnings,
        )

    @classmethod
    def _build_assist_summary(
        cls,
        req: CLIToolPreviewReq,
        suggested_name: str,
        readme_summary: str,
        exists: bool,
        warnings: list[str],
        recommended: Optional[CLIToolPreviewCommand],
    ) -> str:
        parts = [f"已按 {req.source_type} 方式分析 {suggested_name}。"]
        if readme_summary:
            parts.append(readme_summary)
        elif recommended:
            parts.append(f"推荐先用 `{recommended.command}` 作为启动命令。")
        if not exists and warnings:
            parts.append(warnings[0])
        if req.notes:
            parts.append(f"备注：{req.notes.strip()}")
        return " ".join(part for part in parts if part).strip()

    @classmethod
    def _build_structured_suggestions(
        cls,
        *,
        req: CLIToolPreviewReq,
        suggested_name: str,
        readme_summary: str,
        detected_files: list[str],
        install_suggestions: list[CLIToolPreviewCommand],
        run_suggestions: list[CLIToolPreviewCommand],
        healthcheck_suggestions: list[CLIToolPreviewCommand],
        credential_mode_suggestions: list[CLIToolCredentialModeSuggestion],
        warnings: list[str],
    ) -> list[CLIToolStructuredSuggestion]:
        suggestions: list[CLIToolStructuredSuggestion] = []

        if install_suggestions:
            item = install_suggestions[0]
            suggestions.append(
                CLIToolStructuredSuggestion(
                    id="install",
                    title="安装方式",
                    summary=item.reason or "优先使用这条安装命令接入 CLI。",
                    confidence=item.confidence,
                    notes=item.notes,
                    warnings=warnings,
                    detected_files=detected_files,
                    references=[req.install_source] if req.install_source else [],
                    command=item.command,
                    args_template=item.args_template,
                    cwd_mode=item.cwd_mode,
                    install_source=req.install_source or None,
                    install_command=cls._format_shell_command(item),
                )
            )

        if run_suggestions:
            item = run_suggestions[0]
            suggestions.append(
                CLIToolStructuredSuggestion(
                    id="run",
                    title="启动命令",
                    summary=item.reason or f"推荐把 {suggested_name} 挂成默认运行命令。",
                    confidence=item.confidence,
                    notes=item.notes,
                    warnings=[],
                    detected_files=detected_files,
                    references=[req.local_path or req.tool_dir] if (req.local_path or req.tool_dir) else [],
                    command=item.command,
                    args_template=item.args_template,
                    cwd_mode=item.cwd_mode,
                    cwd=item.cwd,
                    display_name=suggested_name,
                    tool_name=suggested_name,
                    tool_dir=req.tool_dir or req.local_path or None,
                )
            )

        if healthcheck_suggestions:
            item = healthcheck_suggestions[0]
            suggestions.append(
                CLIToolStructuredSuggestion(
                    id="healthcheck",
                    title="健康检查",
                    summary=item.reason or "保存前建议先准备一条健康检查命令。",
                    confidence=item.confidence,
                    notes=item.notes,
                    references=[],
                    command=item.command,
                    args_template=item.args_template,
                    cwd_mode=item.cwd_mode,
                    cwd=item.cwd,
                    healthcheck_command=item.healthcheck_command,
                )
            )

        if credential_mode_suggestions:
            item = credential_mode_suggestions[0]
            mode_label = {
                "none": "无需凭证",
                "env": "环境变量",
                "profiles": "多 profile",
                "manual": "手工输入",
            }.get(item.mode, item.mode)
            suggestions.append(
                CLIToolStructuredSuggestion(
                    id="credentials",
                    title="凭证模式",
                    summary=item.reason or f"建议先按 {mode_label} 管理凭证。",
                    confidence=item.confidence,
                    notes=item.notes + ([f"环境变量：{', '.join(item.env_vars)}"] if item.env_vars else []),
                    references=item.env_vars,
                )
            )

        if not suggestions:
            suggestions.append(
                CLIToolStructuredSuggestion(
                    id="fallback",
                    title="手工接入",
                    summary=readme_summary or "没有自动识别到稳定命令，可以先按 README 手工填写。",
                    confidence=0.3,
                    warnings=warnings,
                    detected_files=detected_files,
                )
            )

        return suggestions

    @classmethod
    def _resolve_subject(cls, req: CLIToolPreviewReq) -> tuple[Optional[Path], Path, bool]:
        source_type = req.source_type or "local_directory"
        local_path_raw = (req.local_path or "").strip()
        tool_dir_raw = (req.tool_dir or "").strip()

        if source_type == "local_directory":
            if local_path_raw:
                local_path = cls._resolve_local_path(local_path_raw)
                return local_path, local_path, local_path.is_dir()
            if tool_dir_raw:
                cli_root = cls._get_cli_tools_root()
                resolved = cls._resolve_tool_dir(cli_root, tool_dir_raw)
                return resolved, resolved, resolved.is_dir()
            raise ValueError("tool_dir or local_path is required for local_directory")

        if source_type == "executable":
            subject = local_path_raw or tool_dir_raw or req.command
            if not subject:
                raise ValueError("local_path, tool_dir, or command is required for executable")
            resolved = cls._resolve_local_path(subject)
            return resolved, resolved, resolved.is_file()

        if local_path_raw:
            resolved = cls._resolve_local_path(local_path_raw)
            return resolved, resolved, resolved.exists()

        return None, Path(tool_dir_raw or req.install_source or req.command or ""), False

    @classmethod
    def _subject_directory(cls, local_path: Optional[Path], source_type: str) -> Optional[Path]:
        if local_path is None or not local_path.exists():
            return None
        if source_type == "executable" and local_path.is_file():
            return local_path.parent
        if local_path.is_dir():
            return local_path
        return None

    @classmethod
    def _build_run_suggestions(
        cls,
        req: CLIToolPreviewReq,
        local_path: Optional[Path],
        subject_dir: Optional[Path],
        readme_text: str,
    ) -> list[CLIToolPreviewCommand]:
        candidates: list[CLIToolPreviewCommand] = []

        explicit_command = (req.command or "").strip()
        if explicit_command:
            candidates.append(
                CLIToolPreviewCommand(
                    command=explicit_command,
                    args_template=[],
                    cwd_mode="tool_dir" if subject_dir else "workspace",
                    source="user_input",
                    confidence=0.99,
                    label="Provided command",
                    reason="Frontend provided an explicit run command.",
                    notes=["User-supplied command."],
                )
            )

        if req.source_type == "executable" and local_path:
            candidates.append(
                CLIToolPreviewCommand(
                    command=str(local_path),
                    args_template=[],
                    cwd_mode="workspace",
                    source="local_executable",
                    confidence=0.98 if local_path.exists() else 0.72,
                    label="Local executable",
                    reason="Run the selected executable directly.",
                    notes=[f"Resolved from local path: {local_path}"],
                )
            )

        if subject_dir and subject_dir.is_dir():
            candidates.extend(cls._discover_readme_candidates(readme_text, subject_dir))
            candidates.extend(cls._discover_executable_candidates(subject_dir))
            candidates.extend(cls._discover_package_json_candidates(subject_dir))
            candidates.extend(cls._discover_pyproject_candidates(subject_dir))

        if req.source_type == "npm_package":
            candidates.extend(cls._build_package_run_suggestions(req, package_manager="npm"))
        elif req.source_type == "python_package":
            candidates.extend(cls._build_package_run_suggestions(req, package_manager="pip"))
        elif req.source_type == "github_repo":
            candidates.extend(cls._build_repo_run_suggestions(req, subject_dir))

        candidates = cls._dedupe_candidates(candidates)
        candidates.sort(
            key=lambda item: (-item.confidence, item.command, len(item.args_template))
        )
        return candidates

    @classmethod
    def _build_install_suggestions(
        cls,
        req: CLIToolPreviewReq,
        exists: bool,
    ) -> list[CLIToolPreviewCommand]:
        install_source = (req.install_source or "").strip()
        source_type = req.source_type or "local_directory"
        suggestions: list[CLIToolPreviewCommand] = []

        if source_type == "local_directory":
            return suggestions

        if source_type == "executable":
            if exists:
                return suggestions
            suggestions.append(
                CLIToolPreviewCommand(
                    command="manual",
                    args_template=[],
                    cwd_mode="workspace",
                    source="manual_install",
                    confidence=0.45,
                    label="Manual setup",
                    reason="Executable tools are usually copied into a local path or added to PATH manually.",
                    notes=["No automatic installer was inferred."],
                )
            )
            return suggestions

        if source_type == "npm_package" and install_source:
            suggestions.append(
                CLIToolPreviewCommand(
                    command="pnpm",
                    args_template=["dlx", install_source],
                    cwd_mode="workspace",
                    source="pnpm_dlx",
                    confidence=0.89,
                    label="One-off run",
                    reason="Run the package without a permanent global install.",
                )
            )
            suggestions.append(
                CLIToolPreviewCommand(
                    command="npm",
                    args_template=["install", "-g", install_source],
                    cwd_mode="workspace",
                    source="npm_install",
                    confidence=0.88,
                    label="Global npm install",
                    reason="Install the package globally so its CLI entry is available on PATH.",
                )
            )
            return suggestions

        if source_type == "python_package" and install_source:
            suggestions.append(
                CLIToolPreviewCommand(
                    command="pip",
                    args_template=["install", install_source],
                    cwd_mode="workspace",
                    source="pip_install",
                    confidence=0.9,
                    label="pip install",
                    reason="Install the Python package into the current backend environment.",
                )
            )
            suggestions.append(
                CLIToolPreviewCommand(
                    command="uv",
                    args_template=["tool", "install", install_source],
                    cwd_mode="workspace",
                    source="uv_tool_install",
                    confidence=0.72,
                    label="uv tool install",
                    reason="Install as an isolated CLI if uv is available.",
                )
            )
            return suggestions

        if source_type == "github_repo" and install_source:
            repo_url = cls._normalize_repo_url(install_source)
            target_dir = cls._default_clone_dir(req)
            suggestions.append(
                CLIToolPreviewCommand(
                    command="git",
                    args_template=["clone", repo_url, target_dir],
                    cwd_mode="workspace",
                    source="git_clone",
                    confidence=0.86,
                    label="Clone repository",
                    reason="Clone the repository locally before wiring its CLI entry.",
                )
            )
            return suggestions

        return suggestions

    @classmethod
    def _build_healthcheck_suggestions(
        cls,
        run_suggestions: list[CLIToolPreviewCommand],
    ) -> list[CLIToolPreviewCommand]:
        suggestions: list[CLIToolPreviewCommand] = []
        for candidate in run_suggestions[:3]:
            healthcheck_args = list(candidate.args_template)
            if "--help" not in healthcheck_args and "-h" not in healthcheck_args:
                healthcheck_args.append("--help")
            shell_command = cls._format_shell_tokens(candidate.command, healthcheck_args)
            suggestions.append(
                candidate.model_copy(
                    update={
                        "source": f"{candidate.source}_healthcheck",
                        "confidence": max(candidate.confidence - 0.02, 0.0),
                        "label": candidate.label or "Healthcheck",
                        "reason": candidate.reason or "Verify the CLI boots and prints usage.",
                        "healthcheck_command": shell_command,
                    }
                )
            )
        return suggestions

    @classmethod
    def _build_credential_mode_suggestions(
        cls,
        req: CLIToolPreviewReq,
        subject_dir: Optional[Path],
        readme_text: str,
    ) -> list[CLIToolCredentialModeSuggestion]:
        manifest_mode = cls._read_manifest_credential_mode(subject_dir)
        if manifest_mode:
            return [
                CLIToolCredentialModeSuggestion(
                    mode=manifest_mode,
                    confidence=0.97,
                    reason="Credential mode declared by local manifest.yaml.",
                )
            ]

        lowered = readme_text.lower()
        env_vars = sorted(
            {
                token
                for token in _ENV_VAR_PATTERN.findall(readme_text)
                if any(keyword in token for keyword in ("KEY", "TOKEN", "SECRET", "PASSWORD", "API"))
            }
        )
        if env_vars or any(keyword in lowered for keyword in ("api key", "access token", "setx ", "export ")):
            return [
                CLIToolCredentialModeSuggestion(
                    mode="env",
                    confidence=0.72,
                    reason="README hints that credentials are provided through environment variables.",
                    env_vars=env_vars,
                )
            ]

        if any(keyword in lowered for keyword in ("profile", "profiles", "credential profile")):
            return [
                CLIToolCredentialModeSuggestion(
                    mode="profiles",
                    confidence=0.61,
                    reason="README suggests a reusable profile-based credential setup.",
                )
            ]

        if req.source_type in {"npm_package", "python_package", "github_repo", "local_directory", "executable"}:
            return [
                CLIToolCredentialModeSuggestion(
                    mode="none",
                    confidence=0.55,
                    reason="No credential requirement was detected from the local files or provided metadata.",
                )
            ]

        return []

    @classmethod
    def _build_package_run_suggestions(
        cls,
        req: CLIToolPreviewReq,
        package_manager: str,
    ) -> list[CLIToolPreviewCommand]:
        install_source = (req.install_source or "").strip()
        command_name = (req.command or "").strip()
        suggestions: list[CLIToolPreviewCommand] = []

        if package_manager == "npm":
            if command_name:
                suggestions.append(
                    CLIToolPreviewCommand(
                        command=command_name,
                        args_template=[],
                        cwd_mode="workspace",
                        source="npm_command",
                        confidence=0.93,
                        label="Installed CLI command",
                        reason="Use the explicit command provided by the frontend.",
                    )
                )
            elif install_source:
                suggestions.append(
                    CLIToolPreviewCommand(
                        command="pnpm",
                        args_template=["dlx", install_source],
                        cwd_mode="workspace",
                        source="pnpm_dlx",
                        confidence=0.8,
                        label="pnpm dlx",
                        reason="Run the npm package without assuming a global install.",
                    )
                )
            return suggestions

        if command_name:
            suggestions.append(
                CLIToolPreviewCommand(
                    command=command_name,
                    args_template=[],
                    cwd_mode="workspace",
                    source="python_command",
                    confidence=0.93,
                    label="Installed CLI command",
                    reason="Use the explicit command provided by the frontend.",
                )
            )
        elif install_source:
            module_name = install_source.replace("-", "_")
            suggestions.append(
                CLIToolPreviewCommand(
                    command="python",
                    args_template=["-m", module_name],
                    cwd_mode="workspace",
                    source="python_module",
                    confidence=0.66,
                    label="python -m",
                    reason="Fallback run command derived from the package name.",
                )
            )
        return suggestions

    @classmethod
    def _build_repo_run_suggestions(
        cls,
        req: CLIToolPreviewReq,
        subject_dir: Optional[Path],
    ) -> list[CLIToolPreviewCommand]:
        if subject_dir and subject_dir.exists():
            return []

        command_name = (req.command or "").strip()
        if not command_name:
            return []

        return [
            CLIToolPreviewCommand(
                command=command_name,
                args_template=[],
                cwd_mode="workspace",
                source="github_repo_command",
                confidence=0.75,
                label="Repository command",
                reason="Use the provided command after cloning and installing dependencies.",
            )
        ]

    @classmethod
    def _build_warnings(
        cls,
        req: CLIToolPreviewReq,
        source_type: str,
        exists: bool,
        subject_dir: Optional[Path],
        run_suggestions: list[CLIToolPreviewCommand],
    ) -> list[str]:
        warnings: list[str] = []
        if source_type == "local_directory" and not exists:
            warnings.append("Tool directory does not exist.")
        if source_type == "executable" and not exists:
            warnings.append("Executable path does not exist.")
        if source_type in {"npm_package", "python_package", "github_repo"} and not (req.install_source or req.command):
            warnings.append("No install source or command was provided.")
        if subject_dir and exists and not run_suggestions:
            warnings.append("No obvious CLI entry was discovered.")
        if req.doc_url and not _URL_PATTERN.match(req.doc_url):
            warnings.append("doc_url is present but is not a valid http(s) URL.")
        return warnings

    @classmethod
    def _get_cli_tools_root(cls) -> Path:
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

    @classmethod
    def _resolve_tool_dir(cls, cli_root: Path, tool_dir: str) -> Path:
        if not tool_dir or not tool_dir.strip():
            raise ValueError("tool_dir is required")

        candidate = (cli_root / Path(tool_dir)).resolve()
        if candidate != cli_root and cli_root not in candidate.parents:
            raise ValueError("tool_dir escapes cli_tools root")
        return candidate

    @classmethod
    def _resolve_local_path(cls, raw_path: str) -> Path:
        path = Path(raw_path)
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        else:
            path = path.resolve()
        return path

    @classmethod
    def _load_readme(cls, tool_path: Path) -> tuple[Optional[Path], str]:
        for name in _README_NAMES:
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
                label="README example",
                reason="Command found in README usage examples.",
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
                            label="Executable file",
                            reason="Discovered an executable file under the tool directory.",
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
                            label="Python entrypoint",
                            reason="Discovered a common Python CLI entry file.",
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
                    label="package.json bin",
                    reason="Use the package bin entry through node.",
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
                        label="package.json bin",
                        reason="Use the package bin entry through node.",
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
                        label="package.json script",
                        reason="Run the CLI-oriented npm script from package.json.",
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
                    label="Python console script",
                    reason="Derived from pyproject console scripts.",
                    notes=[f"{source_name}: {script_name} -> {script_value}"],
                )
            )

        return candidates

    @classmethod
    def _read_manifest_credential_mode(cls, subject_dir: Optional[Path]) -> Optional[str]:
        if subject_dir is None:
            return None

        manifest_path = subject_dir / "manifest.yaml"
        if not manifest_path.is_file():
            return None

        text = manifest_path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"credentials:\s*(?:\r?\n\s+.*)*?\r?\n\s*mode:\s*([A-Za-z_]+)", text)
        if not match:
            return None

        mode = match.group(1).strip().lower()
        if mode in {"none", "env", "profiles", "manual"}:
            return mode
        return None

    @classmethod
    def _detect_files(cls, local_path: Optional[Path], subject_dir: Optional[Path]) -> list[str]:
        if local_path and local_path.is_file():
            return [local_path.name]

        if not subject_dir or not subject_dir.exists():
            return []

        files = []
        for child in sorted(subject_dir.iterdir(), key=lambda item: item.name.lower()):
            files.append(child.name)
            if len(files) >= 12:
                break
        return files

    @classmethod
    def _default_name(
        cls,
        req: CLIToolPreviewReq,
        local_path: Optional[Path],
        resolved_path: Path,
    ) -> str:
        if req.install_source:
            return cls._humanize_name(req.install_source.split("/")[-1])
        if req.command:
            return cls._humanize_name(req.command)
        if local_path:
            return cls._humanize_name(local_path.stem if local_path.is_file() else local_path.name)
        return cls._humanize_name(resolved_path.stem or resolved_path.name)

    @classmethod
    def _default_description(cls, source_type: str, suggested_name: str) -> str:
        labels = {
            "local_directory": "Local CLI tool directory",
            "executable": "Local executable CLI tool",
            "npm_package": "CLI tool installed from an npm package",
            "python_package": "CLI tool installed from a Python package",
            "github_repo": "CLI tool sourced from a GitHub repository",
        }
        prefix = labels.get(source_type, "CLI tool")
        return f"{prefix}: {suggested_name}"

    @classmethod
    def _normalize_repo_url(cls, install_source: str) -> str:
        if _URL_PATTERN.match(install_source):
            return install_source
        return f"https://github.com/{install_source}.git"

    @classmethod
    def _default_clone_dir(cls, req: CLIToolPreviewReq) -> str:
        if req.local_path:
            return req.local_path
        if req.install_source:
            return req.install_source.rstrip("/").split("/")[-1]
        return "cli-tool"

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

    @classmethod
    def _format_shell_command(cls, candidate: CLIToolPreviewCommand) -> str:
        return cls._format_shell_tokens(candidate.command, candidate.args_template)

    @classmethod
    def _format_shell_tokens(cls, command: str, args: list[str]) -> str:
        return " ".join([command, *args]).strip()
