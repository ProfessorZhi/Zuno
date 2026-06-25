from __future__ import annotations

import json
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
    schema_data: dict[str, Any] = field(default_factory=dict)
    retrieval_policy_data: dict[str, Any] = field(default_factory=dict)
    eval_dataset_text: str | None = None
    eval_dataset_rows: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_path": self.base_path,
            "contract": self.contract.model_dump(),
            "settings": dict(self.settings),
            "prompt_paths": dict(self.prompt_paths),
            "readiness": self.readiness.to_dict(),
            "schema_data": dict(self.schema_data),
            "retrieval_policy_data": dict(self.retrieval_policy_data),
            "eval_dataset_rows": list(self.eval_dataset_rows),
        }

    def to_project_payload(self) -> dict[str, Any]:
        source_domain_pack = dict(self.settings.get("source_domain_pack") or {})
        prompts = dict(self.settings.get("prompts") or {})
        return {
            "id": self.contract.graphrag_project_id,
            "graphrag_project_id": self.contract.graphrag_project_id,
            "name": source_domain_pack.get("name") or self.contract.graphrag_project_id,
            "version": source_domain_pack.get("version") or self.contract.prompt_version or "project",
            "description": source_domain_pack.get("description") or "GraphRAG Project compatibility payload",
            "base_path": self.base_path,
            "schema": self.settings.get("schema_path"),
            "extraction_prompt": prompts.get("extract_graph"),
            "retrieval_policy": self.settings.get("retrieval_policy_path"),
            "answer_template": prompts.get("local_query"),
            "report_template": prompts.get("report_template"),
            "eval_dataset": self.settings.get("eval_dataset_path"),
            "schema_path": str(Path(self.base_path) / str(self.settings.get("schema_path") or "")),
            "retrieval_policy_path": str(Path(self.base_path) / str(self.settings.get("retrieval_policy_path") or "")),
            "eval_dataset_path": str(Path(self.base_path) / str(self.settings.get("eval_dataset_path") or "")),
            "schema_data": dict(self.schema_data),
            "retrieval_policy_data": dict(self.retrieval_policy_data),
            "extraction_prompt_text": self.prompt_texts.get("extract_graph"),
            "answer_template_text": self.prompt_texts.get("local_query"),
            "report_template_text": self.prompt_texts.get("report_template"),
            "eval_dataset_text": self.eval_dataset_text,
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
        settings = self._load_retrieval_policy(project_dir, settings)
        contract = GraphRAGSettingsValidator.validate_contract(
            settings,
            project_id=normalized,
            settings_path=settings_path,
        )
        prompt_paths, prompt_texts, readiness_errors = self._load_prompts(
            project_dir,
            GraphRAGSettingsValidator.prompt_manifest(settings),
        )
        schema_data = self._load_json_asset(
            project_dir,
            str(settings.get("schema_path") or "").strip(),
        )
        eval_dataset_text, eval_dataset_rows = self._load_eval_dataset(
            project_dir,
            str(settings.get("eval_dataset_path") or "").strip(),
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
            schema_data=schema_data,
            retrieval_policy_data=dict(settings.get("retrieval_policy") or {}),
            eval_dataset_text=eval_dataset_text,
            eval_dataset_rows=eval_dataset_rows,
        )

    @staticmethod
    def _load_retrieval_policy(project_dir: Path, settings: dict[str, Any]) -> dict[str, Any]:
        relative_path = str(settings.get("retrieval_policy_path") or "").strip()
        if not relative_path:
            return settings
        policy_path = project_dir / relative_path
        if not policy_path.is_file():
            raise ValueError(f"retrieval_policy_path not found: {relative_path}")
        payload = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"{policy_path} must be a YAML object")
        merged = dict(settings)
        merged["retrieval_policy"] = payload
        return merged

    @staticmethod
    def _load_json_asset(project_dir: Path, relative_path: str) -> dict[str, Any]:
        if not relative_path:
            return {}
        asset_path = project_dir / relative_path
        if not asset_path.is_file():
            raise ValueError(f"project asset not found: {relative_path}")
        payload = json.loads(asset_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{asset_path} must be a JSON object")
        return payload

    @staticmethod
    def _load_eval_dataset(project_dir: Path, relative_path: str) -> tuple[str | None, list[dict[str, Any]]]:
        if not relative_path:
            return None, []
        asset_path = project_dir / relative_path
        if not asset_path.is_file():
            raise ValueError(f"project asset not found: {relative_path}")
        text = asset_path.read_text(encoding="utf-8")
        rows: list[dict[str, Any]] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"{asset_path} rows must be JSON objects")
            rows.append(payload)
        return text, rows

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
