from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.tools.registry import call_internal


class OrderIdInput(BaseModel):
    order_id: str = Field(description="订单ID")


async def _get_order_status(order_id: str) -> dict:
    return await call_internal("GET", f"/internal/orders/{order_id}")


get_order_status = StructuredTool.from_function(
    coroutine=_get_order_status,
    name="get_order_status",
    description="根据订单ID查询订单状态、金额、问题类型等信息",
    args_schema=OrderIdInput,
)