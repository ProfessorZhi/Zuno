import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api" / "src"))

from tools.evals.zuno.rag_eval.paths import default_runs_root


def test_is_probably_local_base_url():
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import is_probably_local_base_url

    assert is_probably_local_base_url("http://127.0.0.1:8000/v1") is True
    assert is_probably_local_base_url("http://host.docker.internal:11434/v1") is True
    assert is_probably_local_base_url("https://api.openai.com/v1") is False


def test_infer_provider_from_base_url():
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import infer_provider_from_base_url

    assert infer_provider_from_base_url("http://127.0.0.1:11434/v1") == "openai-compatible-local"
    assert infer_provider_from_base_url("https://dashscope.aliyuncs.com/compatible-mode/v1") == "dashscope"


def test_validate_model_id_accepts_matching_embedding(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import validate_model_id

    async def fake_get_llm_by_id(llm_id):
        return {"llm_id": llm_id, "llm_type": "Embedding", "base_url": "http://127.0.0.1:11434/v1"}

    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMService.get_llm_by_id", fake_get_llm_by_id)
    payload = asyncio.run(validate_model_id("llm_embed_1", "Embedding"))
    assert payload["llm_id"] == "llm_embed_1"


def test_validate_model_id_rejects_wrong_type(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import validate_model_id

    async def fake_get_llm_by_id(llm_id):
        return {"llm_id": llm_id, "llm_type": "LLM"}

    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMService.get_llm_by_id", fake_get_llm_by_id)

    try:
        asyncio.run(validate_model_id("llm_embed_1", "Embedding"))
    except ValueError as exc:
        assert "must be Embedding" in str(exc)
    else:
        raise AssertionError("expected validate_model_id to reject wrong type")


def test_probe_embedding_model_returns_dimension(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import probe_embedding_model

    async def fake_get_embedding(text, config_override=None):
        return [0.1, 0.2, 0.3, 0.4]

    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.get_embedding", fake_get_embedding)
    result = asyncio.run(probe_embedding_model({"llm_id": "embed_1", "model": "bge-local"}))
    assert result["dimension"] == 4
    assert result["llm_id"] == "embed_1"


def test_preflight_local_embedding_eval_includes_probe(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import preflight_local_embedding_eval

    async def fake_get_llm_by_id(llm_id):
        return {
            "llm_id": llm_id,
            "llm_type": "Embedding",
            "model": "bge-local",
            "base_url": "http://127.0.0.1:11434/v1",
        }

    async def fake_get_embedding(text, config_override=None):
        return [1.0, 2.0, 3.0]

    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMService.get_llm_by_id", fake_get_llm_by_id)
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.get_embedding", fake_get_embedding)
    payload = asyncio.run(
        preflight_local_embedding_eval(
            text_embedding_model_id="embed_1",
            probe_embedding=True,
        )
    )
    assert payload["embedding_probe"]["dimension"] == 3
    assert payload["resolved_text_embedding_model_id"] == "embed_1"


def test_resolve_embedding_model_id_auto_picks_local_candidate(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import resolve_embedding_model_id

    async def fake_list_llm_candidates(*, expected_type=None, local_only=False):
        assert expected_type == "Embedding"
        return [
            {
                "llm_id": "embed_remote",
                "model": "text-embedding-v4",
                "llm_type": "Embedding",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model_slot": None,
                "is_local": False,
            },
            {
                "llm_id": "embed_local_slot",
                "model": "bge-m3",
                "llm_type": "Embedding",
                "base_url": "http://127.0.0.1:11434/v1",
                "model_slot": "embedding",
                "is_local": True,
            },
        ]

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_local_embedding_eval.list_llm_candidates",
        fake_list_llm_candidates,
    )
    resolved_id, candidates = asyncio.run(
        resolve_embedding_model_id(
            None,
            auto_pick_local_embedding=True,
        )
    )
    assert resolved_id == "embed_local_slot"
    assert len(candidates) == 2


def test_preflight_auto_pick_local_embedding(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import preflight_local_embedding_eval

    async def fake_resolve_embedding_model_id(text_embedding_model_id, *, auto_pick_local_embedding=False):
        assert text_embedding_model_id is None
        assert auto_pick_local_embedding is True
        return (
            "embed_local_1",
            [{"llm_id": "embed_local_1", "llm_type": "Embedding", "is_local": True}],
        )

    async def fake_get_llm_by_id(llm_id):
        return {
            "llm_id": llm_id,
            "llm_type": "Embedding",
            "model": "bge-local",
            "base_url": "http://127.0.0.1:11434/v1",
        }

    async def fake_get_embedding(text, config_override=None):
        return [1.0, 2.0]

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_local_embedding_eval.resolve_embedding_model_id",
        fake_resolve_embedding_model_id,
    )
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMService.get_llm_by_id", fake_get_llm_by_id)
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.get_embedding", fake_get_embedding)

    payload = asyncio.run(
        preflight_local_embedding_eval(
            text_embedding_model_id=None,
            auto_pick_local_embedding=True,
        )
    )
    assert payload["resolved_text_embedding_model_id"] == "embed_local_1"
    assert payload["embedding_probe"]["dimension"] == 2


def test_preflight_can_use_active_config_embedding(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import preflight_local_embedding_eval

    async def fake_resolve_embedding_model_id(text_embedding_model_id, *, auto_pick_local_embedding=False):
        return None, []

    async def fake_get_active_embedding_config():
        return {
            "model": "bge-m3",
            "base_url": "http://127.0.0.1:11434/v1",
            "api_key": "dummy",
            "llm_type": "Embedding",
            "model_slot": "embedding",
            "provider": "config",
            "llm_id": None,
            "is_local": True,
        }

    async def fake_get_embedding(text, config_override=None):
        return [0.1, 0.2, 0.3]

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_local_embedding_eval.resolve_embedding_model_id",
        fake_resolve_embedding_model_id,
    )
    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_local_embedding_eval.get_active_embedding_config",
        fake_get_active_embedding_config,
    )
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.get_embedding", fake_get_embedding)

    payload = asyncio.run(
        preflight_local_embedding_eval(
            text_embedding_model_id=None,
            use_active_config_embedding=True,
        )
    )
    assert payload["resolved_text_embedding_model_id"] is None
    assert payload["active_embedding_config"]["model_slot"] == "embedding"
    assert payload["embedding_probe"]["dimension"] == 3


def test_preflight_rejects_remote_embedding_target(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import preflight_local_embedding_eval

    async def fake_get_llm_by_id(llm_id):
        return {
            "llm_id": llm_id,
            "llm_type": "Embedding",
            "model": "text-embedding-v4",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        }

    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMService.get_llm_by_id", fake_get_llm_by_id)

    try:
        asyncio.run(preflight_local_embedding_eval(text_embedding_model_id="embed_remote"))
    except ValueError as exc:
        assert "not local" in str(exc)
    else:
        raise AssertionError("expected remote embedding target to be rejected")


def test_resolve_direct_local_embedding_registration_registers_new_llm(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import resolve_direct_local_embedding_registration

    created_payloads = []
    rows = []

    class FakeRow:
        def __init__(self, payload):
            self.payload = payload

        def to_dict(self):
            return dict(self.payload)

    async def fake_get_all_llm():
        return [FakeRow(item) for item in rows]

    async def fake_create_llm(**kwargs):
        created_payloads.append(dict(kwargs))
        rows.append(
            {
                "llm_id": "llm_local_direct_1",
                "llm_type": kwargs["llm_type"],
                "model": kwargs["model"],
                "base_url": kwargs["base_url"],
                "api_key": kwargs["api_key"],
                "provider": kwargs["provider"],
                "user_id": kwargs["user_id"],
                "model_slot": kwargs.get("model_slot"),
            }
        )

    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMDao.get_all_llm", fake_get_all_llm)
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMService.create_llm", fake_create_llm)

    payload = asyncio.run(
        resolve_direct_local_embedding_registration(
            model_name="bge-m3",
            base_url="http://127.0.0.1:11434/v1",
            api_key="",
        )
    )
    assert payload["llm_id"] == "llm_local_direct_1"
    assert created_payloads[0]["provider"] == "openai-compatible-local"


def test_preflight_accepts_direct_local_embedding_registration(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import preflight_local_embedding_eval

    async def fake_resolve_direct_local_embedding_registration(*, model_name=None, base_url=None, api_key=None):
        assert model_name == "bge-m3"
        assert base_url == "http://127.0.0.1:11434/v1"
        return {
            "llm_id": "llm_local_direct_1",
            "llm_type": "Embedding",
            "model": "bge-m3",
            "base_url": "http://127.0.0.1:11434/v1",
            "provider": "openai-compatible-local",
        }

    async def fake_get_llm_by_id(llm_id):
        return {
            "llm_id": llm_id,
            "llm_type": "Embedding",
            "model": "bge-m3",
            "base_url": "http://127.0.0.1:11434/v1",
        }

    async def fake_list_llm_candidates(*, expected_type=None, local_only=False):
        return [{"llm_id": "llm_local_direct_1", "llm_type": "Embedding", "is_local": True}]

    async def fake_get_embedding(text, config_override=None):
        return [0.1, 0.2, 0.3, 0.4]

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_local_embedding_eval.resolve_direct_local_embedding_registration",
        fake_resolve_direct_local_embedding_registration,
    )
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.LLMService.get_llm_by_id", fake_get_llm_by_id)
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.list_llm_candidates", fake_list_llm_candidates)
    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.get_embedding", fake_get_embedding)

    payload = asyncio.run(
        preflight_local_embedding_eval(
            text_embedding_model_id=None,
            direct_local_embedding_model_name="bge-m3",
            direct_local_embedding_base_url="http://127.0.0.1:11434/v1",
            register_direct_local_embedding=True,
        )
    )
    assert payload["resolved_text_embedding_model_id"] == "llm_local_direct_1"
    assert payload["direct_local_registration"]["provider"] == "openai-compatible-local"
    assert payload["embedding_probe"]["dimension"] == 4


def test_preflight_accepts_direct_local_embedding_without_registration(monkeypatch):
    from tools.evals.zuno.rag_eval.run_local_embedding_eval import preflight_local_embedding_eval

    async def fake_get_embedding(text, config_override=None):
        assert config_override["model"] == "bge-m3-dev"
        assert config_override["base_url"] == "http://127.0.0.1:11434/v1"
        return [0.1, 0.2, 0.3]

    monkeypatch.setattr("tools.evals.zuno.rag_eval.run_local_embedding_eval.get_embedding", fake_get_embedding)

    payload = asyncio.run(
        preflight_local_embedding_eval(
            text_embedding_model_id=None,
            direct_local_embedding_model_name="bge-m3-dev",
            direct_local_embedding_base_url="http://127.0.0.1:11434/v1",
            register_direct_local_embedding=False,
        )
    )
    assert payload["resolved_text_embedding_model_id"] is None
    assert payload["direct_local_registration"] is None
    assert payload["direct_local_config"]["model"] == "bge-m3-dev"
    assert payload["embedding_probe"]["dimension"] == 3


def test_run_local_embedding_eval_falls_back_to_stackless_when_db_is_unavailable(monkeypatch):
    from sqlalchemy.exc import OperationalError

    from tools.evals.zuno.rag_eval.run_local_embedding_eval import run_local_embedding_eval

    async def fake_preflight_local_embedding_eval(**kwargs):
        raise OperationalError("select 1", {}, Exception("localhost:5432 unavailable"))

    async def fake_run_stackless_local_eval(**kwargs):
        output_root = Path(kwargs["output_root"])
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / "baseline_rag").mkdir(parents=True, exist_ok=True)
        (output_root / "baseline_rag" / "metrics.json").write_text(
            '{"sample_count":1,"retrieval_recall_at_k":1.0,"hit_rate_at_k":1.0,"context_precision_at_k":1.0,"mrr_at_k":1.0,"ndcg_at_k":1.0,"faithfulness":1.0,"citation_accuracy":1.0}',
            encoding="utf-8",
        )
        return {
            "knowledge_id": "stackless_eval_1",
            "profiles": ["baseline_rag"],
            "output_root": str(output_root),
            "effective_dataset_path": "dataset.jsonl",
            "preflight": {"embedding_probe": {"dimension": 3}},
            "report": {"profiles": {"baseline_rag": {"retrieval_recall_at_k": 1.0}}},
        }

    def fake_summarize(*, dataset_path, profiles_root):
        return {"profiles": {"baseline_rag": {"overall": {"retrieval_recall_at_k": 1.0}}}}

    def fake_write_markdown(path, summary):
        path.write_text("# summary", encoding="utf-8")

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_local_embedding_eval.preflight_local_embedding_eval",
        fake_preflight_local_embedding_eval,
    )
    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_stackless_local_eval.run_stackless_local_eval",
        fake_run_stackless_local_eval,
    )
    monkeypatch.setattr("tools.evals.zuno.rag_eval.summarize_eval_profiles.summarize", fake_summarize)
    monkeypatch.setattr("tools.evals.zuno.rag_eval.summarize_eval_profiles.write_markdown", fake_write_markdown)

    result = asyncio.run(
        run_local_embedding_eval(
            manifest_path=Path("manifest.json"),
            dataset_path=Path("dataset.jsonl"),
            knowledge_name="ZunoLocalEmbeddingEval",
            text_embedding_model_id=None,
            profile_set="local_compare",
            output_root=default_runs_root() / "test-local-embedding-fallback",
            direct_local_embedding_model_name="zuno-local-embedding-dev",
            direct_local_embedding_base_url="http://127.0.0.1:11434/v1",
        )
    )
    assert result["execution_mode"] == "stackless_fallback"
    assert result["fallback_reason"] == "database_unavailable_for_local_embedding_registration_or_ingest"
    assert result["knowledge_id"] == "stackless_eval_1"
