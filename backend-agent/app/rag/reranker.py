import os
from typing import Any

import httpx


class DashScopeReranker:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
        self.model = "gte-rerank"
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))
        return self._client

    async def rerank(self, query: str, documents: list[str], top_n: int = 5, timeout: float = 3.0) -> list[dict[str, Any]]:
        if not documents:
            return []
        if not self.api_key:
            return self._fallback(documents, top_n)

        payload = {
            "model": self.model,
            "input": {
                "query": query,
                "documents": [{"text": doc, "index": idx} for idx, doc in enumerate(documents)],
            },
            "parameters": {"top_n": top_n},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = await self._get_client().post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=httpx.Timeout(timeout),
            )
            if response.status_code != 200:
                return self._fallback(documents, top_n)

            results = response.json().get("output", {}).get("results", [])
            ranked = [
                {
                    "text": item.get("document", {}).get("text", ""),
                    "original_index": item.get("document", {}).get("index", 0),
                    "relevance_score": item.get("relevance_score", 0.0),
                }
                for item in results
            ]
            ranked.sort(key=lambda item: item["relevance_score"], reverse=True)
            return ranked[:top_n]
        except Exception:
            return self._fallback(documents, top_n)

    def _fallback(self, documents: list[str], top_n: int) -> list[dict[str, Any]]:
        return [
            {
                "text": document,
                "original_index": index,
                "relevance_score": 0.0,
                "fallback": True,
            }
            for index, document in enumerate(documents[:top_n])
        ]


_reranker_instance: DashScopeReranker | None = None


def get_reranker() -> DashScopeReranker:
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = DashScopeReranker()
    return _reranker_instance
