"""测试时间戳混入类"""

from app.models.mixins import TimestampMixin


def test_timestamp_mixin_has_created_at():
    assert hasattr(TimestampMixin, "created_at")


def test_timestamp_mixin_has_updated_at():
    assert hasattr(TimestampMixin, "updated_at")
