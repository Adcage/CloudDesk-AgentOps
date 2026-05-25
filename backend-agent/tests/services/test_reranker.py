from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.reranker import DashScopeReranker


class TestDashScopeReranker:
    @pytest.fixture
    def reranker(self):
        return DashScopeReranker(api_key="test-key")

    @pytest.fixture
    def mock_api_response(self):
        return {
            "output": {
                "results": [
                    {
                        "document": {"text": "退款政策：重复扣费可退款", "index": 3},
                        "relevance_score": 0.95,
                    },
                    {
                        "document": {"text": "账单周期为每月1号", "index": 1},
                        "relevance_score": 0.72,
                    },
                    {
                        "document": {"text": "企业SLA为99.9%", "index": 0},
                        "relevance_score": 0.31,
                    },
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_rerank_returns_sorted_results(self, reranker, mock_api_response):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = mock_api_response

        with patch.object(reranker, "_get_client", return_value=MagicMock(post=AsyncMock(return_value=mock_response))):
            results = await reranker.rerank(
                "重复扣费怎么退款",
                ["企业SLA为99.9%", "账单周期为每月1号", "登录问题排查", "退款政策：重复扣费可退款"],
                top_n=3,
            )

        assert len(results) == 3
        assert results[0]["relevance_score"] >= results[1]["relevance_score"]
        assert "退款" in results[0]["text"]

    @pytest.mark.asyncio
    async def test_rerank_falls_back_when_request_fails(self, reranker):
        with patch.object(reranker, "_get_client", return_value=MagicMock(post=AsyncMock(side_effect=Exception("timeout")))):
            results = await reranker.rerank("退款", ["doc1", "doc2", "doc3"], top_n=2)

        assert len(results) == 2
        assert all(item.get("fallback") for item in results)
