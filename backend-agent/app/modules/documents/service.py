import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document
from app.rag.ingest import ingest_document

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    async def ingest(self, title: str, content: str, doc_type: str = "policy") -> str:
        document_id = await ingest_document(title, content, doc_type)
        return document_id

    def list_documents(self) -> list[dict]:
        rows = self.db.execute(
            select(Document).order_by(Document.created_at.desc())
        ).scalars().all()

        return [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "version": doc.version,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
            }
            for doc in rows
        ]