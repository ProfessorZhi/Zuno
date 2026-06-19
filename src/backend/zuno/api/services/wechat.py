import hashlib
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
import requests
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from zuno.api.services.workspace_session import WorkSpaceSessionService
from zuno.services.redis import redis_client
from zuno.settings import app_settings
from zuno.utils.runtime_observability import RedisKeys

WECHAT_SYSTEM_PROMPT = """
浣犳槸涓€涓湡瀹炪€佽嚜鐒躲€佹湁娓╁害鐨勫井淇″姪鎵嬨€?璇风洿鎺ュ洖绛旂敤鎴烽棶棰橈紝浼樺厛绠€娲併€佸彲闈犮€佸儚鐪熷疄鍔╃悊涓€鏍蜂氦娴併€?涓嶈浣跨敤 Markdown銆?
鍘嗗彶瀵硅瘽锛?{history}
"""


class WeChatService:
    @classmethod
    def get_cached_reply(cls, from_user: str, content: str):
        return redis_client.get(RedisKeys.wechat_reply(from_user, content))

    @classmethod
    def cache_reply(cls, *, from_user: str, content: str, reply: str, expiration: int = 7200) -> None:
        redis_client.set(
            key=RedisKeys.wechat_reply(from_user, content),
            value={"user": from_user, "content": reply},
            expiration=expiration,
        )

    @classmethod
    async def build_history_messages(cls, from_user: str) -> str:
        workspace_session = await WorkSpaceSessionService.get_workspace_session_from_id(from_user, from_user)
        if workspace_session:
            contexts = workspace_session.get("contexts", [])
            return "\n".join(
                [
                    f"user query: {message.get('query')}, answer: {message.get('answer')}\n"
                    for message in reversed(contexts[-2:])
                ]
            )
        return "鏃犲巻鍙插璇?"

    @classmethod
    async def invoke_wechat_agent(
        cls,
        *,
        from_user: str,
        to_user: str,
        content: str,
        history_messages: str,
    ):
        from zuno.services.workspace.wechat_agent import WeChatAgent

        wechat_agent = WeChatAgent(
            user_id=from_user,
            session_id=from_user,
            wechat_account_user=to_user,
        )
        return await wechat_agent.ainvoke(
            [
                SystemMessage(WECHAT_SYSTEM_PROMPT.format(history=history_messages)),
                HumanMessage(content),
            ]
        )

    @classmethod
    def _get_access_token(cls):
        wechat_conf = app_settings.wechat_config
        url = (
            "https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential&appid={wechat_conf.get('app_id')}"
            f"&secret={wechat_conf.get('secret')}"
        )
        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=10)
                result = response.json()
                if "access_token" in result:
                    return result["access_token"]
                logger.error(f"failed to get access_token: {result}")
                return None
        except Exception as err:
            logger.error(f"failed to get access_token: {err}")
            return None

    @classmethod
    def send_user_message(cls, to_user, content):
        access_token = cls._get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        data = {
            "touser": to_user,
            "msgtype": "text",
            "text": {"content": content},
        }
        resp = requests.post(url, json=data)
        return resp.json()

    @classmethod
    def push_user_image(cls, image_path=None):
        access_token = cls._get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
        default_candidates = [Path("zuno/config/default.jpg"), Path("zuno/config/default.jpg")]
        default_image = next((str(candidate) for candidate in default_candidates if candidate.exists()), str(default_candidates[-1]))
        files = {"media": open(image_path or default_image, "rb")}
        response = requests.post(url, files=files)
        result = response.json()
        return result.get("media_id")

    @classmethod
    def check_signature(cls, token: str, signature: str, timestamp: str, nonce: str) -> bool:
        tmp_list = sorted([token, timestamp, nonce])
        tmp_str = "".join(tmp_list)
        tmp_str = hashlib.sha1(tmp_str.encode("utf-8")).hexdigest()
        return tmp_str == signature

    @classmethod
    def parse_wechat_xml(cls, xml_data: str):
        root = ET.fromstring(xml_data)
        msg_type = root.find("MsgType").text
        from_user = root.find("FromUserName").text
        to_user = root.find("ToUserName").text
        event = root.find("Event").text if root.find("Event") is not None else ""
        content = root.find("Content").text if root.find("Content") is not None else ""
        return {
            "msg_type": msg_type,
            "from_user": from_user,
            "to_user": to_user,
            "event": event,
            "content": content,
        }

    @classmethod
    async def process_user_keyword(cls, keyword, from_user, to_user):
        if keyword in ["清空会话", "清空聊天记录", "清除会话", "清除聊天记录"]:
            await WorkSpaceSessionService.clear_workspace_session_contexts(from_user)
            return cls.build_text_reply(to_user, from_user, "聊天记录已清空，有什么新问题再问我。")
        if "毕业照" in keyword:
            media_id = cls.push_user_image()
            return cls.build_image_reply(to_user, from_user, media_id)
        if "微信账号" in keyword:
            return cls.build_text_reply(
                to_user,
                from_user,
                f"您的微信账号为：{from_user}，可在当前部署的 Zuno 站点中使用微信账号注册并查看聊天记录。",
            )
        return None

    @classmethod
    def build_text_reply(cls, to_user: str, from_user: str, content: str) -> str:
        return f"""
        <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{int(time.time())}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{content}]]></Content>
        </xml>
        """

    @classmethod
    def build_image_reply(cls, to_user: str, from_user: str, media_id: str) -> str:
        return f"""
        <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{int(time.time())}</CreateTime>
            <MsgType><![CDATA[image]]></MsgType>
            <Image>
                <MediaId><![CDATA[{media_id}]]></MediaId>
            </Image>
        </xml>
        """


__all__ = ["WeChatService"]
