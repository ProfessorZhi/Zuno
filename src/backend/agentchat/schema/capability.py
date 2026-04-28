from pydantic import BaseModel, Field


class CapabilitySearchReq(BaseModel):
    query: str = ""
    kind: str = ""
    limit: int = Field(default=8, ge=1, le=50)
