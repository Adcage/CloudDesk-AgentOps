"""PostgreSQL 全文检索（关键词通道）"""

from __future__ import annotations

from sqlalchemy import text

from app.db.session import SessionLocal


async def keyword_search(query: str, top_k: int = 20) -> list[dict]:
    if not query or not query.strip():
        return []

    safe_query = " | ".join(query.split())

    sql = text("""
        SELECT dc.chunk_id, dc.chunk_text, dc.document_id, dc.metadata,
               d.title AS source_title,
               ts_rank(dc.text_search, websearch_to_tsquery('simple', :query)) AS rank
        FROM agent.document_chunks dc
        JOIN agent.documents d ON dc.document_id = d.document_id
        WHERE dc.text_search @@ websearch_to_tsquery('simple', :query)
        ORDER BY rank DESC
        LIMIT :limit
    """)

    db = SessionLocal()
    try:
        rows = db.execute(
            sql,
            {"query": safe_query, "limit": top_k},
        ).fetchall()

        return [
            {
                "chunk_id": row[0],
                "text": row[1],
                "document_id": row[2],
                "metadata": row[3],
                "source": row[4],
                "keyword_score": float(row[5]),
            }
            for row in rows
        ]
    finally:
        db.close()
