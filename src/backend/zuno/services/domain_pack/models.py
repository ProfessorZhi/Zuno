from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class DomainPack:
    id: str
    name: str
    version: str
    description: str
    schema: str
    extraction_prompt: str
    retrieval_policy: str
    answer_template: str | None = None
    report_template: str | None = None
    eval_dataset: str | None = None
    base_path: str | None = None
    schema_path: str | None = None
    extraction_prompt_path: str | None = None
    retrieval_policy_path: str | None = None
    answer_template_path: str | None = None
    report_template_path: str | None = None
    eval_dataset_path: str | None = None
    schema_data: dict | None = None
    extraction_prompt_text: str | None = None
    retrieval_policy_data: dict | None = None
    answer_template_text: str | None = None
    report_template_text: str | None = None
    eval_dataset_text: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


__all__ = ["DomainPack"]
