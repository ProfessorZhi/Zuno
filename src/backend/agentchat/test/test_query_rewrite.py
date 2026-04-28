import asyncio

from agentchat.services.rewrite.query_write import QueryRewrite


class _FakeResponse:
    def __init__(self, content):
        self.content = content


class _FakeClient:
    def __init__(self, content):
        self._content = content

    def invoke(self, _messages):
        return _FakeResponse(self._content)


def test_query_rewrite_accepts_json_array(monkeypatch):
    rewriter = QueryRewrite()
    monkeypatch.setattr(rewriter, '_get_client', lambda: _FakeClient('["问题一", "问题二", "问题三"]'))

    result = asyncio.run(rewriter.rewrite('原问题'))

    assert result == ['问题一', '问题二', '问题三']


def test_query_rewrite_accepts_variations_object(monkeypatch):
    rewriter = QueryRewrite()
    monkeypatch.setattr(
        rewriter,
        '_get_client',
        lambda: _FakeClient('{"original_query":"原问题","variations":["问题一","问题二","问题三"]}'),
    )

    result = asyncio.run(rewriter.rewrite('原问题'))

    assert result == ['问题一', '问题二', '问题三']


def test_query_rewrite_falls_back_when_json_invalid(monkeypatch):
    rewriter = QueryRewrite()
    monkeypatch.setattr(rewriter, '_get_client', lambda: _FakeClient('not-json'))

    result = asyncio.run(rewriter.rewrite('原问题'))

    assert result == ['原问题']
