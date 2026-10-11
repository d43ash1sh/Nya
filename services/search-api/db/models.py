"""
SQLAlchemy models for ঞ (Nya) Search Engine.
Includes Source Registry, Indexed Documents, Deduplication Hashes,
Privacy-Safe Feedback, and AI Usage Audit.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SourceRegistry(Base):
    __tablename__ = "source_registry"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    base_url = Column(String(512), nullable=False)
    crawl_allowed = Column(Boolean, default=True, nullable=False)
    robots_txt_url = Column(String(512), nullable=True)
    license_info = Column(String(255), default="Public Web / Fair Indexing")
    language_focus = Column(String(50), default="as")  # 'as', 'en', 'mixed'
    rate_limit_delay = Column(Float, default=1.5)
    is_authoritative = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    documents = relationship("IndexedDocument", back_populates="source")


class IndexedDocument(Base):
    __tablename__ = "indexed_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(1024), unique=True, nullable=False, index=True)
    canonical_url = Column(String(1024), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    body_text = Column(Text, nullable=False)
    snippet = Column(Text, nullable=False)
    language = Column(String(50), default="as", index=True)  # 'as', 'en', 'mixed'
    source_id = Column(String(36), ForeignKey("source_registry.id"), nullable=True)
    content_hash = Column(String(64), nullable=False, index=True)  # SHA256 / SimHash for deduplication
    published_date = Column(DateTime(timezone=True), nullable=True)
    indexed_at = Column(DateTime(timezone=True), default=utc_now)
    is_removed = Column(Boolean, default=False, nullable=False, index=True)  # Privacy/Takedown flag

    source = relationship("SourceRegistry", back_populates="documents")

    __table_args__ = (
        Index("idx_doc_search", "is_removed", "language"),
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Query hash is logged rather than raw text to uphold privacy-by-default
    query_hash = Column(String(64), nullable=False, index=True)
    result_id = Column(String(36), nullable=True)
    feedback_type = Column(String(50), nullable=False)  # 'relevance', 'ai_quality', 'broken_link', 'privacy'
    is_positive = Column(Boolean, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class AIUsageLog(Base):
    __tablename__ = "ai_usage_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), default=utc_now)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    tokens_used = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    status = Column(String(50), nullable=False)
