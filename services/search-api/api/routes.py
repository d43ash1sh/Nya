"""
API Routes for ঞ (Nya) Search.
Endpoints:
- GET /api/v1/search & POST /api/v1/search
- GET /api/v1/health
- POST /api/v1/feedback
- GET /api/v1/sources
"""

import time
import hashlib
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

logger = logging.getLogger("nya.api")

from db.session import get_db_session
from db.models import IndexedDocument, SourceRegistry, Feedback
from nlp.query_processor import QueryProcessor
from search.retrieval import RetrievalEngine
from ai.gateway import AIGateway
from ai.cost_guard import CostGuard
from packages.contracts.schema import (
    SearchResponse,
    SearchResultItem,
    SearchRequest,
    FeedbackRequest,
    FeedbackResponse,
    HealthStatus,
    LanguageType,
    DateFilter,
    SafeSearchLevel,
    SortOption,
)
from config import settings

router = APIRouter(prefix="/api/v1")

query_processor = QueryProcessor()
retrieval_engine = RetrievalEngine()
ai_gateway = AIGateway()
cost_guard = CostGuard()


@router.get("/health", response_model=HealthStatus)
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """System health check and diagnostic status."""
    db_ok = True
    doc_count = 0
    try:
        count_res = await session.execute(
            select(func.count(IndexedDocument.id)).where(IndexedDocument.is_removed == False)
        )
        doc_count = count_res.scalar() or 0
    except Exception:
        db_ok = False

    _, remaining_budget = await cost_guard.can_execute(session)

    return HealthStatus(
        status="ok" if db_ok else "degraded",
        version="0.1.0-beta",
        database_connected=db_ok,
        ai_provider=settings.AI_PROVIDER,
        ai_budget_remaining_usd=remaining_budget,
        indexed_documents_count=doc_count,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/search", response_model=SearchResponse)
async def search_get(
    q: str = Query(..., min_length=1, max_length=250, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Results per page"),
    language: LanguageType = Query(LanguageType.ALL, description="Language filter"),
    safe_search: SafeSearchLevel = Query(SafeSearchLevel.MODERATE, description="Safe Search level"),
    date_filter: DateFilter = Query(DateFilter.ALL, description="Publication date filter"),
    sort: SortOption = Query(SortOption.NEWEST, description="Sort order: newest (default) or relevance"),
    enable_ai: bool = Query(True, description="Generate grounded AI answer"),
    session: AsyncSession = Depends(get_db_session),
):
    """Execute search query via HTTP GET."""
    return await _execute_search(
        query=q,
        page=page,
        page_size=page_size,
        language=language,
        safe_search=safe_search,
        date_filter=date_filter,
        sort=sort,
        enable_ai=enable_ai,
        session=session,
    )


@router.post("/search", response_model=SearchResponse)
async def search_post(
    body: SearchRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute search query via HTTP POST."""
    return await _execute_search(
        query=body.query,
        page=body.page,
        page_size=body.page_size,
        language=body.language,
        safe_search=body.safe_search,
        date_filter=body.date_filter,
        sort=body.sort,
        enable_ai=body.enable_ai,
        session=session,
    )


def _format_timestamp(val: Any) -> Optional[str]:
    if not val:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


async def _execute_search(
    query: str,
    page: int,
    page_size: int,
    language: LanguageType,
    safe_search: SafeSearchLevel,
    date_filter: DateFilter,
    sort: SortOption,
    enable_ai: bool,
    session: AsyncSession,
) -> SearchResponse:
    start_time = time.time()

    # 1. Linguistic processing: Normalization, transliteration, script detection, temporal intent
    processed = query_processor.process(query)

    # 2. Retrieval & Ranking
    results, total_matches = await retrieval_engine.search(
        session=session,
        processed_query=processed,
        language_filter=language.value,
        date_filter=date_filter.value,
        sort=sort.value,
        page=page,
        page_size=page_size,
    )

    # 3. Grounded AI inference (if enabled and results found)
    req_id = f"nya-{uuid.uuid4().hex[:8]}"
    ai_answer = None
    if enable_ai and results:
        ai_answer = await ai_gateway.generate_grounded_answer(
            query=processed.normalized_query,
            retrieved_documents=results,
            session=session,
            language=processed.detected_language,
            request_id=req_id,
        )

    # 4. Check if whole index is empty or in cold-start
    empty_notice = None
    if total_matches == 0:
        count_res = await session.execute(select(func.count(IndexedDocument.id)))
        total_in_db = count_res.scalar() or 0
        if total_in_db == 0:
            empty_notice = (
                "The search index is currently being populated with permitted regional sources. "
                "No live documents have been indexed yet."
            )
        else:
            empty_notice = (
                f"No documents matched '{processed.normalized_query}'. "
                "Try searching in native Assamese script or broader keywords."
            )

    # 5. Freshness assessment: for time-sensitive or news queries, verify if genuinely fresh results exist
    has_fresh_results = True
    freshness_notice = None
    if processed.is_time_sensitive or processed.is_news_intent:
        now = datetime.now(timezone.utc)
        recent_threshold_days = 90
        has_recent = False
        for r in results:
            raw_pub = r.get("published_at") or r.get("published_date")
            if raw_pub:
                try:
                    dt = datetime.fromisoformat(str(raw_pub).replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if (now - dt).days <= recent_threshold_days or r.get("is_news"):
                        has_recent = True
                        break
                except Exception:
                    pass
        if not has_recent and total_matches > 0:
            has_fresh_results = False
            freshness_notice = (
                "No recent news found from verified sources for this topic. "
                "Showing relevant background information."
            )

    # 6. Formulate related query suggestions
    related_queries = []
    if processed.transliteration_suggestion:
        related_queries.append(processed.transliteration_suggestion)
    if processed.detected_language == "as_native":
        related_queries.append(f"{processed.normalized_query} বাতৰি")
        related_queries.append(f"{processed.normalized_query} তথ্য")
    elif processed.detected_language in ("as_romanized", "en"):
        related_queries.append(f"{processed.normalized_query} news")
        related_queries.append(f"{processed.normalized_query} Assam")

    # Map results to contract items
    result_items = [
        SearchResultItem(
            id=str(r["id"]),
            title=r["title"],
            url=r["url"],
            display_url=r.get("canonical_url") or r["url"],
            snippet=r["snippet"],
            language=r["language"],
            published_date=_format_timestamp(r.get("published_at") or r.get("published_date")),
            published_at=_format_timestamp(r.get("published_at") or r.get("published_date")),
            updated_at=_format_timestamp(r.get("updated_at")),
            crawled_at=_format_timestamp(r.get("crawled_at")),
            is_news=bool(r.get("is_news", False)),
            score=r["score"],
            source_name=r.get("source_name") or r.get("source_domain") or "Web",
            source_domain=r.get("source_domain") or "",
            is_authoritative=bool(r.get("is_authoritative", False)),
        )
        for r in results
    ]

    total_latency = round((time.time() - start_time) * 1000, 2)

    detected_lang_enum = (
        LanguageType(processed.detected_language)
        if processed.detected_language in [e.value for e in LanguageType]
        else LanguageType.ALL
    )

    return SearchResponse(
        query=query,
        normalized_query=processed.normalized_query,
        detected_language=detected_lang_enum,
        transliteration_suggestion=processed.transliteration_suggestion,
        spelling_suggestion=processed.spelling_suggestion,
        total_results=total_matches,
        page=page,
        page_size=page_size,
        latency_ms=total_latency,
        sort=sort,
        is_time_sensitive_query=processed.is_time_sensitive,
        has_fresh_results=has_fresh_results,
        freshness_notice=freshness_notice,
        results=result_items,
        ai_answer=ai_answer,
        related_queries=related_queries[:4],
        empty_index_notice=empty_notice,
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    body: FeedbackRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Submits user feedback with privacy-first query hashing.
    Raw queries are never stored in feedback records.
    """
    # Hash query to protect user search privacy
    query_hash = hashlib.sha256(body.query.strip().lower().encode("utf-8")).hexdigest()

    feedback_entry = Feedback(
        query_hash=query_hash,
        result_id=body.result_id,
        feedback_type=body.feedback_type,
        is_positive=body.is_positive,
        comment=body.comment,
    )
    session.add(feedback_entry)
    await session.commit()

    return FeedbackResponse(
        success=True,
        message="Thank you for helping improve Nya search quality.",
    )


@router.get("/sources")
async def list_sources(session: AsyncSession = Depends(get_db_session)):
    """List permitted sources in the registry."""
    stmt = select(SourceRegistry).order_by(SourceRegistry.name)
    res = await session.execute(stmt)
    sources = res.scalars().all()
    return [
        {
            "id": s.id,
            "domain": s.domain,
            "name": s.name,
            "base_url": s.base_url,
            "crawl_allowed": s.crawl_allowed,
            "license_info": s.license_info,
            "language_focus": s.language_focus,
            "is_authoritative": s.is_authoritative,
        }
        for s in sources
    ]
