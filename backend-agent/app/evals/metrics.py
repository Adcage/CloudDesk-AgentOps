def compute_metrics(results: list[dict]) -> dict:
    if not results:
        return {
            "intent_accuracy": 0.0,
            "retrieval_hit_rate": 0.0,
            "tool_call_accuracy": 0.0,
            "approval_routing_accuracy": 0.0,
            "task_success_rate": 0.0,
            "avg_latency_ms": 0.0,
            "avg_cost": 0.0,
            "total_cases": 0,
            "error_count": 0,
        }

    total = len(results)
    error_count = sum(1 for r in results if "error" in r)
    valid_results = [r for r in results if "error" not in r]

    if not valid_results:
        return {
            "intent_accuracy": 0.0,
            "retrieval_hit_rate": 0.0,
            "tool_call_accuracy": 0.0,
            "approval_routing_accuracy": 0.0,
            "task_success_rate": 0.0,
            "avg_latency_ms": 0.0,
            "avg_cost": 0.0,
            "total_cases": total,
            "error_count": error_count,
        }

    valid_count = len(valid_results)

    intent_correct = sum(
        1 for r in valid_results
        if r.get("selected_agent", "") != "error"
    )
    retrieval_hits = sum(1 for r in valid_results if r.get("retrieval_hit", False))
    tool_call_correct = sum(
        1 for r in valid_results if r.get("tool_call_correct", False)
    )
    approval_routing_correct = sum(
        1 for r in valid_results if r.get("approval_routing_correct", False)
    )
    task_success = sum(1 for r in valid_results if r.get("task_success", False))

    total_latency = sum(r.get("latency_ms", 0) for r in valid_results)
    total_cost = sum(r.get("estimated_cost", 0) for r in valid_results)

    approval_cases = [
        r for r in valid_results
        if r.get("intent") in ("approval_needed", "refund_request", "close_account", "modify_plan")
    ]
    approval_count = len(approval_cases) if approval_cases else valid_count

    return {
        "intent_accuracy": round(intent_correct / valid_count, 4) if valid_count else 0.0,
        "retrieval_hit_rate": round(retrieval_hits / valid_count, 4) if valid_count else 0.0,
        "tool_call_accuracy": round(tool_call_correct / valid_count, 4) if valid_count else 0.0,
        "approval_routing_accuracy": round(approval_routing_correct / approval_count, 4) if approval_count else 0.0,
        "task_success_rate": round(task_success / valid_count, 4) if valid_count else 0.0,
        "avg_latency_ms": round(total_latency / valid_count, 2) if valid_count else 0.0,
        "avg_cost": round(total_cost / valid_count, 6) if valid_count else 0.0,
        "total_cases": total,
        "error_count": error_count,
        "breakdown": {
            "policy_qa": _compute_category_metrics(
                [r for r in valid_results if r.get("intent") == "answer_policy"]
            ),
            "login_issue": _compute_category_metrics(
                [r for r in valid_results if r.get("intent") == "answer_troubleshooting"]
            ),
            "billing_issue": _compute_category_metrics(
                [r for r in valid_results if r.get("intent") == "billing_issue"]
            ),
            "refund_request": _compute_category_metrics(
                [r for r in valid_results if r.get("intent") == "refund_request"]
            ),
            "ticket_create": _compute_category_metrics(
                [r for r in valid_results if r.get("intent") == "ticket_create"]
            ),
            "high_risk": _compute_category_metrics(
                [r for r in valid_results if r.get("risk_level") == "high"]
            ),
        },
    }


def _compute_category_metrics(cases: list[dict]) -> dict:
    if not cases:
        return {
            "retrieval_hit_rate": 0.0,
            "tool_call_accuracy": 0.0,
            "task_success_rate": 0.0,
            "count": 0,
        }

    count = len(cases)
    return {
        "retrieval_hit_rate": round(
            sum(1 for c in cases if c.get("retrieval_hit", False)) / count, 4
        ),
        "tool_call_accuracy": round(
            sum(1 for c in cases if c.get("tool_call_correct", False)) / count, 4
        ),
        "task_success_rate": round(
            sum(1 for c in cases if c.get("task_success", False)) / count, 4
        ),
        "count": count,
    }