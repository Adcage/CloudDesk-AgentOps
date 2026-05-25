from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    trace_id: str = Field(description="追踪ID")
    conversation_id: str = Field(description="会话ID")
    user_id: str = Field(default="", description="用户ID")
    user_role: str = Field(default="support_agent", description="用户角色")
    message: str = Field(description="用户消息")


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    selected_agent: str = ""
    citations: list[str] = []
    tool_calls: list[str] = []
    tool_call_results: list[dict] = []
    citation_details: list[dict[str, str]] = []
    approval_required: bool = False
    approval_id: str | None = None
    trace_id: str
    customer_context: dict | None = None
    order_context: dict | None = None
