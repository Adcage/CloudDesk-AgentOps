from __future__ import annotations

import httpx

from app.core.config import settings


class DashScopeEmbeddings:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _embed(self, text: str) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": text,
        }
        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers=headers,
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        body = response.json()
        return body["data"][0]["embedding"]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]


def get_embeddings():
    if settings.embedding_api_key and settings.embedding_base_url:
        return DashScopeEmbeddings(
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url,
            model=settings.embedding_model,
        )
    from langchain_community.embeddings import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
