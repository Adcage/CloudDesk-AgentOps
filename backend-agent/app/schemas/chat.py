from pydantic import BaseModel


class ChatRequest(BaseModel):
    trace_id: str
    conversation_id: str
    user_id: str
    user_role: str
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    selected_agent: str
    citations: list[str] = []
    tool_calls: list[str] = []
    tool_call_results: list[dict] = []
    citation_details: list[dict[str, str]] = []
    approval_required: bool = False
    approval_id: str | None = None
    trace_id: str
    customer_context: dict | None = None
    order_context: dict | None = None
    intent: str = ""
    risk_level: str = "low"
    entities: dict | None = None
    workflow_steps: list[dict] = []
