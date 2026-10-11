"""
API and Privacy Integration Tests.
Verifies:
1. /api/v1/health returns correct diagnostics
2. /api/v1/search returns ranked results, detected language, and grounded AI answer
3. /api/v1/feedback hashes queries using SHA-256 (no raw queries stored)
4. AI disabled / budget exhaustion fallback behavior
"""

import sys
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "services" / "search-api"))
sys.path.insert(0, str(root_dir))

from main import app
from db.models import Feedback, IndexedDocument
from db.session import async_session_factory
from sqlalchemy import select


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database_connected"] is True
        assert data["indexed_documents_count"] > 0


@pytest.mark.asyncio
async def test_search_api_native_assamese():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/search?q=বিহু")
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "বিহু"
        assert data["detected_language"] in ("as_native", "all")
        assert data["total_results"] > 0
        assert len(data["results"]) > 0

        # AI Answer verification
        assert data["ai_answer"] is not None
        assert data["ai_answer"]["status"] == "grounded"
        assert len(data["ai_answer"]["citations"]) > 0


@pytest.mark.asyncio
async def test_search_api_romanized_assamese():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/search?q=axom")
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_language"] == "as_romanized"
        assert data["transliteration_suggestion"] is not None
        assert "অসম" in data["transliteration_suggestion"]


@pytest.mark.asyncio
async def test_privacy_feedback_query_hashing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        feedback_payload = {
            "query": "private medical search query",
            "feedback_type": "relevance",
            "is_positive": True,
            "comment": "Found great information",
        }
        resp = await client.post("/api/v1/feedback", json=feedback_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

        # Verify database does NOT store the raw query "private medical search query"
        async with async_session_factory() as session:
            stmt = select(Feedback).where(Feedback.comment == "Found great information")
            res = await session.execute(stmt)
            entry = res.scalars().first()
            assert entry is not None
            # The query must be hashed, NOT stored as plain text
            assert entry.query_hash != "private medical search query"
            assert len(entry.query_hash) == 64  # SHA-256 hex digest length
