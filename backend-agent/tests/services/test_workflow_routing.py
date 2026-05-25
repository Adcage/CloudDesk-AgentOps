import pytest

from app.workflow import graph as workflow_graph
from app.workflow.graph import need_approval


def test_need_approval_stops_after_approval_agent_runs():
    state = {
        "approval_required": True,
        "handoff_count": 0,
        "selected_agent": "approval_agent",
        "approval_id": "A100",
        "tool_calls": ["create_refund_approval"],
    }

    assert need_approval(state) == "generate_final_answer"


def test_need_approval_routes_to_approval_agent_before_it_runs():
    state = {
        "approval_required": True,
        "handoff_count": 0,
        "selected_agent": "billing_agent",
        "approval_id": None,
        "tool_calls": ["search_knowledge_base"],
    }

    assert need_approval(state) == "approval_agent"


def test_need_approval_routes_when_handoff_set_but_approval_not_created_yet():
    state = {
        "approval_required": True,
        "handoff_count": 1,
        "selected_agent": "approval_agent",
        "approval_id": None,
        "tool_calls": ["search_knowledge_base"],
    }

    assert need_approval(state) == "approval_agent"


@pytest.mark.asyncio
async def test_run_approval_marks_selected_agent(monkeypatch):
    class DummyApprovalAgent:
        async def run(self, **kwargs):
            return {
                "answer": "需要审批",
                "citations": [],
                "tool_call_results": [],
                "approval_required": True,
                "approval_id": "A100",
            }

    monkeypatch.setattr(workflow_graph, "ApprovalAgent", DummyApprovalAgent)

    result = await workflow_graph.run_approval(
        {
            "query": "退款200",
            "entities": {"customer_id": "C002", "order_id": "O1003", "amount": 200.0},
            "trace_id": "TR_X",
            "intent": "refund_request",
        }
    )

    assert result["selected_agent"] == "approval_agent"
