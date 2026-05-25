from __future__ import annotations

from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal
from app.rag.embeddings import get_embeddings
from app.rag.fusion import reciprocal_rank_fusion
from app.rag.keyword_search import keyword_search
from app.rag.reranker import get_reranker


async def retrieve(
    query: str,
    top_k: int | None = None,
    use_hybrid: bool = True,
    use_rerank: bool = True,
) -> list[dict]:
    if top_k is None:
        top_k = settings.rag_top_k

    vector_top_k = (
        max(top_k * 2, 20)
        if use_hybrid and use_rerank
        else (max(top_k, 20) if use_rerank else top_k)
    )

    embeddings_model = get_embeddings()
    query_embedding = embeddings_model.embed_query(query)

    db = SessionLocal()
    try:
        sql = text("""
            SELECT dc.chunk_id, dc.chunk_text, dc.document_id, dc.metadata,
                   d.title AS source_title
            FROM agent.document_chunks dc
            JOIN agent.documents d ON dc.document_id = d.document_id
            ORDER BY dc.embedding <=> :embedding
            LIMIT :limit
        """)
        rows = db.execute(
            sql,
            {"embedding": str(query_embedding), "limit": vector_top_k},
        ).fetchall()

        vector_results = []
        for row in rows:
            vector_results.append({
                "chunk_id": row[0],
                "text": row[1],
                "document_id": row[2],
                "metadata": row[3],
                "source": row[4],
            })

        if use_hybrid:
            kw_top_k = top_k * 2
            kw_results = await keyword_search(query, top_k=kw_top_k)

            if kw_results:
                results = reciprocal_rank_fusion(
                    vector_results,
                    kw_results,
                    k=60,
                    top_n=top_k * 2 if use_rerank else top_k,
                )
            else:
                results = vector_results
        else:
            results = vector_results

        if use_rerank and len(results) > top_k:
            reranker = get_reranker()
            ranked = await reranker.rerank(
                query,
                [item["text"] for item in results],
                top_n=top_k,
            )
            reranked_results = []
            for r_item in ranked:
                original_idx = r_item.get("original_index", 0)
                if 0 <= original_idx < len(results):
                    reranked_results.append({
                        **results[original_idx],
                        "rerank_score": r_item.get("relevance_score", 0),
                        "reranked": True,
                    })
            return reranked_results

        return results[:top_k]
    finally:
        db.close()
