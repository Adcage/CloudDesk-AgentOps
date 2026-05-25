import pytest

from app.guardrails.approval_policy import check_approval_required


@pytest.mark.parametrize(
    ("action", "amount", "risk_level", "expected_required", "expected_level"),
    [
        ("refund", 30, "low", False, None),
        ("refund", 30, "high", True, "manager"),
        ("refund", 80, "low", True, "regular"),
        ("refund", 250, "high", True, "director"),
        ("modify_plan", 0, "low", True, "regular"),
        ("close_account", 0, "medium", True, "manager"),
        ("send_email", 0, "low", False, None),
        ("unknown_action", 100, "low", False, None),
    ],
)
def test_check_approval_required_uses_amount_risk_matrix(
    action,
    amount,
    risk_level,
    expected_required,
    expected_level,
):
    decision = check_approval_required(action, amount, risk_level)

    assert decision.required is expected_required
    assert getattr(decision, "level", None) == expected_level
