from pathlib import Path


def test_auth_service_does_not_depend_on_werkzeug():
    service_file = Path("app/modules/auth/service.py")
    source = service_file.read_text(encoding="utf-8")

    assert "from werkzeug.security import" not in source
