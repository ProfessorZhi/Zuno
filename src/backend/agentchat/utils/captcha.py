from agentchat.services.redis import redis_client
from agentchat.utils.runtime_observability import RedisKeys


async def verify_captcha(captcha: str, captcha_key: str):
    # check captcha
    redis_key = RedisKeys.captcha(captcha_key)
    captcha_value = redis_client.get(redis_key) or redis_client.get(captcha_key)
    if captcha_value:
        redis_client.delete(redis_key)
        redis_client.delete(captcha_key)
        return captcha_value.lower() == captcha.lower()
    else:
        return False
