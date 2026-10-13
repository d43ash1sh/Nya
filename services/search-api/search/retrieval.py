"""
Retrieval Engine for ঞ (Nya) Search.
Executes multi-source candidate retrieval:
1. Local permitted authoritative regional index (SQLite).
2. Live encyclopedic knowledge provider (Wikipedia MediaWiki API).
3. Privacy-conscious live web provider (DuckDuckGo Lite).

Applies:
- Deduplication via canonical URLs and content hashing.
- Multi-signal ranking (phrase matching, term frequency, script alignment, freshness).
- Domain diversity suppression.
- Honest, accurate pagination and non-fabricated result counting.
"""

import asyncio
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import IndexedDocument, SourceRegistry
from search.ranking import RankingEngine
from search.providers.wikipedia import WikipediaProvider
from search.providers.duckduckgo import DuckDuckGoProvider
from nlp.query_processor import ProcessedQuery


class RetrievalEngine:
    def __init__(self):
        self.ranker = RankingEngine()
        self.wiki_provider = WikipediaProvider(timeout_seconds=4.0)
        self.web_provider = DuckDuckGoProvider(timeout_seconds=4.5)

    async def search(
        self,
        session: AsyncSession,
        processed_query: ProcessedQuery,
        language_filter: str = "all",
        date_filter: str = "all",
        sort: str = "newest",
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Executes candidate retrieval across local index and live web providers,
        deduplicates candidates, scores them, and returns (ranked_paged_results, total_count).
        """
        query_terms = list(processed_query.search_terms)
        normalized_q = processed_query.normalized_query
        detected_lang = processed_query.detected_language

        # If news/temporal intent detected, ensure core topic terms are searched
        if processed_query.is_time_sensitive or processed_query.is_news_intent:
            if processed_query.core_topic and processed_query.core_topic != normalized_q:
                core_tokens = processed_query.core_topic.split()
                for ct in core_tokens:
                    if ct not in query_terms:
                        query_terms.append(ct)

        # 1. Fetch local database candidates
        local_candidates = await self._search_local_db(
            session=session,
            processed_query=processed_query,
            language_filter=language_filter,
            date_filter=date_filter,
        )

        # 2. Concurrently fetch live web and encyclopedic candidates
        # Query external providers for broader coverage
        web_queries = [normalized_q]
        if processed_query.core_topic and processed_query.core_topic != normalized_q:
            web_queries.append(processed_query.core_topic)
        if processed_query.transliteration_suggestion and processed_query.transliteration_suggestion != normalized_q:
            web_queries.append(processed_query.transliteration_suggestion)

        for term in query_terms:
            if any(0x0980 <= ord(c) <= 0x09FF for c in term) and term not in web_queries:
                web_queries.append(term)

        tasks = [
            self.wiki_provider.search(
                query=web_queries[0],
                detected_language=detected_lang,
                page=page,
                page_size=page_size,
            ),
            self.web_provider.search(
                query=web_queries[0],
                detected_language=detected_lang,
                page=page,
                page_size=page_size,
            ),
        ]

        # Query native Assamese Wikipedia for all transliterated expansions
        for alt_q in web_queries[1:]:
            tasks.append(
                self.wiki_provider.search(
                    query=alt_q,
                    detected_language="as_native",
                    page=1,
                    page_size=5,
                )
            )

        provider_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. Combine and Deduplicate Candidates
        seen_canonical_urls = set()
        seen_content_hashes = set()
        all_candidates: List[Dict[str, Any]] = []

        def add_candidate(doc: Dict[str, Any]):
            canonical = doc.get("canonical_url") or doc.get("url") or ""
            chash = doc.get("content_hash") or ""

            # Normalize canonical url for duplicate suppression
            norm_canonical = canonical.lower().rstrip("/").replace("https://", "").replace("http://", "")
            if norm_canonical in seen_canonical_urls or (chash and chash in seen_content_hashes):
                return

            # Apply language filter if specified
            doc_lang = doc.get("language", "en")
            if language_filter != "all":
                if language_filter in ("as", "as_native", "as_romanized") and doc_lang != "as":
                    return
                elif language_filter == "en" and doc_lang != "en":
                    return

            seen_canonical_urls.add(norm_canonical)
            if chash:
                seen_content_hashes.add(chash)
            all_candidates.append(doc)

        # Add local candidates first (regional priority)
        for doc in local_candidates:
            add_candidate(doc)

        # Add external provider candidates
        for res in provider_results:
            if isinstance(res, list):
                for doc in res:
                    add_candidate(doc)

        total_matches = len(all_candidates)
        if total_matches == 0:
            return [], 0

        # 4. Multi-signal ranking and domain diversity
        ranked_docs = self.ranker.rank_and_diversify(
            documents=all_candidates,
            query_terms=query_terms,
            normalized_query=normalized_q,
            query_lang=detected_lang,
            max_results=max(100, page * page_size),
            sort=sort,
            is_time_sensitive=processed_query.is_time_sensitive,
            is_news_intent=processed_query.is_news_intent,
        )

        # 5. Accurate pagination slicing
        start_idx = (page - 1) * page_size
        paged_results = ranked_docs[start_idx : start_idx + page_size]

        return paged_results, total_matches

    async def _search_local_db(
        self,
        session: AsyncSession,
        processed_query: ProcessedQuery,
        language_filter: str,
        date_filter: str,
    ) -> List[Dict[str, Any]]:
        """Searches local SQLite IndexedDocument records."""
        try:
            stmt = (
                select(
                    IndexedDocument.id,
                    IndexedDocument.url,
                    IndexedDocument.canonical_url,
                    IndexedDocument.title,
                    IndexedDocument.body_text,
                    IndexedDocument.snippet,
                    IndexedDocument.language,
                    IndexedDocument.content_hash,
                    IndexedDocument.published_date,
                    IndexedDocument.published_at,
                    IndexedDocument.updated_at,
                    IndexedDocument.crawled_at,
                    IndexedDocument.is_news,
                    SourceRegistry.name.label("source_name"),
                    SourceRegistry.domain.label("source_domain"),
                    SourceRegistry.is_authoritative.label("is_authoritative"),
                )
                .outerjoin(SourceRegistry, IndexedDocument.source_id == SourceRegistry.id)
                .where(IndexedDocument.is_removed == False)
            )

            if language_filter != "all":
                if language_filter in ("as", "as_native", "as_romanized"):
                    stmt = stmt.where(IndexedDocument.language == "as")
                elif language_filter == "en":
                    stmt = stmt.where(IndexedDocument.language == "en")

            if date_filter != "all":
                now = datetime.now(timezone.utc)
                cutoff = None
                if date_filter == "past_24h":
                    cutoff = now - timedelta(days=1)
                elif date_filter == "past_week":
                    cutoff = now - timedelta(days=7)
                elif date_filter == "past_month":
                    cutoff = now - timedelta(days=30)
                elif date_filter == "past_year":
                    cutoff = now - timedelta(days=365)
                if cutoff:
                    stmt = stmt.where(
                        (IndexedDocument.published_at >= cutoff) | (IndexedDocument.published_date >= cutoff)
                    )

            result = await session.execute(stmt)
            rows = result.mappings().all()

            def matches_term(term: str, text: str) -> bool:
                if not term or not text:
                    return False
                if len(term) <= 3:
                    return bool(re.search(rf"\b{re.escape(term)}\b", text))
                return term in text

            local_matches = []
            query_terms = [t.lower() for t in processed_query.search_terms]
            norm_q = processed_query.normalized_query.lower()

            # If time-sensitive query has a specific topical constraint (e.g. 'ai' in 'latest ai news'), require topic match
            topic_tokens = (
                [t.lower() for t in processed_query.core_topic.split() if len(t) > 1]
                if (processed_query.is_time_sensitive or processed_query.is_news_intent) and processed_query.core_topic
                else []
            )

            for row in rows:
                title_lower = row["title"].lower()
                body_lower = row["body_text"].lower()

                # Enforce topical filter: if query was about a specific subject, document must match the subject
                if topic_tokens and not any(matches_term(tt, title_lower) or matches_term(tt, body_lower) for tt in topic_tokens):
                    continue

                is_match = False
                for term in query_terms:
                    if matches_term(term, title_lower) or matches_term(term, body_lower):
                        is_match = True
                        break

                if is_match or matches_term(norm_q, title_lower) or matches_term(norm_q, body_lower):
                    doc_dict = dict(row)
                    doc_dict["id"] = str(doc_dict["id"])
                    local_matches.append(doc_dict)

            return local_matches
        except Exception:
            return []
