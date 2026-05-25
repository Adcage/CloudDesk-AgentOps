from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError
from app.core.response import success_payload
from app.db.session import get_db
from app.modules.traces.service import TraceService

router = APIRouter()


@router.get("/traces")
def list_traces(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = TraceService(db)
    result = service.list_traces(page=page, page_size=page_size)
    return success_payload(result)


@router.get("/traces/{trace_id}")
def get_trace_detail(
    trace_id: str,
    db: Session = Depends(get_db),
):
    service = TraceService(db)
    result = service.get_trace_detail(trace_id)
    if not result:
        raise BusinessError("Trace not found", status_code=404)
    return success_payload(result.model_dump())