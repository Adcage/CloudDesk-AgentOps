"""模块注册系统测试"""

import pytest

from app.core.modules import (
    parse_enabled_modules,
    validate_enabled_modules,
)


def test_parse_enabled_modules_basic():
    result = parse_enabled_modules("health,auth")
    assert result == ["health", "auth"]


def test_parse_enabled_modules_with_spaces():
    result = parse_enabled_modules("health , auth , file_upload")
    assert result == ["health", "auth", "file_upload"]


def test_parse_enabled_modules_deduplicates():
    result = parse_enabled_modules("health,auth,health")
    assert result == ["health", "auth"]


def test_validate_unknown_module_raises():
    with pytest.raises(RuntimeError, match="Unknown module: 'unknown'"):
        validate_enabled_modules(["unknown"])


def test_validate_missing_dependency_raises():
    with pytest.raises(RuntimeError, match="depends on 'auth'"):
        validate_enabled_modules(["health", "wechat_mini_auth"])


def test_validate_with_satisfied_dependency():
    # 不应抛出异常
    validate_enabled_modules(["health", "auth", "wechat_mini_auth"])
