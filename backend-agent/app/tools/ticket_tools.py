from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.tools.registry import call_internal


class CreateTicketInput(BaseModel):
    customer_id: str = Field(description="客户ID")
    subject: str = Field(description="工单主题")
    category: str = Field(description="工单分类")
    priority: str = Field(default="medium", description="优先级: low/medium/high")
    agent_summary: str = Field(description="Agent 生成的工单摘要")
    trace_id: str = Field(default="", description="追踪ID")


async def _create_ticket(
    customer_id: str,
    subject: str,
    category: str,
    priority: str = "medium",
    agent_summary: str = "",
    trace_id: str = "",
) -> dict:
    payload = {
        "customer_id": customer_id,
        "subject": subject,
        "category": category,
        "priority": priority,
        "agent_summary": agent_summary,
        "trace_id": trace_id,
    }
    return await call_internal("POST", "/internal/tickets", json=payload, trace_id=trace_id)


create_ticket = StructuredTool.from_function(
    coroutine=_create_ticket,
    name="create_ticket",
    description="为客户创建工单，需要提供客户ID、主题、分类、优先级和摘要",
    args_schema=CreateTicketInput,
)