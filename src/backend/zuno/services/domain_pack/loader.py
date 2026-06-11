from __future__ import annotations

import json
from pathlib import Path

from zuno.services.domain_pack.models import DomainPack
from zuno.services.domain_pack.validators import DomainPackValidator


class DomainPackLoader:
    def __init__(self, packs_root: Path | None = None):
        self.packs_root = packs_root or Path(__file__).resolve().parents[2] / "domain_packs"

    @staticmethod
    def _parse_simple_yaml(text: str) -> dict[str, str]:
        payload: dict[str, object] = {}
        for raw_line in str(text or "").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            normalized = value.strip().strip("'\"")
            lowered = normalized.lower()
            if lowered in {"true", "false"}:
                payload[key.strip()] = lowered == "true"
                continue
            try:
                payload[key.strip()] = int(normalized)
                continue
            except ValueError:
                pass
            try:
                payload[key.strip()] = float(normalized)
                continue
            except ValueError:
                pass
            payload[key.strip()] = normalized
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
        payload = self._parse_simple_yaml(pack_file.read_text(encoding="utf-8"))
        DomainPackValidator.validate_payload(payload)
        schema_path = pack_dir / str(payload["schema"])
        extraction_prompt_path = pack_dir / str(payload["extraction_prompt"])
        retrieval_policy_path = pack_dir / str(payload["retrieval_policy"])
        answer_template_name = payload.get("answer_template")
        report_template_name = payload.get("report_template")
        eval_dataset_name = payload.get("eval_dataset")
        answer_template_path = pack_dir / str(answer_template_name) if answer_template_name else None
        report_template_path = pack_dir / str(report_template_name) if report_template_name else None
        eval_dataset_path = pack_dir / str(eval_dataset_name) if eval_dataset_name else None

        schema_data = json.loads(schema_path.read_text(encoding="utf-8")) if schema_path.exists() else None
        retrieval_policy_data = (
            self._parse_simple_yaml(retrieval_policy_path.read_text(encoding="utf-8"))
            if retrieval_policy_path.exists()
            else {}
        )

        return DomainPack(
            base_path=str(pack_dir),
            schema_path=str(schema_path),
            extraction_prompt_path=str(extraction_prompt_path),
            retrieval_policy_path=str(retrieval_policy_path),
            answer_template_path=str(answer_template_path) if answer_template_path else None,
            report_template_path=str(report_template_path) if report_template_path else None,
            eval_dataset_path=str(eval_dataset_path) if eval_dataset_path else None,
            schema_data=schema_data,
            extraction_prompt_text=self._read_text(extraction_prompt_path),
            retrieval_policy_data=retrieval_policy_data,
            answer_template_text=self._read_text(answer_template_path),
            report_template_text=self._read_text(report_template_path),
            **payload,
        )


__all__ = ["DomainPackLoader"]
