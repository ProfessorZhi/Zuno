import json
import ssl
import urllib.parse
import urllib.request

from langchain.tools import tool
from loguru import logger

from agentchat.prompts.tool import DELIVERY_PROMPT
from agentchat.settings import app_settings


@tool(parse_docstring=True)
def get_delivery_info(delivery_number: str, company_type: str = ""):
    """
    Query delivery tracking information from the configured Aliyun express API.

    Args:
        delivery_number (str): Tracking number, optionally suffixed like 123456789:1234.
        company_type (str): Optional courier company code such as zto, yto or sfexpress.

    Returns:
        str: Human readable delivery tracking result.
    """
    return _get_delivery(delivery_number, company_type)


def _get_delivery(delivery_number: str, company_type: str = ""):
    api_key = (app_settings.tools.delivery.get("api_key") or "").strip()
    endpoint = (app_settings.tools.delivery.get("endpoint") or "").strip()

    if not api_key:
        return "物流工具暂不可用：系统尚未配置阿里云物流 APPCODE，请先完成工具配置。"
    if not endpoint:
        return "物流工具暂不可用：系统尚未配置阿里云物流接口地址，请先完成工具配置。"

    params = {"no": delivery_number.strip()}
    if company_type.strip():
        params["type"] = company_type.strip()

    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    headers = {"Authorization": f"APPCODE {api_key}"}

    try:
        request = urllib.request.Request(url, headers=headers)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(request, context=ctx, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        status_code = str(payload.get("status", "")).strip()
        message = str(payload.get("msg", "")).strip()
        result = payload.get("result") or {}

        if status_code != "0":
            error_map = {
                "201": "快递单号错误",
                "203": "快递公司不存在",
                "204": "快递公司识别失败",
                "205": "没有查询到物流信息，可能需要补充快递公司代码",
                "207": "请求来源受限",
            }
            return f"物流查询失败：{error_map.get(status_code, message or '接口返回异常')}。"

        company = result.get("expName") or result.get("type") or (company_type or "自动识别")
        number = result.get("number") or delivery_number
        items = result.get("list") or []

        if not items:
            return f"未查询到 {number} 的物流轨迹，请确认单号是否正确，或补充快递公司代码后再试。"

        timeline = [
            f"时间：{item.get('time', '未知')}，物流信息：{item.get('status', '暂无描述')}"
            for item in items
        ]
        timeline.reverse()

        final_result = DELIVERY_PROMPT.format(company, number, "\n".join(timeline))
        logger.info(f"------执行物流 API------\n{final_result}")
        return final_result
    except Exception as err:
        logger.error(f"delivery action appear: {err}")
        return "查询快递信息失败，请检查阿里云物流接口配置、运单号，或稍后重试。"
