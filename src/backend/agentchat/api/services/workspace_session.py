import re

from agentchat.database.dao.workspace_session import WorkSpaceSession, WorkSpaceSessionDao
from agentchat.database.models.workspace_session import WorkSpaceSessionCreate
from agentchat.utils.model_output import strip_model_wrapper_from_user_input, strip_think_tags


WRAPPED_HISTORY_HINTS = ("<chat_history>", "web_search", "read_webpage", "tool_code", "对话历史")


PLACEHOLDER_SESSION_TITLES = {"", "新对话", "未命名会话", "你好", "您好", "hi", "hello"}


class WorkSpaceSessionService:
    @staticmethod
    def is_placeholder_title(title: str | None) -> bool:
        return str(title or "").strip().lower() in PLACEHOLDER_SESSION_TITLES

    @staticmethod
    def normalize_workspace_mode(raw_mode: str | None) -> str:
        return "agent" if str(raw_mode or "").strip().lower() == "agent" else "normal"

    @classmethod
    def serialize_session(cls, session: WorkSpaceSession | dict | None) -> dict | None:
        if session is None:
            return None

        payload = session if isinstance(session, dict) else session.to_dict()
        payload["contexts"] = cls.sanitize_contexts(payload.get("contexts", []))
        payload["workspace_mode"] = cls.normalize_workspace_mode(payload.get("agent"))
        return payload

    @classmethod
    async def prune_empty_workspace_sessions(cls, user_id: str, workspace_mode: str) -> None:
        sessions = await WorkSpaceSessionDao.get_workspace_sessions(user_id, workspace_mode=workspace_mode)
        empty_session_ids = [
            session.session_id
            for session in sessions
            if not (session.contexts or [])
        ]
        if empty_session_ids:
            await WorkSpaceSessionDao.delete_workspace_session(empty_session_ids, user_id)

    @staticmethod
    def _looks_like_system_wrapper(content: str | None) -> bool:
        if not content:
            return False

        raw = str(content)
        lowered = re.sub(r"\s+", "", raw).lower()
        stripped = strip_model_wrapper_from_user_input(raw)
        if stripped != raw.strip():
            return True

        return any(hint in lowered for hint in WRAPPED_HISTORY_HINTS)

    @classmethod
    def sanitize_context(cls, context: dict | None) -> dict | None:
        if not context:
            return context

        cleaned = dict(context)
        query = str(cleaned.get("query") or "")
        if cls._looks_like_system_wrapper(query):
            cleaned["query"] = strip_model_wrapper_from_user_input(query)
        return cleaned

    @classmethod
    def sanitize_contexts(cls, contexts: list[dict] | None) -> list[dict]:
        if not contexts:
            return []
        return [ctx for ctx in (cls.sanitize_context(context) for context in contexts) if ctx]

    @staticmethod
    def normalize_session_title(raw_title: str, fallback_query: str = "") -> str:
        fallback_query = (fallback_query or "").strip()
        title = strip_think_tags(raw_title or "").strip()

        if title:
            title = re.sub(r"<think>.*?</think>", "", title, flags=re.IGNORECASE | re.DOTALL)
            title = re.sub(r"<Thought_END>.*?</Thought_END>", "", title, flags=re.IGNORECASE | re.DOTALL)
            title = title.replace("```", " ").replace("\r", "\n")

            candidates = []
            for line in title.splitlines():
                normalized_line = line.strip().lstrip("-*#>\"'` ").strip()
                normalized_line = re.sub(r"[。！？，：:;,，；]+$", "", normalized_line)
                if normalized_line:
                    candidates.append(normalized_line)

            short_candidates = [candidate for candidate in candidates if len(candidate) <= 32]
            if short_candidates:
                return short_candidates[-1][:32]

            compact_title = re.sub(r"\s+", " ", title).strip()
            if compact_title:
                return compact_title[:32]

        if fallback_query:
            return fallback_query[:32]

        return "新对话"

    @classmethod
    async def create_workspace_session(cls, session_create: WorkSpaceSessionCreate):
        payload = session_create.model_dump()
        workspace_mode = cls.normalize_workspace_mode(payload.pop("workspace_mode", "normal"))
        payload["contexts"] = cls.sanitize_contexts(payload.get("contexts", []))
        payload["agent"] = workspace_mode
        await cls.prune_empty_workspace_sessions(payload["user_id"], workspace_mode)
        workspace_session = WorkSpaceSession(**payload)
        return await WorkSpaceSessionDao.create_workspace_session(workspace_session)

    @classmethod
    async def get_workspace_sessions(cls, user_id, workspace_mode: str | None = None):
        normalized_mode = cls.normalize_workspace_mode(workspace_mode) if workspace_mode else None
        results = await WorkSpaceSessionDao.get_workspace_sessions(user_id, workspace_mode=normalized_mode)
        results = [result for result in results if result.contexts or []]
        results.sort(key=lambda x: x.update_time, reverse=True)
        return [cls.serialize_session(result) for result in results]

    @classmethod
    async def delete_workspace_session(cls, session_ids, user_id):
        await WorkSpaceSessionDao.delete_workspace_session(session_ids, user_id)

    @classmethod
    async def update_workspace_session_contexts(cls, session_id, session_context, title: str | None = None):
        return await WorkSpaceSessionDao.update_workspace_session_contexts(
            session_id,
            cls.sanitize_context(session_context),
            cls.normalize_session_title(title or "", fallback_query=session_context.get("query", "")) if title else None,
        )

    @classmethod
    async def clear_workspace_session_contexts(cls, session_id):
        return await WorkSpaceSessionDao.clear_workspace_session_contexts(session_id)

    @classmethod
    async def get_workspace_session_from_id(cls, session_id, user_id):
        result = await WorkSpaceSessionDao.get_workspace_session_from_id(session_id, user_id=user_id)
        return cls.serialize_session(result)

    @classmethod
    async def generate_session_title(cls, user_query):
        pass
