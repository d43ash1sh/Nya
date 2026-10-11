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

from typing import List, Dict, Any
from datetime import datetime, timezone
import math


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
    ) -> float:
        """Calculate relevance score for a document."""
        title_lower = doc.get("title", "").lower()
        body_lower = doc.get("body_text", "").lower()
        doc_lang = doc.get("language", "as")

        score = 0.0

        # Term frequency in title and body
        for term in query_terms:
            t = term.lower()
            if t in title_lower:
                # Title matches heavily boosted
                score += 3.0 * self.title_boost
            if t in body_lower:
                # Body match occurrences
                occurrences = body_lower.count(t)
                score += min(math.log1p(occurrences), 4.0)

        # Exact phrase match boost
        if normalized_query.lower() in title_lower:
            score += 5.0 * self.exact_phrase_boost
        elif normalized_query.lower() in body_lower:
            score += 2.5 * self.exact_phrase_boost

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

        # Freshness score if publication date is available
        pub_date = doc.get("published_date")
        if pub_date:
            try:
                if isinstance(pub_date, str):
                    pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                else:
                    pub_dt = pub_date

                now = datetime.now(timezone.utc)
                age_days = (now - pub_dt).days
                if age_days >= 0:
                    freshness = math.exp(-age_days / 365.0)  # 1-year exponential decay
                    score += freshness * 1.5
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
    ) -> List[Dict[str, Any]]:
        """
        Scores all candidates and applies domain diversity suppression
        to prevent any single domain from monopolizing top search spots.
        """
        scored_docs = []
        for doc in documents:
            s = self.score_document(doc, query_terms, normalized_query, query_lang)
            scored_doc = dict(doc)
            scored_doc["score"] = s
            scored_docs.append(scored_doc)

        # Sort primarily by initial score descending
        scored_docs.sort(key=lambda d: d["score"], reverse=True)

        # Apply domain diversity penalty
        domain_counts: Dict[str, int] = {}
        reranked: List[Dict[str, Any]] = []

        for doc in scored_docs:
            domain = doc.get("source_domain", "")
            count = domain_counts.get(domain, 0)
            adjusted_score = doc["score"]

            if count > 0:
                # Apply progressive penalty for repeated domain in same result set
                adjusted_score *= (self.domain_penalty_factor ** count)

            doc["score"] = round(adjusted_score, 4)
            domain_counts[domain] = count + 1
            reranked.append(doc)

        # Final sort with adjusted scores
        reranked.sort(key=lambda d: d["score"], reverse=True)
        return reranked[:max_results]
