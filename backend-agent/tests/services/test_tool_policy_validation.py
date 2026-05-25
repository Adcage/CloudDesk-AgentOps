from app.guardrails.tool_policy import validate_tool_access, validate_tool_input


def test_validate_tool_access_respects_agent_whitelist():
    assert validate_tool_access("billing_agent", "get_order_status") is True
    assert validate_tool_access("account_agent", "get_order_status") is False


def test_validate_tool_input_returns_cleaned_payload_for_valid_input():
    valid, error, cleaned = validate_tool_input(
        "create_refund_approval",
        {
            "customer_id": "C001",
            "order_id": "O1001",
            "amount": 199.0,
            "reason": "重复扣费",
            "action": "refund",
            "trace_id": "TR_1",
        },
    )

    assert valid is True
    assert error is None
    assert cleaned["amount"] == 199.0


def test_validate_tool_input_rejects_missing_required_fields():
    valid, error, cleaned = validate_tool_input(
        "create_refund_approval",
        {
            "customer_id": "C001",
            "amount": -1,
        },
    )

    assert valid is False
    assert error is not None
    assert cleaned is None
