from app.modules.evals.service import _tool_calls_match


def test_tool_match_allows_customer_history_as_order_context_substitute():
    assert _tool_calls_match(
        ["search_knowledge_base", "get_customer_profile", "get_customer_history"],
        ["get_customer_profile", "get_order_status", "search_knowledge_base"],
    ) is True


def test_tool_match_requires_create_ticket_when_expected():
    assert _tool_calls_match(
        ["search_knowledge_base"],
        ["search_knowledge_base", "create_ticket"],
    ) is False
