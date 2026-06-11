from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from agentchat.core.agents.structured_response_agent import StructuredResponseAgent
from agentchat.database.dao.agent_skill import AgentSkillDao
from agentchat.database.models.agent_skill import AgentSkill
from agentchat.prompts.skill import AgentSkillAsToolPrompt
from agentchat.schema.agent_skill import (
    AgentSkillCreateReq,
    AgentSkillFile,
    AgentSkillFolder,
    AgentSkillResponseFormat,
)


def default_agent_skill_folder(name: str, description: str) -> dict:
    default_skill_readme = f"""
---
name: {name}
description: {description}
---
    """

    default_folder = AgentSkillFolder(name=name, path=f"/{name}")
    default_folder.folder.append(
        AgentSkillFile(
            name="SKILL.md",
            path=f"/{name}/SKILL.md",
            content=default_skill_readme,
        )
    )
    default_folder.folder.append(AgentSkillFolder(name="reference", path=f"/{name}/reference"))
    default_folder.folder.append(AgentSkillFolder(name="scripts", path=f"/{name}/scripts"))
    return default_folder.model_dump()


class AgentSkillService:
    MAX_SKILL_RUNTIME_CHARS = 12000
    MAX_SKILL_EXTRA_FILES = 6
    HOST_SKILL_ROOT_ENV = "ZUNO_SKILLS_DIR"
    SYSTEM_SKILL_ROOT = Path(__file__).resolve().parents[2] / "system_skills"
    SYSTEM_SKILL_DEFINITIONS = (
        {
            "id": "system-skill-creator",
            "name": "skill-creator",
            "description": "Create a Zuno-compatible skill package from a user requirement.",
            "as_tool_name": "system_skill_creator",
            "folder_name": "skill-creator",
        },
        {
            "id": "system-skill-installer",
            "name": "skill-installer",
            "description": "Convert an existing local folder into a Zuno-compatible skill package.",
            "as_tool_name": "system_skill_installer",
            "folder_name": "skill-installer",
        },
    )

    @classmethod
    def is_system_skill_id(cls, skill_id: str | None) -> bool:
        return any(skill["id"] == skill_id for skill in cls.SYSTEM_SKILL_DEFINITIONS)

    @classmethod
    def is_host_skill_id(cls, skill_id: str | None) -> bool:
        return bool(skill_id and skill_id.startswith("host-skill-"))

    @classmethod
    def is_readonly_skill_id(cls, skill_id: str | None) -> bool:
        return cls.is_system_skill_id(skill_id) or cls.is_host_skill_id(skill_id)

    @classmethod
    def _get_host_skill_root(cls) -> Path:
        custom_root = os.getenv(cls.HOST_SKILL_ROOT_ENV, "").strip()
        if custom_root:
            return Path(custom_root).expanduser()
        return Path.home() / ".zuno" / "skills"

    @staticmethod
    def _read_text_file(file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def _strip_wrapping_quotes(value: str) -> str:
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1].strip()
        return value

    @classmethod
    def _parse_skill_frontmatter(cls, skill_md_content: str) -> dict[str, str]:
        match = re.match(r"^---\s*\n(.*?)\n---\s*", skill_md_content, re.DOTALL)
        if not match:
            return {}

        metadata: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = cls._strip_wrapping_quotes(value)
        return metadata

    @classmethod
    def _load_skill_json(cls, skill_dir: Path) -> dict[str, Any]:
        skill_json_path = skill_dir / "skill.json"
        if not skill_json_path.exists():
            return {}

        try:
            return json.loads(cls._read_text_file(skill_json_path))
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _sanitize_tool_name(name: str) -> str:
        sanitized = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        if not sanitized:
            sanitized = "host_skill"
        if not sanitized.endswith("_skill"):
            sanitized = f"{sanitized}_skill"
        return sanitized

    @staticmethod
    def _host_skill_id(folder_name: str) -> str:
        return f"host-skill-{folder_name}"

    @classmethod
    def _build_disk_skill_tree(cls, current_path: Path, root_path: str) -> list[AgentSkillFile | AgentSkillFolder]:
        items: list[AgentSkillFile | AgentSkillFolder] = []
        for child in sorted(current_path.iterdir(), key=lambda item: (item.is_file(), item.name.lower())):
            if child.name in {".gitkeep", "__pycache__"}:
                continue

            child_root_path = f"{root_path}/{child.name}"
            if child.is_dir():
                items.append(
                    AgentSkillFolder(
                        name=child.name,
                        path=child_root_path,
                        folder=cls._build_disk_skill_tree(child, child_root_path),
                    )
                )
                continue

            items.append(
                AgentSkillFile(
                    name=child.name,
                    path=child_root_path,
                    content=cls._read_text_file(child),
                )
            )
        return items

    @classmethod
    def _build_system_skill_folder(cls, skill_name: str, readme_content: str) -> dict:
        root_path = f"/{skill_name}"
        return AgentSkillFolder(
            name=skill_name,
            path=root_path,
            folder=[
                AgentSkillFile(
                    name="SKILL.md",
                    path=f"{root_path}/SKILL.md",
                    content=readme_content,
                ),
                AgentSkillFolder(name="reference", path=f"{root_path}/reference"),
                AgentSkillFolder(name="scripts", path=f"{root_path}/scripts"),
            ],
        ).model_dump()

    @classmethod
    def _build_host_skill_folder(cls, folder_name: str, skill_dir: Path) -> dict:
        root_path = f"/{folder_name}"
        return AgentSkillFolder(
            name=folder_name,
            path=root_path,
            folder=cls._build_disk_skill_tree(skill_dir, root_path),
        ).model_dump()

    @classmethod
    def _load_system_skill(cls, definition: dict) -> SimpleNamespace:
        readme_path = cls.SYSTEM_SKILL_ROOT / definition["folder_name"] / "SKILL.md"
        readme_content = cls._read_text_file(readme_path).strip()
        now = datetime.now()
        return SimpleNamespace(
            id=definition["id"],
            name=definition["name"],
            description=definition["description"],
            user_id="system",
            as_tool_name=definition["as_tool_name"],
            folder=cls._build_system_skill_folder(definition["name"], readme_content),
            create_time=now,
            update_time=now,
            is_system=True,
            is_readonly=True,
            source="system",
        )

    @classmethod
    def _load_host_skill(cls, skill_dir: Path) -> SimpleNamespace | None:
        skill_md_path = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md_path.exists():
            return None

        skill_md_content = cls._read_text_file(skill_md_path).strip()
        frontmatter = cls._parse_skill_frontmatter(skill_md_content)
        skill_json = cls._load_skill_json(skill_dir)

        folder_name = skill_dir.name
        skill_name = (
            str(skill_json.get("name") or frontmatter.get("name") or folder_name)
        ).strip()
        description = (
            str(skill_json.get("description") or frontmatter.get("description") or "")
        ).strip() or f"Host skill loaded from {skill_dir}"

        now = datetime.now()
        return SimpleNamespace(
            id=cls._host_skill_id(folder_name),
            name=skill_name,
            description=description,
            user_id="host",
            as_tool_name=cls._sanitize_tool_name(skill_name),
            folder=cls._build_host_skill_folder(folder_name, skill_dir),
            create_time=now,
            update_time=now,
            is_system=False,
            is_readonly=True,
            source="host",
        )

    @classmethod
    def list_system_skills(cls) -> list[SimpleNamespace]:
        return [cls._load_system_skill(definition) for definition in cls.SYSTEM_SKILL_DEFINITIONS]

    @classmethod
    def list_host_skills(cls) -> list[SimpleNamespace]:
        host_root = cls._get_host_skill_root()
        if not host_root.exists() or not host_root.is_dir():
            return []

        host_skills: list[SimpleNamespace] = []
        for skill_dir in sorted(host_root.iterdir(), key=lambda item: item.name.lower()):
            skill = cls._load_host_skill(skill_dir)
            if skill is not None:
                host_skills.append(skill)
        return host_skills

    @classmethod
    def list_builtin_skills(cls) -> list[SimpleNamespace]:
        return [*cls.list_system_skills(), *cls.list_host_skills()]

    @classmethod
    def _serialize_skill(cls, skill) -> dict:
        if hasattr(skill, "to_dict"):
            data = skill.to_dict()
        elif hasattr(skill, "model_dump"):
            data = skill.model_dump()
        elif hasattr(skill, "__dict__"):
            data = vars(skill).copy()
        else:
            data = dict(skill)

        data["is_system"] = bool(getattr(skill, "is_system", False))
        data["is_readonly"] = bool(getattr(skill, "is_readonly", data["is_system"]))
        data["source"] = getattr(skill, "source", "user")
        return data

    @classmethod
    async def create_agent_skill(cls, agent_skill_req: AgentSkillCreateReq, user_id: str) -> dict:
        structured_agent = StructuredResponseAgent(AgentSkillResponseFormat)
        structured_response = structured_agent.get_structured_response(
            AgentSkillAsToolPrompt.format(
                name=agent_skill_req.name,
                description=agent_skill_req.description,
            )
        )

        agent_skill = AgentSkill(
            **agent_skill_req.model_dump(),
            user_id=user_id,
            as_tool_name=structured_response.as_tool_name,
            folder=default_agent_skill_folder(agent_skill_req.name, agent_skill_req.description),
        )

        await AgentSkillDao.create_agent_skill(agent_skill)
        return agent_skill.model_dump()

    @classmethod
    async def delete_agent_skill(cls, agent_skill_id: str):
        if cls.is_readonly_skill_id(agent_skill_id):
            raise ValueError("Readonly skills cannot be deleted.")
        return await AgentSkillDao.delete_agent_skill(agent_skill_id)

    @classmethod
    async def get_agent_skills(cls, user_id: str) -> list[dict]:
        results = await AgentSkillDao.get_agent_skills(user_id)
        return [cls._serialize_skill(skill) for skill in [*cls.list_builtin_skills(), *results]]

    @classmethod
    async def get_agent_skill_by_id(cls, agent_skill_id: str) -> dict:
        for skill in cls.list_builtin_skills():
            if skill.id == agent_skill_id:
                return cls._serialize_skill(skill)
        result = await AgentSkillDao.get_agent_skill_by_id(agent_skill_id)
        return cls._serialize_skill(result)

    @classmethod
    async def get_agent_skills_by_ids(cls, agent_skill_ids: list[str]) -> list:
        if not agent_skill_ids:
            return []

        builtin_skill_map = {skill.id: skill for skill in cls.list_builtin_skills()}
        database_skill_ids = [skill_id for skill_id in agent_skill_ids if skill_id not in builtin_skill_map]
        database_skills = await AgentSkillDao.get_agent_skills_by_ids(database_skill_ids)
        database_skill_map = {skill.id: skill for skill in database_skills}

        ordered_skills = []
        for skill_id in agent_skill_ids:
            if skill_id in builtin_skill_map:
                ordered_skills.append(builtin_skill_map[skill_id])
            elif skill_id in database_skill_map:
                ordered_skills.append(database_skill_map[skill_id])
        return ordered_skills

    @classmethod
    async def update_agent_skill_file(cls, agent_skill_id: str, target_path: str, new_content: str) -> dict:
        if cls.is_readonly_skill_id(agent_skill_id):
            raise ValueError("Readonly skills cannot be modified.")

        agent_skill = await AgentSkillDao.get_agent_skill_by_id(agent_skill_id)
        agent_skill_copy = agent_skill.folder.copy()

        for item in agent_skill_copy.get("folder", []):
            if item["path"] == target_path:
                item["content"] = new_content
                break

            if item.get("name") in ("reference", "scripts") and "folder" in item:
                for subitem in item["folder"]:
                    if subitem["path"] == target_path:
                        subitem["content"] = new_content

        agent_skill.folder = agent_skill_copy
        await AgentSkillDao.update_agent_skill(agent_skill)
        return agent_skill.model_dump()

    @classmethod
    async def add_agent_skill_file(cls, agent_skill_id: str, path: str, name: str) -> dict:
        if cls.is_readonly_skill_id(agent_skill_id):
            raise ValueError("Readonly skills cannot add files.")

        agent_skill = await AgentSkillDao.get_agent_skill_by_id(agent_skill_id)
        agent_skill_copy = agent_skill.folder.copy()

        for item in agent_skill_copy.get("folder", []):
            if item["path"] == path:
                if "folder" not in item:
                    item["folder"] = []
                item["folder"].append(
                    {
                        "name": name,
                        "type": "file",
                        "path": f"{path.rstrip('/')}/{name}",
                        "content": "",
                    }
                )
                break

        agent_skill.folder = agent_skill_copy
        await AgentSkillDao.update_agent_skill(agent_skill)
        return agent_skill.model_dump()

    @classmethod
    async def upload_agent_skill_file(cls, agent_skill_id: str, path: str, name: str, content: str) -> dict:
        if cls.is_readonly_skill_id(agent_skill_id):
            raise ValueError("Readonly skills cannot upload files.")

        agent_skill = await AgentSkillDao.get_agent_skill_by_id(agent_skill_id)
        agent_skill_copy = agent_skill.folder.copy()

        for item in agent_skill_copy.get("folder", []):
            if item["path"] == path:
                if "folder" not in item:
                    item["folder"] = []
                item["folder"].append(
                    {
                        "name": name,
                        "type": "file",
                        "path": f"{path.rstrip('/')}/{name}",
                        "content": content,
                    }
                )
                break

        agent_skill.folder = agent_skill_copy
        await AgentSkillDao.update_agent_skill(agent_skill)
        return agent_skill.model_dump()

    @classmethod
    async def delete_agent_skill_file(cls, agent_skill_id: str, path: str, name: str) -> dict:
        if cls.is_readonly_skill_id(agent_skill_id):
            raise ValueError("Readonly skills cannot delete files.")

        agent_skill = await AgentSkillDao.get_agent_skill_by_id(agent_skill_id)
        agent_skill_copy = agent_skill.folder.copy()

        target_path = f"{path.rstrip('/')}/{name}"
        for item in agent_skill_copy.get("folder", []):
            if item.get("path") == path and "folder" in item:
                item["folder"] = [f for f in item["folder"] if f.get("path") != target_path]
                break

        agent_skill.folder = agent_skill_copy
        await AgentSkillDao.update_agent_skill(agent_skill)
        return agent_skill.model_dump()

    @staticmethod
    def get_skill_md_content(data: dict) -> str:
        folder = data.get("folder", [])
        for item in folder:
            if item.get("name") == "SKILL.md" and item.get("type") == "file":
                return item.get("content", "")
        return ""

    @classmethod
    def _iter_skill_files(cls, node, parent_path: str = ""):
        if isinstance(node, dict):
            node_type = node.get("type")
            node_path = node.get("path") or parent_path
            if node_type == "file":
                yield {
                    "name": node.get("name", ""),
                    "path": node_path,
                    "content": node.get("content", "") or "",
                }
                return

            for child in node.get("folder", []):
                yield from cls._iter_skill_files(child, node_path)
            return

        if isinstance(node, list):
            for item in node:
                yield from cls._iter_skill_files(item, parent_path)

    @classmethod
    def build_skill_runtime_context(
        cls,
        agent_skill: AgentSkill,
        query: str | None = None,
        max_chars: int | None = None,
        max_extra_files: int | None = None,
    ) -> str:
        max_chars = max_chars or cls.MAX_SKILL_RUNTIME_CHARS
        max_extra_files = max_extra_files or cls.MAX_SKILL_EXTRA_FILES

        skill_files = list(cls._iter_skill_files(agent_skill.folder))
        skill_md = ""
        extra_files: list[dict] = []

        for file_info in skill_files:
            if file_info["name"] == "SKILL.md":
                skill_md = file_info["content"].strip()
            else:
                extra_files.append(file_info)

        header_lines = [
            f"Skill Name: {agent_skill.name}",
            f"Skill Description: {agent_skill.description or 'N/A'}",
        ]
        if query:
            header_lines.append(f"Current User Task: {query.strip()}")
        sections = ["\n".join(header_lines)]

        if skill_md:
            sections.append(f"[SKILL.md]\n{skill_md}")

        if extra_files:
            query_terms = {term for term in (query or "").lower().split() if len(term) > 1}

            def score_file(file_info: dict) -> tuple[int, int]:
                path = file_info["path"].lower()
                content = file_info["content"].lower()
                score = 0
                for term in query_terms:
                    if term in path:
                        score += 5
                    if term in content:
                        score += 1
                important_path = any(part in path for part in ("/reference/", "/scripts/"))
                return (score, 1 if important_path else 0)

            ranked_files = sorted(extra_files, key=score_file, reverse=True)
            selected_files: list[dict] = []
            selected_paths: set[str] = set()
            for file_info in ranked_files:
                if file_info["path"] in selected_paths:
                    continue
                selected_files.append(file_info)
                selected_paths.add(file_info["path"])
                if len(selected_files) >= max_extra_files:
                    break

            file_sections: list[str] = []
            for file_info in selected_files:
                file_content = file_info["content"].strip()
                if not file_content:
                    file_sections.append(f"- {file_info['path']} (empty)")
                    continue
                file_sections.append(f"[{file_info['path']}]\n{file_content}")
            if file_sections:
                sections.append("[Additional Skill Files]\n" + "\n\n".join(file_sections))

        runtime_text = "\n\n".join(section for section in sections if section.strip())
        if len(runtime_text) > max_chars:
            runtime_text = runtime_text[: max_chars - 20].rstrip() + "\n\n[truncated]"
        return runtime_text
