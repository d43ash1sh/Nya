"""
Multi-signal Ranking and Domain Diversity Engine for ঞ (Nya) Search.
Applies:
- Title match boost
- Exact phrase match boost
- Language alignment boost
- Authoritative source boost
- Freshness decay
- Domain diversity / deduplication penalty to avoid single-domain dominance
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import math
import re


class RankingEngine:
    def __init__(
        self,
        title_boost: float = 3.0,
        exact_phrase_boost: float = 2.0,
        language_match_boost: float = 1.5,
        authoritative_boost: float = 1.3,
        domain_penalty_factor: float = 0.65,
    ):
        self.title_boost = title_boost
        self.exact_phrase_boost = exact_phrase_boost
        self.language_match_boost = language_match_boost
        self.authoritative_boost = authoritative_boost
        self.domain_penalty_factor = domain_penalty_factor

    def score_document(
        self,
        doc: Dict[str, Any],
        query_terms: List[str],
        normalized_query: str,
        query_lang: str,
        is_news_query: bool = False,
        is_time_sensitive: bool = False,
    ) -> float:
        """Calculate relevance score for a document."""
        title_lower = doc.get("title", "").lower()
        body_lower = doc.get("body_text", "").lower()
        doc_lang = doc.get("language", "as")

        score = 0.0

        # Term frequency in title and body
        for term in query_terms:
            t = term.lower().strip()
            if not t:
                continue

            # For short terms (<= 3 chars), strictly require whole word boundaries
            # to prevent false-positive substring matches (e.g. 'ko' inside 'Tokyo' or 'Korea')
            word_pattern = rf"\b{re.escape(t)}\b"
            has_word_title = bool(re.search(word_pattern, title_lower))

            if has_word_title:
                score += 3.0 * self.title_boost
            elif len(t) > 3 and t in title_lower:
                score += 1.0 * self.title_boost

            if len(t) <= 3:
                occurrences = len(re.findall(word_pattern, body_lower))
            else:
                occurrences = body_lower.count(t)

            if occurrences > 0:
                score += min(math.log1p(occurrences), 4.0)

        # Exact phrase match boost (supports cross-script transliteration for Assamese docs)
        norm_q = normalized_query.lower().strip()
        candidate_phrases = [norm_q] if norm_q else []
        if doc_lang == "as":
            for term in query_terms:
                t_clean = term.lower().strip()
                if any(0x0980 <= ord(c) <= 0x09FF for c in t_clean) and t_clean not in candidate_phrases:
                    candidate_phrases.append(t_clean)

        for cp in candidate_phrases:
            if not cp:
                continue
            if len(cp) <= 3:
                phrase_pattern = rf"\b{re.escape(cp)}\b"
                if re.search(phrase_pattern, title_lower):
                    score += 5.0 * self.exact_phrase_boost
                    break
                elif re.search(phrase_pattern, body_lower):
                    score += 2.5 * self.exact_phrase_boost
                    break
            else:
                if cp in title_lower:
                    score += 5.0 * self.exact_phrase_boost
                    break
                elif cp in body_lower:
                    score += 2.5 * self.exact_phrase_boost
                    break

        # Language alignment boost
        if query_lang in ("as_native", "as_romanized") and doc_lang == "as":
            score *= self.language_match_boost
        elif query_lang == "en" and doc_lang == "en":
            score *= self.language_match_boost
        elif query_lang == "mixed":
            score *= 1.2

        # Authoritative publisher boost
        if doc.get("is_authoritative", False):
            score *= self.authoritative_boost

        # News intent adjustment: deprioritize static encyclopedias when user searches for news/latest
        is_news = (
            is_news_query
            or is_time_sensitive
            or doc.get("_is_news_intent", False)
            or doc.get("_is_time_sensitive", False)
        )
        domain = doc.get("source_domain", "").lower()
        if is_news:
            if "wikipedia.org" in domain:
                score *= 0.35  # Suppress generic encyclopedia definitions from hijacking breaking news
            elif doc.get("is_news", False):
                score *= 1.8   # Boost genuine news articles and announcements

        # Freshness score if publication date is available
        pub_date = doc.get("published_at") or doc.get("published_date")
        if pub_date:
            try:
                if isinstance(pub_date, str):
                    pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                else:
                    pub_dt = pub_date

                if pub_dt.tzinfo is None:
                    pub_dt = pub_dt.replace(tzinfo=timezone.utc)

                now = datetime.now(timezone.utc)
                age_days = (now - pub_dt).days
                if age_days >= 0:
                    freshness = math.exp(-age_days / 180.0)  # exponential freshness decay
                    score += freshness * (3.0 if is_news else 1.5)
            except Exception:
                pass

        return round(score, 4)

    def rank_and_diversify(
        self,
        documents: List[Dict[str, Any]],
        query_terms: List[str],
        normalized_query: str,
        query_lang: str,
        max_results: int = 10,
        sort: str = "newest",
        sort_by: Optional[str] = None,
        is_time_sensitive: bool = False,
        is_news_intent: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Scores all candidates and sorts them by 'newest' (descending verified publication time,
        with undated items after dated items) or 'relevance' (multi-signal score with domain diversity).
        Enforces relevance filtering so completely irrelevant pages are never returned.
        """
        effective_sort = sort_by or sort or "newest"
        scored_docs = []
        for doc in documents:
            doc_copy = dict(doc)
            doc_copy["_is_time_sensitive"] = is_time_sensitive
            doc_copy["_is_news_intent"] = is_news_intent
            s = self.score_document(
                doc_copy,
                query_terms,
                normalized_query,
                query_lang,
                is_news_query=is_news_intent,
                is_time_sensitive=is_time_sensitive,
            )
            doc_copy["score"] = s
            # Retain documents that meet base relevance threshold
            if s > 0.05:
                scored_docs.append(doc_copy)

        if not scored_docs and documents:
            # Fallback in case terms were all stop-words or empty scores
            for doc in documents:
                d = dict(doc)
                d["score"] = 0.1
                scored_docs.append(d)

        # Apply domain diversity penalty for score stabilization
        scored_docs.sort(key=lambda d: d["score"], reverse=True)
        domain_counts: Dict[str, int] = {}
        for doc in scored_docs:
            dom = doc.get("source_domain", "")
            count = domain_counts.get(dom, 0)
            if count > 0:
                doc["score"] = round(doc["score"] * (self.domain_penalty_factor ** count), 4)
            domain_counts[dom] = count + 1

        # Relevance filtering: prevent incidental/irrelevant pages from outranking genuinely relevant pages
        if scored_docs:
            max_s = max(d["score"] for d in scored_docs)
            rel_threshold = max(0.2, max_s * 0.15) if max_s > 5.0 else 0.1
            scored_docs = [d for d in scored_docs if d["score"] >= rel_threshold] or scored_docs

        if effective_sort == "newest":
            # Separate dated from undated
            dated_docs = []
            undated_docs = []

            for doc in scored_docs:
                raw_pub = doc.get("published_at") or doc.get("published_date")
                parsed_dt = None
                if raw_pub:
                    try:
                        if isinstance(raw_pub, str):
                            parsed_dt = datetime.fromisoformat(raw_pub.replace("Z", "+00:00"))
                        else:
                            parsed_dt = raw_pub
                        if parsed_dt.tzinfo is None:
                            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                        else:
                            parsed_dt = parsed_dt.astimezone(timezone.utc)
                    except Exception:
                        parsed_dt = None

                if parsed_dt:
                    doc["_parsed_pub_dt"] = parsed_dt
                    dated_docs.append(doc)
                else:
                    undated_docs.append(doc)

            # Sort dated docs by verified publication timestamp descending (newest first)
            # Secondary sort by relevance score descending
            dated_docs.sort(key=lambda d: (d["_parsed_pub_dt"], d["score"]), reverse=True)

            # Clean temporary sort field
            for d in dated_docs:
                d.pop("_parsed_pub_dt", None)

            # Undated docs follow dated docs, ordered by relevance score descending
            undated_docs.sort(key=lambda d: d["score"], reverse=True)

            final_ranked = dated_docs + undated_docs
        else:
            # Sort by relevance score descending
            scored_docs.sort(key=lambda d: d["score"], reverse=True)
            final_ranked = scored_docs

        return final_ranked[:max_results]
