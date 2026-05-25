from types import SimpleNamespace

from app.modules.traces.service import TraceService


def test_build_handoff_graph_returns_nodes_and_edges():
    service = TraceService(db=None)  # type: ignore[arg-type]
    handoffs = [
        SimpleNamespace(handoff_id="ho1", from_agent="supervisor_agent", to_agent="billing_agent", reason="route_billing"),
        SimpleNamespace(handoff_id="ho2", from_agent="billing_agent", to_agent="approval_agent", reason="need_approval"),
    ]

    graph = service._build_handoff_graph(handoffs)

    assert graph is not None
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2
    assert graph["edges"][0]["from"] == "supervisor_agent"
