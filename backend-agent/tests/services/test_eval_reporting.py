from app.modules.evals.service import _normalize_expected_tools


def test_normalize_expected_tools_preserves_existing_search_tool_once():
    tools = _normalize_expected_tools("search_knowledge_base,get_customer_profile", "refund_policy.md")

    assert tools.count("search_knowledge_base") == 1
