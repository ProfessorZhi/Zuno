from __future__ import annotations

import re
from pathlib import Path

from zuno.services.graphrag.extractor import GraphExtractor


class StructuredGraphExtractor(GraphExtractor):
    FILE_NAME_TITLE_HINTS = {
        "master_service_agreement": "主服务合同",
        "saas_subscription": "SaaS订阅服务合同",
        "loan_agreement": "借款合同",
        "commercial_lease": "商业房屋租赁合同",
        "procurement_framework": "采购框架协议",
        "data_processing_addendum": "数据处理附录",
        "distribution_agreement": "区域经销协议",
        "outsourcing_service_agreement": "外包运维服务合同",
    }
    CLAUSE_HEADING_PATTERN = re.compile(r"^\s*第(?P<index>[一二三四五六七八九十百千万0-9]+)条[：:\s]*(?P<title>[^\n]*)")
    PARTY_PATTERN = re.compile(
        r"(?P<label>甲方|乙方|丙方)(?:（[^）]+）)?[：:]\s*(?P<name>[^\n，。、；;（）()]{2,60})"
    )
    REGULATION_PATTERN = re.compile(r"《[^》]{2,40}》")
    TERM_PATTERN = re.compile(
        r"(?:不少于|不迟于|提前|自[^，。；;\n]{0,20})?\d+(?:小时|个工作日|个自然日|个交易日|日|天|个月|年)"
    )
    AMOUNT_PATTERN = re.compile(r"人民币\s*[0-9一二三四五六七八九十百千万.,]+(?:元|万元)")
    RISK_CUE_MAP = {
        "违约责任": "违约责任",
        "提前到期": "提前到期风险",
        "单方解除": "单方解除风险",
        "逾期": "逾期履约风险",
        "泄露": "数据泄露风险",
        "侵权": "知识产权侵权风险",
        "恢复原状": "恢复原状风险",
        "赔偿": "赔偿责任风险",
    }
    OBLIGATION_CUE_MAP = {
        "保密": "保密义务",
        "支付": "付款义务",
        "付款": "付款义务",
        "交付": "交付义务",
        "提供服务": "服务提供义务",
        "配合": "配合义务",
        "通知": "通知义务",
        "返还": "返还义务",
        "删除": "删除义务",
        "销毁": "删除义务",
        "审计": "审计配合义务",
        "修复": "修复义务",
        "赔偿": "赔偿义务",
    }

    @classmethod
    def _chunk_dict(cls, chunk: dict) -> dict:
        return chunk.to_dict() if hasattr(chunk, "to_dict") else dict(chunk)

    @staticmethod
    def _normalize_text(value: str) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip()

    @classmethod
    def _build_contract_name(cls, chunk_payload: dict, content: str) -> str:
        for line in str(content or "").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                title = stripped.lstrip("#").strip()
                if title:
                    return title
        file_name = str(chunk_payload.get("file_name") or "").strip()
        if file_name:
            lowered_stem = Path(file_name).stem.lower()
            for hint, title in cls.FILE_NAME_TITLE_HINTS.items():
                if hint in lowered_stem:
                    return title
            return Path(file_name).stem.replace("_", " ")
        return "Contract"

    @classmethod
    def _find_clause_sections(cls, content: str) -> list[dict[str, str]]:
        lines = str(content or "").splitlines()
        sections: list[dict[str, str]] = []
        current_heading: str | None = None
        current_title: str | None = None
        buffer: list[str] = []

        def split_title_and_inline_body(raw_title: str) -> tuple[str, str]:
            normalized = cls._normalize_text(raw_title)
            if not normalized:
                return "未命名条款", ""
            for delimiter in ("：", ":"):
                if delimiter not in normalized:
                    continue
                title_part, inline_body = normalized.split(delimiter, 1)
                title_part = cls._normalize_text(title_part)
                inline_body = cls._normalize_text(inline_body)
                if title_part and inline_body:
                    return title_part, inline_body
            return normalized, ""

        def flush() -> None:
            nonlocal current_heading, current_title, buffer
            if current_heading and buffer:
                body = "\n".join(buffer).strip()
                if body:
                    sections.append(
                        {
                            "clause_name": current_heading,
                            "title": current_title or "",
                            "content": body,
                        }
                    )
            current_heading = None
            current_title = None
            buffer = []

        for raw_line in lines:
            stripped = raw_line.strip()
            match = cls.CLAUSE_HEADING_PATTERN.match(stripped)
            if match:
                flush()
                title, inline_body = split_title_and_inline_body(match.group("title"))
                current_title = title
                current_heading = f"第{match.group('index')}条 {title}"
                if inline_body:
                    buffer.append(inline_body)
                continue
            if current_heading:
                buffer.append(raw_line)
        flush()
        return sections

    @classmethod
    def _extract_parties(cls, content: str) -> list[dict[str, str]]:
        parties: list[dict[str, str]] = []
        seen: set[str] = set()
        for match in cls.PARTY_PATTERN.finditer(str(content or "")):
            label = cls._normalize_text(match.group("label"))
            name = cls._normalize_text(match.group("name")).rstrip("。；;）)")
            if not label or not name:
                continue
            key = f"{label}:{name}"
            if key in seen:
                continue
            seen.add(key)
            parties.append({"label": label, "name": name})
        return parties

    @classmethod
    def _extract_obligations(cls, content: str) -> list[str]:
        obligations: list[str] = []
        lowered = str(content or "")
        for cue, label in cls.OBLIGATION_CUE_MAP.items():
            if cue in lowered and label not in obligations:
                obligations.append(label)
        return obligations

    @classmethod
    def _extract_risks(cls, content: str) -> list[str]:
        risks: list[str] = []
        lowered = str(content or "")
        for cue, label in cls.RISK_CUE_MAP.items():
            if cue in lowered and label not in risks:
                risks.append(label)
        return risks

    @classmethod
    def _extract_regulations(cls, content: str) -> list[str]:
        return sorted({match.group(0) for match in cls.REGULATION_PATTERN.finditer(str(content or ""))})

    @classmethod
    def _extract_terms(cls, content: str) -> list[str]:
        terms = []
        for match in cls.TERM_PATTERN.finditer(str(content or "")):
            value = cls._normalize_text(match.group(0))
            if value and value not in terms:
                terms.append(value)
        return terms

    @classmethod
    def _extract_amounts(cls, content: str) -> list[str]:
        amounts = []
        for match in cls.AMOUNT_PATTERN.finditer(str(content or "")):
            value = cls._normalize_text(match.group(0))
            if value and value not in amounts:
                amounts.append(value)
        return amounts

    @classmethod
    def _append_project_id(cls, items: list[dict], project_payload: dict | None) -> None:
        if not project_payload:
            return
        project_id = str(
            project_payload.get("graphrag_project_id") or project_payload.get("id") or ""
        ).strip()
        if not project_id:
            return
        for item in items:
            item.setdefault("domain_pack_id", project_id)

    async def extract_from_chunk(
        self,
        chunk: dict,
        knowledge_id: str,
        *,
        project_payload: dict | None = None,
        domain_pack: dict | None = None,
    ) -> dict:
        project_payload = project_payload or domain_pack
        chunk_payload = self._chunk_dict(chunk)
        result = await super().extract_from_chunk(chunk_payload, knowledge_id)
        content = str(chunk_payload.get("content") or "")
        chunk_id = str(chunk_payload.get("chunk_id") or "")
        contract_name = self._build_contract_name(chunk_payload, content)

        schema_entities = set((project_payload or {}).get("schema_data", {}).get("entities") or [])
        schema_relations = set((project_payload or {}).get("schema_data", {}).get("relations") or [])

        def add_entity(name: str, entity_type: str, evidence: str, confidence: float, metadata: dict | None = None) -> None:
            if entity_type not in schema_entities or not name:
                return
            result.setdefault("entities", []).append(
                {
                    "name": name,
                    "type": entity_type,
                    "knowledge_id": knowledge_id,
                    "chunk_id": chunk_id,
                    "evidence": evidence[:240],
                    "confidence": confidence,
                    "metadata": metadata or {},
                }
            )

        def add_relation(source: str, target: str, relation_type: str, evidence: str, confidence: float) -> None:
            if relation_type not in schema_relations or not source or not target:
                return
            result.setdefault("relations", []).append(
                {
                    "source": source,
                    "target": target,
                    "relation_type": relation_type,
                    "knowledge_id": knowledge_id,
                    "chunk_id": chunk_id,
                    "evidence": evidence[:240],
                    "confidence": confidence,
                }
            )

        add_entity(contract_name, "Contract", content, 0.96)

        for party in self._extract_parties(content):
            add_entity(party["name"], "Party", content, 0.92, metadata={"label": party["label"]})
            add_relation(party["name"], contract_name, "PARTY_SIGNS_CONTRACT", content, 0.91)

        for clause in self._find_clause_sections(content):
            clause_name = clause["clause_name"]
            clause_content = clause["content"]
            clause_evidence = f"{clause_name} {clause_content}".strip()
            add_entity(clause_name, "Clause", clause_evidence, 0.95, metadata={"title": clause["title"]})
            add_relation(contract_name, clause_name, "CONTRACT_HAS_CLAUSE", clause_evidence, 0.94)

            for obligation in self._extract_obligations(clause_content):
                add_entity(obligation, "Obligation", clause_evidence, 0.88)
                add_relation(clause_name, obligation, "CLAUSE_HAS_OBLIGATION", clause_evidence, 0.9)

            for risk in self._extract_risks(clause_content):
                add_entity(risk, "Risk", clause_evidence, 0.9)
                add_relation(clause_name, risk, "CLAUSE_HAS_RISK", clause_evidence, 0.91)

            for regulation in self._extract_regulations(clause_content):
                add_entity(regulation, "Regulation", clause_evidence, 0.87)
                add_relation(clause_name, regulation, "CLAUSE_REFERENCES_REGULATION", clause_evidence, 0.89)

            for term in self._extract_terms(clause_content):
                add_entity(term, "Term", clause_evidence, 0.84)

            for amount in self._extract_amounts(clause_content):
                add_entity(amount, "Amount", clause_evidence, 0.84)

        seen_entities: set[tuple[str, str]] = set()
        deduped_entities: list[dict] = []
        for entity in result.get("entities", []):
            key = (str(entity.get("name") or ""), str(entity.get("type") or "entity"))
            if not key[0] or key in seen_entities:
                continue
            seen_entities.add(key)
            deduped_entities.append(entity)
        result["entities"] = deduped_entities

        seen_relations: set[tuple[str, str, str]] = set()
        deduped_relations: list[dict] = []
        for relation in result.get("relations", []):
            key = (
                str(relation.get("source") or ""),
                str(relation.get("target") or ""),
                str(relation.get("relation_type") or "related_to"),
            )
            if not key[0] or not key[1] or key in seen_relations:
                continue
            seen_relations.add(key)
            deduped_relations.append(relation)
        result["relations"] = deduped_relations

        self._append_project_id(result.get("entities", []), project_payload)
        self._append_project_id(result.get("relations", []), project_payload)
        return result


__all__ = ["StructuredGraphExtractor"]
