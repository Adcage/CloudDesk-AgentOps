from dataclasses import dataclass


HIGH_RISK_ACTIONS: set[str] = {
    "execute_refund",
    "close_account",
    "modify_plan",
    "delete_data",
}

REFUND_APPROVAL_THRESHOLD = 100.0


@dataclass(frozen=True)
class ApprovalDecision:
    required: bool
    level: str | None = None
    reason: str | None = None


APPROVAL_MATRIX = {
    "refund": {
        (0, 50): {
            "low": ApprovalDecision(False, None, "low_amount_refund"),
            "medium": ApprovalDecision(False, None, "low_amount_refund"),
            "high": ApprovalDecision(True, "manager", "high_risk_refund"),
        },
        (50, 200): {
            "low": ApprovalDecision(True, "regular", "medium_amount_refund"),
            "medium": ApprovalDecision(True, "regular", "medium_amount_refund"),
            "high": ApprovalDecision(True, "manager", "high_risk_refund"),
        },
        (200, None): {
            "low": ApprovalDecision(True, "manager", "high_amount_refund"),
            "medium": ApprovalDecision(True, "manager", "high_amount_refund"),
            "high": ApprovalDecision(True, "director", "high_amount_high_risk_refund"),
        },
    },
    "modify_plan": {
        (0, None): {
            "low": ApprovalDecision(True, "regular", "modify_plan_requires_approval"),
            "medium": ApprovalDecision(True, "manager", "modify_plan_medium_risk"),
            "high": ApprovalDecision(True, "director", "modify_plan_high_risk"),
        },
    },
    "close_account": {
        (0, None): {
            "low": ApprovalDecision(True, "manager", "close_account_requires_manager"),
            "medium": ApprovalDecision(True, "manager", "close_account_requires_manager"),
            "high": ApprovalDecision(True, "director", "close_account_high_risk"),
        },
    },
    "send_email": {
        (0, 200): {
            "low": ApprovalDecision(False, None, "low_risk_email"),
            "medium": ApprovalDecision(False, None, "low_risk_email"),
            "high": ApprovalDecision(False, None, "low_risk_email"),
        },
        (200, None): {
            "low": ApprovalDecision(False, None, "high_amount_email_low_risk"),
            "medium": ApprovalDecision(True, "regular", "high_amount_email"),
            "high": ApprovalDecision(True, "regular", "high_amount_email"),
        },
    },
}


def check_approval_required(action: str, amount: float | None = None, risk_level: str = "low") -> ApprovalDecision:
    normalized_action = (action or "").lower().replace("_request", "")
    normalized_risk = (risk_level or "low").lower()
    amount_value = float(amount or 0)

    rules = APPROVAL_MATRIX.get(normalized_action)
    if not rules:
        return ApprovalDecision(False, None, f"unknown_action:{normalized_action}")

    for (lower, upper), risk_rules in rules.items():
        if amount_value >= lower and (upper is None or amount_value < upper):
            return risk_rules.get(normalized_risk, risk_rules.get("low", ApprovalDecision(False, None, "fallback_low")))

    return ApprovalDecision(False, None, f"no_matching_threshold:{normalized_action}")
