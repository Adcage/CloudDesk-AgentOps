import pytest

pytestmark = pytest.mark.skip(reason="Requires running PostgreSQL instance")

from sqlalchemy import text

from app.db.session import SessionLocal


def test_db_session_can_execute_sql():
    with SessionLocal() as db:
        result = db.execute(text("SELECT 1")).scalar_one()
    assert result == 1
