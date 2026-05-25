"""表格数据仓储层"""

from sqlalchemy.orm import Session

from app.modules.tabular_data.models import TabularJob


class TabularJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, job_id: int) -> TabularJob | None:
        return self.db.get(TabularJob, job_id)

    def create_import_job(
        self,
        created_by: str,
        params_json: dict,
        source_file_path: str,
    ) -> TabularJob:
        job = TabularJob(
            job_type="import",
            status="PENDING",
            created_by=created_by,
            params_json=params_json,
            source_file_path=source_file_path,
        )
        self.db.add(job)
        return job

    def create_export_job(self, created_by: str, params_json: dict) -> TabularJob:
        job = TabularJob(
            job_type="export",
            status="PENDING",
            created_by=created_by,
            params_json=params_json,
        )
        self.db.add(job)
        return job
