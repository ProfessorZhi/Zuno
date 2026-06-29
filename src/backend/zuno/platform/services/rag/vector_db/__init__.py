from __future__ import annotations

from pkgutil import extend_path

from zuno.settings import app_settings

__path__ = extend_path(__path__, __name__)


class LazyVectorStoreClient:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            mode = str((app_settings.rag.vector_db or {}).get("mode") or "").strip().lower()
            if mode == "chroma":
                from zuno.services.rag.vector_db.chroma_client import ChromaClient

                self._client = ChromaClient()
            elif mode == "lite":
                from zuno.services.rag.vector_db.milvus_lite_client import MilvusLiteClient

                self._client = MilvusLiteClient()
            else:
                from zuno.services.rag.vector_db.milvus_client import MilvusClient

                self._client = MilvusClient()
        return self._client

    def __getattr__(self, item):
        return getattr(self._get_client(), item)


milvus_client = LazyVectorStoreClient()

__all__ = ["LazyVectorStoreClient", "milvus_client"]
