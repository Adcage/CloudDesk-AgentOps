import asyncio

from app.observability.trace_logger import TraceLogger


class DummySession:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None


def test_trace_logger_save_uses_selected_agent_arg():
    logger = TraceLogger(trace_id="TR_TEST_AGENT", session_id="sess_test")
    db = DummySession()

    asyncio.run(logger.save(
        db=db,
        final_answer="ok",
        model_used="deepseek-v4-pro",
        token_usage=0,
        intent="refund_request",
        user_query="test",
        risk_level="medium",
        entities={},
        approval_required=True,
        approval_id="A1",
        handoff_count=1,
        citations=[],
        workflow_steps=[],
        prompt_version="v1",
        selected_agent="approval_agent",
    ))

    trace = db.items[0]
    assert trace.selected_agent == "approval_agent"
