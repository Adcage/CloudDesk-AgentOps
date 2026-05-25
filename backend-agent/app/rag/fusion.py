"""Reciprocal Rank Fusion (RRF) 融合算法"""

from __future__ import annotations


def reciprocal_rank_fusion(
    vector_results: list[dict],
    keyword_results: list[dict],
    k: int = 60,
    top_n: int = 5,
) -> list[dict]:
    scores: dict[str, dict] = {}

    for rank, item in enumerate(vector_results):
        key = str(item.get("chunk_id", ""))
        if not key:
            continue
        scores[key] = {
            **item,
            "rrf_score": 1.0 / (k + rank + 1),
        }

    for rank, item in enumerate(keyword_results):
        key = str(item.get("chunk_id", ""))
        if not key:
            continue
        if key in scores:
            scores[key]["rrf_score"] += 1.0 / (k + rank + 1)
        else:
            scores[key] = {
                **item,
                "rrf_score": 1.0 / (k + rank + 1),
            }

    merged = sorted(
        scores.values(),
        key=lambda x: float(x.get("rrf_score", 0)),
        reverse=True,
    )
    return merged[:top_n]
