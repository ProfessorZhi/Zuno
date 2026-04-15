from langchain.tools import tool
from langchain_community.utilities import SerpAPIWrapper

from agentchat.settings import app_settings


def _get_search_client() -> SerpAPIWrapper:
    api_key = (app_settings.tools.google.get("api_key") or "").strip()
    if not api_key:
        raise ValueError("Google 搜索工具未配置，请先在系统中补充 Google/SerpAPI Key")
    return SerpAPIWrapper(serpapi_api_key=api_key)


@tool("web_search", parse_docstring=True)
def google_search(query: str):
    """
    根据用户的问题进行网上搜索信息。

    Args:
        query (str): 用户的问题。

    Returns:
        str: 搜索到的信息。
    """
    return _google_search(query)


def _google_search(query: str):
    """使用搜索工具给用户进行搜索"""
    result = _get_search_client().run(query)
    return result
