import json

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from agentchat.core.models.manager import ModelManager
from agentchat.prompts.rewrite import system_query_rewrite, user_query_write


class QueryRewrite:
    def _get_client(self):
        return ModelManager.get_conversation_model()

    async def rewrite(self, user_input):
        rewrite_prompt = user_query_write.format(user_input=user_input)
        response = self._get_client().invoke(
            [
                SystemMessage(content=system_query_rewrite),
                HumanMessage(content=rewrite_prompt),
            ]
        )
        cleaned_response = response.content.replace("```json", "")
        cleaned_response = cleaned_response.replace("```", "").strip()

        try:
            result = json.loads(cleaned_response)
            if isinstance(result, list):
                normalized = [item for item in result if isinstance(item, str) and item.strip()]
                return normalized or [user_input]
            if isinstance(result, dict):
                variations = result.get("variations")
                if isinstance(variations, list):
                    normalized = [item for item in variations if isinstance(item, str) and item.strip()]
                    return normalized or [user_input]
            return [user_input]
        except Exception as e:
            logger.info(f"json loads error: {e}")
            return [user_input]


query_rewriter = QueryRewrite()
