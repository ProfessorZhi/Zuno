from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CompletionReq(BaseModel):
    user_input: str = Field(description="用户输入的问题")
    dialog_id: str = Field(description="对话 ID")
    file_url: Optional[str] = Field(None, description="对话上传文件的对象存储链接")
    multi_agent_enabled: bool = Field(False, description="是否显式启用 multi-agent runtime")


class ToolCall(BaseModel):
    tool_name: str = Field(..., description="工具名称，例如 get_current_time 或 get_weather")
    tool_args: Any = Field(..., description="工具参数，可为字符串、字典或空值")
    message: str = Field(..., description="该工具调用的说明信息")


StepTools = List[ToolCall]


class PlanToolFlow(BaseModel):
    root: Dict[str, StepTools] = Field(
        ...,
        description="工具调用流程，键为步骤名，值为该步骤的工具调用列表",
    )

    def dict(self, **kwargs) -> Dict[str, Any]:
        return super().dict(**kwargs)

    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)


__all__ = [
    "CompletionReq",
    "PlanToolFlow",
    "StepTools",
    "ToolCall",
]
