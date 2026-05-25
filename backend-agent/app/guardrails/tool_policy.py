from pydantic import BaseModel, ConfigDict, Field, ValidationError


AGENT_TOOL_WHITELIST: dict[str, set[str]] = {
    "billing_agent": {
        "get_customer_profile",
        "get_customer_history",
        "get_order_status",
        "create_ticket",
        "create_refund_approval",
        "search_knowledge_base",
    },
    "account_agent": {
        "get_customer_profile",
        "create_ticket",
        "search_knowledge_base",
    },
    "approval_agent": {
        "create_refund_approval",
        "search_knowledge_base",
    },
}


class _ToolInputModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class GetCustomerProfileInput(_ToolInputModel):
    customer_id: str


class GetCustomerHistoryInput(_ToolInputModel):
    customer_id: str


class GetOrderStatusInput(_ToolInputModel):
    order_id: str


class CreateTicketInput(_ToolInputModel):
    customer_id: str
    subject: str
    category: str = "general"
    priority: str = "medium"
    agent_summary: str | None = None
    trace_id: str | None = None


class CreateRefundApprovalInput(_ToolInputModel):
    customer_id: str
    order_id: str
    amount: float = Field(gt=0)
    reason: str
    action: str | None = None
    trace_id: str | None = None


TOOL_SCHEMAS: dict[str, type[_ToolInputModel]] = {
    "get_customer_profile": GetCustomerProfileInput,
    "get_customer_history": GetCustomerHistoryInput,
    "get_order_status": GetOrderStatusInput,
    "create_ticket": CreateTicketInput,
    "create_refund_approval": CreateRefundApprovalInput,
}


def validate_tool_access(agent_name: str, tool_name: str) -> bool:
    allowed = AGENT_TOOL_WHITELIST.get(agent_name, set())
    return tool_name in allowed


def validate_tool_input(tool_name: str, tool_input: dict) -> tuple[bool, str | None, dict | None]:
    schema = TOOL_SCHEMAS.get(tool_name)
    if schema is None:
        return True, None, tool_input

    try:
        validated = schema(**tool_input)
    except ValidationError as exc:
        return False, str(exc), None

    return True, None, validated.model_dump(exclude_none=True)
