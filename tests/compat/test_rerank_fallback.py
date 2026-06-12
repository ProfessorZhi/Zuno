import asyncio
from unittest.mock import patch

from agentchat.services.rag.rerank import Reranker
from agentchat.settings import app_settings


def test_rerank_documents_falls_back_when_not_configured():
    original_api_key = app_settings.multi_models.rerank.api_key
    original_base_url = app_settings.multi_models.rerank.base_url
    original_model_name = app_settings.multi_models.rerank.model_name

    app_settings.multi_models.rerank.api_key = ""
    app_settings.multi_models.rerank.base_url = ""
    app_settings.multi_models.rerank.model_name = ""

    try:
        with patch("agentchat.database.dao.llm.LLMDao.get_llm_by_slot", return_value=None):
            results = asyncio.run(Reranker.rerank_documents("什么是 RAG", ["doc1", "doc2"]))
    finally:
        app_settings.multi_models.rerank.api_key = original_api_key
        app_settings.multi_models.rerank.base_url = original_base_url
        app_settings.multi_models.rerank.model_name = original_model_name

    assert [item.content for item in results] == ["doc1", "doc2"]
    assert all(item.query == "什么是 RAG" for item in results)
