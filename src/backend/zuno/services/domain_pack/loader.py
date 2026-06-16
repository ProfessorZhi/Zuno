from __future__ import annotations

import json
from pathlib import Path

import yaml

from zuno.services.domain_pack.models import DomainPack
from zuno.services.domain_pack.validators import DomainPackValidator


def _find_repo_root(package_root: Path) -> Path:
    for parent in package_root.parents:
        if (parent / "docs" / "architecture").exists() and (parent / "README.md").exists():
            return parent
    return package_root.parents[-1]


class DomainPackLoader:
    def __init__(self, packs_root: Path | None = None):
        repo_root = _find_repo_root(Path(__file__).resolve())
        self.packs_root = packs_root or repo_root / "domain-packs"

    @staticmethod
    def _parse_yaml(text: str, *, field_name: str) -> dict:
        payload = yaml.safe_load(text) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"domain pack {field_name} must be a YAML object")
        return payload

    @classmethod
    def _read_text(cls, path: Path | None) -> str | None:
        if path is None or not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def load(self, pack_id: str | None) -> DomainPack | None:
        normalized = str(pack_id or "").strip()
        if not normalized:
            return None
        pack_dir = self.packs_root / normalized
        pack_file = pack_dir / "pack.yaml"
        if not pack_file.exists():
            raise ValueError(f"domain pack not found: {normalized}")
        payload = self._parse_yaml(pack_file.read_text(encoding="utf-8"), field_name="pack.yaml")
        DomainPackValidator.validate_payload(payload, expected_pack_id=normalized)
        asset_paths = DomainPackValidator.resolve_asset_paths(payload, pack_dir=pack_dir)
        DomainPackValidator.validate_asset_paths(asset_paths)

        schema_path = asset_paths["schema"]
        extraction_prompt_path = asset_paths["extraction_prompt"]
        retrieval_policy_path = asset_paths["retrieval_policy"]
        answer_template_path = asset_paths["answer_template"]
        report_template_path = asset_paths["report_template"]
        eval_dataset_path = asset_paths["eval_dataset"]

        schema_data = json.loads(schema_path.read_text(encoding="utf-8")) if schema_path else None
        retrieval_policy_data = (
            self._parse_yaml(retrieval_policy_path.read_text(encoding="utf-8"), field_name="retrieval_policy.yaml")
            if retrieval_policy_path
            else {}
        )

        pack = DomainPack(
            base_path=str(pack_dir),
            schema_path=str(schema_path) if schema_path else None,
            extraction_prompt_path=str(extraction_prompt_path) if extraction_prompt_path else None,
            retrieval_policy_path=str(retrieval_policy_path) if retrieval_policy_path else None,
            answer_template_path=str(answer_template_path) if answer_template_path else None,
            report_template_path=str(report_template_path) if report_template_path else None,
            eval_dataset_path=str(eval_dataset_path) if eval_dataset_path else None,
            schema_data=schema_data,
            extraction_prompt_text=self._read_text(extraction_prompt_path),
            retrieval_policy_data=retrieval_policy_data,
            answer_template_text=self._read_text(answer_template_path),
            report_template_text=self._read_text(report_template_path),
            eval_dataset_text=self._read_text(eval_dataset_path),
            **payload,
        )
        DomainPackValidator.validate_loaded_pack(pack)
        return pack


def load_domain_pack(pack_id: str | None, packs_root: Path | None = None) -> DomainPack | None:
    return DomainPackLoader(packs_root=packs_root).load(pack_id)


__all__ = ["DomainPackLoader", "load_domain_pack"]
