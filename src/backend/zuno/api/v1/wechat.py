import asyncio

from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from loguru import logger

from zuno.api.services.wechat import WeChatService
from zuno.settings import app_settings

router = APIRouter(tags=["Wechat"])


@router.get("/wechat", response_class=PlainTextResponse)
async def wechat_verify(
    request: Request,
    signature: str,
    timestamp: str,
    nonce: str,
    echostr: str,
):
    _ = request
    wechat_conf = app_settings.wechat_config
    if WeChatService.check_signature(wechat_conf.get("token"), signature, timestamp, nonce):
        return echostr
    return "Signature verification failed"


@router.post("/wechat")
async def handle_wechat_message(request: Request):
    body = await request.body()
    xml_str = body.decode("utf-8")
    try:
        data = WeChatService.parse_wechat_xml(xml_str)
    except Exception as err:
        logger.error(f"Error parsing XML: {err}")
        return ""

    msg_type = data.get("msg_type")
    from_user = data.get("from_user")
    to_user = data.get("to_user")
    content = data.get("content")
    event = data.get("event")

    if msg_type == "event":
        if event == "subscribe":
            reply_xml = WeChatService.build_text_reply(to_user, from_user, "Welcome to Zuno.")
        elif event == "unsubscribe":
            reply_xml = WeChatService.build_text_reply(to_user, from_user, "Goodbye for now.")
        else:
            reply_xml = WeChatService.build_text_reply(to_user, from_user, "success")
        return reply_xml

    if msg_type != "text":
        reply_xml = WeChatService.build_text_reply(
            to_user,
            from_user,
            "Only text messages are supported right now.",
        )
        return reply_xml

    if not content:
        reply_xml = WeChatService.build_text_reply(
            to_user,
            from_user,
            "The message content was empty.",
        )
        return reply_xml

    logger.info(f"received wechat message: {content}")

    if response := await WeChatService.process_user_keyword(content, from_user, to_user):
        return Response(content=response, media_type="text/xml; charset=utf-8")

    cached_reply = WeChatService.get_cached_reply(from_user, content)
    if cached_reply:
        model_reply = cached_reply.get("content")
    else:
        history_messages = await WeChatService.build_history_messages(from_user)

        try:
            timeout_event = asyncio.Event()

            async def run_wechat_agent():
                response = await WeChatService.invoke_wechat_agent(
                    from_user=from_user,
                    to_user=to_user,
                    content=content,
                    history_messages=history_messages,
                )
                if timeout_event.is_set():
                    WeChatService.cache_reply(
                        from_user=from_user,
                        content=content,
                        reply=response.content,
                    )
                    logger.info(f"background task completed and saved to Redis: {response.content[:50]}...")
                return response

            run_wechat_agent_task = asyncio.create_task(run_wechat_agent())
            shield_wechat_agent_task = asyncio.shield(run_wechat_agent_task)

            response = await asyncio.wait_for(shield_wechat_agent_task, 4.5)
            model_reply = response.content
        except asyncio.TimeoutError:
            timeout_event.set()
            logger.warning("Wechat agent task timeout after 4.5s, running...")
            model_reply = "The assistant is still working. Please ask the same question again in a moment."
        except Exception as err:
            logger.error(f"failed to call wechat chat agent: {err}")
            model_reply = "The assistant could not reply right now. Please try again later."

    reply_xml = WeChatService.build_text_reply(to_user, from_user, model_reply)
    logger.info(f"returning wechat XML: {reply_xml}")
    return Response(content=reply_xml, media_type="text/xml; charset=utf-8")


__all__ = ["handle_wechat_message", "router", "wechat_verify"]
