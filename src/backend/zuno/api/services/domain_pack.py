from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from zuno.services.domain_pack.loader import DomainPackLoader


class DomainPackService:
    @staticmethod
    def _safe_pack_id(value: str | None) -> str:
        pack_id = str(value or "").strip().replace(" ", "_")
        if not pack_id:
            raise ValueError("domain pack id is required")
        if any(part in {"", ".", ".."} for part in Path(pack_id).parts) or "/" in pack_id or "\\" in pack_id:
            raise ValueError(f"invalid domain pack id: {value}")
        return pack_id

    @classmethod
    def _pack_dir(cls, pack_id: str) -> Path:
        loader = DomainPackLoader()
        return loader.packs_root / cls._safe_pack_id(pack_id)

    @staticmethod
    def _pack_status(pack_dir: Path) -> str:
        return "published" if (pack_dir / "pack.yaml").exists() else "draft"

    @staticmethod
    def _read_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"domain pack manifest must be an object: {path.name}")
        return payload

    @staticmethod
    def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    @staticmethod
    def _default_schema() -> dict[str, list[str]]:
        return {
            "entities": ["Document", "Topic", "Requirement"],
            "relations": ["MENTIONS", "DEPENDS_ON", "SUPPORTS"],
        }

    @staticmethod
    def _default_retrieval_policy() -> dict[str, Any]:
        return {
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
            "citation_strictness": "medium",
            "risk_relation_preference": "SUPPORTS",
            "graph_seed_terms": ["topic", "requirement"],
            "graph_relation_cues": ["depends on", "supports"],
            "graph_step_cues": ["evidence", "source"],
        }

    @staticmethod
    def _read_json_asset(pack_dir: Path, manifest: dict[str, Any], key: str) -> Any | None:
        path_value = manifest.get(key)
        if not path_value:
            return None
        path = pack_dir / str(path_value)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _read_text_asset(pack_dir: Path, manifest: dict[str, Any], key: str) -> str | None:
        path_value = manifest.get(key)
        if not path_value:
            return None
        path = pack_dir / str(path_value)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    @classmethod
    def _read_yaml_asset(cls, pack_dir: Path, manifest: dict[str, Any], key: str) -> dict[str, Any] | None:
        path_value = manifest.get(key)
        if not path_value:
            return None
        path = pack_dir / str(path_value)
        if not path.exists():
            return None
        return cls._read_yaml(path)

    @classmethod
    def _draft_manifest(cls, payload: dict[str, Any]) -> dict[str, Any]:
        pack_id = cls._safe_pack_id(payload.get("pack_id") or payload.get("id") or payload.get("name"))
        return {
            "id": pack_id,
            "name": str(payload.get("name") or pack_id),
            "version": str(payload.get("version") or "0.1.0-draft"),
            "description": str(payload.get("description") or "Draft domain pack"),
            "schema": "schema.json",
            "extraction_prompt": "extraction_prompt.md",
            "retrieval_policy": "retrieval_policy.yaml",
            "answer_template": "answer_template.md",
            "report_template": "report_template.md",
            "eval_dataset": "eval_dataset.jsonl",
            "default_retrieval_profile": payload.get("default_retrieval_profile") or "auto",
            "default_eval_profile_id": payload.get("default_eval_profile_id"),
        }

    @classmethod
    def _write_pack_assets(cls, pack_dir: Path, payload: dict[str, Any], manifest: dict[str, Any]) -> None:
        pack_dir.mkdir(parents=True, exist_ok=True)
        schema_data = payload.get("schema_data") or payload.get("schema") or cls._default_schema()
        retrieval_policy = (
            payload.get("retrieval_policy_data")
            or payload.get("retrieval_policy")
            or cls._default_retrieval_policy()
        )
        extraction_prompt = str(
            payload.get("extraction_prompt_text")
            or payload.get("extraction_prompt")
            or "Extract entities, relations, and source evidence for this domain pack."
        )
        answer_template = str(
            payload.get("answer_template_text")
            or "{{conclusion}}\n\nEvidence:\n{{evidence}}\n\nRisks:\n{{risks}}\n\nCitations:\n{{citations}}\n"
        )
        report_template = str(
            payload.get("report_template_text")
            or "{{summary}}\n\nRisks:\n{{risks}}\n\nEvidence:\n{{evidence}}\n\nRecommendations:\n{{recommendations}}\n"
        )
        eval_dataset = str(payload.get("eval_dataset_text") or "")

        (pack_dir / manifest["schema"]).write_text(
            json.dumps(schema_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (pack_dir / manifest["extraction_prompt"]).write_text(extraction_prompt, encoding="utf-8")
        cls._write_yaml(pack_dir / manifest["retrieval_policy"], retrieval_policy)
        (pack_dir / manifest["answer_template"]).write_text(answer_template, encoding="utf-8")
        (pack_dir / manifest["report_template"]).write_text(report_template, encoding="utf-8")
        (pack_dir / manifest["eval_dataset"]).write_text(eval_dataset, encoding="utf-8")

    @classmethod
    def _summary_from_manifest(cls, pack_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
        return {
            "pack_id": manifest.get("id") or pack_dir.name,
            "name": manifest.get("name") or pack_dir.name,
            "version": manifest.get("version"),
            "description": manifest.get("description"),
            "status": cls._pack_status(pack_dir),
        }

    @classmethod
    async def list_domain_packs(cls) -> list[dict[str, Any]]:
        loader = DomainPackLoader()
        results: list[dict[str, Any]] = []
        for pack_dir in sorted(loader.packs_root.iterdir() if loader.packs_root.exists() else []):
            if not pack_dir.is_dir():
                continue
            try:
                pack = loader.load(pack_dir.name)
            except Exception:
                draft_manifest = cls._read_yaml(pack_dir / "draft.yaml")
                if draft_manifest:
                    results.append(cls._summary_from_manifest(pack_dir, draft_manifest))
                    continue
                results.append(
                    {
                        "pack_id": pack_dir.name,
                        "name": pack_dir.name,
                        "status": "draft",
                    }
                )
                continue

            results.append(
                {
                    "pack_id": pack.id,
                    "name": pack.name,
                    "version": pack.version,
                    "description": pack.description,
                    "status": cls._pack_status(pack_dir),
                }
            )
        return results

    @classmethod
    async def get_domain_pack(cls, pack_id: str) -> dict[str, Any]:
        pack_dir = cls._pack_dir(pack_id)
        manifest_path = pack_dir / "pack.yaml"
        draft_path = pack_dir / "draft.yaml"
        if manifest_path.exists():
            pack = DomainPackLoader().load(pack_dir.name)
            if pack is None:
                raise ValueError(f"domain pack not found: {pack_id}")
            payload = pack.to_dict()
            payload["pack_id"] = pack.id
            payload["status"] = "published"
            return payload
        if draft_path.exists():
            manifest = cls._read_yaml(draft_path)
            return {
                **cls._summary_from_manifest(pack_dir, manifest),
                "schema_data": json.loads((pack_dir / manifest["schema"]).read_text(encoding="utf-8")),
                "extraction_prompt_text": (pack_dir / manifest["extraction_prompt"]).read_text(encoding="utf-8"),
                "retrieval_policy_data": cls._read_yaml(pack_dir / manifest["retrieval_policy"]),
                "answer_template_text": (pack_dir / manifest["answer_template"]).read_text(encoding="utf-8"),
                "report_template_text": (pack_dir / manifest["report_template"]).read_text(encoding="utf-8"),
                "eval_dataset_text": (pack_dir / manifest["eval_dataset"]).read_text(encoding="utf-8"),
            }
        raise ValueError(f"domain pack not found: {pack_id}")

    @classmethod
    async def create_draft(cls, payload: dict[str, Any]) -> dict[str, Any]:
        manifest = cls._draft_manifest(payload)
        pack_dir = cls._pack_dir(str(manifest["id"]))
        cls._write_pack_assets(pack_dir, payload, manifest)
        cls._write_yaml(pack_dir / "draft.yaml", manifest)
        return cls._summary_from_manifest(pack_dir, manifest)

    @classmethod
    async def create_draft_from_knowledge(cls, payload: dict[str, Any]) -> dict[str, Any]:
        knowledge_id = str(payload.get("knowledge_id") or "").strip()
        if not knowledge_id:
            raise ValueError("knowledge_id is required")
        draft_payload = {
            **payload,
            "description": payload.get("description") or f"Draft generated from knowledge {knowledge_id}",
            "schema_data": payload.get("schema_data") or cls._default_schema(),
            "retrieval_policy_data": payload.get("retrieval_policy_data") or cls._default_retrieval_policy(),
        }
        result = await cls.create_draft(draft_payload)
        result["source_knowledge_id"] = knowledge_id
        result["representative_file_ids"] = list(payload.get("file_ids") or [])
        return result

    @classmethod
    async def update_domain_pack(cls, pack_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        pack_dir = cls._pack_dir(pack_id)
        current_manifest = cls._read_yaml(pack_dir / "draft.yaml") or cls._read_yaml(pack_dir / "pack.yaml")
        manifest = {
            **cls._draft_manifest({"pack_id": pack_dir.name}),
            **current_manifest,
            **{key: value for key, value in payload.items() if key in {"name", "version", "description", "default_retrieval_profile", "default_eval_profile_id"}},
            "id": pack_dir.name,
        }
        asset_payload = {
            "schema_data": cls._read_json_asset(pack_dir, current_manifest, "schema"),
            "retrieval_policy_data": cls._read_yaml_asset(pack_dir, current_manifest, "retrieval_policy"),
            "extraction_prompt_text": cls._read_text_asset(pack_dir, current_manifest, "extraction_prompt"),
            "answer_template_text": cls._read_text_asset(pack_dir, current_manifest, "answer_template"),
            "report_template_text": cls._read_text_asset(pack_dir, current_manifest, "report_template"),
            "eval_dataset_text": cls._read_text_asset(pack_dir, current_manifest, "eval_dataset"),
        }
        asset_payload.update({key: value for key, value in payload.items() if value is not None})
        cls._write_pack_assets(pack_dir, asset_payload, manifest)
        cls._write_yaml(pack_dir / "draft.yaml", manifest)
        return cls._summary_from_manifest(pack_dir, manifest)

    @classmethod
    async def publish_domain_pack(cls, pack_id: str) -> dict[str, Any]:
        pack_dir = cls._pack_dir(pack_id)
        draft_path = pack_dir / "draft.yaml"
        if draft_path.exists():
            cls._write_yaml(pack_dir / "pack.yaml", cls._read_yaml(draft_path))
        pack = DomainPackLoader().load(pack_dir.name)
        if pack is None:
            raise ValueError(f"domain pack not found: {pack_id}")
        return {
            "pack_id": pack.id,
            "status": "published",
            "version": pack.version,
            "name": pack.name,
        }


__all__ = ["DomainPackService"]
