from fastapi import APIRouter, Depends, UploadFile, Query
from sqlalchemy.orm import Session

from app.core.response import success_payload
from app.db.session import get_db
from app.modules.documents.service import DocumentService
from app.rag.retriever import retrieve

router = APIRouter()


@router.post("/documents/ingest")
async def ingest_document_endpoint(
    title: str,
    file: UploadFile,
    doc_type: str = "policy",
    db: Session = Depends(get_db),
):
    content = (await file.read()).decode("utf-8")
    service = DocumentService(db)
    document_id = await service.ingest(title=title, content=content, doc_type=doc_type)
    return success_payload({"document_id": document_id, "title": title})


@router.get("/documents")
def list_documents_endpoint(
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    documents = service.list_documents()
    return success_payload(documents)


@router.get("/documents/search")
async def search_documents_endpoint(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20),
):
    results = await retrieve(query=query, top_k=top_k)
    return success_payload(results)