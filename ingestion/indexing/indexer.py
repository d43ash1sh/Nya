"""
Document Indexer and Deduplication Pipeline.
Canonicalizes URLs, computes content hashes, applies Assamese normalization,
and indexes documents into the primary search database.
"""

import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import IndexedDocument
from nlp.assamese_normalizer import AssameseNormalizer
from nlp.script_detector import ScriptDetector


class DocumentIndexer:
    def __init__(self):
        self.normalizer = AssameseNormalizer()
        self.detector = ScriptDetector()

    def compute_content_hash(self, body_text: str) -> str:
        """Compute SHA-256 fingerprint for near-duplicate and exact-duplicate detection."""
        # Normalize text before hashing
        norm = self.normalizer.normalize(body_text.lower())
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    async def index_document(
        self,
        session: AsyncSession,
        url: str,
        canonical_url: str,
        title: str,
        body_text: str,
        snippet: str,
        source_id: Optional[str] = None,
        published_date: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        crawled_at: Optional[datetime] = None,
        is_news: bool = False,
    ) -> IndexedDocument:
        """Indexes or updates an existing document in the search database."""
        content_hash = self.compute_content_hash(body_text)

        # Detect language
        detected = self.detector.detect(f"{title} {body_text[:200]}")
        doc_lang = "as" if detected in ("as_native", "as_romanized") else ("en" if detected == "en" else "mixed")

        # Resolve publication timestamp
        effective_published_at = published_at or published_date
        effective_crawled_at = crawled_at or datetime.now(timezone.utc)

        # Check if URL already exists
        stmt = select(IndexedDocument).where(IndexedDocument.url == url)
        res = await session.execute(stmt)
        existing = res.scalars().first()

        if existing:
            existing.canonical_url = canonical_url
            existing.title = title
            existing.body_text = body_text
            existing.snippet = snippet
            existing.content_hash = content_hash
            existing.language = doc_lang
            existing.source_id = source_id
            existing.published_date = effective_published_at
            existing.published_at = effective_published_at
            existing.updated_at = updated_at
            existing.crawled_at = effective_crawled_at
            existing.is_news = is_news
            existing.indexed_at = datetime.now(timezone.utc)
            existing.is_removed = False
            await session.commit()
            return existing

        # Create new record
        new_doc = IndexedDocument(
            url=url,
            canonical_url=canonical_url,
            title=title,
            body_text=body_text,
            snippet=snippet,
            language=doc_lang,
            source_id=source_id,
            content_hash=content_hash,
            published_date=effective_published_at,
            published_at=effective_published_at,
            updated_at=updated_at,
            crawled_at=effective_crawled_at,
            is_news=is_news,
            indexed_at=datetime.now(timezone.utc),
            is_removed=False,
        )
        session.add(new_doc)
        await session.commit()
        return new_doc
