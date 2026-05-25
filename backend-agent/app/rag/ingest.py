import uuid

from langchain_text_splitters import MarkdownHeaderTextSplitter

from app.db.session import SessionLocal
from app.db.models import Document, DocumentChunk
from app.rag.embeddings import get_embeddings


def _split_markdown(content: str) -> list[dict]:
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ])
    chunks = splitter.split_text(content)
    return [{"text": c.page_content, "metadata": c.metadata} for c in chunks]


async def ingest_document(title: str, content: str, doc_type: str = "policy") -> str:
    document_id = f"doc_{uuid.uuid4().hex[:12]}"

    chunks_data = _split_markdown(content)
    if not chunks_data:
        single_chunk = {"text": content, "metadata": {}}
        chunks_data = [single_chunk]

    embeddings_model = get_embeddings()
    texts = [c["text"] for c in chunks_data]
    embeddings = embeddings_model.embed_documents(texts)

    db = SessionLocal()
    try:
        document = Document(
            document_id=document_id,
            title=title,
            doc_type=doc_type,
        )
        db.add(document)

        for idx, (chunk_data, embedding) in enumerate(zip(chunks_data, embeddings)):
            chunk = DocumentChunk(
                chunk_id=f"chk_{uuid.uuid4().hex[:12]}",
                document_id=document_id,
                chunk_text=chunk_data["text"],
                chunk_index=idx,
                embedding=embedding,
                metadata_=chunk_data.get("metadata"),
            )
            db.add(chunk)

        db.commit()
        return document_id
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()