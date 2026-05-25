"""测试模块动态加载。"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_minimal_app_only_health():
    with patch("app.core.modules.ENABLED_MODULES", ("health",)):
        from app.main import create_app

        app = create_app()

        client = TestClient(app)

        # health 应该可访问
        resp = client.get("/health")
        assert resp.status_code == 200

        # auth 不应该存在
        resp = client.post("/auth/register", json={"account": "u", "password": "p"})
        assert resp.status_code == 404


def test_unknown_module_raises():
    with patch("app.core.modules.ENABLED_MODULES", ("health", "unknown_module")):
        from app.main import create_app

        with pytest.raises(RuntimeError, match="Unknown module"):
            create_app()
