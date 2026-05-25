"""成本追踪：多模型定价、持久化到 DB、聚合查询

模型定价单位：USD / 100万 token（input）或 USD / 100万 token（output）
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import func, select

MODEL_COSTS: dict[str, dict[str, float]] = {
    "gpt-4o-mini":       {"input": 0.15, "output": 0.60},
    "gpt-4o":            {"input": 2.50, "output": 10.00},
    "qwen-turbo":        {"input": 0.30, "output": 0.60},
    "qwen-plus":         {"input": 2.00, "output": 6.00},
    "deepseek-chat":     {"input": 0.14, "output": 0.28},
    "text-embedding-v3": {"input": 0.02, "output": 0.0},
    "text-embedding-v4": {"input": 0.02, "output": 0.0},
    "gte-rerank":        {"input": 20.00, "output": 0.0},
}

_DAILY_TOTAL_COST = 0.0


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    costs = MODEL_COSTS.get(model)
    if not costs:
        return 0.0
    input_cost = (input_tokens / 1_000_000) * costs["input"]
    output_cost = (output_tokens / 1_000_000) * costs["output"]
    return round(input_cost + output_cost, 6)


def track_cost(
    agent_name: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    trace_id: str = "",
    task_type: str = "generate",
) -> float:
    global _DAILY_TOTAL_COST

    estimated = estimate_cost(model, input_tokens, output_tokens)
    _DAILY_TOTAL_COST += estimated

    try:
        from app.db.models import AgentCostDetail
        from app.db.session import SessionLocal

        db = SessionLocal()
        try:
            cost_id = f"cost_{uuid.uuid4().hex[:12]}"
            record = AgentCostDetail(
                cost_id=cost_id,
                trace_id=trace_id,
                agent_name=agent_name,
                model_name=model,
                task_type=task_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=Decimal(str(estimated)),
            )
            db.add(record)
            db.commit()
        finally:
            db.close()
    except Exception:
        pass

    return estimated


def track_latency(model: str, latency_ms: int) -> None:
    from app.routing.model_router import get_router

    get_router().record_latency(model, latency_ms)


def get_daily_total() -> float:
    return _DAILY_TOTAL_COST


def get_cost_summary(db, days: int = 7) -> dict:
    from app.db.models import AgentCostDetail

    cutoff = func.now() - timedelta(days=days)

    total_stmt = select(
        func.coalesce(func.sum(AgentCostDetail.estimated_cost), 0)
    ).where(AgentCostDetail.created_at >= cutoff)
    total = db.execute(total_stmt).scalar() or 0

    agent_stmt = (
        select(
            AgentCostDetail.agent_name,
            func.sum(AgentCostDetail.estimated_cost).label("total_cost"),
        )
        .where(AgentCostDetail.created_at >= cutoff)
        .group_by(AgentCostDetail.agent_name)
        .order_by(func.sum(AgentCostDetail.estimated_cost).desc())
    )
    by_agent = [
        {"agent_name": row[0], "total_cost": float(row[1] or 0)}
        for row in db.execute(agent_stmt).fetchall()
    ]

    model_stmt = (
        select(
            AgentCostDetail.model_name,
            func.sum(AgentCostDetail.estimated_cost).label("total_cost"),
            func.count().label("call_count"),
            func.sum(AgentCostDetail.input_tokens).label("total_input"),
            func.sum(AgentCostDetail.output_tokens).label("total_output"),
        )
        .where(AgentCostDetail.created_at >= cutoff)
        .group_by(AgentCostDetail.model_name)
        .order_by(func.sum(AgentCostDetail.estimated_cost).desc())
    )
    by_model = [
        {
            "model_name": row[0],
            "total_cost": float(row[1] or 0),
            "call_count": int(row[2] or 0),
            "total_input_tokens": int(row[3] or 0),
            "total_output_tokens": int(row[4] or 0),
        }
        for row in db.execute(model_stmt).fetchall()
    ]

    return {
        "total_cost": float(total),
        "by_agent": by_agent,
        "by_model": by_model,
        "days": days,
    }


def get_daily_trend(db, days: int = 30) -> list[dict]:
    from app.db.models import AgentCostDetail

    cutoff = func.now() - timedelta(days=days)

    stmt = (
        select(
            func.date(AgentCostDetail.created_at).label("date"),
            func.sum(AgentCostDetail.estimated_cost).label("daily_cost"),
        )
        .where(AgentCostDetail.created_at >= cutoff)
        .group_by(func.date(AgentCostDetail.created_at))
        .order_by("date")
    )
    return [
        {"date": str(row[0]), "daily_cost": float(row[1] or 0)}
        for row in db.execute(stmt).fetchall()
    ]
