"""PDF报告服务"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessError
from app.modules.pdf_report.repository import PdfJobRepository


def _storage_root() -> Path:
    root = Path(settings.storage_root)
    if not root.is_absolute():
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def _render_pdf_bytes(template_code: str, payload: dict) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise BusinessError("pdf generation requires reportlab", status_code=500) from exc

    buffer = BytesIO()
    report = canvas.Canvas(buffer, pagesize=A4)
    font_name = settings.pdf_default_font
    report.setFont(font_name, 12)
    report.drawString(50, 800, f"Template: {template_code}")

    y_axis = 780
    for key, value in payload.items():
        report.drawString(50, y_axis, f"{key}: {value}")
        y_axis -= 20

    report.showPage()
    report.save()
    return buffer.getvalue()


class PdfReportService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PdfJobRepository(db)

    def create_pdf_job(self, payload: dict) -> dict:
        template_code = str(payload.get("template_code", "")).strip()
        if not template_code:
            raise BusinessError("template_code is required", status_code=400)

        job = self.repo.create_job(
            created_by="system",
            template_code=template_code,
            params_json=payload,
        )
        self.db.commit()

        # 同步生成 PDF
        try:
            content = _render_pdf_bytes(template_code, payload.get("payload", {}))
            file_name = f"pdf_report_{job.id}.pdf"
            target = _storage_root() / "pdf_reports" / file_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

            job.result_file_path = str(target)
            job.status = "SUCCESS"
        except Exception as e:
            job.status = "FAILED"
            job.error_message = str(e)

        self.db.commit()
        return {"job_id": job.id, "status": job.status}

    def get_pdf_job(self, job_id: int) -> dict:
        job = self.repo.get_by_id(job_id)
        if job is None:
            raise BusinessError("job not found", status_code=404)

        return {
            "job_id": job.id,
            "status": job.status,
            "error_message": job.error_message,
        }
