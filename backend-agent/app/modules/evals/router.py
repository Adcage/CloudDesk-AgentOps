from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import success_payload
from app.db.session import get_db
from app.modules.evals.service import EvalService

router = APIRouter()


@router.post("/evals/run")
async def run_evals_endpoint(
    body: dict | None = None,
    db: Session = Depends(get_db),
):
    service = EvalService(db)
    case_ids = body.get("case_ids") if isinstance(body, dict) else None
    results = await service.run_evaluation(case_ids=case_ids)
    return success_payload(results)


@router.get("/evals/results")
async def list_eval_results_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = EvalService(db)
    return success_payload(await service.list_results(page=page, page_size=page_size))


@router.get("/evals/summary")
async def eval_summary_endpoint(db: Session = Depends(get_db)):
    service = EvalService(db)
    return success_payload(await service.get_summary())


@router.get("/evals/results/by-version")
async def eval_by_version_endpoint(db: Session = Depends(get_db)):
    service = EvalService(db)
    return success_payload(await service.group_by_version())
