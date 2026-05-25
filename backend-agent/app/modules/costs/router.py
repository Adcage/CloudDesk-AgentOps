"""成本查询 API 路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import success_payload
from app.db.session import get_db
from app.modules.costs.service import CostService

router = APIRouter()


@router.get("/costs/today")
async def costs_today(db: Session = Depends(get_db)):
    service = CostService(db)
    return success_payload(service.get_summary(days=1))


@router.get("/costs/by-agent")
async def costs_by_agent(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    service = CostService(db)
    summary = service.get_summary(days=days)
    return success_payload({"by_agent": summary["by_agent"], "days": days})


@router.get("/costs/history")
async def costs_history(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    service = CostService(db)
    trend = service.get_trend(days=days)
    return success_payload({"daily_trend": trend, "days": days})
