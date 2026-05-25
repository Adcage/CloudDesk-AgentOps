from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.tools.registry import call_internal


class CustomerIdInput(BaseModel):
    customer_id: str = Field(description="客户ID")


async def _get_customer_profile(customer_id: str) -> dict:
    return await call_internal("GET", f"/internal/customers/{customer_id}")


async def _get_customer_history(customer_id: str) -> dict:
    return await call_internal("GET", f"/internal/customers/{customer_id}/history")


get_customer_profile = StructuredTool.from_function(
    coroutine=_get_customer_profile,
    name="get_customer_profile",
    description="根据客户ID查询客户档案信息，包括姓名、邮箱、套餐、风险等级等",
    args_schema=CustomerIdInput,
)

get_customer_history = StructuredTool.from_function(
    coroutine=_get_customer_history,
    name="get_customer_history",
    description="根据客户ID查询客户历史记录，包括订单数、工单数、审批数等聚合信息",
    args_schema=CustomerIdInput,
)