"""成本查询服务"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.observability.cost_tracker import get_cost_summary, get_daily_trend


class CostService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, days: int = 7) -> dict:
        return get_cost_summary(self.db, days=days)

    def get_trend(self, days: int = 30) -> list[dict]:
        return get_daily_trend(self.db, days=days)
