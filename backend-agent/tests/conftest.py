import os
from unittest.mock import patch

os.environ["APP_ENV"] = "test"

_test_modules_patch = patch("app.core.modules.ENABLED_MODULES", ("health", "auth", "file_upload"))
_test_modules_patch.start()

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app

_test_modules_patch.stop()

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)

NON_AGENT_TABLES = [
    tbl for name, tbl in Base.metadata.tables.items()
    if not name.startswith("agent.")
]


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    for tbl in NON_AGENT_TABLES:
        tbl.create(bind=engine, checkfirst=True)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        for tbl in reversed(NON_AGENT_TABLES):
            tbl.drop(bind=engine, checkfirst=True)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    with patch("app.core.modules.ENABLED_MODULES", ("health", "auth", "file_upload")):
        app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
