from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from langchain.tools import tool


class _ReadableTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth:
            return

        text = " ".join(data.split())
        if text:
            self._parts.append(text)

    def text(self) -> str:
        return "\n".join(self._parts)


@tool("read_webpage", parse_docstring=True)
def read_webpage(url: str) -> str:
    """
    读取网页正文内容，适用于用户要求打开、查看、总结某个 URL 的场景。

    Args:
        url: 用户提供的完整网页 URL，必须以 http:// 或 https:// 开头

    Returns:
        网页标题与可读正文摘要，或读取失败原因
    """
    if not url.startswith(("http://", "https://")):
        return "网页读取失败：请提供以 http:// 或 https:// 开头的完整 URL。"

    try:
        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            },
        )
        with urlopen(request, timeout=12) as response:
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(800_000)

        if "text/html" not in content_type and "text/plain" not in content_type:
            return f"网页读取完成，但内容类型是 {content_type or '未知'}，不是可直接总结的文本页面。"

        html = raw.decode("utf-8", errors="ignore")
        parser = _ReadableTextParser()
        parser.feed(html)
        text = parser.text().strip()

        if not text:
            return "网页读取完成，但没有提取到可读正文。"

        return f"URL: {url}\n\n网页正文摘录:\n{text[:12000]}"
    except HTTPError as exc:
        return f"网页读取失败：HTTP {exc.code} {exc.reason}"
    except URLError as exc:
        return f"网页读取失败：{exc.reason}"
    except Exception as exc:
        return f"网页读取失败：{exc}"
