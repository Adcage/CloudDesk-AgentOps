"""表格数据路由"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.response import success_payload
from app.db.session import get_db
from app.modules.tabular_data.service import TabularDataService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> TabularDataService:
    return TabularDataService(db)


@router.post("/import/preview")
async def import_preview_endpoint(
    file: UploadFile = File(...),
    service: TabularDataService = Depends(get_service),
):
    content = await file.read()
    result = service.preview_import(file.filename or "", content)
    return success_payload(result)


@router.post("/export")
def create_export_endpoint(
    payload: dict,
    service: TabularDataService = Depends(get_service),
):
    result = service.create_export_job(payload)
    return success_payload(result)


@router.get("/export/{job_id}")
def get_export_job_endpoint(
    job_id: int,
    service: TabularDataService = Depends(get_service),
):
    result = service.get_export_job(job_id)
    return success_payload(result)
