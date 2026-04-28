import asyncio
from types import SimpleNamespace


def test_create_workspace_session_endpoint_persists_scope_payload(monkeypatch):
    from agentchat.api.v1.workspace import (
        WorkSpaceSessionCreateBody,
        create_workspace_session,
    )

    captured = {}

    class FakeSession:
        def __init__(self, payload):
            self.payload = payload

        def to_dict(self):
            return {
                "session_id": self.payload.session_id or "session_new",
                "title": self.payload.title,
                "agent": self.payload.workspace_mode,
                "user_id": self.payload.user_id,
                "workspace_mode": self.payload.workspace_mode,
                "contexts": self.payload.contexts,
            }

    async def fake_create_workspace_session(payload):
        captured["payload"] = payload
        return FakeSession(payload)

    monkeypatch.setattr(
        "agentchat.api.v1.workspace.WorkSpaceSessionService.create_workspace_session",
        fake_create_workspace_session,
    )

    login_user = SimpleNamespace(user_id="u_browser")
    body = WorkSpaceSessionCreateBody(
        title="Browser fresh session",
        session_id="session_browser_1",
        agent="simple",
        workspace_mode="agent",
        contexts=[{"query": "What is RAG?", "answer": "retrieval augmented generation"}],
    )

    response = asyncio.run(create_workspace_session(body, login_user))

    assert response.status_code == 200
    assert response.data["title"] == "Browser fresh session"
    assert response.data["session_id"] == "session_browser_1"
    assert response.data["workspace_mode"] == "agent"
    assert captured["payload"].user_id == "u_browser"
    assert captured["payload"].contexts[0]["query"] == "What is RAG?"


def test_create_workspace_session_endpoint_allows_missing_session_id(monkeypatch):
    from agentchat.api.v1.workspace import (
        WorkSpaceSessionCreateBody,
        create_workspace_session,
    )

    captured = {}

    class FakeSession:
        def __init__(self, payload):
            self.payload = payload

        def to_dict(self):
            return {
                "session_id": self.payload.session_id or "session_generated",
                "title": self.payload.title,
                "agent": self.payload.workspace_mode,
                "user_id": self.payload.user_id,
                "workspace_mode": self.payload.workspace_mode,
                "contexts": self.payload.contexts,
            }

    async def fake_create_workspace_session(payload):
        captured["payload"] = payload
        return FakeSession(payload)

    monkeypatch.setattr(
        "agentchat.api.v1.workspace.WorkSpaceSessionService.create_workspace_session",
        fake_create_workspace_session,
    )

    login_user = SimpleNamespace(user_id="u_workspace")
    body = WorkSpaceSessionCreateBody(
        title="New workspace session",
        agent="simple",
        workspace_mode="normal",
        contexts=[],
    )

    response = asyncio.run(create_workspace_session(body, login_user))

    assert response.status_code == 200
    assert response.data["session_id"] == "session_generated"
    assert response.data["workspace_mode"] == "normal"
    assert captured["payload"].session_id is None


def test_get_workspace_sessions_endpoint_passes_mode_filter(monkeypatch):
    from agentchat.api.v1.workspace import get_workspace_sessions

    captured = {}

    async def fake_get_workspace_sessions(user_id, workspace_mode=None):
        captured["args"] = {
            "user_id": user_id,
            "workspace_mode": workspace_mode,
        }
        return []

    monkeypatch.setattr(
        "agentchat.api.v1.workspace.WorkSpaceSessionService.get_workspace_sessions",
        fake_get_workspace_sessions,
    )

    login_user = SimpleNamespace(user_id="u_scope")
    response = asyncio.run(
        get_workspace_sessions(
            workspace_mode="agent",
            login_user=login_user,
        )
    )

    assert response.status_code == 200
    assert captured["args"] == {
        "user_id": "u_scope",
        "workspace_mode": "agent",
    }
