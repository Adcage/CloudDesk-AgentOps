"""表格数据任务模型"""

from typing import Any

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.models.base import Base
from app.models.mixins import TimestampMixin


class TabularJob(Base, TimestampMixin):
    __tablename__ = "tabular_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_type: Mapped[str] = mapped_column(String(16), nullable=False)  # import/export
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    created_by: Mapped[str] = mapped_column(String(64), nullable=False, default="system")
    params_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    summary_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    source_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    result_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
