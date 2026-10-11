"""
Unit Tests for Multi-Signal Ranking and Domain Diversity Suppression.
"""

import sys
from pathlib import Path
import pytest

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "services" / "search-api"))
sys.path.insert(0, str(root_dir))

from search.ranking import RankingEngine


def test_ranking_title_boost():
    ranker = RankingEngine()
    terms = ["বিহু"]
    normalized_q = "বিহু"

    doc_with_title_match = {
        "title": "ৰঙালী বিহু উৎসৱ",
        "body_text": "অসমৰ বসন্ত কালৰ উৎসৱ।",
        "language": "as",
        "source_domain": "example1.org",
    }
    doc_with_only_body_match = {
        "title": "অসমৰ লোকসংস্কৃতি",
        "body_text": "ইয়াত বিহু পালন কৰা হয়।",
        "language": "as",
        "source_domain": "example2.org",
    }

    score1 = ranker.score_document(doc_with_title_match, terms, normalized_q, "as_native")
    score2 = ranker.score_document(doc_with_only_body_match, terms, normalized_q, "as_native")

    assert score1 > score2


def test_domain_diversity_suppression():
    ranker = RankingEngine(domain_penalty_factor=0.5)
    terms = ["assam"]
    normalized_q = "assam"

    # Three identical relevance documents from domain A, and one from domain B
    docs = [
        {"id": "1", "title": "Assam News 1", "body_text": "assam", "source_domain": "dominantsite.com"},
        {"id": "2", "title": "Assam News 2", "body_text": "assam", "source_domain": "dominantsite.com"},
        {"id": "3", "title": "Assam News 3", "body_text": "assam", "source_domain": "dominantsite.com"},
        {"id": "4", "title": "Assam Overview", "body_text": "assam", "source_domain": "alternativesite.org"},
    ]

    reranked = ranker.rank_and_diversify(docs, terms, normalized_q, "en", max_results=4)

    # First from dominantsite gets full score, but subsequent ones get penalized
    # alternative site should rise ahead of repeated dominant site results
    domains = [d["source_domain"] for d in reranked]
    assert "alternativesite.org" in domains[:3]
