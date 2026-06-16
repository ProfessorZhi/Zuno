from __future__ import annotations

import json
from pathlib import Path

from zuno.services.domain_pack.models import DomainPack


class DomainPackValidator:
    REQUIRED_FIELDS = {
        "id",
        "name",
        "version",
        "description",
        "schema",
        "extraction_prompt",
        "retrieval_policy",
    }
    REQUIRED_POLICY_FIELDS = {
        "graph_hop_limit",
        "max_paths_per_entity",
        "citation_strictness",
        "risk_relation_preference",
        "graph_seed_terms",
        "graph_relation_cues",
        "graph_step_cues",
    }
    REQUIRED_ANSWER_PLACEHOLDERS = {
        "{{conclusion}}",
        "{{evidence}}",
        "{{risks}}",
        "{{citations}}",
    }
    REQUIRED_REPORT_PLACEHOLDERS = {
        "{{summary}}",
        "{{risks}}",
        "{{evidence}}",
        "{{recommendations}}",
    }

    @classmethod
    def validate_payload(cls, payload: dict, *, expected_pack_id: str | None = None) -> None:
        missing = sorted(field for field in cls.REQUIRED_FIELDS if not payload.get(field))
        if missing:
            raise ValueError(f"domain pack missing required fields: {', '.join(missing)}")
        pack_id = str(payload.get("id") or "").strip()
        if expected_pack_id and pack_id != expected_pack_id:
            raise ValueError(
                f"domain pack id mismatch: expected `{expected_pack_id}` but manifest declares `{pack_id}`"
            )
        for field in cls.REQUIRED_FIELDS | {"answer_template", "report_template", "eval_dataset"}:
            if field not in payload or payload.get(field) is None:
                continue
            if not str(payload.get(field) or "").strip():
                raise ValueError(f"domain pack field `{field}` cannot be empty")

    @staticmethod
    def _resolve_pack_path(pack_dir: Path, relative_path: str | None, *, field_name: str) -> Path | None:
        if relative_path is None:
            return None
        candidate = (pack_dir / str(relative_path)).resolve()
        pack_root = pack_dir.resolve()
        if pack_root not in candidate.parents and candidate != pack_root:
            raise ValueError(f"domain pack field `{field_name}` points outside pack root: {relative_path}")
        return candidate

    @classmethod
    def resolve_asset_paths(cls, payload: dict, *, pack_dir: Path) -> dict[str, Path | None]:
        return {
            "schema": cls._resolve_pack_path(pack_dir, payload.get("schema"), field_name="schema"),
            "extraction_prompt": cls._resolve_pack_path(
                pack_dir,
                payload.get("extraction_prompt"),
                field_name="extraction_prompt",
            ),
            "retrieval_policy": cls._resolve_pack_path(
                pack_dir,
                payload.get("retrieval_policy"),
                field_name="retrieval_policy",
            ),
            "answer_template": cls._resolve_pack_path(
                pack_dir,
                payload.get("answer_template"),
                field_name="answer_template",
            ),
            "report_template": cls._resolve_pack_path(
                pack_dir,
                payload.get("report_template"),
                field_name="report_template",
            ),
            "eval_dataset": cls._resolve_pack_path(
                pack_dir,
                payload.get("eval_dataset"),
                field_name="eval_dataset",
            ),
        }

    @staticmethod
    def _ensure_file_exists(path: Path | None, *, field_name: str, required: bool) -> None:
        if path is None:
            if required:
                raise ValueError(f"domain pack missing required asset: {field_name}")
            return
        if not path.exists() or not path.is_file():
            raise ValueError(f"domain pack asset not found for `{field_name}`: {path.name}")

    @classmethod
    def validate_asset_paths(cls, asset_paths: dict[str, Path | None]) -> None:
        cls._ensure_file_exists(asset_paths.get("schema"), field_name="schema", required=True)
        cls._ensure_file_exists(
            asset_paths.get("extraction_prompt"),
            field_name="extraction_prompt",
            required=True,
        )
        cls._ensure_file_exists(
            asset_paths.get("retrieval_policy"),
            field_name="retrieval_policy",
            required=True,
        )
        cls._ensure_file_exists(
            asset_paths.get("answer_template"),
            field_name="answer_template",
            required=False,
        )
        cls._ensure_file_exists(
            asset_paths.get("report_template"),
            field_name="report_template",
            required=False,
        )
        cls._ensure_file_exists(
            asset_paths.get("eval_dataset"),
            field_name="eval_dataset",
            required=False,
        )

    @staticmethod
    def _validate_string_list(values: object, *, field_name: str) -> list[str]:
        if not isinstance(values, list) or not values:
            raise ValueError(f"domain pack `{field_name}` must be a non-empty list")
        cleaned = []
        for item in values:
            text = str(item or "").strip()
            if not text:
                raise ValueError(f"domain pack `{field_name}` cannot contain empty values")
            cleaned.append(text)
        return cleaned

    @classmethod
    def validate_schema_data(cls, schema_data: dict | None) -> None:
        if not isinstance(schema_data, dict):
            raise ValueError("domain pack schema must be a JSON object")
        cls._validate_string_list(schema_data.get("entities"), field_name="schema.entities")
        cls._validate_string_list(schema_data.get("relations"), field_name="schema.relations")

    @classmethod
    def _normalize_string_list_field(cls, value: object, *, field_name: str) -> list[str]:
        if isinstance(value, str):
            normalized = [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
            if "|" in value:
                normalized = [item.strip() for item in value.split("|") if item.strip()]
            if normalized:
                return normalized
        return cls._validate_string_list(value, field_name=field_name)

    @classmethod
    def validate_retrieval_policy_data(cls, policy: dict | None) -> None:
        if not isinstance(policy, dict):
            raise ValueError("domain pack retrieval policy must be a YAML object")
        missing = sorted(field for field in cls.REQUIRED_POLICY_FIELDS if field not in policy)
        if missing:
            raise ValueError(f"domain pack retrieval policy missing fields: {', '.join(missing)}")
        for numeric_key in ("graph_hop_limit", "max_paths_per_entity"):
            value = policy.get(numeric_key)
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"domain pack retrieval policy `{numeric_key}` must be a positive integer")
        citation_strictness = str(policy.get("citation_strictness") or "").strip().lower()
        if citation_strictness not in {"low", "medium", "high"}:
            raise ValueError("domain pack retrieval policy `citation_strictness` must be low, medium, or high")
        risk_relation = str(policy.get("risk_relation_preference") or "").strip()
        if not risk_relation:
            raise ValueError("domain pack retrieval policy `risk_relation_preference` cannot be empty")
        cls._normalize_string_list_field(policy.get("graph_seed_terms"), field_name="graph_seed_terms")
        cls._normalize_string_list_field(policy.get("graph_relation_cues"), field_name="graph_relation_cues")
        cls._normalize_string_list_field(policy.get("graph_step_cues"), field_name="graph_step_cues")

    @staticmethod
    def _looks_encoding_damaged(value: str | None) -> bool:
        if not value:
            return False
        text = str(value)
        question_count = text.count("?")
        non_space_count = sum(1 for char in text if not char.isspace())
        return non_space_count > 0 and (question_count / non_space_count >= 0.25 or "???" in text)

    @classmethod
    def validate_text_asset(cls, field_name: str, text: str | None) -> None:
        normalized = str(text or "").strip()
        if not normalized:
            raise ValueError(f"domain pack text asset `{field_name}` cannot be empty")
        if cls._looks_encoding_damaged(normalized):
            raise ValueError(f"domain pack text asset `{field_name}` appears encoding-damaged")

    @classmethod
    def validate_template_text(cls, field_name: str, text: str | None) -> None:
        cls.validate_text_asset(field_name, text)
        placeholders = (
            cls.REQUIRED_ANSWER_PLACEHOLDERS
            if field_name == "answer_template"
            else cls.REQUIRED_REPORT_PLACEHOLDERS
        )
        if "{{" not in str(text):
            raise ValueError(
                f"domain pack template `{field_name}` must declare placeholders: {', '.join(sorted(placeholders))}"
            )
        missing = sorted(token for token in placeholders if token not in str(text))
        if missing:
            raise ValueError(
                f"domain pack template `{field_name}` missing placeholders: {', '.join(missing)}"
            )

    @classmethod
    def validate_eval_dataset_text(cls, text: str | None) -> None:
        cls.validate_text_asset("eval_dataset", text)
        rows = [line.strip() for line in str(text or "").splitlines() if line.strip()]
        if not rows:
            raise ValueError("domain pack eval dataset must contain at least one JSONL row")
        for index, row in enumerate(rows, start=1):
            try:
                payload = json.loads(row)
            except json.JSONDecodeError as err:
                raise ValueError(f"domain pack eval dataset row {index} is not valid JSON: {err.msg}") from err
            required_fields = {"id", "query", "reference_answer", "gold_evidence", "required_citations"}
            missing = sorted(field for field in required_fields if field not in payload)
            if missing:
                raise ValueError(
                    f"domain pack eval dataset row {index} missing fields: {', '.join(missing)}"
                )

    @classmethod
    def validate_loaded_pack(cls, pack: DomainPack) -> None:
        cls.validate_payload(pack.to_dict(), expected_pack_id=pack.id)
        cls.validate_schema_data(pack.schema_data)
        cls.validate_retrieval_policy_data(pack.retrieval_policy_data)
        cls.validate_text_asset("extraction_prompt", pack.extraction_prompt_text)
        if pack.answer_template_path:
            cls.validate_template_text("answer_template", pack.answer_template_text)
        if pack.report_template_path:
            cls.validate_template_text("report_template", pack.report_template_text)
        if pack.eval_dataset_path:
            cls.validate_eval_dataset_text(pack.eval_dataset_text)

    @classmethod
    def validate_pack(cls, pack: DomainPack) -> None:
        cls.validate_loaded_pack(pack)


__all__ = ["DomainPackValidator"]
