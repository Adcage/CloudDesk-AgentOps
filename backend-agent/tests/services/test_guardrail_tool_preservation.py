import pytest

from app.workflow.graph import check_guardrails


@pytest.mark.asyncio
async def test_check_guardrails_keeps_already_executed_tool_history():
    state = {
        "selected_agent": "approval_agent",
        "tool_calls": ["search_knowledge_base", "get_customer_profile", "get_order_status", "create_refund_approval"],
        "handoff_count": 1,
    }

    result = await check_guardrails(state)

    assert result["tool_calls"] == state["tool_calls"]
