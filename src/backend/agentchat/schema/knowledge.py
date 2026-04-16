from typing import Optional

from pydantic import BaseModel, Field


class KnowledgeCreateRequest(BaseModel):
    knowledge_name: str = Field(description="knowledge name", min_length=2, max_length=10)
    knowledge_desc: Optional[str] = Field(
        description="knowledge description",
        min_length=10,
        max_length=200,
        default=None,
    )
    default_retrieval_mode: str = Field(default="rag", description="default retrieval mode")


class KnowledgeUpdateRequest(BaseModel):
    knowledge_id: str = Field(description="knowledge id")
    knowledge_name: Optional[str] = Field(default=None, description="knowledge name", min_length=2, max_length=10)
    knowledge_desc: Optional[str] = Field(
        default=None,
        description="knowledge description",
        min_length=10,
        max_length=200,
    )
    default_retrieval_mode: Optional[str] = Field(default=None, description="default retrieval mode")
