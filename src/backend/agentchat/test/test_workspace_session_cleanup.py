import asyncio


def test_create_workspace_session_prunes_empty_disposable_sessions_for_same_scope(monkeypatch):
    from agentchat.api.services.workspace_session import WorkSpaceSessionService
    from agentchat.database.models.workspace_session import WorkSpaceSessionCreate

    captured = {"deleted": None, "created": None}

    class FakeExistingSession:
        def __init__(self, session_id):
            self.session_id = session_id
            self.contexts = []

    async def fake_get_workspace_sessions(user_id, workspace_mode=None):
        assert user_id == "u_scope"
        assert workspace_mode == "agent"
        return [FakeExistingSession("old_empty_session")]

    async def fake_delete_workspace_session(session_ids, user_id):
        captured["deleted"] = (session_ids, user_id)

    async def fake_create_workspace_session(workspace_session):
        captured["created"] = workspace_session
        return workspace_session

    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.get_workspace_sessions",
        fake_get_workspace_sessions,
    )
    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.delete_workspace_session",
        fake_delete_workspace_session,
    )
    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.create_workspace_session",
        fake_create_workspace_session,
    )

    payload = WorkSpaceSessionCreate(
        title="Fresh agent session",
        agent="simple",
        user_id="u_scope",
        workspace_mode="agent",
        contexts=[],
    )

    asyncio.run(WorkSpaceSessionService.create_workspace_session(payload))

    assert captured["deleted"] == (["old_empty_session"], "u_scope")
    assert captured["created"] is not None


def test_create_workspace_session_keeps_nonempty_or_nondisposable_sessions(monkeypatch):
    from agentchat.api.services.workspace_session import WorkSpaceSessionService
    from agentchat.database.models.workspace_session import WorkSpaceSessionCreate

    captured = {"deleted": None}

    class FakeExistingSession:
        def __init__(self, session_id, contexts=None):
            self.session_id = session_id
            self.contexts = contexts or []

    async def fake_get_workspace_sessions(user_id, workspace_mode=None):
        return [
            FakeExistingSession("non_empty", contexts=[{"query": "hi", "answer": "there"}]),
            FakeExistingSession("another_non_empty", contexts=[{"query": "yo", "answer": "ok"}]),
        ]

    async def fake_delete_workspace_session(session_ids, user_id):
        captured["deleted"] = (session_ids, user_id)

    async def fake_create_workspace_session(workspace_session):
        return workspace_session

    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.get_workspace_sessions",
        fake_get_workspace_sessions,
    )
    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.delete_workspace_session",
        fake_delete_workspace_session,
    )
    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.create_workspace_session",
        fake_create_workspace_session,
    )

    payload = WorkSpaceSessionCreate(
        title="Fresh normal session",
        agent="simple",
        user_id="u_scope",
        workspace_mode="normal",
        contexts=[],
    )

    asyncio.run(WorkSpaceSessionService.create_workspace_session(payload))

    assert captured["deleted"] is None


def test_update_workspace_session_contexts_passes_normalized_title(monkeypatch):
    from agentchat.api.services.workspace_session import WorkSpaceSessionService

    captured = {}

    async def fake_update_workspace_session_contexts(session_id, session_context, title=None):
        captured["session_id"] = session_id
        captured["session_context"] = session_context
        captured["title"] = title
        return {"session_id": session_id, "title": title, "contexts": [session_context]}

    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.update_workspace_session_contexts",
        fake_update_workspace_session_contexts,
    )

    asyncio.run(
        WorkSpaceSessionService.update_workspace_session_contexts(
            "session_1",
            {"query": "帮我查天气", "answer": "好的"},
            title="### 天气查询",
        )
    )

    assert captured["session_id"] == "session_1"
    assert captured["session_context"]["query"] == "帮我查天气"
    assert captured["title"] == "天气查询"


def test_get_workspace_sessions_hides_empty_drafts(monkeypatch):
    from agentchat.api.services.workspace_session import WorkSpaceSessionService

    class FakeSession:
        def __init__(self, session_id, contexts):
            self.session_id = session_id
            self.title = session_id
            self.agent = "agent"
            self.contexts = contexts
            self.update_time = None
            self.create_time = None

        def to_dict(self):
            return {
                "session_id": self.session_id,
                "title": self.title,
                "agent": self.agent,
                "contexts": self.contexts,
                "update_time": self.update_time,
                "create_time": self.create_time,
            }

    async def fake_get_workspace_sessions(user_id, workspace_mode=None):
        return [
            FakeSession("empty_draft", []),
            FakeSession("real_session", [{"query": "hi", "answer": "ok"}]),
        ]

    monkeypatch.setattr(
        "agentchat.api.services.workspace_session.WorkSpaceSessionDao.get_workspace_sessions",
        fake_get_workspace_sessions,
    )

    result = asyncio.run(WorkSpaceSessionService.get_workspace_sessions("u_scope", "agent"))

    assert [item["session_id"] for item in result] == ["real_session"]
