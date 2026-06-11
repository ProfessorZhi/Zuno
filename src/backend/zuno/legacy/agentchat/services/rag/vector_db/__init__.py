from agentchat.services.rag.vector_db.milvus_client import MilvusClient
from agentchat.services.rag.vector_db.chroma_client import ChromaClient
from agentchat.services.rag.vector_db.milvus_lite_client import MilvusLiteClient
from agentchat.settings import app_settings


class LazyVectorStoreClient:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            mode = app_settings.rag.vector_db.get("mode")
            if mode == "chroma":
                self._client = ChromaClient()
            elif mode == "lite":
                self._client = MilvusLiteClient()
            else:
                self._client = MilvusClient()
        return self._client

    def __getattr__(self, item):
        return getattr(self._get_client(), item)


milvus_client = LazyVectorStoreClient()
