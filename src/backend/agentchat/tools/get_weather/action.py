import requests
from langchain.tools import tool
from loguru import logger

from agentchat.prompts.tool import MESSAGE_PROMPT, WEATHER_PROMPT
from agentchat.settings import app_settings


@tool(parse_docstring=True)
def get_weather(city: str):
    """
    查询用户提供城市的天气情况。

    Args:
        city (str): 用户提供的城市名称。

    Returns:
        str: 城市的天气信息或清晰的失败原因。
    """
    return _get_weather(city)


def _get_weather(location: str):
    """帮助用户查询城市天气。"""
    api_key = (app_settings.tools.weather.get("api_key") or "").strip()
    endpoint = (app_settings.tools.weather.get("endpoint") or "").strip()

    if not api_key:
        return "天气工具暂不可用：系统尚未配置高德天气 API Key，请先完成工具配置。"
    if not endpoint:
        return "天气工具暂不可用：系统尚未配置天气接口地址，请先完成工具配置。"

    params = {
        "key": api_key,
        "city": location,
        "extensions": "all",
    }

    try:
        response = requests.get(url=endpoint, params=params, timeout=5)
        response.raise_for_status()
        result = response.json()

        if result.get("status") != "1":
            error_message = result.get("info") or result.get("infocode") or "天气接口返回异常"
            return f"天气工具暂不可用：{error_message}。请检查高德天气 API Key 或接口配置。"

        forecasts = result.get("forecasts") or []
        if not forecasts:
            return f"天气工具未返回 {location} 的天气数据，请确认城市名称是否正确。"

        forecast = forecasts[0] or {}
        city = forecast.get("city") or location
        casts = forecast.get("casts") or []
        if not casts:
            return f"天气工具未返回 {city} 的详细天气预报，请稍后重试。"

        message_result: list[str] = []
        for item in casts:
            weather_message = MESSAGE_PROMPT.format(
                item.get("date"),
                item.get("daytemp"),
                item.get("nighttemp"),
                item.get("dayweather"),
                item.get("nightweather"),
            )
            message_result.append(weather_message)

        if not message_result:
            return f"天气工具未返回 {city} 的可用天气内容，请稍后重试。"

        return WEATHER_PROMPT.format(city, message_result[0], message_result[1:])
    except Exception as err:
        logger.error(f"Call Weather Tool Err: {err}")
        return "天气工具暂不可用：请求天气服务失败，请检查网络或工具配置后重试。"
