import pytest

from app.agents import billing as billing_module


@pytest.mark.asyncio
async def test_billing_agent_handoffs_instead_of_creating_approval(monkeypatch):
    approval_create_called = {"value": False}

    async def fake_retrieve(query: str):
        return [{"source": "refund_policy.md", "text": "policy"}]

    async def fake_customer(customer_id: str):
        return {"code": 0, "data": {"customerId": customer_id}}

    async def fake_order(order_id: str):
        return {"code": 0, "data": {"orderId": order_id, "amount": 200.0}}

    async def fake_create_approval(**kwargs):
        approval_create_called["value"] = True
        return {"code": 0, "data": {"approvalId": "A1"}}

    monkeypatch.setattr(billing_module, "retrieve", fake_retrieve)
    monkeypatch.setattr(billing_module, "_get_customer_profile", fake_customer)
    monkeypatch.setattr(billing_module, "_get_order_status", fake_order)
    monkeypatch.setattr(billing_module, "_create_refund_approval", fake_create_approval)

    agent = billing_module.BillingAgent()
    result = await agent.run(
        query="客户C002要求退款200，订单号O1003，需要审批吗？",
        entities={"customer_id": "C002", "order_id": "O1003", "amount": 200.0},
        trace_id="TR_BILLING_TEST",
    )

    assert result["approval_required"] is True
    assert result["approval_id"] is None
    assert result["handoff_to"] == "approval_agent"
    assert approval_create_called["value"] is False
