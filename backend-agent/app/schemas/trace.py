from pydantic import BaseModel

from app.schemas.tool_calls import ToolCallRecord


class TraceStep(BaseModel):
    step: int
    agent: str
    action: str
    detail: dict | None = None


class TraceListItem(BaseModel):
    trace_id: str
    session_id: str = ""
    user_query: str = ""
    selected_agent: str = ""
    intent: str = ""
    risk_level: str = ""
    latency_ms: int = 0
    approval_required: bool = False
    created_at: str | None = None


class TraceDetail(BaseModel):
    trace_id: str
    session_id: str
    user_query: str
    selected_agent: str
    intent: str
    risk_level: str = ""
    entities: dict | None = None
    model_used: str
    tool_calls: list[ToolCallRecord] = []
    handoffs: list[dict] = []
    handoff_graph: dict | None = None
    approval_required: bool = False
    approval_id: str | None = None
    handoff_count: int = 0
    citations: list = []
    workflow_steps: list[dict] = []
    final_answer: str
    latency_ms: int
    token_usage: int
    estimated_cost: float
