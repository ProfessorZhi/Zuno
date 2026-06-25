from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from zuno.services.graphrag.models import GraphRAGProjectContract


def _find_repo_root(package_root: Path) -> Path:
    for parent in package_root.parents:
        if (parent / "docs" / "architecture").exists() and (parent / "README.md").exists():
            return parent
    return package_root.parents[-1]


@dataclass(slots=True)
class ProjectReadiness:
    ready: bool
    status: str
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "status": self.status,
            "errors": list(self.errors),
        }


@dataclass(slots=True)
class LoadedGraphRAGProject:
    base_path: str
    contract: GraphRAGProjectContract
    settings: dict[str, Any]
    prompt_paths: dict[str, str]
    prompt_texts: dict[str, str]
    readiness: ProjectReadiness

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_path": self.base_path,
            "contract": self.contract.model_dump(),
            "settings": dict(self.settings),
            "prompt_paths": dict(self.prompt_paths),
            "readiness": self.readiness.to_dict(),
        }


class GraphRAGSettingsValidator:
    @staticmethod
    def parse_settings(text: str, *, settings_path: Path) -> dict[str, Any]:
        payload = yaml.safe_load(text) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"{settings_path} must be a YAML object")
        return payload

    @staticmethod
    def validate_contract(payload: dict[str, Any], *, project_id: str, settings_path: Path) -> GraphRAGProjectContract:
        contract_payload = {
            key: value
            for key, value in payload.items()
            if key in GraphRAGProjectContract.model_fields
        }
        contract_payload.setdefault("graphrag_project_id", project_id)
        contract_payload["settings_path"] = str(settings_path)
        if contract_payload.get("graphrag_project_id") != project_id:
            raise ValueError(
                f"graphrag_project_id mismatch: expected {project_id}, got {contract_payload.get('graphrag_project_id')}"
            )
        try:
            return GraphRAGProjectContract.model_validate(contract_payload)
        except ValidationError as err:
            raise ValueError(str(err)) from err

    @staticmethod
    def prompt_manifest(payload: dict[str, Any]) -> dict[str, str]:
        prompts = payload.get("prompts") or {}
        if not isinstance(prompts, dict):
            raise ValueError("prompts must be a YAML object")
        return {
            str(name): str(relative_path)
            for name, relative_path in prompts.items()
            if str(name).strip() and str(relative_path).strip()
        }


class GraphRAGProjectLoader:
    def __init__(self, projects_root: Path | None = None):
        repo_root = _find_repo_root(Path(__file__).resolve())
        self.projects_root = Path(projects_root) if projects_root else repo_root / "graphrag-projects"

    def load(self, project_id: str | None) -> LoadedGraphRAGProject | None:
        normalized = str(project_id or "").strip()
        if not normalized:
            return None

        project_dir = self.projects_root / normalized
        settings_path = project_dir / "settings.yaml"
        if not settings_path.exists():
            raise ValueError(f"settings.yaml not found: {normalized}")

        settings = GraphRAGSettingsValidator.parse_settings(
            settings_path.read_text(encoding="utf-8"),
            settings_path=settings_path,
        )
        contract = GraphRAGSettingsValidator.validate_contract(
            settings,
            project_id=normalized,
            settings_path=settings_path,
        )
        prompt_paths, prompt_texts, readiness_errors = self._load_prompts(
            project_dir,
            GraphRAGSettingsValidator.prompt_manifest(settings),
        )
        ready = contract.status == "ready" and not readiness_errors
        readiness = ProjectReadiness(
            ready=ready,
            status="ready" if ready else "not_ready",
            errors=readiness_errors,
        )
        return LoadedGraphRAGProject(
            base_path=str(project_dir),
            contract=contract,
            settings=settings,
            prompt_paths=prompt_paths,
            prompt_texts=prompt_texts,
            readiness=readiness,
        )

    @staticmethod
    def _load_prompts(
        project_dir: Path,
        prompts: dict[str, str],
    ) -> tuple[dict[str, str], dict[str, str], list[str]]:
        prompt_paths: dict[str, str] = {}
        prompt_texts: dict[str, str] = {}
        errors: list[str] = []
        for name, relative_path in prompts.items():
            path = project_dir / relative_path
            if not path.is_file():
                errors.append(f"missing prompt: {name}")
                continue
            prompt_paths[name] = str(path)
            prompt_texts[name] = path.read_text(encoding="utf-8")
        return prompt_paths, prompt_texts, errors


__all__ = [
    "GraphRAGProjectLoader",
    "GraphRAGSettingsValidator",
    "LoadedGraphRAGProject",
    "ProjectReadiness",
]
