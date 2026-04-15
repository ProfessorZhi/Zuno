from agentchat.tools.arxiv.action import get_arxiv
from agentchat.tools.convert_to_docx.action import convert_to_docx
from agentchat.tools.convert_to_pdf.action import convert_to_pdf
from agentchat.tools.delivery.action import get_delivery_info
from agentchat.tools.get_weather.action import get_weather
from agentchat.tools.image2text.action import image_to_text
from agentchat.tools.send_email.action import list_email_accounts, send_email
from agentchat.tools.text2image.action import text_to_image
from agentchat.tools.web_reader.action import read_webpage
from agentchat.tools.web_search.bocha_search.action import bocha_search
from agentchat.tools.web_search.google_search.action import google_search
from agentchat.tools.web_search.tavily_search.action import tavily_search


AgentTools = [
    send_email,
    list_email_accounts,
    tavily_search,
    read_webpage,
    bocha_search,
    get_weather,
    get_arxiv,
    get_delivery_info,
    text_to_image,
    image_to_text,
    convert_to_pdf,
    convert_to_docx,
]


AgentToolsWithName = {
    "send_email": send_email,
    "list_email_accounts": list_email_accounts,
    "tavily_search": tavily_search,
    "web_search": tavily_search,
    "read_webpage": read_webpage,
    "get_arxiv": get_arxiv,
    "get_weather": get_weather,
    "get_delivery": get_delivery_info,
    "get_delivery_info": get_delivery_info,
    "text_to_image": text_to_image,
    "image_to_text": image_to_text,
    "convert_to_pdf": convert_to_pdf,
    "convert_to_docx": convert_to_docx,
    "bocha_search": bocha_search,
}


WorkSpacePlugins = AgentToolsWithName


WeChatTools = {
    "tavily_search": tavily_search,
    "get_arxiv": get_arxiv,
    "get_weather": get_weather,
    "text_to_image": text_to_image,
    "bocha_search": bocha_search,
    "read_webpage": read_webpage,
}


__all__ = [
    "AgentTools",
    "AgentToolsWithName",
    "WorkSpacePlugins",
    "WeChatTools",
    "google_search",
]
