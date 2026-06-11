from typing import List
import re
from uuid import uuid4

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

from agentchat.api.services.dialog import DialogService
from agentchat.database.dao.history import HistoryDao
from agentchat.services.rag.es_client import client as es_client
from agentchat.services.rag.vector_db import milvus_client
from agentchat.schema.chunk import ChunkModel
from agentchat.utils.helpers import get_now_beijing_time
from agentchat.utils.model_output import strip_model_wrapper_from_user_input

Assistant_Role = "assistant"
User_Role = "user"
WRAPPED_HISTORY_HINTS = ("<chat_history>", "web_search", "read_webpage", "tool_code", "对话历史")


class HistoryService:
    @staticmethod
    def _looks_like_system_prompt(content: str | None) -> bool:
        if not content:
            return False

        raw = str(content)
        lowered = re.sub(r"\s+", "", raw).lower()
        stripped = strip_model_wrapper_from_user_input(raw)
        if stripped != raw.strip():
            return True

        return any(hint in lowered for hint in WRAPPED_HISTORY_HINTS)

    @staticmethod
    def _strip_system_prompt_wrapper(content: str | None) -> str | None:
        if not content:
            return content

        stripped = strip_model_wrapper_from_user_input(content)
        return stripped if stripped else content

    @classmethod
    async def create_history(cls, role: str, content: str, events: List[dict], dialog_id: str):
        try:
            await HistoryDao.create_history(role, content, events, dialog_id)
        except Exception as err:
            raise ValueError(f"Add history data appear error: {err}")

    @classmethod
    async def select_history(cls, dialog_id: str, top_k: int = 4) -> List[BaseMessage] | None:
        try:
            result = await HistoryDao.select_history_from_time(dialog_id, top_k)
            messages: List[BaseMessage] = []
            for data in result:
                if data.role == Assistant_Role:
                    if cls._looks_like_system_prompt(data.content):
                        continue
                    messages.append(AIMessage(content=data.content))
                elif data.role == User_Role:
                    cleaned = cls._strip_system_prompt_wrapper(data.content)
                    if not cleaned or cls._looks_like_system_prompt(cleaned):
                        continue
                    messages.append(HumanMessage(content=cleaned))
            return messages
        except Exception as err:
            raise ValueError(f"Select history is appear error: {err}")

    @classmethod
    async def enable_memory_select_history(cls, dialog_id: str, top_k: int = 10):
        pass

    @classmethod
    async def get_dialog_history(cls, dialog_id: str):
        try:
            results = await HistoryDao.get_dialog_history(dialog_id)
            cleaned_results = []
            for res in results:
                if res.role not in (User_Role, Assistant_Role):
                    continue
                if res.role == Assistant_Role:
                    if cls._looks_like_system_prompt(res.content):
                        continue
                    cleaned_results.append(res.to_dict())
                    continue

                cleaned = cls._strip_system_prompt_wrapper(res.content)
                if not cleaned or cls._looks_like_system_prompt(cleaned):
                    continue
                payload = res.to_dict()
                payload["content"] = cleaned
                cleaned_results.append(payload)

            return cleaned_results
        except Exception as err:
            raise ValueError(f"Get dialog history is appear error: {err}")

    @classmethod
    async def save_es_documents(cls, index_name, content):
        chunk = ChunkModel(
            chunk_id=uuid4().hex,
            content=content,
            file_id="history_rag",
            knowledge_id=index_name,
            summary="history_rag",
            update_time=get_now_beijing_time(),
            file_name="history_rag",
        )

        chunks = [chunk]

        await es_client.index_documents(index_name, chunks)

    @classmethod
    async def save_milvus_documents(cls, collection_name, content):
        chunk = ChunkModel(
            chunk_id=uuid4().hex,
            content=content,
            file_id='history_rag',
            knowledge_id=collection_name,
            update_time=get_now_beijing_time(),
            summary="history_rag",
            file_name='history_rag'
        )
        chunks = [chunk]

        await milvus_client.insert(collection_name, chunks)

    @classmethod
    async def save_chat_history(cls, role, content, events, dialog_id, memory_enable: bool = False):
        if role == User_Role:
            content = cls._strip_system_prompt_wrapper(content)

        if role == Assistant_Role and cls._looks_like_system_prompt(content):
            await DialogService.update_dialog_time(dialog_id=dialog_id)
            return

        await cls.create_history(role, content, events, dialog_id)
        await DialogService.update_dialog_time(dialog_id=dialog_id)

        # 目前都已经改成使用 Memory 功能，历史记录只存数据库中
        # if memory_enable:
        #     documents = f"{role}: \n {content}"
        #     await cls.save_es_documents(dialog_id, documents)
        #     await cls.save_milvus_documents(dialog_id, documents)
        #     await DialogService.update_dialog_time(dialog_id=dialog_id)
