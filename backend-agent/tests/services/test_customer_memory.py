import pytest

from app.memory.customer_memory import build_memory_summary_text, get_memory_summary


def test_build_memory_summary_text_formats_memory_payload():
    summary = build_memory_summary_text(
        customer_id="C001",
        latest_summary="过去90天有2次退款，风险中等。",
        session_count=3,
        message_count=12,
    )

    assert "C001" in summary
    assert "2次退款" in summary
    assert "3" in summary


@pytest.mark.asyncio
async def test_get_memory_summary_returns_empty_when_no_memory(db_session):
    result = await get_memory_summary("C404", db_session)

    assert result == ""
