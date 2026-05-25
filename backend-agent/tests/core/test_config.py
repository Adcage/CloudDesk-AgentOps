from app.core.config import Settings


def test_settings_read_from_env(monkeypatch):
    monkeypatch.setenv("APP_NAME", "demo-app")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.app_name == "demo-app"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"


def test_storage_root_default():
    s = Settings()
    assert s.storage_root == "instance/storage"
