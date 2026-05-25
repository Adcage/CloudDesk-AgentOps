"""PDF报告仓储层"""

from sqlalchemy.orm import Session

from app.modules.pdf_report.models import PdfJob


class PdfJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, job_id: int) -> PdfJob | None:
        return self.db.get(PdfJob, job_id)

    def create_job(
        self,
        created_by: str,
        template_code: str,
        params_json: dict,
    ) -> PdfJob:
        job = PdfJob(
            template_code=template_code,
            status="PENDING",
            created_by=created_by,
            params_json=params_json,
        )
        self.db.add(job)
        return job
