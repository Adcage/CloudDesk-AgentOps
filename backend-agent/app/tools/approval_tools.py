from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.tools.registry import call_internal


class CreateRefundApprovalInput(BaseModel):
    customer_id: str = Field(description="客户ID")
    order_id: str = Field(description="订单ID")
    action: str = Field(description="审批动作类型，如 refund")
    amount: float = Field(description="退款金额")
    reason: str = Field(description="审批原因")
    trace_id: str = Field(default="", description="追踪ID")


async def _create_refund_approval(
    customer_id: str,
    order_id: str,
    action: str,
    amount: float,
    reason: str,
    trace_id: str = "",
) -> dict:
    payload = {
        "customer_id": customer_id,
        "order_id": order_id,
        "action": action,
        "amount": amount,
        "reason": reason,
        "trace_id": trace_id,
    }
    return await call_internal("POST", "/internal/approvals", json=payload, trace_id=trace_id)


create_refund_approval = StructuredTool.from_function(
    coroutine=_create_refund_approval,
    name="create_refund_approval",
    description="创建退款审批单，需要提供客户ID、订单ID、动作类型、退款金额和原因",
    args_schema=CreateRefundApprovalInput,
)