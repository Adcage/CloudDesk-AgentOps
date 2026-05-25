from app.modules.evals.service import _is_case_successful, _normalize_expected_tools


def test_normalize_expected_tools_adds_search_tool_for_doc_expectation():
    tools = _normalize_expected_tools("get_customer_profile", "refund_policy.md")

    assert "get_customer_profile" in tools
    assert "search_knowledge_base" in tools


def test_policy_case_success_depends_on_retrieval_and_search_tool():
    assert _is_case_successful(
        expected_action="answer_policy",
        retrieval_hit=True,
        tool_call_correct=True,
        approval_routing_correct=True,
    ) is True


def test_refund_case_success_depends_on_tools_and_approval():
    assert _is_case_successful(
        expected_action="refund_request",
        retrieval_hit=False,
        tool_call_correct=True,
        approval_routing_correct=True,
    ) is True


def test_refund_case_fails_when_tools_missing():
    assert _is_case_successful(
        expected_action="refund_request",
        retrieval_hit=True,
        tool_call_correct=False,
        approval_routing_correct=True,
    ) is False
