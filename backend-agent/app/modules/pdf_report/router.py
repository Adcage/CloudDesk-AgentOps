"""PDF报告路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_payload
from app.db.session import get_db
from app.modules.pdf_report.service import PdfReportService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> PdfReportService:
    return PdfReportService(db)


@router.post("/generate")
def create_pdf_job_endpoint(
    payload: dict,
    service: PdfReportService = Depends(get_service),
):
    result = service.create_pdf_job(payload)
    return success_payload(result)


@router.get("/jobs/{job_id}")
def get_pdf_job_endpoint(
    job_id: int,
    service: PdfReportService = Depends(get_service),
):
    result = service.get_pdf_job(job_id)
    return success_payload(result)
