import asyncio
import importlib
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    runtime_root = str(BACKEND_ROOT)
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def _write_pack(root: Path, pack_id: str, *, answer_template: str = "answer_template.md") -> Path:
    pack_dir = root / pack_id
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "pack.yaml").write_text(
        "\n".join(
            [
                f"id: {pack_id}",
                "name: Test Pack",
                "version: 0.1.0",
                "description: test pack",
                "schema: schema.json",
                "extraction_prompt: extraction_prompt.md",
                "retrieval_policy: retrieval_policy.yaml",
                f"answer_template: {answer_template}",
                "report_template: report_template.md",
                "eval_dataset: eval_dataset.jsonl",
            ]
        ),
        encoding="utf-8",
    )
    (pack_dir / "schema.json").write_text(
        json.dumps({"entities": ["Contract"], "relations": ["CLAUSE_HAS_RISK"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (pack_dir / "extraction_prompt.md").write_text("Extract evidence.", encoding="utf-8")
    (pack_dir / "retrieval_policy.yaml").write_text(
        "\n".join(
            [
                "graph_hop_limit: 2",
                "max_paths_per_entity: 5",
                "citation_strictness: high",
                "risk_relation_preference: CLAUSE_HAS_RISK",
                "graph_seed_terms:",
                "  - 风险",
                "graph_relation_cues:",
                "  - 条款",
                "graph_step_cues:",
                "  - 步骤",
            ]
        ),
        encoding="utf-8",
    )
    (pack_dir / "answer_template.md").write_text(
        "## 结论\n{{conclusion}}\n\n## 条款依据\n{{evidence}}\n\n## 风险点\n{{risks}}\n\n## 引用\n{{citations}}\n",
        encoding="utf-8",
    )
    (pack_dir / "report_template.md").write_text(
        "## 审查结论\n{{summary}}\n\n## 风险列表\n{{risks}}\n\n## 条款依据\n{{evidence}}\n\n## 修改建议\n{{recommendations}}\n",
        encoding="utf-8",
    )
    (pack_dir / "eval_dataset.jsonl").write_text(
        json.dumps(
            {
                "id": "q1",
                "query": "是否有风险",
                "reference_answer": "有风险",
                "gold_evidence": [{"document": "doc.md", "text_contains": "风险"}],
                "required_citations": True,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return pack_dir


def test_contract_review_pack_loads_as_formal_domain_pack():
    _ensure_runtime_paths()

    DomainPackLoader = importlib.import_module("zuno.services.domain_pack.loader").DomainPackLoader

    pack = DomainPackLoader().load("contract_review")

    assert pack is not None
    assert pack.id == "contract_review"
    assert pack.retrieval_policy_data["graph_hop_limit"] == 2
    assert isinstance(pack.retrieval_policy_data["graph_seed_terms"], list)
    assert "{{conclusion}}" in (pack.answer_template_text or "")
    assert "{{recommendations}}" in (pack.report_template_text or "")
    assert "这份合同是否约定了违约责任？" in (pack.eval_dataset_text or "")


def test_domain_pack_loader_rejects_missing_required_fields(tmp_path):
    _ensure_runtime_paths()

    DomainPackLoader = importlib.import_module("zuno.services.domain_pack.loader").DomainPackLoader

    pack_dir = tmp_path / "broken"
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "pack.yaml").write_text(
        "\n".join(
            [
                "id: broken",
                "name: Broken Pack",
                "version: 0.1.0",
                "description: missing schema",
                "extraction_prompt: extraction_prompt.md",
                "retrieval_policy: retrieval_policy.yaml",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required fields"):
        DomainPackLoader(packs_root=tmp_path).load("broken")


def test_domain_pack_loader_rejects_illegal_template_reference(tmp_path):
    _ensure_runtime_paths()

    DomainPackLoader = importlib.import_module("zuno.services.domain_pack.loader").DomainPackLoader

    _write_pack(tmp_path, "bad_template", answer_template="../escape.md")

    with pytest.raises(ValueError, match="outside pack root"):
        DomainPackLoader(packs_root=tmp_path).load("bad_template")


def test_domain_pack_loader_rejects_invalid_policy(tmp_path):
    _ensure_runtime_paths()

    DomainPackLoader = importlib.import_module("zuno.services.domain_pack.loader").DomainPackLoader

    pack_dir = _write_pack(tmp_path, "bad_policy")
    (pack_dir / "retrieval_policy.yaml").write_text(
        "\n".join(
            [
                "graph_hop_limit: wrong",
                "max_paths_per_entity: 5",
                "citation_strictness: high",
                "risk_relation_preference: CLAUSE_HAS_RISK",
                "graph_seed_terms:",
                "  - 风险",
                "graph_relation_cues:",
                "  - 条款",
                "graph_step_cues:",
                "  - 步骤",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="graph_hop_limit"):
        DomainPackLoader(packs_root=tmp_path).load("bad_policy")


def test_graph_retriever_adapter_merges_runtime_domain_pack_policy(monkeypatch):
    _ensure_runtime_paths()

    GraphRetrieverAdapter = importlib.import_module(
        "zuno.services.retrieval.retrievers"
    ).GraphRetrieverAdapter

    captured = {}

    async def fake_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": "contract_review",
            "domain_pack": {
                "id": "contract_review",
                "retrieval_policy_data": {
                    "graph_hop_limit": 2,
                    "max_paths_per_entity": 5,
                    "citation_strictness": "high",
                    "risk_relation_preference": "CLAUSE_HAS_RISK",
                    "graph_seed_terms": ["违约责任"],
                    "graph_relation_cues": ["条款"],
                    "graph_step_cues": ["步骤"],
                },
            },
        }

    class FakeRetriever:
        async def retrieve(self, query, knowledge_id, **kwargs):
            captured["knowledge_id"] = knowledge_id
            captured["kwargs"] = kwargs
            return {"content": "", "documents": [], "domain_pack_id": kwargs.get("domain_pack_id")}

    monkeypatch.setattr(
        "zuno.services.retrieval.retrievers.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )

    result = asyncio.run(
        GraphRetrieverAdapter(retriever=FakeRetriever()).retrieve(
            "这份合同是否约定了违约责任？",
            ["kb_1"],
            {"graph_hop_limit": 3},
        )
    )

    assert captured["knowledge_id"] == "kb_1"
    assert captured["kwargs"]["domain_pack_id"] == "contract_review"
    assert captured["kwargs"]["query_policy"]["graph_relation_cues"] == ["条款"]
    assert captured["kwargs"]["query_policy"]["graph_hop_limit"] == 3
    assert result["domain_pack_id"] == "contract_review"


def test_knowledge_service_local_runtime_loads_domain_pack_from_domain_pack_id(monkeypatch):
    _ensure_runtime_paths()

    KnowledgeService = importlib.import_module("zuno.api.services.knowledge").KnowledgeService

    monkeypatch.setattr(
        "zuno.api.services.knowledge.get_local_runtime_settings",
        lambda _knowledge_id: {
            "knowledge_config": {"domain_pack_id": "contract_review"},
            "domain_pack_id": "contract_review",
        },
    )

    runtime = asyncio.run(KnowledgeService.get_runtime_settings("kb_1"))

    assert runtime["domain_pack_id"] == "contract_review"
    assert runtime["domain_pack"]["id"] == "contract_review"
    assert runtime["domain_pack"]["retrieval_policy_data"]["citation_strictness"] == "high"


def test_domain_qa_graph_renders_template_boundary_without_contract_hardcode():
    _ensure_runtime_paths()

    DomainPackLoader = importlib.import_module("zuno.services.domain_pack.loader").DomainPackLoader
    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph

    pack = DomainPackLoader().load("contract_review")
    answer, report = DomainQAGraph._build_answer_markdown(
        {
            "domain_pack": pack.to_dict(),
            "vector_contexts": [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "contract.md",
                    "content": "乙方违约时应承担违约责任。",
                }
            ],
            "graph_paths": [{"source": "第八条 违约责任", "target": "违约责任"}],
            "graph_path_strings": ["第八条 违约责任 -> 违约责任"],
            "citations": [{"file_name": "contract.md", "chunk_id": "chunk_1", "knowledge_id": "kb_1"}],
        }
    )

    assert "# 合同审查回答" in answer
    assert "# 合同审查报告" in report
    assert "{{conclusion}}" not in answer
    assert "{{summary}}" not in report
    assert "# Contract Review Report" not in report
