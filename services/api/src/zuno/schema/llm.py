from pydantic import BaseModel


class LLMCreateReq(BaseModel):
    model: str
    api_key: str
    base_url: str
    llm_type: str = "LLM"
    provider: str = "OpenAI"
    model_slot: str | None = None


class LLMUpdateReq(BaseModel):
    llm_id: str
    model: str = None
    api_key: str = None
    base_url: str = None
    llm_type: str = None
    provider: str = None
    model_slot: str | None = None


class LLMDeleteReq(BaseModel):
    llm_id: str


class LLMSearchReq(BaseModel):
    llm_name: str


class LLMActivateReq(BaseModel):
    llm_id: str
    model_slot: str


__all__ = [
    "LLMActivateReq",
    "LLMCreateReq",
    "LLMDeleteReq",
    "LLMSearchReq",
    "LLMUpdateReq",
]
